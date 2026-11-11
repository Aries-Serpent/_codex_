import { test as base, expect, type Page } from '@playwright/test';
import { dashboardAPI, syntheticKey, variants, type Variant } from './lazy-init/variants';

const code = 'def synthetic_function():\n    return "browser fixture"\n';
const expectedAuthorization = ['Bearer', syntheticKey].join(' ');
const response = {
  code,
  metadata: { k1_factor: 0.32, coherence: 0.8, cache_hit: false, processing_time_ms: 50 },
  quantum_metrics: { superposition_states: 3, entanglement_score: 0.9 },
};
const dashboardResponses: Record<string, unknown> = {
  '/api/cognitive/state': {
    k1_factor: 0.32, accuracy: 0.9, coherence: 0.8, quantum_advantage: 2.86, superposition_states: [],
  },
  '/api/agents/state': { agents: [], tasks: [] },
  '/api/memory/state': {
    stm_count: 0, ltm_count: 0, capacity: 100, cache_hit_rate: 0.5,
    compression_rate: 0.5, patterns: [],
  },
};

type Call = { url: string; method: string; body: unknown; authorization: string | undefined };
type Harness = {
  open: (variant?: Variant, cascade?: boolean) => Promise<void>;
  calls: Call[];
  inferStatus: number;
  statusCode: number;
  cacheHit: boolean;
  malformedResponse: boolean;
  hasKey: () => boolean;
  holdStatus: () => void;
  releaseStatus: () => void;
};

const test = base.extend<{ harness: Harness }>({
  harness: async ({ page, context }, runFixture, testInfo) => {
    const urls = testInfo.config.metadata.lazyURLs as Record<Variant, string> | undefined;
    if (!urls) throw new Error('Use --config e2e/lazy-init.playwright.config.ts for real build-time variants');
    let active: Variant = 'default';
    let statusGate: Promise<void> | undefined;
    let release = () => {};
    const unexpected: string[] = [];
    const pageErrors: string[] = [];
    page.on('pageerror', error => pageErrors.push(error.message));
    const harness: Harness = {
      calls: [], inferStatus: 200, statusCode: 200, cacheHit: false, malformedResponse: false,
      hasKey: () => Boolean(variants[active].key),
      holdStatus() { statusGate = new Promise<void>(resolve => { release = resolve; }); },
      releaseStatus() { release(); statusGate = undefined; },
      async open(variant = 'default', cascade = false) {
        active = variant;
        await page.goto(new URL(cascade ? 'e2e/lazy-init/cascade.html' : '', urls[variant]).href);
        await expect(page.locator('meta[name="lazy-init-variant"]')).toHaveAttribute('content', variant);
        if (!cascade) {
          await expect(page.getByRole('tab', { name: 'Code', exact: true })).toBeVisible();
          await page.getByRole('tab', { name: 'Code', exact: true }).click();
          await expect(page.getByRole('heading', { name: 'Code Generation', exact: true })).toBeVisible();
        }
      },
    };
    // Cross-engine clipboard boundary: assert the bytes handed to writeText, not an OS permission prompt.
    await page.addInitScript(() => {
      const writes: string[] = [];
      Object.defineProperty(window, '__lazyClipboard', { value: writes });
      Object.defineProperty(navigator, 'clipboard', {
        configurable: true, value: { writeText: async (text: string) => { writes.push(text); } },
      });
    });
    await context.route('**/*', async route => {
      const request = route.request();
      const url = new URL(request.url());
      const api = variants[active].api || 'http://localhost:8000';
      if (request.method() === 'GET' && url.href === 'https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap') {
        await route.fulfill({ contentType: 'text/css', body: '/* Offline synthetic fonts: use system fallback. */' });
      } else if (request.method() === 'POST' && url.href === new URL('/_spark/loaded', urls[active]).href) {
        await route.fulfill({ status: 204 });
      } else if (request.method() === 'GET' && url.origin === dashboardAPI &&
          Object.hasOwn(dashboardResponses, url.pathname) && !url.search) {
        await route.fulfill({ json: dashboardResponses[url.pathname] });
      } else if (url.href === `${api}/status` || url.href === `${api}/infer`) {
        harness.calls.push({
          url: url.href, method: request.method(),
          body: request.method() === 'POST' ? request.postDataJSON() : null,
          authorization: request.headers().authorization,
        });
        if (url.href === `${api}/status`) {
          expect(request.method()).toBe('GET');
          await statusGate;
          await route.fulfill({
            status: harness.statusCode,
            json: harness.statusCode === 200 ? { healthy: true, metrics: {} } : { message: 'Synthetic unavailable status' },
          });
        } else {
          expect(request.method()).toBe('POST');
          expect(request.headers()['content-type']).toBe('application/json');
          await route.fulfill({
            status: harness.inferStatus,
            json: harness.inferStatus === 200
              ? harness.malformedResponse
                ? { code: 'untrusted malformed response' }
                : { ...response, metadata: { ...response.metadata, cache_hit: harness.cacheHit } }
              : { message: `Synthetic infer ${harness.inferStatus}` },
          });
        }
      } else if (url.origin === new URL(urls[active]).origin &&
                 request.method() === 'GET' && !['fetch', 'xhr'].includes(request.resourceType()) &&
                 !/^\/(?:_spark|api)\//.test(url.pathname)) {
        await route.continue();
      } else {
        unexpected.push(`${request.method()} ${url.href}`);
        await route.abort('blockedbyclient');
      }
    });
    try {
      await runFixture(harness);
    } finally {
      harness.releaseStatus();
      await testInfo.attach('harness-evidence.json', {
        body: JSON.stringify({ variant: active, calls: harness.calls, unexpected, pageErrors }),
        contentType: 'application/json',
      });
      expect.soft(unexpected, 'No unmocked external/backend traffic').toEqual([]);
      expect.soft(pageErrors, 'No uncaught browser errors').toEqual([]);
    }
  },
});

