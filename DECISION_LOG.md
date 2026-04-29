# Decision Log

Technical decisions made during the design and implementation of this project.

---

## 1. Architecture: Clean Architecture over MVC

**Decision:** Three-layer Clean Architecture (Domain → Application → Infrastructure).

**Rationale:**
- The domain layer has **zero framework dependencies** — entities and repository interfaces are plain Python dataclasses and ABCs. This makes them trivially testable without spinning up any I/O.
- Use cases encode business rules once, independently of delivery mechanism (REST today, gRPC or CLI tomorrow).
- Swapping PostgreSQL for a different database, or FastAPI for another framework, requires changes only in the Infrastructure layer.

**Trade-off:** More files and more indirection than a flat MVC structure. Worth it at any scale where the domain is non-trivial and testability matters.

---

## 2. Database: PostgreSQL over SQLite / MongoDB

**Decision:** PostgreSQL 16 with SQLAlchemy 2.x (async) + Alembic migrations.

**Rationale:**
- ACID compliance, strong typing, referential integrity (foreign keys with `ON DELETE CASCADE/SET NULL`) are a natural fit for relational task/user data.
- SQLAlchemy 2.x with `asyncpg` gives true async I/O without the quirks of sync drivers wrapped in thread pools.
- Alembic provides reproducible, reviewable migrations — critical in CI/CD pipelines.

**Trade-off:** Heavier to spin up locally than SQLite. Mitigated by the provided `docker-compose.yml`.

---

## 3. Authentication: JWT (stateless) over sessions

**Decision:** HS256 JWT via `python-jose`, password hashing with `passlib[bcrypt]`.

**Rationale:**
- Stateless tokens work without a shared session store — ideal for horizontal scaling (multiple `app` replicas in `docker-compose.prod.yml`).
- bcrypt is the industry standard for password hashing; its tunable cost factor allows adapting to hardware improvements.

**Trade-off:** Token revocation requires either short expiry + refresh tokens, or a denylist (e.g., Redis). This implementation uses short-lived tokens; refresh tokens are a natural next step.

---

## 4. Completion percentage: calculated at query time, not stored

**Decision:** `completion_percentage` is computed on each `GET /tasks` call via two `COUNT` queries.

**Rationale:**
- Storing a cached percentage requires maintaining it on every task status change — a synchronisation burden that adds complexity without measurable benefit at typical task-list sizes.
- Two indexed `COUNT` queries on a task list are sub-millisecond. Premature optimisation (materialised views, triggers) would add complexity with no observable benefit.

**Trade-off:** For lists with millions of tasks, pre-aggregation would be preferable. A future migration could add a background job or a DB trigger if needed.

---

## 5. Docker: multistage build with a non-root runtime image

**Decision:** Three stages — `builder`, `development`, `runtime`.

**Rationale:**
- `builder`: installs `build-essential` and all Python wheels into an isolated venv.
- `development`: extends builder, installs dev deps, mounts source via volume — enables hot-reload.
- `runtime`: starts from a fresh `python:3.12-slim`, copies only the venv and source. No build tools, no dev deps, no root user. Final image is ~200 MB smaller than a naïve single-stage build.
- A dedicated `HEALTHCHECK` instruction lets Docker and orchestrators (ECS, Kubernetes) detect unhealthy containers automatically.

---

## 6. Two Compose files: dev vs. prod

**Decision:** `docker-compose.yml` (development) + `docker-compose.prod.yml` (production).

**Rationale:**
- Development needs hot-reload, Adminer (DB GUI), exposed PostgreSQL port, and hardcoded dev credentials — none of which belong in production.
- Production needs resource limits, replica count, Nginx as a reverse proxy/TLS terminator, structured logging, and secrets injected via environment variables (never committed).
- Separating them avoids feature-flag proliferation inside a single file and makes it clear which settings are environment-specific.

---

## 7. Simulated notifications (no real email)

**Decision:** `NotificationService` logs a structured event instead of calling an SMTP/SES endpoint.

**Rationale:**
- A real email integration (SES, SendGrid) requires external credentials and network access, turning a unit/integration test into an end-to-end test with external side effects.
- The structured log (`structlog`) is observable in tests and staging. In production, replacing `logger.info(...)` with an async HTTP call to the email provider is a localised, one-file change.

---

## 8. Testing strategy: unit + integration, real DB for integration tests

**Decision:** Unit tests mock repositories; integration tests run against a real PostgreSQL test database with per-test transaction rollback.

**Rationale:**
- Mocking in unit tests isolates business logic from I/O, making them fast and deterministic.
- Integration tests that talk to a real database catch issues that mocks hide (enum mapping, constraint violations, query correctness).
- Per-test `SAVEPOINT` rollback keeps tests independent and fast without truncating tables between runs.

**Trade-off:** Integration tests require a running PostgreSQL instance. The provided `docker-compose.yml` and GitHub Actions service container remove this friction in practice.

---

## 9. Pydantic v2 for API schemas, dataclasses for domain entities

**Decision:** Pydantic `BaseModel` is used only in the Infrastructure (API) layer; domain entities are plain `@dataclass`.

**Rationale:**
- Domain entities must not depend on Pydantic (or any framework). Using dataclasses keeps the domain portable.
- Pydantic v2 is the right tool at the API boundary: automatic JSON coercion, OpenAPI schema generation, and validation error messages out of the box.

---

## 10. CI/CD: GitHub Actions with matrix strategy

**Decision:** Three jobs — `lint`, `test` (with postgres service), `docker build`.

**Rationale:**
- Lint failures are cheap to catch and should not block PRs silently.
- Running tests against a real PostgreSQL service container (not mocked) mirrors production behaviour.
- Building the Docker image in CI proves the Dockerfile is always in a buildable state, not just "works on my machine".
- `docker/build-push-action` with GHA cache (`cache-from/to: type=gha`) makes repeated builds fast.

---

## 11. Documentation protected with HTTP Basic Auth

**Decision:** `/docs`, `/redoc` and `/openapi.json` are served manually with an `HTTPBasic` dependency. FastAPI's default automatic exposure of these routes is disabled (`docs_url=None`, `redoc_url=None`, `openapi_url=None`).

**Rationale:**
- The OpenAPI schema exposes the full surface of the API — every endpoint, every request/response shape, every error code. Leaving it public is equivalent to handing an attacker a detailed map of the service.
- HTTP Basic Auth adds a lightweight but effective gate: browsers prompt for credentials automatically, and the protected routes return `401 + WWW-Authenticate: Basic` on failure.
- `secrets.compare_digest` is used instead of a plain `==` comparison to prevent timing-based credential enumeration attacks.
- Credentials are configured via `DOCS_USERNAME` / `DOCS_PASSWORD` in the environment file, so they can be rotated without a code change.

**Default values:** `admin` / `admin` for development. These **must** be changed before any deployment. The `.env.prod.example` marks them as `CHANGE_ME`.

**Trade-off:** HTTP Basic Auth transmits credentials on every request (Base64-encoded, not encrypted). This is acceptable when the service is behind TLS (Nginx in the production compose handles termination). For a zero-trust environment, blocking `/docs` and `/redoc` at the Nginx level is an even stronger option.
