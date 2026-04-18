# Architecture Overview

## System Architecture

```
┌──────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Frontend   │────▶│   Backend API    │────▶│   MongoDB       │
│   (Next.js)  │     │   (FastAPI)      │     │   (Database)    │
└──────────────┘     └──────────────────┘     └─────────────────┘
                            │    │
                     ┌──────┘    └──────┐
                     ▼                  ▼
              ┌──────────────┐  ┌──────────────┐
              │    Redis     │  │   Celery     │
              │   (Cache)    │  │  (Workers)   │
              └──────────────┘  └──────────────┘
                                       │
                     ┌─────────────────┼─────────────────┐
                     ▼                 ▼                  ▼
              ┌──────────────┐ ┌──────────────┐  ┌──────────────┐
              │   Scrapers   │ │ Notifications│  │  WhatsApp    │
              │ (Court Sites)│ │ (Email/SMS)  │  │  Assistant   │
              └──────────────┘ └──────────────┘  └──────────────┘
```

## Components

### Backend (FastAPI)
- **`main.py`** — Application entry point, lifespan management, CORS, route registration
- **`api/routes/`** — REST endpoints for scraping, cause lists, analytics
- **`api/models/`** — Pydantic data models (Case, CauseList, User)
- **`api/services/`** — Business logic (scraping, PDF generation, notifications, AI)
- **`utils/`** — Database (Motor/MongoDB), cache (Redis), validators

### Scrapers
- **`HighCourtScraper`** — Scrape from 10+ High Court websites
- **`DistrictCourtScraper`** — Scrape from eCourts India platform
- **`CauseListScraper`** — Parse HTML/PDF cause lists daily
- **`IntelligentScraper`** — AI-powered adaptive scraper that learns page structures

### Workers (Celery)
- **`celery_app.py`** — Task queue configuration with beat scheduler
- **`tasks.py`** — Background tasks: scraping, notifications, cleanup, PDF reports

### Frontend (Next.js)
- **`Dashboard`** — Overview with stats, upcoming hearings, trends
- **`CaseSearch`** — Search and track cases across courts
- **`CauseListMonitor`** — View and monitor daily cause lists
- **`Analytics`** — Charts, predictions, court performance metrics

### WhatsApp Assistant
- **`DriveHandler`** — Google Drive operations via WhatsApp
- **`AIHandler`** — AI-powered analysis, predictions, Q&A via WhatsApp
- **n8n Workflows** — Automation workflows for Drive, calendar, notifications

### ML Models
- **`CasePredictor`** — Random Forest + Gradient Boosting for hearing/outcome prediction
- **`CauseListAnalyzer`** — Volume trends, anomaly detection, judge workload, efficiency scoring

## Data Flow

1. **Scraping** → Court websites scraped → data stored in MongoDB → cached in Redis
2. **Notifications** → Celery beat triggers checks → case updates detected → notifications sent
3. **API Requests** → Frontend/WhatsApp → FastAPI → Redis cache check → MongoDB → response
4. **ML Predictions** → Case data → feature engineering → model inference → prediction response

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js, React, TypeScript, Tailwind CSS |
| Backend API | FastAPI, Python 3.11, Pydantic |
| Database | MongoDB 7 (Motor async driver) |
| Cache | Redis 7 (async redis-py) |
| Task Queue | Celery 5 with Redis broker |
| Scraping | httpx, BeautifulSoup4, pdfplumber |
| AI | OpenAI GPT-4, scikit-learn |
| Notifications | Twilio (WhatsApp), SMTP (Email) |
| Deployment | Docker Compose, nginx |
