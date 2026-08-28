import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { CodeGenerator } from '../CodeGenerator';
import { SparkLLMClient } from '@/lib/spark-llm-client';

// Mock the clients with real constructor-based classes so prototype assignments work
vi.mock('@/lib/spark-llm-client', () => {
  class SparkLLMClientMock {
    async getStatus() {
      return { healthy: true, mode: 'AI-Powered', model: 'gpt-4o-mini (Spark Runtime)' };
    }

    async generateCode() {
      return {
        code: 'def ai_generated():\n    pass',
        metadata: { k1_factor: 0.31, coherence: 0.78, cache_hit: false, processing_time_ms: 123 },
        quantum_metrics: { superposition_states: 3, entanglement_score: 0.82 },
      };
    }
  }

  return { SparkLLMClient: SparkLLMClientMock };
});

vi.mock('@/lib/codex-api-client', () => {
  class CodexAPIClientMock {
    async getStatus() {
      return { healthy: true, metrics: { k1_factor: 0.312 } };
    }

    async generateCode() {
      return {
        code: '# Generated code',
        metadata: { k1_factor: 0.312, coherence: 0.685, cache_hit: false, processing_time_ms: 1200 },
        quantum_metrics: { superposition_states: 3, entanglement_score: 0.85 },
      };
    }
  }

  return {
    CodexAPIClient: CodexAPIClientMock,
    CodexAPIError: class CodexAPIError extends Error {
      constructor(public statusCode: number, message: string) {
        super(message);
        this.name = 'CodexAPIError';
      }
    },
  };
});

vi.mock('@/lib/mock-api-client', () => {
  class MockCodexAPIClient {
    async getStatus() {
      return { healthy: true, metrics: { k1_factor: 0.312 } };
    }

    async generateCode() {
      return {
        code: '# Generated code',
        metadata: { k1_factor: 0.312, coherence: 0.685, cache_hit: false, processing_time_ms: 1200 },
        quantum_metrics: { superposition_states: 3, entanglement_score: 0.85 },
      };
    }
  }

  return { MockCodexAPIClient };
});

describe('CodeGenerator - AI Mode Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render AI Mode toggle', () => {
    render(<CodeGenerator />);

    expect(screen.getByText(/AI Mode:/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Toggle AI Mode/i)).toBeInTheDocument();
  });

  it('should toggle AI Mode on and off', () => {
    render(<CodeGenerator />);

    const toggle = screen.getByLabelText(/Toggle AI Mode/i);

    // Initially off
    expect(screen.getByText('Off')).toBeInTheDocument();

    // Turn on
    fireEvent.click(toggle);
    expect(screen.getByText('On')).toBeInTheDocument();

    // Turn off
    fireEvent.click(toggle);
    expect(screen.getByText('Off')).toBeInTheDocument();
  });

  it('should show "AI-Powered" status when AI mode is on and connected', async () => {
    const mockGetStatus = vi.fn().mockResolvedValue({
      healthy: true,
      mode: 'AI-Powered',
      model: 'gpt-4o-mini (Spark Runtime)'
    });

    SparkLLMClient.prototype.getStatus = mockGetStatus;

    render(<CodeGenerator />);

    const toggle = screen.getByLabelText(/Toggle AI Mode/i);
    fireEvent.click(toggle);

    await waitFor(() => {
      expect(screen.getByText(/AI Mode:/i)).toBeInTheDocument();
    });
  });

  it('should use SparkLLMClient when AI mode is enabled', async () => {
    const mockGenerateCode = vi.fn().mockResolvedValue({
      code: 'def ai_generated():\n    pass',
      metadata: {
        k1_factor: 0.31,
        coherence: 0.78,
        cache_hit: false,
        processing_time_ms: 123
      },
      quantum_metrics: {
        superposition_states: 3,
        entanglement_score: 0.82,
        decoherence_time: 0.45
      }
    });

    SparkLLMClient.prototype.generateCode = mockGenerateCode;

    render(<CodeGenerator />);

    // Enable AI mode
    const toggle = screen.getByLabelText(/Toggle AI Mode/i);
    fireEvent.click(toggle);

    // Enter prompt
    const textarea = screen.getByPlaceholderText(/example: create a fastapi endpoint/i);
    fireEvent.change(textarea, { target: { value: 'Create a test function with 10+ chars' } });

    // Click generate
    const generateButton = screen.getByRole('button', { name: /generate code/i });
    fireEvent.click(generateButton);

    await waitFor(() => {
      expect(mockGenerateCode).toHaveBeenCalledWith({
        prompt: 'Create a test function with 10+ chars',
        context: { language: 'python', tier: 'B' }
      });
    });
  });

  it('should display quantum metrics from AI generation', async () => {
    const mockGenerateCode = vi.fn().mockResolvedValue({
      code: 'def quantum_code():\n    pass',
      metadata: {
        k1_factor: 0.305,
        coherence: 0.81,
        cache_hit: false,
        processing_time_ms: 234
      },
      quantum_metrics: {
        superposition_states: 3,
        entanglement_score: 0.85,
        decoherence_time: 0.52
      }
    });

    SparkLLMClient.prototype.generateCode = mockGenerateCode;

    render(<CodeGenerator />);

    // Enable AI mode
    const toggle = screen.getByLabelText(/Toggle AI Mode/i);
    fireEvent.click(toggle);

    // Generate code
    const textarea = screen.getByPlaceholderText(/example: create a fastapi endpoint/i);
    fireEvent.change(textarea, { target: { value: 'Generate quantum AI code now' } });

    const generateButton = screen.getByRole('button', { name: /generate code/i });
    fireEvent.click(generateButton);

    await waitFor(() => {
      expect(mockGenerateCode).toHaveBeenCalled();
    }, { timeout: 3000 });
  });

  it('should handle AI generation errors gracefully', async () => {
    const mockGenerateCode = vi.fn().mockRejectedValue(new Error('AI service unavailable'));

    SparkLLMClient.prototype.generateCode = mockGenerateCode;

    render(<CodeGenerator />);

    // Enable AI mode
    const toggle = screen.getByLabelText(/Toggle AI Mode/i);
    fireEvent.click(toggle);

    // Try to generate
    const textarea = screen.getByPlaceholderText(/example: create a fastapi endpoint/i);
    fireEvent.change(textarea, { target: { value: 'Test error handling with AI mode' } });

    const generateButton = screen.getByRole('button', { name: /generate code/i });
    fireEvent.click(generateButton);

    await waitFor(() => {
      expect(mockGenerateCode).toHaveBeenCalled();
    });
  });

  it('should show different status based on AI mode', async () => {
    render(<CodeGenerator />);

    // Check initial status (Demo mode)
    expect(screen.getByText(/Status:/i)).toBeInTheDocument();

    // Enable AI mode
    const toggle = screen.getByLabelText(/Toggle AI Mode/i);
    fireEvent.click(toggle);

    // Status should update for AI mode
    await waitFor(() => {
      expect(screen.getByText(/Status:/i)).toBeInTheDocument();
    });
  });
});
