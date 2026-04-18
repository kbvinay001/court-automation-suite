# Court Automation Suite - API Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
All protected endpoints require a JWT Bearer token:
```
Authorization: Bearer <token>
```

---

## Court Scraper Endpoints

### Search Cases
```http
GET /scraper/search?query={query}&court_type={court_type}&court_name={court_name}
```
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| query | string | Yes | Case number or party name |
| court_type | string | No | `high_court`, `district_court`, `supreme_court` |
| court_name | string | No | Specific court name |

**Response:** `{ "data": [CaseResponse], "total": int }`

### Get Case Details
```http
GET /scraper/case/{case_number}
```

### Scrape Case
```http
POST /scraper/scrape
```
```json
{
  "case_number": "WP(C)/1234/2024",
  "court_type": "high_court",
  "court_name": "Delhi High Court"
}
```

### Batch Scrape
```http
POST /scraper/batch-scrape
```
```json
{
  "case_numbers": ["WP(C)/1234/2024", "CS/890/2024"],
  "court_type": "high_court",
  "court_name": "Delhi High Court"
}
```

### Track / Untrack Case
```http
POST /scraper/track/{case_number}
DELETE /scraper/track/{case_number}
```

### List Tracked Cases
```http
GET /scraper/tracked
```

### Upcoming Hearings
```http
GET /scraper/hearings/upcoming?days=7
```

### Supported Courts
```http
GET /scraper/courts
```

---

## Cause List Endpoints

### Today's Cause List
```http
GET /causelist/today?court_name={court_name}
```

### Cause List by Date
```http
GET /causelist/{date}?court_name={court_name}
```
Date format: `YYYY-MM-DD`

### Search Cause List
```http
GET /causelist/search?case_number={case_number}&court_name={court_name}
```

### Monitor Case
```http
POST /causelist/monitor
```
```json
{
  "case_number": "WP(C)/1234/2024",
  "court_name": "Delhi High Court"
}
```

### Refresh Cause List
```http
POST /causelist/refresh?court_name={court_name}
```

### Weekly Cause List
```http
GET /causelist/weekly?court_name={court_name}
```

---

## Analytics Endpoints

### Dashboard
```http
GET /analytics/dashboard
```

### Case Trends
```http
GET /analytics/trends?period=30&court_name={court_name}
```

### Court Performance
```http
GET /analytics/court-performance?court_name={court_name}
```

### Case Type Distribution
```http
GET /analytics/case-types?court_name={court_name}
```

### AI Predictions
```http
GET /analytics/predictions?case_number={case_number}
```

### Hearing Heatmap
```http
GET /analytics/heatmap?court_name={court_name}
```

---

## Health Check
```http
GET /health
```
**Response:** `{ "status": "healthy", "timestamp": "ISO-8601" }`

## Error Responses
All errors return:
```json
{
  "detail": "Error description",
  "status_code": 400
}
```

| Code | Description |
|------|-------------|
| 400 | Bad Request |
| 404 | Not Found |
| 422 | Validation Error |
| 429 | Rate Limit Exceeded |
| 500 | Internal Server Error |
