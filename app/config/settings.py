from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized application settings loaded from environment variables or .env."""

    APP_NAME: str = "PropTech Multi-Agent Real Estate Investment Analyzer"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Security & JWT
    JWT_SECRET_KEY: str = "super-secret-production-proptech-jwt-key-change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Dual DAL Databases (defaults support seamless local async SQLite + in-memory Mongo fallback if Docker isn't running)
    DATABASE_URL: str = "sqlite+aiosqlite:///./proptech_local.db"
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "proptech_ai"
    USE_IN_MEMORY_MONGO_FALLBACK: bool = True

    # External API & Agent configuration
    MARKET_API_BASE_URL: str = "https://api.nadlan-gov-mock.il/v1"
    MARKET_API_TIMEOUT_SECONDS: float = 8.0
    OPENAI_API_KEY: str = ""
    DEFAULT_MORTGAGE_RATE_PCT: float = 4.85
    DEFAULT_LOAN_YEARS: int = 25
    HITL_RISK_SCORE_THRESHOLD: int = 70
    MAX_CONTEXT_TOKENS_PER_AGENT: int = 4096

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
