# EchoChat Frontend E2E Tests

## Overview

End-to-end tests for the EchoChat frontend using Playwright. These tests simulate real user interactions with the application.

## Test Structure

```
e2e/
├── homepage.spec.ts     # Homepage and content display tests
├── chat.spec.ts         # Chat widget and conversation tests
├── admin.spec.ts        # Admin dashboard tests
└── README.md           # This file
```

## Setup

### Install Dependencies

```bash
cd frontend
npm install
```

### Install Playwright Browsers

```bash
npx playwright install
```

This will download the necessary browser binaries (Chromium, Firefox, WebKit).

## Running Tests

### Run All E2E Tests

```bash
npm run test:e2e
```

### Run Tests in UI Mode (Interactive)

```bash
npm run test:e2e:ui
```

This opens the Playwright UI where you can:
- See all tests
- Run tests individually
- Watch tests execute in real-time
- Time-travel through test execution

### Run Tests in Headed Mode (See Browser)

```bash
npm run test:e2e:headed
```

### Run Specific Test File

```bash
npx playwright test e2e/homepage.spec.ts
npx playwright test e2e/chat.spec.ts
npx playwright test e2e/admin.spec.ts
```

### Run Specific Test

```bash
npx playwright test -g "should load the homepage"
```

### Run Tests in Specific Browser

```bash
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

## Test Reports

After running tests, view the HTML report:

```bash
npx playwright show-report
```

## Debugging Tests

### Debug Mode

```bash
npx playwright test --debug
```

This opens the Playwright Inspector for step-by-step debugging.

### Debug Specific Test

```bash
npx playwright test e2e/chat.spec.ts --debug
```

### View Trace

If a test fails, Playwright automatically captures a trace:

```bash
npx playwright show-trace test-results/[test-name]/trace.zip
```

## Test Configuration

Configuration is in `playwright.config.ts`:

- **Browsers**: Tests run on Chromium, Firefox, WebKit, Mobile Chrome, and Mobile Safari
- **Base URL**: `http://localhost:3000` (configurable via `PLAYWRIGHT_TEST_BASE_URL`)
- **Retries**: 2 retries on CI, 0 locally
- **Screenshots**: Captured on failure
- **Videos**: Recorded on failure
- **Traces**: Captured on first retry

## Writing Tests

### Basic Test Structure

```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test('should do something', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('h1')).toBeVisible();
  });
});
```

### Mocking API Responses

```typescript
test('should handle API response', async ({ page }) => {
  await page.route('**/api/chat', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ response: 'Test' })
    });
  });

  await page.goto('/');
  // ... test continues
});
```

### Testing User Interactions

```typescript
test('should allow user interaction', async ({ page }) => {
  await page.goto('/');

  // Type in input
  await page.locator('input[type="text"]').fill('Hello');

  // Click button
  await page.getByRole('button', { name: 'Send' }).click();

  // Verify result
  await expect(page.locator('.response')).toContainText('Hello');
});
```

## Best Practices

1. **Use data-testid attributes**: Add `data-testid` to elements for stable selectors
2. **Mock API calls**: Use route handlers to mock backend responses
3. **Wait for network idle**: Use `page.waitForLoadState('networkidle')` when needed
4. **Test user flows**: Focus on real user scenarios, not implementation details
5. **Keep tests independent**: Each test should be able to run alone
6. **Use descriptive test names**: Make it clear what behavior is being tested

## CI/CD Integration

Tests can be integrated into CI/CD pipeline:

```yaml
- name: Install dependencies
  run: npm ci

- name: Install Playwright Browsers
  run: npx playwright install --with-deps

- name: Run E2E tests
  run: npm run test:e2e

- name: Upload test results
  if: always()
  uses: actions/upload-artifact@v3
  with:
    name: playwright-report
    path: playwright-report/
```

## Troubleshooting

### Tests Timeout

Increase timeout in test:

```typescript
test('slow test', async ({ page }) => {
  test.setTimeout(60000); // 60 seconds
  // ... test code
});
```

### Element Not Found

Use proper waiting strategies:

```typescript
// Wait for element
await page.waitForSelector('.my-element');

// Or use auto-waiting assertions
await expect(page.locator('.my-element')).toBeVisible();
```

### Browser Not Installed

Install browsers:

```bash
npx playwright install
```

Or install specific browser:

```bash
npx playwright install chromium
```

## Test Coverage

E2E tests cover:

- ✅ Homepage loading and display
- ✅ Chat widget interactions
- ✅ Message sending and receiving
- ✅ Conversation history
- ✅ Admin dashboard
- ✅ Statistics display
- ✅ Job management
- ✅ Error handling
- ✅ API mocking
- ✅ Mobile responsiveness

## Resources

- [Playwright Documentation](https://playwright.dev)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [Playwright API Reference](https://playwright.dev/docs/api/class-playwright)
