import { useState, useCallback, useEffect, useRef } from 'react';
import { Copy, Download, Sparkle, CheckCircle, XCircle } from '@phosphor-icons/react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { toast } from 'sonner';
import { CodexAPIClient, CodexResponse, CodexAPIError } from '@/lib/codex-api-client';
import { MockCodexAPIClient } from '@/lib/mock-api-client';
import { SparkLLMClient } from '@/lib/spark-llm-client';
import { CodeEditor } from './CodeEditor';
import { MetricsBar } from './MetricsBar';
import { InteractiveDemo } from './InteractiveDemo';

const API_URL = import.meta.env.VITE_CODEX_API || 'http://localhost:8000';

// Tier mapping used by generation backends:
// - API/Mock client expects tier 'A'
// - Spark runtime expects tier 'B'
const API_MOCK_TIER = 'A';
const SPARK_TIER = 'B';

/**
 * Factory function to create a CodexAPIClient instance.
 * Uses lazy initialization to support hot module replacement during development,
 * allowing the API key to be reconfigured without reloading the module.
 * @returns CodexAPIClient instance or null if API key is not available
 */
function createClient(): CodexAPIClient | null {
  const apiKey = import.meta.env.VITE_CODEX_KEY;
  return apiKey ? new CodexAPIClient(API_URL, apiKey) : null;
}

/**
 * Factory function to create a MockCodexAPIClient instance.
 * Uses lazy initialization to maintain consistency with the main client pattern.
 * @returns MockCodexAPIClient instance
 */
function createMockClient(): MockCodexAPIClient {
  return new MockCodexAPIClient();
}

