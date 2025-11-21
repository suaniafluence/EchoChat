#!/bin/bash
# EchoChat - Update Script
# Run this to update the application after git pull

set -e

APP_DIR="/opt/echochat"
BACKEND_DIR="$APP_DIR/backend"
FRONTEND_DIR="$APP_DIR/frontend"
VENV_DIR="$BACKEND_DIR/venv"

echo "=== Updating EchoChat ==="

# Pull latest code
cd $APP_DIR
git pull origin main

# Update backend
echo "Updating backend dependencies..."
source $VENV_DIR/bin/activate
cd $BACKEND_DIR
pip install -r requirements.txt

# Update frontend
echo "Updating frontend..."
cd $FRONTEND_DIR
npm install
npm run build

# Restart services
echo "Restarting services..."
sudo systemctl restart echochat-backend echochat-frontend

echo "=== Update Complete ==="
