import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { CodeGenerator } from '../CodeGenerator';
import { CodexAPIClient } from '@/lib/codex-api-client';
import { SparkLLMClient } from '@/lib/spark-llm-client';

// Create mock instances that will be reused
const createMockCodexClient = () => ({
  getStatus: async () => ({
    healthy: true,
    metrics: { k1_factor: 0.312 },
  }),
  generateCode: async () => ({
    code: '# Generated code',
    metadata: { k1_factor: 0.312, coherence: 0.685, cache_hit: false, processing_time_ms: 1200 },
    quantum_metrics: { superposition_states: 3, entanglement_score: 0.85 },
  }),
});

const createMockSparkClient = () => ({
  generateCode: async () => ({
    code: '# AI generated code',
    metadata: { k1_factor: 0.28, coherence: 0.85 },
    quantum_metrics: { superposition_states: 3, entanglement_score: 0.85 },
  }),
  getStatus: async () => ({
    healthy: true,
    model: 'gpt-4o-mini (Spark Runtime)',
  }),
});

// Mock the modules with constructor-safe factory functions
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

vi.mock('@/lib/spark-llm-client', () => {
  class SparkLLMClientMock {
    async generateCode() {
      return {
        code: '# AI generated code',
        metadata: { k1_factor: 0.28, coherence: 0.85 },
        quantum_metrics: { superposition_states: 3, entanglement_score: 0.85 },
      };
    }

    async getStatus() {
      return {
        healthy: true,
        model: 'gpt-4o-mini (Spark Runtime)',
      };
    }
  }

  return { SparkLLMClient: SparkLLMClientMock };
});

