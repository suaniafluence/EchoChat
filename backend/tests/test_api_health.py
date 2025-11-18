"""Functional tests for health endpoints."""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.functional
class TestHealthEndpoints:
    """Test health and status endpoints."""

    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint returns app info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "running"

    def test_health_endpoint(self, client: TestClient):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_root_endpoint_structure(self, client: TestClient):
        """Test root endpoint returns proper structure."""
        response = client.get("/")
        data = response.json()
        assert isinstance(data["name"], str)
        assert isinstance(data["version"], str)
        assert len(data["version"]) > 0
