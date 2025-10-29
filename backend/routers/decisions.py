"""Trading decisions API endpoints."""

from __future__ import annotations

import time
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from storage import get_db
from storage.repository import TradingDecisionRepository, ModelPerformanceRepository
from trade_agent.config import AgentSettings, ModelChoice
from trade_agent.runtime import create_agent

from ..schemas import (
    ExecuteDecisionRequest,
    ExecuteDecisionResponse,
    TradingDecisionDetail,
    TradingDecisionResponse,
)

router = APIRouter()


@router.post("/execute", response_model=ExecuteDecisionResponse)
async def execute_decision(
    request: ExecuteDecisionRequest,
    db: Session = Depends(get_db),
) -> ExecuteDecisionResponse:
    """
    Execute a trading decision using the configured agent.

    This endpoint runs the trading agent, stores the result in the database,
    and returns the decision along with execution metadata.
    """
    start_time = time.time()

    try:
        # Create agent settings
        settings = AgentSettings.from_env()
        if request.model_choice:
            try:
                settings.model_choice = ModelChoice.from_string(request.model_choice)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid model choice: {request.model_choice}")

        # Create and run agent
        agent = create_agent(settings=settings)
        initial_state = {"symbols": request.symbols} if request.symbols else None
        result = agent.run(initial_state=initial_state)

        execution_time_ms = (time.time() - start_time) * 1000
        decision_text = result.get("decision", "")

        # Store decision in database
        decision_record = TradingDecisionRepository.create(
            db=db,
            model_choice=settings.model_choice.value,
            temperature=settings.temperature,
            decision=decision_text,
            account_data=result.get("account_data"),
            positions_data=result.get("positions_data"),
            market_data=result.get("market_data"),
            assets_data=result.get("assets_data"),
            orders_data=result.get("orders_data"),
            symbols=result.get("symbols"),
            prompt=result.get("prompt"),
            execution_time_ms=execution_time_ms,
        )

        # Update model performance
        ModelPerformanceRepository.update_after_decision(
            db=db,
            model_choice=settings.model_choice.value,
            execution_time_ms=execution_time_ms,
            success=True,
        )

        return ExecuteDecisionResponse(
            decision_id=decision_record.id,
            decision=decision_text,
            execution_time_ms=execution_time_ms,
            timestamp=decision_record.timestamp,
        )

    except Exception as e:
        execution_time_ms = (time.time() - start_time) * 1000

        # Store failed decision
        settings = AgentSettings.from_env()
        TradingDecisionRepository.create(
            db=db,
            model_choice=settings.model_choice.value,
            temperature=settings.temperature,
            decision="",
            execution_time_ms=execution_time_ms,
            error_message=str(e),
        )

        # Update performance metrics
        ModelPerformanceRepository.update_after_decision(
            db=db,
            model_choice=settings.model_choice.value,
            execution_time_ms=execution_time_ms,
            success=False,
        )

        raise HTTPException(status_code=500, detail=f"Failed to execute trading decision: {str(e)}")


@router.get("/latest", response_model=List[TradingDecisionResponse])
def get_latest_decisions(
    limit: int = Query(10, ge=1, le=100, description="Number of decisions to return"),
    db: Session = Depends(get_db),
) -> List[TradingDecisionResponse]:
    """
    Get the most recent trading decisions.

    Returns a list of recent decisions ordered by timestamp (newest first).
    """
    decisions = TradingDecisionRepository.get_latest(db, limit=limit)
    return [TradingDecisionResponse.model_validate(d) for d in decisions]


@router.get("/{decision_id}", response_model=TradingDecisionDetail)
def get_decision_detail(
    decision_id: int,
    db: Session = Depends(get_db),
) -> TradingDecisionDetail:
    """
    Get detailed information about a specific trading decision.

    Includes full context data (account, positions, market data, etc.)
    and the complete prompt used.
    """
    from storage.models import TradingDecision

    decision = db.query(TradingDecision).filter(TradingDecision.id == decision_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    return TradingDecisionDetail.model_validate(decision)


@router.get("/", response_model=List[TradingDecisionResponse])
def get_decisions_by_filter(
    model_choice: Optional[str] = Query(None, description="Filter by model (gpt5 or deepseek)"),
    start_date: Optional[datetime] = Query(None, description="Start date (ISO 8601)"),
    end_date: Optional[datetime] = Query(None, description="End date (ISO 8601)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    db: Session = Depends(get_db),
) -> List[TradingDecisionResponse]:
    """
    Get trading decisions with optional filters.

    Supports filtering by model choice and date range.
    """
    canonical_choice = None
    if model_choice:
        try:
            canonical_choice = ModelChoice.from_string(model_choice).value
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid model choice: {model_choice}")

    if start_date and end_date:
        decisions = TradingDecisionRepository.get_by_date_range(
            db, start_date=start_date, end_date=end_date, model_choice=canonical_choice
        )
    elif canonical_choice:
        decisions = TradingDecisionRepository.get_by_model(db, model_choice=canonical_choice, limit=limit)
    else:
        decisions = TradingDecisionRepository.get_latest(db, limit=limit)

    return [TradingDecisionResponse.model_validate(d) for d in decisions]
