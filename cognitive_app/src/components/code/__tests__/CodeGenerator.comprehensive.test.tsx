import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { CodeGenerator } from '../CodeGenerator';
import { toast } from 'sonner';
import { CodexAPIClient } from '@/lib/codex-api-client';

vi.mock('sonner', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
  },
}));

vi.mock('@/lib/codex-api-client', () => ({
  CodexAPIClient: vi.fn(),
  CodexAPIError: class CodexAPIError extends Error {},
}));

const mockSpark = {
  llm: vi.fn(),
};

vi.mock('@/lib/spark-llm-client', () => {
  class SparkLLMClientMock {
    async getStatus() {
      return { healthy: true, mode: 'AI-Powered', model: 'gpt-4o-mini (Spark Runtime)' };
    }

    async generateCode({ prompt }: { prompt: string }) {
      const code = await mockSpark.llm(prompt);
      return {
        code: typeof code === 'string'
          ? code
          : `def generated_function():\n    """AI-generated code for ${prompt}"""\n    return "success"`,
        metadata: { k1_factor: 0.331, coherence: 0.81, cache_hit: false, processing_time_ms: 120 },
        quantum_metrics: { superposition_states: 3, entanglement_score: 0.82 },
      };
    }
  }

  return { SparkLLMClient: SparkLLMClientMock };
});

vi.mock('@/lib/mock-api-client', () => {
  class MockCodexAPIClient {
    async getStatus() {
      return { healthy: true, metrics: { k1_factor: 0.312 } };
    }

    async generateCode({ prompt }: { prompt: string }) {
      return {
        code: `def generated_function():\n    """AI-generated code for ${prompt}"""\n    return "success"`,
        metadata: { k1_factor: 0.312, coherence: 0.85, cache_hit: true, processing_time_ms: 150 },
        quantum_metrics: { superposition_states: 2, entanglement_score: 0.9 },
      };
    }
  }

  return { MockCodexAPIClient };
});

