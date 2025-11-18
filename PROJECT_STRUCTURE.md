# 📁 Project Structure

Complete file structure of EchoChat with descriptions.

## Root Directory

```
EchoChat/
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
├── LICENSE                      # MIT license
├── Makefile                     # Convenient make commands
├── README.md                    # Main documentation
├── QUICKSTART.md               # 5-minute setup guide
├── ARCHITECTURE.md             # Technical architecture details
├── DEPLOYMENT.md               # Production deployment guide
├── PROJECT_STRUCTURE.md        # This file
├── docker-compose.yml          # Docker Compose configuration
├── install.sh                  # Automated installation script
├── start.sh                    # Start application script
├── stop.sh                     # Stop application script
├── logs.sh                     # View logs script
├── backend/                    # Backend application
└── frontend/                   # Frontend application
```

## Backend Structure

```
backend/
├── .env.example                # Backend environment template
├── .dockerignore              # Docker build exclusions
├── Dockerfile                 # Backend container definition
├── requirements.txt           # Python dependencies
└── app/                       # Application code
    ├── main.py                # FastAPI application entry point
    ├── config.py              # Configuration management
    ├── api/                   # API endpoints
    │   ├── __init__.py
    │   ├── chat.py            # Chat endpoint (Anthropic)
    │   └── admin.py           # Admin endpoints (scraping, stats)
    ├── models/                # Database models
    │   ├── __init__.py
    │   ├── database.py        # SQLAlchemy setup
    │   ├── scraped_page.py    # Page model
    │   └── scrape_job.py      # Job model with status tracking
    ├── scraper/               # Web scraping module
    │   ├── __init__.py
    │   └── scraper.py         # Playwright-based scraper
    ├── rag/                   # RAG pipeline
    │   ├── __init__.py
    │   └── rag_engine.py      # ChromaDB + embeddings
    ├── scheduler/             # Automated tasks
    │   ├── __init__.py
    │   └── scheduler.py       # APScheduler setup
    └── utils/                 # Utilities
        └── logger.py          # Centralized logging
```

### Backend File Descriptions

| File | Purpose | Key Features |
|------|---------|--------------|
| `main.py` | FastAPI app | CORS, lifespan events, router inclusion |
| `config.py` | Settings | Pydantic settings from env vars |
| `api/chat.py` | Chat endpoint | RAG retrieval + Anthropic API |
| `api/admin.py` | Admin API | Scraping, jobs, stats, homepage |
| `models/database.py` | DB setup | SQLAlchemy engine & session |
| `models/scraped_page.py` | Page model | URL, title, content, HTML |
| `models/scrape_job.py` | Job model | Status tracking, timestamps |
| `scraper/scraper.py` | Web scraper | Playwright, recursive crawling |
| `rag/rag_engine.py` | RAG engine | ChromaDB, embeddings, retrieval |
| `scheduler/scheduler.py` | Task scheduler | Automated scraping + reindexing |
| `utils/logger.py` | Logging | File rotation, console output |

## Frontend Structure

```
frontend/
├── .env.local.example         # Frontend environment template
├── .dockerignore             # Docker build exclusions
├── Dockerfile                # Frontend container definition
├── package.json              # Node dependencies
├── tsconfig.json             # TypeScript configuration
├── next.config.js            # Next.js configuration
├── tailwind.config.js        # Tailwind CSS configuration
├── postcss.config.js         # PostCSS configuration
├── pages/                    # Next.js pages
│   ├── _app.tsx              # App wrapper
│   ├── index.tsx             # Homepage (clone + chat)
│   └── admin.tsx             # Admin dashboard
├── components/               # React components
│   └── Chat.tsx              # Chat widget
├── lib/                      # Utilities
│   └── api.ts                # API client (axios)
└── styles/                   # Styles
    └── globals.css           # Global CSS + Tailwind
```

### Frontend File Descriptions

| File | Purpose | Key Features |
|------|---------|--------------|
| `pages/index.tsx` | Main page | Homepage clone, chat widget |
| `pages/admin.tsx` | Admin panel | Stats, scrape form, job history |
| `pages/_app.tsx` | App wrapper | Global styles, app initialization |
| `components/Chat.tsx` | Chat UI | Bubble, messages, markdown rendering |
| `lib/api.ts` | API client | Typed axios wrapper |
| `styles/globals.css` | Global styles | Tailwind imports, custom styles |
| `next.config.js` | Next.js config | Standalone output, env vars |
| `tailwind.config.js` | Tailwind config | Theme, colors, content paths |

## Docker Files

```
docker-compose.yml             # Multi-container orchestration
backend/Dockerfile            # Backend image
frontend/Dockerfile           # Frontend image (multi-stage)
backend/.dockerignore         # Backend build exclusions
frontend/.dockerignore        # Frontend build exclusions
```

### Docker Configuration

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Defines backend + frontend services with volumes |
| `backend/Dockerfile` | Python 3.11 + Playwright + dependencies |
| `frontend/Dockerfile` | Node 18 multi-stage build |

## Scripts

```
install.sh                    # Automated setup with prompts
start.sh                      # Start application (docker compose up)
stop.sh                       # Stop application (docker compose down)
logs.sh                       # View logs (docker compose logs)
Makefile                      # Convenient make commands
```

### Script Descriptions

