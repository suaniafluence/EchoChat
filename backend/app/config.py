"""Configuration management for EchoChat."""
from pydantic_settings import BaseSettings
from pydantic import field_validator, ValidationError
from typing import List
import os
import sys
from pathlib import Path

# Calculate the backend directory (parent of app directory)
BACKEND_DIR = Path(__file__).parent.parent.resolve()
DATA_DIR = BACKEND_DIR / "data"
LOGS_DIR = BACKEND_DIR / "logs"
CHROMA_DIR = BACKEND_DIR / "chroma_data"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "EchoChat"
    app_version: str = "1.0.0"
    debug: bool = False

    # Target website
    target_url: str = "https://www.example.fr"
    scrape_frequency_hours: int = 24

    # Anthropic API
    anthropic_api_key: str
    anthropic_model: str = "claude-sonnet-4-5-20250929"

    @field_validator('anthropic_api_key')
    @classmethod
    def validate_anthropic_api_key(cls, v: str) -> str:
        """Validate that the Anthropic API key is provided."""
        if not v or not v.strip():
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable is required but not set. "
                "Please set it in your .env file or environment variables. "
                "Get your API key from: https://console.anthropic.com/"
            )
        return v.strip()

    # Database
    database_url: str = f"sqlite:///{DATA_DIR}/echochat.db"
    chroma_persist_directory: str = str(CHROMA_DIR)
    
    # RAG Configuration
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_results: int = 5
    
    # Scraper Configuration
    scraper_timeout: int = 30000  # Timeout per page in milliseconds
    scrape_job_timeout: int = 7200  # Total job timeout in seconds (2 hours)
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:8000"
    
    # Logging
    log_level: str = "INFO"
    log_file: str = str(LOGS_DIR / "app.log")
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins into list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
try:
    settings = Settings()
except ValidationError as e:
    print(f"\n❌ Configuration Error:\n", file=sys.stderr)
    for error in e.errors():
        field = error['loc'][0]
        msg = error['msg']
        print(f"  • {field}: {msg}", file=sys.stderr)
    print("\nPlease check your .env file or environment variables.\n", file=sys.stderr)
    sys.exit(1)


def get_settings() -> Settings:
    """Dependency injection for settings."""
    return settings
