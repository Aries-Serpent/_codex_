import { describe, it, expect, vi, beforeEach } from 'vitest';
import { SparkLLMClient } from '../spark-llm-client';

describe('SparkLLMClient', () => {
  let client: SparkLLMClient;

  beforeEach(() => {
    client = new SparkLLMClient();
    vi.clearAllMocks();
  });

  describe('generateCode', () => {
    it('should generate code using Spark LLM for Python', async () => {
      const mockLLM = vi.fn().mockResolvedValue('def hello():\n    print("Hello, World!")');
      global.spark = {
        llm: mockLLM,
        llmPrompt: (strings: TemplateStringsArray, ...values: any[]) => {
          return strings.reduce((acc, str, i) => acc + str + (values[i] || ''), '');
        }
      } as any;

      const request = {
        prompt: 'Create a hello world function',
        context: {
          language: 'python',
          tier: 'B'
        }
      };

      const result = await client.generateCode(request);

      expect(result.code).toBe('def hello():\n    print("Hello, World!")');
      expect(result.metadata.k1_factor).toBeGreaterThanOrEqual(0.28);
      expect(result.metadata.k1_factor).toBeLessThanOrEqual(0.33);
      expect(result.metadata.coherence).toBeGreaterThanOrEqual(0.72);
      expect(result.metadata.coherence).toBeLessThanOrEqual(0.84);
      expect(typeof result.metadata.cache_hit).toBe('boolean');
      expect(result.metadata.processing_time_ms).toBeGreaterThanOrEqual(0);
      expect(result.quantum_metrics.superposition_states).toBeGreaterThanOrEqual(2);
      expect(result.quantum_metrics.superposition_states).toBeLessThanOrEqual(4);
      expect(result.quantum_metrics.entanglement_score).toBeGreaterThanOrEqual(0.78);
      expect(mockLLM).toHaveBeenCalledTimes(1);
    });

    it('should use default language and tier when not provided', async () => {
      const mockLLM = vi.fn().mockResolvedValue('code');
      global.spark = {
        llm: mockLLM,
        llmPrompt: (strings: TemplateStringsArray, ...values: any[]) => {
          return strings.reduce((acc, str, i) => acc + str + (values[i] || ''), '');
        }
      } as any;

      const request = {
        prompt: 'Create something'
      };

      const result = await client.generateCode(request);

      expect(result.code).toBe('code');
      expect(mockLLM).toHaveBeenCalled();
    });

    it('should fallback to template-based generation on Spark LLM error', async () => {
      const mockLLM = vi.fn().mockRejectedValue(new Error('LLM API error'));
      global.spark = {
        llm: mockLLM,
        llmPrompt: (strings: TemplateStringsArray, ...values: any[]) => {
          return strings.reduce((acc, str, i) => acc + str + (values[i] || ''), '');
        }
      } as any;

      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      const request = {
        prompt: 'Create a test function',
        context: {
          language: 'python',
          tier: 'B'
        }
      };

      const result = await client.generateCode(request);

      expect(result.code).toContain('def ');
      expect(result.code).toContain('Create a test function');
      expect(result.metadata.cache_hit).toBe(false);
      expect(consoleErrorSpy).toHaveBeenCalledWith('Spark LLM generation error:', expect.any(Error));

      consoleErrorSpy.mockRestore();
    });

    it('should generate Python fallback code with proper structure', async () => {
      const mockLLM = vi.fn().mockRejectedValue(new Error('Error'));
      global.spark = {
        llm: mockLLM,
        llmPrompt: (strings: TemplateStringsArray, ...values: any[]) => ''
      } as any;

      vi.spyOn(console, 'error').mockImplementation(() => {});

      const request = {
        prompt: 'Create a data validator',
        context: {
          language: 'python',
          tier: 'A'
        }
      };

      const result = await client.generateCode(request);

      expect(result.code).toContain('def ');
      expect(result.code).toContain('validate_input');
    });

    it('should generate JavaScript/TypeScript fallback code', async () => {
      const mockLLM = vi.fn().mockRejectedValue(new Error('Error'));
      global.spark = {
        llm: mockLLM,
        llmPrompt: (strings: TemplateStringsArray, ...values: any[]) => ''
      } as any;

      vi.spyOn(console, 'error').mockImplementation(() => {});

      const request = {
        prompt: 'Create an async handler',
        context: {
          language: 'javascript',
          tier: 'B'
        }
      };

      const result = await client.generateCode(request);

      expect(result.code).toContain('async function');
    });

    it('should generate generic fallback code for unsupported languages', async () => {
      const mockLLM = vi.fn().mockRejectedValue(new Error('Error'));
      global.spark = {
        llm: mockLLM,
        llmPrompt: (strings: TemplateStringsArray, ...values: any[]) => ''
      } as any;

      vi.spyOn(console, 'error').mockImplementation(() => {});

      const request = {
        prompt: 'Create something',
        context: {
          language: 'ruby',
          tier: 'B'
        }
      };

      const result = await client.generateCode(request);

      expect(result.code).toContain('function main()');
    });
  });

  describe('getStatus', () => {
    it('should return healthy status with AI-Powered mode', async () => {
      const status = await client.getStatus();

      expect(status.healthy).toBe(true);
      expect(status.mode).toBe('AI-Powered');
      expect(status.model).toBe('gpt-4o-mini (Spark Runtime)');
    });
  });
});
