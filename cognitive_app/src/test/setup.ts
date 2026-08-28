import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach, vi } from 'vitest';

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  }),
});

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver implements IntersectionObserver {
  readonly root: Element | null = null;
  readonly rootMargin: string = '';
  readonly thresholds: ReadonlyArray<number> = [];

  constructor() {}

  disconnect(): void {}

  observe(): void {}

  takeRecords(): IntersectionObserverEntry[] {
    return [];
  }

  unobserve(): void {}
};

// Mock HTMLCanvasElement for canvas rendering tests
HTMLCanvasElement.prototype.getContext = vi.fn().mockReturnValue({
  fillRect: vi.fn(),
  clearRect: vi.fn(),
  getImageData: vi.fn(),
  putImageData: vi.fn(),
  createImageData: vi.fn(),
  setTransform: vi.fn(),
  drawImage: vi.fn(),
  save: vi.fn(),
  fillText: vi.fn(),
  restore: vi.fn(),
  beginPath: vi.fn(),
  moveTo: vi.fn(),
  lineTo: vi.fn(),
  closePath: vi.fn(),
  stroke: vi.fn(),
  fill: vi.fn(),
  translate: vi.fn(),
  scale: vi.fn(),
  rotate: vi.fn(),
  arc: vi.fn(),
  setLineDash: vi.fn(),
  createLinearGradient: vi.fn(() => ({
    addColorStop: vi.fn(),
  })),
  createRadialGradient: vi.fn(() => ({
    addColorStop: vi.fn(),
  })),
});

// Mock canvas width and height properties
Object.defineProperty(HTMLCanvasElement.prototype, 'width', {
  get: function() { return this._width || 800; },
  set: function(val) { this._width = val; },
});

Object.defineProperty(HTMLCanvasElement.prototype, 'height', {
  get: function() { return this._height || 600; },
  set: function(val) { this._height = val; },
});

// Mock spark API for tests
(global as any).spark = {
  llmPrompt: (strings: TemplateStringsArray, ...values: any[]) => {
    return strings.reduce((acc, str, i) => acc + str + (values[i] || ''), '');
  },
  llm: vi.fn().mockResolvedValue(`def generated_function():
    """AI-generated code"""
    return "success"`),
  user: vi.fn().mockResolvedValue({
    avatarUrl: 'https://example.com/avatar.png',
    email: 'test@example.com',
    id: 'test-user-id',
    isOwner: true,
    login: 'testuser',
  }),
  kv: {
    keys: vi.fn().mockResolvedValue([]),
    get: vi.fn().mockResolvedValue(undefined),
    set: vi.fn().mockResolvedValue(undefined),
    delete: vi.fn().mockResolvedValue(undefined),
  },
  import: {
    meta: {
      env: {
        DEV: true,
        PROD: false,
        MODE: 'test',
      },
    },
  },
};
