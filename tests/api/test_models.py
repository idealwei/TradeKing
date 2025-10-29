"""Tests for model performance endpoints."""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient


class TestModelsEndpoint:
    """Test suite for /api/models endpoints."""

    @patch("backend.routers.decisions.create_agent")
    def test_get_all_model_performance(self, mock_create_agent, client: TestClient, mock_env):
        """Test retrieving performance metrics for all models."""
        # Create some decisions first to generate performance data
        mock_agent = Mock()
        mock_agent.run.return_value = {
            "decision": "Test decision",
            "account_data": "{}",
            "positions_data": "{}",
            "market_data": "{}",
            "assets_data": "{}",
            "orders_data": "{}",
        }
        mock_create_agent.return_value = mock_agent

        client.post("/api/decisions/execute", json={})

        # Get all model performance
        response = client.get("/api/models/performance")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        if len(data) > 0:
            perf = data[0]
            assert "model_choice" in perf
            assert "total_decisions" in perf
            assert "successful_decisions" in perf
            assert "failed_decisions" in perf
            assert "avg_execution_time_ms" in perf
            assert "total_profit_loss" in perf
            assert "updated_at" in perf

    @patch("backend.routers.decisions.create_agent")
    def test_get_specific_model_performance(self, mock_create_agent, client: TestClient, mock_env):
        """Test retrieving performance for a specific model."""
        # Create a decision for the model
        mock_agent = Mock()
        mock_agent.run.return_value = {
            "decision": "Test decision for gpt5",
            "account_data": "{}",
            "positions_data": "{}",
            "market_data": "{}",
            "assets_data": "{}",
            "orders_data": "{}",
        }
        mock_create_agent.return_value = mock_agent

        client.post("/api/decisions/execute", json={"model_choice": "gpt5"})

        # Get performance for specific model
        response = client.get("/api/models/performance/gpt5")

        assert response.status_code == 200
        data = response.json()

        assert data["model_choice"] == "gpt5"
        assert data["total_decisions"] >= 1
        assert isinstance(data["successful_decisions"], int)
        assert isinstance(data["failed_decisions"], int)

    def test_get_model_performance_invalid_model(self, client: TestClient):
        """Test retrieving performance for invalid model."""
        response = client.get("/api/models/performance/invalid_model")

        assert response.status_code == 400
        assert "Invalid model choice" in response.json()["detail"]

    def test_get_model_performance_no_data(self, client: TestClient):
        """Test retrieving performance for model with no decisions."""
        # This should return 404 since there are no decisions
        response = client.get("/api/models/performance/deepseek")

        # Should either return empty data or 404
        assert response.status_code in [200, 404]

    @patch("backend.routers.decisions.create_agent")
    def test_model_performance_metrics_accuracy(self, mock_create_agent, client: TestClient, mock_env):
        """Test that performance metrics are calculated correctly."""
        mock_agent = Mock()
        mock_agent.run.return_value = {
            "decision": "Test decision",
            "account_data": "{}",
            "positions_data": "{}",
            "market_data": "{}",
            "assets_data": "{}",
            "orders_data": "{}",
        }
        mock_create_agent.return_value = mock_agent

        # Execute multiple decisions
        num_decisions = 3
        for _ in range(num_decisions):
            client.post("/api/decisions/execute", json={})

        response = client.get("/api/models/performance/gpt5")
        data = response.json()

        # Verify counts
        assert data["total_decisions"] == num_decisions
        assert data["successful_decisions"] + data["failed_decisions"] == data["total_decisions"]
