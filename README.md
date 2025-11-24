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

## 🚀 Quick Start

### Option 1: Installation Automatique (Recommandé)

```bash
# Clone the repository
git clone https://github.com/yourusername/EchoChat.git
cd EchoChat

# Run installation script
chmod +x install.sh
./install.sh
```

Le script `install.sh` va :
- ✅ Vérifier que Docker et Docker Compose sont installés
- ✅ Créer les fichiers `.env` depuis les exemples
- ✅ Vous demander votre clé API Anthropic et l'URL cible
- ✅ Construire les images Docker
- ✅ Préparer l'application au démarrage

### Option 2: Installation Manuelle

```bash
# Clone and configure
git clone https://github.com/yourusername/EchoChat.git
cd EchoChat
cp .env.example .env

# Edit .env with your settings:
# - TARGET_URL: Website to scrape
# - ANTHROPIC_API_KEY: Your Anthropic API key
# - SCRAPE_FREQUENCY_HOURS: Scraping frequency (default: 24)

# Build and start
docker compose up -d
```

## 📜 Scripts de Démarrage

EchoChat inclut plusieurs scripts pour faciliter l'utilisation :

### `./start.sh` - Démarrer l'application

```bash
./start.sh
```

Ce script :
- ✅ Vérifie que le fichier `.env` existe (sinon le copie depuis `.env.example`)
- ✅ Vérifie que Docker est en cours d'exécution
- ✅ Démarre les conteneurs en mode détaché
- ✅ Affiche les URLs d'accès (frontend, admin, API docs)

### `./logs.sh` - Voir les logs

```bash
./logs.sh
```

Affiche les logs en temps réel des conteneurs backend et frontend. Appuyez sur `Ctrl+C` pour quitter.

### `./stop.sh` - Arrêter l'application

```bash
./stop.sh
```

Arrête proprement tous les conteneurs Docker.

### Commandes Docker alternatives

Si vous préférez utiliser Docker directement :

```bash
# Démarrer
docker compose up -d

# Voir les logs
docker compose logs -f

# Arrêter
docker compose down

# Voir le statut
docker compose ps
```

## 🎯 Utilisation

### 1. Accès à l'application

Après le démarrage, accédez à :

- **Application principale** : http://localhost:3000
- **Panel Admin** : http://localhost:3000/admin
- **Documentation API** : http://localhost:8000/docs

### 2. Premier scraping

1. Visitez http://localhost:3000/admin
2. Entrez l'URL cible dans le formulaire
3. Cliquez sur "Start Scraping"
4. Attendez que le job se termine (suivez la progression dans les logs)
5. Retournez sur http://localhost:3000 pour voir le clone de la page d'accueil et le chat

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
| `ANTHROPIC_MODEL` | Claude model to use | `claude-sonnet-4-5-20250929` |
| `SCRAPE_FREQUENCY_HOURS` | Scraping frequency | `24` |
| `SCRAPER_TIMEOUT` | Page timeout (ms) | `30000` |
| `SCRAPE_JOB_TIMEOUT` | Total job timeout (s) | `7200` |
| `CHUNK_SIZE` | Text chunk size for RAG | `1000` |
| `TOP_K_RESULTS` | Number of RAG results | `5` |

**Frontend** (`.env.local`):

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |

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
