"""Functional tests for chat API endpoints."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock


@pytest.mark.functional
class TestChatEndpoint:
    """Test chat endpoint functionality."""

    def test_chat_missing_message(self, client: TestClient):
        """Test chat endpoint with missing message."""
        response = client.post("/api/chat", json={})
        assert response.status_code == 422  # Validation error

    def test_chat_empty_message(self, client: TestClient):
        """Test chat endpoint with empty message."""
        response = client.post("/api/chat", json={
            "message": "",
            "conversation_history": []
        })
        # Should either validate or process
        assert response.status_code in [422, 404, 500]

    @patch('app.api.chat.get_rag_engine')
    def test_chat_no_context_found(self, mock_rag_engine, client: TestClient):
        """Test chat when no relevant context is found."""
        # Mock RAG engine to return no results
        mock_engine = Mock()
        mock_engine.retrieve.return_value = []
        mock_rag_engine.return_value = mock_engine

        response = client.post("/api/chat", json={
            "message": "What is this about?",
            "conversation_history": []
        })

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "No relevant information found" in data["detail"]

    @patch('app.api.chat.anthropic.Anthropic')
    @patch('app.api.chat.get_rag_engine')
    def test_chat_successful_response(self, mock_rag_engine, mock_anthropic, client: TestClient):
        """Test successful chat response."""
        # Mock RAG engine
        mock_engine = Mock()
        mock_engine.retrieve.return_value = [
            {
                'content': 'This is test content about the website.',
                'metadata': {
                    'url': 'https://example.com/page1',
                    'title': 'Test Page 1'
                }
            },
            {
                'content': 'More information about the topic.',
                'metadata': {
                    'url': 'https://example.com/page2',
                    'title': 'Test Page 2'
                }
            }
        ]
        mock_rag_engine.return_value = mock_engine

        # Mock Anthropic client
        mock_response = Mock()
        mock_response.content = [Mock(text="This is a test response from the AI.")]

        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        response = client.post("/api/chat", json={
            "message": "What is this website about?",
            "conversation_history": []
        })

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "sources" in data
        assert isinstance(data["sources"], list)
        assert len(data["sources"]) > 0
        assert "url" in data["sources"][0]
        assert "title" in data["sources"][0]
        assert "excerpt" in data["sources"][0]

    @patch('app.api.chat.anthropic.Anthropic')
    @patch('app.api.chat.get_rag_engine')
    def test_chat_with_conversation_history(self, mock_rag_engine, mock_anthropic, client: TestClient):
        """Test chat with conversation history."""
        # Mock RAG engine
        mock_engine = Mock()
        mock_engine.retrieve.return_value = [
            {
                'content': 'Context content',
                'metadata': {
                    'url': 'https://example.com',
                    'title': 'Test Page'
                }
            }
        ]
        mock_rag_engine.return_value = mock_engine

        # Mock Anthropic client
        mock_response = Mock()
        mock_response.content = [Mock(text="Response with history.")]

        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        conversation = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "Tell me more"}
        ]

        response = client.post("/api/chat", json={
            "message": "What else?",
            "conversation_history": conversation
        })

        assert response.status_code == 200
        data = response.json()
        assert "response" in data

        # Verify that conversation history was passed to Anthropic
        mock_client.messages.create.assert_called_once()
        call_args = mock_client.messages.create.call_args
        messages = call_args[1]['messages']

        # Should have history + current message (limited to last 5)
        assert len(messages) == 4  # 3 history + 1 current

    @patch('app.api.chat.anthropic.Anthropic')
    @patch('app.api.chat.get_rag_engine')
    def test_chat_anthropic_api_error(self, mock_rag_engine, mock_anthropic, client: TestClient):
        """Test chat when Anthropic API fails."""
        # Mock RAG engine
        mock_engine = Mock()
        mock_engine.retrieve.return_value = [
            {
                'content': 'Context',
                'metadata': {'url': 'https://example.com', 'title': 'Test'}
            }
        ]
        mock_rag_engine.return_value = mock_engine

        # Mock Anthropic to raise an error
        import anthropic
        mock_client = Mock()
        mock_client.messages.create.side_effect = anthropic.APIError("API Error")
        mock_anthropic.return_value = mock_client

        response = client.post("/api/chat", json={
            "message": "Test question",
            "conversation_history": []
        })

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data

    @patch('app.api.chat.anthropic.Anthropic')
    @patch('app.api.chat.get_rag_engine')
    def test_chat_source_truncation(self, mock_rag_engine, mock_anthropic, client: TestClient):
        """Test that sources are properly truncated."""
        # Mock RAG engine with long content
        long_content = "A" * 500
        mock_engine = Mock()
        mock_engine.retrieve.return_value = [
            {
                'content': long_content,
                'metadata': {
                    'url': 'https://example.com',
                    'title': 'Long Content Page'
                }
            }
        ]
        mock_rag_engine.return_value = mock_engine

        # Mock Anthropic
        mock_response = Mock()
        mock_response.content = [Mock(text="Response")]
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        response = client.post("/api/chat", json={
            "message": "Test",
            "conversation_history": []
        })

        assert response.status_code == 200
        data = response.json()
        # Excerpt should be truncated to 200 chars + "..."
        excerpt = data["sources"][0]["excerpt"]
        assert len(excerpt) <= 203  # 200 + "..."
        assert excerpt.endswith("...")

    @patch('app.api.chat.anthropic.Anthropic')
    @patch('app.api.chat.get_rag_engine')
    def test_chat_max_sources_returned(self, mock_rag_engine, mock_anthropic, client: TestClient):
        """Test that maximum 3 sources are returned."""
        # Mock RAG engine with many results
        mock_engine = Mock()
        mock_engine.retrieve.return_value = [
            {
                'content': f'Content {i}',
                'metadata': {
                    'url': f'https://example.com/page{i}',
                    'title': f'Page {i}'
                }
            }
            for i in range(10)
        ]
        mock_rag_engine.return_value = mock_engine

        # Mock Anthropic
        mock_response = Mock()
        mock_response.content = [Mock(text="Response")]
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        response = client.post("/api/chat", json={
            "message": "Test",
            "conversation_history": []
        })

        assert response.status_code == 200
        data = response.json()
        # Should only return top 3 sources
        assert len(data["sources"]) == 3
