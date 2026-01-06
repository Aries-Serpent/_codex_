import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { CodeGenerator } from '../CodeGenerator';
import { CodexAPIClient } from '@/lib/codex-api-client';
import { MockCodexAPIClient } from '@/lib/mock-api-client';

vi.mock('@/lib/codex-api-client');
vi.mock('@/lib/mock-api-client');

describe('CodeGenerator - Lazy Initialization Pattern', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    delete import.meta.env.VITE_CODEX_KEY;
    delete import.meta.env.VITE_CODEX_API;
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
      vi.mocked(mockApiClient.getStatus).mockResolvedValue({
        healthy: true,
        metrics: { k1_factor: 0.312 },
      });

      render(<CodeGenerator />);

      await waitFor(() => {
        const button = screen.getByRole('button', { name: /Generate Code/i });
        expect(button).not.toBeDisabled();
      });
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
      expect(screen.getByText('API Status:')).toBeInTheDocument();
      expect(screen.getByLabelText(/Describe the code/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Generate Code/i })).toBeInTheDocument();
    });
  });

  describe('Test 5: Environment Configuration', () => {
    it('should handle different timing configurations', async () => {
      vi.useFakeTimers();

      const mockClient = new MockCodexAPIClient();
      vi.mocked(mockClient.getStatus).mockResolvedValue({
        healthy: true,
        metrics: { k1_factor: 0.312 },
      });

      render(<CodeGenerator />);

      await waitFor(() => {
        expect(screen.getByText('Connected')).toBeInTheDocument();
      });

      vi.advanceTimersByTime(30000);

      await waitFor(() => {
        expect(mockClient.getStatus).toHaveBeenCalledTimes(2);
      });

      vi.useRealTimers();
    });

    it('should handle different API URL configurations', async () => {
      import.meta.env.VITE_CODEX_API = 'https://api.example.com';
      import.meta.env.VITE_CODEX_KEY = 'test-key';

      const mockApiClient = new CodexAPIClient('https://api.example.com', 'test-key');
      vi.mocked(mockApiClient.getStatus).mockResolvedValue({
        healthy: true,
        metrics: { k1_factor: 0.312 },
      });

      render(<CodeGenerator />);

      await waitFor(() => {
        expect(mockApiClient.getStatus).toHaveBeenCalled();
      });
    });
  });

  describe('Component Structure Validation', () => {
    it('should have status indicator with correct states', async () => {
      render(<CodeGenerator />);

      const statusContainer = screen.getByText('API Status:').parentElement;
      expect(statusContainer).toBeInTheDocument();

      await waitFor(() => {
        const dot = statusContainer?.querySelector('.w-2.h-2.rounded-full');
        expect(dot).toBeInTheDocument();
      });
    });

    it('should have textarea with validation styling', async () => {
      render(<CodeGenerator />);

      const textarea = screen.getByPlaceholderText(/Example: Create a FastAPI/i);
      expect(textarea).toHaveClass('font-mono', 'resize-none');

      fireEvent.change(textarea, { target: { value: 'Hi' } });

      await waitFor(() => {
        expect(textarea).toHaveClass('border-destructive');
      });
    });

    it('should have Generate button with proper states', async () => {
      render(<CodeGenerator />);

      const button = screen.getByRole('button', { name: /Generate Code/i });
      expect(button).toBeInTheDocument();

      const icon = button.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });
  });
});

describe('CodeGenerator - Real Workflows', () => {
  it('should generate code successfully in demo mode', async () => {
    const mockClient = new MockCodexAPIClient();
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
    });

    const textarea = screen.getByPlaceholderText(/Example: Create a FastAPI/i);
    fireEvent.change(textarea, { target: { value: 'Create a hello world function' } });

    const button = screen.getByRole('button', { name: /Generate Code/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('Generated Code')).toBeInTheDocument();
      expect(screen.getByText(/def hello_world/i)).toBeInTheDocument();
    });
  });

  it('should handle copy functionality', async () => {
    const mockClient = new MockCodexAPIClient();
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

    Object.assign(navigator, {
      clipboard: {
        writeText: vi.fn().mockResolvedValue(undefined),
      },
    });

    render(<CodeGenerator />);

    const textarea = screen.getByPlaceholderText(/Example: Create a FastAPI/i);
    fireEvent.change(textarea, { target: { value: 'Create a test function' } });

    const generateButton = screen.getByRole('button', { name: /Generate Code/i });
    fireEvent.click(generateButton);

    await waitFor(() => {
      expect(screen.getByText('Generated Code')).toBeInTheDocument();
    });

    const copyButton = screen.getByRole('button', { name: /Copy/i });
    fireEvent.click(copyButton);

    expect(navigator.clipboard.writeText).toHaveBeenCalledWith('def test():\n    pass');
  });

  it('should handle download functionality', async () => {
    const mockClient = new MockCodexAPIClient();
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

    render(<CodeGenerator />);

    const textarea = screen.getByPlaceholderText(/Example: Create a FastAPI/i);
    fireEvent.change(textarea, { target: { value: 'Create a download test function' } });

    const generateButton = screen.getByRole('button', { name: /Generate Code/i });
    fireEvent.click(generateButton);

    await waitFor(() => {
      expect(screen.getByText('Generated Code')).toBeInTheDocument();
    });

    const downloadButton = screen.getByRole('button', { name: /Download/i });
    fireEvent.click(downloadButton);

    expect(createObjectURL).toHaveBeenCalled();
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

    const textarea = screen.getByPlaceholderText(/Example: Create a FastAPI/i);
    textarea.focus();
    expect(document.activeElement).toBe(textarea);

    const button = screen.getByRole('button', { name: /Generate Code/i });
    button.focus();
    expect(document.activeElement).toBe(button);
  });
});