describe('CodeGenerator - Comprehensive Test Suite (90%+ Coverage)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockSpark.llm.mockResolvedValue(`def generated_function():\n    """AI-generated code"""\n    return "success"`);
    delete (import.meta.env as any).VITE_CODEX_KEY;
    delete (import.meta.env as any).VITE_CODEX_API;

    vi.mocked(CodexAPIClient).mockImplementation(function () {
      return {
        getStatus: async () => ({ healthy: true, metrics: { k1_factor: 0.312 } }),
        generateCode: async ({ prompt }: { prompt: string }) => ({
          code: `def generated_function():\n    """AI-generated code for ${prompt}"""\n    return "success"`,
          metadata: { k1_factor: 0.312, coherence: 0.85, cache_hit: false, processing_time_ms: 150 },
          quantum_metrics: { superposition_states: 2, entanglement_score: 0.9 },
        }),
      } as any;
    });
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('renders the core generator UI', async () => {
    render(<CodeGenerator />);

    expect(screen.getByText('Code Generation')).toBeInTheDocument();
    expect(screen.getByText(/Status:/)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/example: create a fastapi/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /generate code/i })).toBeInTheDocument();
    expect(screen.getAllByText(/AI Mode:/i).length).toBeGreaterThan(0);
  });

  it('disables generation until the prompt is valid', async () => {
    render(<CodeGenerator />);

    await waitFor(() => {
      expect(screen.getByText('Connected')).toBeInTheDocument();
    });

    const textarea = screen.getByPlaceholderText(/example: create a fastapi/i);
    fireEvent.change(textarea, { target: { value: 'Short' } });

    const button = screen.getByRole('button', { name: /generate code/i });
    expect(button).toBeDisabled();
    expect(screen.getByText('5 / 5000 (min: 10)')).toBeInTheDocument();
  });

  it('generates code through the demo fallback path', async () => {
    render(<CodeGenerator />);

    await waitFor(() => {
      expect(screen.getByText('Connected')).toBeInTheDocument();
    });

    const textarea = screen.getByPlaceholderText(/example: create a fastapi/i);
    fireEvent.change(textarea, { target: { value: 'Create a test function' } });

    const button = screen.getByRole('button', { name: /generate code/i });
    await waitFor(() => expect(button).not.toBeDisabled());
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('Generated Code')).toBeInTheDocument();
    }, { timeout: 3000 });

    expect(toast.success).toHaveBeenCalledWith(
      'Code generated successfully',
      expect.objectContaining({
        description: expect.stringContaining('Generated with Demo Mode'),
      })
    );
  });

  it('uses Spark when AI mode is enabled', async () => {
    render(<CodeGenerator />);

    await waitFor(() => {
      expect(screen.getByText('Connected')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('switch', { name: /toggle ai mode/i }));
    const textarea = screen.getByPlaceholderText(/example: create a fastapi/i);
    fireEvent.change(textarea, { target: { value: 'Create a Python function to add two numbers' } });

    const button = screen.getByRole('button', { name: /generate code/i });
    await waitFor(() => expect(button).not.toBeDisabled());
    fireEvent.click(button);

    await waitFor(() => {
      expect(mockSpark.llm).toHaveBeenCalled();
    }, { timeout: 3000 });
  });

  it('shows the loading text while generation is in flight', async () => {
    mockSpark.llm.mockImplementation(() => new Promise(resolve => setTimeout(() => resolve('code'), 1000)));

    render(<CodeGenerator />);
    await waitFor(() => expect(screen.getByText('Connected')).toBeInTheDocument());

    fireEvent.click(screen.getByRole('switch', { name: /toggle ai mode/i }));
    const textarea = screen.getByPlaceholderText(/example: create a fastapi/i);
    fireEvent.change(textarea, { target: { value: 'Create a hello function' } });

    const button = screen.getByRole('button', { name: /generate code/i });
    await waitFor(() => expect(button).not.toBeDisabled());
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /generating code/i })).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('falls back to the mock generator after a Spark error', async () => {
    mockSpark.llm.mockRejectedValueOnce(new Error('Spark unavailable'));

    render(<CodeGenerator />);
    await waitFor(() => expect(screen.getByText('Connected')).toBeInTheDocument());

    fireEvent.click(screen.getByRole('switch', { name: /toggle ai mode/i }));
    const textarea = screen.getByPlaceholderText(/example: create a fastapi/i);
    fireEvent.change(textarea, { target: { value: 'Create a fallback function' } });

    const button = screen.getByRole('button', { name: /generate code/i });
    await waitFor(() => expect(button).not.toBeDisabled());
    fireEvent.click(button);

    await waitFor(() => {
      expect(mockSpark.llm).toHaveBeenCalled();
    }, { timeout: 3000 });

    await waitFor(() => {
      expect(screen.getByText('Generated Code')).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('shows the interactive demo toggle after generation', async () => {
    render(<CodeGenerator />);

    await waitFor(() => {
      expect(screen.getByText('Connected')).toBeInTheDocument();
    });

    const textarea = screen.getByPlaceholderText(/example: create a fastapi/i);
    fireEvent.change(textarea, { target: { value: 'Create a hello function' } });

    const button = screen.getByRole('button', { name: /generate code/i });
    await waitFor(() => expect(button).not.toBeDisabled());
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('Generated Code')).toBeInTheDocument();
    }, { timeout: 3000 });

    fireEvent.click(screen.getByRole('button', { name: /try it live/i }));
    await waitFor(() => {
      expect(screen.getByText('Interactive Code Demo')).toBeInTheDocument();
    });
  });

  // Gap 2.1 — Spark fallback: assert toast.success fires after successful Spark generation
  it('fires toast.success after Spark generation succeeds', async () => {
    render(<CodeGenerator />);
    await waitFor(() => expect(screen.getByText('Connected')).toBeInTheDocument());

    fireEvent.click(screen.getByRole('switch', { name: /toggle ai mode/i }));
    const textarea = screen.getByPlaceholderText(/example: create a fastapi/i);
    fireEvent.change(textarea, { target: { value: 'Create a function to multiply numbers' } });

    const button = screen.getByRole('button', { name: /generate code/i });
    await waitFor(() => expect(button).not.toBeDisabled());
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('Generated Code')).toBeInTheDocument();
    }, { timeout: 3000 });

    expect(toast.success).toHaveBeenCalledWith(
      'Code generated successfully',
      expect.objectContaining({
        description: expect.stringContaining('Generated with Spark AI'),
      })
    );
  });

  // Gap 2.5 — Non-429 API error: info message + toast.error + mock fallback succeeds
  it('shows info message and toast.error on non-429 API error, then falls back to mock', async () => {
    const apiError = new Error('Internal Server Error');
    // Use a regular function (not arrow) so vitest spy can call it with `new`.
    vi.mocked(CodexAPIClient).mockImplementation(function () {
      return {
        getStatus: async () => ({ healthy: true, metrics: { k1_factor: 0.312 } }),
        generateCode: async () => { throw apiError; },
      };
    } as any);

    (import.meta.env as any).VITE_CODEX_KEY = 'test-key';

    render(<CodeGenerator />);
    await waitFor(() => expect(screen.getByText('Connected')).toBeInTheDocument(), { timeout: 3000 });

    const textarea = screen.getByPlaceholderText(/example: create a fastapi/i);
    fireEvent.change(textarea, { target: { value: 'Create a function that does something useful' } });

    const button = screen.getByRole('button', { name: /generate code/i });
    await waitFor(() => expect(button).not.toBeDisabled());
    fireEvent.click(button);

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith(
        'Primary API unavailable',
        expect.objectContaining({ description: 'Using mock generation as a fallback.' })
      );
    }, { timeout: 3000 });

    await waitFor(() => {
      expect(screen.getByText(/Primary API failed/)).toBeInTheDocument();
    }, { timeout: 3000 });

    await waitFor(() => {
      expect(screen.getByText('Generated Code')).toBeInTheDocument();
    }, { timeout: 3000 });

    delete (import.meta.env as any).VITE_CODEX_KEY;
  });

  // Gap 2.8 — Prompt too short: the button stays disabled and the char-count hint
  // "(min: 10)" is visible — this is the UI guard that prevents the toast path from
  // ever being reached via normal interaction.
  it('keeps the generate button disabled and shows min-length hint when prompt < 10 chars', async () => {
    render(<CodeGenerator />);
    await waitFor(() => expect(screen.getByText('Connected')).toBeInTheDocument());

    const textarea = screen.getByPlaceholderText(/example: create a fastapi/i);

    // 5-char prompt
    fireEvent.change(textarea, { target: { value: 'Short' } });
    expect(screen.getByText('5 / 5000 (min: 10)')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /generate code/i })).toBeDisabled();

    // 9-char prompt (still one below the threshold)
    fireEvent.change(textarea, { target: { value: '123456789' } });
    expect(screen.getByText('9 / 5000 (min: 10)')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /generate code/i })).toBeDisabled();

    // Exactly 10 chars → button becomes enabled and hint disappears
    fireEvent.change(textarea, { target: { value: '1234567890' } });
    await waitFor(() => expect(screen.getByRole('button', { name: /generate code/i })).not.toBeDisabled());
    expect(screen.queryByText(/min: 10/)).not.toBeInTheDocument();
  });

  // Gap 2.7 — Mock generateCode failure path: toast.error('Generation failed') fires.
  // The mock-api-client vi.mock factory is module-scoped, so we use prototype spying to
  // make the already-instantiated mock client's generateCode throw for this one test.
  it('fires toast.error when mock client generateCode throws', async () => {
    delete (import.meta.env as any).VITE_CODEX_KEY;

    // Spy on MockCodexAPIClient prototype so ANY instance created by the component throws.
    const { MockCodexAPIClient } = await import('@/lib/mock-api-client');
    const generateSpy = vi
      .spyOn(MockCodexAPIClient.prototype, 'generateCode')
      .mockRejectedValueOnce(new Error('Mock generation failed'));

    render(<CodeGenerator />);
    await waitFor(() => expect(screen.getByText('Connected')).toBeInTheDocument());

    const textarea = screen.getByPlaceholderText(/example: create a fastapi/i);
    fireEvent.change(textarea, { target: { value: 'Create a function to divide numbers safely' } });

    const button = screen.getByRole('button', { name: /generate code/i });
    await waitFor(() => expect(button).not.toBeDisabled());
    fireEvent.click(button);

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith(
        'Generation failed',
        expect.objectContaining({ description: 'Mock generation failed' })
      );
    }, { timeout: 3000 });

    generateSpy.mockRestore();
  });

  // Test: clipboard failure shows toast.error
  it('shows toast.error when clipboard.writeText rejects', async () => {
    // Mock clipboard to reject
    const clipboardMock = {
      writeText: vi.fn().mockRejectedValueOnce(new Error('Permission denied')),
    };
    Object.defineProperty(navigator, 'clipboard', {
      value: clipboardMock,
      configurable: true,
    });

    render(<CodeGenerator />);
    await waitFor(() => expect(screen.getByText('Connected')).toBeInTheDocument());

    const textarea = screen.getByPlaceholderText(/example: create a fastapi/i);
    fireEvent.change(textarea, { target: { value: 'Create a function to add numbers' } });

    const button = screen.getByRole('button', { name: /generate code/i });
    await waitFor(() => expect(button).not.toBeDisabled());
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('Generated Code')).toBeInTheDocument();
    }, { timeout: 3000 });

    const copyButton = screen.getByRole('button', { name: /copy/i });
    fireEvent.click(copyButton);

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith(
        'Failed to copy',
        expect.objectContaining({
          description: expect.stringContaining('clipboard'),
        })
      );
    }, { timeout: 3000 });

    // Restore clipboard
    Object.defineProperty(navigator, 'clipboard', {
      value: { writeText: vi.fn().mockResolvedValue(undefined) },
      configurable: true,
    });
  });

  // Test: generation calls use DEFAULT_LANGUAGE ('python')
  it('calls mock generateCode with language python (DEFAULT_LANGUAGE)', async () => {
    delete (import.meta.env as any).VITE_CODEX_KEY;

    const { MockCodexAPIClient } = await import('@/lib/mock-api-client');
    const generateSpy = vi.spyOn(MockCodexAPIClient.prototype, 'generateCode');

    render(<CodeGenerator />);
    await waitFor(() => expect(screen.getByText('Connected')).toBeInTheDocument());

    const textarea = screen.getByPlaceholderText(/example: create a fastapi/i);
    fireEvent.change(textarea, { target: { value: 'Create a function to multiply numbers' } });

    const button = screen.getByRole('button', { name: /generate code/i });
    await waitFor(() => expect(button).not.toBeDisabled());
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('Generated Code')).toBeInTheDocument();
    }, { timeout: 3000 });

    expect(generateSpy).toHaveBeenCalledWith(
      expect.objectContaining({
        context: expect.objectContaining({ language: 'python', tier: 'A' }),
      })
    );

    generateSpy.mockRestore();
  });

  it('renders metrics output once generation succeeds', async () => {
    render(<CodeGenerator />);

    await waitFor(() => {
      expect(screen.getByText('Connected')).toBeInTheDocument();
    });

    const textarea = screen.getByPlaceholderText(/example: create a fastapi/i);
    fireEvent.change(textarea, { target: { value: 'Create test code' } });

    const button = screen.getByRole('button', { name: /generate code/i });
    await waitFor(() => expect(button).not.toBeDisabled());
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('Generated Code')).toBeInTheDocument();
    }, { timeout: 3000 });

    expect(screen.getByText(/k₁ factor/i)).toBeInTheDocument();
  });

  it('shows the AI model selection details and status in AI mode', async () => {
    render(<CodeGenerator />);
    await waitFor(() => expect(screen.getByText('Connected')).toBeInTheDocument());

    fireEvent.click(screen.getByRole('switch', { name: /toggle ai mode/i }));
    await waitFor(() => {
      expect(screen.getByText('AI-Powered')).toBeInTheDocument();
      expect(screen.getAllByText(/AI Mode:/i).length).toBeGreaterThan(0);
    });

    const textarea = screen.getByPlaceholderText(/example: create a fastapi/i);
    fireEvent.change(textarea, { target: { value: 'Create a safe REST handler with validation' } });

    const button = screen.getByRole('button', { name: /generate code/i });
    await waitFor(() => expect(button).not.toBeDisabled());
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('Generated Code')).toBeInTheDocument();
      expect(toast.success).toHaveBeenCalledWith(
        'Code generated successfully',
        expect.objectContaining({
          description: expect.stringContaining('Spark AI'),
        })
      );
    }, { timeout: 3000 });

    expect(screen.getAllByText(/AI Mode:/i).length).toBeGreaterThan(0);
  });
});
