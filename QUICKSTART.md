# 🚀 Quick Start Guide

Get EchoChat running in 5 minutes!

## Prerequisites

- Docker Desktop installed and running
- Anthropic API key ([get one here](https://console.anthropic.com/))

## Installation

### Option 1: Automated Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/EchoChat.git
cd EchoChat

# Run the installation script
chmod +x install.sh
./install.sh
```

The script will:
1. Check for Docker
2. Create environment files
3. Prompt for your Anthropic API key
4. Prompt for target URL
5. Build Docker images

### Option 2: Manual Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/EchoChat.git
cd EchoChat

# Copy environment file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your favorite editor
```

Required in `.env`:
```env
TARGET_URL=https://www.example.fr
ANTHROPIC_API_KEY=your_key_here
```

Build and start:
```bash
docker compose build
docker compose up -d
```

## Usage

### Start the application

```bash
./start.sh
# Or: docker compose up -d
```

### Access the application

1. **Admin Panel**: http://localhost:3000/admin
   - Enter target URL
   - Click "Start Scraping"
   - Wait for completion (check status)

2. **Main App**: http://localhost:3000
   - View the cloned homepage
   - Click chat bubble
   - Ask questions about the website

3. **API Docs**: http://localhost:8000/docs
   - Explore API endpoints
   - Test requests

### View logs

```bash
./logs.sh
# Or: docker compose logs -f
```

### Stop the application

```bash
./stop.sh
# Or: docker compose down
```

## Common Commands

```bash
# View running containers
docker compose ps

# Restart a service
docker compose restart backend

# Rebuild after code changes
docker compose build
docker compose up -d

# Clean up everything
docker compose down -v  # Warning: deletes all data!
```

## Troubleshooting

### Backend won't start

```bash
# Check logs
docker compose logs backend

# Common issue: Missing API key
# Solution: Check .env file has ANTHROPIC_API_KEY
```

### Frontend can't reach backend

```bash
# Check backend is running
curl http://localhost:8000/health

# Should return: {"status":"healthy"}
```

### Scraping fails

```bash
# Check target URL is accessible
curl -I https://your-target-url.com

# Increase timeout in .env:
SCRAPER_TIMEOUT=60000
```

### Out of disk space

```bash
# Clean up Docker
docker system prune -a

# Remove old data
rm -rf backend/data backend/logs backend/chroma_data
```

## Next Steps

1. ✅ Complete first scrape
2. ✅ Test chat functionality
3. ✅ Check mobile responsiveness
4. ✅ Configure automated scraping frequency
5. ✅ Deploy to production (see DEPLOYMENT.md)

## Tips

- **First scrape**: Can take several minutes depending on site size
- **Chat quality**: Improves with more scraped content
- **Scheduled scraping**: Runs automatically every 24 hours (configurable)
- **Admin panel**: Auto-refreshes every 5 seconds
- **Mobile**: Chat widget works on all screen sizes

## Getting Help

- 📖 Full documentation: README.md
- 🏗️ Architecture details: ARCHITECTURE.md
- 🚀 Deployment guide: DEPLOYMENT.md
- 🐛 Issues: GitHub Issues

## What's Next?

After your first successful scrape:

1. **Customize frequency**: Change `SCRAPE_FREQUENCY_HOURS` in `.env`
2. **Try different sites**: Update `TARGET_URL` and re-scrape
3. **Deploy to production**: Follow DEPLOYMENT.md
4. **Monitor performance**: Check admin panel regularly

Happy chatting! 🎉
