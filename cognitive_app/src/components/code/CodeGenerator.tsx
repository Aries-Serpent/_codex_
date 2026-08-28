import { useState, useCallback, useEffect } from 'react';
import { Copy, Download, Sparkle, CheckCircle, XCircle } from '@phosphor-icons/react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { toast } from 'sonner';
import type { CodexResponse } from '@/lib/codex-api-client';
import {
  appService,
  DEFAULT_LANGUAGE,
  DEFAULT_MODEL,
  SUPPORTED_LANGUAGES,
  SUPPORTED_MODELS,
  type AppGenerationLanguage,
  type AppGenerationModel,
} from '@/services/app-service';
import { CodeEditor } from './CodeEditor';
import { MetricsBar } from './MetricsBar';
import { InteractiveDemo } from './InteractiveDemo';

export interface CodeGeneratorProps {
  onCodeGenerated?: (code: string) => void;
}

export function CodeGenerator({ onCodeGenerated }: CodeGeneratorProps) {
  const [prompt, setPrompt] = useState('');
  const [result, setResult] = useState<CodexResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [infoMessage, setInfoMessage] = useState<string | null>(null);
  const [apiStatus, setApiStatus] = useState<'connected' | 'error' | 'checking'>('checking');
  const [useAIMode, setUseAIMode] = useState(false);
  const [showInteractiveDemo, setShowInteractiveDemo] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState<AppGenerationLanguage>(DEFAULT_LANGUAGE);
  const [selectedModel, setSelectedModel] = useState<AppGenerationModel>(DEFAULT_MODEL);

  const checkApiStatus = useCallback(async () => {
    setApiStatus('checking');

    try {
      const status = await appService.getStatus(useAIMode);
      setApiStatus(status.status);
      setError(status.error);
      setInfoMessage(status.message);
    } catch (err) {
      console.error('App service status check failed:', err);
      setApiStatus('error');
      setError('Unable to check service status');
      setInfoMessage(null);
    }
  }, [useAIMode]);

  useEffect(() => {
    void checkApiStatus();
    const interval = setInterval(() => {
      void checkApiStatus();
    }, 30000);
    return () => clearInterval(interval);
  }, [checkApiStatus]);

  const finishWithResult = useCallback(
    (response: CodexResponse, source: 'spark' | 'api' | 'mock', fallbackError?: unknown) => {
      const k1Factor = typeof response.metadata?.k1_factor === 'number' ? response.metadata.k1_factor : 0.32;
      const coherence = typeof response.metadata?.coherence === 'number' ? response.metadata.coherence : 0.8;

      setResult(response);
      if (onCodeGenerated) {
        onCodeGenerated(response.code);
      }

      if (source === 'mock') {
        const fallbackMessage =
          fallbackError instanceof Error
            ? fallbackError.message
            : fallbackError !== undefined && fallbackError !== null
              ? String(fallbackError)
              : null;
        setInfoMessage(
          fallbackMessage ? `Primary API failed: ${fallbackMessage}. Falling back to demo mode.` : 'Using demo mode (API key not configured)',
        );
      }

      const sourceLabel = source === 'spark' ? 'Spark AI' : source === 'api' ? 'Codex API' : 'Demo Mode';
      toast.success('Code generated successfully', {
        description:
          source === 'spark'
            ? `Generated with ${sourceLabel} • k₁ factor: ${k1Factor.toFixed(4)} • coherence: ${coherence.toFixed(4)}`
            : `Generated with ${sourceLabel} • k₁ factor: ${k1Factor.toFixed(4)}`,
      });
      setLoading(false);
    },
    [onCodeGenerated, selectedModel],
  );

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

    try {
      const { response, source, fallbackError } = await appService.generateCode({
        prompt,
        language: selectedLanguage,
        model: selectedModel,
        aiMode: useAIMode,
      });

      const elapsed = Date.now() - startTime;
      if (elapsed < 500) {
        await new Promise((resolve) => setTimeout(resolve, 500 - elapsed));
      }

      if (fallbackError) {
        const message = fallbackError instanceof Error ? fallbackError.message : String(fallbackError);
        toast.error('Generation failed', {
          description: message,
        });
      }

      finishWithResult(response, source, fallbackError);
      return;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown generation error';
      setError(message);
      toast.error('Generation failed', {
        description: message,
      });
    } finally {
      setLoading(false);
    }
  }, [finishWithResult, prompt, selectedLanguage, selectedModel, useAIMode]);

  const handleCopy = useCallback(() => {
    if (result) {
      navigator.clipboard
        .writeText(result.code)
        .then(() => {
          toast.success('Code copied to clipboard');
        })
        .catch((err) => {
          console.error('Failed to copy to clipboard:', err);
          toast.error('Failed to copy', {
            description: 'Could not write to clipboard. Check browser permissions.',
          });
        });
    }
  }, [result]);

  const handleDownload = useCallback(() => {
    if (result?.code) {
      const blob = new Blob([result.code], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `generated_code.${
        selectedLanguage === 'python'
          ? 'py'
          : selectedLanguage === 'javascript'
            ? 'js'
            : selectedLanguage === 'typescript'
              ? 'ts'
              : selectedLanguage === 'rust'
                ? 'rs'
                : selectedLanguage === 'go'
                  ? 'go'
                  : 'sh'
      }`;
      a.rel = 'noopener';
      a.style.display = 'none';
      if (a.parentNode) {
        a.parentNode.removeChild(a);
      }
      try {
        document.body.appendChild(a);
        a.click();
      } finally {
        if (a.parentNode) {
          a.parentNode.removeChild(a);
        }
        URL.revokeObjectURL(url);
      }
      toast.success('Code downloaded');
    }
  }, [result, selectedLanguage]);

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
              <Switch checked={useAIMode} onCheckedChange={setUseAIMode} aria-label="Toggle AI Mode" />
              <span className="text-sm font-medium">{useAIMode ? 'On' : 'Off'}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">Status:</span>
              <div
                className={`w-2 h-2 rounded-full ${
                  apiStatus === 'connected' ? 'bg-green-500' : apiStatus === 'error' ? 'bg-red-500' : 'bg-yellow-500'
                }`}
              />
              <span
                className={`text-sm ${
                  apiStatus === 'connected' ? 'text-green-500' : apiStatus === 'error' ? 'text-red-500' : 'text-yellow-500'
                }`}
              >
                {apiStatus === 'connected' ? (useAIMode ? 'AI-Powered' : 'Connected') : apiStatus === 'error' ? 'Error' : 'Checking...'}
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
              <span className={`text-xs ${!isValidPrompt && charCount > 0 ? 'text-destructive' : 'text-muted-foreground'}`}>
                {charCount} / 5000 {charCount < 10 && charCount > 0 && '(min: 10)'}
              </span>
            </div>
            <Textarea
              id="prompt"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Tab' && !e.shiftKey && !e.metaKey && !e.ctrlKey && !e.altKey) {
                  e.preventDefault();
                  const generateButton = document.getElementById('generate-code-button');
                  if (generateButton instanceof HTMLButtonElement) {
                    generateButton.focus();
                  }
                }
              }}
              placeholder="Example: Create a FastAPI endpoint for user authentication with JWT tokens..."
              rows={8}
              className={[
                'font-mono resize-none',
                !isValidPrompt && charCount > 0 ? 'border-destructive aria-invalid:border-destructive' : '',
              ].filter(Boolean).join(' ')}
              aria-invalid={!isValidPrompt && charCount > 0}
            />
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <label className="text-sm font-medium">Model</label>
              <Select value={selectedModel} onValueChange={(value) => setSelectedModel(value as AppGenerationModel)}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select model" />
                </SelectTrigger>
                <SelectContent>
                  {SUPPORTED_MODELS.map((model) => (
                    <SelectItem key={model} value={model}>
                      {model}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Language</label>
              <Select value={selectedLanguage} onValueChange={(value) => setSelectedLanguage(value as AppGenerationLanguage)}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select language" />
                </SelectTrigger>
                <SelectContent>
                  {SUPPORTED_LANGUAGES.map((language) => (
                    <SelectItem key={language} value={language}>
                      {language}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <Button
            id="generate-code-button"
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
              <path d="M128,24A104,104,0,1,0,232,128,104.11,104.11,0,0,0,128,24Zm-4,48a12,12,0,1,1-12,12A12,12,0,0,1,124,72Zm12,112a16,16,0,0,1-16-16V128a8,8,0,0,1,0-16,16,16,0,0,1,16,16v40a8,8,0,0,1,0,16Z" />
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
                <Button onClick={handleCopy} variant="outline" size="sm">
                  <Copy className="w-4 h-4 mr-2" />
                  Copy
                </Button>
                <Button onClick={handleDownload} variant="outline" size="sm">
                  <Download className="w-4 h-4 mr-2" />
                  Download
                </Button>
                <Button onClick={() => setShowInteractiveDemo((prev) => !prev)} variant="secondary" size="sm">
                  Try It Live
                </Button>
              </div>
            </div>

            {showInteractiveDemo && (
              <div className="mt-6 space-y-4">
                <h3 className="text-lg font-semibold">Interactive Code Demo</h3>
                <InteractiveDemo script={result.code} language={selectedLanguage} />
              </div>
            )}

            <CodeEditor code={result.code} language={selectedLanguage} />
          </Card>
        </div>
      )}
    </div>
  );
}
