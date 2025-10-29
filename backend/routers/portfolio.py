"""Portfolio and equity curve API endpoints."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from storage import get_db
from storage.repository import PortfolioSnapshotRepository
from trade_agent.config import ModelChoice

from ..schemas import EquityCurvePoint, EquityCurveResponse, PortfolioSnapshotResponse

router = APIRouter()


@router.get("/latest", response_model=PortfolioSnapshotResponse)
def get_latest_snapshot(
    model_choice: Optional[str] = Query(None, description="Filter by model (gpt5 or deepseek)"),
    db: Session = Depends(get_db),
) -> PortfolioSnapshotResponse:
    """
    Get the most recent portfolio snapshot.

    Optionally filter by model choice to get the latest snapshot for a specific model.
    """
    normalized_choice: Optional[str] = None
    if model_choice:
        try:
            normalized_choice = ModelChoice.from_string(model_choice).value
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid model choice: {model_choice}")

    snapshot = PortfolioSnapshotRepository.get_latest(db, model_choice=normalized_choice)
    if not snapshot:
        raise HTTPException(status_code=404, detail="Portfolio snapshot not found")

    return PortfolioSnapshotResponse.model_validate(snapshot)


@router.get("/equity-curve", response_model=EquityCurveResponse)
def get_equity_curve(
    model_choice: str = Query(..., description="Model to get equity curve for (gpt5 or deepseek)"),
    limit: int = Query(1000, ge=1, le=10000, description="Maximum number of data points"),
    db: Session = Depends(get_db),
) -> EquityCurveResponse:
    """
    Get equity curve data for visualization.

    Returns historical portfolio values over time for charting.
    """
    try:
        choice = ModelChoice.from_string(model_choice)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid model choice: {model_choice}")

    snapshots = PortfolioSnapshotRepository.get_equity_curve(db, model_choice=choice.value, limit=limit)

    if not snapshots:
        raise HTTPException(status_code=404, detail=f"Portfolio data not found for model: {choice.value}")

    # Convert snapshots to data points
    data_points = [
        EquityCurvePoint(timestamp=s.timestamp, total_value=s.total_value, total_pnl=s.total_pnl) for s in snapshots
    ]

    initial_value = snapshots[0].total_value - snapshots[0].total_pnl
    current_value = snapshots[-1].total_value
    total_return_pct = ((current_value - initial_value) / initial_value) * 100 if initial_value > 0 else 0.0

    return EquityCurveResponse(
        model_choice=choice.value,
        data_points=data_points,
        initial_value=initial_value,
        current_value=current_value,
        total_return_pct=total_return_pct,
    )
