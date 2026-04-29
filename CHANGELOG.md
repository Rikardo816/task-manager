# Changelog

All notable changes to this project are documented in this file.

---

## [v0.1.0] — 2026-04-29

### Added
- Full CRUD for task lists and tasks with Clean Architecture (Domain → Application → Infrastructure)
- JWT authentication: `POST /auth/register`, `POST /auth/login`
- Task status change: `PATCH /task-lists/{id}/tasks/{task_id}/status`
- Task assignment with simulated email notification: `PATCH /task-lists/{id}/tasks/{task_id}/assignee`
- Task list endpoint with filters (`?status=`, `?priority=`) and `completion_percentage` field
- `GET /users/me`, `GET /users` — authenticated user endpoints
- `GET /system/enums` — available task statuses and priorities
- `GET /health` (liveness) and `GET /status` (readiness — checks DB connectivity)
- Structured logging with `structlog` and per-request correlation ID middleware
- `NotificationPort` abstract interface for email notifications (DIP)
- Application mappers (`task_mapper`, `task_list_mapper`) replacing private `_to_output` helpers
- `update()` method on `Task` and `TaskList` domain entities (timestamp managed by the entity)
- `GetUserUseCase` and `ListUsersUseCase` — users router goes through the application layer
- `CurrentUser` dataclass in `dependencies.py`; `username` included in JWT payload
- `ALLOWED_ORIGINS` setting for CORS (replaces invalid `allow_origins=["*"]` + credentials combo)
- `.dockerignore` to exclude dev artefacts, secrets and IDE files from the image
- Multistage `Dockerfile` (builder → development → runtime) with venv at `/venv`
- `docker-compose.yml` (dev with hot-reload) and `docker-compose.prod.yml` (2 replicas + Nginx)
- `Makefile` with targets for install, run, test, lint, format, Docker, migrations
- `.pre-commit-config.yaml` with isort, black, ruff, flake8 and general file hygiene hooks
- GitHub Actions CI: lint → test (PostgreSQL service) → Docker build
- Alembic migration setup with `compare_type=True` and `compare_server_default=True`

### Changed
- Migrated package management from pip to **uv** with `uv.lock` for reproducible installs
- Replaced `passlib` with `bcrypt` directly (incompatible with bcrypt 4.x on Python 3.13)
- `POSTGRES_*` individual fields replace a single `DATABASE_URL` string in all `.env` files; URL built internally via `@computed_field`
- All `datetime.utcnow()` calls replaced with `datetime.now(UTC)` (deprecation fix)
- `DateTime` columns changed to `DateTime(timezone=True)` for timezone-aware storage
- `Mapped[str]` annotations for enum columns corrected to `Mapped[TaskStatus]` / `Mapped[Priority]` with `native_enum=False`
- `Mapped[list]` on `TaskListModel.tasks` corrected to `Mapped[list["TaskModel"]]`
- Repository `update()` methods rewritten with `sa_update()` — eliminates the redundant SELECT before every write
- `count_by_task_list` + `count_completed_by_task_list` merged into `count_tasks_summary()` returning `(total, completed)` in one query
- `AuthService` instantiated once at module level in `dependencies.py` (singleton)
- All routers receive repositories via `Depends(get_task_repo / get_task_list_repo / get_user_repo)` — no concrete SQLAlchemy classes leaked into the API layer
- `Base.metadata.create_all` gated to `ENVIRONMENT=development`; production must run `alembic upgrade head`
- `TaskStatus` and `Priority` migrated from `(str, Enum)` to `StrEnum` (Python 3.11+)
- Login use case checks `is_active` before bcrypt to prevent timing-based user enumeration
- `lifespan` function annotated with `AsyncGenerator[None, None]` return type
- `asyncio_default_fixture_loop_scope = function` added to `pytest.ini`
- Connection pool explicit settings: `pool_timeout=30`, `pool_recycle=1800`
- HTTP Basic Auth protection on `/docs`, `/redoc` and `/openapi.json`
