/**
 * Vitest Configuration for Cognitive App Testing
 * 
 * Configures Vitest test runner for React component testing with:
 * - jsdom environment for DOM simulation
 * - React plugin for JSX transformation
 * - Path aliases matching Vite configuration
 * - Coverage reporting with v8 provider
 * - Test setup file for global configuration
 * 
 * @see https://vitest.dev/config/
 */
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/test/setup.ts',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/mockData',
        'dist/',
      ],
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
