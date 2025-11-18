"""End-to-end tests for complete user workflows."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime
from unittest.mock import Mock, patch

from app.models.scrape_job import ScrapeJob, JobStatus
from app.models.scraped_page import ScrapedPage


@pytest.mark.e2e
class TestAdminWorkflow:
    """Test complete admin workflow."""

    def test_admin_dashboard_empty_state(self, client: TestClient):
        """Test admin dashboard with no data."""
        # 1. Get stats (should be empty)
        response = client.get("/api/admin/stats")
        assert response.status_code == 200
        stats = response.json()
        assert stats["total_pages"] == 0
        assert stats["total_chunks"] == 0
        assert stats["last_scrape"] is None

        # 2. Get jobs (should be empty)
        response = client.get("/api/admin/jobs")
        assert response.status_code == 200
        jobs = response.json()
        assert len(jobs) == 0

        # 3. Try to get homepage (should fail)
        response = client.get("/api/admin/homepage")
        assert response.status_code == 404

    def test_admin_view_existing_data(self, client: TestClient, test_db: Session):
        """Test admin viewing existing scraped data."""
        # Setup: Create existing data
        job = ScrapeJob(
            target_url="https://example.com",
            status=JobStatus.COMPLETED,
            pages_scraped=5,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        test_db.add(job)

        for i in range(5):
            page = ScrapedPage(
                url=f"https://example.com/page{i}",
                title=f"Page {i}",
                content=f"Content for page {i}",
                html=f"<html>Page {i}</html>",
                is_homepage=(i == 0),
                scraped_at=datetime.utcnow()
            )
            test_db.add(page)

        test_db.commit()
        test_db.refresh(job)

        # 1. Check stats
        response = client.get("/api/admin/stats")
        assert response.status_code == 200
        stats = response.json()
        assert stats["total_pages"] == 5
        assert stats["last_scrape"] is not None

        # 2. Check jobs list
        response = client.get("/api/admin/jobs")
        assert response.status_code == 200
        jobs = response.json()
        assert len(jobs) == 1
        assert jobs[0]["status"] == "completed"
        assert jobs[0]["pages_scraped"] == 5

        # 3. Check specific job
        response = client.get(f"/api/admin/jobs/{job.id}")
        assert response.status_code == 200
        job_data = response.json()
        assert job_data["id"] == job.id
        assert job_data["pages_scraped"] == 5

        # 4. Get homepage
        response = client.get("/api/admin/homepage")
        assert response.status_code == 200
        homepage = response.json()
        assert homepage["url"] == "https://example.com/page0"
        assert homepage["title"] == "Page 0"

    def test_admin_monitor_job_progression(self, client: TestClient, test_db: Session):
        """Test monitoring a job as it progresses."""
        # Create a job in different states
        job = ScrapeJob(
            target_url="https://example.com",
            status=JobStatus.RUNNING,
            pages_scraped=0,
            started_at=datetime.utcnow()
        )
        test_db.add(job)
        test_db.commit()
        test_db.refresh(job)

        # 1. Check initial state
        response = client.get(f"/api/admin/jobs/{job.id}")
        assert response.status_code == 200
        job_data = response.json()
        assert job_data["status"] == "running"
        assert job_data["pages_scraped"] == 0

        # 2. Simulate progress
        job.pages_scraped = 3
        test_db.commit()

        response = client.get(f"/api/admin/jobs/{job.id}")
        job_data = response.json()
        assert job_data["pages_scraped"] == 3

        # 3. Simulate completion
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        job.pages_scraped = 10
        test_db.commit()

        response = client.get(f"/api/admin/jobs/{job.id}")
        job_data = response.json()
        assert job_data["status"] == "completed"
        assert job_data["pages_scraped"] == 10
        assert job_data["completed_at"] is not None


@pytest.mark.e2e
class TestChatWorkflow:
    """Test complete chat workflow."""

    @patch('app.api.chat.anthropic.Anthropic')
    @patch('app.api.chat.get_rag_engine')
    def test_single_turn_conversation(self, mock_rag_engine, mock_anthropic, client: TestClient):
        """Test a single-turn conversation."""
        # Setup mocks
        mock_engine = Mock()
        mock_engine.retrieve.return_value = [
            {
                'content': 'Information about the website features.',
                'metadata': {
                    'url': 'https://example.com/features',
                    'title': 'Features Page'
                }
            }
        ]
        mock_rag_engine.return_value = mock_engine

        mock_response = Mock()
        mock_response.content = [Mock(text="The website has many great features.")]
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        # User sends a message
        response = client.post("/api/chat", json={
            "message": "What features does this website have?",
            "conversation_history": []
        })

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "sources" in data
        assert len(data["sources"]) > 0

    @patch('app.api.chat.anthropic.Anthropic')
    @patch('app.api.chat.get_rag_engine')
    def test_multi_turn_conversation(self, mock_rag_engine, mock_anthropic, client: TestClient):
        """Test a multi-turn conversation with context."""
        # Setup mocks
        mock_engine = Mock()
        mock_engine.retrieve.return_value = [
            {
                'content': 'Pricing information: Basic plan is $10/month.',
                'metadata': {
                    'url': 'https://example.com/pricing',
                    'title': 'Pricing'
                }
            }
        ]
        mock_rag_engine.return_value = mock_engine

        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        # Turn 1: Initial question
        mock_response1 = Mock()
        mock_response1.content = [Mock(text="Hello! How can I help you?")]
        mock_client.messages.create.return_value = mock_response1

        response1 = client.post("/api/chat", json={
            "message": "Hello",
            "conversation_history": []
        })

        assert response1.status_code == 200
        data1 = response1.json()

        # Build conversation history
        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": data1["response"]}
        ]

        # Turn 2: Follow-up question
        mock_response2 = Mock()
        mock_response2.content = [Mock(text="The basic plan costs $10 per month.")]
        mock_client.messages.create.return_value = mock_response2

        response2 = client.post("/api/chat", json={
            "message": "What is the pricing?",
            "conversation_history": history
        })

        assert response2.status_code == 200
        data2 = response2.json()
        assert "response" in data2

        # Update history
        history.extend([
            {"role": "user", "content": "What is the pricing?"},
            {"role": "assistant", "content": data2["response"]}
        ])

        # Turn 3: Another follow-up
        mock_response3 = Mock()
        mock_response3.content = [Mock(text="Yes, there are volume discounts available.")]
        mock_client.messages.create.return_value = mock_response3

        response3 = client.post("/api/chat", json={
            "message": "Are there any discounts?",
            "conversation_history": history
        })

        assert response3.status_code == 200
        data3 = response3.json()
        assert "response" in data3

    @patch('app.api.chat.get_rag_engine')
    def test_chat_no_indexed_content_workflow(self, mock_rag_engine, client: TestClient):
        """Test chat when no content has been indexed yet."""
        # Mock RAG to return no results
        mock_engine = Mock()
        mock_engine.retrieve.return_value = []
        mock_rag_engine.return_value = mock_engine

        # User tries to chat
        response = client.post("/api/chat", json={
            "message": "Tell me about this site",
            "conversation_history": []
        })

        # Should return 404 with helpful message
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "scraped" in data["detail"].lower() or "indexed" in data["detail"].lower()


@pytest.mark.e2e
class TestFullApplicationWorkflow:
    """Test complete application workflow from scraping to chatting."""

    @patch('app.api.chat.anthropic.Anthropic')
    @patch('app.api.chat.get_rag_engine')
    def test_complete_user_journey(
        self,
        mock_rag_engine,
        mock_anthropic,
        client: TestClient,
        test_db: Session
    ):
        """Test the complete user journey: scrape -> view data -> chat."""

        # Step 1: Admin checks initial state (empty)
        response = client.get("/api/admin/stats")
        assert response.status_code == 200
        initial_stats = response.json()
        assert initial_stats["total_pages"] == 0

        # Step 2: Simulate scraping completion by adding data
        job = ScrapeJob(
            target_url="https://example.com",
            status=JobStatus.COMPLETED,
            pages_scraped=3,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        test_db.add(job)

        pages_data = [
            {
                "url": "https://example.com",
                "title": "Homepage",
                "content": "Welcome to our website. We offer great products.",
                "is_homepage": True
            },
            {
                "url": "https://example.com/about",
                "title": "About Us",
                "content": "We are a company that values quality and service.",
                "is_homepage": False
            },
            {
                "url": "https://example.com/contact",
                "title": "Contact",
                "content": "Email us at contact@example.com",
                "is_homepage": False
            }
        ]

        for page_data in pages_data:
            page = ScrapedPage(
                url=page_data["url"],
                title=page_data["title"],
                content=page_data["content"],
                html=f"<html><body>{page_data['content']}</body></html>",
                is_homepage=page_data["is_homepage"],
                scraped_at=datetime.utcnow()
            )
            test_db.add(page)

        test_db.commit()

        # Step 3: Admin checks stats again (should have data)
        response = client.get("/api/admin/stats")
        assert response.status_code == 200
        updated_stats = response.json()
        assert updated_stats["total_pages"] == 3

        # Step 4: Admin views job history
        response = client.get("/api/admin/jobs")
        assert response.status_code == 200
        jobs = response.json()
        assert len(jobs) == 1
        assert jobs[0]["status"] == "completed"

        # Step 5: Admin views homepage
        response = client.get("/api/admin/homepage")
        assert response.status_code == 200
        homepage = response.json()
        assert "Welcome to our website" in homepage["html"]

        # Step 6: User starts chatting
        # Setup mocks for chat
        mock_engine = Mock()
        mock_engine.retrieve.return_value = [
            {
                'content': 'We offer great products.',
                'metadata': {
                    'url': 'https://example.com',
                    'title': 'Homepage'
                }
            }
        ]
        mock_rag_engine.return_value = mock_engine

        mock_response = Mock()
        mock_response.content = [Mock(text="We offer great products and services.")]
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        response = client.post("/api/chat", json={
            "message": "What products do you offer?",
            "conversation_history": []
        })

        assert response.status_code == 200
        chat_data = response.json()
        assert "response" in chat_data
        assert "sources" in chat_data
        assert len(chat_data["sources"]) > 0

        # Step 7: User asks follow-up question
        mock_engine.retrieve.return_value = [
            {
                'content': 'Email us at contact@example.com',
                'metadata': {
                    'url': 'https://example.com/contact',
                    'title': 'Contact'
                }
            }
        ]

        mock_response2 = Mock()
        mock_response2.content = [Mock(text="You can email us at contact@example.com")]
        mock_client.messages.create.return_value = mock_response2

        history = [
            {"role": "user", "content": "What products do you offer?"},
            {"role": "assistant", "content": chat_data["response"]}
        ]

        response = client.post("/api/chat", json={
            "message": "How can I contact you?",
            "conversation_history": history
        })

        assert response.status_code == 200
        chat_data2 = response.json()
        assert "email" in chat_data2["response"].lower() or "contact" in chat_data2["response"].lower()