const prompt = (page: Page) => page.getByRole('textbox', { name: 'Describe the code you want to generate' });
const generateButton = (page: Page) => page.getByRole('button', { name: 'Generate Code', exact: true });
const status = (page: Page) => page.getByText('Status:', { exact: true }).locator('..');
const inferCalls = (harness: Harness) => harness.calls.filter(call => call.url.endsWith('/infer'));
const statusCalls = (harness: Harness) => harness.calls.filter(call => call.url.endsWith('/status'));

async function connected(page: Page) {
  await expect(status(page)).toHaveText('Status:Connected');
  await expect(status(page).locator('div.rounded-full')).toHaveClass(/bg-green-500/);
}

async function generate(page: Page, harness: Harness, text = 'Create a synthetic Python function') {
  await connected(page);
  const previousCalls = inferCalls(harness).length;
  await prompt(page).fill(text);
  await expect(generateButton(page)).toBeEnabled();
  await generateButton(page).click();
  await expect(page.getByRole('heading', { name: 'Generated Code', exact: true })).toBeVisible();
  await expect(generateButton(page)).toBeEnabled();
  if (harness.hasKey()) {
    await expect.poll(() => inferCalls(harness).length).toBe(previousCalls + 1);
    expect(inferCalls(harness).at(-1)).toMatchObject({
      method: 'POST', authorization: expectedAuthorization,
      body: { prompt: text, context: { language: 'python', tier: 'B' } },
    });
  }
}

async function demoResult(page: Page) {
  await expect(page.locator('pre code')).toContainText('Generated using quantum-enhanced cognitive brain');
  await expect(page.getByText('Code generated successfully', { exact: true })).toBeVisible();
  await expect(page.getByText(/Generated with Demo Mode • k₁ factor:/)).toBeVisible();
}

test('L01 missing key explains demo mode without configuration errors', async ({ page, harness }) => {
  await harness.open('noKey');
  await connected(page);
  await expect(page.getByText('Using demo mode (API key not configured)', { exact: true })).toBeVisible();
  await expect(page.getByText('Missing VITE_CODEX_KEY environment variable', { exact: true })).toHaveCount(0);
  expect(harness.calls).toEqual([]);
});

test('L02 missing key uses green demo-connected status, not red error', async ({ page, harness }) => {
  await harness.open('noKey');
  await connected(page);
  await expect(status(page).getByText('Error', { exact: true })).toHaveCount(0);
  expect(statusCalls(harness)).toEqual([]);
});

