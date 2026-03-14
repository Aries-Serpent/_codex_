/**
 * har-replay-client.ts
 *
 * Loads a HAR (HTTP Archive) file from `public/har-cache/api-demo.har` and
 * replays recorded responses, enabling the Cognitive App to work fully in:
 *   - GitHub Pages (no backend)
 *   - Codespace offline mode
 *   - Documentation demos
 *   - CI snapshot tests
 *
 * Priority order:
 *   1. Real backend at VITE_API_BASE_URL (if reachable)
 *   2. HAR replay   (if VITE_HAR_REPLAY=true OR backend unreachable)
 *   3. Mock client  (built-in fallback, no network required)
 *
 * HAR files are stored in Git LFS:
 *   cognitive_app/public/har-cache/api-demo.har
 *
 * To record a new HAR:
 *   1. Start the backend: `docker compose up api`
 *   2. Open DevTools → Network → Export HAR
 *   3. Save to cognitive_app/public/har-cache/api-demo.har
 *   4. Commit (LFS handles the large file automatically)
 */

export interface HAREntry {
  request: {
    method: string;
    url: string;
    postData?: { text: string };
  };
  response: {
    status: number;
    headers: Array<{ name: string; value: string }>;
    content: {
      mimeType: string;
      text: string;
    };
  };
  time: number; // recorded response time in ms
}

export interface HARLog {
  version: string;
  entries: HAREntry[];
}

export interface HAR {
  log: HARLog;
}

// ---------------------------------------------------------------------------
// HAR loader (cached singleton)
// ---------------------------------------------------------------------------

let _harCache: HAR | null = null;
let _harLoadAttempted = false;

export async function loadHAR(harPath?: string): Promise<HAR | null> {
  if (_harLoadAttempted) return _harCache;
  _harLoadAttempted = true;

  const base = import.meta.env.BASE_URL ?? '/';
  const path = harPath ?? `${base}har-cache/api-demo.har`;

  try {
    const res = await fetch(path);
    if (!res.ok) return null;
    _harCache = (await res.json()) as HAR;
    console.info(`[HAR] Loaded ${_harCache.log.entries.length} recorded entries from ${path}`);
    return _harCache;
  } catch {
    console.warn('[HAR] No HAR cache available — falling back to mock client');
    return null;
  }
}

// ---------------------------------------------------------------------------
// URL normalisation (strips origin + query params for matching)
// ---------------------------------------------------------------------------

function normalisePath(url: string): string {
  try {
    const u = new URL(url, 'http://localhost');
    return u.pathname;
  } catch {
    return url.split('?')[0];
  }
}

// ---------------------------------------------------------------------------
// HAR replay fetch — drop-in replacement for window.fetch
// ---------------------------------------------------------------------------

export async function harFetch(
  input: string | URL | Request,
  init?: RequestInit,
): Promise<Response> {
  const url   = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url;
  const method = (init?.method ?? (input instanceof Request ? input.method : 'GET')).toUpperCase();

  const har = await loadHAR();
  if (!har) throw new Error('HAR not loaded');

  const targetPath = normalisePath(url);

  // Find best matching entry (method + path)
  const entry = har.log.entries.find(e =>
    e.request.method.toUpperCase() === method &&
    normalisePath(e.request.url) === targetPath,
  ) ?? har.log.entries.find(e =>
    // Fallback: path-only match ignoring method
    normalisePath(e.request.url) === targetPath,
  );

  if (!entry) {
    throw new Error(`[HAR] No recorded entry for ${method} ${targetPath}`);
  }

  // Simulate realistic latency (capped at 2s)
  const delay = Math.min(entry.time, 2000);
  await new Promise(r => setTimeout(r, delay));

  const headers = new Headers(
    Object.fromEntries(entry.response.headers.map(h => [h.name, h.value])),
  );

  return new Response(entry.response.content.text, {
    status:  entry.response.status,
    headers,
  });
}

// ---------------------------------------------------------------------------
// Auto-detect mode and export the right fetch
// ---------------------------------------------------------------------------

export type FetchMode = 'live' | 'har' | 'mock';

export async function detectMode(apiBaseUrl: string): Promise<FetchMode> {
  // Explicit override
  if (import.meta.env.VITE_HAR_REPLAY === 'true') return 'har';

  // Try live backend with 2s timeout
  try {
    const ctrl = new AbortController();
    const tid = setTimeout(() => ctrl.abort(), 2000);
    const res = await fetch(`${apiBaseUrl}/health`, { signal: ctrl.signal });
    clearTimeout(tid);
    if (res.ok) return 'live';
  } catch {
    // unreachable
  }

  // Try loading HAR
  const har = await loadHAR();
  return har ? 'har' : 'mock';
}