| Script | Command | Purpose |
|--------|---------|---------|
| `install.sh` | `./install.sh` | Interactive setup wizard |
| `start.sh` | `./start.sh` | Start all services |
| `stop.sh` | `./stop.sh` | Stop all services |
| `logs.sh` | `./logs.sh` | Stream logs |
| `Makefile` | `make <command>` | Development shortcuts |

### Make Commands

```bash
make help          # Show all commands
make install       # Install dependencies locally
make dev-backend   # Run backend in dev mode
make dev-frontend  # Run frontend in dev mode
make build         # Build Docker images
make start         # Start with Docker
make stop          # Stop containers
make logs          # View logs
make clean         # Clean up data/logs
make setup         # Create .env files
```

## Configuration Files

```
.env.example                  # Root environment template
backend/.env.example          # Backend environment template
frontend/.env.local.example   # Frontend environment template
```

### Environment Variables

**Root `.env`**:
- `TARGET_URL`: Website to scrape
- `ANTHROPIC_API_KEY`: Anthropic API key
- `SCRAPE_FREQUENCY_HOURS`: Scraping frequency

**Backend `.env`**:
- All root variables plus backend-specific settings
- Database, ChromaDB, scraper, RAG configurations

**Frontend `.env.local`**:
- `NEXT_PUBLIC_API_URL`: Backend API URL

## Documentation Files

```
README.md                     # Main documentation (features, setup, usage)
QUICKSTART.md                # 5-minute getting started guide
ARCHITECTURE.md              # Technical deep dive
DEPLOYMENT.md                # Production deployment guide
PROJECT_STRUCTURE.md         # This file
LICENSE                      # MIT license
```

## Runtime Data (Ignored by Git)

```
backend/data/                 # SQLite database
backend/logs/                 # Application logs
backend/chroma_data/         # ChromaDB vector store
frontend/.next/              # Next.js build output
frontend/node_modules/       # Node dependencies
backend/__pycache__/         # Python cache
```

## Docker Volumes

```yaml
volumes:
  backend-data:              # Persistent database
  backend-logs:              # Persistent logs
  chroma-data:               # Persistent vectors
```

## Key Technologies by File

### Python/Backend
- **FastAPI**: `main.py`, `api/*.py`
- **Playwright**: `scraper/scraper.py`
- **SQLAlchemy**: `models/*.py`
- **ChromaDB**: `rag/rag_engine.py`
- **Anthropic**: `api/chat.py`
- **APScheduler**: `scheduler/scheduler.py`

### TypeScript/Frontend
- **Next.js**: `pages/*.tsx`, `next.config.js`
- **React**: `components/*.tsx`, `pages/*.tsx`
- **Tailwind CSS**: `tailwind.config.js`, `globals.css`
- **Axios**: `lib/api.ts`

### DevOps
- **Docker**: `Dockerfile`, `docker-compose.yml`
- **Bash**: `*.sh` scripts
- **Make**: `Makefile`

## Lines of Code (Approximate)

| Component | Files | Lines |
|-----------|-------|-------|
| Backend Python | 12 | ~1,500 |
| Frontend TypeScript | 8 | ~1,000 |
| Configuration | 10 | ~300 |
| Documentation | 5 | ~2,000 |
| Scripts | 4 | ~200 |
| **Total** | **39** | **~5,000** |

## File Naming Conventions

- **Python**: snake_case (e.g., `scraped_page.py`)
- **TypeScript**: PascalCase for components (e.g., `Chat.tsx`)
- **TypeScript**: camelCase for utilities (e.g., `api.ts`)
- **Config**: lowercase with dots (e.g., `next.config.js`)
- **Documentation**: UPPERCASE (e.g., `README.md`)
- **Scripts**: lowercase (e.g., `start.sh`)

## Import Structure

### Backend
```python
# Standard library
import asyncio
from typing import List

# Third-party
from fastapi import FastAPI
from sqlalchemy.orm import Session

# Local
from app.config import settings
from app.models import ScrapedPage
```

### Frontend
```typescript
// React/Next
import { useState } from 'react';
import Head from 'next/head';

// Third-party
import axios from 'axios';

// Local
import Chat from '@/components/Chat';
import { adminAPI } from '@/lib/api';
```

## Testing Structure (Future)

```
backend/tests/
├── test_scraper.py
├── test_rag.py
├── test_api.py
└── conftest.py

frontend/tests/
├── components/
│   └── Chat.test.tsx
└── pages/
    └── admin.test.tsx
```

## Build Artifacts (Not in Git)

```
frontend/.next/              # Next.js build
frontend/node_modules/       # Dependencies
backend/__pycache__/         # Python cache
backend/data/                # Runtime data
backend/logs/                # Runtime logs
backend/chroma_data/         # Vector DB
.env                         # Local env vars
```

## Total Project Size

- **Source code**: ~5,000 lines
- **Dependencies**: ~500 MB (Docker images)
- **Runtime data**: Variable (depends on scraped sites)

---

This structure is designed to be:
- **Modular**: Clear separation of concerns
- **Scalable**: Easy to add new features
- **Maintainable**: Consistent naming and organization
- **Documented**: Every major component explained

For questions about specific files, see:
- Technical details: ARCHITECTURE.md
- Usage instructions: README.md or QUICKSTART.md
