"""FastAPI application factory and configuration."""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from storage import init_db

from .routers import decisions, health, models, portfolio

# Load environment variables from the project-level .env file if present
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env", override=False)

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.

    Startup:
    - Initialize database
    - Start scheduler (if enabled)

    Shutdown:
    - Clean up resources
    """
    # Startup
    logger.info("Initializing database...")
    init_db()

    # Start scheduler if enabled
    if os.getenv("SCHEDULER_ENABLED", "false").lower() == "true":
        from .scheduler import start_scheduler

        logger.info("Starting trading scheduler...")
        start_scheduler()

    yield

    # Shutdown
    logger.info("Shutting down TradeKing backend...")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured application instance
    """
    app = FastAPI(
        title="TradeKing API",
        description="AI-driven U.S. equities trading agent with LangGraph and Longbridge integration",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, replace with specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health.router, prefix="/api", tags=["health"])
    app.include_router(decisions.router, prefix="/api/decisions", tags=["decisions"])
    app.include_router(models.router, prefix="/api/models", tags=["models"])
    app.include_router(portfolio.router, prefix="/api/portfolio", tags=["portfolio"])

    # Mount static files (frontend)
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
    if os.path.exists(static_dir):
        app.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")
        logger.info(f"Mounted frontend from {static_dir}")

    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", "8000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"

    uvicorn.run("backend.app:app", host=host, port=port, reload=debug)