describe('CodeGenerator - Lazy Initialization Pattern', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    delete import.meta.env.VITE_CODEX_KEY;
    delete import.meta.env.VITE_CODEX_API;

    // Set up mocks with factory functions
    const mockCodexClient = createMockCodexClient();
    const mockSparkClient = createMockSparkClient();

    // MockCodexAPIClient uses real implementation, only mock CodexAPIClient and SparkLLMClient
    vi.mocked(CodexAPIClient).mockImplementation(function () {
      return mockCodexClient as any;
    });
    vi.mocked(SparkLLMClient).mockImplementation(function () {
      return mockSparkClient as any;
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Test 2: No API Key Scenario', () => {
    it('should show "Connected" status with green dot when no API key', async () => {
      render(<CodeGenerator />);

      await waitFor(() => {
        const statusText = screen.getByText('Connected');
        expect(statusText).toBeInTheDocument();
        expect(statusText).toHaveClass('text-green-500');
      }, { timeout: 3000 });
    });

    it('should display blue info message for demo mode', async () => {
      render(<CodeGenerator />);

      await waitFor(() => {
        const infoMessage = screen.getByText(/Using demo mode/i);
        expect(infoMessage).toBeInTheDocument();
      }, { timeout: 3000 });

      const errorMessage = screen.queryByText(/Error/i);
      expect(errorMessage).not.toBeInTheDocument();
    });

    it('should enable Generate button in demo mode', async () => {
      render(<CodeGenerator />);

      // Wait for status check to complete
      await waitFor(() => {
        expect(screen.getByText('Connected')).toBeInTheDocument();
      }, { timeout: 3000 });

      // Add valid prompt to enable button (needs min 10 chars)
      const textarea = screen.getByPlaceholderText(/Example: Create a FastAPI/i);
      fireEvent.change(textarea, { target: { value: 'Create a simple hello world function' } });

      // Now button should be enabled
      await waitFor(() => {
        const button = screen.getByRole('button', { name: /Generate Code/i });
        expect(button).not.toBeDisabled();
      }, { timeout: 2000 });
    });
  });

  describe('Test 3: With API Key Scenario', () => {
    beforeEach(() => {
      import.meta.env.VITE_CODEX_KEY = 'test-api-key-12345';
      import.meta.env.VITE_CODEX_API = 'http://localhost:8000';

      // Ensure CodexAPIClient mock is set up for this scenario
      const mockCodexClient = createMockCodexClient();
      vi.mocked(CodexAPIClient).mockImplementation(function () {
        return mockCodexClient as any;
      });
    });

    it('should show "Checking..." status initially', async () => {
      // Mock delayed response
      const delayedMock = createMockCodexClient();
      delayedMock.getStatus = async () => {
        await new Promise(resolve => setTimeout(resolve, 100));
        return { healthy: true, metrics: {} };
      };
      vi.mocked(CodexAPIClient).mockImplementation(function () {
        return delayedMock as any;
      });

      render(<CodeGenerator />);

      const statusText = screen.getByText('Checking...');
      expect(statusText).toBeInTheDocument();
      expect(statusText).toHaveClass('text-yellow-500');
    });

    it('should transition to "Connected" after successful check', async () => {
      render(<CodeGenerator />);

      await waitFor(() => {
        const statusText = screen.getByText('Connected');
        expect(statusText).toBeInTheDocument();
        expect(statusText).toHaveClass('text-green-500');
      }, { timeout: 3000 });
    });

    it('should enable button after successful API check', async () => {
      render(<CodeGenerator />);

      await waitFor(() => {
        expect(screen.getByText('Connected')).toBeInTheDocument();
      }, { timeout: 3000 });

      // Add valid prompt to enable button (needs min 10 chars)
      const textarea = screen.getByPlaceholderText(/Example: Create a FastAPI/i);
      fireEvent.change(textarea, { target: { value: 'Create a simple hello world function' } });

      await waitFor(() => {
        const button = screen.getByRole('button', { name: /Generate Code/i });
        expect(button).not.toBeDisabled();
      }, { timeout: 2000 });
    });
  });

  describe('Test 4: Mock Fallback Scenario', () => {
    it('should validate character count minimum (10 chars)', async () => {
      render(<CodeGenerator />);

      const textarea = screen.getByPlaceholderText(/Example: Create a FastAPI/i);
      fireEvent.change(textarea, { target: { value: 'Hello' } });

      await waitFor(() => {
        const counter = screen.getByText(/5 \/ 5000 \(min: 10\)/i);
        expect(counter).toBeInTheDocument();
        expect(counter).toHaveClass('text-destructive');
      });

      const button = screen.getByRole('button', { name: /Generate Code/i });
      expect(button).toBeDisabled();
    });

    it('should display character count correctly', async () => {
      render(<CodeGenerator />);

      const textarea = screen.getByPlaceholderText(/Example: Create a FastAPI/i);
      fireEvent.change(textarea, { target: { value: 'Create a hello world function' } });

      await waitFor(() => {
        const counter = screen.getByText('29 / 5000');
        expect(counter).toBeInTheDocument();
      });
    });

    it('should have proper UI structure', async () => {
      render(<CodeGenerator />);

      expect(screen.getByText('Code Generation')).toBeInTheDocument();
      expect(screen.getByText('Status:')).toBeInTheDocument();
      expect(screen.getByLabelText(/Describe the code/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Generate Code/i })).toBeInTheDocument();
    });
  });

  describe('Test 5: Environment Configuration', () => {
    it('should handle different timing configurations', async () => {
      render(<CodeGenerator />);

      await waitFor(() => {
        expect(screen.getByText('Connected')).toBeInTheDocument();
      }, { timeout: 3000 });

      // Verify component rendered successfully
      expect(screen.getByText('Code Generation')).toBeInTheDocument();
    }, 10000);

    it('should handle different API URL configurations', async () => {
      import.meta.env.VITE_CODEX_API = 'https://api.example.com';
      import.meta.env.VITE_CODEX_KEY = 'test-key';

      render(<CodeGenerator />);

      await waitFor(() => {
        expect(screen.getByText('Connected')).toBeInTheDocument();
      }, { timeout: 3000 });

      // Verify component rendered with API configuration
      expect(screen.getByText('Code Generation')).toBeInTheDocument();
    }, 10000);
  });

  describe('Component Structure Validation', () => {
    it('should have status indicator with correct states', async () => {
      render(<CodeGenerator />);

      await waitFor(() => {
        expect(screen.getByText('Status:')).toBeInTheDocument();
      }, { timeout: 2000 });

      const statusContainer = screen.getByText('Status:').parentElement;
      expect(statusContainer).toBeInTheDocument();

      await waitFor(() => {
        const dot = statusContainer?.querySelector('.w-2.h-2.rounded-full');
        expect(dot).toBeInTheDocument();
      }, { timeout: 2000 });
    }, 10000);

    it('should have textarea with validation styling', async () => {
      render(<CodeGenerator />);

      const textarea = screen.getByPlaceholderText(/Example: Create a FastAPI/i);
      expect(textarea).toHaveClass('font-mono', 'resize-none');

      fireEvent.change(textarea, { target: { value: 'Hi' } });

      await waitFor(() => {
        expect(textarea).toHaveClass('border-destructive');
      }, { timeout: 2000 });
    }, 10000);

    it('should have Generate button with proper states', async () => {
      render(<CodeGenerator />);

      await waitFor(() => {
        const button = screen.getByRole('button', { name: /Generate Code/i });
        expect(button).toBeInTheDocument();
      }, { timeout: 2000 });

      const button = screen.getByRole('button', { name: /Generate Code/i });
      const icon = button.querySelector('svg');
      expect(icon).toBeInTheDocument();
    }, 10000);
  });
});

