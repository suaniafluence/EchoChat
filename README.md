# EchoChat 🤖

**EchoChat** is a full-stack application that scrapes entire websites in-depth, indexes content using RAG (Retrieval Augmented Generation), and provides an AI-powered chat interface using the Anthropic Claude API. The homepage displays a pixel-perfect clone of the scraped site's home page with an integrated chat widget.

## 🌟 Features

- **Deep Web Scraping**: Recursively scrapes entire websites (same domain only) using Playwright
- **RAG Pipeline**: Indexes content with ChromaDB and sentence-transformers embeddings
- **AI Chat**: Anthropic Claude-powered chat that answers questions based on scraped content
- **Pixel-Perfect Clone**: Displays the original homepage with integrated chat
- **Automated Scraping**: Configurable scheduled scraping (default: daily)
- **Admin Dashboard**: Web UI for configuration, monitoring, and manual scraping
- **Docker Ready**: Full containerization with docker-compose
- **Mobile-First**: Responsive design with Tailwind CSS
- **Multi-Language**: Supports all languages (primarily optimized for French)

## 🏗️ Architecture

### Backend (Python/FastAPI)
- **Scraper**: Playwright headless browser for deep crawling
- **RAG**: ChromaDB vector store + sentence-transformers
- **API**: RESTful endpoints for chat and administration
- **Scheduler**: APScheduler for automated scraping
- **Database**: SQLite for metadata

### Frontend (Next.js/React)
- **Main Page**: Pixel-perfect homepage clone + chat widget
- **Admin Panel**: Configuration and monitoring dashboard
- **Mobile-First**: Tailwind CSS responsive design

## 📋 Prerequisites

- **Docker & Docker Compose** (recommended)
- **OR** Manual setup:
  - Python 3.11+
  - Node.js 18+
  - Anthropic API key

## 🚀 Quick Start with Docker

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/EchoChat.git
cd EchoChat
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and set your configuration:

```env
TARGET_URL=https://www.yoursite.fr
ANTHROPIC_API_KEY=your_anthropic_api_key_here
SCRAPE_FREQUENCY_HOURS=24
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Start the application

```bash
docker compose up -d
```

This will:
- Build and start the backend (port 8000)
- Build and start the frontend (port 3000)
- Create persistent volumes for data

### 4. Access the application

- **Main App**: http://localhost:3000
- **Admin Panel**: http://localhost:3000/admin
- **API Docs**: http://localhost:8000/docs

### 5. Start your first scrape

1. Visit http://localhost:3000/admin
2. Enter the target URL
3. Click "Start Scraping"
4. Wait for the scraping job to complete
5. Visit http://localhost:3000 to see the cloned homepage and chat

## 🛠️ Manual Installation

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run the backend
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local
# Edit .env.local with your API URL

# Run the frontend
npm run dev
```

## 📁 Project Structure

```
EchoChat/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration management
│   │   ├── models/              # Database models
│   │   ├── scraper/             # Web scraping module
│   │   ├── rag/                 # RAG pipeline
│   │   ├── api/                 # API endpoints
│   │   ├── scheduler/           # Automated tasks
│   │   └── utils/               # Utilities (logging, etc.)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── pages/
│   │   ├── index.tsx            # Main page
│   │   └── admin.tsx            # Admin dashboard
│   ├── components/
│   │   └── Chat.tsx             # Chat widget
│   ├── lib/
│   │   └── api.ts               # API client
│   ├── styles/
│   │   └── globals.css          # Global styles
│   ├── package.json
│   ├── Dockerfile
│   └── .env.local.example
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🔧 Configuration

### Environment Variables

**Backend** (`backend/.env`):

| Variable | Description | Default |
|----------|-------------|---------|
| `TARGET_URL` | Website to scrape | `https://www.example.fr` |
| `ANTHROPIC_API_KEY` | Anthropic API key | Required |
| `ANTHROPIC_MODEL` | Claude model to use | `claude-3-5-sonnet-20241022` |
| `SCRAPE_FREQUENCY_HOURS` | Scraping frequency | `24` |
| `RESPECT_ROBOTS_TXT` | Respect robots.txt | `False` |
| `CHUNK_SIZE` | Text chunk size for RAG | `1000` |
| `TOP_K_RESULTS` | Number of RAG results | `5` |

**Frontend** (`.env.local`):

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |

## 🎯 Usage

### Admin Panel Features

1. **Statistics Dashboard**: View total pages, chunks, and last scrape time
2. **Manual Scraping**: Start a new scraping job on-demand
3. **Job History**: Monitor recent scraping jobs and their status
4. **Real-time Updates**: Auto-refresh every 5 seconds

### Chat Interface

- Click the chat bubble on the homepage
- Ask questions about the website content
- Responses are based solely on scraped content
- Sources are cited for transparency

## 🌐 Deployment

### Backend Deployment (Free Options)

#### Render.com

1. Create a new Web Service
2. Connect your GitHub repository
3. Select `backend` as root directory
4. Build command: `pip install -r requirements.txt && playwright install chromium`
5. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables from `.env`

#### Railway.app

1. Create new project from GitHub repo
2. Select backend service
3. Add environment variables
4. Deploy automatically

#### Fly.io

```bash
cd backend
fly launch
fly secrets set ANTHROPIC_API_KEY=your_key
fly deploy
```

### Frontend Deployment (Vercel)

1. Import your repository to Vercel
2. Set root directory to `frontend`
3. Add environment variable:
   - `NEXT_PUBLIC_API_URL`: Your backend URL
4. Deploy

## 📊 API Endpoints

### Chat API

**POST** `/api/chat`
```json
{
  "message": "What is this website about?",
  "conversation_history": []
}
```

### Admin API

**POST** `/api/admin/scrape` - Start scraping job
**GET** `/api/admin/jobs` - Get recent jobs
**GET** `/api/admin/jobs/{id}` - Get specific job
**GET** `/api/admin/stats` - Get system statistics
**GET** `/api/admin/homepage` - Get homepage HTML

## 🔍 How It Works

1. **Scraping**: Playwright visits the target URL and recursively follows internal links
2. **Storage**: Page content and HTML are stored in SQLite
3. **Indexing**: Content is chunked and embedded using sentence-transformers
4. **RAG**: Embeddings are stored in ChromaDB for fast similarity search
5. **Chat**: User questions trigger:
   - RAG retrieval of relevant contexts
   - Prompt construction with contexts
   - Anthropic API call for response generation
6. **Display**: Homepage HTML is rendered with an integrated chat widget

## 🔒 Important Notes

### Security

- **robots.txt**: By default, this tool **does not respect** robots.txt. Use responsibly.
- **Rate Limiting**: Built-in delays (0.5s) between requests to be polite
- **API Keys**: Never commit API keys to version control

### Limitations

- Scrapes only the same domain (no external links)
- JavaScript-heavy sites may require additional wait times
- Large sites can take significant time and storage

## 🐛 Troubleshooting

### Playwright errors

```bash
# Install system dependencies
playwright install-deps chromium
```

### ChromaDB errors

```bash
# Clear ChromaDB data
rm -rf backend/chroma_data
```

### Frontend can't connect to backend

- Check `NEXT_PUBLIC_API_URL` is correct
- Verify backend is running on the specified port
- Check CORS settings in backend config

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please open an issue on GitHub.

---

Built with ❤️ using FastAPI, Next.js, Anthropic Claude, and ChromaDB
