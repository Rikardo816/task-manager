from functools import lru_cache

from pydantic import computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_INSECURE_SECRETS = {
    "changeme-generate-with-openssl-rand-hex-32",
    "dev-secret-key-do-not-use-in-production",
    "CHANGE_ME",
    "admin",
    "",
}


class Settings(BaseSettings):
    APP_NAME: str = "Task Manager API"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    APP_PORT: int = 8000

    # ── Database connection parts ────────────────────────────────────────────
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "taskmanager"
    POSTGRES_TEST_DB: str = "taskmanager_test"

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @computed_field
    @property
    def TEST_DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_TEST_DB}"
        )

    # ── Auth ─────────────────────────────────────────────────────────────────
    SECRET_KEY: str = "changeme-generate-with-openssl-rand-hex-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ── API Documentation ─────────────────────────────────────────────────────
    DOCS_USERNAME: str = "admin"
    DOCS_PASSWORD: str = "admin"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    @model_validator(mode="after")
    def validate_secrets(self) -> "Settings":
        errors: list[str] = []

        if len(self.SECRET_KEY) < 32:
            errors.append(
                "SECRET_KEY must be at least 32 characters long. "
                "Generate one with: openssl rand -hex 32"
            )

        if self.ENVIRONMENT == "production":
            if self.SECRET_KEY in _INSECURE_SECRETS:
                errors.append(
                    "SECRET_KEY is set to a known insecure placeholder. "
                    "Generate a real key with: openssl rand -hex 32"
                )
            if self.DOCS_USERNAME in _INSECURE_SECRETS:
                errors.append(
                    "DOCS_USERNAME must not be 'admin' or empty in production."
                )
            if self.DOCS_PASSWORD in _INSECURE_SECRETS:
                errors.append(
                    "DOCS_PASSWORD must not be 'admin' or empty in production."
                )

        if errors:
            bullet_list = "\n".join(f"  • {e}" for e in errors)
            raise ValueError(
                f"Invalid configuration for environment '{self.ENVIRONMENT}':\n"
                + bullet_list
            )

        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
