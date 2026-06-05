# Playwright Configuration Recipe for MCP Integration

> **Generated**: 2026-02-17T11:20:00Z
> **Repository**: Aries-Serpent/_codex_
> **Purpose**: Production-ready Playwright configuration for MCP-enabled e2e testing
> **Status**: Ready for Implementation

---

## Overview

This recipe provides complete Playwright configuration for:
- **E2E testing** with GitHub Copilot Agent/MCP integration
- **Multi-browser support** (Chromium, Firefox, WebKit)
- **CI/CD integration** with GitHub Actions
- **Visual regression testing** capabilities
- **Accessibility testing** with snapshots

---

## File: `playwright.config.ts`

### Location
```
project-root/
├── playwright.config.ts          # Main config (this file)
├── e2e/                          # Test directory
│   ├── example.spec.ts
│   └── fixtures/
├── playwright-report/             # HTML report output
└── test-results/                  # Test artifacts
```

### Complete Configuration

```typescript
/**
 * Playwright Configuration for _codex_ Repository
 *
 * Features:
 * - Multi-browser testing (Chromium, Firefox, WebKit)
 * - CI/CD optimized (parallel disabled, retry on failure)
 * - MCP integration ready (custom fixtures, reporters)
 * - Screenshot/video capture on failure
 * - Accessibility testing support
 *
 * @see https://playwright.dev/docs/test-configuration
 */

import { defineConfig, devices } from '@playwright/test';
import type { PlaywrightTestConfig } from '@playwright/test';

/**
 * Environment variable configuration
 * Set these in .env or CI/CD secrets
 */
const BASE_URL = process.env.BASE_URL || 'http://localhost:5173';
const CI = !!process.env.CI;
const WORKERS = process.env.CI ? 1 : undefined;
const RETRIES = process.env.CI ? 2 : 0;

/**
 * GitHub Actions specific configuration
 * Enables artifact upload and summary reporting
 */
const GITHUB_ACTIONS = !!process.env.GITHUB_ACTIONS;
const GITHUB_STEP_SUMMARY = process.env.GITHUB_STEP_SUMMARY;

/**
 * Main Playwright configuration
 */
export default defineConfig({
  /**
   * Test directory
   * All test files matching pattern will be discovered
   */
  testDir: './e2e',

  /**
   * Test file pattern
   * Matches: *.spec.ts, *.spec.js, *.test.ts, *.test.js
   */
  testMatch: /.*\.(spec|test)\.(ts|js)$/,

  /**
   * Parallel execution
   * Disabled on CI for stability, enabled locally for speed
   */
  fullyParallel: !CI,

  /**
   * Fail fast on CI if test.only is accidentally left in
   */
  forbidOnly: CI,

  /**
   * Retry failed tests on CI only
   * Helps with flaky tests in CI environments
   */
  retries: RETRIES,

  /**
   * Worker configuration
   * CI: 1 worker (sequential) for stability
   * Local: Default (parallel) for speed
   */
  workers: WORKERS,

  /**
   * Reporter configuration
   * Multiple reporters for comprehensive output
   */
  reporter: [
    // HTML report (interactive, best for local debugging)
    ['html', {
      outputFolder: 'playwright-report',
      open: CI ? 'never' : 'on-failure'
    }],

    // JSON report (machine-readable, for MCP integration)
    ['json', {
      outputFile: 'test-results/results.json'
    }],

    // JUnit report (for CI/CD integration)
    ['junit', {
      outputFile: 'test-results/junit.xml'
    }],

    // Line reporter (console output)
    ['list'],

    // GitHub Actions reporter (if running in GitHub Actions)
    ...(GITHUB_ACTIONS ? [['github'] as const] : []),
  ],

  /**
   * Shared test options
   * Applied to all tests across all projects
   */
  use: {
    /**
     * Base URL for navigation
     * Used in page.goto('/path') - becomes baseURL + path
     */
    baseURL: BASE_URL,

    /**
     * Trace collection
     * - on-first-retry: Collect trace only when retrying
     * - retain-on-failure: Keep traces for failed tests
     */
    trace: 'on-first-retry',

    /**
     * Screenshot capture
     * - only-on-failure: Capture screenshot when test fails
     */
    screenshot: 'only-on-failure',

    /**
     * Video recording
     * - retain-on-failure: Keep video only for failed tests
     * Helps debug visual issues and timing problems
     */
    video: 'retain-on-failure',

    /**
     * Action timeout
     * Maximum time for individual actions (click, fill, etc.)
     */
    actionTimeout: 10_000, // 10 seconds

    /**
     * Navigation timeout
     * Maximum time for page.goto() and page.reload()
     */
    navigationTimeout: 30_000, // 30 seconds

    /**
     * Viewport size (desktop default)
     * Can be overridden per test or project
     */
    viewport: { width: 1280, height: 720 },

    /**
     * Ignore HTTPS errors
     * Useful for local development with self-signed certs
     * CAUTION: Never enable for production testing
     */
    ignoreHTTPSErrors: !CI,

    /**
     * User agent
     * Can be customized for specific testing scenarios
     */
    // userAgent: 'Playwright Test / _codex_ Repository',

    /**
     * Locale and timezone
     * Ensures consistent test results across environments
     */
    locale: 'en-US',
    timezoneId: 'UTC',

    /**
     * Permissions
     * Grant specific browser permissions for testing
     */
    // permissions: ['clipboard-read', 'clipboard-write'],

    /**
     * Extra HTTP headers
     * Useful for authentication or feature flags
     */
    // extraHTTPHeaders: {
    //   'Authorization': `Bearer ${process.env.TEST_API_TOKEN}`,
    // },
  },

  /**
   * Test timeout
   * Maximum time for a single test (including retries)
   */
  timeout: 60_000, // 1 minute per test

  /**
   * Global timeout
   * Maximum time for entire test suite
   */
  globalTimeout: 30 * 60_000, // 30 minutes total

  /**
   * Expect timeout
   * Maximum time for expect() assertions
   */
  expect: {
    timeout: 10_000, // 10 seconds for assertions

    /**
     * Custom expect matchers timeout
     */
    toHaveScreenshot: {
      maxDiffPixels: 100, // Allow up to 100 pixel difference
      threshold: 0.2,     // 20% threshold for visual changes
    },
  },

  /**
   * Projects configuration
   * Define multiple browser configurations
   */
  projects: [
    /**
     * Desktop Chromium
     * Primary browser for testing
     */
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        // Chromium-specific options
        launchOptions: {
          args: [
            '--disable-dev-shm-usage', // Reduce memory usage in CI
            '--no-sandbox',            // Required for Docker/CI
          ],
        },
      },
    },

    /**
     * Desktop Firefox
     * Secondary browser for cross-browser testing
     */
    {
      name: 'firefox',
      use: {
        ...devices['Desktop Firefox'],
        // Firefox-specific options
      },
    },

    /**
     * Desktop WebKit (Safari)
     * Third browser for comprehensive coverage
     */
    {
      name: 'webkit',
      use: {
        ...devices['Desktop Safari'],
        // WebKit-specific options
      },
    },

    /**
     * Mobile browsers (optional, disabled by default)
     * Uncomment to enable mobile testing
     */
    // {
    //   name: 'Mobile Chrome',
    //   use: {
    //     ...devices['Pixel 5'],
    //   },
    // },
    // {
    //   name: 'Mobile Safari',
    //   use: {
    //     ...devices['iPhone 12'],
    //   },
    // },

    /**
     * Branded browsers (optional)
     * Test against specific browser channels
     */
    // {
    //   name: 'Microsoft Edge',
    //   use: {
    //     ...devices['Desktop Edge'],
    //     channel: 'msedge'
    //   },
    // },
    // {
    //   name: 'Google Chrome',
    //   use: {
    //     ...devices['Desktop Chrome'],
    //     channel: 'chrome'
    //   },
    // },
  ],

  /**
   * Web server configuration
   * Auto-start dev server before tests
   */
  webServer: {
    /**
     * Command to start dev server
     * Adjust based on your project's package.json scripts
     */
    command: 'npm run dev',

    /**
     * URL to wait for before starting tests
     * Must match baseURL for proper test execution
     */
    url: BASE_URL,

    /**
     * Reuse existing server
     * On CI: false (always start fresh)
     * Local: true (reuse if already running)
     */
    reuseExistingServer: !CI,

    /**
     * Server startup timeout
     * Increase if your app takes longer to start
     */
    timeout: 120_000, // 2 minutes

    /**
     * Output handling
     * pipe: Capture output for debugging
     * ignore: Suppress output
     */
    stdout: 'pipe',
    stderr: 'pipe',

    /**
     * Environment variables for dev server
     */
    env: {
      NODE_ENV: 'test',
      // Add test-specific env vars here
    },
  },

  /**
   * Output directory for test artifacts
   * Screenshots, videos, traces stored here
   */
  outputDir: 'test-results/',

  /**
   * Preserve output between runs
   * false: Clean before each run (recommended)
   * true: Keep previous artifacts
   */
  preserveOutput: 'never',

  /**
   * Snapshot path template
   * Customize snapshot file naming
   */
  snapshotPathTemplate: '{testDir}/__screenshots__/{testFilePath}/{arg}{ext}',

  /**
   * Global setup/teardown scripts
   * Run once before/after all tests
   */
  // globalSetup: require.resolve('./global-setup'),
  // globalTeardown: require.resolve('./global-teardown'),

  /**
   * Grep patterns
   * Run only tests matching specific patterns
   * Example: GREP=@smoke npm run test:e2e
   */
  grep: process.env.GREP ? new RegExp(process.env.GREP) : undefined,
  grepInvert: process.env.GREP_INVERT ? new RegExp(process.env.GREP_INVERT) : undefined,

  /**
   * Metadata
   * Custom metadata attached to test results
   */
  metadata: {
    repository: 'Aries-Serpent/_codex_',
    environment: CI ? 'CI' : 'local',
    node_version: process.version,
    playwright_version: require('@playwright/test/package.json').version,
  },
});
```

