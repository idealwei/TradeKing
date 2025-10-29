"""Scheduler for automated trading decision execution."""

from __future__ import annotations

import logging
import os

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

# Global scheduler instance
_scheduler: BackgroundScheduler | None = None


def execute_trading_decision_job():
    """
    Job function that executes a trading decision.

    This is called periodically by the scheduler.
    """
    try:
        from storage import SessionLocal
        from storage.repository import TradingDecisionRepository, ModelPerformanceRepository
        from trade_agent.runtime import create_agent
        import time

        logger.info("Executing scheduled trading decision...")

        db = SessionLocal()
        try:
            start_time = time.time()

            # Create and run agent
            agent = create_agent()
            result = agent.run()
            decision_text = result.get("decision", "")
            execution_time_ms = (time.time() - start_time) * 1000

            # Get model choice from settings
            from trade_agent.config import AgentSettings

            settings = AgentSettings.from_env()

            # Store decision
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

            # Update performance
            ModelPerformanceRepository.update_after_decision(
                db=db,
                model_choice=settings.model_choice.value,
                execution_time_ms=execution_time_ms,
                success=True,
            )

            logger.info(f"Successfully executed decision {decision_record.id}")

        except Exception as e:
            logger.error(f"Failed to execute scheduled trading decision: {e}", exc_info=True)
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Critical error in scheduler job: {e}", exc_info=True)


def start_scheduler():
    """
    Start the background scheduler for automated trading decisions.

    The scheduler interval is configured via the SCHEDULER_INTERVAL_MINUTES
    environment variable (default: 5 minutes).
    """
    global _scheduler

    if _scheduler is not None:
        logger.warning("Scheduler already running")
        return

    interval_minutes = int(os.getenv("SCHEDULER_INTERVAL_MINUTES", "5"))

    _scheduler = BackgroundScheduler()
    _scheduler.add_job(
        execute_trading_decision_job,
        trigger=IntervalTrigger(minutes=interval_minutes),
        id="trading_decision_job",
        name="Execute Trading Decision",
        replace_existing=True,
    )
    _scheduler.start()

    logger.info(f"Scheduler started with {interval_minutes}-minute interval")


def stop_scheduler():
    """Stop the background scheduler."""
    global _scheduler

    if _scheduler is None:
        return

    _scheduler.shutdown()
    _scheduler = None
    logger.info("Scheduler stopped")
