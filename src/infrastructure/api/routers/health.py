from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import text

from src.config import get_settings
from src.infrastructure.database.connection import engine

router = APIRouter(tags=["health"])
_settings = get_settings()


class HealthResponse(BaseModel):
    status: str
    version: str


class StatusResponse(BaseModel):
    status: str
    version: str
    services: dict[str, str]


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Liveness check — is the API process alive?",
)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", version=_settings.APP_VERSION)


@router.get(
    "/status",
    response_model=StatusResponse,
    responses={503: {"model": StatusResponse}},
    summary="Readiness check — are all external services reachable?",
)
async def status() -> JSONResponse:
    checks = {"database": "ok" if await _check_database() else "error"}
    healthy = all(v == "ok" for v in checks.values())
    body = StatusResponse(
        status="healthy" if healthy else "unhealthy",
        version=_settings.APP_VERSION,
        services=checks,
    )
    return JSONResponse(
        status_code=200 if healthy else 503,
        content=body.model_dump(),
    )


async def _check_database() -> bool:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
