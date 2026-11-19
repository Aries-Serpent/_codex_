import { execFileSync } from 'node:child_process';
import { resolve } from 'node:path';
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
      url: 'http://localhost:5173/',
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

  it('passes the configured forwarded brain origin to Vite', async () => {
    vi.stubEnv('COGNITIVE_BRAIN_API_URL', 'https://brain.example.invalid/forwarded/');
    const config = await defaultConfig();
    expect(config.webServer).toMatchObject({
      env: {
        VITE_CLI_API_URL: 'https://brain.example.invalid/forwarded',
      },
    });
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
    ['1', 'true', 'http://localhost:5173/_codex_/cognitive_app/'],
    ['1', '', 'http://localhost:5173/'],
    ['', 'true', 'http://localhost:5173/'],
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

  it('isolates lazy variant builds from shell credentials and from other port ranges', () => {
    // Real Node + Vite config loading (esbuild cannot run inside the jsdom test environment).
    const probe = `
      import { loadConfigFromFile, loadEnv } from 'vite';
      const { config } = await loadConfigFromFile(
        { command: 'serve', mode: 'development' }, 'e2e/lazy-init.vite.config.ts', undefined, 'silent');
      console.log(JSON.stringify({
        envDir: config.envDir,
        exposed: loadEnv('development', process.cwd(), config.envPrefix),
        outDir: config.build.outDir,
      }));`;
    const output = execFileSync(process.execPath, ['--input-type=module', '-e', probe], {
      cwd: resolve(__dirname, '../../..'),
      env: {
        ...process.env,
        LAZY_VARIANT: 'default',
        E2E_PORT: '5410',
        LAZY_INIT_SYNTHETIC_ONLY_TOKEN: 'prefix-sentinel-token',
        VITE_GITHUB_TOKEN: 'shell-sentinel-token',
      },
      encoding: 'utf8',
    });
    const result = JSON.parse(output.trim().split('\n').pop() ?? '');
    expect(result.envDir).toBe(false);
    expect(result.exposed).toEqual({});
    expect(result.outDir).toMatch(/[/\\]dist[/\\]lazy-init[/\\]5410[/\\]default$/);
  });
});
