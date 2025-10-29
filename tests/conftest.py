"""Pytest configuration and shared fixtures."""

import os
import sys
from typing import Generator

import pytest
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from storage import get_db
from storage.database import Base
# Import models to ensure they are registered with Base
from storage.models import TradingDecision, ModelPerformance, PortfolioSnapshot  # noqa: F401


# Test database URL
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def test_engine():
    """Create a test database engine."""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    # Create all tables once
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_db(test_engine) -> Generator[Session, None, None]:
    """Create a test database session for each test."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(autocommit=False, autoflush=False, bind=connection)()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(test_db, test_engine) -> TestClient:
    """Create a test client with test database."""

    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    # Create app instance without lifespan
    from backend.routers import decisions, health, models, portfolio

    app = FastAPI(
        title="TradeKing API",
        description="Test API",
        version="0.1.0",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health.router, prefix="/api", tags=["health"])
    app.include_router(decisions.router, prefix="/api/decisions", tags=["decisions"])
    app.include_router(models.router, prefix="/api/models", tags=["models"])
    app.include_router(portfolio.router, prefix="/api/portfolio", tags=["portfolio"])

    # Override database dependency
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def mock_env(monkeypatch):
    """Set up mock environment variables for testing."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
    monkeypatch.setenv("TRADE_AGENT_MODEL", "gpt5")
    monkeypatch.setenv("SCHEDULER_ENABLED", "false")
    monkeypatch.setenv("DATABASE_URL", TEST_DATABASE_URL)
