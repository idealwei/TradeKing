"""Data access layer for trading decisions and performance tracking."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from .models import ModelPerformance, PortfolioSnapshot, TradingDecision


class TradingDecisionRepository:
    """Repository for managing trading decisions."""

    @staticmethod
    def create(
        db: Session,
        model_choice: str,
        temperature: float,
        decision: str,
        account_data: Optional[dict] = None,
        positions_data: Optional[dict] = None,
        market_data: Optional[dict] = None,
        assets_data: Optional[dict] = None,
        orders_data: Optional[dict] = None,
        symbols: Optional[List[str]] = None,
        prompt: Optional[str] = None,
        execution_time_ms: Optional[float] = None,
        error_message: Optional[str] = None,
    ) -> TradingDecision:
        """Create a new trading decision record."""
        decision_record = TradingDecision(
            model_choice=model_choice,
            temperature=temperature,
            decision=decision,
            account_data=account_data,
            positions_data=positions_data,
            market_data=market_data,
            assets_data=assets_data,
            orders_data=orders_data,
            symbols=symbols,
            prompt=prompt,
            execution_time_ms=execution_time_ms,
            error_message=error_message,
        )
        db.add(decision_record)
        db.commit()
        db.refresh(decision_record)
        return decision_record

    @staticmethod
    def get_latest(db: Session, limit: int = 10) -> List[TradingDecision]:
        """Get the most recent trading decisions."""
        return db.query(TradingDecision).order_by(desc(TradingDecision.timestamp)).limit(limit).all()

    @staticmethod
    def get_by_model(db: Session, model_choice: str, limit: int = 100) -> List[TradingDecision]:
        """Get trading decisions for a specific model."""
        return (
            db.query(TradingDecision)
            .filter(TradingDecision.model_choice == model_choice)
            .order_by(desc(TradingDecision.timestamp))
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_date_range(
        db: Session, start_date: datetime, end_date: datetime, model_choice: Optional[str] = None
    ) -> List[TradingDecision]:
        """Get trading decisions within a date range."""
        query = db.query(TradingDecision).filter(
            TradingDecision.timestamp >= start_date, TradingDecision.timestamp <= end_date
        )
        if model_choice:
            query = query.filter(TradingDecision.model_choice == model_choice)
        return query.order_by(TradingDecision.timestamp).all()


class ModelPerformanceRepository:
    """Repository for tracking model performance metrics."""

    @staticmethod
    def get_or_create(db: Session, model_choice: str) -> ModelPerformance:
        """Get existing performance record or create a new one."""
        perf = db.query(ModelPerformance).filter(ModelPerformance.model_choice == model_choice).first()
        if not perf:
            perf = ModelPerformance(model_choice=model_choice)
            db.add(perf)
            db.commit()
            db.refresh(perf)
        return perf

    @staticmethod
    def update_after_decision(
        db: Session,
        model_choice: str,
        execution_time_ms: Optional[float] = None,
        success: bool = True,
        profit_loss: float = 0.0,
    ) -> ModelPerformance:
        """Update performance metrics after a trading decision."""
        perf = ModelPerformanceRepository.get_or_create(db, model_choice)

        # Update counters
        perf.total_decisions += 1
        if success:
            perf.successful_decisions += 1
        else:
            perf.failed_decisions += 1

        # Update execution time (rolling average)
        if execution_time_ms is not None:
            if perf.avg_execution_time_ms is None:
                perf.avg_execution_time_ms = execution_time_ms
            else:
                # Exponential moving average
                perf.avg_execution_time_ms = 0.9 * perf.avg_execution_time_ms + 0.1 * execution_time_ms

        # Update P&L
        perf.total_profit_loss += profit_loss

        # Update timestamps
        now = datetime.utcnow()
        if perf.first_decision_at is None:
            perf.first_decision_at = now
        perf.last_decision_at = now
        perf.updated_at = now

        db.commit()
        db.refresh(perf)
        return perf

    @staticmethod
    def get_all(db: Session) -> List[ModelPerformance]:
        """Get performance metrics for all models."""
        return db.query(ModelPerformance).all()


class PortfolioSnapshotRepository:
    """Repository for portfolio snapshots."""

    @staticmethod
    def create(
        db: Session,
        model_choice: str,
        total_value: float,
        cash_balance: float,
        positions: dict,
        realized_pnl: float = 0.0,
        unrealized_pnl: float = 0.0,
        decision_id: Optional[int] = None,
    ) -> PortfolioSnapshot:
        """Create a new portfolio snapshot."""
        snapshot = PortfolioSnapshot(
            model_choice=model_choice,
            total_value=total_value,
            cash_balance=cash_balance,
            positions=positions,
            realized_pnl=realized_pnl,
            unrealized_pnl=unrealized_pnl,
            total_pnl=realized_pnl + unrealized_pnl,
            decision_id=decision_id,
        )
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)
        return snapshot

    @staticmethod
    def get_equity_curve(db: Session, model_choice: str, limit: int = 1000) -> List[PortfolioSnapshot]:
        """Get portfolio snapshots for equity curve visualization."""
        return (
            db.query(PortfolioSnapshot)
            .filter(PortfolioSnapshot.model_choice == model_choice)
            .order_by(PortfolioSnapshot.timestamp)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_latest(db: Session, model_choice: Optional[str] = None) -> Optional[PortfolioSnapshot]:
        """Get the most recent portfolio snapshot."""
        query = db.query(PortfolioSnapshot)
        if model_choice:
            query = query.filter(PortfolioSnapshot.model_choice == model_choice)
        return query.order_by(desc(PortfolioSnapshot.timestamp)).first()
