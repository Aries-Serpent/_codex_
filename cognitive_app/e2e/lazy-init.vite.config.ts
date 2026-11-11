import { mergeConfig } from 'vite';
import { resolve } from 'node:path';
import applicationConfig from './vite.config';
import { dashboardAPI, variants, type Variant } from './lazy-init/variants';

const name = process.env.LAZY_VARIANT as Variant;
if (!Object.hasOwn(variants, name)) throw new Error('LAZY_VARIANT must name a lazy-init build variant');
const variant = variants[name];
const literal = (value: string | undefined) => value === undefined ? 'undefined' : JSON.stringify(value);
const outDir = resolve(import.meta.dirname, `../dist/lazy-init/${name}`);

export default mergeConfig(applicationConfig, {
  // Never consume a developer's real credentials or permit environment inheritance.
  envDir: false,
  define: {
    'import.meta.env.VITE_CODEX_KEY': literal(variant.key),
    'import.meta.env.VITE_CODEX_API': literal(variant.api),
    'import.meta.env.VITE_CLI_API_URL': JSON.stringify(dashboardAPI),
    'import.meta.env.VITE_STAGE_EXECUTION_TIME_MS': literal(variant.timing),
    'import.meta.env.VITE_API_MODE': JSON.stringify('mock'),
  },
  plugins: [{
    name: 'lazy-init-build-binding',
    enforce: 'post',
    config() {
      // Spark's config hook otherwise replaces every variant's output with "dist".
      return { build: { outDir } };
    },
    transformIndexHtml() {
      return [{ tag: 'meta', attrs: { name: 'lazy-init-variant', content: name }, injectTo: 'head' }];
    },
  }],
  server: {
    watch: { ignored: ['**/dist/**', '**/test-results/**', '**/playwright-report/**'] },
  },
  build: {
    outDir,
    rollupOptions: {
      input: {
        app: resolve(import.meta.dirname, '../index.html'),
        cascade: resolve(import.meta.dirname, 'lazy-init/cascade.html'),
      },
    },
  },
  preview: { host: '127.0.0.1', strictPort: true, proxy: {} },
});
