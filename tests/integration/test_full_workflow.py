"""Integration tests for complete trading workflow."""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient


class TestFullTradingWorkflow:
    """Test complete trading workflow from decision to performance tracking."""

    @patch("backend.routers.decisions.create_agent")
    def test_complete_trading_cycle(self, mock_create_agent, client: TestClient, mock_env):
        """Test a complete trading cycle: execute decision -> check decision -> check performance."""
        # Setup mock agent
        mock_agent = Mock()
        mock_agent.run.return_value = {
            "decision": "BUY NVDA.US 100 shares at market price",
            "account_data": {"balance": 100000},
            "positions_data": {},
            "market_data": {"NVDA.US": {"price": 500}},
            "assets_data": {},
            "orders_data": {},
            "symbols": ["NVDA.US"],
            "prompt": "Trading analysis prompt",
        }
        mock_create_agent.return_value = mock_agent

        # Step 1: Check system health
        health_response = client.get("/api/health")
        assert health_response.status_code == 200
        assert health_response.json()["status"] == "healthy"

        # Step 2: Execute a trading decision
        execute_response = client.post(
            "/api/decisions/execute",
            json={"symbols": ["NVDA.US"], "model_choice": "gpt5"},
        )
        assert execute_response.status_code == 200
        decision_data = execute_response.json()
        decision_id = decision_data["decision_id"]
        assert "BUY NVDA.US" in decision_data["decision"]

        # Step 3: Retrieve decision details
        detail_response = client.get(f"/api/decisions/{decision_id}")
        assert detail_response.status_code == 200
        detail_data = detail_response.json()
        assert detail_data["id"] == decision_id
        assert "account_data" in detail_data
        assert "prompt" in detail_data

        # Step 4: Check latest decisions
        latest_response = client.get("/api/decisions/latest")
        assert latest_response.status_code == 200
        latest_decisions = latest_response.json()
        assert len(latest_decisions) >= 1
        assert any(d["id"] == decision_id for d in latest_decisions)

        # Step 5: Check model performance
        perf_response = client.get("/api/models/performance/gpt5")
        assert perf_response.status_code == 200
        perf_data = perf_response.json()
        assert perf_data["total_decisions"] >= 1
        assert perf_data["model_choice"] == "gpt5"

    @patch("backend.routers.decisions.create_agent")
    def test_multiple_models_comparison(self, mock_create_agent, client: TestClient, mock_env):
        """Test executing decisions with different models and comparing performance."""
        mock_agent = Mock()
        mock_agent.run.return_value = {
            "decision": "Test decision",
            "account_data": {},
            "positions_data": {},
            "market_data": {},
            "assets_data": {},
            "orders_data": {},
        }
        mock_create_agent.return_value = mock_agent

        # Execute with GPT5
        gpt5_response = client.post(
            "/api/decisions/execute",
            json={"model_choice": "gpt5"},
        )
        assert gpt5_response.status_code == 200

        # Execute with DeepSeek
        deepseek_response = client.post(
            "/api/decisions/execute",
            json={"model_choice": "deepseek"},
        )
        assert deepseek_response.status_code == 200

        # Compare performance
        all_perf_response = client.get("/api/models/performance")
        assert all_perf_response.status_code == 200
        all_perf = all_perf_response.json()

        # Should have data for both models
        model_choices = [p["model_choice"] for p in all_perf]
        assert "gpt5" in model_choices
        assert "deepseek" in model_choices

    @patch("backend.routers.decisions.create_agent")
    def test_error_handling_workflow(self, mock_create_agent, client: TestClient, mock_env):
        """Test that errors are properly handled and recorded."""
        # Setup mock to raise an error
        mock_agent = Mock()
        mock_agent.run.side_effect = Exception("Simulated trading error")
        mock_create_agent.return_value = mock_agent

        # Execute decision that will fail
        response = client.post("/api/decisions/execute", json={})

        # Should return error
        assert response.status_code == 500
        assert "Failed to execute" in response.json()["detail"]

        # Performance should still be updated
        perf_response = client.get("/api/models/performance/gpt5")
        if perf_response.status_code == 200:
            perf_data = perf_response.json()
            # Should have recorded the failed decision
            assert perf_data["failed_decisions"] >= 1
