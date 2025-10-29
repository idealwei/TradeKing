"""Tests for portfolio endpoints."""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from storage.repository import PortfolioSnapshotRepository


class TestPortfolioEndpoint:
    """Test suite for /api/portfolio endpoints."""

    def test_get_latest_snapshot_not_found(self, client: TestClient):
        """Test retrieving latest snapshot when none exists."""
        response = client.get("/api/portfolio/latest")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_latest_snapshot_success(self, client: TestClient, test_db: Session):
        """Test retrieving latest portfolio snapshot."""
        # Create a test snapshot
        snapshot = PortfolioSnapshotRepository.create(
            db=test_db,
            model_choice="gpt5",
            total_value=100000.0,
            cash_balance=50000.0,
            positions={"NVDA.US": {"shares": 100, "avg_price": 500.0}},
            realized_pnl=5000.0,
            unrealized_pnl=2000.0,
        )

        response = client.get("/api/portfolio/latest")

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "id" in data
        assert "timestamp" in data
        assert "model_choice" in data
        assert "total_value" in data
        assert "cash_balance" in data
        assert "positions" in data
        assert "realized_pnl" in data
        assert "unrealized_pnl" in data
        assert "total_pnl" in data

        # Verify values
        assert data["model_choice"] == "gpt5"
        assert data["total_value"] == 100000.0
        assert data["cash_balance"] == 50000.0

    def test_get_latest_snapshot_with_model_filter(self, client: TestClient, test_db: Session):
        """Test retrieving latest snapshot for specific model."""
        # Create snapshots for different models
        PortfolioSnapshotRepository.create(
            db=test_db,
            model_choice="gpt5",
            total_value=100000.0,
            cash_balance=50000.0,
            positions={},
            realized_pnl=0.0,
            unrealized_pnl=0.0,
        )

        response = client.get("/api/portfolio/latest?model_choice=gpt5")

        assert response.status_code == 200
        data = response.json()
        assert data["model_choice"] == "gpt5"

    def test_get_latest_snapshot_invalid_model(self, client: TestClient):
        """Test retrieving snapshot with invalid model choice."""
        response = client.get("/api/portfolio/latest?model_choice=invalid")

        assert response.status_code == 400
        assert "Invalid model choice" in response.json()["detail"]

    def test_get_equity_curve_not_found(self, client: TestClient):
        """Test retrieving equity curve when no data exists."""
        response = client.get("/api/portfolio/equity-curve?model_choice=gpt5")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_equity_curve_success(self, client: TestClient, test_db: Session):
        """Test retrieving equity curve data."""
        # Create multiple snapshots to form a curve
        for i in range(5):
            PortfolioSnapshotRepository.create(
                db=test_db,
                model_choice="gpt5",
                total_value=100000.0 + (i * 1000),
                cash_balance=50000.0,
                positions={},
                realized_pnl=i * 500.0,
                unrealized_pnl=i * 200.0,
            )

        response = client.get("/api/portfolio/equity-curve?model_choice=gpt5")

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "model_choice" in data
        assert "data_points" in data
        assert "initial_value" in data
        assert "current_value" in data
        assert "total_return_pct" in data

        # Verify data
        assert data["model_choice"] == "gpt5"
        assert isinstance(data["data_points"], list)
        assert len(data["data_points"]) == 5

        # Verify data point structure
        if len(data["data_points"]) > 0:
            point = data["data_points"][0]
            assert "timestamp" in point
            assert "total_value" in point
            assert "total_pnl" in point

    def test_get_equity_curve_with_limit(self, client: TestClient, test_db: Session):
        """Test retrieving equity curve with custom limit."""
        # Create 10 snapshots
        for i in range(10):
            PortfolioSnapshotRepository.create(
                db=test_db,
                model_choice="gpt5",
                total_value=100000.0 + (i * 1000),
                cash_balance=50000.0,
                positions={},
                realized_pnl=0.0,
                unrealized_pnl=0.0,
            )

        response = client.get("/api/portfolio/equity-curve?model_choice=gpt5&limit=5")

        assert response.status_code == 200
        data = response.json()
        assert len(data["data_points"]) <= 5

    def test_get_equity_curve_invalid_model(self, client: TestClient):
        """Test retrieving equity curve with invalid model."""
        response = client.get("/api/portfolio/equity-curve?model_choice=invalid")

        assert response.status_code == 400
        assert "Invalid model choice" in response.json()["detail"]

    def test_get_equity_curve_missing_model_param(self, client: TestClient):
        """Test retrieving equity curve without model parameter."""
        response = client.get("/api/portfolio/equity-curve")

        # Should return validation error (422)
        assert response.status_code == 422
