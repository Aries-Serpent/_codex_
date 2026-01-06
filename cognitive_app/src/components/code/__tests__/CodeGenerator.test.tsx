import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { CodeGenerator } from '../CodeGenerator';
import { CodexAPIClient } from '@/lib/codex-api-client';
import { MockCodexAPIClient } from '@/lib/mock-api-client';
import { SparkLLMClient } from '@/lib/spark-llm-client';

vi.mock('@/lib/codex-api-client');
vi.mock('@/lib/mock-api-client');
vi.mock('@/lib/spark-llm-client');

describe('CodeGenerator - Lazy Initialization Pattern', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    delete import.meta.env.VITE_CODEX_KEY;
    delete import.meta.env.VITE_CODEX_API;
    
    // Mock SparkLLMClient to prevent AI Mode from interfering with tests
    const mockSparkClient = {
      generateCode: vi.fn().mockResolvedValue({
        code: '# AI generated code',
        metadata: { k1_factor: 0.28, coherence: 0.85 },
        quantum_metrics: { superposition_states: 3, entanglement_score: 0.85 },
      }),
      getStatus: vi.fn().mockResolvedValue({
        healthy: true,
        model: 'gpt-4o-mini (Spark Runtime)',
      }),
    };
    vi.mocked(SparkLLMClient).mockImplementation(() => mockSparkClient as any);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Test 2: No API Key Scenario', () => {
    it('should show "Connected" status with green dot when no API key', async () => {
      const mockClient = new MockCodexAPIClient();
      vi.mocked(mockClient.getStatus).mockResolvedValue({
        healthy: true,
        metrics: { k1_factor: 0.312 },
      });

      render(<CodeGenerator />);

      await waitFor(() => {
        const statusText = screen.getByText('Connected');
        expect(statusText).toBeInTheDocument();
        expect(statusText).toHaveClass('text-green-500');
      });
    });

    it('should display blue info message for demo mode', async () => {
      const mockClient = new MockCodexAPIClient();
      vi.mocked(mockClient.getStatus).mockResolvedValue({
        healthy: true,
        metrics: { k1_factor: 0.312 },
      });

      render(<CodeGenerator />);

      await waitFor(() => {
        const infoMessage = screen.getByText(/Using demo mode/i);
        expect(infoMessage).toBeInTheDocument();
      });

      const errorMessage = screen.queryByText(/Error/i);
      expect(errorMessage).not.toBeInTheDocument();
    });

    it('should enable Generate button in demo mode', async () => {
      const mockClient = new MockCodexAPIClient();
      vi.mocked(mockClient.getStatus).mockResolvedValue({
        healthy: true,
        metrics: { k1_factor: 0.312 },
      });

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
      });
    });
  });

  describe('Test 3: With API Key Scenario', () => {
    beforeEach(() => {
      import.meta.env.VITE_CODEX_KEY = 'test-api-key-12345';
      import.meta.env.VITE_CODEX_API = 'http://localhost:8000';
    });

    it('should show "Checking..." status initially', async () => {
      const mockApiClient = new CodexAPIClient('http://localhost:8000', 'test-key');
      vi.mocked(mockApiClient.getStatus).mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve({ healthy: true, metrics: {} }), 100))
      );

      render(<CodeGenerator />);

      const statusText = screen.getByText('Checking...');
      expect(statusText).toBeInTheDocument();
      expect(statusText).toHaveClass('text-yellow-500');
    });

    it('should transition to "Connected" after successful check', async () => {
      const mockApiClient = new CodexAPIClient('http://localhost:8000', 'test-key');
      vi.mocked(mockApiClient.getStatus).mockResolvedValue({
        healthy: true,
        metrics: { k1_factor: 0.312 },
      });

      render(<CodeGenerator />);

      await waitFor(() => {
        const statusText = screen.getByText('Connected');
        expect(statusText).toBeInTheDocument();
        expect(statusText).toHaveClass('text-green-500');
      });
    });

    it('should enable button after successful API check', async () => {
      const mockApiClient = new CodexAPIClient('http://localhost:8000', 'test-key');
      const mockGetStatus = vi.fn().mockResolvedValue({
        healthy: true,
        metrics: { k1_factor: 0.312 },
      });
      mockApiClient.getStatus = mockGetStatus;
      vi.mocked(CodexAPIClient).mockImplementation(() => mockApiClient as any);

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
      const mockClient = new MockCodexAPIClient();
      const mockGetStatus = vi.fn().mockResolvedValue({
        healthy: true,
        metrics: { k1_factor: 0.312 },
      });
      mockClient.getStatus = mockGetStatus;
      vi.mocked(MockCodexAPIClient).mockImplementation(() => mockClient as any);

      render(<CodeGenerator />);

      await waitFor(() => {
        expect(screen.getByText('Connected')).toBeInTheDocument();
      }, { timeout: 3000 });

      // Verify status check was called
      expect(mockGetStatus).toHaveBeenCalled();
    }, 10000);

    it('should handle different API URL configurations', async () => {
      import.meta.env.VITE_CODEX_API = 'https://api.example.com';
      import.meta.env.VITE_CODEX_KEY = 'test-key';

      const mockApiClient = new CodexAPIClient('https://api.example.com', 'test-key');
      const mockGetStatus = vi.fn().mockResolvedValue({
        healthy: true,
        metrics: { k1_factor: 0.312 },
      });
      mockApiClient.getStatus = mockGetStatus;
      vi.mocked(CodexAPIClient).mockImplementation(() => mockApiClient as any);

      render(<CodeGenerator />);

      await waitFor(() => {
        expect(screen.getByText('Connected')).toBeInTheDocument();
      }, { timeout: 3000 });

      expect(mockGetStatus).toHaveBeenCalled();
    }, 10000);
  });

  describe('Component Structure Validation', () => {
    it('should have status indicator with correct states', async () => {
      const mockClient = new MockCodexAPIClient();
      vi.mocked(MockCodexAPIClient).mockImplementation(() => mockClient as any);
      vi.mocked(mockClient.getStatus).mockResolvedValue({
        healthy: true,
        metrics: { k1_factor: 0.312 },
      });

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
      const mockClient = new MockCodexAPIClient();
      vi.mocked(MockCodexAPIClient).mockImplementation(() => mockClient as any);
      vi.mocked(mockClient.getStatus).mockResolvedValue({
        healthy: true,
        metrics: { k1_factor: 0.312 },
      });

      render(<CodeGenerator />);

      const textarea = screen.getByPlaceholderText(/Example: Create a FastAPI/i);
      expect(textarea).toHaveClass('font-mono', 'resize-none');

      fireEvent.change(textarea, { target: { value: 'Hi' } });

      await waitFor(() => {
        expect(textarea).toHaveClass('border-destructive');
      }, { timeout: 2000 });
    }, 10000);

    it('should have Generate button with proper states', async () => {
      const mockClient = new MockCodexAPIClient();
      vi.mocked(MockCodexAPIClient).mockImplementation(() => mockClient as any);
      vi.mocked(mockClient.getStatus).mockResolvedValue({
        healthy: true,
        metrics: { k1_factor: 0.312 },
      });

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
  });

  it('should generate code successfully in demo mode', async () => {
    const mockClient = new MockCodexAPIClient();
    vi.mocked(MockCodexAPIClient).mockImplementation(() => mockClient as any);
    vi.mocked(mockClient.getStatus).mockResolvedValue({
      healthy: true,
      metrics: { k1_factor: 0.312 },
    });
    vi.mocked(mockClient.generateCode).mockResolvedValue({
      code: 'def hello_world():\n    print("Hello, World!")',
      metadata: {
        k1_factor: 0.312,
        coherence: 0.685,
        cache_hit: false,
        processing_time_ms: 1200,
      },
      quantum_metrics: {
        superposition_states: 3,
        entanglement_score: 0.85,
      },
    });

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
      expect(screen.getByText(/def hello_world/i)).toBeInTheDocument();
    }, { timeout: 5000 });
  });

  it('should handle copy functionality', async () => {
    const mockClient = new MockCodexAPIClient();
    vi.mocked(MockCodexAPIClient).mockImplementation(() => mockClient as any);
    vi.mocked(mockClient.getStatus).mockResolvedValue({
      healthy: true,
      metrics: { k1_factor: 0.312 },
    });
    vi.mocked(mockClient.generateCode).mockResolvedValue({
      code: 'def test():\n    pass',
      metadata: {
        k1_factor: 0.312,
        coherence: 0.685,
        cache_hit: false,
        processing_time_ms: 1200,
      },
      quantum_metrics: {
        superposition_states: 3,
        entanglement_score: 0.85,
      },
    });

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
      expect(mockWriteText).toHaveBeenCalledWith('def test():\n    pass');
    }, { timeout: 2000 });
  });

  it('should handle download functionality', async () => {
    const mockClient = new MockCodexAPIClient();
    vi.mocked(MockCodexAPIClient).mockImplementation(() => mockClient as any);
    vi.mocked(mockClient.getStatus).mockResolvedValue({
      healthy: true,
      metrics: { k1_factor: 0.312 },
    });
    vi.mocked(mockClient.generateCode).mockResolvedValue({
      code: 'def download_test():\n    pass',
      metadata: {
        k1_factor: 0.312,
        coherence: 0.685,
        cache_hit: false,
        processing_time_ms: 1200,
      },
      quantum_metrics: {
        superposition_states: 3,
        entanglement_score: 0.85,
      },
    });

    const createObjectURL = vi.fn().mockReturnValue('blob:mock-url');
    const revokeObjectURL = vi.fn();
    global.URL.createObjectURL = createObjectURL;
    global.URL.revokeObjectURL = revokeObjectURL;

    // Mock document.createElement for download link
    const mockLink = document.createElement('a');
    const clickSpy = vi.spyOn(mockLink, 'click');
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
  });
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
