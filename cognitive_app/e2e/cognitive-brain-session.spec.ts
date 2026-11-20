import { expect, test, type Page } from '@playwright/test';

const API = process.env.COGNITIVE_BRAIN_API_URL || 'http://localhost:8765';
const API_URL = new URL(API);
const BOOTSTRAPS = (
  process.env.COGNITIVE_BRAIN_UI_BOOTSTRAPS
  || process.env.COGNITIVE_BRAIN_UI_BOOTSTRAP
  || ''
).split(',').filter(Boolean);
const LIVE_E2E_ENABLED = process.env.COGNITIVE_BRAIN_LIVE_E2E === '1' && BOOTSTRAPS.length > 0;
let bootstrapCursor = 0;
const apiPort = API_URL.port || (API_URL.protocol === 'https:' ? '443' : '80');
const LOOPBACK_APIS = [`http://localhost:${apiPort}`, `http://127.0.0.1:${apiPort}`];
const DEFAULT_BROWSER_API = API_URL.hostname === '127.0.0.1'
  ? `http://localhost:${apiPort}`
  : API;
const COOKIE_TARGETS = [...new Set([...LOOPBACK_APIS, API])];
const UI_URL = new URL(process.env.BASE_URL || `http://localhost:${process.env.E2E_PORT || '5173'}/`);

test.use({ trace: 'off' });
test.describe.configure({ mode: 'serial' });
test.skip(
  !LIVE_E2E_ENABLED,
  'Set COGNITIVE_BRAIN_LIVE_E2E=1 and provide UI bootstrap tokens to run live-backend tests.',
);

const protectedRequest = {
  method: 'POST',
  credentials: 'include' as RequestCredentials,
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ command: 'git status --short', timeout: 10 }),
};

async function openWithBootstrap(page: Page, url = '/'): Promise<string | null> {
  const capability = BOOTSTRAPS[bootstrapCursor++] || null;
  if (capability) {
    await page.addInitScript(value => {
      window.history.replaceState(
        window.history.state,
        '',
        `${window.location.pathname}${window.location.search}#codex_ui_bootstrap=${encodeURIComponent(value)}`,
      );
    }, capability);
  }
  await page.goto(url);
  return capability;
}

function fixtureURLFor(api: string): string {
  const url = new URL(UI_URL);
  const target = new URL(api);
  if (LOOPBACK_APIS.includes(target.origin)) url.hostname = target.hostname;
  url.pathname = `${url.pathname.replace(/\/$/, '')}/e2e/fixtures/dependencies.html`;
  return url.toString();
}

test('Cognitive Brain UI proves bootstrap is consumed and cookie access works', async ({ page }) => {
  let sessionRequests = 0;
  let bootstrapObserved = false;
  let browserAuthorizationObserved = false;
  page.on('request', request => {
    const url = new URL(request.url());
    if (url.origin === new URL(DEFAULT_BROWSER_API).origin) {
      const headers = request.headers();
      browserAuthorizationObserved ||= 'authorization' in headers;
      if (request.method() === 'POST' && url.pathname === '/api/session') {
        sessionRequests += 1;
        bootstrapObserved ||= Boolean(capability) &&
          headers['x-codex-bootstrap'] === capability;
      }
    }
  });
  const sessionResponse = page.waitForResponse(response =>
    response.request().method() === 'POST' &&
    response.url() === `${DEFAULT_BROWSER_API.replace(/\/$/, '')}/api/session`
  );

  const capability = await openWithBootstrap(page);
  expect(capability).not.toBeNull();
  expect((await sessionResponse).ok()).toBe(true);
  await expect.poll(() => page.evaluate(() => window.location.hash)).toBe('');
  expect(sessionRequests).toBe(1);
  expect(bootstrapObserved).toBe(Boolean(capability));

  const proof = await page.evaluate(async ({ api, request }) => {
    const reusedSession = await fetch(`${api}/api/session`, {
      method: 'POST',
      credentials: 'include',
    });
    const command = await fetch(`${api}/api/cli/run`, request);
    return {
      reusedStatus: reusedSession.status,
      reusedBody: await reusedSession.json(),
      commandStatus: command.status,
      cookieVisibleToDocument: document.cookie.includes('codex_ui_session'),
    };
  }, { api: DEFAULT_BROWSER_API.replace(/\/$/, ''), request: protectedRequest });

  expect(proof.reusedStatus).toBe(200);
  expect(proof.reusedBody.credential_transport).toBe('httponly_cookie');
  expect(proof.commandStatus).toBe(200);
  expect(proof.cookieVisibleToDocument).toBe(false);
  expect(browserAuthorizationObserved).toBe(false);
});

for (const target of COOKIE_TARGETS) {
  test(`Cognitive Brain UI proves protected cookie access for ${new URL(target).origin}`, async ({ page }) => {
    await openWithBootstrap(page, fixtureURLFor(target));
    const proof = await page.evaluate(async ({ api, request }) => {
      const fragment = new URLSearchParams(window.location.hash.slice(1));
      const capability = fragment.get('codex_ui_bootstrap');
      fragment.delete('codex_ui_bootstrap');
      const remaining = fragment.toString();
      window.history.replaceState(
        window.history.state,
        '',
        `${window.location.pathname}${window.location.search}${remaining ? `#${remaining}` : ''}`,
      );
      const sessionHeaders = new Headers();
      if (capability) sessionHeaders.set('X-Codex-Bootstrap', capability);
      const session = await fetch(`${api}/api/session`, {
        method: 'POST',
        credentials: 'include',
        headers: sessionHeaders,
      });
      const command = await fetch(`${api}/api/cli/run`, request);
      const reusedSession = await fetch(`${api}/api/session`, {
        method: 'POST',
        credentials: 'include',
      });
      return {
        fragmentRemoved: !window.location.hash.includes('codex_ui_bootstrap'),
        sessionStatus: session.status,
        commandStatus: command.status,
        reusedStatus: reusedSession.status,
        cookieVisibleToDocument: document.cookie.includes('codex_ui_session'),
      };
    }, { api: target.replace(/\/$/, ''), request: protectedRequest });

    expect(proof.fragmentRemoved).toBe(true);
    expect(proof.sessionStatus).toBe(200);
    expect(proof.commandStatus).toBe(200);
    expect(proof.reusedStatus).toBe(200);
    expect(proof.cookieVisibleToDocument).toBe(false);
  });
}

test('Cognitive Brain UI cookies are bound to the exact target hostname', async ({ page }) => {
  await openWithBootstrap(page);
  await expect.poll(async () => page.evaluate(async api =>
    (await fetch(`${api}/api/session`, { method: 'POST', credentials: 'include' })).status,
  DEFAULT_BROWSER_API.replace(/\/$/, ''))).toBe(200);

  const mismatchedOrigins = LOOPBACK_APIS
    .filter(origin => origin !== new URL(DEFAULT_BROWSER_API).origin);
  const statuses = await page.evaluate(async ({ api, mismatched, request }) => {
    const matching = await fetch(`${api}/api/cli/run`, request);
    const failures = await Promise.all(mismatched.map(async origin => {
      try {
        return (await fetch(`${origin}/api/cli/run`, request)).status;
      } catch {
        return 0;
      }
    }));
    return { matching: matching.status, mismatched: failures };
  }, {
    api: DEFAULT_BROWSER_API.replace(/\/$/, ''),
    mismatched: [...new Set(mismatchedOrigins)],
    request: protectedRequest,
  });

  expect(statuses.matching).toBe(200);
  expect(statuses.mismatched).not.toEqual([]);
  expect(statuses.mismatched.every(status => status !== 200)).toBe(true);
});
