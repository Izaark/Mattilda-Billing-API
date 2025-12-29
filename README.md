# Mattilda Billing API

A RESTful API for managing schools, students, invoices, and payments with real-time account statement generation. Built with Clean Architecture principles and SOLID design patterns.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-316192.svg)](https://www.postgresql.org/)
[![Tests](https://img.shields.io/badge/Tests-115%20passed-success.svg)](./tests)
[![Coverage](https://img.shields.io/badge/Coverage-97%25-brightgreen.svg)](./.coveragerc)

---

## Tech Stack

- **Framework**: FastAPI 0.115
- **Database**: PostgreSQL 16
- **ORM**: SQLAlchemy 2.0 (async-ready)
- **Migrations**: Alembic 1.14
- **Testing**: pytest + Factory Boy + Faker
- **Logging**: structlog (JSON structured logs)
- **Validation**: Pydantic 2.10
- **Containerization**: Docker + Docker Compose

---

## Prerequisites

- Docker >= 20.10
- Docker Compose >= 2.0
- Git

---

## Quick Start

### 1. Clone and Setup

```bash
# Clone repository
git clone https://github.com/Izaark/Mattilda-Billing-API
cd Mattilda-Billing-API
# Create environment file
cp .env.example .env
# ⚠️ IMPORTANT: Edit .env and set your API_KEY
```

### 2. Start Services

```bash
# Start all services (DB + Backend)
docker-compose up -d

# Check services are healthy
docker-compose ps
```

### 3. Run Migrations

```bash
# Apply database migrations
docker-compose exec backend alembic upgrade head
```

### 4. Verify Installation

```bash
# Run tests
docker-compose exec backend pytest

# Check API is running
curl http://localhost:8000/health
# Expected: {"status": "healthy"}

# Access interactive docs
open http://localhost:8000/docs
```

### 5. (Optional) Load Sample Data

```bash
# Create realistic sample data (schools, students, invoices, payments)
docker-compose exec backend python scripts/seed.py

# Verify data was created
curl http://localhost:8000/api/v1/schools
curl http://localhost:8000/api/v1/students
curl http://localhost:8000/api/v1/invoices
curl http://localhost:8000/api/v1/students/1/statement
curl http://localhost:8000/api/v1/schools/1/statement
```

**Sample data includes**:
- 3 schools: México (MXN), Colombia (COP), Ecuador (USD)
- 8 students across different schools
- 16 invoices with varied statuses (PAID, PARTIAL, ISSUED, VOID)
- 12 payments with different methods

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | `postgresql://mattilda:secret@localhost:5432/mattilda_billing`  | PostgreSQL connection string (format: `postgresql://user:pass@host:port/db`) |
| `API_KEY` | Yes | `dev-secret-key` | Auth key for write endpoints (use same in Swagger/cURL) |
| `API_V1_PREFIX` | No | `/api/v1` | API route prefix |
| `ENVIRONMENT` | No | `development` | Environment name |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity |


---

## Architecture

This project follows **Clean Architecture** principles with a layered structure:

```
┌─────────────────────────────────────────────┐
│          API Layer (FastAPI)                │  ← HTTP Endpoints
├─────────────────────────────────────────────┤
│       Services (Business Logic)             │  ← Core business rules
├─────────────────────────────────────────────┤
│     Repositories (Data Access)              │  ← Database operations
├─────────────────────────────────────────────┤
│      Domain Models (ORM + Enums)            │  ← Data structures
└─────────────────────────────────────────────┘
```

### Key Design Patterns

- **Repository Pattern**: Abstracts data access logic
- **Dependency Injection**: Services receive dependencies via constructor
- **Soft Deletes**: Schools use `is_active`, Invoices use `VOID` status
- **Domain-Driven Design**: Business rules in `domain/business_rules.py`


### Entity Relationship Diagram

```mermaid
erDiagram
    SCHOOL ||--o{ STUDENT : "has many"
    STUDENT ||--o{ INVOICE : "has many"
    INVOICE ||--o{ PAYMENT : "has many"

    SCHOOL {
        bigint id PK
        string name "unique(name,country)"
        string country "2 chars"
        string currency "3 chars"
        boolean is_active "soft delete"
        datetime created_at
        datetime updated_at
    }

    STUDENT {
        bigint id PK
        bigint school_id FK "RESTRICT"
        string first_name
        string last_name
        string email "unique"
        datetime created_at
        datetime updated_at
    }

    INVOICE {
        bigint id PK
        bigint student_id FK "RESTRICT"
        decimal amount_total "CHECK > 0"
        string currency "3 chars"
        string status "ISSUED|PARTIAL|PAID|VOID"
        datetime issued_at
        date due_date
        string description "nullable"
        datetime created_at
        datetime updated_at
    }

    PAYMENT {
        bigint id PK
        bigint invoice_id FK "RESTRICT"
        decimal amount "CHECK > 0"
        datetime paid_at
        string method "nullable"
        string reference "nullable"
        datetime created_at
    }
```

**Key Constraints**:
- School: Unique(name, country) - prevents duplicate schools per country
- Student: Unique(email) - one email per student globally
- Invoice/Payment: CHECK amount > 0 - business rule enforcement
- All FKs: ON DELETE RESTRICT - data integrity (no orphans)

---

## Project Structure

```
app/
├── api/v1/              # API endpoints (routers)
├── services/            # Business logic layer
├── repositories/        # Data access layer
├── domain/
│   ├── models/          # SQLAlchemy ORM models
│   ├── business_rules.py # Pure business logic
│   └── enums.py         # Status enums
├── schemas/             # Pydantic models (request/response)
├── infrastructure/      # External concerns (DB, logging, auth)
└── exceptions/          # Custom exception classes

tests/
├── unit/                # Unit tests (services, repos, domain)
└── integration/         # Integration tests (full flow)
```

---

## API Endpoints

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs

### Authentication

Protected endpoints (POST, PUT, DELETE, PATCH) require API Key authentication.

**In Swagger UI:**
1. Click the "Authorize" 🔒 button at the top right
2. Enter your API_KEY from `.env`
3. Click "Authorize"

**With cURL:**
```bash
curl -H "X-API-Key: your-secret-key-here" \
  -X POST http://localhost:8000/api/v1/schools \
  -H "Content-Type: application/json" \
  -d '{"name": "Test School", "country": "MX", "currency": "MXN"}'
```

### Available Endpoints

| Resource | Endpoints | Auth Required |
|----------|-----------|---------------|
| **Schools** | `GET /api/v1/schools` | No |
| | `POST /api/v1/schools` | Yes |
| | `GET /api/v1/schools/{id}` | No |
| | `PATCH /api/v1/schools/{id}` | Yes |
| | `DELETE /api/v1/schools/{id}` | Yes |
| | `PATCH /api/v1/schools/{id}/activate` | Yes |
| **Students** | `GET /api/v1/students` | No |
| | `POST /api/v1/students` | Yes |
| | `GET /api/v1/students/{id}` | No |
| | `PATCH /api/v1/students/{id}` | Yes |
| | `DELETE /api/v1/students/{id}` | Yes |
| **Invoices** | `GET /api/v1/invoices` | No |
| | `POST /api/v1/invoices` | Yes |
| | `GET /api/v1/invoices/{id}` | No |
| | `PATCH /api/v1/invoices/{id}` | Yes |
| | `DELETE /api/v1/invoices/{id}` | Yes |
| **Payments** | `GET /api/v1/payments` | No |
| | `POST /api/v1/payments` | Yes |
| **Statements** | `GET /api/v1/students/{id}/statement` | No |
| | `GET /api/v1/schools/{id}/statement` | No |

### Usage Examples

**Get Student Statement:**
```bash
curl http://localhost:8000/api/v1/students/1/statement
```

**Response:**
```json
{
  "student": {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com"
  },
  "currency": "MXN",
  "totals": {
    "invoiced": "15000.00",
    "paid": "8000.00",
    "pending": "7000.00"
  },
  "invoices": [
    {
      "id": 1,
      "amount_total": "10000.00",
      "paid": "5000.00",
      "pending": "5000.00",
      "status": "PARTIAL"
    }
  ]
}
```

---

## Testing

### Run Tests

```bash
# All tests (115 tests, ~5 seconds)
docker-compose exec backend pytest

# With detailed output
docker-compose exec backend pytest -v

# Only unit tests (fast)
docker-compose exec backend pytest tests/unit

# Only integration tests
docker-compose exec backend pytest tests/integration

# Run specific test file
docker-compose exec backend pytest tests/unit/services/test_payment_service.py

# Run specific test function
docker-compose exec backend pytest tests/unit/services/test_payment_service.py::TestPaymentService::test_create_payment_successfully -v

# Generate HTML coverage report
docker-compose exec backend pytest --cov=app --cov-report=html
open htmlcov/index.html
```

### Test Stack

- **Framework**: pytest 7.4
- **Data Factories**: Factory Boy + Faker
- **Database**: PostgreSQL (auto-created `mattilda_billing_test`)
- **Coverage**: 97% (115 tests passing)
- **Types**: Unit tests (services, repos, domain) + Integration tests (statements)

---

## Technical Decisions

### Clean Architecture

**Why**: Clear separation (API → Services → Repositories → Domain) improves testability and maintainability. Worth the extra folders for a system with complex aggregations (statements).

---

### Pydantic over Marshmallow

**Why**: Native FastAPI integration, better type hints, faster.

---

### API Key Authentication

**Why**: Proportional to challenge scope. Simple, testable.

---

### Pagination: Limit + Offset

**Why**: Standard, simple, performant enough for typical school/student counts.

**Not**: Cursor-based pagination unnecessary without high-scale requirements.

---

### Structured Logging (JSON)

**Why**: Captures business events (payments, errors), production-ready (ELK/Datadog compatible).

**Not**: Metrics system (Prometheus) would be over-engineering without load testing data.

---

### No Redis Cache

**Why**: 
- No measured performance bottleneck
- Statements are optimized queries with eager loading
- Would add complexity (invalidation, stale data) without proven need

**When to add**: After load testing shows latency > 500ms and cache hit rate > 80%.
---

### Soft Deletes (Strategic)

**Why applied selectively**:
- Schools: `is_active` (reactivation possible)
- Invoices: `VOID` status (audit trail, immutable)
- Students: Hard delete (GDPR compliance ready)

---

### Testing: 97% Coverage

**Strategy**:
- Unit tests for services, repos, domain logic (fast)
- Integration tests for statements (core business value)
- Factory Boy for realistic data
- PostgreSQL for tests (same as prod, avoids SQLite gotchas)

**Not chasing 100%**: Config and routers excluded (tested in real usage).

---

## Development

### Add Migration

```bash
# Generate from model changes
docker-compose exec backend alembic revision --autogenerate -m "description"

# Apply
docker-compose exec backend alembic upgrade head

# Rollback
docker-compose exec backend alembic downgrade -1
```

### Add New Endpoint

1. **Domain Model** (if new entity): `app/domain/models/`
2. **Repository** (data access): `app/repositories/`
3. **Schema** (request/response): `app/schemas/`
4. **Service** (business logic): `app/services/`
5. **Router** (HTTP endpoint): `app/api/v1/`
6. **Tests**: `tests/unit/` and `tests/integration/`
7. Test in Swagger: http://localhost:8000/docs

---

## Troubleshooting

**403 on POST endpoints**
- Check API_KEY in `.env` matches header
- In Swagger: Click "Authorize", paste key

**Migrations not applying**
```bash
docker-compose down
docker-compose up -d --build
docker-compose exec backend alembic upgrade head
```

**Tests fail: Database not found**
- Should auto-create via init script
- Manual fix: `docker-compose exec db psql -U mattilda -c "CREATE DATABASE mattilda_billing_test;"`

---

## Future Enhancements

**Not implemented (intentionally scoped out)**:

- **Redis Cache**: Add after load testing proves need (latency > 500ms)
- **Metrics**: Prometheus/Grafana once SLOs defined
- **Rate Limiting**: When API becomes public-facing
- **OAuth2**: If user management is added to domain
- **CI/CD**: GitHub Actions for production deployment
- **Pre-commit Hooks**: black, ruff, mypy for code quality enforcement
- **Makefile**: Common commands (test, lint, format, migrate) for developer productivity

---