---

## Example Test Files

### Basic Test Example

```typescript
// e2e/example.spec.ts

import { test, expect } from '@playwright/test';

test.describe('Example Test Suite', () => {
  test('should load homepage', async ({ page }) => {
    // Navigate to homepage
    await page.goto('/');

    // Wait for page to be fully loaded
    await page.waitForLoadState('networkidle');

    // Assert title
    await expect(page).toHaveTitle(/Codex/i);

    // Assert main heading
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
  });

  test('should have working navigation', async ({ page }) => {
    await page.goto('/');

    // Click navigation link
    await page.getByRole('link', { name: /About/ }).click();

    // Wait for navigation
    await page.waitForURL('**/about');

    // Assert we're on the about page
    await expect(page.getByRole('heading', { name: /About/ })).toBeVisible();
  });
});
```

### Advanced Test with Custom Fixtures

```typescript
// e2e/advanced.spec.ts

import { test as base, expect } from '@playwright/test';

/**
 * Custom fixtures for MCP integration
 */
type CustomFixtures = {
  authenticatedPage: Page;
  mcpContext: {
    repositoryId: string;
    branchName: string;
  };
};

const test = base.extend<CustomFixtures>({
  /**
   * Authenticated page fixture
   * Auto-login before each test
   */
  authenticatedPage: async ({ page }, use) => {
    // Perform login
    await page.goto('/login');
    await page.fill('[name="username"]', process.env.TEST_USERNAME!);
    await page.fill('[name="password"]', process.env.TEST_PASSWORD!);
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');

    // Use authenticated page in test
    await use(page);

    // Cleanup (logout)
    await page.goto('/logout');
  },

  /**
   * MCP context fixture
   * Provides repository context from GitHub MCP
   */
  mcpContext: async ({}, use) => {
    const context = {
      repositoryId: process.env.GITHUB_REPOSITORY_ID || 'R_kgDOPjJ9Hg',
      branchName: process.env.GITHUB_REF_NAME || 'main',
    };

    await use(context);
  },
});

test.describe('Advanced Tests with Fixtures', () => {
  test('should access authenticated route', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/dashboard');
    await expect(authenticatedPage.getByText(/Welcome/)).toBeVisible();
  });

  test('should use MCP context', async ({ page, mcpContext }) => {
    console.log(`Testing repository: ${mcpContext.repositoryId}`);
    console.log(`Branch: ${mcpContext.branchName}`);

    // Test implementation...
  });
});
```