test('L03 missing key gates empty prompts, but enables valid demo generation', async ({ page, harness }) => {
  await harness.open('noKey');
  await connected(page);
  await expect(generateButton(page)).toBeDisabled();
  await expect(page.getByRole('heading', { name: 'Generated Code', exact: true })).toHaveCount(0);
  await generate(page, harness);
  await demoResult(page);
  expect(harness.calls).toEqual([]);
});

test('L04 missing key preserves prompt entry and counts without live submission', async ({ page, harness }) => {
  await harness.open('noKey');
  await connected(page);
  const text = 'Create a test function';
  await prompt(page).fill(text);
  await expect(page.getByText(`${text.length} / 5000`, { exact: true })).toBeVisible();
  await expect(generateButton(page)).toBeEnabled();
  expect(harness.calls).toEqual([]);
});

test('L05 held status request exposes yellow Checking state', async ({ page, harness }) => {
  harness.holdStatus();
  await harness.open();
  await expect.poll(() => statusCalls(harness).length).toBe(1);
  await expect(status(page)).toHaveText('Status:Checking...');
  await expect(status(page).locator('div.rounded-full')).toHaveClass(/bg-yellow-500/);
  harness.releaseStatus();
  await connected(page);
});

test('L06 valid keyed status transitions exactly to Connected', async ({ page, harness }) => {
  await harness.open();
  await connected(page);
  expect(statusCalls(harness)).toEqual([{
    url: 'http://localhost:8000/status', method: 'GET', body: null, authorization: expectedAuthorization,
  }]);
  await expect(page.getByText(/using demo mode/i)).toHaveCount(0);
});

test('L07 initialization enables generation only with a valid prompt', async ({ page, harness }) => {
  await harness.open();
  await connected(page);
  await expect(generateButton(page)).toBeDisabled();
  await prompt(page).fill('Generate a valid function');
  await expect(generateButton(page)).toBeEnabled();
});

test('L08 status timer rechecks at 30000ms and cleans up on unmount', async ({ page, harness }) => {
  const now = new Date('2030-01-01T00:00:00Z');
  await page.clock.install({ time: now });
  await page.clock.pauseAt(now);
  await harness.open();
  await connected(page);
  expect(statusCalls(harness)).toHaveLength(1);
  await page.clock.runFor(29_999);
  expect(statusCalls(harness)).toHaveLength(1);
  await page.clock.runFor(1);
  await expect.poll(() => statusCalls(harness).length).toBe(2);
  await connected(page);
  await page.getByRole('tab', { name: 'Demo', exact: true }).click();
  await page.clock.runFor(60_000);
  expect(statusCalls(harness)).toHaveLength(2);
});

test('L09 keyed prompt entry has accurate count and no invalid styling', async ({ page, harness }) => {
  await harness.open();
  const text = 'Create a FastAPI endpoint for user authentication';
  await prompt(page).fill(text);
  await expect(page.getByText(`${text.length} / 5000`, { exact: true })).toBeVisible();
  await expect(prompt(page)).toHaveAttribute('aria-invalid', 'false');
  await expect(prompt(page)).not.toHaveClass(/(^|\s)border-destructive(\s|$)/);
});

test('L10 short-to-valid prompt removes validation styling at ten characters', async ({ page, harness }) => {
  await harness.open();
  await connected(page);
  await prompt(page).fill('Short');
  await expect(prompt(page)).toHaveClass(/(^|\s)border-destructive(\s|$)/);
  await expect(generateButton(page)).toBeDisabled();
  await expect(page.getByText('5 / 5000 (min: 10)', { exact: true })).toBeVisible();
  await prompt(page).fill('1234567890');
  await expect(prompt(page)).not.toHaveClass(/(^|\s)border-destructive(\s|$)/);
  await expect(generateButton(page)).toBeEnabled();
});

test('L11 progressive counts and minimum warning follow actual string lengths', async ({ page, harness }) => {
  await harness.open();
  for (const text of ['Test', 'Testing more']) {
    await prompt(page).fill(text);
    await expect(page.getByText(`${text.length} / 5000${text.length < 10 ? ' (min: 10)' : ''}`, { exact: true })).toBeVisible();
  }
  await expect(page.getByText('(min: 10)', { exact: false })).toHaveCount(0);
});

