"""Model performance API endpoints."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from storage import get_db
from storage.repository import ModelPerformanceRepository

from ..schemas import ModelPerformanceResponse

router = APIRouter()


@router.get("/performance", response_model=List[ModelPerformanceResponse])
def get_all_model_performance(db: Session = Depends(get_db)) -> List[ModelPerformanceResponse]:
    """
    Get performance metrics for all models.

    Returns aggregated statistics including decision counts, execution times,
    and profit/loss for each model that has been used.
    """
    performances = ModelPerformanceRepository.get_all(db)
    return [ModelPerformanceResponse.model_validate(p) for p in performances]


@router.get("/performance/{model_choice}", response_model=ModelPerformanceResponse)
def get_model_performance(
    model_choice: str,
    db: Session = Depends(get_db),
) -> ModelPerformanceResponse:
    """
    Get performance metrics for a specific model.

    Args:
        model_choice: Model identifier (e.g., 'gpt5', 'deepseek')
    """
    performance = ModelPerformanceRepository.get_or_create(db, model_choice=model_choice)
    if performance.total_decisions == 0:
        raise HTTPException(status_code=404, detail=f"No decisions found for model: {model_choice}")

    return ModelPerformanceResponse.model_validate(performance)
