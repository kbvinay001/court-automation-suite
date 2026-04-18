#!/bin/bash
# Court Automation Suite - Deploy Script
set -e

echo "🚀 Court Automation Suite - Deployment"
echo "======================================="

ENV=${1:-production}
echo "📍 Environment: $ENV"

# Validate environment
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Run setup.sh first."
    exit 1
fi

# Build and deploy with Docker Compose
echo ""
echo "🐳 Building Docker images..."
cd docker

# Pull latest base images
docker compose pull mongo redis

# Build application images
docker compose build --no-cache

echo ""
echo "🔄 Stopping existing services..."
docker compose down

echo ""
echo "🚀 Starting services..."
docker compose up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check health
echo ""
echo "🔍 Checking service health..."
HEALTH=$(curl -s http://localhost:8000/health 2>/dev/null || echo "unhealthy")
if echo "$HEALTH" | grep -q "healthy"; then
    echo "  ✅ Backend API is healthy"
else
    echo "  ⚠️  Backend API may still be starting..."
fi

# Check frontend
if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null | grep -q "200"; then
    echo "  ✅ Frontend is running"
else
    echo "  ⚠️  Frontend may still be building..."
fi

# Show container status
echo ""
echo "📊 Container Status:"
docker compose ps

echo ""
echo "======================================="
echo "✅ Deployment complete!"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo ""
echo "Useful commands:"
echo "  docker compose logs -f          # View logs"
echo "  docker compose exec backend python scripts/seed_data.py  # Seed data"
echo "  docker compose down             # Stop all services"
