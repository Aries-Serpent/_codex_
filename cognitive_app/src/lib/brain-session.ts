export const DEFAULT_BRAIN_API_URL = 'http://localhost:8765';

interface SessionState {
  established: boolean;
  generation: number;
  pending: Promise<boolean> | null;
}

const sessionStates = new Map<string, SessionState>();
let pendingBootstrapCapability = consumeBootstrapCapability();

function getSessionState(baseURL: string): SessionState {
  const existing = sessionStates.get(baseURL);
  if (existing) return existing;

  const created: SessionState = {
    established: false,
    generation: 0,
    pending: null,
  };
  sessionStates.set(baseURL, created);
  return created;
}

function consumeBootstrapCapability(): string | null {
  if (typeof window === 'undefined') return null;

  const fragment = new URLSearchParams(window.location.hash.slice(1));
  if (!fragment.has('codex_ui_bootstrap')) return null;

  const capability = fragment.get('codex_ui_bootstrap');
  fragment.delete('codex_ui_bootstrap');
  const remaining = fragment.toString();
  window.history.replaceState(
    window.history.state,
    '',
    `${window.location.pathname}${window.location.search}${remaining ? `#${remaining}` : ''}`,
  );
  return capability || null;
}

function takeBootstrapCapability(): string | null {
  const capability = pendingBootstrapCapability || consumeBootstrapCapability();
  pendingBootstrapCapability = null;
  return capability;
}

export function normalizeBrainAPIURL(baseURL?: string): string {
  const configured = (baseURL?.trim() || DEFAULT_BRAIN_API_URL).replace(/\/+$/, '');
  if (typeof window === 'undefined') return configured;

  try {
    const parsed = new URL(configured);
    const localHosts = new Set(['localhost', '127.0.0.1', '[::1]']);
    if (localHosts.has(parsed.hostname) && localHosts.has(window.location.hostname)) {
      parsed.hostname = window.location.hostname;
    }
    return parsed.toString().replace(/\/+$/, '');
  } catch {
    return configured;
  }
}

export function inferBrainAPIURLFromPage(pageURL: URL): string {
  const preview = pageURL.hostname.match(/^(.*)-(?:3000|5173)\.(.+)$/);
  if (preview) return `https://${preview[1]}-8765.${preview[2]}`;
  return DEFAULT_BRAIN_API_URL;
}

export function getBrainAPIURL(): string {
  const configured = import.meta.env.VITE_CLI_API_URL || import.meta.env.VITE_CODEX_API;
  if (configured) return normalizeBrainAPIURL(configured);
  if (typeof window !== 'undefined') return inferBrainAPIURLFromPage(window.location);
  return DEFAULT_BRAIN_API_URL;
}

export async function ensureBrainSession(baseURL = getBrainAPIURL()): Promise<boolean> {
  const normalized = normalizeBrainAPIURL(baseURL);
  const state = getSessionState(normalized);
  if (state.established) return true;
  if (state.pending) return state.pending;

  const capability = takeBootstrapCapability();
  const headers = new Headers();
  if (capability) headers.set('X-Codex-Bootstrap', capability);

  state.pending = fetch(`${normalized}/api/session`, {
    method: 'POST',
    credentials: 'include',
    headers: capability ? headers : undefined,
  }).then(response => response.ok).catch(() => false).then(established => {
    state.established = established;
    state.pending = null;
    if (established) state.generation += 1;
    return established;
  });

  return state.pending;
}

function invalidateBrainSession(baseURL: string, generation: number): void {
  const state = sessionStates.get(baseURL);
  if (state?.generation === generation) state.established = false;
}

export async function brainSessionFetch(
  path: string,
  init: RequestInit = {},
  baseURL = getBrainAPIURL(),
): Promise<Response> {
  const normalized = normalizeBrainAPIURL(baseURL);
  if (!await ensureBrainSession(normalized)) {
    return new Response(null, { status: 401, statusText: 'Session unavailable' });
  }

  const state = getSessionState(normalized);
  const generation = state.generation;
  const headers = new Headers(init.headers);
  headers.delete('Authorization');
  const request = () => fetch(`${normalized}${path}`, {
    ...init,
    credentials: 'include',
    headers,
  });
  const response = await request();
  if (response.status !== 401) return response;

  invalidateBrainSession(normalized, generation);
  if (!await ensureBrainSession(normalized)) return response;
  return request();
}

export function resetBrainSession(baseURL?: string): void {
  if (baseURL) {
    sessionStates.delete(normalizeBrainAPIURL(baseURL));
    return;
  }
  sessionStates.clear();
}
