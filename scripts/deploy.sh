#!/bin/bash
set -e  # Stop on first error

echo "🚀 Starting deployment..."

PROJECT_DIR="/home/ubuntu/rag-ecommerce"
cd $PROJECT_DIR

# Git pull
echo "📥 Pulling latest code..."
git pull origin main

# Docker
echo "🐳 Rebuilding Docker..."
docker compose down
docker compose build --no-cache
docker compose up -d

# Wait & health check
echo "⏳ Waiting for app to start..."
sleep 15

echo "✅ Health check..."
if curl -sf http://localhost:8000/health > /dev/null; then
    echo "✅ App is healthy!"
else
    echo "⚠️ Health check failed - checking logs..."
    docker compose logs --tail=50
    exit 1
fi

echo "🎉 Deployment successful!"
docker compose ps