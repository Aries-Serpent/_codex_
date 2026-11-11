import { afterEach, describe, expect, it, vi } from 'vitest';

const defaultConfigPath = '../../../playwright.config';
const lazyConfigPath = '../../../e2e/lazy-init.playwright.config';

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
  it('excludes the dedicated lazy suite from default discovery', async () => {
    const config = await defaultConfig();
    expect(config.testIgnore).toBe('**/code-generator-lazy-init.spec.ts');
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

  it('keeps lazy discovery, metadata and owned-server directories together', async () => {
    vi.stubEnv('LAZY_PORT', '5410');
    const config = (await import(lazyConfigPath)).default;
    expect(config.testMatch).toBe('code-generator-lazy-init.spec.ts');
    expect(Object.keys(config.metadata?.lazyURLs)).toHaveLength(10);
    const servers = config.webServer;
    expect(Array.isArray(servers)).toBe(true);
    expect(servers).toHaveLength(10);
    if (!Array.isArray(servers)) throw new Error('Expected variant servers');
    for (const server of servers) {
      expect(server.cwd).toMatch(/[/\\]cognitive_app$/);
      expect(server.cwd).not.toContain('%20');
      expect(server.reuseExistingServer).toBe(false);
    }
  });
});
