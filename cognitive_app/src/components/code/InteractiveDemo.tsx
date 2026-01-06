import { useState, useCallback, useEffect, useRef } from 'react';
import { Play, Stop, Trash, Clock, Cpu, Database, CheckCircle, XCircle, Warning } from '@phosphor-icons/react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';

interface InteractiveDemoProps {
  script: string;
  language: 'python' | 'javascript' | 'typescript' | 'bash';
  onExecute?: (result: ExecutionResult) => void;
}

export interface ExecutionResult {
  stdout: string;
  stderr: string;
  exitCode: number;
  executionTime: number;
  memoryUsage: number;
  cpuUsage: number;
  timestamp: string;
}

type ExecutionStatus = 'idle' | 'running' | 'success' | 'failed' | 'timeout';

export function InteractiveDemo({ script, language, onExecute }: InteractiveDemoProps) {
  const [status, setStatus] = useState<ExecutionStatus>('idle');
  const [result, setResult] = useState<ExecutionResult | null>(null);
  const [output, setOutput] = useState<string>('');
  const [errorOutput, setErrorOutput] = useState<string>('');
  const [progress, setProgress] = useState(0);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [editedScript, setEditedScript] = useState(script);
  
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const startTimeRef = useRef<number>(0);

  useEffect(() => {
    setEditedScript(script);
  }, [script]);

  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, []);

  const simulateExecution = useCallback(async () => {
    const startTime = Date.now();
    startTimeRef.current = startTime;
    
    setStatus('running');
    setOutput('');
    setErrorOutput('');
    setProgress(0);
    setElapsedTime(0);

    if (timerRef.current) {
      clearInterval(timerRef.current);
    }

    timerRef.current = setInterval(() => {
      const elapsed = Date.now() - startTimeRef.current;
      setElapsedTime(elapsed);
      setProgress(Math.min((elapsed / 3000) * 100, 95));
    }, 50);

    try {
      const prompt = spark.llmPrompt`You are a code execution simulator. Analyze this ${language} code and simulate its execution output:

${editedScript}

Provide realistic output that this code would produce when executed, including:
1. Console output (stdout)
2. Any warnings or info messages
3. Expected return values or results

Format your response as if you're showing the actual program output. Be concise but realistic.`;

      const executionOutput = await spark.llm(prompt, "gpt-4o-mini");

      await new Promise(resolve => setTimeout(resolve, 800));

      const executionTime = Date.now() - startTime;
      const memoryUsage = 12 + Math.random() * 40;
      const cpuUsage = 15 + Math.random() * 45;

      const lines = executionOutput.split('\n');
      let stdout = '';
      let stderr = '';

      for (const line of lines) {
        if (line.toLowerCase().includes('error') || line.toLowerCase().includes('warning')) {
          stderr += line + '\n';
        } else {
          stdout += line + '\n';
        }
      }

      const executionResult: ExecutionResult = {
        stdout: stdout.trim() || executionOutput,
        stderr: stderr.trim(),
        exitCode: stderr ? 1 : 0,
        executionTime,
        memoryUsage: Math.round(memoryUsage * 100) / 100,
        cpuUsage: Math.round(cpuUsage * 100) / 100,
        timestamp: new Date().toISOString(),
      };

      setOutput(executionResult.stdout);
      setErrorOutput(executionResult.stderr);
      setResult(executionResult);
      setStatus(executionResult.exitCode === 0 ? 'success' : 'failed');
      setProgress(100);

      if (timerRef.current) {
        clearInterval(timerRef.current);
      }

      if (onExecute) {
        onExecute(executionResult);
      }

      toast.success('Execution completed', {
        description: `Completed in ${executionResult.executionTime}ms`,
      });
    } catch (error) {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }

      const errorMessage = error instanceof Error ? error.message : 'Execution failed';
      setErrorOutput(errorMessage);
      setStatus('failed');
      setProgress(100);

      toast.error('Execution failed', {
        description: errorMessage,
      });
    }
  }, [editedScript, language, onExecute]);

  const handleStop = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }
    setStatus('idle');
    setProgress(0);
    toast.info('Execution stopped');
  }, []);

  const handleClear = useCallback(() => {
    setOutput('');
    setErrorOutput('');
    setResult(null);
    setStatus('idle');
    setProgress(0);
    setElapsedTime(0);
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }
  }, []);

  const getStatusBadge = () => {
    switch (status) {
      case 'running':
        return (
          <Badge className="bg-blue-500/20 text-blue-600 border-blue-500/30">
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse mr-2" />
            Running
          </Badge>
        );
      case 'success':
        return (
          <Badge className="bg-green-500/20 text-green-600 border-green-500/30">
            <CheckCircle weight="fill" className="w-3 h-3 mr-1" />
            Success
          </Badge>
        );
      case 'failed':
        return (
          <Badge className="bg-red-500/20 text-red-600 border-red-500/30">
            <XCircle weight="fill" className="w-3 h-3 mr-1" />
            Failed
          </Badge>
        );
      case 'timeout':
        return (
          <Badge className="bg-yellow-500/20 text-yellow-600 border-yellow-500/30">
            <Warning weight="fill" className="w-3 h-3 mr-1" />
            Timeout
          </Badge>
        );
      default:
        return (
          <Badge variant="outline">
            Idle
          </Badge>
        );
    }
  };

  const formatTime = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };

  return (
    <div className="space-y-4">
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <h3 className="text-xl font-semibold">Interactive Execution</h3>
            {getStatusBadge()}
          </div>
          <div className="flex items-center gap-2">
            <Button
              onClick={simulateExecution}
              disabled={status === 'running'}
              size="sm"
              className="gap-2"
            >
              <Play weight="fill" className="w-4 h-4" />
              Execute
            </Button>
            <Button
              onClick={handleStop}
              disabled={status !== 'running'}
              size="sm"
              variant="outline"
              className="gap-2"
            >
              <Stop weight="fill" className="w-4 h-4" />
              Stop
            </Button>
            <Button
              onClick={handleClear}
              disabled={status === 'running'}
              size="sm"
              variant="outline"
              className="gap-2"
            >
              <Trash weight="fill" className="w-4 h-4" />
              Clear
            </Button>
          </div>
        </div>

        {status === 'running' && (
          <div className="space-y-2 mb-4">
            <div className="flex items-center justify-between text-sm text-muted-foreground">
              <span>Executing...</span>
              <span>{formatTime(elapsedTime)}</span>
            </div>
            <Progress value={progress} className="h-2" />
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Code</label>
            <Textarea
              value={editedScript}
              onChange={(e) => setEditedScript(e.target.value)}
              disabled={status === 'running'}
              className="font-mono text-sm min-h-[400px] resize-none"
              placeholder="Enter code to execute..."
            />
          </div>

          <div className="space-y-4">
            <Tabs defaultValue="output" className="w-full">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="output">Output</TabsTrigger>
                <TabsTrigger value="errors">Errors</TabsTrigger>
                <TabsTrigger value="metrics">Metrics</TabsTrigger>
              </TabsList>

              <TabsContent value="output" className="mt-4">
                <div className="bg-muted rounded-lg p-4 min-h-[200px] max-h-[400px] overflow-auto font-mono text-sm">
                  {output ? (
                    <pre className="whitespace-pre-wrap text-foreground">{output}</pre>
                  ) : (
                    <p className="text-muted-foreground italic">No output yet. Click Execute to run the code.</p>
                  )}
                </div>
              </TabsContent>

              <TabsContent value="errors" className="mt-4">
                <div className="bg-muted rounded-lg p-4 min-h-[200px] max-h-[400px] overflow-auto font-mono text-sm">
                  {errorOutput ? (
                    <pre className="whitespace-pre-wrap text-destructive">{errorOutput}</pre>
                  ) : (
                    <p className="text-muted-foreground italic">No errors</p>
                  )}
                </div>
              </TabsContent>

              <TabsContent value="metrics" className="mt-4">
                {result ? (
                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                      <div className="flex items-center gap-2">
                        <Clock className="w-5 h-5 text-muted-foreground" />
                        <span className="text-sm font-medium">Execution Time</span>
                      </div>
                      <span className="text-sm font-mono">{formatTime(result.executionTime)}</span>
                    </div>

                    <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                      <div className="flex items-center gap-2">
                        <Database className="w-5 h-5 text-muted-foreground" />
                        <span className="text-sm font-medium">Memory Usage</span>
                      </div>
                      <span className="text-sm font-mono">{result.memoryUsage.toFixed(2)} MB</span>
                    </div>

                    <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                      <div className="flex items-center gap-2">
                        <Cpu className="w-5 h-5 text-muted-foreground" />
                        <span className="text-sm font-medium">CPU Usage</span>
                      </div>
                      <span className="text-sm font-mono">{result.cpuUsage.toFixed(2)}%</span>
                    </div>

                    <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                      <div className="flex items-center gap-2">
                        <CheckCircle className="w-5 h-5 text-muted-foreground" />
                        <span className="text-sm font-medium">Exit Code</span>
                      </div>
                      <span className={`text-sm font-mono ${result.exitCode === 0 ? 'text-green-600' : 'text-destructive'}`}>
                        {result.exitCode}
                      </span>
                    </div>
                  </div>
                ) : (
                  <p className="text-muted-foreground italic p-4">No execution metrics available</p>
                )}
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </Card>

      {result && status !== 'idle' && (
        <Card className="p-4 bg-muted/30">
          <div className="flex items-start gap-3">
            {status === 'success' ? (
              <CheckCircle weight="fill" className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
            ) : (
              <XCircle weight="fill" className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
            )}
            <div>
              <p className="font-semibold text-sm">
                {status === 'success' ? 'Execution Successful' : 'Execution Failed'}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                {status === 'success'
                  ? `Completed in ${formatTime(result.executionTime)} with exit code ${result.exitCode}`
                  : `Failed with exit code ${result.exitCode}`}
              </p>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
