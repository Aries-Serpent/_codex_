/**
 * Playwright Configuration for Cognitive App E2E Tests
 *
 * Configuration for running end-to-end tests with Playwright.
 * Tests validate lazy initialization, mock fallback, and API integration.
 *
 * @see https://playwright.dev/docs/test-configuration
 */

import { defineConfig, devices } from '@playwright/test';

/**
 * Read environment variables from .env file if available.
 * https://github.com/motdotla/dotenv
 */
// import dotenv from 'dotenv';
// dotenv.config();

/**
 * IMP-007: HAR replay configuration flag for offline CI.
 *
 * Extracted as a named constant for readability and testability.
 * When `CI` or `PLAYWRIGHT_HAR_REPLAY` is set, service workers are blocked
 * so that network traffic can be intercepted by a pre-recorded HAR cache
 * by other parts of the test harness (for example, via Playwright routing
 * or global setup code). This file only toggles the HAR mode flag; it does
 * not itself define which HAR file is used or how routes are matched.
 */
const shouldUseHarReplay = !!(process.env.CI || process.env.PLAYWRIGHT_HAR_REPLAY);
const harReplayConfig = shouldUseHarReplay ? { serviceWorkers: 'block' as const } : {};

/**
 * See https://playwright.dev/docs/test-configuration.
 */
export default defineConfig({
  testDir: './e2e',

  /* Run tests in files in parallel */
  fullyParallel: true,

  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,

  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,

  /* Opt out of parallel tests on CI. */
  workers: process.env.CI ? 1 : undefined,

  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: [
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
    ['json', { outputFile: 'playwright-results.json' }],
    ['list'],
  ],

  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: process.env.BASE_URL || 'http://localhost:5173',

    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: 'on-first-retry',

    /* Screenshot only on failure */
    screenshot: 'only-on-failure',

    /* Video only on failure */
    video: 'retain-on-failure',

    /* Maximum time each action such as `click()` can take */
    actionTimeout: 10000,

    /* Maximum time each navigation action can take */
    navigationTimeout: 30000,

    /* IMP-007: HAR replay for offline CI.
     *
     * When running in CI (or when PLAYWRIGHT_HAR_REPLAY=1 is set) this
     * configuration blocks service workers via `harReplayConfig` so that
     * Playwright's HAR-based routing logic (implemented elsewhere in the
     * test harness) can reliably intercept network requests instead of
     * hitting the live backend. This makes the E2E suite deterministic in
     * environments where the cognitive_app CLI server is not started.
     *
     * The concrete HAR file (for example, a file captured by a scheduled
     * workflow and stored at `cognitive_app/public/har-cache/api-demo.har`)
     * and the actual route-matching rules are configured outside this file.
     * This config layer only enables or disables HAR mode.
     */
    ...harReplayConfig,
  },

  /* Configure projects for major browsers */
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },

    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },

    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },

    /* Test against mobile viewports. */
    // {
    //   name: 'Mobile Chrome',
    //   use: { ...devices['Pixel 5'] },
    // },
    // {
    //   name: 'Mobile Safari',
    //   use: { ...devices['iPhone 12'] },
    // },

    /* Test against branded browsers. */
    // {
    //   name: 'Microsoft Edge',
    //   use: { ...devices['Desktop Edge'], channel: 'msedge' },
    // },
    // {
    //   name: 'Google Chrome',
    //   use: { ...devices['Desktop Chrome'], channel: 'chrome' },
    // },
  ],

  /* Run your local dev server before starting the tests */
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000, // 2 minutes to start dev server
    stdout: 'pipe',
    stderr: 'pipe',
  },

  /* Global timeout for each test */
  timeout: 60 * 1000, // 1 minute per test

  /* Global timeout for the entire test run */
  globalTimeout: 30 * 60 * 1000, // 30 minutes total

  /* Expect timeout */
  expect: {
    timeout: 10 * 1000, // 10 seconds for expect assertions
  },
});
