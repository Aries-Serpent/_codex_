import { afterEach, describe, expect, it, vi } from 'vitest';

const defaultConfigPath = '../../../playwright.config';

afterEach(() => {
  vi.unstubAllEnvs();
  vi.resetModules();
});

async function defaultConfig(baseURL = '') {
  vi.stubEnv('BASE_URL', baseURL);
  vi.stubEnv('E2E_PORT', '5173');
  return (await import(defaultConfigPath)).default;
}

describe('Playwright suite boundaries', () => {
  it('owns a loopback development server by default', async () => {
    const config = await defaultConfig();
    expect(config.webServer).toMatchObject({
      url: 'http://127.0.0.1:5173/',
      reuseExistingServer: false,
    });
  });

  it.each([
    'https://aries-serpent.github.io/_codex_/cognitive_app/',
    'http://localhost:5173/',
    'http://127.0.0.1:5510/',
  ])('uses the supplied server without launching a fixture: %s', async baseURL => {
    const config = await defaultConfig(baseURL);
    expect(config.use?.baseURL).toBe(baseURL);
    expect(config.webServer).toBeUndefined();
  });

  it.each(['file:///tmp/site', `https://${'synthetic-user'}@example.invalid/`])(
    'rejects unsafe target URLs: %s',
    async baseURL => {
      await expect(defaultConfig(baseURL)).rejects.toThrow('HTTP(S) URL without credentials');
    },
  );

  it.each(['', '1'])('serves through the proxy-free e2e config (E2E_PRODUCTION=%s)', async mode => {
    vi.stubEnv('E2E_PRODUCTION', mode);
    const config = await defaultConfig();
    expect(config.webServer.command).toContain('--config e2e/vite.config.ts');
  });

  it.each([
    ['1', 'true', 'http://127.0.0.1:5173/_codex_/cognitive_app/'],
    ['1', '', 'http://127.0.0.1:5173/'],
    ['', 'true', 'http://127.0.0.1:5173/'],
  ])(
    'targets the base path its own server uses (E2E_PRODUCTION=%s, GITHUB_ACTIONS=%s)',
    async (mode, actions, url) => {
      vi.stubEnv('E2E_PRODUCTION', mode);
      vi.stubEnv('GITHUB_ACTIONS', actions);
      const config = await defaultConfig();
      expect(config.use?.baseURL).toBe(url);
      expect(config.webServer.url).toBe(url);
    },
  );

});
