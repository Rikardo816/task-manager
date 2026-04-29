from dataclasses import dataclass
from uuid import UUID


@dataclass
class RegisterUserInput:
    email: str
    username: str
    password: str


@dataclass
class RegisterUserOutput:
    id: UUID
    email: str
    username: str


@dataclass
class LoginInput:
    email: str
    password: str


@dataclass
class LoginOutput:
    access_token: str
    token_type: str = "bearer"
