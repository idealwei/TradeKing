"""Tests for health check endpoint."""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Test suite for /api/health endpoint."""

    def test_health_check_success(self, client: TestClient):
        """Test that health check returns successful response."""
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "status" in data
        assert "version" in data
        assert "timestamp" in data
        assert "database_connected" in data
        assert "scheduler_running" in data

        # Verify data types
        assert isinstance(data["status"], str)
        assert isinstance(data["version"], str)
        assert isinstance(data["database_connected"], bool)
        assert isinstance(data["scheduler_running"], bool)

    def test_health_check_database_connected(self, client: TestClient):
        """Test that database connection is verified."""
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()

        # Database should be connected in tests
        assert data["database_connected"] is True
        assert data["status"] in ["healthy", "degraded"]

    def test_health_check_version(self, client: TestClient):
        """Test that version is returned."""
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()

        # Version should match
        assert data["version"] == "0.1.0"
