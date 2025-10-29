"""Pydantic schemas for API request/response models."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TradingDecisionResponse(BaseModel):
    """Response model for a trading decision."""

    id: int
    timestamp: datetime
    model_choice: str
    temperature: float
    decision: str
    symbols: Optional[List[str]] = None
    execution_time_ms: Optional[float] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class TradingDecisionDetail(TradingDecisionResponse):
    """Detailed response model including full context."""

    account_data: Optional[Dict[str, Any]] = None
    positions_data: Optional[Dict[str, Any]] = None
    market_data: Optional[Dict[str, Any]] = None
    assets_data: Optional[Dict[str, Any]] = None
    orders_data: Optional[Dict[str, Any]] = None
    prompt: Optional[str] = None


class ModelPerformanceResponse(BaseModel):
    """Response model for model performance metrics."""

    model_choice: str
    total_decisions: int
    successful_decisions: int
    failed_decisions: int
    avg_execution_time_ms: Optional[float] = None
    total_profit_loss: float
    first_decision_at: Optional[datetime] = None
    last_decision_at: Optional[datetime] = None
    updated_at: datetime

    class Config:
        from_attributes = True


class PortfolioSnapshotResponse(BaseModel):
    """Response model for a portfolio snapshot."""

    id: int
    timestamp: datetime
    model_choice: str
    total_value: float
    cash_balance: float
    positions: Dict[str, Any]
    realized_pnl: float
    unrealized_pnl: float
    total_pnl: float
    decision_id: Optional[int] = None

    class Config:
        from_attributes = True


class EquityCurvePoint(BaseModel):
    """Data point for equity curve visualization."""

    timestamp: datetime
    total_value: float
    total_pnl: float


class EquityCurveResponse(BaseModel):
    """Response model for equity curve data."""

    model_choice: str
    data_points: List[EquityCurvePoint]
    initial_value: float
    current_value: float
    total_return_pct: float


class ExecuteDecisionRequest(BaseModel):
    """Request model for executing a trading decision."""

    symbols: Optional[List[str]] = Field(
        None, description="Symbols to analyze. If not provided, uses default watchlist."
    )
    model_choice: Optional[str] = Field(None, description="Override the default model (gpt5 or deepseek)")


class ExecuteDecisionResponse(BaseModel):
    """Response model for decision execution."""

    decision_id: int
    decision: str
    execution_time_ms: float
    timestamp: datetime


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    timestamp: datetime
    database_connected: bool
    scheduler_running: bool
