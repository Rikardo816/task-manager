# ─── Stage 1: builder ────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

# Install uv from the official distroless image — no extra layers, no pip
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv

# System deps for asyncpg compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install production deps before copying source — maximises layer cache reuse.
# This layer is only invalidated when pyproject.toml or uv.lock change.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy source and register the project itself inside the venv
COPY src/ ./src/
RUN uv sync --frozen --no-dev


# ─── Stage 2: development ────────────────────────────────────────────────────
FROM builder AS development

# Add dev extras (pytest, black, ruff, …) on top of the production venv
RUN uv sync --frozen

COPY . .

CMD ["/app/.venv/bin/uvicorn", "src.infrastructure.api.main:app", \
     "--host", "0.0.0.0", "--port", "8000", "--reload"]


# ─── Stage 3: runtime (production) ───────────────────────────────────────────
FROM python:3.12-slim AS runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app"

# Non-root user for least-privilege execution
RUN groupadd --system app && useradd --system --gid app app

# Copy only the venv and application source — no build tools, no uv binary
COPY --from=builder /app/.venv /app/.venv
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./

RUN chown -R app:app /app
USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "src.infrastructure.api.main:app", \
     "--host", "0.0.0.0", "--port", "8000", \
     "--workers", "2"]
