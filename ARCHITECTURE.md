# 🏗️ Architecture Documentation

This document provides an in-depth explanation of EchoChat's architecture, design decisions, and technical implementation.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Homepage    │  │    Chat      │  │    Admin     │      │
│  │  (Clone)     │  │   Widget     │  │   Panel      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │ HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    API Layer                          │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │ Chat API    │  │ Admin API   │  │ Health API  │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  Business Logic                       │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │  │
│  │  │ Scraper  │  │ RAG      │  │Scheduler │           │  │
│  │  │(Playwright)│ │ Engine   │  │(APScheduler)│        │  │
│  │  └──────────┘  └──────────┘  └──────────┘           │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   Data Layer                          │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │  │
│  │  │ SQLite   │  │ ChromaDB │  │ Anthropic│           │  │
│  │  │(Metadata)│  │(Vectors) │  │   API    │           │  │
│  │  └──────────┘  └──────────┘  └──────────┘           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Web Scraper

**Technology**: Playwright (headless Chromium)

**Design Decisions**:
- **Playwright over BeautifulSoup**: Handles JavaScript-rendered content
- **Recursive crawling**: BFS approach to discover all pages
- **Same-domain restriction**: Prevents scraping external sites
- **Robots.txt**: Ignored by default (configurable) for maximum flexibility
- **Politeness**: 0.5s delay between requests

**Algorithm**:
```python
1. Start with seed URL
2. Visit URL with Playwright
3. Extract:
   - Page content (cleaned text)
   - Page HTML (for homepage display)
   - All internal links
4. Add new links to queue
5. Mark current URL as visited
6. Repeat until queue is empty
```

**Key Features**:
- URL normalization (removes fragments, handles relative links)
- Duplicate detection via set of visited URLs
- Error handling with logging
- Configurable timeout and concurrency

### 2. RAG (Retrieval Augmented Generation)

**Components**:
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **Vector Store**: ChromaDB (persistent)
- **Chunking**: Fixed-size with overlap

**Pipeline**:

```
Text Content
     ↓
[Chunking]
     ↓
Text Chunks (1000 chars, 200 overlap)
     ↓
[Embedding Model]
     ↓
Vector Embeddings (384 dimensions)
     ↓
[ChromaDB Storage]
     ↓
Indexed Vectors
```

**Retrieval Process**:
```
User Query
     ↓
[Embed Query]
     ↓
Query Vector
     ↓
[Similarity Search in ChromaDB]
     ↓
Top-K Most Similar Chunks (default: 5)
     ↓
Context for LLM
```

**Why This Approach**:
- **Sentence-transformers**: Fast, runs locally, good quality
- **ChromaDB**: Simple, persistent, perfect for single-server deployment
- **Chunking with overlap**: Preserves context at chunk boundaries
- **Cosine similarity**: Standard for semantic search

### 3. Chat API

**Flow**:
```
User Message
     ↓
[RAG Retrieval]
     ↓
Retrieved Contexts
     ↓
[Prompt Construction]
     ↓
System Prompt + Contexts + User Message
     ↓
[Anthropic API Call]
     ↓
Claude Response
     ↓
[Format with Sources]
     ↓
JSON Response to Frontend
```

**Prompt Engineering**:
- System prompt emphasizes context-only responses
- Sources are injected as numbered contexts
- Conversation history limited to last 5 messages
- Clear instructions about limitations

### 4. Scheduler

**Technology**: APScheduler (AsyncIOScheduler)

**Design**:
- Runs in-process with FastAPI
- Interval-based trigger (configurable hours)
- Job persistence across restarts
- Prevents overlapping executions

**Scheduled Tasks**:
1. **Scrape**: Crawl target website
2. **Reindex**: Full ChromaDB reindexing

**Configuration**:
- Default: 24 hours
- Modifiable via environment variable
- Can be triggered manually via API

### 5. Database Schema

**SQLite (Metadata)**:

```sql
-- Scraped pages
CREATE TABLE scraped_pages (
    id INTEGER PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    title TEXT,
    content TEXT,
    html TEXT,
    is_homepage BOOLEAN,
    scraped_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Scrape jobs
CREATE TABLE scrape_jobs (
    id INTEGER PRIMARY KEY,
    target_url TEXT NOT NULL,
    status TEXT,  -- pending, running, completed, failed
    pages_scraped INTEGER,
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP
);
```

**ChromaDB (Vectors)**:
- Collection: `echochat_docs`
- Metadata per chunk:
  - url
  - title
  - chunk_index
  - total_chunks
  - is_homepage

## Frontend Architecture

### Pages

**1. Homepage (`/`)**:
- Displays scraped homepage HTML (dangerouslySetInnerHTML)
- Integrated chat widget (fixed position)
- Loading and error states

**2. Admin Panel (`/admin`)**:
- Statistics dashboard (cards)
- Scrape job form
- Job history table
- Auto-refresh (5s interval)

### Components

**Chat Widget**:
- Toggleable floating bubble
- Message history
- Markdown rendering
- Source citations
- Loading states

### State Management

- React hooks (useState, useEffect)
- No global state library needed
- API calls via axios
- Real-time updates via polling

