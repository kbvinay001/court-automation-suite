# ⚖️ Court Automation Suite

Full-stack platform for Indian court case tracking, cause list monitoring, AI-powered analytics, and WhatsApp integration.

## Features

- **🔍 Case Search & Tracking** — Search across High Courts, District Courts, and Supreme Court
- **📅 Cause List Monitoring** — Daily cause list scraping with alerts
- **📊 Analytics Dashboard** — Court performance, trends, and AI predictions
- **🤖 AI Analysis** — Case summarization, outcome prediction, entity extraction (OpenAI)
- **📱 WhatsApp Assistant** — Manage cases via WhatsApp with n8n workflows
- **📁 Google Drive Integration** — File management from WhatsApp
- **📧 Notifications** — Email + WhatsApp alerts for hearing reminders
- **🐳 Docker Deployment** — One-command setup with Docker Compose

## Architecture

```
Frontend (Next.js) ←→ Backend (FastAPI) ←→ MongoDB + Redis
                           ↕
                     Celery Workers → Scrapers, Notifications, PDF Reports
                           ↕
                  ML Models (scikit-learn) + OpenAI GPT-4
```

## Quick Start

### Using Docker (recommended)
```bash
cp .env.example .env      # Configure API keys
cd docker
docker compose up -d       # Start all services
```

### Local Development
```bash
# Backend
pip install -r requirements.txt
cd backend && uvicorn main:app --reload

# Frontend
cd frontend && npm install && npm run dev

# Workers
celery -A backend.workers.celery_app worker --loglevel=info
```

**Backend:** http://localhost:8000 | **Frontend:** http://localhost:3000 | **API Docs:** http://localhost:8000/docs

## Project Structure

```
court-automation-suite/
├── backend/                 # FastAPI backend
│   ├── api/routes/          # API endpoints
│   ├── api/models/          # Pydantic data models
│   ├── api/services/        # Business logic
│   ├── scrapers/            # Court website scrapers
│   ├── workers/             # Celery background tasks
│   └── utils/               # Database, cache, validators
├── frontend/                # Next.js frontend
│   ├── components/          # React components
│   ├── pages/               # App pages
│   └── styles/              # Global CSS
├── whatsapp-assistant/      # WhatsApp bot + n8n
├── ml-models/               # ML prediction models
├── docker/                  # Docker configs
├── docs/                    # Documentation
├── tests/                   # Test suites
└── scripts/                 # Setup & deploy scripts
```

## Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | Next.js 14, React, TypeScript, Tailwind CSS |
| Backend | FastAPI, Python 3.11, Pydantic |
| Database | MongoDB 7, Redis 7 |
| Task Queue | Celery 5 |
| Scraping | httpx, BeautifulSoup4, pdfplumber |
| AI | OpenAI GPT-4, scikit-learn |
| Deployment | Docker Compose |

## Documentation

- [API Reference](docs/API.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## License

MIT
