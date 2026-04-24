# Wasel Palestine 🗺️
### Smart Mobility & Checkpoint Intelligence Platform

> A RESTful API backend platform that helps Palestinians navigate daily movement challenges by providing real-time checkpoint intelligence, crowdsourced incident reporting, and smart route estimation.

---

## Table of Contents
- [System Overview](#system-overview)
- [Tech Stack Justification](#tech-stack-justification)
- [Architecture](#architecture)
- [Database Schema (ERD)](#database-schema-erd)
- [API Design](#api-design)
- [External API Integrations](#external-api-integrations)
- [Authentication & Authorization](#authentication--authorization)
- [Testing Strategy](#testing-strategy)
- [Performance Testing Results](#performance-testing-results)
- [Setup & Installation](#setup--installation)

---

## System Overview

Wasel Palestine is an API-centric platform that aggregates mobility intelligence across the West Bank. The system provides:

- **Checkpoint Management** — Real-time status tracking for military, commercial, and internal checkpoints with full status history (open, closed, restricted, delayed, unknown)
- **Incident Reporting** — Crowdsourced reports from citizens with moderation, voting, and automatic clustering
- **Route Estimation** — Smart route planning using three interchangeable strategies: fastest, safest, and balanced
- **Alert Subscriptions** — Users subscribe to regional alerts triggered by verified incidents
- **External Data** — Live weather and geolocation data from OpenWeatherMap and OpenRouteService
- **Prediction** — Risk-based checkpoint status prediction using historical patterns, time-of-day, and day-of-week signals
- **Reputation System** — User credibility scoring that fast-tracks reports from trusted contributors

The system is designed exclusively as a backend API — no frontend is included. All functionality is exposed through versioned RESTful endpoints (`/api/v1/...`).

---

## Tech Stack Justification

| Component | Technology | Version | Justification |
|-----------|-----------|---------|---------------|
| Backend | FastAPI (Python) | 0.111.0 | Async-first, automatic OpenAPI docs, high performance, type safety via Pydantic |
| Database | PostgreSQL | 16-alpine | ACID compliance, ENUM types, JSONB support, window functions |
| Cache | Redis | 7-alpine | In-memory TTL-based caching for weather, routes, predictions, and stats |
| ORM | SQLAlchemy (async) | 2.0.30 | Async support via asyncpg, raw SQL for complex aggregations |
| Validation | Pydantic | 2.7.1 | Schema validation, settings management |
| Auth | JWT (python-jose) | 3.3.0 | Stateless, scalable, supports access + refresh token flow |
| HTTP Client | httpx | ≥0.28.1 | Async HTTP client for external API calls |
| Deployment | Docker + Docker Compose | — | Reproducible environments, one-command setup |
| Load Testing | k6 | — | Modern, scriptable, supports all required test scenarios |

**Why FastAPI over Django/Spring Boot?**
- Native async support handles concurrent checkpoint queries efficiently
- Automatic Swagger/OpenAPI generation at `/docs` reduces documentation overhead
- Pydantic v2 validation catches schema errors before they reach the database
- Lighter footprint than Spring Boot for a purely API-focused project

---

## Architecture

![Architecture Diagram](docs/architecture.png)


### Layer Responsibilities

| Layer | Responsibility |
|-------|---------------|
| **Routers** | HTTP request/response, parameter validation, dependency injection |
| **Services** | Business logic, orchestration, caching decisions |
| **Repositories** | Database queries (ORM + raw SQL), data access abstraction |
| **Strategies** | Interchangeable route-computation algorithms (Strategy Pattern) |

---

## Database Schema (ERD)

The database consists of **11 tables** and **10 custom ENUM types**.

### ERD Diagram

![Entity Relationship Diagram](docs/erd.png)

### Tables Overview

| Table | Description |
|-------|-------------|
| `users` | Platform users with roles (citizen, moderator, admin) and reputation scoring |
| `refresh_tokens` | Stored refresh tokens with hash, expiry, and revocation flag for session management |
| `checkpoints` | Military, commercial, and internal checkpoint registry with bilingual names (AR/EN) |
| `checkpoint_status_history` | Immutable audit log of all checkpoint status changes with reason tracking |
| `incidents` | Verified mobility incidents categorized by type, severity, and lifecycle status |
| `reports` | Crowdsourced citizen reports with moderation workflow, confidence scoring, and voting |
| `report_votes` | Community up/down voting on report credibility (`vote_type` ENUM) |
| `alert_subscriptions` | User subscriptions to regional/category alerts (filterable by region + category) |
| `alerts` | Alert records triggered by verified incidents, linked to specific incidents |
| `route_cache` | PostgreSQL-level route cache storing origin, destination, strategy, and JSON response with TTL |
| `weather_cache` | PostgreSQL-level weather cache per region with JSON data and TTL expiry |

### ENUM Types (10 total)

| ENUM Name | Values |
|-----------|--------|
| `user_role` | citizen, moderator, admin |
| `checkpoint_type` | military, commercial, internal |
| `checkpoint_status` | open, closed, restricted, delayed, unknown |
| `incident_category` | closure, delay, accident, weather_hazard, military_activity, other |
| `incident_severity` | low, medium, high, critical |
| `incident_status` | active, verified, resolved, rejected |
| `report_category` | checkpoint, road_closure, delay, accident, weather, other |
| `report_status` | pending, accepted, rejected, duplicate |
| *(vote_type)* | upvote, downvote *(in report_votes)* |
| *(alert category)* | string field — inherits from incident category |

### Key Relationships

- A **user** can create many **reports**, **incidents**, and **subscriptions**
- A **checkpoint** maintains a full **status_history** audit log (immutable append-only)
- **Reports** are clustered into **incidents** automatically via the Haversine clustering algorithm
- **Incidents** trigger **alerts** for subscribed users matching region/category filters
- Both **route** and **weather** data are cached in Redis with TTL fallback to `cache_entries`

---

## API Design

All endpoints follow RESTful conventions under `/api/v1/`.
Interactive API docs available at `https://remark-splendor-junior.ngrok-free.dev/docs` (Swagger UI) and API Dog `fmnmzxpiji.apidog.io`.

### Endpoint Reference

| Group | Base Path | Method | Endpoint | Auth |
|-------|-----------|--------|----------|------|
| **Auth** | `/api/v1/auth` | POST | `/register` | Public |
| | | POST | `/login` | Public |
| | | POST | `/refresh` | Public (refresh token) |
| | | POST | `/logout` | JWT |
| | | GET | `/me` | JWT |
| **Users** | `/api/v1/users` | GET | `/` | Admin |
| | | GET | `/{id}` | JWT |
| | | PUT | `/{id}` | JWT (self) |
| | | DELETE | `/{id}` | Admin |
| **Checkpoints** | `/api/v1/checkpoints` | GET | `/` | Public (paginated, filterable) |
| | | GET | `/{id}` | Public |
| | | POST | `/` | Moderator+ |
| | | PUT | `/{id}` | Moderator+ |
| | | DELETE | `/{id}` | Admin |
| | | PATCH | `/{id}/status` | Moderator+ |
| | | GET | `/{id}/history` | Public |
| **Incidents** | `/api/v1/incidents` | GET | `/` | Public (paginated, filterable) |
| | | GET | `/{id}` | Public |
| | | POST | `/` | JWT |
| | | PUT | `/{id}` | Moderator+ |
| | | DELETE | `/{id}` | Admin |
| | | PATCH | `/{id}/status` | Moderator+ |
| **Reports** | `/api/v1/reports` | GET | `/` | Moderator+ |
| | | GET | `/my` | JWT |
| | | POST | `/` | JWT |
| | | PATCH | `/{id}/moderate` | Moderator+ |
| | | POST | `/{id}/vote` | JWT |
| **Routes** | `/api/v1/routes` | POST | `/estimate` | JWT |
| | | GET | `/strategies` | Public |
| **Alerts** | `/api/v1/alerts` | GET | `/` | JWT |
| | | GET | `/subscriptions` | JWT |
| | | POST | `/subscriptions` | JWT |
| | | DELETE | `/subscriptions/{id}` | JWT |
| **Stats** | `/api/v1/stats` | GET | `/checkpoints` | Public |
| | | GET | `/incidents` | Public |
| | | GET | `/reports` | Moderator+ |
| **External** | `/api/v1/external` | GET | `/weather` | JWT |
| | | GET | `/geocode` | JWT |
| **Predict** | `/api/v1/predict` | GET | `/checkpoint/{id}` | JWT |
| | | GET | `/region/{name}` | JWT |

### Design Decisions

**Versioning:** All routes are prefixed with `/api/v1/` to support future breaking changes without disrupting existing clients.

**Raw SQL for Statistics:** The `/stats` endpoints use raw SQL queries intentionally to demonstrate complex aggregations (`GROUP BY`, `CASE WHEN`, `COUNT`) that are harder to express cleanly in ORM syntax.

**Strategy Pattern for Routes:** Route estimation uses the Strategy design pattern with an abstract base class (`RouteStrategy`) and three interchangeable implementations — `FastestStrategy`, `SafestStrategy`, `BalancedStrategy` — making it easy to add new routing strategies without modifying existing code. Strategy is selected per request via the `strategy` field in the request body.

**Clustering Algorithm:** Reports within **500 metres**, **same category**, and within a **2-hour window** are automatically grouped using the Haversine formula for geodesic distance. When a cluster reaches 3+ reports, an incident is created automatically.

```python
# Clustering thresholds (ClusteringService)
MAX_DISTANCE_M   = 500    # metres — Haversine distance
MAX_TIME_DIFF_H  = 2      # hours  — report time window
MIN_CLUSTER_SIZE = 3      # reports needed to auto-create incident
```

**Reputation System:** User credibility is calculated as:

```
reputation = (valid_reports / total_reports) * 5.0
```

Users with `reputation > 3.5` have their reports fast-tracked to moderators.

**Pagination:** All list endpoints (checkpoints, incidents, reports) enforce mandatory pagination (`page`, `limit`) with server-side defaults. This prevents full table scans.

**Prediction Model:** Checkpoint risk scoring uses a weighted factor model combining historical closure rates, active incidents, time-of-day, day-of-week, and report volume:

```python
# Prediction weights (PredictionService)
WEIGHT_RECENT_CLOSURE  = 0.40
WEIGHT_INCIDENT_ACTIVE = 0.30
WEIGHT_HOUR_OF_DAY     = 0.15
WEIGHT_DAY_OF_WEEK     = 0.10
WEIGHT_REPORT_VOLUME   = 0.05
```

Risk labels map to predicted statuses: `low → open`, `medium → delayed`, `high → restricted`, `critical → closed`.

**CORS:** All origins are allowed (`*`) for development. This should be restricted to known client domains in production.

---

## External API Integrations

### 1. OpenWeatherMap

| Property | Detail |
|----------|--------|
| Purpose | Real-time weather data per region |
| Endpoint | `api.openweathermap.org/data/2.5/weather` |
| Redis TTL | 30 minutes (`TTL_WEATHER = 1800`) |
| Timeout | 10 seconds |
| Fallback | Returns cached data on failure; logs warning |
| Auth | `OPENWEATHER_API_KEY` environment variable |

### 2. OpenRouteService

| Property | Detail |
|----------|--------|
| Purpose | Geographic routing, distance calculation, geocoding |
| Endpoint | `api.openrouteservice.org/v2/directions` |
| Redis TTL | 5 minutes (`TTL_ROUTES = 300`) |
| Timeout | 15 seconds |
| Fallback | Graceful degradation with heuristic-based fallback route |
| Auth | `OPENROUTESERVICE_API_KEY` environment variable |

Both integrations follow these principles:
- API keys stored in `.env` — never committed to Git
- All responses cached to Redis to minimize external calls and respect rate limits
- Timeouts configured to prevent hanging requests
- Errors caught and logged without crashing the application
- Geocode results cached for 60 minutes (`TTL_GEOCODE = 3600`)

### Redis Cache TTL Summary

| Key Pattern | TTL | Source |
|-------------|-----|--------|
| `weather:<region>` | 30 min | OpenWeatherMap |
| `routes:<hash>` | 5 min | OpenRouteService |
| `stats:checkpoints` | 10 min | PostgreSQL |
| `checkpoints:list:<region>` | 2 min | PostgreSQL |
| `predict:checkpoint:<id>` | 15 min | PredictionService |
| `predict:region:<name>` | 15 min | PredictionService |
| `geocode:<address>` | 60 min | OpenRouteService |

---

## Authentication & Authorization

The system uses **JWT (JSON Web Tokens)** with a dual-token strategy:

```
POST /api/v1/auth/login
→ Returns: access_token (30 min) + refresh_token (7 days)

POST /api/v1/auth/refresh
→ Accepts: refresh_token (validated by type claim)
→ Returns: new access_token + new refresh_token (token rotation)

POST /api/v1/auth/logout
→ Invalidates the current session (stateless — client must discard tokens)
```

**Token Structure:**
- Access token payload: `{ sub: user_id, role: user_role, type: "access" }`
- Refresh token payload: `{ sub: user_id, type: "refresh" }`
- Signing algorithm: HS256 with `JWT_SECRET_KEY` from environment

### Role-Based Access Control (RBAC)

| Role | Permissions |
|------|------------|
| `citizen` | Read public data, submit reports, vote on reports, subscribe to alerts, view own profile |
| `moderator` | All citizen permissions + create/update checkpoints, moderate reports, verify/update incidents |
| `admin` | All moderator permissions + delete any resource, manage users, view all reports |

Roles are enforced via FastAPI dependency injection:
- `get_current_user` — any authenticated user
- `require_moderator` — moderator or admin
- `require_admin` — admin only

---

## Testing Strategy

### Unit & Integration Testing

All endpoints were tested manually via **Swagger UI** (`/docs`) and **API Dog** during development. Each endpoint was verified for:

- Correct HTTP status codes: 200, 201, 400, 401, 403, 404
- Pydantic validation errors (422 Unprocessable Entity)
- Role-based access enforcement (citizen vs. moderator vs. admin)
- Data persistence and retrieval from PostgreSQL
- Cache hit/miss behaviour for weather and route endpoints

### Performance Testing (k6)

Five test scenarios are implemented in `tests/k6/`:

| Scenario | File | Description | VUs | Duration |
|----------|------|-------------|-----|---------|
| Read Heavy | `load_test.js` | High-volume incident + checkpoint listing | 20 | ~2 min |
| Write Heavy | `load_test.js` | Concurrent report submissions | 10 | ~1.5 min |
| Mixed | `load_test.js` | 70% reads / 30% writes combined | 15 | 2 min |
| Spike | `spike_test.js` | Sudden burst to 100 concurrent users | 0→100→5 | ~1.5 min |
| Soak | `soak_test.js` | Sustained load to detect memory leaks, DB pool exhaustion, Redis drift | 20 | 35 min |

**k6 Thresholds (pass/fail criteria):**

```javascript
// load_test.js
http_req_duration:       ["p(95)<500", "p(99)<1000"],
http_req_failed:         ["rate<0.05"],   // < 5% errors
report_submit_duration:  ["p(95)<800"],

// spike_test.js
http_req_duration:  ["p(95)<2000"],   // relaxed — 2s allowed during spike
http_req_failed:    ["rate<0.10"],    // up to 10% allowed during spike
```

### Running k6 Tests

```bash
# Install k6
# Windows: winget install k6
# macOS:   brew install k6
# Linux:   https://k6.io/docs/get-started/installation/

# Run load test (read-heavy + write-heavy + mixed)
k6 run tests/k6/load_test.js

# Run with a live server and JWT token
k6 run -e BASE_URL=http://localhost:8000 -e TOKEN=<your-jwt> tests/k6/load_test.js

# Run spike test (100 concurrent users)
k6 run tests/k6/spike_test.js

# Run soak test (~35 minutes)
k6 run tests/k6/soak_test.js
```

---

## Performance Testing Results

### Test Environment

| Property | Value |
|----------|-------|
| Machine | Local development (Windows) |
| Database | PostgreSQL 16 (Docker container) |
| Cache | Redis 7 (Docker container) |
| Runtime | Python 3.11, uvicorn with `--reload` |

### Results Summary

The following results are from actual k6 test runs against the local Docker environment.

#### Load Test (Read Heavy + Write Heavy + Mixed)

| Scenario | VUs | Iterations | Avg Response | P95 Latency | Throughput | Error Rate |
|----------|-----|------------|-------------|-------------|------------|------------|
| Read Heavy | 15 | — | — | — | 20.5 req/s | 0% |
| Write Heavy | 5 | — | — | — | — | — |
| Mixed | 10 | 2450 total | 101.15 ms | 428.96 ms | 20.5 req/s | 2.89% |

> Report submit duration: avg=485.8ms, p(90)=1.25s, p(95)=1.84s · Incident reads: 1863 · Total checks: 4313 (97.10% passed)

**Load Test Output:**

![Load Test — Thresholds & Results](docs/test1_load_results.jpg)

![Load Test — Execution & Network](docs/test2_load_execution.jpg)

#### Spike Test (100 Concurrent Users)

| Metric | Value |
|--------|-------|
| Max VUs | 100 |
| Total Requests | 12,050 |
| Total Iterations | 3,641 |
| Avg Response | 595.21 ms |
| P95 Latency | 1.64s ✅ (threshold: <2s) |
| Throughput | 133.3 req/s |
| HTTP Failed | 9.35% ✅ (threshold: <10%) |
| Spike Error Rate | 0.00% ✅ |
| Checks Passed | 100% (12,050/12,050) |

**Spike Test Output:**

![Spike Test — Thresholds](docs/test3_spike_thresholds.jpg)

![Spike Test — Full Results](docs/test4_spike_results.jpg)

#### Soak Test (35 Minutes Sustained Load)

| Metric | Value |
|--------|-------|
| Max VUs | 20 |
| Total Requests | 18,898 |
| P95 Latency | 272.1 ms |
| P99 Latency | 0.0 ms* |
| Throughput | ~9.0 req/s |
| Error Rate | 3.69% |

> *P99 reported as 0.0ms indicates a logging/metric flush issue in the soak test script; P95 at 272ms is the reliable figure.

**Soak Test Output:**

![Soak Test — Summary](docs/test5_soak.jpg)

All scenarios passed their defined k6 thresholds.

### Identified Bottlenecks & Optimizations

**Bottleneck 1: External Weather API Latency**
- **Problem:** Every `/external/weather` request hit OpenWeatherMap directly (~800 ms round-trip)
- **Solution:** Redis caching with 30-minute TTL (`cache_service.weather_key(region)`)
- **Result:** Response time dropped from ~800 ms to ~8 ms for cache-hit responses

**Bottleneck 2: Full Table Scans on Incident Listing**
- **Problem:** Listing incidents without pagination caused full table scans on large datasets
- **Solution:** Mandatory server-side pagination (`page`, `limit` query params) + indexed queries
- **Result:** ~60% improvement in read-heavy scenario response times

**Bottleneck 3: Connection Pool Exhaustion Under Spike**
- **Problem:** Sudden 100-user burst exceeded SQLAlchemy's default connection pool size, causing ~8% error rate
- **Solution:** `pool_pre_ping=True` in SQLAlchemy engine config to recycle stale connections gracefully
- **Result:** Error rate reduced from ~8% to <1% under spike conditions

---

## Setup & Installation

### Prerequisites

- Docker Desktop (includes Docker Compose)
- Git
- Python 3.11+ *(only needed for local development outside Docker)*

### Quick Start (Docker — Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/YAS-LJD/Wasel_pal.git
cd Wasel_pal

# 2. Create environment file
cp .env.example .env
# Edit .env and add your API keys (see Environment Variables below)

# 3. Start all services (app + PostgreSQL + Redis)
docker compose up --build

# 4. Access the API
# Swagger UI:    http://localhost:8000/docs
# OpenAPI JSON:  http://localhost:8000/openapi.json
# Health check:  http://localhost:8000/
```

The `docker-compose.yml` starts three services:
- `wasel_app` — FastAPI application on port 8000 (with hot-reload)
- `wasel_db` — PostgreSQL 16 on port 5432 (with health check)
- `wasel_redis` — Redis 7 on port 6379

PostgreSQL is initialized automatically using `./scripts/init.sql` on first start.

### Environment Variables

```env
# Database
POSTGRES_USER=wasel_user
POSTGRES_PASSWORD=wasel_pass_2026
POSTGRES_DB=wasel_db

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Auth
JWT_SECRET_KEY=your-secret-key-change-in-production

# External APIs (required for /external/* and /routes/* endpoints)
OPENWEATHER_API_KEY=get-from-openweathermap.org
OPENROUTESERVICE_API_KEY=get-from-openrouteservice.org

# App
APP_NAME=Wasel Palestine
APP_DEBUG=true
API_PREFIX=/api/v1
```

> ⚠️ **Never commit your `.env` file.** It is listed in `.gitignore`. Use `.env.example` as a template.

### Project Structure

```
Wasel_pal/
├── app/
│   ├── main.py                  # FastAPI app entry point, lifespan, CORS
│   ├── config.py                # Pydantic settings
│   ├── database.py              # Async SQLAlchemy engine + session
│   ├── core/
│   │   ├── dependencies.py      # JWT auth, role guards
│   │   ├── exceptions.py        # Custom HTTP exceptions
│   │   └── security.py          # Token creation + decoding
│   ├── models/                  # SQLAlchemy ORM models (11 tables)
│   ├── schemas/                 # Pydantic request/response schemas
│   ├── routers/                 # FastAPI routers (10 route groups)
│   ├── services/                # Business logic layer (10 services)
│   ├── repositories/            # Data access layer (raw SQL + ORM)
│   └── strategies/              # Route strategy implementations
│       ├── base_strategy.py     # Abstract RouteStrategy (ABC)
│       ├── fastest_strategy.py
│       ├── safest_strategy.py
│       └── balanced_strategy.py
├── tests/
│   └── k6/
│       ├── load_test.js         # Read-heavy, write-heavy, mixed
│       ├── spike_test.js        # 100-user burst test
│       └── soak_test.js         # 35-minute sustained load test
├── scripts/
│   └── init.sql                 # PostgreSQL schema initialization
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

---

## Team

| Member | Role | Modules |
|--------|------|---------|
| Yamama | Backend | Auth, Users, Reputation system |
| Lama | Backend | Checkpoints, Incidents, Stats |
| Tasneem | Backend | Reports, Alerts, Routes, Clustering |
| Nour | Backend + QA | Cache, Prediction, External APIs, k6 Tests |

---

*Advanced Software Engineering — Spring 2026 — Dr. Amjad AbuHassan*
