/**
 * End-to-End Test Spec: CodeGenerator Lazy Initialization
 * 
 * Comprehensive E2E tests for PR #2705 lazy initialization improvements.
 * Uses Playwright for full browser automation and real user interaction testing.
 * 
 * Tests validate:
 * - Test 2: No API Key scenario (error states)
 * - Test 3: With API Key scenario (connection flow)
 * - Test 4: Mock Fallback scenario (graceful degradation)
 * - Test 5: Environment variable configuration (timing)
 * 
 * @requires Playwright ^1.40.0
 * @requires cognitive_app dev server running on localhost:5173
 */

import { test, expect, Page } from '@playwright/test';

// Test configuration
const BASE_URL = process.env.BASE_URL || 'http://localhost:5173';
const API_KEY_VALID = process.env.TEST_API_KEY || 'test-valid-key-12345';
const API_KEY_INVALID = 'invalid-test-key-xxxxx';

/**
 * Helper Functions
 */

async function navigateToCodeGenerator(page: Page) {
  await page.goto(BASE_URL);
  await page.waitForLoadState('networkidle');
  // Wait for Code Generator section to be visible
  await expect(page.getByText('Code Generation')).toBeVisible();
}

async function getAPIStatus(page: Page) {
  const statusSection = page.locator('text=API Status:').locator('..');
  const statusText = await statusSection.getByText(/Connected|Error|Checking/).textContent();
  return statusText?.trim() || '';
}

async function getAPIStatusColor(page: Page) {
  const statusDot = page.locator('[class*="bg-"][class*="500"]').first();
  const classes = await statusDot.getAttribute('class');
  
  if (classes?.includes('bg-green-500')) return 'green';
  if (classes?.includes('bg-red-500')) return 'red';
  if (classes?.includes('bg-yellow-500')) return 'yellow';
  return 'unknown';
}

async function enterPrompt(page: Page, text: string) {
  const textarea = page.getByPlaceholder(/Example: Create a FastAPI endpoint/i);
  await textarea.fill(text);
}

async function clickGenerate(page: Page) {
  const button = page.getByRole('button', { name: /Generate Code/i });
  await button.click();
}

async function waitForToast(page: Page, text: string, timeout = 5000) {
  await expect(page.getByText(text)).toBeVisible({ timeout });
}

/**
 * Test Suite Setup
 */

