"""Utility functions for testing."""

import json
from typing import Any, Dict
from datetime import datetime


def assert_valid_timestamp(timestamp_str: str) -> None:
    """Assert that a timestamp string is valid ISO format."""
    try:
        datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        raise AssertionError(f"Invalid timestamp format: {timestamp_str}")


def assert_json_structure(data: Any, expected_keys: list) -> None:
    """Assert that a dictionary contains all expected keys."""
    assert isinstance(data, dict), f"Expected dict, got {type(data)}"
    missing_keys = set(expected_keys) - set(data.keys())
    assert not missing_keys, f"Missing keys: {missing_keys}"


def assert_positive_number(value: Any, field_name: str = "value") -> None:
    """Assert that a value is a positive number."""
    assert isinstance(value, (int, float)), f"{field_name} must be a number"
    assert value >= 0, f"{field_name} must be non-negative"


def create_mock_trading_state(symbols: list = None) -> Dict[str, Any]:
    """Create a mock trading state for testing."""
    return {
        "decision": "Mock trading decision",
        "account_data": json.dumps({"balance": 100000.0}),
        "positions_data": json.dumps([]),
        "market_data": json.dumps({}),
        "assets_data": json.dumps({}),
        "orders_data": json.dumps([]),
        "symbols": symbols or ["NVDA.US", "TSLA.US"],
        "prompt": "Mock prompt",
    }


def validate_decision_response(response_data: Dict[str, Any]) -> None:
    """Validate the structure of a decision response."""
    required_keys = ["decision_id", "decision", "execution_time_ms", "timestamp"]
    assert_json_structure(response_data, required_keys)

    assert isinstance(response_data["decision_id"], int)
    assert isinstance(response_data["decision"], str)
    assert_positive_number(response_data["execution_time_ms"], "execution_time_ms")
    assert_valid_timestamp(response_data["timestamp"])


def validate_performance_response(response_data: Dict[str, Any]) -> None:
    """Validate the structure of a performance response."""
    required_keys = [
        "model_choice",
        "total_decisions",
        "successful_decisions",
        "failed_decisions",
        "total_profit_loss",
        "updated_at",
    ]
    assert_json_structure(response_data, required_keys)

    assert isinstance(response_data["model_choice"], str)
    assert isinstance(response_data["total_decisions"], int)
    assert isinstance(response_data["successful_decisions"], int)
    assert isinstance(response_data["failed_decisions"], int)
    assert isinstance(response_data["total_profit_loss"], (int, float))
    assert_valid_timestamp(response_data["updated_at"])
