# Task Manager API

REST API for managing task lists and tasks — built with **FastAPI**, **PostgreSQL**, and **Clean Architecture**.

## Features

- **Full CRUD** for task lists and tasks
- **JWT authentication** (register / login)
- **Task assignment** with simulated email notification
- **Filters** by status and priority
- **Completion percentage** per task list
- **Async** end-to-end (SQLAlchemy 2.x + asyncpg)
- **75%+ test coverage** (unit + integration)

---

## Project structure

```
src/
├── domain/          # Entities, repository interfaces, value objects, exceptions
├── application/     # Use cases, services, DTOs  (zero framework imports)
└── infrastructure/  # SQLAlchemy models, repositories, FastAPI routers
tests/
├── unit/            # Domain entities + use cases (mock repos, no I/O)
└── integration/     # Full HTTP tests against a real PostgreSQL test DB
```

---

## Environment variables

All configuration is driven by environment files. Two templates are provided:

| File | Purpose | Committed? |
|------|---------|------------|
| `.env.example` | Development template | ✅ yes |
| `.env.prod.example` | Production template | ✅ yes |
| `.env` | Your local dev config (copied from `.env.example`) | ❌ no |
| `.env.prod` | Your production config (copied from `.env.prod.example`) | ❌ no |

### Key variables

The connection URL is built internally from the individual `POSTGRES_*` fields — you never write the full DSN by hand.

| Variable | Description | Default / Example |
|----------|-------------|-------------------|
| `POSTGRES_HOST` | DB hostname — use `db` inside Docker Compose, `localhost` otherwise | `db` |
| `POSTGRES_PORT` | PostgreSQL port | `5432` |
| `POSTGRES_USER` | PostgreSQL user | `postgres` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `postgres` |
| `POSTGRES_DB` | Application database name | `taskmanager` |
| `POSTGRES_TEST_DB` | Test database name (dev only) | `taskmanager_test` |
| `SECRET_KEY` | JWT signing key — **must be secret in prod** | `openssl rand -hex 32` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime in minutes | `30` |
| `ENVIRONMENT` | Runtime environment label | `development` / `production` |
| `DEBUG` | Enable SQLAlchemy query logging | `true` / `false` |
| `APP_PORT` | Port the server listens on | `8000` |
| `DOCS_USERNAME` | HTTP Basic Auth user for `/docs` and `/redoc` | `admin` |
| `DOCS_PASSWORD` | HTTP Basic Auth password for `/docs` and `/redoc` | `admin` |

> In production, never write secrets directly into `.env.prod`.
> Prefer injecting them at deploy time from AWS Secrets Manager, HashiCorp Vault,
> or your CI/CD secrets store, then writing the file programmatically.

---

## Local setup (without Docker)

