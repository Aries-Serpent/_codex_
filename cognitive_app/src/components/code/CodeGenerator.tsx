import { useState, useCallback, useEffect, useRef } from 'react';
import { Copy, Download, Sparkle, CheckCircle, XCircle } from '@phosphor-icons/react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { CodexAPIClient, CodexResponse, CodexAPIError } from '@/lib/codex-api-client';
import { MockCodexAPIClient } from '@/lib/mock-api-client';
import { CodeEditor } from './CodeEditor';
import { MetricsBar } from './MetricsBar';

const API_URL = import.meta.env.VITE_CODEX_API || 'http://localhost:8000';

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
  const [apiStatus, setApiStatus] = useState<'connected' | 'error' | 'checking'>('checking');
  
  // Lazy initialization: clients are created on first use and can be recreated if needed
  const clientRef = useRef<CodexAPIClient | null>(null);
  const mockClientRef = useRef<MockCodexAPIClient | null>(null);

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

  const checkApiStatus = useCallback(async () => {
    const client = getClient();
    if (!client) {
      setApiStatus('error');
      setError('Missing VITE_CODEX_KEY environment variable. Please configure your API key.');
      return;
    }
    try {
      await client.getStatus();
      setApiStatus('connected');
    } catch {
      try {
        const mockClient = getMockClient();
        await mockClient.getStatus();
        setApiStatus('connected');
      } catch {
        setApiStatus('error');
      }
    }
  }, [getClient, getMockClient]);

  useEffect(() => {
    checkApiStatus();
    const interval = setInterval(checkApiStatus, 30000);
    return () => clearInterval(interval);
  }, [checkApiStatus]);

  const handleGenerate = useCallback(async () => {
    const client = getClient();
    if (!client) {
      setError('Missing API key configuration. Please set VITE_CODEX_KEY environment variable.');
      toast.error('Configuration Error', {
        description: 'API key not configured',
      });
      return;
    }

    if (prompt.trim().length < 10) {
      setError('Prompt must be at least 10 characters');
      toast.error('Prompt too short', {
        description: 'Please enter at least 10 characters',
      });
      return;
    }

    setLoading(true);
    setError(null);

    const startTime = Date.now();

    try {
      const response = await client.generateCode({
        prompt,
        context: { language: 'python', tier: 'A' },
      });

      const elapsed = Date.now() - startTime;
      if (elapsed < 500) {
        await new Promise(resolve => setTimeout(resolve, 500 - elapsed));
      }

      setResult(response);
      toast.success('Code generated successfully', {
        description: `k₁ factor: ${response.metadata.k1_factor.toFixed(4)}`,
      });
    } catch (err) {
      try {
        const mockClient = getMockClient();
        const mockResponse = await mockClient.generateCode({
          prompt,
          context: { language: 'python', tier: 'A' },
        });

        const elapsed = Date.now() - startTime;
        if (elapsed < 500) {
          await new Promise(resolve => setTimeout(resolve, 500 - elapsed));
        }

        setResult(mockResponse);
        toast.success('Code generated successfully (Demo Mode)', {
          description: `k₁ factor: ${mockResponse.metadata.k1_factor.toFixed(4)}`,
        });
        setError(null);
      } catch (mockErr) {
        const errorMessage = err instanceof CodexAPIError 
          ? `${err.message} (HTTP ${err.statusCode})`
          : err instanceof Error 
          ? err.message 
          : 'Unknown error occurred';
        
        setError(errorMessage);
        toast.error('Generation failed', {
          description: errorMessage,
        });

        if (err instanceof CodexAPIError && err.statusCode === 429) {
          toast.error('Rate limit exceeded', {
            description: 'Please try again later or upgrade your plan',
            duration: 5000,
          });
        }
      }
    } finally {
      setLoading(false);
    }
  }, [prompt, getClient]);

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
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">API Status:</span>
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
              {apiStatus === 'connected' ? 'Connected' : 
               apiStatus === 'error' ? 'Error' : 
               'Checking...'}
            </span>
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
              className={`font-mono resize-none ${
                !isValidPrompt && charCount > 0 ? 'border-destructive' : ''
              }`}
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
              </div>
            </div>

            <CodeEditor code={result.code} language="python" />
          </Card>
        </div>
      )}
    </div>
  );
}
