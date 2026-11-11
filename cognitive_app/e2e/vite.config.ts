import { mergeConfig } from 'vite';
import { resolve } from 'node:path';
import applicationConfig from '../vite.config';

export default mergeConfig(applicationConfig, {
  plugins: [{
    name: 'isolated-e2e-server',
    enforce: 'post',
    configResolved(config) {
      config.server.host = '127.0.0.1';
      config.server.port = Number(process.env.E2E_PORT || 5173);
      config.server.strictPort = true;
      config.server.proxy = {};
    },
  }],
  build: {
    rollupOptions: {
      input: {
        app: resolve(import.meta.dirname, '../index.html'),
        dependencies: resolve(import.meta.dirname, 'fixtures/dependencies.html'),
      },
    },
  },
});
