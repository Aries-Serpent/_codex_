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

});
