import { describe, it, expect, vi, beforeEach } from 'vitest';
import { AppService, DEFAULT_LANGUAGE, DEFAULT_MODEL } from '../app-service';
import { CodexAPIClient, CodexAPIError } from '@/lib/codex-api-client';
import { SparkLLMClient } from '@/lib/spark-llm-client';

vi.mock('@/lib/codex-api-client', () => ({
  CodexAPIClient: vi.fn(function () {
    return {
      async getStatus() {
        return { healthy: true, metrics: { k1_factor: 0.31 } };
      },
      async generateCode() {
        return {
          code: 'def generated():\n    return "ok"',
          metadata: { k1_factor: 0.31, coherence: 0.78, cache_hit: false, processing_time_ms: 150 },
          quantum_metrics: { superposition_states: 2, entanglement_score: 0.8 },
        };
      },
    };
  }),
  CodexAPIError: class CodexAPIError extends Error {
    constructor(public statusCode: number, message: string) {
      super(message);
      this.name = 'CodexAPIError';
    }
  },
}));

vi.mock('@/lib/spark-llm-client', () => ({
  SparkLLMClient: vi.fn(function () {
    return {
      async getStatus() {
        return { healthy: true, mode: 'AI-Powered', model: 'gpt-4o-mini (Spark Runtime)' };
      },
      async generateCode() {
        return {
          code: 'def spark_generated():\n    return "spark"',
          metadata: { k1_factor: 0.29, coherence: 0.82, cache_hit: false, processing_time_ms: 110 },
          quantum_metrics: { superposition_states: 3, entanglement_score: 0.85 },
        };
      },
    };
  }),
}));

vi.mock('@/lib/mock-api-client', () => ({
  MockCodexAPIClient: vi.fn(function () {
    return {
      async getStatus() {
        return { healthy: true, metrics: { k1_factor: 0.312 } };
      },
      async generateCode() {
        return {
          code: 'def mock_generated():\n    return "mock"',
          metadata: { k1_factor: 0.312, coherence: 0.68, cache_hit: true, processing_time_ms: 200 },
          quantum_metrics: { superposition_states: 2, entanglement_score: 0.7 },
        };
      },
    };
  }),
}));

describe('AppService code generation integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    const env = import.meta.env as any;
    delete env.VITE_CODEX_KEY;
    delete env.VITE_CODEX_API;
  });

  it('returns a Spark response when AI mode is enabled and available', async () => {
    const service = new AppService();

    const result = await service.generateCode({
      prompt: 'Create a fastapi route for health checks',
      language: DEFAULT_LANGUAGE,
      model: DEFAULT_MODEL,
      aiMode: true,
    });

    expect(result.source).toBe('spark');
    expect(result.response.code).toContain('spark_generated');
    expect(vi.mocked(SparkLLMClient)).toHaveBeenCalled();
  });

  it('falls back to API generation after a Spark failure', async () => {
    const env = import.meta.env as any;
    env.VITE_CODEX_KEY = 'test-api-key';
    env.VITE_CODEX_API = 'http://localhost:8000';

    vi.mocked(SparkLLMClient).mockImplementation(function () {
      return {
        async getStatus() { return { healthy: true, mode: 'AI-Powered', model: 'gpt-4o-mini (Spark Runtime)' }; },
        async generateCode() {
          throw new Error('Spark unavailable');
        },
      } as any;
    });

    vi.mocked(CodexAPIClient).mockImplementation(function () {
      return {
        async getStatus() { return { healthy: true, metrics: { k1_factor: 0.31 } }; },
        async generateCode() {
          return {
            code: 'def api_generated():\n    return "api"',
            metadata: { k1_factor: 0.31, coherence: 0.78, cache_hit: false, processing_time_ms: 150 },
            quantum_metrics: { superposition_states: 2, entanglement_score: 0.8 },
          };
        },
      } as any;
    });

    const service = new AppService();
    const result = await service.generateCode({
      prompt: 'Create a safe REST handler',
      language: 'python',
      model: 'gpt-4o-mini',
      aiMode: true,
    });

    expect(result.source).toBe('api');
    expect(result.response.code).toContain('api_generated');
  });

  it('re-throws 429 API rate limits to allow the UI recovery path', async () => {
    const env = import.meta.env as any;
    env.VITE_CODEX_KEY = 'test-rate-limit-key';
    env.VITE_CODEX_API = 'http://localhost:8000';

    const rateLimitError = new CodexAPIError(429, 'Rate limit exceeded');
    vi.mocked(CodexAPIClient).mockImplementation(function () {
      return {
        async getStatus() { return { healthy: true, metrics: { k1_factor: 0.31 } }; },
        async generateCode() {
          throw rateLimitError;
        },
      } as any;
    });

    const service = new AppService();

    await expect(service.generateCode({
      prompt: 'Create a function to do work',
      language: 'python',
      model: 'gpt-4o',
    })).rejects.toMatchObject({ statusCode: 429, message: 'Rate limit exceeded' });
  });

  it('uses demo-mode status when no API key is configured', async () => {
    const service = new AppService();

    await expect(service.getStatus(false)).resolves.toMatchObject({
      status: 'connected',
      message: 'Using demo mode (API key not configured)',
    });
  });
});
