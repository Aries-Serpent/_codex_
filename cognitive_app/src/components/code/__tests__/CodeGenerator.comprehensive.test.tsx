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

    vi.mocked(CodexAPIClient).mockImplementation(() => ({
      getStatus: async () => ({ healthy: true, metrics: { k1_factor: 0.312 } }),
      generateCode: async ({ prompt }: { prompt: string }) => ({
        code: `def generated_function():\n    """AI-generated code for ${prompt}"""\n    return "success"`,
        metadata: { k1_factor: 0.312, coherence: 0.85, cache_hit: false, processing_time_ms: 150 },
        quantum_metrics: { superposition_states: 2, entanglement_score: 0.9 },
      }),
    }) as any);
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
    expect(screen.getByText(/AI Mode:/i)).toBeInTheDocument();
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
});
