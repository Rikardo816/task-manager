from fastapi import APIRouter
from pydantic import BaseModel

from src.domain.value_objects.enums import Priority, TaskStatus

router = APIRouter(prefix="/system", tags=["system"])


class EnumsResponse(BaseModel):
    task_status: list[str]
    priority: list[str]


@router.get("/enums", response_model=EnumsResponse)
async def get_enums() -> EnumsResponse:
    return EnumsResponse(
        task_status=[s.value for s in TaskStatus],
        priority=[p.value for p in Priority],
    )