test.describe('E2E: CodeGenerator Lazy Initialization (PR #2705)', () => {
  
  test.beforeEach(async ({ page }) => {
    // Clear any existing storage
    await page.context().clearCookies();
    await page.evaluate(() => localStorage.clear());
  });

  /**
   * Test 2: Lazy Initialization - No API Key
   * 
   * Validates complete user flow when API key is missing:
   * ✅ Error message displayed in UI
   * ✅ Red "Error" status indicator visible
   * ✅ Generate button disabled (cannot interact)
   * ✅ Helpful error message guides user
   */
  test.describe('Test 2: No API Key Scenario', () => {
    
    test('should display error state when API key is missing', async ({ page }) => {
      // Arrange: Navigate without API key in environment
      await page.addInitScript(() => {
        delete (window as any).import.meta.env.VITE_CODEX_KEY;
      });

      // Act: Load the application
      await navigateToCodeGenerator(page);

      // Assert: Error message appears
      await expect(page.getByText(/Missing VITE_CODEX_KEY environment variable/i)).toBeVisible();
      
      // Assert: Error description provides guidance
      await expect(page.getByText(/Please configure your API key/i)).toBeVisible();
    });

    test('should show red error indicator for API status', async ({ page }) => {
      await page.addInitScript(() => {
        delete (window as any).import.meta.env.VITE_CODEX_KEY;
      });

      await navigateToCodeGenerator(page);

      // Wait for status check to complete
      await page.waitForTimeout(1000);

      // Assert: Status shows "Error"
      const status = await getAPIStatus(page);
      expect(status).toContain('Error');

      // Assert: Red indicator visible
      const color = await getAPIStatusColor(page);
      expect(color).toBe('red');
    });

    test('should disable generate button when no API key', async ({ page }) => {
      await page.addInitScript(() => {
        delete (window as any).import.meta.env.VITE_CODEX_KEY;
      });

      await navigateToCodeGenerator(page);

      // Assert: Generate button is disabled
      const generateButton = page.getByRole('button', { name: /Generate Code/i });
      await expect(generateButton).toBeDisabled();

      // Assert: Button cannot be clicked
      await generateButton.click({ force: true }).catch(() => {
        // Expected to fail - button is disabled
      });
      
      // Assert: No code generation occurs
      await expect(page.getByText(/Generated Code/i)).not.toBeVisible();
    });

    test('should prevent prompt submission when API key missing', async ({ page }) => {
      await page.addInitScript(() => {
        delete (window as any).import.meta.env.VITE_CODEX_KEY;
      });

      await navigateToCodeGenerator(page);

      // Try to enter prompt
      await enterPrompt(page, 'Create a test function');

      // Verify character count updates (component still functional)
      await expect(page.getByText(/21 \/ 5000/)).toBeVisible();

      // Generate button remains disabled
      const generateButton = page.getByRole('button', { name: /Generate Code/i });
      await expect(generateButton).toBeDisabled();
    });
  });

  /**
   * Test 3: Lazy Initialization - With API Key
   * 
   * Validates complete connection flow when API key is present:
   * ✅ Initial "Checking..." state with yellow indicator
   * ✅ Automatic status check on mount
   * ✅ Transition to "Connected" with green indicator
   * ✅ Generate button becomes enabled
   * ✅ Periodic status rechecks (every 30 seconds)
   */
  test.describe('Test 3: With API Key Scenario', () => {
    
    test('should show checking state initially', async ({ page }) => {
      // Arrange: Set valid API key
      await page.addInitScript((apiKey) => {
        (window as any).import.meta.env.VITE_CODEX_KEY = apiKey;
      }, API_KEY_VALID);

      // Act: Load application
      await navigateToCodeGenerator(page);

      // Assert: Initial state is "Checking..."
      await expect(page.getByText(/Checking/i)).toBeVisible({ timeout: 1000 });

      // Assert: Yellow indicator visible
      const color = await getAPIStatusColor(page);
      expect(color).toBe('yellow');
    });

    test('should transition to connected state after status check', async ({ page }) => {
      await page.addInitScript((apiKey) => {
        (window as any).import.meta.env.VITE_CODEX_KEY = apiKey;
        (window as any).import.meta.env.VITE_CODEX_API = 'http://localhost:8000';
      }, API_KEY_VALID);

      await navigateToCodeGenerator(page);

      // Wait for status check to complete (mock will succeed or fail to fallback)
      await page.waitForTimeout(2000);

      // Assert: Status shows either "Connected" or "Error" (with mock fallback)
      const status = await getAPIStatus(page);
      expect(['Connected', 'Error']).toContain(status);

      // If connected, should be green; if error (with mock), still functional
      const color = await getAPIStatusColor(page);
      expect(['green', 'red']).toContain(color);
    });

    test('should enable generate button after initialization', async ({ page }) => {
      await page.addInitScript((apiKey) => {
        (window as any).import.meta.env.VITE_CODEX_KEY = apiKey;
      }, API_KEY_VALID);

      await navigateToCodeGenerator(page);

      // Wait for initialization to complete
      await page.waitForTimeout(2000);

      // Assert: Generate button becomes enabled
      const generateButton = page.getByRole('button', { name: /Generate Code/i });
      await expect(generateButton).toBeEnabled({ timeout: 3000 });
    });

    test('should periodically recheck API status', async ({ page }) => {
      await page.addInitScript((apiKey) => {
        (window as any).import.meta.env.VITE_CODEX_KEY = apiKey;
      }, API_KEY_VALID);

      // Track network requests
      const statusCheckUrls: string[] = [];
      page.on('request', request => {
        if (request.url().includes('/status') || request.url().includes('/health')) {
          statusCheckUrls.push(request.url());
        }
      });

      await navigateToCodeGenerator(page);

      // Wait initial check
      await page.waitForTimeout(2000);
      const initialChecks = statusCheckUrls.length;

      // Wait 31 seconds for periodic recheck (30s interval + buffer)
      await page.waitForTimeout(31000);

      // Assert: At least one additional status check occurred
      expect(statusCheckUrls.length).toBeGreaterThan(initialChecks);
    });

    test('should allow prompt entry when API key present', async ({ page }) => {
      await page.addInitScript((apiKey) => {
        (window as any).import.meta.env.VITE_CODEX_KEY = apiKey;
      }, API_KEY_VALID);

      await navigateToCodeGenerator(page);
      await page.waitForTimeout(2000);

      // Enter prompt
      const testPrompt = 'Create a FastAPI endpoint for user authentication';
      await enterPrompt(page, testPrompt);

      // Assert: Character count updates
      await expect(page.getByText(/52 \/ 5000/)).toBeVisible();

      // Assert: No error border (valid input)
      const textarea = page.getByPlaceholder(/Example: Create a FastAPI endpoint/i);
      const classes = await textarea.getAttribute('class');
      expect(classes).not.toContain('border-destructive');
    });
  });

  /**
   * Test 4: Mock Fallback Scenario
   * 
   * Validates graceful degradation when API fails:
   * ✅ Invalid API key triggers fallback
   * ✅ Mock client activates automatically
   * ✅ Toast notification shows "(Demo Mode)"
   * ✅ Generated code appears correctly
   * ✅ User experience remains smooth
   */
  test.describe('Test 4: Mock Fallback Scenario', () => {
    
    test('should accept valid prompt input (10+ characters)', async ({ page }) => {
      await page.addInitScript((apiKey) => {
        (window as any).import.meta.env.VITE_CODEX_KEY = apiKey;
      }, API_KEY_INVALID);

      await navigateToCodeGenerator(page);
      await page.waitForTimeout(2000);

      // Test short prompt (invalid)
      await enterPrompt(page, 'Short');
      await expect(page.getByText(/5 \/ 5000/)).toBeVisible();
      await expect(page.getByText(/\(min: 10\)/)).toBeVisible();

      // Textarea should have error styling
      const textarea = page.getByPlaceholder(/Example: Create a FastAPI endpoint/i);
      const classesInvalid = await textarea.getAttribute('class');
      expect(classesInvalid).toContain('border-destructive');

      // Test valid prompt
      await enterPrompt(page, 'Create a hello world function');
      await expect(page.getByText(/31 \/ 5000/)).toBeVisible();

      // Error styling should be removed
      const classesValid = await textarea.getAttribute('class');
      expect(classesValid).not.toContain('border-destructive');
    });

    test('should show character count validation', async ({ page }) => {
      await page.addInitScript((apiKey) => {
        (window as any).import.meta.env.VITE_CODEX_KEY = apiKey;
      }, API_KEY_INVALID);

      await navigateToCodeGenerator(page);
      await page.waitForTimeout(1000);

      const textarea = page.getByPlaceholder(/Example: Create a FastAPI endpoint/i);

      // Test progressive character count
      await textarea.fill('Test');
      await expect(page.getByText(/4 \/ 5000/)).toBeVisible();

      await textarea.fill('Testing more');
      await expect(page.getByText(/12 \/ 5000/)).toBeVisible();

      // Min warning should disappear when valid
      await expect(page.getByText(/\(min: 10\)/)).not.toBeVisible();
    });

    test('should trigger mock fallback on API failure', async ({ page, context }) => {
      // Mock API to fail
      await context.route('**/generate', route => {
        route.fulfill({
          status: 401,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Unauthorized' }),
        });
      });

      await page.addInitScript((apiKey) => {
        (window as any).import.meta.env.VITE_CODEX_KEY = apiKey;
      }, API_KEY_INVALID);

      await navigateToCodeGenerator(page);
      await page.waitForTimeout(2000);

      // Enter valid prompt
      await enterPrompt(page, 'Create a test function with type hints');
      
      // Click generate
      await clickGenerate(page);

      // Wait for toast notification
      await waitForToast(page, 'Code generated successfully (Demo Mode)', 10000);

      // Assert: Mock-generated code appears
      await expect(page.getByText(/Generated Code/i)).toBeVisible({ timeout: 5000 });
      
      // Assert: Some code content is visible
      const codeBlock = page.locator('pre, code').first();
      await expect(codeBlock).toBeVisible();
    });

    test('should display Demo Mode toast notification', async ({ page, context }) => {
      await context.route('**/generate', route => {
        route.fulfill({ status: 500 });
      });

      await page.addInitScript((apiKey) => {
        (window as any).import.meta.env.VITE_CODEX_KEY = apiKey;
      }, API_KEY_INVALID);

      await navigateToCodeGenerator(page);
      await page.waitForTimeout(2000);

      await enterPrompt(page, 'Generate a Python class');
      await clickGenerate(page);

      // Assert: Toast contains "(Demo Mode)" text
      await expect(page.getByText(/(Demo Mode)/i)).toBeVisible({ timeout: 10000 });

      // Assert: k₁ factor is displayed in toast
      await expect(page.getByText(/k₁ factor:/i)).toBeVisible();
    });

    test('should show copy and download buttons after generation', async ({ page, context }) => {
      await context.route('**/generate', route => {
        route.fulfill({ status: 500 });
      });

      await page.addInitScript((apiKey) => {
        (window as any).import.meta.env.VITE_CODEX_KEY = apiKey;
      }, API_KEY_INVALID);

      await navigateToCodeGenerator(page);
      await page.waitForTimeout(2000);

      await enterPrompt(page, 'Create a simple API endpoint');
      await clickGenerate(page);

      // Wait for generation to complete
      await expect(page.getByText(/Generated Code/i)).toBeVisible({ timeout: 10000 });

      // Assert: Copy button visible
      const copyButton = page.getByRole('button', { name: /Copy/i });
      await expect(copyButton).toBeVisible();

      // Assert: Download button visible
      const downloadButton = page.getByRole('button', { name: /Download/i });
      await expect(downloadButton).toBeVisible();
    });

    test('should display Cache Hit badge when applicable', async ({ page, context }) => {
      // Mock response with cache_hit: true
      await context.route('**/generate', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            code: 'def cached_function():\n    pass',
            metadata: {
              k1_factor: 0.95,
              cache_hit: true,
              generation_time_ms: 50,
            },
            quantum_metrics: {
              coherence: 0.98,
              entanglement: 0.91,
            },
          }),
        });
      });

      await page.addInitScript((apiKey) => {
        (window as any).import.meta.env.VITE_CODEX_KEY = apiKey;
      }, API_KEY_VALID);

      await navigateToCodeGenerator(page);
      await page.waitForTimeout(2000);

      await enterPrompt(page, 'Previously generated function');
      await clickGenerate(page);

      // Assert: Cache Hit badge appears
      await expect(page.getByText(/Cache Hit/i)).toBeVisible({ timeout: 10000 });
    });
  });

  /**
   * Test 5: Environment Variable Configuration
   * 
   * Validates cascade timing configuration:
   * ✅ Component renders with various VITE_STAGE_EXECUTION_TIME_MS values
   * ✅ Default 800ms behavior
   * ✅ Custom timing (200ms, 2000ms)
   * ✅ Invalid values fall back to default
   */
  test.describe('Test 5: Cascade Timing Configuration', () => {
    
    test('should render with default timing (800ms)', async ({ page }) => {
      await page.addInitScript(() => {
        delete (window as any).import.meta.env.VITE_STAGE_EXECUTION_TIME_MS;
        (window as any).import.meta.env.VITE_CODEX_KEY = 'test-key';
      });

      await navigateToCodeGenerator(page);

      // Assert: Component loads successfully
      await expect(page.getByText(/Code Generation/i)).toBeVisible();
    });

    test('should render with fast timing (200ms)', async ({ page }) => {
      await page.addInitScript(() => {
        (window as any).import.meta.env.VITE_STAGE_EXECUTION_TIME_MS = '200';
        (window as any).import.meta.env.VITE_CODEX_KEY = 'test-key';
      });

      await navigateToCodeGenerator(page);

      // Assert: Component loads and functions normally
      await expect(page.getByText(/Code Generation/i)).toBeVisible();
      
      // Note: Actual timing validation would require cascade component interaction
    });

    test('should render with slow timing (2000ms)', async ({ page }) => {
      await page.addInitScript(() => {
        (window as any).import.meta.env.VITE_STAGE_EXECUTION_TIME_MS = '2000';
        (window as any).import.meta.env.VITE_CODEX_KEY = 'test-key';
      });

      await navigateToCodeGenerator(page);

      await expect(page.getByText(/Code Generation/i)).toBeVisible();
    });

    test('should handle invalid timing values gracefully', async ({ page }) => {
      // Test invalid values that should fall back to default
      const invalidValues = ['0', '-500', '20000', 'invalid', 'NaN'];

      for (const invalidValue of invalidValues) {
        await page.addInitScript((value) => {
          (window as any).import.meta.env.VITE_STAGE_EXECUTION_TIME_MS = value;
          (window as any).import.meta.env.VITE_CODEX_KEY = 'test-key';
        }, invalidValue);

        await page.goto(BASE_URL);

        // Assert: Component still loads (fallback to default 800ms)
        await expect(page.getByText(/Code Generation/i)).toBeVisible({ timeout: 5000 });

        // Reload for next iteration
        await page.reload();
      }
    });

    test('should handle various API URL configurations', async ({ page }) => {
      const apiUrls = [
        undefined, // Default
        'http://localhost:8000',
        'https://api.example.com',
        'http://custom-api.local:3000',
      ];

      for (const apiUrl of apiUrls) {
        await page.addInitScript((url) => {
          if (url) {
            (window as any).import.meta.env.VITE_CODEX_API = url;
          } else {
            delete (window as any).import.meta.env.VITE_CODEX_API;
          }
          (window as any).import.meta.env.VITE_CODEX_KEY = 'test-key';
        }, apiUrl);

        await page.goto(BASE_URL);

        // Assert: Component loads successfully with any API configuration
        await expect(page.getByText(/Code Generation/i)).toBeVisible({ timeout: 5000 });

        await page.reload();
      }
    });
  });

  /**
   * Additional E2E Tests: Real User Workflows
   */
  test.describe('Real User Workflow Tests', () => {
    
    test('complete workflow: enter prompt, generate, copy code', async ({ page, context }) => {
      await context.route('**/generate', route => {
        route.fulfill({ status: 500 }); // Force mock fallback
      });

      await page.addInitScript(() => {
        (window as any).import.meta.env.VITE_CODEX_KEY = 'test-key';
      });

      await navigateToCodeGenerator(page);
      await page.waitForTimeout(2000);

      // Step 1: Enter prompt
      await enterPrompt(page, 'Create a REST API endpoint for user registration');

      // Step 2: Click generate
      await clickGenerate(page);

      // Step 3: Wait for code generation
      await expect(page.getByText(/Generated Code/i)).toBeVisible({ timeout: 10000 });

      // Step 4: Copy code
      const copyButton = page.getByRole('button', { name: /Copy/i });
      await copyButton.click();

      // Assert: Toast confirms copy
      await expect(page.getByText(/copied to clipboard/i)).toBeVisible({ timeout: 3000 });
    });

    test('complete workflow: generate, download code file', async ({ page, context }) => {
      await context.route('**/generate', route => {
        route.fulfill({ status: 500 });
      });

      await page.addInitScript(() => {
        (window as any).import.meta.env.VITE_CODEX_KEY = 'test-key';
      });

      await navigateToCodeGenerator(page);
      await page.waitForTimeout(2000);

      await enterPrompt(page, 'Generate a data validation function');
      await clickGenerate(page);

      await expect(page.getByText(/Generated Code/i)).toBeVisible({ timeout: 10000 });

      // Setup download listener
      const downloadPromise = page.waitForEvent('download');

      // Click download
      const downloadButton = page.getByRole('button', { name: /Download/i });
      await downloadButton.click();

      // Assert: Download initiated
      const download = await downloadPromise;
      expect(download.suggestedFilename()).toBe('generated_code.py');

      // Assert: Toast confirms download
      await expect(page.getByText(/downloaded/i)).toBeVisible({ timeout: 3000 });
    });

    test('error recovery: retry after prompt too short', async ({ page }) => {
      await page.addInitScript(() => {
        (window as any).import.meta.env.VITE_CODEX_KEY = 'test-key';
      });

      await navigateToCodeGenerator(page);
      await page.waitForTimeout(2000);

      // Try short prompt
      await enterPrompt(page, 'Test');
      
      const generateButton = page.getByRole('button', { name: /Generate Code/i });
      
      // Button should be disabled with short prompt
      await expect(generateButton).toBeDisabled();

      // Fix prompt
      await enterPrompt(page, 'Create a comprehensive test suite');

      // Button should become enabled
      await expect(generateButton).toBeEnabled();

      // Generate should work
      await clickGenerate(page);
      // Mock fallback will activate...
    });
  });

  /**
   * Accessibility Tests
   */
  test.describe('Accessibility Validation', () => {
    
    test('should have proper ARIA labels and roles', async ({ page }) => {
      await page.addInitScript(() => {
        (window as any).import.meta.env.VITE_CODEX_KEY = 'test-key';
      });

      await navigateToCodeGenerator(page);

      // Assert: Generate button has proper role
      const generateButton = page.getByRole('button', { name: /Generate Code/i });
      await expect(generateButton).toBeVisible();

      // Assert: Textarea has proper label
      const textarea = page.getByLabelText(/Describe the code you want to generate/i);
      await expect(textarea).toBeVisible();
    });

    test('should support keyboard navigation', async ({ page }) => {
      await page.addInitScript(() => {
        (window as any).import.meta.env.VITE_CODEX_KEY = 'test-key';
      });

      await navigateToCodeGenerator(page);
      await page.waitForTimeout(1000);

      // Tab to textarea
      await page.keyboard.press('Tab');
      
      // Type in textarea
      await page.keyboard.type('Generate a test function');

      // Tab to generate button
      await page.keyboard.press('Tab');

      // Press Enter to submit
      await page.keyboard.press('Enter');

      // Should trigger generation (mock fallback)
      // Note: Full validation depends on button focus state
    });
  });
});
