import { beforeEach, describe, expect, it, vi } from 'vitest';
import {
  getBrainAPIURL,
  inferBrainAPIURLFromPage,
  resetBrainSession,
} from '@/lib/brain-session';
import { CodexAPIClient } from '@/lib/codex-api-client';

describe('browser Cognitive Brain session transport', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
    vi.unstubAllEnvs();
    window.history.replaceState(null, '', '/');
    resetBrainSession();
  });

  it('deduplicates bootstrap and retries a protected request once after rebootstrap', async () => {
    window.history.replaceState(null, '', '/#codex_ui_bootstrap=one-time-capability');
    const fetchMock = vi.spyOn(globalThis, 'fetch')
      .mockImplementation(async (input) => {
        const url = String(input);
        if (url.endsWith('/api/session')) {
          return new Response(null, { status: 204 });
        }
        const statusCalls = fetchMock.mock.calls.filter(([request]) => String(request).endsWith('/status'));
        return new Response(
          JSON.stringify(statusCalls.length === 1
            ? { message: 'expired' }
            : { healthy: true, metrics: {} }),
          {
            status: statusCalls.length === 1 ? 401 : 200,
            headers: { 'Content-Type': 'application/json' },
          },
        );
      });
    const client = new CodexAPIClient('http://localhost:8765');

    await Promise.all([client.getStatus(), client.getStatus()]);

    expect(window.location.hash).toBe('');
    const bootstrapCalls = fetchMock.mock.calls.filter(([url]) => String(url).endsWith('/api/session'));
    expect(bootstrapCalls).toHaveLength(2);
    expect(new Headers(bootstrapCalls[0]?.[1]?.headers).get('X-Codex-Bootstrap')).toBe('one-time-capability');
    expect(new Headers(bootstrapCalls[1]?.[1]?.headers).has('X-Codex-Bootstrap')).toBe(false);
    expect(fetchMock.mock.calls.filter(([url]) => String(url).endsWith('/status'))).toHaveLength(3);
    expect(fetchMock.mock.calls.every(([, init]) => !new Headers(init?.headers).has('Authorization'))).toBe(true);
  });

  it('reuses a cookie session without a bootstrap capability', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(new Response(null, { status: 204 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ healthy: true, metrics: {} }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }));

    await expect(new CodexAPIClient().getStatus()).resolves.toEqual({ healthy: true, metrics: {} });

    expect(new Headers(fetchMock.mock.calls[0]?.[1]?.headers).has('X-Codex-Bootstrap')).toBe(false);
    expect(new Headers(fetchMock.mock.calls[1]?.[1]?.headers).has('Authorization')).toBe(false);
  });

  it('uses the configured code-generation API only for inference, not Brain sessions', () => {
    vi.stubEnv('VITE_CLI_API_URL', '');
    vi.stubEnv('VITE_CODEX_API', 'https://inference.example.invalid');

    expect(getBrainAPIURL()).toBe('http://localhost:8765');
  });

  it('normalizes an inferred Brain URL to the page hostname', () => {
    vi.stubEnv('VITE_CLI_API_URL', '');
    vi.stubEnv('VITE_CODEX_API', '');
    vi.stubGlobal('window', { location: new URL('http://127.0.0.1:5173/') });

    expect(getBrainAPIURL()).toBe('http://127.0.0.1:8765');
  });

  it('uses a credential-free transport for the separately configured inference API', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(
      JSON.stringify({ healthy: true, metrics: {} }),
      { status: 200, headers: { 'Content-Type': 'application/json' } },
    ));
    const client = new CodexAPIClient('https://inference.example.invalid', false);

    await expect(client.getStatus()).resolves.toEqual({ healthy: true, metrics: {} });

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock).toHaveBeenCalledWith(
      'https://inference.example.invalid/status',
      expect.objectContaining({ credentials: 'omit' }),
    );
    expect(new Headers(fetchMock.mock.calls[0]?.[1]?.headers).has('Authorization')).toBe(false);
  });

  it('distinguishes session transport failures from HTTP authorization denials', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch')
      .mockRejectedValueOnce(new TypeError('offline'))
      .mockResolvedValueOnce(new Response(null, { status: 403 }));
    const client = new CodexAPIClient('http://localhost:8765');

    await expect(client.getStatus()).rejects.toBeInstanceOf(TypeError);
    await expect(client.getStatus()).rejects.toMatchObject({ statusCode: 403 });

    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it('derives a sibling Codespaces API origin without embedding a name', () => {
    expect(
      inferBrainAPIURLFromPage(new URL('https://generated-name-5173.preview.app.github.dev/')),
    ).toBe('https://generated-name-8765.preview.app.github.dev');
  });

  it('defaults to localhost and normalizes configured forwarded origins', () => {
    vi.stubEnv('VITE_CLI_API_URL', '');
    vi.stubEnv('VITE_CODEX_API', '');
    expect(getBrainAPIURL()).toBe('http://localhost:8765');

    vi.stubEnv('VITE_CLI_API_URL', 'https://forwarded.example.invalid/brain/');
    expect(getBrainAPIURL()).toBe('https://forwarded.example.invalid/brain');
  });
});
