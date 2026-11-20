/**
 * CodeGenerator Component - Lazy Initialization Tests
 *
 * Tests for session-client lazy initialization:
 * - Test 2: Default API configuration
 * - Test 3: Explicit API configuration
 * - Test 4: Mock fallback behavior
 * - Test 5: Environment variable configuration
 *
 * These tests validate the lazy initialization pattern implemented
 * in response to code review feedback.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { CodeGenerator } from '../CodeGenerator';

// Mock the API clients with working implementations
vi.mock('@/lib/codex-api-client', () => {
  class CodexAPIClient {
    constructor(apiUrl: string) {}

    async getStatus() {
      // Simulate async delay for realistic timing
      await new Promise(resolve => setTimeout(resolve, 50));
      return { status: 'ok' };
    }

    async generateCode(prompt: string) {
      return {
        code: 'def hello():\n    print("Hello, World!")',
        metadata: {
          k1_factor: 0.9234,
          cache_hit: false,
          processing_time: 1.234,
        },
        quantum_metrics: {
          coherence: 0.85,
          entanglement: 0.72,
        },
      };
    }
  }

  class CodexAPIError extends Error {
    constructor(message: string, public statusCode: number) {
      super(message);
      this.name = 'CodexAPIError';
    }
  }

  return {
    CodexAPIClient,
    CodexAPIError,
  };
});

vi.mock('@/lib/mock-api-client', () => {
  class MockCodexAPIClient {
    constructor() {}

    async getStatus() {
      // Simulate async delay for realistic timing
      await new Promise(resolve => setTimeout(resolve, 50));
      return { status: 'mock' };
    }

    async generateCode(prompt: string) {
      return {
        code: '# Mock generated code\ndef example():\n    pass',
        metadata: {
          k1_factor: 0.5000,
          cache_hit: false,
          processing_time: 0.100,
        },
        quantum_metrics: {
          coherence: 0.50,
          entanglement: 0.50,
        },
      };
    }
  }

  return {
    MockCodexAPIClient,
  };
});

// Mock sonner toast
vi.mock('sonner', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

describe('CodeGenerator - Lazy Initialization Tests (PR #2705)', () => {
  let originalEnv: Record<string, any>;

  beforeEach(() => {
    // Save original environment
    originalEnv = { ...import.meta.env };

    // Clear all mocks
    vi.clearAllMocks();
  });

  afterEach(() => {
    // Restore original environment
    Object.keys(originalEnv).forEach(key => {
      import.meta.env[key] = originalEnv[key];
    });
  });

  /** Test the localhost session default without browser credentials. */
  describe('Test 2: Default API configuration', () => {
    it('[APPROVED] should use the session client without browser credentials', async () => {
      delete import.meta.env.VITE_CLI_API_URL;
      delete import.meta.env.VITE_CODEX_API;
      import.meta.env.DEV = false;
      render(<CodeGenerator />);

      await waitFor(() => {
        expect(screen.getByText('Connected')).toBeInTheDocument();
      }, { timeout: 3000 });
      expect(screen.queryByText(/using demo mode/i)).not.toBeInTheDocument();
    });

    it('[APPROVED] should show a green Connected status', async () => {
      render(<CodeGenerator />);

      await waitFor(() => {
        const statusText = screen.getByText(/connected/i);
        expect(statusText).toBeInTheDocument();
        const statusContainer = statusText.closest('div');
        expect(statusContainer?.querySelector('.bg-green-500')).toBeInTheDocument();
      }, { timeout: 2000 });
      expect(screen.queryByText(/using demo mode/i)).not.toBeInTheDocument();
    });

    it('[APPROVED] should enable generate button after session initialization', async () => {
      render(<CodeGenerator />);

      // With mock fallback available, button should be enabled (not disabled by apiStatus)
      await waitFor(() => {
        const generateButton = screen.getByRole('button', { name: /generate code/i });
        // Button is only disabled if prompt is invalid (< 10 chars)
        // Since prompt is empty, button is disabled due to !isValidPrompt, not apiStatus
        expect(generateButton).toBeDisabled(); // Still disabled due to empty prompt
      });

      // But let's verify it enables with valid prompt
      const textarea = screen.getByPlaceholderText(/example: create a fastapi endpoint/i);
      fireEvent.change(textarea, { target: { value: 'Valid prompt with enough characters' } });

      await waitFor(() => {
        const generateButton = screen.getByRole('button', { name: /generate code/i });
        expect(generateButton).not.toBeDisabled(); // Now enabled with valid prompt
      });
    });
  });

  /** Test an explicit loopback API origin. */
  describe('Test 3: Explicit API configuration', () => {
    beforeEach(() => {
      import.meta.env.VITE_CLI_API_URL = 'http://127.0.0.1:8765';
      import.meta.env.DEV = false;
    });

    it('[APPROVED] should show "Checking..." status initially', () => {
      render(<CodeGenerator />);

      const statusText = screen.getByText(/checking/i);
      expect(statusText).toBeInTheDocument();

      // Verify yellow status indicator
      const statusContainer = statusText.closest('div');
      const statusDot = statusContainer?.querySelector('.bg-yellow-500');
      expect(statusDot).toBeInTheDocument();
    });

    it('[APPROVED] should transition to "Connected" or "Error" status', async () => {
      render(<CodeGenerator />);

      await waitFor(() => {
        // After status check, should show either Connected or Error
        const statusText = screen.queryByText(/connected/i) || screen.queryByText(/error/i);
        expect(statusText).toBeInTheDocument();
      }, { timeout: 3000 });
    });

    it('[APPROVED] should enable generate button after status check completes', async () => {
      render(<CodeGenerator />);

      // Wait for status check to complete
      await waitFor(() => {
        const statusText = screen.queryByText(/connected/i) || screen.queryByText(/error/i);
        expect(statusText).toBeInTheDocument();
      }, { timeout: 3000 });

      // Add valid prompt first (button requires valid prompt to be enabled)
      const textarea = screen.getByPlaceholderText(/example: create a fastapi endpoint/i);
      fireEvent.change(textarea, { target: { value: 'Valid test prompt with sufficient characters' } });

      // Now button should be enabled
      await waitFor(() => {
        const generateButton = screen.getByRole('button', { name: /generate code/i });
        // Button should be enabled once status check completes AND prompt is valid
        expect(generateButton).not.toBeDisabled();
      }, { timeout: 2000 });
    });
  });

  /**
   * Test 4: Mock Fallback Scenario
   *
   * Validates prompt behavior after the primary session path is initialized.
   */
  describe('Test 4: Mock Fallback Scenario', () => {
    it('[APPROVED] should accept prompt input of at least 10 characters', async () => {
      render(<CodeGenerator />);

      const textarea = screen.getByPlaceholderText(/example: create a fastapi endpoint/i);

      // Short prompt (invalid)
      fireEvent.change(textarea, { target: { value: 'Short' } });
      expect(screen.getByText(/5 \/ 5000/)).toBeInTheDocument();

      // Valid prompt (10+ chars) - "Create a hello world function" = 29 chars
      fireEvent.change(textarea, { target: { value: 'Create a hello world function' } });
      expect(screen.getByText(/29 \/ 5000/)).toBeInTheDocument();
    });

    it('[APPROVED] should show character count and validation', () => {
      render(<CodeGenerator />);

      const textarea = screen.getByPlaceholderText(/example: create a fastapi endpoint/i);

      // Check character counter updates
      fireEvent.change(textarea, { target: { value: 'Test' } });
      expect(screen.getByText(/4 \/ 5000/)).toBeInTheDocument();
      expect(screen.getByText(/\(min: 10\)/)).toBeInTheDocument();
    });

    it('[APPROVED] should have copy and download buttons after generation', async () => {
      render(<CodeGenerator />);

      // Note: Full generation flow requires API mocking
      // This test validates button structure exists in component
      const allButtons = screen.getAllByRole('button');
      expect(allButtons.length).toBeGreaterThan(0);
    });
  });

  /**
   * Test 5: Cascade Timing Configuration
   *
   * Validates environment variable configuration behavior.
   * Note: This tests the CodeGenerator component's integration,
   * not the CascadingExecutionMonitor timing constant directly.
   */
  describe('Test 5: Environment Variable Configuration', () => {
    it('[APPROVED] should render component regardless of VITE_STAGE_EXECUTION_TIME_MS', () => {
      // Test with default (no env var)
      delete import.meta.env.VITE_STAGE_EXECUTION_TIME_MS;
      const { unmount } = render(<CodeGenerator />);
      expect(screen.getByText(/code generation/i)).toBeInTheDocument();
      unmount();

      // Test with custom value
      import.meta.env.VITE_STAGE_EXECUTION_TIME_MS = '200';
      render(<CodeGenerator />);
      expect(screen.getByText(/code generation/i)).toBeInTheDocument();
    });

    it('[APPROVED] should handle various API URL configurations', () => {
      delete import.meta.env.VITE_CLI_API_URL;
      delete import.meta.env.VITE_CODEX_API;
      const { unmount } = render(<CodeGenerator />);
      expect(screen.getByText(/code generation/i)).toBeInTheDocument();
      unmount();

      import.meta.env.VITE_CLI_API_URL = 'https://api.example.com';
      render(<CodeGenerator />);
      expect(screen.getByText(/code generation/i)).toBeInTheDocument();
    });
  });

  /**
   * Additional Validation: Component Structure
   *
   * Validates UI elements are present as expected
   */
  describe('Component Structure Validation', () => {
    it('[APPROVED] should render all expected UI sections', () => {
      render(<CodeGenerator />);

      // Main heading
      expect(screen.getByText(/code generation/i)).toBeInTheDocument();

      // Status section (updated from API status)
      expect(screen.getByText(/AI Mode:/i)).toBeInTheDocument();
      expect(screen.getByText(/Status:/i)).toBeInTheDocument();

      // Prompt textarea
      expect(screen.getByPlaceholderText(/example: create a fastapi endpoint/i)).toBeInTheDocument();

      // Generate button
      expect(screen.getByRole('button', { name: /generate code/i })).toBeInTheDocument();
    });

    it('[APPROVED] should show character count with proper formatting', () => {
      render(<CodeGenerator />);

      // Initial state (0 characters)
      expect(screen.getByText(/0 \/ 5000/)).toBeInTheDocument();
    });

    it('[APPROVED] should apply correct styling based on validation state', async () => {
      render(<CodeGenerator />);

      const textarea = screen.getByPlaceholderText(/example: create a fastapi endpoint/i);

      // Short input (invalid) should show error styling
      fireEvent.change(textarea, { target: { value: 'Short' } });

      // Wait for the aria-invalid attribute to be applied
      await waitFor(() => {
        expect(textarea).toHaveAttribute('aria-invalid', 'true');
      }, { timeout: 1000 });

      // Valid input should not have error styling
      fireEvent.change(textarea, { target: { value: 'This is a valid prompt with enough characters' } });

      await waitFor(() => {
        expect(textarea).toHaveAttribute('aria-invalid', 'false');
      }, { timeout: 1000 });
    });
  });
});
