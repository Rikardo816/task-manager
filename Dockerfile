# ─── Stage 1: builder ────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# System deps for asyncpg (libpq not needed at build for pure-python wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install production deps into an isolated venv
RUN python -m venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml ./
# Install only production dependencies (no [dev])
RUN pip install --upgrade pip && pip install .


# ─── Stage 2: development ────────────────────────────────────────────────────
FROM builder AS development

# Install dev extras on top of the production venv
RUN pip install ".[dev]"

COPY . .

CMD ["uvicorn", "src.infrastructure.api.main:app", \
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

# Copy only the venv and application source — no build tools
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
