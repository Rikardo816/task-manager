from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Placeholders that must never reach a production deployment.
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

    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/taskmanager"
    )
    TEST_DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/taskmanager_test"
    )

    SECRET_KEY: str = "changeme-generate-with-openssl-rand-hex-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    DOCS_USERNAME: str = "admin"
    DOCS_PASSWORD: str = "admin"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    # ── Validators ──────────────────────────────────────────────────────────

    @model_validator(mode="after")
    def validate_secrets(self) -> "Settings":
        errors: list[str] = []

        # SECRET_KEY minimum length is enforced in every environment because a
        # short key is cryptographically weak regardless of where the app runs.
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