---

## package.json Scripts

### Recommended Scripts

```json
{
  "scripts": {
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui",
    "test:e2e:debug": "playwright test --debug",
    "test:e2e:headed": "playwright test --headed",
    "test:e2e:chromium": "playwright test --project=chromium",
    "test:e2e:firefox": "playwright test --project=firefox",
    "test:e2e:webkit": "playwright test --project=webkit",
    "test:e2e:mobile": "playwright test --project='Mobile Chrome' --project='Mobile Safari'",
    "test:e2e:report": "playwright show-report",
    "test:e2e:trace": "playwright show-trace",
    "test:e2e:codegen": "playwright codegen",
    "test:e2e:install": "playwright install --with-deps",
    "test:e2e:update-snapshots": "playwright test --update-snapshots",
    "test:e2e:ci": "playwright test --reporter=github --reporter=html",
    "test:e2e:smoke": "GREP='@smoke' playwright test",
    "test:e2e:regression": "GREP='@regression' playwright test"
  },
  "devDependencies": {
    "@playwright/test": "^1.57.0",
    "@types/node": "^22.10.0",
    "typescript": "~5.7.2"
  }
}
```

---

## GitHub Actions Integration

### Example Workflow

```yaml
# .github/workflows/e2e-tests.yml

name: E2E Tests (Playwright)

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main]
  workflow_dispatch:

env:
  NODE_VERSION: '22'
  PYTHON_VERSION: '3.11'

jobs:
  e2e-tests:
    name: Run E2E Tests
    runs-on: ubuntu-latest

    strategy:
      fail-fast: false
      matrix:
        browser: [chromium, firefox, webkit]

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Install Playwright browsers
        run: npx playwright install --with-deps ${{ matrix.browser }}

      - name: Run E2E tests
        env:
          BASE_URL: http://localhost:5173
          CI: true
        run: npm run test:e2e -- --project=${{ matrix.browser }}

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-results-${{ matrix.browser }}
          path: |
            playwright-report/
            test-results/
          retention-days: 7

      - name: Upload trace files
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-traces-${{ matrix.browser }}
          path: test-results/**/*.zip
          retention-days: 7

      - name: Generate summary
        if: always()
        run: |
          echo "## E2E Test Results (${{ matrix.browser }})" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY

          if [ -f test-results/results.json ]; then
            TOTAL=$(jq '.suites[].tests | length' test-results/results.json | paste -sd+ | bc)
            PASSED=$(jq '[.suites[].tests[] | select(.status == "passed")] | length' test-results/results.json)
            FAILED=$(jq '[.suites[].tests[] | select(.status == "failed")] | length' test-results/results.json)

            echo "- **Total Tests**: $TOTAL" >> $GITHUB_STEP_SUMMARY
            echo "- **Passed**: ✅ $PASSED" >> $GITHUB_STEP_SUMMARY
            echo "- **Failed**: ❌ $FAILED" >> $GITHUB_STEP_SUMMARY
          fi
```

