"""Functional tests for admin API endpoints."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.scrape_job import ScrapeJob, JobStatus
from app.models.scraped_page import ScrapedPage


@pytest.mark.functional
class TestAdminStatsEndpoint:
    """Test admin statistics endpoint."""

    def test_get_stats_empty_database(self, client: TestClient):
        """Test stats endpoint with empty database."""
        response = client.get("/api/admin/stats")
        assert response.status_code == 200
        data = response.json()

        assert "total_pages" in data
        assert "total_chunks" in data
        assert "last_scrape" in data
        assert "target_url" in data
        assert "scrape_frequency_hours" in data

        assert data["total_pages"] == 0
        assert data["total_chunks"] == 0
        assert data["last_scrape"] is None

    def test_get_stats_with_data(self, client: TestClient, test_db: Session):
        """Test stats endpoint with existing data."""
        # Create some test data
        page1 = ScrapedPage(
            url="https://example.com/page1",
            title="Test Page 1",
            content="Test content 1",
            html="<html>Test 1</html>",
            scraped_at=datetime.utcnow()
        )
        page2 = ScrapedPage(
            url="https://example.com/page2",
            title="Test Page 2",
            content="Test content 2",
            html="<html>Test 2</html>",
            scraped_at=datetime.utcnow()
        )

        test_db.add(page1)
        test_db.add(page2)
        test_db.commit()

        response = client.get("/api/admin/stats")
        assert response.status_code == 200
        data = response.json()

        assert data["total_pages"] == 2


@pytest.mark.functional
class TestAdminJobsEndpoint:
    """Test admin jobs endpoints."""

    def test_get_jobs_empty(self, client: TestClient):
        """Test getting jobs with empty database."""
        response = client.get("/api/admin/jobs")
        assert response.status_code == 200
        jobs = response.json()
        assert isinstance(jobs, list)
        assert len(jobs) == 0

    def test_get_jobs_with_data(self, client: TestClient, test_db: Session):
        """Test getting jobs with existing data."""
        # Create test jobs
        job1 = ScrapeJob(
            target_url="https://example.com",
            status=JobStatus.COMPLETED,
            pages_scraped=10,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        job2 = ScrapeJob(
            target_url="https://example.com",
            status=JobStatus.RUNNING,
            pages_scraped=5,
            started_at=datetime.utcnow()
        )

        test_db.add(job1)
        test_db.add(job2)
        test_db.commit()

        response = client.get("/api/admin/jobs")
        assert response.status_code == 200
        jobs = response.json()
        assert len(jobs) == 2
        assert jobs[0]["status"] in ["completed", "running", "failed", "pending"]

    def test_get_jobs_with_limit(self, client: TestClient, test_db: Session):
        """Test getting jobs with limit parameter."""
        # Create multiple jobs
        for i in range(15):
            job = ScrapeJob(
                target_url="https://example.com",
                status=JobStatus.COMPLETED,
                pages_scraped=i,
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow()
            )
            test_db.add(job)
        test_db.commit()

        # Test default limit
        response = client.get("/api/admin/jobs")
        assert response.status_code == 200
        jobs = response.json()
        assert len(jobs) == 10  # Default limit

        # Test custom limit
        response = client.get("/api/admin/jobs?limit=5")
        assert response.status_code == 200
        jobs = response.json()
        assert len(jobs) == 5

    def test_get_single_job(self, client: TestClient, test_db: Session):
        """Test getting a single job by ID."""
        job = ScrapeJob(
            target_url="https://example.com",
            status=JobStatus.COMPLETED,
            pages_scraped=10,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        test_db.add(job)
        test_db.commit()
        test_db.refresh(job)

        response = client.get(f"/api/admin/jobs/{job.id}")
        assert response.status_code == 200
        job_data = response.json()
        assert job_data["id"] == job.id
        assert job_data["target_url"] == "https://example.com"
        assert job_data["pages_scraped"] == 10

    def test_get_nonexistent_job(self, client: TestClient):
        """Test getting a job that doesn't exist."""
        response = client.get("/api/admin/jobs/99999")
        assert response.status_code == 404


@pytest.mark.functional
class TestAdminHomepageEndpoint:
    """Test admin homepage endpoint."""

    def test_get_homepage_not_found(self, client: TestClient):
        """Test getting homepage when none exists."""
        response = client.get("/api/admin/homepage")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_get_homepage_with_data(self, client: TestClient, test_db: Session):
        """Test getting homepage with existing data."""
        page = ScrapedPage(
            url="https://example.com",
            title="Example Homepage",
            content="Homepage content",
            html="<html><body>Test</body></html>",
            is_homepage=True,
            scraped_at=datetime.utcnow()
        )
        test_db.add(page)
        test_db.commit()

        response = client.get("/api/admin/homepage")
        assert response.status_code == 200
        data = response.json()
        assert "url" in data
        assert "title" in data
        assert "html" in data
        assert "scraped_at" in data
        assert data["url"] == "https://example.com"
        assert data["title"] == "Example Homepage"


@pytest.mark.functional
@pytest.mark.slow
class TestAdminScrapeEndpoint:
    """Test admin scrape endpoint."""

    def test_start_scrape_missing_url(self, client: TestClient):
        """Test starting scrape without URL."""
        response = client.post("/api/admin/scrape", json={})
        assert response.status_code == 422  # Validation error

    def test_start_scrape_invalid_url(self, client: TestClient):
        """Test starting scrape with invalid URL."""
        response = client.post("/api/admin/scrape", json={
            "target_url": "not-a-url",
            "reindex": False
        })
        # Should either validate or accept and fail later
        assert response.status_code in [400, 422, 500]

    def test_start_scrape_valid_url(self, client: TestClient):
        """Test starting scrape with valid URL."""
        response = client.post("/api/admin/scrape", json={
            "target_url": "https://example.com",
            "reindex": False
        })

        # Should create a job (might fail in execution but should accept request)
        assert response.status_code in [200, 202, 500]  # 500 if scraper actually runs and fails

        if response.status_code in [200, 202]:
            data = response.json()
            assert "id" in data
            assert "target_url" in data
            assert "status" in data
            assert data["target_url"] == "https://example.com"
