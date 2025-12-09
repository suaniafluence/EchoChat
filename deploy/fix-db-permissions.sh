#!/bin/bash

# Fix Database Permissions Script
# This script fixes common permission issues with SQLite database

echo "🔧 EchoChat Database Permission Fix"
echo "===================================="
echo ""

# Define paths
BACKEND_DIR="/opt/echochat/backend"
DATA_DIR="${BACKEND_DIR}/data"
DB_FILE="${DATA_DIR}/echochat.db"
SERVICE_USER="www-data"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root (use sudo)"
    exit 1
fi

echo "📁 Checking directories..."

# Create data directory if it doesn't exist
if [ ! -d "$DATA_DIR" ]; then
    echo "   Creating data directory: $DATA_DIR"
    mkdir -p "$DATA_DIR"
else
    echo "   ✓ Data directory exists"
fi

# Set directory permissions
echo "🔐 Setting directory permissions..."
chmod 755 "$DATA_DIR"
chown -R ${SERVICE_USER}:${SERVICE_USER} "$DATA_DIR"
echo "   ✓ Directory permissions set (755, owner: ${SERVICE_USER})"

# Check if database file exists
if [ -f "$DB_FILE" ]; then
    echo "📄 Database file found"
    echo "🔐 Setting database file permissions..."
    chmod 644 "$DB_FILE"
    chown ${SERVICE_USER}:${SERVICE_USER} "$DB_FILE"
    echo "   ✓ Database file permissions set (644, owner: ${SERVICE_USER})"
else
    echo "ℹ️  Database file doesn't exist yet (will be created on first run)"
fi

# Create logs directory if it doesn't exist
LOGS_DIR="${BACKEND_DIR}/logs"
if [ ! -d "$LOGS_DIR" ]; then
    echo "📁 Creating logs directory: $LOGS_DIR"
    mkdir -p "$LOGS_DIR"
fi

chmod 755 "$LOGS_DIR"
chown -R ${SERVICE_USER}:${SERVICE_USER} "$LOGS_DIR"
echo "   ✓ Logs directory permissions set"

echo ""
echo "✅ Permissions fixed successfully!"
echo ""
echo "📋 Summary:"
echo "   - Data directory: $DATA_DIR (755, ${SERVICE_USER})"
echo "   - Database file: $DB_FILE (644, ${SERVICE_USER})"
echo "   - Logs directory: $LOGS_DIR (755, ${SERVICE_USER})"
echo ""
echo "🔄 Restart the backend service to apply changes:"
echo "   sudo systemctl restart echochat-backend"
echo ""
