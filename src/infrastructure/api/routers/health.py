from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    version: str


@router.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check() -> HealthResponse:
    from src.config import get_settings

    s = get_settings()
    return HealthResponse(status="ok", version=s.APP_VERSION)
