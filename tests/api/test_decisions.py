"""Tests for trading decisions endpoints."""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient


class TestDecisionsEndpoint:
    """Test suite for /api/decisions endpoints."""

    @patch("backend.routers.decisions.create_agent")
    def test_execute_decision_success(self, mock_create_agent, client: TestClient, mock_env):
        """Test successful trading decision execution."""
        # Mock agent behavior
        mock_agent = Mock()
        mock_agent.run.return_value = {
            "decision": "Test trading decision",
            "account_data": {},
            "positions_data": {},
            "market_data": {},
            "assets_data": {},
            "orders_data": {},
            "symbols": ["NVDA.US"],
            "prompt": "Test prompt",
        }
        mock_create_agent.return_value = mock_agent

        # Execute decision
        response = client.post(
            "/api/decisions/execute",
            json={"symbols": ["NVDA.US"], "model_choice": "gpt5"},
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "decision_id" in data
        assert "decision" in data
        assert "execution_time_ms" in data
        assert "timestamp" in data

        # Verify data values
        assert data["decision"] == "Test trading decision"
        assert isinstance(data["decision_id"], int)
        assert isinstance(data["execution_time_ms"], (int, float))
        assert data["execution_time_ms"] >= 0

    @patch("backend.routers.decisions.create_agent")
    def test_execute_decision_without_symbols(self, mock_create_agent, client: TestClient, mock_env):
        """Test executing decision without specifying symbols."""
        mock_agent = Mock()
        mock_agent.run.return_value = {
            "decision": "Test decision with default symbols",
            "account_data": {},
            "positions_data": {},
            "market_data": {},
            "assets_data": {},
            "orders_data": {},
        }
        mock_create_agent.return_value = mock_agent

        response = client.post("/api/decisions/execute", json={})

        assert response.status_code == 200
        data = response.json()
        assert "decision" in data

    def test_execute_decision_invalid_model(self, client: TestClient, mock_env):
        """Test executing decision with invalid model choice."""
        response = client.post(
            "/api/decisions/execute",
            json={"model_choice": "invalid_model"},
        )

        assert response.status_code == 400
        assert "Invalid model choice" in response.json()["detail"]

    @patch("backend.routers.decisions.create_agent")
    def test_get_latest_decisions(self, mock_create_agent, client: TestClient, mock_env):
        """Test retrieving latest trading decisions."""
        # First create some decisions
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

        # Create a few decisions
        for i in range(3):
            client.post("/api/decisions/execute", json={})

        # Get latest decisions
        response = client.get("/api/decisions/latest")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) <= 10  # Default limit
        if len(data) > 0:
            decision = data[0]
            assert "id" in decision
            assert "decision" in decision
            assert "timestamp" in decision
            assert "model_choice" in decision

    def test_get_latest_decisions_with_limit(self, client: TestClient):
        """Test retrieving latest decisions with custom limit."""
        response = client.get("/api/decisions/latest?limit=5")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5

    @patch("backend.routers.decisions.create_agent")
    def test_get_decision_detail(self, mock_create_agent, client: TestClient, mock_env):
        """Test retrieving detailed decision information."""
        # Create a decision first
        mock_agent = Mock()
        mock_agent.run.return_value = {
            "decision": "Detailed test decision",
            "account_data": {},
            "positions_data": {},
            "market_data": {},
            "assets_data": {},
            "orders_data": {},
            "prompt": "Test prompt",
        }
        mock_create_agent.return_value = mock_agent

        create_response = client.post("/api/decisions/execute", json={})
        decision_id = create_response.json()["decision_id"]

        # Get decision detail
        response = client.get(f"/api/decisions/{decision_id}")

        assert response.status_code == 200
        data = response.json()

        # Verify detailed fields
        assert "id" in data
        assert "decision" in data
        assert "account_data" in data
        assert "positions_data" in data
        assert "market_data" in data
        assert "prompt" in data

    def test_get_decision_detail_not_found(self, client: TestClient):
        """Test retrieving non-existent decision."""
        response = client.get("/api/decisions/99999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_decisions_by_filter(self, client: TestClient):
        """Test filtering decisions by various criteria."""
        # Test with model filter
        response = client.get("/api/decisions/?model_choice=gpt5")
        assert response.status_code == 200

        # Test with limit
        response = client.get("/api/decisions/?limit=20")
        assert response.status_code == 200
        assert len(response.json()) <= 20

    def test_get_decisions_invalid_model_filter(self, client: TestClient):
        """Test filtering with invalid model choice."""
        response = client.get("/api/decisions/?model_choice=invalid")

        assert response.status_code == 400
        assert "Invalid model choice" in response.json()["detail"]
