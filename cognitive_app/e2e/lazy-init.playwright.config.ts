import { defineConfig, devices } from '@playwright/test';
import { resolve } from 'node:path';
import { variantNames, variantURL } from './lazy-init/variants';

const firstPort = Number(process.env.LAZY_PORT || 5410);
if (!Number.isInteger(firstPort) || firstPort < 1024 || firstPort + variantNames.length - 1 > 65535) {
  throw new Error('LAZY_PORT must start an unprivileged ten-port loopback range');
}
const production = process.env.E2E_PRODUCTION === '1';
const base = process.env.GITHUB_ACTIONS ? '/_codex_/cognitive_app/' : '/';

export default defineConfig({
  testDir: '.',
  testMatch: 'code-generator-lazy-init.spec.ts',
  fullyParallel: true,
  forbidOnly: true,
  retries: 0,
  workers: 3,
  timeout: 60_000,
  globalTimeout: 15 * 60_000,
  expect: { timeout: 10_000 },
  outputDir: `../test-results/lazy-init-${production ? 'production' : 'development'}-${firstPort}`,
  reporter: [['list']],
  metadata: {
    lazyURLs: Object.fromEntries(variantNames.map(name => [name, variantURL(name, firstPort, base)])),
  },
  use: {
    baseURL: variantURL('default', firstPort, base),
    serviceWorkers: 'block',
    actionTimeout: 10_000,
    navigationTimeout: 30_000,
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  ],
  webServer: variantNames.map((name, index) => {
    const port = firstPort + index;
    const args = `--config e2e/lazy-init.vite.config.ts --host 127.0.0.1 --port ${port} --strictPort`;
    return {
      cwd: resolve(import.meta.dirname, '..'),
      command: production
        ? `node node_modules/vite/bin/vite.js build --config e2e/lazy-init.vite.config.ts && node node_modules/vite/bin/vite.js preview ${args}`
        : `node node_modules/vite/bin/vite.js ${args}`,
      env: { LAZY_VARIANT: name, E2E_PORT: String(port), GITHUB_ACTIONS: process.env.GITHUB_ACTIONS || '' },
      url: variantURL(name, firstPort, base),
      reuseExistingServer: false,
      timeout: production ? 600_000 : 120_000,
      stdout: 'pipe',
      stderr: 'pipe',
    };
  }),
});