export function CodeGenerator() {
  const [prompt, setPrompt] = useState('');
  const [result, setResult] = useState<CodexResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [infoMessage, setInfoMessage] = useState<string | null>(null);
  const [apiStatus, setApiStatus] = useState<'connected' | 'error' | 'checking'>('checking');
  const [useAIMode, setUseAIMode] = useState(false);
  const [showInteractiveDemo, setShowInteractiveDemo] = useState(false);

  // Lazy initialization: clients are created on first use and can be recreated if needed
  const clientRef = useRef<CodexAPIClient | null>(null);
  const mockClientRef = useRef<MockCodexAPIClient | null>(null);
  const sparkClientRef = useRef<SparkLLMClient | null>(null);

  const getClient = useCallback(() => {
    // Attempt to recreate client if it doesn't exist or if API key might have changed
    if (!clientRef.current) {
      clientRef.current = createClient();
    }
    return clientRef.current;
  }, []);

  const getMockClient = useCallback(() => {
    if (!mockClientRef.current) {
      mockClientRef.current = createMockClient();
    }
    return mockClientRef.current;
  }, []);

  const getSparkClient = useCallback(() => {
    if (!sparkClientRef.current) {
      sparkClientRef.current = new SparkLLMClient();
    }
    return sparkClientRef.current;
  }, []);

  const checkApiStatus = useCallback(async () => {
    setApiStatus('checking');

    // If AI mode is enabled, check Spark client
    if (useAIMode) {
      try {
        const sparkClient = getSparkClient();
        const status = await sparkClient.getStatus();
        setApiStatus('connected');
        setError(null);
        setInfoMessage(`AI Mode: ${status.model}`);
        return;
      } catch (err) {
        console.error('Spark status check failed:', err);
        setApiStatus('error');
        setError('Spark LLM client unavailable');
        setInfoMessage(null);
        return;
      }
    }

    const client = getClient();
    if (!client) {
      // No API key - use mock client in demo mode
      const mockClient = getMockClient();
      try {
        // Check mock status to maintain consistent async behavior
        await mockClient.getStatus();
        setApiStatus('connected'); // Mock available
        setInfoMessage('Using demo mode (API key not configured)');
        setError(null);
      } catch (err) {
        console.error('Mock client status check failed:', err);
        setApiStatus('error');
        setError('Demo mode unavailable');
        setInfoMessage(null);
      }
      return;
    }
    try {
      await client.getStatus();
      setApiStatus('connected');
      setError(null);
      setInfoMessage(null);
    } catch (err) {
      console.error('Primary API status check failed:', err);
      try {
        const mockClient = getMockClient();
        await mockClient.getStatus();
        setApiStatus('connected'); // Mock available as fallback
        setInfoMessage('API connection failed, using demo mode');
        setError(null);
      } catch (err) {
        console.error('Mock client status check failed:', err);
        setApiStatus('error');
        setError('Unable to connect to API or demo mode');
        setInfoMessage(null);
      }
    }
  }, [getClient, getMockClient, getSparkClient, useAIMode]);

  useEffect(() => {
    checkApiStatus();
    const interval = setInterval(checkApiStatus, 30000);
    return () => clearInterval(interval);
  }, [checkApiStatus]);

  const handleGenerate = useCallback(async () => {
    if (prompt.trim().length < 10) {
      setError('Prompt must be at least 10 characters');
      toast.error('Prompt too short', {
        description: 'Please enter at least 10 characters',
      });
      return;
    }

    setLoading(true);
    setError(null);
    setShowInteractiveDemo(false);

    const startTime = Date.now();

    const finishWithResult = (response: CodexResponse, source: 'spark' | 'api' | 'mock') => {
      const k1Factor = typeof response.metadata?.k1_factor === 'number'
        ? response.metadata.k1_factor
        : 0.32;
      const coherence = typeof response.metadata?.coherence === 'number'
        ? response.metadata.coherence
        : 0.8;

      const client = getClient();
      setResult(response);
      if (source === 'spark') {
        setInfoMessage(`AI Mode: gpt-4o-mini (Spark Runtime)`);
      } else if (source === 'mock') {
        setInfoMessage(client ? 'API connection failed, using demo mode' : 'Using demo mode (API key not configured)');
      } else {
        setInfoMessage(null);
      }

      const sourceLabel = source === 'spark' ? 'Spark AI' : source === 'api' ? 'Codex API' : 'Demo Mode';
      toast.success('Code generated successfully', {
        description: source === 'spark'
          ? `Generated with ${sourceLabel} • k₁ factor: ${k1Factor.toFixed(4)} • coherence: ${coherence.toFixed(4)}`
          : `Generated with ${sourceLabel} • k₁ factor: ${k1Factor.toFixed(4)}`,
      });
      setLoading(false);
    };

    if (useAIMode) {
      try {
        const sparkClient = getSparkClient();
        const response = await sparkClient.generateCode({
          prompt,
          context: { language: 'python', tier: SPARK_TIER },
        });

        const elapsed = Date.now() - startTime;
        if (elapsed < 500) {
          await new Promise(resolve => setTimeout(resolve, 500 - elapsed));
        }

        finishWithResult(response, 'spark');
        return;
      } catch (err) {
        console.error('Spark code generation failed, falling back to API/mock generation.', err);
        setInfoMessage(null);
        // Fall through to API/mock generation when Spark is unavailable or fails.
      }
    }

    const client = getClient();
    if (client) {
      try {
        const response = await client.generateCode({
          prompt,
          context: { language: 'python', tier: API_MOCK_TIER },
        });

        const elapsed = Date.now() - startTime;
        if (elapsed < 500) {
          await new Promise(resolve => setTimeout(resolve, 500 - elapsed));
        }

        finishWithResult(response, 'api');
        return;
      } catch (err) {
        if (err instanceof CodexAPIError && err.statusCode === 429) {
          toast.error('Rate limit exceeded', {
            description: 'Please try again later or upgrade your plan',
            duration: 5000,
          });
          return;
        } else {
          const errorMessage = err instanceof Error
            ? err.message
            : 'Unknown API error';

          setInfoMessage(`Primary API failed (${errorMessage}). Falling back to mock generation.`);
          toast.error('Primary API unavailable', {
            description: 'Using mock generation as a fallback.',
          });
        }
      }
    }

    try {
      const mockClient = getMockClient();
      const mockResponse = await mockClient.generateCode({
        prompt,
        context: { language: 'python', tier: API_MOCK_TIER },
      });

      const elapsed = Date.now() - startTime;
      if (elapsed < 500) {
        await new Promise(resolve => setTimeout(resolve, 500 - elapsed));
      }

      setError(null);
      finishWithResult(mockResponse, 'mock');
    } catch (mockErr) {
      const errorMessage = mockErr instanceof Error
        ? mockErr.message
        : 'Unknown error occurred';

      setError(errorMessage);
      toast.error('Generation failed', {
        description: errorMessage,
      });
    } finally {
      setLoading(false);
    }
  }, [prompt, getClient, getMockClient, getSparkClient, useAIMode]);

  const handleCopy = useCallback(() => {
    if (result?.code) {
      navigator.clipboard.writeText(result.code);
      toast.success('Code copied to clipboard');
    }
  }, [result]);

  const handleDownload = useCallback(() => {
    if (result?.code) {
      const blob = new Blob([result.code], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'generated_code.py';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      toast.success('Code downloaded');
    }
  }, [result]);

  const charCount = prompt.length;
  const isValidPrompt = charCount >= 10 && charCount <= 5000;

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-semibold text-accent">Code Generation</h2>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">AI Mode:</span>
              <Switch
                checked={useAIMode}
                onCheckedChange={setUseAIMode}
                aria-label="Toggle AI Mode"
              />
              <span className="text-sm font-medium">
                {useAIMode ? 'On' : 'Off'}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">Status:</span>
              <div className={`w-2 h-2 rounded-full ${
                apiStatus === 'connected' ? 'bg-green-500' :
                apiStatus === 'error' ? 'bg-red-500' :
                'bg-yellow-500'
              }`} />
              <span className={`text-sm ${
                apiStatus === 'connected' ? 'text-green-500' :
                apiStatus === 'error' ? 'text-red-500' :
                'text-yellow-500'
              }`}>
                {apiStatus === 'connected' ? (useAIMode ? 'AI-Powered' : 'Connected') :
                 apiStatus === 'error' ? 'Error' :
                 'Checking...'}
              </span>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label htmlFor="prompt" className="text-sm font-medium">
                Describe the code you want to generate
              </label>
              <span className={`text-xs ${
                !isValidPrompt && charCount > 0 ? 'text-destructive' : 'text-muted-foreground'
              }`}>
                {charCount} / 5000 {charCount < 10 && charCount > 0 && '(min: 10)'}
              </span>
            </div>
            <Textarea
              id="prompt"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Example: Create a FastAPI endpoint for user authentication with JWT tokens..."
              rows={8}
              className="font-mono resize-none"
              aria-invalid={!isValidPrompt && charCount > 0}
            />
          </div>

          <Button
            onClick={handleGenerate}
            disabled={loading || !isValidPrompt || apiStatus === 'error'}
            className="w-full sm:w-auto"
            size="lg"
          >
            {loading ? (
              <>
                <Sparkle className="w-5 h-5 mr-2 animate-spin" />
                Generating Code...
              </>
            ) : (
              <>
                <Sparkle className="w-5 h-5 mr-2" />
                Generate Code
              </>
            )}
          </Button>
        </div>

        {infoMessage && !error && (
          <div className="mt-4 p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg flex items-start gap-3">
            <svg className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 256 256" xmlns="http://www.w3.org/2000/svg">
              <path d="M128,24A104,104,0,1,0,232,128,104.11,104.11,0,0,0,128,24Zm-4,48a12,12,0,1,1-12,12A12,12,0,0,1,124,72Zm12,112a16,16,0,0,1-16-16V128a8,8,0,0,1,0-16,16,16,0,0,1,16,16v40a8,8,0,0,1,0,16Z"/>
            </svg>
            <div>
              <p className="font-semibold text-blue-600 dark:text-blue-400">Info</p>
              <p className="text-sm text-blue-600/90 dark:text-blue-400/90 mt-1">{infoMessage}</p>
            </div>
          </div>
        )}

        {error && (
          <div className="mt-4 p-4 bg-destructive/10 border border-destructive rounded-lg flex items-start gap-3">
            <XCircle weight="fill" className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-destructive">Error</p>
              <p className="text-sm text-destructive/90 mt-1">{error}</p>
            </div>
          </div>
        )}
      </Card>

      {result && (
        <div className="space-y-6">
          <MetricsBar metadata={result.metadata} quantumMetrics={result.quantum_metrics} />

          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <h3 className="text-xl font-semibold">Generated Code</h3>
                {result.metadata.cache_hit && (
                  <Badge variant="outline" className="border-accent text-accent">
                    <CheckCircle weight="fill" className="w-3 h-3 mr-1" />
                    Cache Hit
                  </Badge>
                )}
              </div>
              <div className="flex items-center gap-2">
                <Button
                  onClick={handleCopy}
                  variant="outline"
                  size="sm"
                >
                  <Copy className="w-4 h-4 mr-2" />
                  Copy
                </Button>
                <Button
                  onClick={handleDownload}
                  variant="outline"
                  size="sm"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Download
                </Button>
                <Button
                  onClick={() => setShowInteractiveDemo((prev) => !prev)}
                  variant="secondary"
                  size="sm"
                >
                  Try It Live
                </Button>
              </div>
            </div>

            {showInteractiveDemo && (
              <div className="mt-6 space-y-4">
                <h3 className="text-lg font-semibold">Interactive Code Demo</h3>
                <InteractiveDemo script={result.code} language="python" />
              </div>
            )}

            <CodeEditor code={result.code} language="python" />
          </Card>
        </div>
      )}
    </div>
  );
}
