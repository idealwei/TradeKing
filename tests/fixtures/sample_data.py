"""Sample data for testing."""

from datetime import datetime, timedelta


# Sample trading decision data
SAMPLE_DECISION = {
    "decision": "BUY NVDA.US 100 shares at market price. SELL TSLA.US 50 shares at limit $200.",
    "account_data": '{"balance": 100000.00, "buying_power": 80000.00}',
    "positions_data": '[{"symbol": "TSLA.US", "shares": 100, "avg_price": 180.00}]',
    "market_data": '{"NVDA.US": {"price": 500.00, "change": 2.5}, "TSLA.US": {"price": 195.00, "change": -1.2}}',
    "assets_data": '{"total": 120000.00, "cash": 100000.00, "securities": 20000.00}',
    "orders_data": '[]',
    "symbols": ["NVDA.US", "TSLA.US"],
    "prompt": "Test trading prompt",
}

# Sample portfolio snapshot
SAMPLE_PORTFOLIO = {
    "model_choice": "gpt5",
    "total_value": 120000.0,
    "cash_balance": 80000.0,
    "positions": {
        "NVDA.US": {"shares": 100, "avg_price": 500.0, "current_price": 505.0, "market_value": 50500.0},
        "TSLA.US": {"shares": 50, "avg_price": 180.0, "current_price": 195.0, "market_value": 9750.0},
    },
    "realized_pnl": 2000.0,
    "unrealized_pnl": 1250.0,
}

# Sample model performance data
SAMPLE_PERFORMANCE = {
    "model_choice": "gpt5",
    "total_decisions": 10,
    "successful_decisions": 9,
    "failed_decisions": 1,
    "avg_execution_time_ms": 1500.0,
    "total_profit_loss": 5000.0,
}

# Sample market data
SAMPLE_MARKET_DATA = {
    "NVDA.US": {
        "symbol": "NVDA.US",
        "price": 500.00,
        "change": 2.5,
        "change_percent": 0.5,
        "volume": 10000000,
        "high": 505.00,
        "low": 495.00,
        "open": 498.00,
    },
    "TSLA.US": {
        "symbol": "TSLA.US",
        "price": 195.00,
        "change": -1.2,
        "change_percent": -0.61,
        "volume": 15000000,
        "high": 198.00,
        "low": 192.00,
        "open": 196.00,
    },
}


def generate_equity_curve_data(num_points=30, initial_value=100000.0):
    """Generate sample equity curve data points."""
    data_points = []
    current_value = initial_value
    current_pnl = 0.0

    for i in range(num_points):
        # Simulate some volatility
        change = (i % 5 - 2) * 100  # Simple zigzag pattern
        current_value += change
        current_pnl += change

        data_points.append(
            {
                "timestamp": (datetime.utcnow() - timedelta(days=num_points - i)).isoformat(),
                "total_value": round(current_value, 2),
                "total_pnl": round(current_pnl, 2),
            }
        )

    return data_points
