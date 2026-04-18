# ⚖️ Court Automation Suite

> [!WARNING]
> **🚧 This project is currently under active development.**  
> Expect breaking changes, incomplete features, and rough edges.  
> Not production-ready. Use for development/evaluation only.

Full-stack platform for Indian court case tracking, cause list monitoring, AI-powered analytics, and WhatsApp integration.

---

## 🚀 Quick Start (Windows — One Click)

1. **Prerequisites** — install these once:
   - [Python 3.11+](https://www.python.org/downloads/) — check ✅ *Add to PATH*
   - [Node.js 20+](https://nodejs.org/)
   - [Docker Desktop](https://www.docker.com/products/docker-desktop/) — for MongoDB & Redis

2. **First-time setup:**
   ```bat
   # In the project root:
   python -m venv .venv
   .venv\Scripts\pip install -r requirements.txt
   cd frontend && npm install && cd ..
   copy .env.example .env
   ```

3. **Start everything:**
   ```
   Double-click  start-all.bat
   ```
   The browser will open automatically at **http://localhost:3000** once the frontend is ready.

4. **Stop everything:**
   ```
   Double-click  stop-all.bat
   ```

---

## Features (in progress)

| Feature | Status |
|---------|--------|
| 🔍 Case Search & Tracking | ✅ Working |
| 📅 Cause List Monitoring | ✅ Working |
| 📊 Analytics Dashboard | ✅ Working |
| 🛡️ Auth (JWT) | ✅ Working |
| 🤖 AI Case Analysis (OpenAI) | 🚧 Needs API key |
| 📱 WhatsApp Assistant | 🚧 In development |
| 🔔 Email / WhatsApp Notifications | 🚧 In development |
| 🐳 Full Docker Compose stack | 🚧 In development |
| 📁 Google Drive Integration | 🔜 Planned |
| ✅ Playwright E2E Tests | 🚧 In development |

---

## Architecture

```
Frontend (Next.js 14)
    ↕  REST / JWT
Backend (FastAPI + Python 3.11)
    ↕
MongoDB 7  ←→  Redis 7  ←→  Celery Workers
    ↕
Court Scrapers (httpx + BeautifulSoup + pdfplumber)
    ↕
OpenAI GPT-4 / scikit-learn ML
```

---

## Project Structure

```
court-automation-suite/
├── backend/                 # FastAPI backend
│   ├── api/
│   │   ├── routes/          # auth, scraper, causelist, analytics, reports
│   │   ├── models/          # Pydantic data models
│   │   └── services/        # Business logic layer
│   ├── scrapers/            # High Court / District Court / CauseList scrapers
│   ├── workers/             # Celery background tasks
│   └── utils/               # DB, cache, validators, security
├── frontend/                # Next.js 14 app
│   ├── components/          # React components (Dashboard, CaseSearch, …)
│   ├── pages/               # App pages
│   └── lib/                 # API client, auth context
├── e2e/                     # Playwright E2E test suite
│   ├── pages/               # Page Object Models
│   ├── tests/               # Test specs (auth, search, causelist, PDF)
│   └── fixtures/            # Auth setup fixture
├── whatsapp-assistant/      # WhatsApp bot / n8n workflows
├── ml-models/               # ML prediction models
├── docker/                  # Dockerfiles + docker-compose.yml
├── docs/                    # Documentation
├── tests/                   # pytest unit + integration tests
├── scripts/                 # Utility scripts (secrets scan, seed data, …)
├── start-all.bat            # ← One-click launcher (Windows)
├── stop-all.bat             # ← One-click stopper (Windows)
├── .env.example             # Environment variable template
└── requirements.txt         # Python dependencies
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, React 18, TypeScript, Tailwind CSS |
| Backend | FastAPI, Python 3.11+, Pydantic v2 |
| Database | MongoDB 7, Redis 7 |
| Auth | JWT (access + refresh tokens), bcrypt |
| Task Queue | Celery 5 + Redis broker |
| Scraping | httpx, BeautifulSoup4, pdfplumber, tenacity |
| AI | OpenAI GPT-4, scikit-learn |
| Testing | pytest, Playwright 1.43 |
| Security | bandit, secrets scanner, rate-limiter (slowapi) |
| Deployment | Docker Compose |

---

## Environment Variables

Copy `.env.example` to `.env` and fill in:

```env
# Required
MONGODB_URL=mongodb://localhost:27017
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=change-me-to-something-long-and-random

# Optional (for AI features)
OPENAI_API_KEY=sk-...

# Optional (for notifications)
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
```

---

## Development

```bash
# Backend — runs at http://localhost:8000
cd backend
uvicorn main:app --reload

# Frontend — runs at http://localhost:3000
cd frontend
npm run dev

# Run unit tests
pytest tests/ -v

# Run E2E tests (requires running stack)
cd e2e && npm test

# Security scan
python scripts/scan_secrets.py
.venv/Scripts/bandit -r backend/ --severity-level medium
```

---

## API Reference

Once the backend is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Contributing

This project is in active development. Issues and PRs are welcome.  
Please check `docs/` for architecture notes before making large changes.

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

> **Note:** Court data scraped by this tool is sourced from publicly available Indian court portals.  
> This tool is intended for informational and legal research purposes only.