---

## Advanced Configurations

### Visual Regression Testing

```typescript
// e2e/visual-regression.spec.ts

import { test, expect } from '@playwright/test';

test.describe('Visual Regression Tests', () => {
  test('homepage snapshot', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Take screenshot and compare with baseline
    await expect(page).toHaveScreenshot('homepage.png', {
      fullPage: true,
      animations: 'disabled',
    });
  });

  test('component snapshot', async ({ page }) => {
    await page.goto('/components');

    // Screenshot specific element
    const button = page.getByRole('button', { name: /Submit/ });
    await expect(button).toHaveScreenshot('submit-button.png');
  });
});
```

### Accessibility Testing

```typescript
// e2e/accessibility.spec.ts

import { test, expect } from '@playwright/test';

test.describe('Accessibility Tests', () => {
  test('homepage accessibility snapshot', async ({ page }) => {
    await page.goto('/');

    // Capture accessibility tree
    const snapshot = await page.accessibility.snapshot();

    // Assert structure
    expect(snapshot).toBeDefined();
    expect(snapshot!.role).toBe('WebArea');
  });

  test('keyboard navigation', async ({ page }) => {
    await page.goto('/');

    // Tab through interactive elements
    await page.keyboard.press('Tab');
    await expect(page.locator(':focus')).toHaveRole('link');

    // Press Enter on focused element
    await page.keyboard.press('Enter');
    await page.waitForNavigation();
  });
});
```

---

## Best Practices

### DO ✅

1. **Use page object model** for complex tests
2. **Add test tags** (`@smoke`, `@regression`) for filtering
3. **Use `waitForLoadState`** before assertions
4. **Capture screenshots** on failure
5. **Use `test.step`** for better reporting
6. **Set appropriate timeouts** for slow operations
7. **Run tests in CI/CD** on every PR
8. **Update snapshots** intentionally, not automatically
9. **Use fixtures** for common setup/teardown
10. **Mock external APIs** for faster, more reliable tests

### DON'T ❌

1. **Don't use `waitForTimeout`** unless absolutely necessary
2. **Don't hardcode URLs** - use `baseURL`
3. **Don't skip tests** without documenting why
4. **Don't test external sites** in CI (flaky)
5. **Don't commit test artifacts** to git
6. **Don't use `test.only`** in committed code
7. **Don't run all browsers** locally (slow)
8. **Don't ignore accessibility** testing
9. **Don't use CSS selectors** when semantic selectors available
10. **Don't test implementation details** - test user behavior

---

## Troubleshooting

### Common Issues

**Issue**: Tests fail with "Target closed"

**Solution**: Increase navigation timeout or check for page crashes
```typescript
use: {
  navigationTimeout: 60_000, // Increase timeout
}
```

---

**Issue**: Screenshots don't match baseline

**Solution**: Update snapshots intentionally
```bash
npm run test:e2e:update-snapshots
```

---

**Issue**: Tests timeout in CI but pass locally

**Solution**: Disable parallelism in CI, increase global timeout
```typescript
workers: process.env.CI ? 1 : undefined,
globalTimeout: 60 * 60_000, // 60 minutes
```

---

## References

- [Playwright Documentation](https://playwright.dev/)
- [Best Practices](https://playwright.dev/docs/best-practices)
- [CI Configuration](https://playwright.dev/docs/ci)
- [Visual Comparisons](https://playwright.dev/docs/test-snapshots)

---

**Status**: ✅ Production-Ready
**Version**: 1.0.0
**Last Updated**: 2026-02-17T11:20:00Z