test('L12 401 infer failure produces visible synthetic fallback code', async ({ page, harness }) => {
  harness.inferStatus = 401;
  await harness.open();
  await generate(page, harness);
  expect(inferCalls(harness)).toHaveLength(1);
  await demoResult(page);
  await expect(page.getByText('Primary API failed: Synthetic infer 401. Falling back to demo mode.')).toBeVisible();
});

test('L13 500 infer failure identifies Demo Mode and k1 in toast description', async ({ page, harness }) => {
  harness.inferStatus = 500;
  await harness.open();
  await generate(page, harness);
  await demoResult(page);
  await expect(page.getByText('Generation failed', { exact: true })).toBeVisible();
  expect(inferCalls(harness)).toHaveLength(1);
});

test('L14 fallback generation exposes Copy and Download controls', async ({ page, harness }) => {
  harness.inferStatus = 500;
  await harness.open();
  await generate(page, harness);
  await demoResult(page);
  await expect(page.getByRole('button', { name: 'Copy', exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Download', exact: true })).toBeVisible();
});

test('L15 schema-valid cache responses control Cache Hit badge in both directions', async ({ page, harness }) => {
  harness.cacheHit = true;
  await harness.open();
  await generate(page, harness);
  await expect(page.locator('pre code')).toHaveText(code);
  await expect(page.getByText('Cache Hit', { exact: true })).toBeVisible();
  harness.cacheHit = false;
  await generate(page, harness, 'Generate a different synthetic function');
  await expect(page.getByText('Cache Hit', { exact: true })).toHaveCount(0);
  expect(inferCalls(harness)).toHaveLength(2);
});

async function checkCascade(page: Page, harness: Harness, variant: Variant) {
  await harness.open(variant, true);
  const start = new Date('2030-01-01T00:00:00Z');
  await page.clock.install({ time: start });
  await page.clock.pauseAt(start);
  await page.getByRole('button', { name: 'Start Cascade', exact: true }).click();
  const completed = page.getByRole('status', { name: 'Completed at' });
  await expect(completed).toHaveText('pending');
  await expect(page.getByText('50%', { exact: true })).toBeVisible();
  await page.clock.runFor(variants[variant].stageMs - 1);
  await expect(page.getByText('50%', { exact: true })).toBeVisible();
  await page.clock.runFor(1);
  await expect(page.getByText('100%', { exact: true })).toBeVisible();
  await page.clock.runFor(variants[variant].stageMs - 1);
  await expect(completed).toHaveText('pending');
  await page.clock.runFor(1);
  await expect(completed).toHaveText(String(start.getTime() + 2 * variants[variant].stageMs));
  await expect(page.getByText('1/1', { exact: true })).toBeVisible();
}

test('L16 default cascade executes two actual 800ms stages', async ({ page, harness }) => {
  await checkCascade(page, harness, 'default');
});
test('L17 fast build executes two actual 200ms stages', async ({ page, harness }) => {
  await checkCascade(page, harness, 'fast');
});
test('L18 slow build executes two actual 2000ms stages', async ({ page, harness }) => {
  await checkCascade(page, harness, 'slow');
});
test('L19 every invalid timing build executes fallback 800ms stages', async ({ page, harness }) => {
  test.setTimeout(120_000);
  for (const variant of ['zero', 'negative', 'excessive', 'invalid', 'nan'] as const) {
    await test.step(variant, async () => {
      await checkCascade(page, harness, variant);
    });
  }
});

test('L20 API URL builds send status and infer to the exact configured endpoint', async ({ page, harness }) => {
  test.setTimeout(120_000);
  for (const variant of ['default', 'fast', 'slow', 'customAPI'] as const) {
    await test.step(variant, async () => {
      harness.calls.length = 0;
      await harness.open(variant);
      await generate(page, harness);
      const api = variants[variant].api || 'http://localhost:8000';
      expect(harness.calls.map(call => call.url)).toEqual([`${api}/status`, `${api}/infer`]);
      await expect(page.locator('pre code')).toHaveText(code);
      await expect(page.getByText(/Generated with Codex API • k₁ factor:/)).toBeVisible();
    });
  }
});

test('L21 generate then copy writes the exact displayed code bytes', async ({ page, harness }) => {
  await harness.open();
  await generate(page, harness);
  await page.getByRole('button', { name: 'Copy', exact: true }).click();
  await expect(page.getByText('Code copied to clipboard', { exact: true })).toBeVisible();
  expect(await page.evaluate(() => (window as unknown as { __lazyClipboard: string[] }).__lazyClipboard)).toEqual([code]);
});

test('L22 download has Python filename and exact generated content', async ({ page, harness }) => {
  await harness.open();
  await generate(page, harness);
  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Download', exact: true }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toBe('generated_code.py');
  const stream = await download.createReadStream();
  const chunks: Buffer[] = [];
  for await (const chunk of stream) chunks.push(Buffer.from(chunk));
  expect(Buffer.concat(chunks).toString('utf8')).toBe(code);
  await expect(page.getByText('Code downloaded', { exact: true })).toBeVisible();
});

test('L23 correcting a too-short prompt recovers through successful generation', async ({ page, harness }) => {
  await harness.open();
  await connected(page);
  await prompt(page).fill('Test');
  await expect(generateButton(page)).toBeDisabled();
  expect(inferCalls(harness)).toEqual([]);
  await generate(page, harness, 'Create a comprehensive test suite');
  await expect(page.locator('pre code')).toHaveText(code);
  expect(inferCalls(harness)).toHaveLength(1);
});

test('L24 controls expose real accessible names, roles and invalid state', async ({ page, harness }) => {
  await harness.open();
  await expect(prompt(page)).toBeVisible();
  await expect(generateButton(page)).toBeVisible();
  await expect(page.getByRole('switch', { name: 'Toggle AI Mode' })).not.toBeChecked();
  await prompt(page).fill('short');
  await expect(prompt(page)).toHaveAttribute('aria-invalid', 'true');
});

test('L25 keyboard Tab moves from prompt to Generate and Enter submits once', async ({ page, harness }) => {
  await harness.open();
  await connected(page);
  await prompt(page).focus();
  await expect(prompt(page)).toBeFocused();
  await page.keyboard.type('Generate a synthetic test function');
  await page.keyboard.press('Tab');
  await expect(generateButton(page)).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page.locator('pre code')).toHaveText(code);
  expect(inferCalls(harness)).toHaveLength(1);
});

test('429 infer rejection stays an error and never fabricates demo success', async ({ page, harness }) => {
  harness.inferStatus = 429;
  await harness.open();
  await connected(page);
  await prompt(page).fill('Create a rate limited function');
  await generateButton(page).click();
  await expect(page.getByText('Generation failed', { exact: true })).toBeVisible();
  await expect(page.getByText('Synthetic infer 429', { exact: true })).toHaveCount(2);
  await expect(generateButton(page)).toBeEnabled();
  await expect(page.getByRole('heading', { name: 'Generated Code', exact: true })).toHaveCount(0);
  await expect(page.getByText(/Generated with Demo Mode/)).toHaveCount(0);
  expect(inferCalls(harness)).toHaveLength(1);
});

test('prompt maximum accepts 5000 and rejects 5001 without an infer request', async ({ page, harness }) => {
  await harness.open();
  await connected(page);
  await prompt(page).fill('x'.repeat(5001));
  await expect(page.getByText('5001 / 5000', { exact: true })).toBeVisible();
  await expect(prompt(page)).toHaveAttribute('aria-invalid', 'true');
  await expect(generateButton(page)).toBeDisabled();
  expect(inferCalls(harness)).toEqual([]);
  await generate(page, harness, 'x'.repeat(5000));
  await expect(page.locator('pre code')).toHaveText(code);
  expect(inferCalls(harness)).toHaveLength(1);
});

test('failed keyed status explicitly connects in demo mode', async ({ page, harness }) => {
  harness.statusCode = 503;
  await harness.open();
  await connected(page);
  await expect(page.getByText('API connection failed, using demo mode', { exact: true })).toBeVisible();
  expect(statusCalls(harness)).toHaveLength(1);
});

test('malformed successful infer response is rejected before explicit demo fallback', async ({ page, harness }) => {
  harness.malformedResponse = true;
  await harness.open();
  await generate(page, harness);
  expect(inferCalls(harness)).toHaveLength(1);
  await demoResult(page);
  await expect(page.getByText('Generation failed', { exact: true })).toBeVisible();
  await expect(page.getByText(/Primary API failed:/)).toBeVisible();
  await expect(page.locator('pre code')).not.toContainText('untrusted malformed response');
  await expect(page.getByText(/Generated with Codex API/)).toHaveCount(0);
});