## Design Patterns

### 1. Dependency Injection

FastAPI's `Depends()` for clean dependency management:
```python
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/chat")
async def chat(message: ChatMessage, db: Session = Depends(get_db)):
    # db is automatically injected and cleaned up
```

### 2. Singleton Pattern

RAG engine initialized once:
```python
_rag_engine: Optional[RAGEngine] = None

def get_rag_engine() -> RAGEngine:
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    return _rag_engine
```

### 3. Repository Pattern

Database operations encapsulated in models:
```python
class ScrapedPage(Base):
    # ORM model with built-in CRUD
```

### 4. Background Tasks

Long-running operations don't block API responses:
```python
@router.post("/scrape")
async def start_scrape(
    request: ScrapeRequest,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(run_scraper, ...)
    return {"status": "started"}
```

## Security Considerations

### 1. API Key Management

- Environment variables only
- Never committed to git
- Validated on startup

### 2. CORS Configuration

- Whitelist specific origins
- Configurable via environment

### 3. Input Validation

- Pydantic models for all API inputs
- URL validation
- SQL injection prevention (SQLAlchemy ORM)

### 4. XSS Prevention

- React escapes by default
- dangerouslySetInnerHTML only for homepage (scraped content)
- Markdown rendering with sanitization

### 5. Rate Limiting

- Polite scraping (0.5s delays)
- Can add request rate limiting if needed

## Performance Optimizations

### 1. Caching

- ChromaDB persists to disk (no re-indexing needed)
- SQLite for fast metadata queries

### 2. Async Operations

- FastAPI async endpoints
- Playwright async API
- Background task processing

### 3. Lazy Loading

- RAG engine initialized on first use
- Embeddings loaded once

### 4. Chunking Strategy

- Fixed-size chunks (1000 chars)
- Overlap (200 chars) for context preservation
- Balanced between quality and performance

## Scalability Considerations

### Current Architecture

- Single server deployment
- Suitable for:
  - Small to medium websites (< 10,000 pages)
  - Low to medium traffic (< 1000 requests/day)

### Scaling Options

**Horizontal Scaling**:
1. Separate scraper service
2. API server auto-scaling
3. Shared database (PostgreSQL)
4. Distributed vector store (Pinecone, Weaviate)

**Vertical Scaling**:
1. Increase memory for larger embeddings
2. More CPU for faster scraping
3. SSD for faster ChromaDB queries

## Trade-offs & Limitations

### Current Trade-offs

1. **SQLite vs PostgreSQL**:
   - ✅ Simple, no setup
   - ❌ No horizontal scaling
   - Decision: Good for MVP and single-server deployments

2. **Chromium vs lighter browsers**:
   - ✅ Full JavaScript support
   - ❌ Higher memory usage
   - Decision: Necessary for modern websites

3. **Local embeddings vs API**:
   - ✅ No API costs, fast
   - ❌ Slightly lower quality than large models
   - Decision: Good balance for most use cases

4. **Polling vs WebSockets**:
   - ✅ Simple implementation
   - ❌ Higher overhead
   - Decision: Fine for admin panel updates

### Known Limitations

1. **Single domain only**: By design for focused content
2. **No incremental scraping**: Full rescrape on each run
3. **No real-time updates**: Scheduled batch processing
4. **Memory intensive**: Playwright + embeddings + vectors

## Future Enhancements

### Phase 2 (Suggested)

- [ ] Incremental scraping (only new/changed pages)
- [ ] Multi-domain support with namespace isolation
- [ ] Real-time scraping status with WebSockets
- [ ] User authentication for admin panel
- [ ] Advanced search filters
- [ ] Export scraped data
- [ ] Custom scraping rules per site

### Phase 3 (Advanced)

- [ ] Distributed scraping with Celery
- [ ] PostgreSQL with pgvector
- [ ] Redis caching layer
- [ ] Kubernetes deployment
- [ ] Multi-tenant support
- [ ] GraphQL API
- [ ] Analytics dashboard

## Testing Strategy

### Unit Tests

- Scraper URL normalization
- RAG chunking logic
- API endpoint validation

### Integration Tests

- End-to-end scraping flow
- RAG indexing and retrieval
- Chat API with mocked Anthropic

### Manual Testing

- Admin panel workflows
- Chat interface UX
- Mobile responsiveness

## Monitoring & Observability

### Logging

- Structured logging with timestamps
- Log levels: DEBUG, INFO, WARNING, ERROR
- File rotation (10MB, 5 backups)

### Metrics (Future)

- Scraping duration
- Pages per scrape
- Chat response times
- API error rates

### Health Checks

- `/health` endpoint
- Database connectivity
- ChromaDB availability

## Contributing

When contributing, consider:
- Maintain async-first design
- Add type hints
- Write tests for new features
- Update documentation
- Follow existing code style

---

This architecture is designed to be:
- **Simple**: Easy to understand and deploy
- **Effective**: Solves the core problem well
- **Extensible**: Can grow with requirements
- **Maintainable**: Clear separation of concerns

For questions or suggestions, open an issue on GitHub.