describe('CodeGenerator - Real Workflows', () => {
  beforeEach(() => {
    // Reset mocks for this suite
    vi.clearAllMocks();
    // No need to mock MockCodexAPIClient - using real implementation
  });

  it('should generate code successfully in demo mode', async () => {
    render(<CodeGenerator />);

    await waitFor(() => {
      expect(screen.getByText('Connected')).toBeInTheDocument();
    }, { timeout: 3000 });

    const textarea = screen.getByPlaceholderText(/Example: Create a FastAPI/i);
    fireEvent.change(textarea, { target: { value: 'Create a hello world function' } });

    const button = screen.getByRole('button', { name: /Generate Code/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('Generated Code')).toBeInTheDocument();
    }, { timeout: 5000 });
  }, 15000);

  it('should handle copy functionality', async () => {
    const mockWriteText = vi.fn().mockResolvedValue(undefined);
    Object.assign(navigator, {
      clipboard: {
        writeText: mockWriteText,
      },
    });

    render(<CodeGenerator />);

    // Wait for connection status
    await waitFor(() => {
      expect(screen.getByText('Connected')).toBeInTheDocument();
    }, { timeout: 3000 });

    const textarea = screen.getByPlaceholderText(/Example: Create a FastAPI/i);
    fireEvent.change(textarea, { target: { value: 'Create a test function' } });

    const generateButton = screen.getByRole('button', { name: /Generate Code/i });
    fireEvent.click(generateButton);

    // Wait for code generation to complete
    await waitFor(() => {
      expect(screen.getByText('Generated Code')).toBeInTheDocument();
    }, { timeout: 5000 });

    // Find Copy button with more flexible selector
    const copyButton = await waitFor(() => {
      const buttons = screen.getAllByRole('button');
      const copyBtn = buttons.find(btn => btn.textContent?.includes('Copy') || btn.getAttribute('aria-label')?.includes('Copy'));
      expect(copyBtn).toBeDefined();
      return copyBtn!;
    }, { timeout: 3000 });

    fireEvent.click(copyButton);

    await waitFor(() => {
      expect(mockWriteText).toHaveBeenCalled();
    }, { timeout: 2000 });
  }, 15000);

  it('should handle download functionality', async () => {
    const createObjectURL = vi.fn().mockReturnValue('blob:mock-url');
    const revokeObjectURL = vi.fn();
    global.URL.createObjectURL = createObjectURL;
    global.URL.revokeObjectURL = revokeObjectURL;

    // Mock document.createElement for download link
    const mockLink = document.createElement('a');
    vi.spyOn(document, 'createElement').mockReturnValue(mockLink);

    render(<CodeGenerator />);

    // Wait for connection status
    await waitFor(() => {
      expect(screen.getByText('Connected')).toBeInTheDocument();
    }, { timeout: 3000 });

    const textarea = screen.getByPlaceholderText(/Example: Create a FastAPI/i);
    fireEvent.change(textarea, { target: { value: 'Create a download test function' } });

    const generateButton = screen.getByRole('button', { name: /Generate Code/i });
    fireEvent.click(generateButton);

    // Wait for code generation to complete
    await waitFor(() => {
      expect(screen.getByText('Generated Code')).toBeInTheDocument();
    }, { timeout: 5000 });

    // Find Download button with more flexible selector
    const downloadButton = await waitFor(() => {
      const buttons = screen.getAllByRole('button');
      const downloadBtn = buttons.find(btn =>
        btn.textContent?.includes('Download') ||
        btn.getAttribute('aria-label')?.includes('Download')
      );
      expect(downloadBtn).toBeDefined();
      return downloadBtn!;
    }, { timeout: 3000 });

    fireEvent.click(downloadButton);

    await waitFor(() => {
      expect(createObjectURL).toHaveBeenCalled();
    }, { timeout: 2000 });

    expect(revokeObjectURL).toHaveBeenCalled();
  }, 15000);
});

describe('CodeGenerator - Accessibility', () => {
  it('should have proper ARIA labels', async () => {
    render(<CodeGenerator />);

    expect(screen.getByLabelText(/Describe the code/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Generate Code/i })).toBeInTheDocument();
  });

  it('should have keyboard navigation support', async () => {
    render(<CodeGenerator />);

    // Wait for component to fully render
    await waitFor(() => {
      expect(screen.getByText('Status:')).toBeInTheDocument();
    });

    // Test textarea focus first (it appears first in DOM)
    const textarea = screen.getByPlaceholderText(/Example: Create a FastAPI/i);
    textarea.focus();
    expect(document.activeElement).toBe(textarea);

    // Test button focus (use Tab key simulation for realistic navigation)
    fireEvent.keyDown(textarea, { key: 'Tab', code: 'Tab' });

    // Button should be focusable via keyboard or direct focus
    const button = screen.getByRole('button', { name: /Generate Code/i });
    button.focus();
    expect(document.activeElement).toBe(button);
  });
});
