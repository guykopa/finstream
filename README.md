# finstream

**Industrial ETL pipeline for financial data processing** — built in Python with TDD, SOLID principles, and hexagonal architecture.

**[Live project page →](https://guykopa.github.io/finstream/)**

---

## What it does

finstream covers the full lifecycle of a Finance Information System:

| Step | What | How |
|------|------|-----|
| Extract | Read transactions | CSV files, Yahoo Finance REST API (live), PostgreSQL |
| Clean | Remove invalid data | DataCleaner — bad amounts, unknown currencies |
| Transform | Normalize currencies, deduplicate, standardize dates | pandas, chunked |
| Validate | 5-rule quality engine with configurable gate | score ≥ 80% to proceed |
| Load | Write clean data | PostgreSQL, bulk insert via psycopg2 |
| Expose | REST API + BI dashboard | FastAPI + JWT |
| Monitor | Metrics + structured logs + alerts | Prometheus + Grafana |

## Architecture

Pipeline Pattern (ETL core) + Hexagonal Architecture (application layer).

```
FastAPI / CLI
    ↓
ETLPipeline
  IDataSource → DataCleaner → CurrencyNormalizer → Deduplicator → DateStandardizer
              → QualityEngine (5 rules) → PostgreSQLStorage
    ↓
Prometheus → Grafana
```

See [ARCHITECTURE.md](Architecture.md) for the full architecture diagram.

## Quick start

```bash
# 1. Clone the repository
git clone https://github.com/guykopa/finstream.git && cd finstream

# 2. Create virtual environment
python -m venv .venv && source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment variables
cp .env.example .env   # then edit JWT_SECRET

# 5. Start with Docker (recommended)
cd docker && docker compose up
```

Services:
- API + Swagger UI: http://localhost:8000/docs
- BI Dashboard: http://localhost:8000/dashboard
- Grafana: http://localhost:3000 (admin / admin)
- pgAdmin: http://localhost:5050
- Prometheus: http://localhost:9090

Default API credentials: `admin@finstream.io` / `changeme`

## Data sources

### CSV files
```bash
POST /pipeline/run
{
  "business_date": "2024-01-15",
  "source": "csv",
  "file_path": "/app/data/transactions_2024_01_15.csv"
}
```

### Live market data (Yahoo Finance REST API)
```bash
POST /pipeline/run
{
  "business_date": "2024-01-15",
  "source": "live"
}
```
Fetches real-time OHLCV data for 12 tickers (Apple, LVMH, Airbus, NVDA...).

### Fake data (development)
```bash
POST /pipeline/run
{
  "business_date": "2024-01-15",
  "source": "fake"
}
```

## API endpoints

```
POST /auth/token              → get JWT token
POST /pipeline/run            → trigger ETL pipeline      [JWT]
GET  /pipeline/status/{id}    → run status                [JWT]
GET  /quality/reports         → list quality reports      [JWT]
GET  /quality/reports/{id}    → one quality report        [JWT]
GET  /dashboard               → interactive BI dashboard
GET  /health                  → health check
GET  /metrics                 → Prometheus metrics
```

## Tests

```bash
export JWT_SECRET="test-secret-minimum-32-chars"

pytest tests/unit/                     # unit tests (no infrastructure)
pytest tests/integration/              # integration tests (requires PostgreSQL)
pytest tests/non_regression/           # stability tests
pytest --cov=finstream --cov-report=html   # with coverage report
```

Coverage target: **≥ 90%**.

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `JWT_SECRET` | Yes | HMAC secret for JWT signing (min 32 chars) |
| `DATABASE_URL` | Yes (production) | PostgreSQL connection string |
| `DEMO_EMAIL` | No | Login email (default: `admin@finstream.io`) |
| `DEMO_PASSWORD` | No | Login password (default: `changeme`) |

## Project structure

```
finstream/
├── finstream/
│   ├── interfaces/      ← abstract contracts (IDataSource, IDataStorage...)
│   ├── domain/          ← models, services, exceptions (no pandas)
│   ├── extract/         ← CSVSource, PostgreSQLSource, YahooFinanceAPISource
│   ├── transform/       ← DataCleaner, CurrencyNormalizer, Deduplicator, DateStandardizer
│   ├── quality/         ← 5 rules + QualityEngine
│   ├── load/            ← PostgreSQLStorage (psycopg2 bulk insert)
│   ├── bigdata/         ← ChunkProcessor, MemoryOptimizer
│   ├── report/          ← DashboardRenderer (Chart.js HTML)
│   ├── pipeline/        ← ETLPipeline orchestrator
│   ├── api/             ← FastAPI + JWT + routes + schemas
│   ├── monitoring/      ← Prometheus metrics, structured logger, alerting
│   └── cli/             ← argparse CLI
├── tests/
│   ├── unit/            ← mocked, no infrastructure
│   ├── integration/     ← real PostgreSQL
│   └── non_regression/  ← stability
├── data/                ← CSV financial data (Yahoo Finance, Bloomberg...)
├── scripts/             ← 6 Bash admin scripts
├── migrations/          ← Alembic (3 versions)
├── docker/              ← Dockerfile + docker-compose
├── monitoring/          ← Prometheus config + Grafana dashboards
└── docs/                ← GitHub Pages
```

## Stack

Python 3.11 · FastAPI · SQLAlchemy · Alembic · pandas · psycopg2 · pydantic · PyJWT · httpx · Prometheus · Grafana · Chart.js · pytest · Docker
