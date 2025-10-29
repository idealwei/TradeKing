"""SQLAlchemy models for storing trading data."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Column, DateTime, Float, Integer, String, Text

from .database import Base


class TradingDecision(Base):
    """
    Stores each trading decision made by the agent.

    This table captures the complete context and output of every agent run,
    enabling historical analysis, backtesting validation, and performance tracking.
    """

    __tablename__ = "trading_decisions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Model information
    model_choice = Column(String(50), nullable=False, index=True)  # 'gpt5', 'deepseek'
    temperature = Column(Float, nullable=False)

    # Input context (stored as JSON for flexibility)
    account_data = Column(JSON, nullable=True)
    positions_data = Column(JSON, nullable=True)
    market_data = Column(JSON, nullable=True)
    assets_data = Column(JSON, nullable=True)
    orders_data = Column(JSON, nullable=True)
    symbols = Column(JSON, nullable=True)  # List of symbols analyzed

    # Prompt and decision
    prompt = Column(Text, nullable=True)
    decision = Column(Text, nullable=False)  # The LLM's output

    # Execution metadata
    execution_time_ms = Column(Float, nullable=True)  # Latency tracking
    error_message = Column(Text, nullable=True)  # Error if decision failed

    def __repr__(self) -> str:
        return f"<TradingDecision(id={self.id}, model={self.model_choice}, timestamp={self.timestamp})>"


class ModelPerformance(Base):
    """
    Aggregated performance metrics for each model.

    This table provides a summary view for comparing different models
    and tracking performance over time.
    """

    __tablename__ = "model_performance"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    model_choice = Column(String(50), nullable=False, unique=True, index=True)

    # Performance metrics
    total_decisions = Column(Integer, default=0, nullable=False)
    successful_decisions = Column(Integer, default=0, nullable=False)
    failed_decisions = Column(Integer, default=0, nullable=False)

    avg_execution_time_ms = Column(Float, nullable=True)
    total_profit_loss = Column(Float, default=0.0, nullable=False)

    # Timestamps
    first_decision_at = Column(DateTime, nullable=True)
    last_decision_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<ModelPerformance(model={self.model_choice}, decisions={self.total_decisions})>"


class PortfolioSnapshot(Base):
    """
    Periodic snapshots of portfolio state for equity curve visualization.

    Stores the portfolio composition at specific points in time,
    enabling historical tracking and performance charting.
    """

    __tablename__ = "portfolio_snapshots"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    model_choice = Column(String(50), nullable=False, index=True)

    # Portfolio state
    total_value = Column(Float, nullable=False)  # Total portfolio value in USD
    cash_balance = Column(Float, nullable=False)
    positions = Column(JSON, nullable=False)  # Dict of {symbol: {quantity, value, unrealized_pnl}}

    # Performance metrics
    realized_pnl = Column(Float, default=0.0, nullable=False)
    unrealized_pnl = Column(Float, default=0.0, nullable=False)
    total_pnl = Column(Float, default=0.0, nullable=False)

    # Metadata
    decision_id = Column(Integer, nullable=True)  # Link to TradingDecision that triggered this snapshot

    def __repr__(self) -> str:
        return f"<PortfolioSnapshot(model={self.model_choice}, value=${self.total_value:.2f}, timestamp={self.timestamp})>"
