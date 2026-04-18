# Deployment Guide

## Prerequisites
- Docker & Docker Compose v2+
- Node.js 20+ (for local frontend dev)
- Python 3.11+ (for local backend dev)
- MongoDB 7+ (or use Docker)
- Redis 7+ (or use Docker)

## Quick Start (Docker)

### 1. Clone and Configure
```bash
git clone <repo-url> court-automation-suite
cd court-automation-suite
cp .env.example .env
# Edit .env with your API keys and credentials
```

### 2. Build and Run
```bash
cd docker
docker compose up -d --build
```

Services will start:
- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:3000
- **MongoDB**: localhost:27017
- **Redis**: localhost:6379

### 3. Seed Database
```bash
docker compose exec backend python scripts/seed_data.py
```

### 4. Verify
```bash
curl http://localhost:8000/health
```

## Local Development

### Backend
```bash
pip install -r requirements.txt
cd backend
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Celery Workers
```bash
celery -A backend.workers.celery_app worker --loglevel=info
celery -A backend.workers.celery_app beat --loglevel=info
```

## Production Deployment

### Environment Variables
Set all variables from `.env.example` in your production environment. Critical ones:
- `MONGODB_URL` — Production MongoDB connection string
- `REDIS_URL` — Production Redis URL
- `OPENAI_API_KEY` — For AI features
- `TWILIO_*` — For WhatsApp notifications

### Security Checklist
- [ ] Change all default credentials
- [ ] Enable MongoDB authentication
- [ ] Use Redis with password
- [ ] Set up HTTPS/TLS with nginx reverse proxy
- [ ] Configure CORS origins for your domain
- [ ] Set `ALLOWED_USERS` for WhatsApp bot
- [ ] Enable rate limiting

### Monitoring
- Health check: `GET /health`
- Docker health checks configured for all services
- Celery Flower for task monitoring: `celery -A backend.workers.celery_app flower`

### Scaling
```bash
# Scale workers
docker compose up -d --scale celery-worker=4

# Backend workers (in Dockerfile CMD)
uvicorn backend.main:app --workers 4
```

### Backup
```bash
# MongoDB backup
docker compose exec mongo mongodump --out /data/backup

# Redis persistence enabled via appendonly
```
