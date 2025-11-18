# EchoChat Testing Guide

Complete testing documentation for the EchoChat application.

## Overview

EchoChat has comprehensive test coverage including:

- **Backend Functional Tests**: API endpoint testing with pytest
- **Backend E2E Tests**: Complete workflow testing
- **Frontend E2E Tests**: User interface testing with Playwright

## Quick Start

### Backend Tests

```bash
cd backend
pip install -r requirements.txt -r requirements-dev.txt
pytest
```

### Frontend Tests

```bash
cd frontend
npm install
npx playwright install
npm run test:e2e
```

## Test Architecture

```
EchoChat/
├── backend/
│   ├── tests/
│   │   ├── conftest.py              # Test fixtures
│   │   ├── test_api_health.py       # Health endpoints
│   │   ├── test_api_admin.py        # Admin API tests
│   │   ├── test_api_chat.py         # Chat API tests
│   │   └── test_e2e_workflows.py    # E2E workflows
│   ├── pytest.ini                   # Pytest configuration
│   └── requirements-dev.txt         # Test dependencies
│
└── frontend/
    ├── e2e/
    │   ├── homepage.spec.ts         # Homepage tests
    │   ├── chat.spec.ts             # Chat tests
    │   └── admin.spec.ts            # Admin tests
    └── playwright.config.ts         # Playwright config
```

## Backend Testing

### Running Backend Tests

```bash
# All tests
cd backend && pytest

# Specific test type
pytest -m functional
pytest -m e2e
pytest -m "not slow"

# Specific file
pytest tests/test_api_chat.py

# With coverage
pytest --cov=app --cov-report=html
```

### Backend Test Types

#### 1. Functional Tests

Test individual API endpoints:

```python
@pytest.mark.functional
def test_get_stats(client: TestClient):
    response = client.get("/api/admin/stats")
    assert response.status_code == 200
```

#### 2. E2E Tests

Test complete workflows:

```python
@pytest.mark.e2e
def test_complete_workflow(client: TestClient, test_db: Session):
    # Setup data
    # Execute workflow
    # Verify results
```

### Backend Test Coverage

- ✅ Health endpoints (100%)
- ✅ Admin stats API
- ✅ Admin jobs API
- ✅ Admin homepage API
- ✅ Chat API with RAG
- ✅ Error handling
- ✅ Database operations
- ✅ Complete user workflows

## Frontend Testing

### Running Frontend Tests

```bash
# All E2E tests
cd frontend && npm run test:e2e

# Interactive UI mode
npm run test:e2e:ui

# Headed mode (see browser)
npm run test:e2e:headed

# Specific browser
npx playwright test --project=chromium
```

### Frontend Test Coverage

- ✅ Homepage loading
- ✅ Chat widget interactions
- ✅ Message sending/receiving
- ✅ Conversation history
- ✅ Admin dashboard
- ✅ Statistics display
- ✅ Job management
- ✅ Error handling
- ✅ Mobile responsiveness

## Test Data Management

### Backend Test Data

Tests use isolated SQLite databases:

```python
# Automatically provided via fixtures
def test_example(test_db: Session):
    # test_db is a fresh database for this test
    page = ScrapedPage(...)
    test_db.add(page)
    test_db.commit()
```

### Frontend Test Data

Mock API responses:

```typescript
await page.route('**/api/admin/stats', async (route) => {
  await route.fulfill({
    status: 200,
    body: JSON.stringify({ total_pages: 42 })
  });
});
```

## Mocking and Fixtures

### Backend Mocking

```python
from unittest.mock import Mock, patch

@patch('app.api.chat.get_rag_engine')
def test_chat(mock_rag_engine, client):
    mock_engine = Mock()
    mock_engine.retrieve.return_value = [...]
    mock_rag_engine.return_value = mock_engine
```

### Frontend Mocking

```typescript
await page.route('**/api/**', route => {
  route.fulfill({ status: 200, body: '{}' });
});
```

## Continuous Integration

Tests run automatically in GitHub Actions on:

- Push to `main`
- Push to `claude/**` branches
- Pull requests

### CI Configuration

See `.github/workflows/ci.yml`:

```yaml
- name: Run backend tests
  run: |
    cd backend
    pytest tests/ -v --cov=app

- name: Run frontend E2E tests
  run: |
    cd frontend
    npm run test:e2e
```

## Test Markers

Backend tests use pytest markers:

```python
@pytest.mark.functional  # Functional API tests
@pytest.mark.e2e        # End-to-end tests
@pytest.mark.slow       # Long-running tests
@pytest.mark.unit       # Unit tests
```

Run tests by marker:

```bash
pytest -m functional
pytest -m "e2e and not slow"
```

## Coverage Goals

### Backend Coverage Targets

- **Overall**: > 80%
- **Critical paths**: > 95%
- **API endpoints**: 100%

### Frontend Coverage

E2E tests cover all major user flows:

- Homepage display ✅
- Chat interactions ✅
- Admin operations ✅
- Error scenarios ✅

## Debugging Tests

### Backend Debugging

```bash
# Run with verbose output
pytest -vv

# Run with print statements
pytest -s

# Drop into debugger on failure
pytest --pdb
```

### Frontend Debugging

```bash
# Debug mode
npx playwright test --debug

# View trace
npx playwright show-trace test-results/.../trace.zip

# View last test report
npx playwright show-report
```

## Common Issues

### Backend Tests

**Issue**: Import errors

```bash
# Solution: Ensure you're in backend directory
cd backend
pip install -r requirements.txt -r requirements-dev.txt
```

**Issue**: Database lock errors

Solution: Tests use function-scoped databases. Ensure proper fixture usage.

### Frontend Tests

**Issue**: Browser not installed

```bash
# Solution
npx playwright install
```

**Issue**: Tests timeout

```typescript
// Increase timeout
test.setTimeout(60000);
```

## Best Practices

### Backend

1. ✅ Use fixtures for database setup
2. ✅ Mock external APIs (RAG, Anthropic)
3. ✅ Test both success and error cases
4. ✅ Keep tests independent
5. ✅ Use descriptive test names

### Frontend

1. ✅ Mock API calls
2. ✅ Use data-testid attributes
3. ✅ Wait for elements properly
4. ✅ Test user flows, not implementation
5. ✅ Keep tests fast and reliable

## Adding New Tests

### Backend Test Template

```python
@pytest.mark.functional
def test_new_feature(client: TestClient, test_db: Session):
    """Test description."""
    # Arrange
    # Act
    # Assert
```

### Frontend Test Template

```typescript
test('should do something', async ({ page }) => {
  // Arrange
  await page.goto('/');

  // Act
  await page.locator('button').click();

  // Assert
  await expect(page.locator('.result')).toBeVisible();
});
```

## Resources

- [Backend Tests README](backend/tests/README.md)
- [Frontend E2E README](frontend/e2e/README.md)
- [Pytest Documentation](https://docs.pytest.org/)
- [Playwright Documentation](https://playwright.dev)

## Test Execution Times

- **Backend Unit/Functional**: ~5-10 seconds
- **Backend E2E**: ~10-15 seconds
- **Frontend E2E** (single browser): ~30-60 seconds
- **Full test suite**: ~2-3 minutes

## Maintenance

### Update Test Dependencies

Backend:
```bash
cd backend
pip install --upgrade pytest pytest-cov pytest-asyncio
```

Frontend:
```bash
cd frontend
npm update @playwright/test
npx playwright install
```

### Review Test Coverage

```bash
# Backend
cd backend
pytest --cov=app --cov-report=html
open htmlcov/index.html

# Frontend
# (Coverage via E2E test execution logs)
```
