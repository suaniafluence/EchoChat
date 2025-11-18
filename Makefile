.PHONY: help install dev build start stop logs clean test

help: ## Show this help message
	@echo "EchoChat - Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies (backend and frontend)
	@echo "📦 Installing backend dependencies..."
	cd backend && pip install -r requirements.txt && playwright install chromium
	@echo "📦 Installing frontend dependencies..."
	cd frontend && npm install
	@echo "✅ Dependencies installed"

dev-backend: ## Run backend in development mode
	cd backend && uvicorn app.main:app --reload

dev-frontend: ## Run frontend in development mode
	cd frontend && npm run dev

build: ## Build Docker images
	docker compose build

start: ## Start application with Docker
	@./start.sh

stop: ## Stop application
	@./stop.sh

logs: ## View application logs
	@./logs.sh

clean: ## Clean up data and logs
	@echo "🧹 Cleaning up..."
	rm -rf backend/data backend/logs backend/chroma_data
	rm -rf frontend/.next frontend/node_modules
	@echo "✅ Cleanup complete"

test-backend: ## Run backend tests
	cd backend && pytest

lint-backend: ## Lint backend code
	cd backend && flake8 app/

lint-frontend: ## Lint frontend code
	cd frontend && npm run lint

setup: ## Initial setup (copy .env files)
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env"; fi
	@if [ ! -f backend/.env ]; then cp backend/.env.example backend/.env; echo "Created backend/.env"; fi
	@if [ ! -f frontend/.env.local ]; then cp frontend/.env.local.example frontend/.env.local; echo "Created frontend/.env.local"; fi
	@echo "⚠️  Please edit .env files with your configuration"
