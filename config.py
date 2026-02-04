"""Configuration management for ARRS system."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys (Optional)
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

    # Database
    database_url: str = "sqlite:///data/database.db"
    json_storage_path: str = "./data/analyses"

    # Crawler Settings
    crawler_timeout: int = 30
    crawler_user_agent: str = "ARRS-Bot/1.0"
    playwright_headless: bool = True

    # Rate Limiting
    claude_rpm_limit: int = 50
    crawler_delay_ms: int = 1000

    # Scoring Weights
    weight_ade: float = 0.30
    weight_arce: float = 0.20
    weight_tre: float = 0.20

    # Feature Flags
    enable_playwright: bool = True
    enable_caching: bool = True
    debug_mode: bool = False

    # LLM Provider Settings
    llm_provider: str = "openai"  # "openai", "ollama" (local, free) or "claude" (API key required)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama2"  # or "mistral", "phi", etc.
    openai_model: str = "gpt-4"  # or "gpt-3.5-turbo", "gpt-4-turbo", etc.

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Global settings instance
settings = Settings()
