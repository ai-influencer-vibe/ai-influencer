"""Application configuration models and helpers."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-driven runtime configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: str = Field(default="development", alias="APP_ENV")
    app_name: str = Field(default="AI Influencer Platform", alias="APP_NAME")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    secret_key: str = Field(default="change-me", alias="SECRET_KEY")
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    postgres_db: str = Field(default="ai_influencer", alias="POSTGRES_DB")
    postgres_user: str = Field(default="app", alias="POSTGRES_USER")
    postgres_password: str = Field(default="app", alias="POSTGRES_PASSWORD")
    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")

    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")

    text_provider: str = Field(default="mock", alias="TEXT_PROVIDER")
    image_provider: str = Field(default="mock", alias="IMAGE_PROVIDER")
    embedding_provider: str = Field(default="mock", alias="EMBEDDING_PROVIDER")

    @property
    def database_url(self) -> str:
        """Build the SQLAlchemy connection string for PostgreSQL."""

        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        """Build the Redis connection string for caching and Celery."""

        return f"redis://{self.redis_host}:{self.redis_port}/0"


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings object for the current process."""

    return Settings()
