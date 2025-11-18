#!/bin/bash

set -e

echo "🚀 EchoChat Installation Script"
echo "================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on supported OS
if [[ "$OSTYPE" != "linux-gnu"* ]] && [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}❌ Unsupported OS. This script supports Linux and macOS only.${NC}"
    exit 1
fi

# Check for Docker
echo "🔍 Checking for Docker..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed.${NC}"
    echo "Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
else
    echo -e "${GREEN}✅ Docker found${NC}"
fi

# Check for Docker Compose
echo "🔍 Checking for Docker Compose..."
if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed.${NC}"
    echo "Please install Docker Compose from: https://docs.docker.com/compose/install/"
    exit 1
else
    echo -e "${GREEN}✅ Docker Compose found${NC}"
fi

# Setup environment files
echo ""
echo "📝 Setting up environment files..."

if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✅ Created .env${NC}"
    
    # Prompt for Anthropic API key
    echo ""
    echo -e "${YELLOW}Please enter your Anthropic API key:${NC}"
    read -r ANTHROPIC_KEY
    
    if [ -n "$ANTHROPIC_KEY" ]; then
        sed -i.bak "s/your_anthropic_api_key_here/$ANTHROPIC_KEY/" .env
        rm .env.bak 2>/dev/null || true
        echo -e "${GREEN}✅ API key configured${NC}"
    fi
    
    # Prompt for target URL
    echo ""
    echo -e "${YELLOW}Please enter the target URL to scrape (e.g., https://www.example.fr):${NC}"
    read -r TARGET_URL
    
    if [ -n "$TARGET_URL" ]; then
        sed -i.bak "s|https://www.example.fr|$TARGET_URL|" .env
        rm .env.bak 2>/dev/null || true
        echo -e "${GREEN}✅ Target URL configured${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  .env already exists, skipping${NC}"
fi

if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    # Copy values from root .env if it exists
    if [ -f .env ]; then
        source .env
        sed -i.bak "s/your_anthropic_api_key_here/$ANTHROPIC_API_KEY/" backend/.env 2>/dev/null || true
        sed -i.bak "s|https://www.example.fr|$TARGET_URL|" backend/.env 2>/dev/null || true
        rm backend/.env.bak 2>/dev/null || true
    fi
    echo -e "${GREEN}✅ Created backend/.env${NC}"
else
    echo -e "${YELLOW}⚠️  backend/.env already exists, skipping${NC}"
fi

# Build Docker images
echo ""
echo "🏗️  Building Docker images..."
docker compose build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Docker images built successfully${NC}"
else
    echo -e "${RED}❌ Failed to build Docker images${NC}"
    exit 1
fi

# Success message
echo ""
echo -e "${GREEN}🎉 Installation complete!${NC}"
echo ""
echo "To start EchoChat, run:"
echo "  ./start.sh"
echo ""
echo "Or use:"
echo "  docker compose up -d"
echo ""
echo "Then visit:"
echo "  - Frontend: http://localhost:3000"
echo "  - Admin Panel: http://localhost:3000/admin"
echo "  - API Docs: http://localhost:8000/docs"
echo ""
echo "To view logs:"
echo "  ./logs.sh"
echo ""
echo "To stop:"
echo "  ./stop.sh"
echo ""
