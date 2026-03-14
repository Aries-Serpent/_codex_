/**
 * api-mode-selector.ts
 *
 * Detects the best available API mode and returns a configured client.
 *
 * Priority chain
 * ──────────────
 * 1. **Live CLI server** (localhost:8765 or VITE_CLI_API_URL)
 *    Full cognitive brain — memory, OODA, agent orchestration.
 *    Auth: VITE_CODEX_KEY bearer token (matches CODEX_MASTER_KEY on server).
 *    Available in: Codespace, local dev, Docker Compose.
 *
 * 2. **GitHub Public API** (api.github.com — no auth needed, repo is public)
 *    Real live data: workflow runs, repo stats, releases, branch status.
 *    Rate limit: 60 req/hr unauthenticated | 5,000/hr with VITE_GITHUB_TOKEN.
 *    Available in: GitHub Pages, any browser, CI.
 *
 * 3. **HAR replay** (cognitive_app/public/har-cache/api-demo.har)
 *    Recorded brain API responses served offline.
 *    Stored in Git LFS — auto-downloaded in Codespace/CI.
 *    Available in: GitHub Pages offline, documentation demos.
 *
 * 4. **Mock client** (built-in, zero network)
 *    Deterministic fake data — always works.
 *    Available in: unit tests, isolated dev, no-network environments.
 *
 * Usage
 * ─────
 * import { selectAPIMode, APIMode } from '@/lib/api-mode-selector';
 * const { mode, client } = await selectAPIMode();
 */

import { CodexAPIClient }    from './codex-api-client';
import { MockCodexAPIClient } from './mock-api-client';
import { loadHAR, harFetch }  from './har-replay-client';
import * as GitHubAPI          from './github-public-api';

export type APIMode = 'live' | 'github' | 'har' | 'mock';

export interface SelectedAPI {
  mode:          APIMode;
  /** Cognitive brain client (memory / agents / quantum state) */
  brainClient:   CodexAPIClient | MockCodexAPIClient;
  /** Live GitHub repo data — always available (public repo) */
  githubAPI:     typeof GitHubAPI;
  /** Human-readable description for status indicators */
  label:         string;
  /** true when brain-specific calls go to a real server */
  brainIsLive:   boolean;
}

const CLI_URL  = (import.meta.env.VITE_CLI_API_URL  as string | undefined) ?? 'http://localhost:8765';
const CODEX_KEY = (import.meta.env.VITE_CODEX_KEY   as string | undefined) ?? '';

let _cached: SelectedAPI | null = null;

async function probeLiveServer(): Promise<boolean> {
  try {
    const ctrl = new AbortController();
    const tid  = setTimeout(() => ctrl.abort(), 2500);
    const res  = await fetch(`${CLI_URL}/api/health`, {
      signal:  ctrl.signal,
      headers: CODEX_KEY ? { Authorization: `Bearer ${CODEX_KEY}` } : {},
    });
    clearTimeout(tid);
    return res.ok;
  } catch {
    return false;
  }
}

export async function selectAPIMode(force?: APIMode): Promise<SelectedAPI> {
  if (_cached && !force) return _cached;

  // ── 1. Explicit override (e.g. VITE_API_MODE=mock for tests) ──────────────
  const envMode = (import.meta.env.VITE_API_MODE as string | undefined) as APIMode | undefined;
  const targetMode: APIMode | undefined = force ?? envMode;

  // ── 2. Live server probe ───────────────────────────────────────────────────
  const liveOK = (targetMode === 'live' || !targetMode)
    ? await probeLiveServer()
    : false;

  let mode: APIMode;
  if      (targetMode === 'mock')             mode = 'mock';
  else if (targetMode === 'har')              mode = 'har';
  else if (targetMode === 'github')           mode = 'github';
  else if (liveOK)                            mode = 'live';
  else {
    // Auto-detect: try HAR, then fall back to github data + mock brain
    const har = await loadHAR();
    mode = har ? 'har' : 'github';
  }

  // ── 3. Build clients ───────────────────────────────────────────────────────
  let brainClient: CodexAPIClient | MockCodexAPIClient;
  let label: string;
  let brainIsLive = false;

  switch (mode) {
    case 'live':
      brainClient = new CodexAPIClient(CLI_URL, CODEX_KEY);
      label       = `🟢 Live — ${CLI_URL}`;
      brainIsLive = true;
      break;

    case 'har': {
      // Wrap HAR fetch into the mock client shape
      const harClient = new MockCodexAPIClient();
      // @ts-expect-error — monkey-patch fetch for HAR mode
      (harClient as Record<string, unknown>)._fetch = harFetch;
      brainClient = harClient;
      label       = '📼 HAR replay (demo cache)';
      break;
    }

    case 'github':
      // No real brain server — use mock for brain-specific calls
      brainClient = new MockCodexAPIClient();
      label       = '🌐 GitHub API (public) + mock brain';
      break;

    default: // 'mock'
      brainClient = new MockCodexAPIClient();
      label       = '🤖 Mock (offline)';
      break;
  }

  _cached = {
    mode,
    brainClient,
    githubAPI:   GitHubAPI,
    label,
    brainIsLive,
  };

  console.info(`[API] Mode selected: ${mode} — ${label}`);
  return _cached;
}

/** Reset cached selection (useful in tests or on reconnect) */
export function resetAPIMode(): void { _cached = null; }
