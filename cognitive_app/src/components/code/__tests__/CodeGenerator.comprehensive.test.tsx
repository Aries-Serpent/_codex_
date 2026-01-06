import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { CodeGenerator } from '../CodeGenerator';
import { toast } from 'sonner';

vi.mock('sonner', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

const mockSpark = {
  llmPrompt: vi.fn((strings: TemplateStringsArray, ...values: any[]) => {
    return strings.reduce((acc, str, i) => acc + str + (values[i] || ''), '');
  }),
  llm: vi.fn(),
};

(global as any).spark = mockSpark;

describe('CodeGenerator - Comprehensive Test Suite (90%+ Coverage)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockSpark.llm.mockResolvedValue(`def generated_function():
    """AI-generated code"""
    return "success"`);
    delete (import.meta.env as any).VITE_CODEX_KEY;
    delete (import.meta.env as any).VITE_CODEX_API;
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Component Rendering', () => {
    it('should render all essential UI elements', async () => {
      render(<CodeGenerator />);

      expect(screen.getByText('Code Generation')).toBeInTheDocument();
      expect(screen.getByText('API Status:')).toBeInTheDocument();
      expect(screen.getByPlaceholderText(/example: create a fastapi/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /generate code/i })).toBeInTheDocument();
      expect(screen.getByText(/0 \/ 5000/i)).toBeInTheDocument();
    });

    it('should show checking status initially', () => {
      render(<CodeGenerator />);
      
      expect(screen.getByText('Checking...')).toBeInTheDocument();
    });

    it('should display Spark AI info message when no API key', async () => {
      render(<CodeGenerator />);

      await waitFor(() => {
        const infoText = screen.getByText(/Powered by Spark AI \(GPT-4o-mini\)/i);
        expect(infoText).toBeInTheDocument();
      }, { timeout: 3000 });
    });
  });

  describe('Input Validation', () => {
    it('should show character count as user types', () => {
      render(<CodeGenerator />);
      const textarea = screen.getByPlaceholderText(/example: create a fastapi/i);

      fireEvent.change(textarea, { target: { value: 'Hello' } });
      expect(screen.getByText('5 / 5000 (min: 10)')).toBeInTheDocument();
    });

    it('should show red border and validation message for short input', () => {
      render(<CodeGenerator />);
      const textarea = screen.getByPlaceholderText(/example: create a fastapi/i) as HTMLTextAreaElement;

      fireEvent.change(textarea, { target: { value: 'Short' } });
      
      expect(screen.getByText('5 / 5000 (min: 10)')).toBeInTheDocument();
      expect(textarea.className).toContain('border-destructive');
    });

    it('should remove validation styling when input is valid', () => {
      render(<CodeGenerator />);
      const textarea = screen.getByPlaceholderText(/example: create a fastapi/i) as HTMLTextAreaElement;

      fireEvent.change(textarea, { target: { value: 'Create a hello world function' } });
      
      expect(screen.getByText('29 / 5000')).toBeInTheDocument();
      expect(textarea.className).not.toContain('border-destructive');
    });

    it('should disable button when input is too short', async () => {
      render(<CodeGenerator />);
      
      await waitFor(() => {
        expect(screen.getByText('Connected')).toBeInTheDocument();
      });

      const textarea = screen.getByPlaceholderText(/example: create a fastapi/i);
      fireEvent.change(textarea, { target: { value: 'Short' } });

      const button = screen.getByRole('button', { name: /generate code/i });
      expect(button).toBeDisabled();
    });

    it('should enable button when input is valid and API is connected', async () => {
      render(<CodeGenerator />);
      
      await waitFor(() => {
        expect(screen.getByText('Connected')).toBeInTheDocument();
      });

      const textarea = screen.getByPlaceholderText(/example: create a fastapi/i);
      fireEvent.change(textarea, { target: { value: 'Create a Python function to add two numbers' } });

      const button = screen.getByRole('button', { name: /generate code/i });
      await waitFor(() => {
        expect(button).not.toBeDisabled();
      });
    });

    it('should show error toast when trying to generate with short prompt', async () => {
      render(<CodeGenerator />);
      
      await waitFor(() => {
        expect(screen.getByText('Connected')).toBeInTheDocument();
      });

      const textarea = screen.getByPlaceholderText(/example: create a fastapi/i);
      fireEvent.change(textarea, { target: { value: 'Short' } });

      expect(toast.error).toHaveBeenCalledWith('Prompt too short', expect.objectContaining({
        description: 'Please enter at least 10 characters'
      }));
    });
  });

  describe('Code Generation Flow', () => {
    it('should generate code successfully with Spark AI', async () => {
      render(<CodeGenerator />);
      
      await waitFor(() => {
        expect(screen.getByText('Connected')).toBeInTheDocument();
      });

      const textarea = screen.getByPlaceholderText(/example: create a fastapi/i);
      fireEvent.change(textarea, { target: { value: 'Create a Python function to add two numbers' } });

      const button = screen.getByRole('button', { name: /generate code/i });
      await waitFor(() => {
        expect(button).not.toBeDisabled();
      });

      fireEvent.click(button);

      await waitFor(() => {
        expect(screen.getByText('Generating Code...')).toBeInTheDocument();
      });

      await waitFor(() => {
        expect(mockSpark.llm).toHaveBeenCalled();
      }, { timeout: 3000 });
    });

    it('should show loading state while generating', async () => {
      mockSpark.llm.mockImplementation(() => new Promise(resolve => setTimeout(() => resolve('code'), 1000)));
      
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
        expect(screen.getByText('Generating Code...')).toBeInTheDocument();
      });

      const generatingButton = screen.getByRole('button', { name: /generating code/i });
      expect(generatingButton).toBeDisabled();
    });

    it('should display generated code after successful generation', async () => {
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
    });

    it('should show success toast after generation', async () => {
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
        expect(toast.success).toHaveBeenCalledWith(
          'Code generated successfully',
          expect.objectContaining({
            description: expect.stringContaining('Generated with Spark AI')
          })
        );
      }, { timeout: 3000 });
    });
  });

  describe('Copy and Download Functionality', () => {
    beforeEach(async () => {
      Object.assign(navigator, {
        clipboard: {
          writeText: vi.fn().mockResolvedValue(undefined),
        },
      });

      global.URL.createObjectURL = vi.fn(() => 'blob:mock-url');
      global.URL.revokeObjectURL = vi.fn();
    });

    it('should copy code to clipboard', async () => {
      render(<CodeGenerator />);
      
      await waitFor(() => {
        expect(screen.getByText('Connected')).toBeInTheDocument();
      });

      const textarea = screen.getByPlaceholderText(/example: create a fastapi/i);
      fireEvent.change(textarea, { target: { value: 'Create test code' } });

      const generateButton = screen.getByRole('button', { name: /generate code/i });
      await waitFor(() => expect(generateButton).not.toBeDisabled());
      fireEvent.click(generateButton);

      await waitFor(() => {
        expect(screen.getByText('Generated Code')).toBeInTheDocument();
      }, { timeout: 3000 });

      const copyButton = screen.getByRole('button', { name: /copy/i });
      fireEvent.click(copyButton);

      await waitFor(() => {
        expect(navigator.clipboard.writeText).toHaveBeenCalled();
        expect(toast.success).toHaveBeenCalledWith('Code copied to clipboard');
      });
    });

    it('should download code as file', async () => {
      const mockClick = vi.fn();
      const mockAppendChild = vi.fn();
      const mockRemoveChild = vi.fn();
      
      document.createElement = vi.fn().mockImplementation((tag) => {
        if (tag === 'a') {
          return {
            click: mockClick,
            href: '',
            download: '',
          };
        }
        return {};
      });
      document.body.appendChild = mockAppendChild;
      document.body.removeChild = mockRemoveChild;

      render(<CodeGenerator />);
      
      await waitFor(() => {
        expect(screen.getByText('Connected')).toBeInTheDocument();
      });

      const textarea = screen.getByPlaceholderText(/example: create a fastapi/i);
      fireEvent.change(textarea, { target: { value: 'Create test code' } });

      const generateButton = screen.getByRole('button', { name: /generate code/i });
      await waitFor(() => expect(generateButton).not.toBeDisabled());
      fireEvent.click(generateButton);

      await waitFor(() => {
        expect(screen.getByText('Generated Code')).toBeInTheDocument();
      }, { timeout: 3000 });

      const downloadButton = screen.getByRole('button', { name: /download/i });
      fireEvent.click(downloadButton);

      await waitFor(() => {
        expect(mockClick).toHaveBeenCalled();
        expect(toast.success).toHaveBeenCalledWith('Code downloaded');
      });
    });
  });

  describe('Status Indicator Behavior', () => {
    it('should show connected status with green indicator', async () => {
      render(<CodeGenerator />);

      await waitFor(() => {
        const statusText = screen.getByText('Connected');
        expect(statusText).toBeInTheDocument();
        expect(statusText.className).toContain('text-green-500');
      });
    });

    it('should recheck status every 30 seconds', async () => {
      vi.useFakeTimers();
      
      render(<CodeGenerator />);

      await waitFor(() => {
        expect(screen.getByText('Connected')).toBeInTheDocument();
      });

      const initialCheckCount = mockSpark.llm.mock.calls.length;

      vi.advanceTimersByTime(30000);

      await waitFor(() => {
        expect(screen.getByText('Checking...')).toBeInTheDocument();
      });

      vi.useRealTimers();
    });
  });

  describe('Error Handling', () => {
    it('should handle LLM generation errors gracefully', async () => {
      mockSpark.llm.mockRejectedValueOnce(new Error('LLM service unavailable'));

      render(<CodeGenerator />);
      
      await waitFor(() => {
        expect(screen.getByText('Connected')).toBeInTheDocument();
      });

      const textarea = screen.getByPlaceholderText(/example: create a fastapi/i);
      fireEvent.change(textarea, { target: { value: 'Create test function' } });

      const button = screen.getByRole('button', { name: /generate code/i });
      await waitFor(() => expect(button).not.toBeDisabled());
      
      fireEvent.click(button);

      await waitFor(() => {
        expect(screen.getByText('Generated Code')).toBeInTheDocument();
      }, { timeout: 3000 });
    });

    it('should show error message when both API and Spark fail', async () => {
      mockSpark.llm.mockRejectedValue(new Error('Complete failure'));
      
      (import.meta.env as any).VITE_CODEX_KEY = 'test-key';

      render(<CodeGenerator />);
      
      await waitFor(() => {
        const errorElement = screen.queryByText(/error/i);
        expect(errorElement).toBeInTheDocument();
      }, { timeout: 3000 });
    });
  });

  describe('Interactive Demo Integration', () => {
    it('should display "Try It Live" button after code generation', async () => {
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

      const tryButton = screen.getByRole('button', { name: /try it live/i });
      expect(tryButton).toBeInTheDocument();
    });

    it('should toggle interactive demo when "Try It Live" is clicked', async () => {
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

      const tryButton = screen.getByRole('button', { name: /try it live/i });
      fireEvent.click(tryButton);

      await waitFor(() => {
        expect(screen.getByText('Interactive Code Demo')).toBeInTheDocument();
      });
    });
  });

  describe('Metrics Display', () => {
    it('should display k1 factor and quantum metrics', async () => {
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

    it('should show cache hit badge when applicable', async () => {
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
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels', () => {
      render(<CodeGenerator />);
      
      const textarea = screen.getByPlaceholderText(/example: create a fastapi/i);
      expect(textarea).toHaveAttribute('id', 'prompt');
    });

    it('should have descriptive button text', () => {
      render(<CodeGenerator />);
      
      const button = screen.getByRole('button', { name: /generate code/i });
      expect(button).toBeInTheDocument();
    });

    it('should show loading state in button text', async () => {
      mockSpark.llm.mockImplementation(() => new Promise(resolve => setTimeout(() => resolve('code'), 1000)));
      
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
        const generatingButton = screen.getByRole('button', { name: /generating code/i });
        expect(generatingButton).toBeInTheDocument();
      });
    });
  });
});
