import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration and settings loaded from environment variables."""

    # Project Information
    PROJECT_NAME: str = "Multi-Stage Research Agent Backend"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api"

    # CORS Settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "*",
    ]

    # Database Configuration
    # Defaults to SQLite async if PostgreSQL is not configured, or use postgresql+asyncpg://...
    DATABASE_URL: str = Field(
        default=os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./research.db"),
        description="SQLAlchemy database connection URL (PostgreSQL + asyncpg or SQLite + aiosqlite)",
    )
    DATABASE_ECHO: bool = False

    # Provider Selection ('openai', 'gemini', 'claude', 'mock')
    LLM_PROVIDER: str = Field(default=os.getenv("LLM_PROVIDER", "mock"))

    # Provider Selection ('tavily', 'brave', 'serper', 'duckduckgo', 'mock')
    SEARCH_PROVIDER: str = Field(default=os.getenv("SEARCH_PROVIDER", "duckduckgo"))

    # API Keys for LLM Providers
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL: Optional[str] = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    CLAUDE_API_KEY: Optional[str] = os.getenv("CLAUDE_API_KEY")
    CLAUDE_MODEL: str = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")

    # API Keys for Search Providers
    TAVILY_API_KEY: Optional[str] = os.getenv("TAVILY_API_KEY")
    BRAVE_API_KEY: Optional[str] = os.getenv("BRAVE_API_KEY")
    SERPER_API_KEY: Optional[str] = os.getenv("SERPER_API_KEY")

    # Pipeline Concurrency & Limits
    MAX_CONCURRENT_REQUESTS: int = 5
    DEFAULT_NUMBER_OF_QUERIES: int = 4
    DEFAULT_INITIAL_SOURCES: int = 8
    DEFAULT_MAX_PAGES: int = 20
    DEFAULT_MAX_DEPTH: int = 2
    DEFAULT_MAX_PAGES_PER_DOMAIN: int = 3

    # Hard Validation Limits
    MIN_NUMBER_OF_QUERIES: int = 1
    MAX_NUMBER_OF_QUERIES: int = 10
    MIN_INITIAL_SOURCES: int = 1
    MAX_INITIAL_SOURCES: int = 30
    MIN_MAX_PAGES: int = 1
    MAX_MAX_PAGES: int = 100
    MIN_MAX_DEPTH: int = 0
    MAX_MAX_DEPTH: int = 3
    MIN_PAGES_PER_DOMAIN: int = 1
    MAX_PAGES_PER_DOMAIN: int = 10

    # Crawler Settings
    CRAWL_TIMEOUT_SECONDS: int = 15
    MAX_PAGE_SIZE_BYTES: int = 5 * 1024 * 1024  # 5 MB
    USER_AGENT: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36 ResearchAgentBot/1.0"
    )
    ENABLE_PLAYWRIGHT_FALLBACK: bool = False

    # Vector Embedding Settings
    EMBEDDING_DIM: int = 1536
    SIMILARITY_THRESHOLD_DEDUP: float = 0.85
    SIMILARITY_THRESHOLD_FOLLOWUP: float = 0.65

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
