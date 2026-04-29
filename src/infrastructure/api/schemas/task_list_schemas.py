from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class TaskListCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)


class TaskListUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)


class TaskListResponse(BaseModel):
    id: UUID
    name: str
    owner_id: UUID
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
