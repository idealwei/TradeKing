"""Health check endpoint."""

from __future__ import annotations

import os
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from storage import get_db

from ..schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)) -> HealthResponse:
    """
    Health check endpoint.

    Returns system status including database connectivity and scheduler state.
    """
    # Check database connection
    database_connected = False
    try:
        db.execute(text("SELECT 1"))
        database_connected = True
    except Exception:
        pass

    # Check scheduler status
    scheduler_running = os.getenv("SCHEDULER_ENABLED", "false").lower() == "true"

    return HealthResponse(
        status="healthy" if database_connected else "degraded",
        version="0.1.0",
        timestamp=datetime.utcnow(),
        database_connected=database_connected,
        scheduler_running=scheduler_running,
    )
