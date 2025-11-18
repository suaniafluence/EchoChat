"""RAG engine for indexing and retrieving content."""
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
import hashlib

from app.models.scraped_page import ScrapedPage
from app.config import settings
from app.utils.logger import logger


class RAGEngine:
    """RAG engine for embedding and retrieval."""
    
    def __init__(self):
        """Initialize the RAG engine."""
        self.embedding_model = SentenceTransformer(settings.embedding_model)
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=settings.chroma_persist_directory,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        try:
            self.collection = self.chroma_client.get_or_create_collection(
                name="echochat_docs",
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB collection: {e}")
            raise
        
        logger.info("RAG engine initialized successfully")
    
    def _chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks with overlap.
        
        Args:
            text: Text to chunk
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
        
        words = text.split()
        chunks = []
        
        chunk_size_words = settings.chunk_size // 5  # Approximate words
        overlap_words = settings.chunk_overlap // 5
        
        for i in range(0, len(words), chunk_size_words - overlap_words):
            chunk = ' '.join(words[i:i + chunk_size_words])
            if chunk:
                chunks.append(chunk)
        
        return chunks
    
    def _generate_chunk_id(self, url: str, chunk_index: int) -> str:
        """
        Generate unique ID for a chunk.
        
        Args:
            url: Source URL
            chunk_index: Index of the chunk
            
        Returns:
            Unique chunk ID
        """
        content = f"{url}_{chunk_index}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def index_page(self, page: ScrapedPage) -> int:
        """
        Index a single page into the vector store.
        
        Args:
            page: ScrapedPage object
            
        Returns:
            Number of chunks indexed
        """
        try:
            # Chunk the content
            chunks = self._chunk_text(page.content)
            
            if not chunks:
                logger.warning(f"No content to index for {page.url}")
                return 0
            
            # Prepare data for ChromaDB
            ids = [self._generate_chunk_id(page.url, i) for i in range(len(chunks))]
            metadatas = [
                {
                    'url': page.url,
                    'title': page.title or "",
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'is_homepage': str(page.is_homepage)
                }
                for i in range(len(chunks))
            ]
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(chunks, show_progress_bar=False)
            
            # Add to ChromaDB
            self.collection.add(
                ids=ids,
                embeddings=embeddings.tolist(),
                documents=chunks,
                metadatas=metadatas
            )
            
            logger.info(f"Indexed {len(chunks)} chunks from {page.url}")
            return len(chunks)
            
        except Exception as e:
            logger.error(f"Failed to index page {page.url}: {e}")
            return 0
    
    def index_all_pages(self, db: Session) -> int:
        """
        Index all scraped pages from database.
        
        Args:
            db: Database session
            
        Returns:
            Total number of chunks indexed
        """
        logger.info("Starting full reindex of all pages")
        
        try:
            # Clear existing collection
            self.chroma_client.delete_collection("echochat_docs")
            self.collection = self.chroma_client.create_collection(
                name="echochat_docs",
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("Cleared existing index")
        except Exception as e:
            logger.warning(f"Failed to clear existing index: {e}")
        
        # Get all pages
        pages = db.query(ScrapedPage).all()
        total_chunks = 0
        
        for page in pages:
            chunks_indexed = self.index_page(page)
            total_chunks += chunks_indexed
        
        logger.info(f"Reindexing complete. Total chunks indexed: {total_chunks} from {len(pages)} pages")
        return total_chunks
    
    def retrieve(self, query: str, top_k: int = None) -> List[Dict]:
        """
        Retrieve relevant chunks for a query.
        
        Args:
            query: Search query
            top_k: Number of results to return (defaults to settings)
            
        Returns:
            List of relevant chunks with metadata
        """
        if top_k is None:
            top_k = settings.top_k_results
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])[0]
            
            # Query ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k
            )
            
            # Format results
            formatted_results = []
            
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if 'distances' in results else None
                    })
            
            logger.info(f"Retrieved {len(formatted_results)} results for query: {query[:50]}...")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to retrieve results: {e}")
            return []
    
    def get_collection_stats(self) -> Dict:
        """
        Get statistics about the indexed collection.
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            count = self.collection.count()
            return {
                'total_chunks': count,
                'collection_name': self.collection.name
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {'total_chunks': 0, 'collection_name': 'unknown'}


# Global RAG engine instance
_rag_engine: Optional[RAGEngine] = None


def get_rag_engine() -> RAGEngine:
    """Get or create global RAG engine instance."""
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    return _rag_engine
