#!/bin/bash
# EchoChat - AWS Ubuntu Deployment Setup Script
# This script sets up the environment on an AWS Ubuntu server

set -e

APP_DIR="/opt/echochat"
BACKEND_DIR="$APP_DIR/backend"
FRONTEND_DIR="$APP_DIR/frontend"
VENV_DIR="$BACKEND_DIR/venv"

echo "=== EchoChat AWS Ubuntu Setup ==="

# Update system
echo "[1/8] Updating system packages..."
sudo apt-get update && sudo apt-get upgrade -y

# Install dependencies
echo "[2/8] Installing system dependencies..."
sudo apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    nodejs \
    npm \
    git \
    curl \
    build-essential \
    libffi-dev \
    libssl-dev

# Install Node.js 18 LTS
echo "[3/8] Installing Node.js 18..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Create app directory
echo "[4/8] Creating application directory..."
sudo mkdir -p $APP_DIR
sudo chown -R $USER:$USER $APP_DIR

# Clone or update repository
echo "[5/8] Setting up application code..."
if [ -d "$APP_DIR/.git" ]; then
    cd $APP_DIR
    git pull origin main
else
    git clone https://github.com/suaniafluence/EchoChat.git $APP_DIR
fi

# Setup backend venv
echo "[6/8] Setting up Python virtual environment..."
cd $BACKEND_DIR
python3.11 -m venv $VENV_DIR
source $VENV_DIR/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
echo "[7/8] Installing Playwright browsers..."
playwright install chromium
playwright install-deps chromium

# Setup frontend
echo "[8/8] Building frontend..."
cd $FRONTEND_DIR
npm install
npm run build

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Copy your .env file to: $BACKEND_DIR/.env"
echo "2. Copy your .env.local file to: $FRONTEND_DIR/.env.local"
echo "3. Configure nginx and systemctl manually"
echo "4. Run: sudo systemctl start echochat-backend echochat-frontend"
echo ""
echo "Application paths:"
echo "  Backend:  $BACKEND_DIR"
echo "  Frontend: $FRONTEND_DIR"
echo "  Venv:     $VENV_DIR"
