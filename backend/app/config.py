"""Configuration management for EchoChat."""
from pydantic_settings import BaseSettings
from typing import List
import os


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
    anthropic_model: str = "claude-3-5-sonnet-20241022"
    
    # Database
    database_url: str = "sqlite:///./data/echochat.db"
    chroma_persist_directory: str = "./chroma_data"
    
    # RAG Configuration
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_results: int = 5
    
    # Scraper Configuration
    max_concurrent_pages: int = 5
    scraper_timeout: int = 30000
    respect_robots_txt: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:8000"
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins into list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Dependency injection for settings."""
    return settings
