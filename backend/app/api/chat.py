"""Chat API endpoints using Anthropic."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
import anthropic
from sqlalchemy.orm import Session

from app.config import settings
from app.rag.rag_engine import get_rag_engine
from app.models.database import get_db
from app.utils.logger import logger


router = APIRouter()


class ChatMessage(BaseModel):
    """Chat message request."""
    message: str
    conversation_history: Optional[List[Dict]] = []


class ChatSource(BaseModel):
    """Source reference for chat response."""
    url: str
    title: str
    excerpt: str


class ChatResponse(BaseModel):
    """Chat response."""
    response: str
    sources: List[ChatSource]


@router.post("/chat", response_model=ChatResponse)
async def chat(
    chat_message: ChatMessage,
    db: Session = Depends(get_db)
):
    """
    Chat endpoint that retrieves context and generates response using Anthropic.
    
    Args:
        chat_message: User message and conversation history
        db: Database session
        
    Returns:
        Chat response with sources
    """
    try:
        # Get RAG engine
        rag_engine = get_rag_engine()
        
        # Retrieve relevant contexts
        contexts = rag_engine.retrieve(chat_message.message)
        
        if not contexts:
            raise HTTPException(
                status_code=404,
                detail="No relevant information found. Please ensure the site has been scraped and indexed."
            )
        
        # Build context string
        context_texts = []
        sources_dict = {}
        
        for ctx in contexts:
            context_texts.append(ctx['content'])
            url = ctx['metadata']['url']
            sources_dict[url] = {
                'url': url,
                'title': ctx['metadata'].get('title', 'Untitled'),
                'excerpt': ctx['content'][:200] + "..."
            }
        
        combined_context = "\n\n".join([f"[Context {i+1}]\n{text}" for i, text in enumerate(context_texts)])
        
        # Build prompt for Anthropic
        system_prompt = """You are a helpful AI assistant that answers questions based ONLY on the provided context from the scraped website content.

IMPORTANT RULES:
1. Answer ONLY based on the context provided below
2. If the answer is not in the context, say "I don't have enough information to answer that question based on the available content"
3. Always cite your sources by mentioning which context sections you used
4. Be concise and accurate
5. Maintain a friendly, professional tone
6. If the user asks in a specific language, respond in that language

Context from the website:
{combined_context}"""
        
        # Prepare messages for Anthropic
        messages = []
        
        # Add conversation history if present
        if chat_message.conversation_history:
            for msg in chat_message.conversation_history[-5:]:  # Keep last 5 messages
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": chat_message.message
        })
        
        # Call Anthropic API
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        
        response = client.messages.create(
            model=settings.anthropic_model,
            max_tokens=1024,
            system=system_prompt,
            messages=messages
        )

        # Extract response text
        if not response.content or len(response.content) == 0:
            raise HTTPException(status_code=500, detail="Empty response from AI service")

        response_text = response.content[0].text
        
        # Build sources list
        sources = [ChatSource(**source) for source in sources_dict.values()]
        
        logger.info(f"Chat response generated for query: {chat_message.message[:50]}...")
        
        return ChatResponse(
            response=response_text,
            sources=sources[:3]  # Return top 3 sources
        )
        
    except anthropic.APIError as e:
        logger.error(f"Anthropic API error: {e}")
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
