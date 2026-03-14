/**
 * har-capture.spec.ts
 *
 * Playwright spec that walks through the full Cognitive App and records
 * all API interactions as a HAR (HTTP Archive) file.
 *
 * The recorded HAR is saved to:
 *   cognitive_app/public/har-cache/api-demo.har
 *
 * This file is stored in Git LFS and used by `har-replay-client.ts` to
 * make the app fully functional on GitHub Pages (no live backend needed).
 *
 * Run manually:
 *   npm run test:e2e -- har-capture.spec.ts
 *   BASE_URL=https://aries-serpent.github.io/_codex_/cognitive_app/ npm run test:e2e -- har-capture.spec.ts
 *
 * Run via CI:
 *   .github/workflows/har-capture.yml (schedule + workflow_dispatch)
 *
 * GitHub App token injection:
 *   Set VITE_GITHUB_TOKEN in env to use the App installation token
 *   (fetched from CLI server /api/github/token when available).
 */

import { test, expect, Page, BrowserContext } from '@playwright/test';
import * as path from 'path';
import * as fs from 'fs';

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const HAR_PATH = path.resolve(__dirname, '../public/har-cache/api-demo.har');
const BASE     = process.env.BASE_URL ?? 'http://localhost:5173';

// Routes we want to capture (localhost CLI server or any backend)
const CAPTURE_URL_FILTER = /localhost:(8765|5173|3000)|aries-serpent\.github\.io/;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

async function waitForAppReady(page: Page): Promise<void> {
  await page.waitForLoadState('networkidle', { timeout: 30_000 });
  // Wait for the React root to mount
  await page.waitForSelector('#root, [data-testid="app-root"], main', { timeout: 15_000 });
}

async function clickIfVisible(page: Page, selector: string): Promise<boolean> {
  try {
    const el = page.locator(selector).first();
    if (await el.isVisible({ timeout: 2_000 })) {
      await el.click();
      await page.waitForTimeout(500);
      return true;
    }
  } catch {
    // not found — continue
  }
  return false;
}

// ---------------------------------------------------------------------------
// HAR capture test suite
// ---------------------------------------------------------------------------

test.describe('HAR capture — Cognitive App full walkthrough', () => {
  let context: BrowserContext;
  let page: Page;

  test.beforeAll(async ({ browser }) => {
    // Ensure output directory exists
    fs.mkdirSync(path.dirname(HAR_PATH), { recursive: true });

    // Create context with HAR recording enabled
    context = await browser.newContext({
      recordHar: {
        path:      HAR_PATH,
        mode:      'full',          // capture all request/response bodies
        urlFilter: CAPTURE_URL_FILTER,
      },
      // Inject GitHub token if available (raises rate limit 60 → 5,000 req/hr)
      extraHTTPHeaders: process.env.VITE_GITHUB_TOKEN
        ? { 'X-Har-Capture': 'true' }
        : {},
    });

    page = await context.newPage();
  });

  test.afterAll(async () => {
    await context.close(); // finalises and writes the HAR file
    console.log(`\n✅ HAR saved to: ${HAR_PATH}`);

    // Report entry count
    try {
      const har = JSON.parse(fs.readFileSync(HAR_PATH, 'utf-8'));
      const count = har?.log?.entries?.length ?? 0;
      console.log(`   Recorded ${count} entries`);
    } catch {
      // non-fatal
    }
  });

  // ── 1. Landing page ───────────────────────────────────────────────────────
  test('01 — landing page loads', async () => {
    await page.goto(BASE, { waitUntil: 'domcontentloaded' });
    await waitForAppReady(page);
    await expect(page).toHaveTitle(/.+/);
    await page.waitForTimeout(1_000);
  });

  // ── 2. Dashboard / metrics ────────────────────────────────────────────────
  test('02 — dashboard metrics', async () => {
    // Try clicking a dashboard or metrics nav item
    const clicked = await clickIfVisible(page, '[data-tab="dashboard"], [href*="dashboard"], button:has-text("Dashboard")');
    if (!clicked) await clickIfVisible(page, '[data-tab="metrics"], button:has-text("Metrics")');
    await page.waitForTimeout(1_500);
    // Trigger any health/status API call
    await page.evaluate(() => window.dispatchEvent(new CustomEvent('codex:refresh-metrics')));
    await page.waitForTimeout(1_000);
  });

  // ── 3. Quantum visualizer ─────────────────────────────────────────────────
  test('03 — quantum state visualizer', async () => {
    await clickIfVisible(page, '[data-tab="quantum"], button:has-text("Quantum"), [href*="quantum"]');
    await page.waitForTimeout(2_000);
  });

  // ── 4. Memory management ──────────────────────────────────────────────────
  test('04 — memory management dashboard', async () => {
    await clickIfVisible(page, '[data-tab="memory"], button:has-text("Memory"), [href*="memory"]');
    await page.waitForTimeout(1_500);

    // Trigger memory search
    const searchInput = page.locator('input[placeholder*="search" i], input[placeholder*="query" i]').first();
    if (await searchInput.isVisible({ timeout: 2_000 }).catch(() => false)) {
      await searchInput.fill('fibonacci');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(1_000);
      await searchInput.clear();
    }
  });

  // ── 5. Agent orchestration ────────────────────────────────────────────────
  test('05 — agent orchestration panel', async () => {
    await clickIfVisible(page, '[data-tab="agents"], button:has-text("Agent"), [href*="agent"]');
    await page.waitForTimeout(1_500);
  });

  // ── 6. Code generator ─────────────────────────────────────────────────────
  test('06 — code generator interaction', async () => {
    await clickIfVisible(page, '[data-tab="code"], button:has-text("Code"), [href*="code"]');
    await page.waitForTimeout(1_000);

    const promptInput = page.locator('textarea[placeholder*="prompt" i], input[placeholder*="prompt" i]').first();
    if (await promptInput.isVisible({ timeout: 2_000 }).catch(() => false)) {
      await promptInput.fill('write a fibonacci function in python');
      // Click generate button
      const genBtn = page.locator('button:has-text("Generate"), button[type="submit"]').first();
      if (await genBtn.isVisible({ timeout: 1_000 }).catch(() => false)) {
        await genBtn.click();
        await page.waitForTimeout(3_000); // wait for generated response
      }
      await promptInput.clear();
    }
  });

  // ── 7. CLI terminal (request preview only) ────────────────────────────────
  test('07 — CLI API client panel', async () => {
    await clickIfVisible(page, '[data-tab="cli"], button:has-text("CLI"), [href*="cli"]');
    await page.waitForTimeout(1_000);

    // Trigger a health check preset
    await clickIfVisible(page, 'button:has-text("Brain Health"), button:has-text("Health")');
    await page.waitForTimeout(1_500);
  });

  // ── 8. Pattern library browser ────────────────────────────────────────────
  test('08 — pattern library browser', async () => {
    await clickIfVisible(page, '[data-tab="patterns"], button:has-text("Pattern"), [href*="pattern"]');
    await page.waitForTimeout(1_500);
  });

  // ── 9. GitHub API data (via github-public-api.ts) ─────────────────────────
  test('09 — GitHub public API calls', async () => {
    // Navigate back to main page to trigger GitHub API calls in app init
    await page.goto(BASE, { waitUntil: 'networkidle' });
    await page.waitForTimeout(2_000);
  });

  // ── 10. Full page scroll to trigger lazy-loaded components ────────────────
  test('10 — scroll and idle', async () => {
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(500);
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.waitForLoadState('networkidle', { timeout: 10_000 }).catch(() => {});
    await page.waitForTimeout(1_000);
  });
});
