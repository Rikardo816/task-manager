from dataclasses import dataclass
from uuid import UUID


@dataclass
class UserOutput:
    id: UUID
    email: str
    username: str
