# EchoChat Backend Tests

## Overview

This directory contains comprehensive test suites for the EchoChat backend API.

## Test Structure

```
tests/
├── conftest.py              # Test fixtures and configuration
├── test_api_health.py       # Health endpoint tests
├── test_api_admin.py        # Admin API functional tests
├── test_api_chat.py         # Chat API functional tests
└── test_e2e_workflows.py    # End-to-end workflow tests
```

## Test Types

### 1. **Functional Tests** (`@pytest.mark.functional`)
- Test individual API endpoints
- Verify request/response formats
- Test error handling
- Validate business logic

### 2. **End-to-End Tests** (`@pytest.mark.e2e`)
- Test complete user workflows
- Simulate real user interactions
- Test integration between components

### 3. **Slow Tests** (`@pytest.mark.slow`)
- Tests that involve actual scraping
- Long-running operations

## Running Tests

### Install Dependencies

```bash
cd backend
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Run All Tests

```bash
pytest
```

### Run Specific Test Types

```bash
# Run only functional tests
pytest -m functional

# Run only E2E tests
pytest -m e2e

# Run excluding slow tests
pytest -m "not slow"
```

### Run Specific Test Files

```bash
# Test health endpoints
pytest tests/test_api_health.py

# Test admin API
pytest tests/test_api_admin.py

# Test chat API
pytest tests/test_api_chat.py

# Test E2E workflows
pytest tests/test_e2e_workflows.py
```

### Run with Coverage

```bash
pytest --cov=app --cov-report=html --cov-report=term
```

The coverage report will be generated in `htmlcov/index.html`.

### Run Specific Tests

```bash
# Run a specific test class
pytest tests/test_api_admin.py::TestAdminStatsEndpoint

# Run a specific test method
pytest tests/test_api_admin.py::TestAdminStatsEndpoint::test_get_stats_empty_database

# Run tests matching a pattern
pytest -k "test_chat"
```

## Test Configuration

### Environment Variables

Tests use a separate test configuration with temporary databases and directories.
The following environment variables are used:

- `ANTHROPIC_API_KEY`: Set to `test-key-12345` by default
- `TARGET_URL`: Set to `https://www.example.com` for tests
- `TESTING`: Set to `1` automatically

### Test Database

Each test function gets a fresh SQLite database that is automatically cleaned up after the test completes.

## Writing New Tests

### Example Functional Test

```python
@pytest.mark.functional
def test_my_endpoint(client: TestClient):
    """Test description."""
    response = client.get("/api/my-endpoint")
    assert response.status_code == 200
    assert "expected_key" in response.json()
```

### Example E2E Test

```python
@pytest.mark.e2e
def test_complete_workflow(client: TestClient, test_db: Session):
    """Test complete user workflow."""
    # Step 1: Setup
    # ...

    # Step 2: Execute
    # ...

    # Step 3: Verify
    # ...
```

### Using Mocks

```python
from unittest.mock import Mock, patch

@patch('app.api.chat.get_rag_engine')
def test_with_mock(mock_rag_engine, client: TestClient):
    """Test using mocked RAG engine."""
    mock_engine = Mock()
    mock_engine.retrieve.return_value = [...]
    mock_rag_engine.return_value = mock_engine

    response = client.post("/api/chat", json={...})
    assert response.status_code == 200
```

## Continuous Integration

Tests are automatically run in GitHub Actions CI pipeline on:
- Push to `main` branch
- Push to `claude/**` branches
- Pull requests to `main`

See `.github/workflows/ci.yml` for CI configuration.

## Troubleshooting

### Tests Fail with Import Errors

Make sure you're in the backend directory and all dependencies are installed:

```bash
cd backend
pip install -r requirements.txt -r requirements-dev.txt
```

### Database Lock Errors

Tests use function-scoped database fixtures, so each test gets a fresh database.
If you see lock errors, make sure you're not running tests in parallel without proper configuration.

### Anthropic API Errors in Tests

Tests mock the Anthropic API by default. If you see API errors, check that the mocks are properly configured.

## Coverage Goals

- **Overall Coverage**: > 80%
- **Critical Paths**: > 95%
- **API Endpoints**: 100%

Current coverage can be viewed by running:

```bash
pytest --cov=app --cov-report=term-missing
```
