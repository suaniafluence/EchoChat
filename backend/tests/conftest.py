"""Test fixtures and configuration."""
import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Generator
import pytest

# Set test environment variables BEFORE any imports
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key-12345")
os.environ.setdefault("TARGET_URL", "https://www.example.com")
os.environ.setdefault("TESTING", "1")

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app
from app.models.database import Base, get_db
from app.config import Settings, settings


# Test settings
TEST_ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "test-key-12345")


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Create test settings."""
    # Create temporary directories for test
    test_data_dir = tempfile.mkdtemp(prefix="echochat_test_data_")
    test_chroma_dir = tempfile.mkdtemp(prefix="echochat_test_chroma_")
    test_logs_dir = tempfile.mkdtemp(prefix="echochat_test_logs_")

    test_config = Settings(
        app_name="EchoChat Test",
        debug=True,
        target_url="https://www.example.com",
        anthropic_api_key=TEST_ANTHROPIC_API_KEY,
        database_url=f"sqlite:///{test_data_dir}/test.db",
        chroma_persist_directory=test_chroma_dir,
        log_file=f"{test_logs_dir}/test.log",
        scrape_frequency_hours=1,
    )

    return test_config


@pytest.fixture(scope="function")
def test_db(test_settings) -> Generator[Session, None, None]:
    """Create a test database for each test function."""
    # Create engine with test database
    engine = create_engine(
        test_settings.database_url,
        connect_args={"check_same_thread": False}
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture(scope="function")
def client(test_db: Session, test_settings: Settings) -> Generator[TestClient, None, None]:
    """Create a test client with test database."""

    # Override database dependency
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    # Override settings
    def override_get_settings():
        return test_settings

    app.dependency_overrides[get_db] = override_get_db
    # Note: settings override would require refactoring the app to use dependency injection

    # Create test client without lifespan events to avoid scheduler
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from app.api import chat, admin

    test_app = FastAPI(title="EchoChat Test")

    test_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    test_app.include_router(chat.router, prefix="/api", tags=["chat"])
    test_app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

    @test_app.get("/")
    async def root():
        return {"name": "EchoChat Test", "version": "1.0.0", "status": "running"}

    @test_app.get("/health")
    async def health():
        return {"status": "healthy"}

    # Override dependencies
    test_app.dependency_overrides[get_db] = override_get_db

    with TestClient(test_app) as test_client:
        yield test_client

    # Clear overrides
    app.dependency_overrides.clear()


@pytest.fixture
def sample_scrape_job_data():
    """Sample data for creating a scrape job."""
    return {
        "target_url": "https://www.example.com",
        "reindex": False
    }


@pytest.fixture
def sample_chat_message():
    """Sample chat message data."""
    return {
        "message": "What is this website about?",
        "conversation_history": []
    }


@pytest.fixture
def sample_conversation_history():
    """Sample conversation history."""
    return [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi! How can I help you?"},
        {"role": "user", "content": "Tell me about this site"}
    ]


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """Setup test environment variables."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", TEST_ANTHROPIC_API_KEY)
    monkeypatch.setenv("TARGET_URL", "https://www.example.com")
    monkeypatch.setenv("TESTING", "1")
