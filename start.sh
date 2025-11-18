#!/bin/bash

echo "🚀 Starting EchoChat..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your configuration before continuing."
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Start services
echo "📦 Building and starting containers..."
docker compose up -d

echo ""
echo "✅ EchoChat is starting!"
echo ""
echo "📍 Access points:"
echo "   - Frontend: http://localhost:3000"
echo "   - Admin Panel: http://localhost:3000/admin"
echo "   - API Docs: http://localhost:8000/docs"
echo ""
echo "📝 To view logs: docker compose logs -f"
echo "🛑 To stop: docker compose down"
