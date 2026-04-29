# ══════════════════════════════════════════════════════════════════════════════
#  Task Manager API — Developer shortcuts
#  Usage: make <target>
#  Run 'make help' to see all available commands.
# ══════════════════════════════════════════════════════════════════════════════

.DEFAULT_GOAL := help
.PHONY: help install run \
        test test-unit test-integration test-cov \
        lint format format-check \
        pre-commit-install pre-commit-run \
        docker-up docker-down docker-fresh docker-logs docker-test \
        migrate migration migrate-down \
        clean

# ── Colours ───────────────────────────────────────────────────────────────────
CYAN  := \033[36m
RESET := \033[0m

# ── Help ──────────────────────────────────────────────────────────────────────

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CYAN)%-22s$(RESET) %s\n", $$1, $$2}'

# ── Setup ─────────────────────────────────────────────────────────────────────

install: ## Install all dependencies including dev extras (uv)
	uv sync --extra dev

# ── Local development ─────────────────────────────────────────────────────────

run: ## Start the API server with hot-reload (requires local PostgreSQL)
	uv run uvicorn src.infrastructure.api.main:app --reload --host 0.0.0.0 --port 8000

# ── Testing ───────────────────────────────────────────────────────────────────

test: ## Run the full test suite with coverage (requires PostgreSQL)
	uv run pytest

test-unit: ## Run unit tests only — no database required
	uv run pytest tests/unit/ --no-cov

test-integration: ## Run integration tests only (requires PostgreSQL)
	uv run pytest tests/integration/

test-cov: ## Run full suite and open the HTML coverage report
	uv run pytest
	@echo "Opening coverage report…"
	@xdg-open htmlcov/index.html 2>/dev/null || open htmlcov/index.html 2>/dev/null || \
		echo "Report generated at htmlcov/index.html"

# ── Code quality ──────────────────────────────────────────────────────────────

lint: ## Run flake8 and ruff
	uv run flake8 src/ tests/
	uv run ruff check src/ tests/

format: ## Auto-format code with black and sort imports with isort
	uv run black src/ tests/
	uv run isort src/ tests/

format-check: ## Check formatting without modifying files (useful in CI)
	uv run black --check src/ tests/
	uv run isort --check-only src/ tests/
	uv run ruff check src/ tests/

# ── Pre-commit ───────────────────────────────────────────────────────────────

pre-commit-install: ## Install pre-commit hooks into .git/hooks (run once after cloning)
	uv run pre-commit install

pre-commit-run: ## Run all pre-commit hooks against every file
	uv run pre-commit run --all-files

# ── Docker ────────────────────────────────────────────────────────────────────

docker-up: ## Build and start all services (app + db + adminer)
	docker compose up --build

docker-down: ## Stop and remove containers (volumes are preserved)
	docker compose down

docker-fresh: ## Stop, remove containers AND volumes, then rebuild from scratch
	docker compose down -v
	docker compose up --build

docker-logs: ## Follow app container logs
	docker compose logs -f app

docker-test: ## Run the full test suite inside the running app container
	docker compose exec app pytest

# ── Database migrations ───────────────────────────────────────────────────────

migrate: ## Apply all pending Alembic migrations
	uv run alembic upgrade head

migration: ## Generate a new Alembic migration (usage: make migration msg="describe change")
	uv run alembic revision --autogenerate -m "$(msg)"

migrate-down: ## Roll back the last Alembic migration
	uv run alembic downgrade -1

# ── Utilities ─────────────────────────────────────────────────────────────────

clean: ## Remove build artefacts, caches and coverage reports
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null; true
	find . -type d -name "htmlcov"       -exec rm -rf {} + 2>/dev/null; true
	find . -type d -name "*.egg-info"    -exec rm -rf {} + 2>/dev/null; true
	find . -type d -name "build"         -exec rm -rf {} + 2>/dev/null; true
	find . -type f -name ".coverage"     -delete 2>/dev/null; true
	@echo "Clean complete."
