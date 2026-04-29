import secrets
from contextlib import asynccontextmanager
from typing import Annotated, Any

import structlog
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

# Ensure models are registered with SQLAlchemy metadata for create_all
import src.infrastructure.database.models  # noqa: F401
from src.config import get_settings
from src.domain.exceptions.domain_exceptions import (
    AlreadyExistsError,
    DomainException,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
)
from src.infrastructure.api.routers import auth, health, task_lists, tasks
from src.infrastructure.database.connection import engine
from src.infrastructure.database.models.base import Base

logger = structlog.get_logger()
settings = get_settings()

_docs_security = HTTPBasic()


def _verify_docs(
    credentials: Annotated[HTTPBasicCredentials, Depends(_docs_security)],
) -> None:
    """HTTP Basic Auth guard for /docs, /redoc and /openapi.json.

    Uses secrets.compare_digest to prevent timing-based username/password
    enumeration attacks.
    """
    valid_user = secrets.compare_digest(
        credentials.username.encode(), settings.DOCS_USERNAME.encode()
    )
    valid_pass = secrets.compare_digest(
        credentials.password.encode(), settings.DOCS_PASSWORD.encode()
    )
    if not (valid_user and valid_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[type-arg]
    logger.info("startup", env=settings.ENVIRONMENT, version=settings.APP_VERSION)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    logger.info("shutdown")
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Task Manager API — Clean Architecture · FastAPI · PostgreSQL · JWT",
    # Docs are served manually below with HTTP Basic Auth protection.
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Protected documentation endpoints ───────────────────────────────────────


@app.get("/openapi.json", include_in_schema=False)
async def openapi_schema(
    _: Annotated[None, Depends(_verify_docs)],
) -> dict[str, Any]:
    return app.openapi()


@app.get("/docs", include_in_schema=False)
async def swagger_ui(
    _: Annotated[None, Depends(_verify_docs)],
) -> HTMLResponse:
    return get_swagger_ui_html(openapi_url="/openapi.json", title=settings.APP_NAME)


@app.get("/redoc", include_in_schema=False)
async def redoc_ui(
    _: Annotated[None, Depends(_verify_docs)],
) -> HTMLResponse:
    return get_redoc_html(openapi_url="/openapi.json", title=settings.APP_NAME)


# ── Exception handlers ───────────────────────────────────────────────────────


def _error(code: str, message: str) -> dict[str, Any]:
    return {"code": code, "detail": message}


@app.exception_handler(NotFoundError)
async def not_found_handler(_: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=_error(exc.code, exc.message),
    )


@app.exception_handler(AlreadyExistsError)
async def conflict_handler(_: Request, exc: AlreadyExistsError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=_error(exc.code, exc.message),
    )


@app.exception_handler(UnauthorizedError)
async def unauthorized_handler(_: Request, exc: UnauthorizedError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=_error(exc.code, exc.message),
    )


@app.exception_handler(ForbiddenError)
async def forbidden_handler(_: Request, exc: ForbiddenError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content=_error(exc.code, exc.message),
    )


@app.exception_handler(DomainException)
async def domain_handler(_: Request, exc: DomainException) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=_error(exc.code, exc.message),
    )


# ── Routers ──────────────────────────────────────────────────────────────────

app.include_router(health.router)
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(task_lists.router, prefix="/task-lists", tags=["task-lists"])
app.include_router(tasks.router, prefix="/task-lists", tags=["tasks"])