**Requirements:** Python 3.12+, PostgreSQL 15+, [uv](https://docs.astral.sh/uv/getting-started/installation/)

```bash
# 1. Clone & enter the project
git clone <repo-url> && cd task-manager

# 2. Install all dependencies — uv creates .venv and installs everything in one step
uv sync --extra dev

# 3. Create your local env file
cp .env.example .env
# The only value you need to change for local dev (no Docker) is POSTGRES_HOST:
#   POSTGRES_HOST=localhost   ← change from "db" to "localhost"

# 4. Create the databases
psql -U postgres -c "CREATE DATABASE taskmanager;"
psql -U postgres -c "CREATE DATABASE taskmanager_test;"

# 5. Run the server
uv run uvicorn src.infrastructure.api.main:app --reload
# Alternatively, activate the venv first:
#   source .venv/bin/activate   # Windows: .venv\Scripts\activate
#   uvicorn src.infrastructure.api.main:app --reload
```

The API will be available at `http://localhost:8000`.
Interactive docs: `http://localhost:8000/docs` (login with `DOCS_USERNAME` / `DOCS_PASSWORD`)

---

## Running with Docker (development)

Hot-reload is enabled; your local source code is mounted inside the container.

```bash
# 1. Create your env file from the template (only needed once)
cp .env.example .env

# 2. Build and start all services  (app + postgres + adminer)
docker compose up --build
```

| Service | URL | Credentials |
|---------|-----|-------------|
| API docs | `http://localhost:8000/docs` | `DOCS_USERNAME` / `DOCS_PASSWORD` from `.env` |
| Adminer (DB GUI) | `http://localhost:8080` | use `POSTGRES_*` values from `.env` |

To run in the background:

```bash
docker compose up -d --build
docker compose logs -f app   # follow logs
```

---

## Running with Docker (production)

```bash
# 1. Create and fill in your production env file (never commit this file)
cp .env.prod.example .env.prod
# Edit .env.prod — replace every CHANGE_ME value, generate a real SECRET_KEY:
#   openssl rand -hex 32

# 2. Build and start
docker compose -f docker-compose.prod.yml up -d --build

# 3. Check logs
docker compose -f docker-compose.prod.yml logs -f app
```

The production setup includes:
- **Multistage Dockerfile** — `builder` stage compiles deps, `runtime` stage is lean and runs as a non-root user
- **2 app replicas** with CPU/memory limits
- **Nginx** as reverse proxy / TLS terminator
- **PostgreSQL port not exposed** — only reachable within the Docker network

---

## Running tests

```bash
# Unit tests only — no database required, no coverage threshold enforced
uv run pytest tests/unit/ --no-cov

# All tests — requires a running PostgreSQL with TEST_DATABASE_URL set in .env.
# Enforces 75% total coverage (unit + integration together reach that bar).
uv run pytest

# Open the HTML coverage report after a full run
open htmlcov/index.html   # macOS; use xdg-open on Linux
```

With Docker running:

```bash
docker compose exec app pytest
```

---

## Linting & formatting

```bash
uv run black src/ tests/          # auto-format
uv run isort src/ tests/          # sort imports
uv run flake8 src/ tests/         # lint
uv run ruff check src/ tests/     # fast lint (superset of flake8)
```

All checks run automatically on every push/PR via GitHub Actions (`.github/workflows/ci.yml`).

---

## API endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/register` | — | Create a new user |
| POST | `/auth/login` | — | Obtain JWT token |
| GET | `/users/me` | ✅ | Current authenticated user |
| GET | `/users` | ✅ | List all users |
| GET | `/system/enums` | — | Valid task statuses and priorities |
| GET | `/task-lists` | ✅ | List all task lists (owner) |
| POST | `/task-lists` | ✅ | Create a task list |
| GET | `/task-lists/{id}` | ✅ | Get a task list |
| PUT | `/task-lists/{id}` | ✅ | Update a task list |
| DELETE | `/task-lists/{id}` | ✅ | Delete a task list |
| GET | `/task-lists/{id}/tasks` | ✅ | List tasks + completion % (`?status=` / `?priority=`) |
| POST | `/task-lists/{id}/tasks` | ✅ | Create a task |
| GET | `/task-lists/{id}/tasks/{task_id}` | ✅ | Get a task |
| PUT | `/task-lists/{id}/tasks/{task_id}` | ✅ | Update a task |
| DELETE | `/task-lists/{id}/tasks/{task_id}` | ✅ | Delete a task |
| PATCH | `/task-lists/{id}/tasks/{task_id}/status` | ✅ | Change task status |
| PATCH | `/task-lists/{id}/tasks/{task_id}/assignee` | ✅ | Assign task to a user |
| GET | `/health` | — | Liveness — API process alive (used by load balancer) |
| GET | `/status` | — | Readiness — external services reachable (DB, etc.) |

---

## Migrations (Alembic)

```bash
# Generate a migration after changing a model
alembic revision --autogenerate -m "describe the change"

# Apply all pending migrations
alembic upgrade head

# Roll back one step
alembic downgrade -1
```
