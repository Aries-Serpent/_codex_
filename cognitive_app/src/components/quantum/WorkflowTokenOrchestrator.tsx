import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Lightning, ArrowRight, CheckCircle, Circle, Link, GitBranch } from '@phosphor-icons/react';
import { useState } from 'react';
import { toast } from 'sonner';
import { motion, AnimatePresence } from 'framer-motion';
import { useAgentOrchestration } from '@/hooks/use-agent-orchestration';
import { WorkflowTokenFlowVisualizer } from './WorkflowTokenFlowVisualizer';
import { CustomWorkflowTokenCreator } from './CustomWorkflowTokenCreator';
import { WorkflowTemplatesLibrary } from './WorkflowTemplatesLibrary';
import { OrchestrationChainBuilder } from './OrchestrationChainBuilder';
import { DependencyGraphVisualizer } from './DependencyGraphVisualizer';
import { ExecutionQueueMonitor } from './ExecutionQueueMonitor';
import { CascadingExecutionMonitor } from './CascadingExecutionMonitor';
import { CascadeWaterfallVisualizer } from './CascadeWaterfallVisualizer';
import { Agent } from '@/lib/codex-api-client';
import { useKV } from '@github/spark/hooks';
import { WorkflowToken, OrchestrationChain, workflowDependencyEngine } from '@/lib/workflow-dependency-engine';

const WORKFLOW_TOKENS: WorkflowToken[] = [
  {
    id: 'AUDIT_EXEC',
    name: 'Audit Execute',
    icon: '🔍',
    description: 'Full system audit pipeline',
    paradigms: ['chaos', 'fractal', 'electromagnetic'],
    stages: ['Scan', 'Analyze', 'Report'],
    color: 'from-blue-500 to-cyan-500',
    priority: 80,
    outputs: ['audit_report'],
  },
  {
    id: 'DOC_GEN',
    name: 'Doc Generate',
    icon: '📚',
    description: 'Automated documentation',
    paradigms: ['fluid', 'wave'],
    stages: ['Extract', 'Structure', 'Format'],
    color: 'from-green-500 to-emerald-500',
    dependencies: ['AUDIT_EXEC'],
    priority: 60,
  },
  {
    id: 'HEAL',
    name: 'Self-Heal',
    icon: '🔧',
    description: 'System repair operations',
    paradigms: ['chaos', 'relativity'],
    stages: ['Detect', 'Isolate', 'Fix'],
    color: 'from-orange-500 to-red-500',
    dependencies: ['AUDIT_EXEC'],
    priority: 90,
  },
  {
    id: 'DECIDE',
    name: 'Quantum Decide',
    icon: '⚛️',
    description: 'Multi-factor decision-making',
    paradigms: ['wave', 'electromagnetic', 'relativity'],
    stages: ['Model', 'Simulate', 'Collapse'],
    color: 'from-purple-500 to-pink-500',
    priority: 70,
  },
  {
    id: 'ORGANIZE',
    name: 'Organize Code',
    icon: '🗂️',
    description: 'Structure optimization',
    paradigms: ['fractal', 'fluid'],
    stages: ['Map', 'Cluster', 'Refactor'],
    color: 'from-indigo-500 to-violet-500',
    dependencies: ['DECIDE'],
    priority: 50,
  },
  {
    id: 'REVIEW',
    name: 'Code Review',
    icon: '✅',
    description: 'Automated quality check',
    paradigms: ['chaos', 'wave', 'fractal'],
    stages: ['Parse', 'Analyze', 'Score'],
    color: 'from-teal-500 to-cyan-500',
    dependencies: ['ORGANIZE', 'HEAL'],
    priority: 40,
  },
];

interface WorkflowExecution {
  executionKey: string;
  tokenId: string;
  currentStage: number;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'blocked';
  startTime?: number;
  endTime?: number;
  blockedBy?: string[];
}

export function WorkflowTokenOrchestrator() {
  const { orchestrateTask, orchestrating, state } = useAgentOrchestration();
  const [customTokens] = useKV<WorkflowToken[]>('custom-workflow-tokens', []);
  const [executions, setExecutions] = useState<WorkflowExecution[]>([]);
  const [selectedToken, setSelectedToken] = useState<string | null>(null);
  const [activeWorkflow, setActiveWorkflow] = useState<string | undefined>(undefined);

  const allTokens = [...WORKFLOW_TOKENS, ...(customTokens || [])];

  const handleExecuteWorkflow = async (token: WorkflowToken) => {
    const analysis = workflowDependencyEngine.analyzeDependencies(token, allTokens);
    
    if (!analysis.canExecute) {
      toast.error('Cannot execute workflow', {
        description: analysis.blockedReason,
      });
      return;
    }

    const executionKey = `${token.id}-${Date.now()}`;
    
    const newExecution: WorkflowExecution = {
      executionKey,
      tokenId: token.id,
      currentStage: 0,
      status: 'running',
      startTime: Date.now(),
    };

    setExecutions(prev => [...prev, newExecution]);
    setSelectedToken(token.id);
    setActiveWorkflow(token.id);

    toast.info(`${token.name} started`, {
      description: 'Orchestrating agents across paradigms',
    });

    for (let i = 0; i < token.stages.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 1500));
      setExecutions(prev => 
        prev.map(ex => 
          ex.executionKey === executionKey
            ? { ...ex, currentStage: i + 1 }
            : ex
        )
      );
    }

    const success = await orchestrateTask(`Execute workflow: ${token.id}`, token.id);

    setExecutions(prev => 
      prev.map(ex => 
        ex.executionKey === executionKey
          ? { ...ex, status: success ? 'completed' : 'failed', endTime: Date.now() }
          : ex
      )
    );

    if (success) {
      toast.success(`${token.name} completed`, {
        description: 'All stages executed successfully',
      });
      
      analysis.dependents.forEach(dependent => {
        const depAnalysis = workflowDependencyEngine.analyzeDependencies(dependent, allTokens);
        if (depAnalysis.canExecute) {
          toast.info(`Auto-triggering ${dependent.name}`, {
            description: 'All dependencies satisfied',
          });
          setTimeout(() => handleExecuteWorkflow(dependent), 1000);
        }
      });
    } else {
      toast.error(`${token.name} failed`, {
        description: 'Workflow execution encountered errors',
      });
    }

    setTimeout(() => {
      setExecutions(prev => 
        prev.filter(ex => ex.executionKey !== executionKey)
      );
      if (activeWorkflow === token.id) {
        setActiveWorkflow(undefined);
      }
    }, 5000);
  };

  const handleExecuteChain = async (chain: OrchestrationChain) => {
    try {
      const chainTokens = chain.tokens
        .map(id => allTokens.find(t => t.id === id))
        .filter(Boolean) as WorkflowToken[];

      const executionOrder = workflowDependencyEngine.buildExecutionChain(
        chainTokens[chainTokens.length - 1].id,
        allTokens
      );

      for (const token of executionOrder) {
        if (!chain.tokens.includes(token.id)) continue;
        await handleExecuteWorkflow(token);
        await new Promise(resolve => setTimeout(resolve, 2000));
      }

      toast.success(`Chain ${chain.name} completed`);
    } catch (error) {
      toast.error('Chain execution failed', {
        description: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  };

  const getTokenExecution = (tokenId: string) => {
    return executions.find(ex => ex.tokenId === tokenId && (ex.status === 'running' || ex.status === 'pending'));
  };

  const selected = allTokens.find(t => t.id === selectedToken);
  const agents: Agent[] = state?.agents || [];

  const completedTokenIds = new Set(
    executions.filter(ex => ex.status === 'completed').map(ex => ex.tokenId)
  );
  const executingTokenIds = new Set(
    executions.filter(ex => ex.status === 'running').map(ex => ex.tokenId)
  );

  const queuedExecutions = executions.map(ex => {
    const token = allTokens.find(t => t.id === ex.tokenId);
    return {
      tokenId: ex.tokenId,
      tokenName: token?.name || ex.tokenId,
      tokenIcon: token?.icon || '📦',
      status: ex.status,
      progress: token ? Math.round((ex.currentStage / token.stages.length) * 100) : 0,
      blockedBy: ex.blockedBy,
      startTime: ex.startTime,
      estimatedCompletion: ex.startTime && token 
        ? ex.startTime + (token.stages.length * 1500)
        : undefined,
    };
  });

  return (
    <div className="space-y-6">
      <ExecutionQueueMonitor executions={queuedExecutions} />
      
      <Tabs defaultValue="cascade" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="cascade" className="flex items-center gap-2">
            <Lightning weight="duotone" className="w-4 h-4" />
            Cascade
          </TabsTrigger>
          <TabsTrigger value="tokens" className="flex items-center gap-2">
            <Lightning weight="duotone" className="w-4 h-4" />
            Tokens
          </TabsTrigger>
          <TabsTrigger value="chains" className="flex items-center gap-2">
            <Link weight="duotone" className="w-4 h-4" />
            Chains
          </TabsTrigger>
          <TabsTrigger value="dependencies" className="flex items-center gap-2">
            <GitBranch weight="duotone" className="w-4 h-4" />
            Graph
          </TabsTrigger>
        </TabsList>

        <TabsContent value="cascade" className="space-y-6 mt-6">
          <CascadeWaterfallVisualizer 
            tokens={allTokens}
            activeTokens={executingTokenIds}
            completedTokens={completedTokenIds}
          />
          
          <CascadingExecutionMonitor 
            tokens={allTokens}
            onExecuteToken={async (token) => {
              const success = await orchestrateTask(`Execute workflow: ${token.id}`, token.id);
              return success;
            }}
            showVisualization={true}
          />
        </TabsContent>

        <TabsContent value="tokens" className="space-y-6 mt-6">
          <WorkflowTemplatesLibrary />
          
          <CustomWorkflowTokenCreator />

      <Card className="p-6 bg-gradient-to-br from-card via-card to-[oklch(0.28_0.03_260)]">
        <div className="flex items-center gap-3 mb-6">
          <div className="flex items-center justify-center w-12 h-12 bg-accent/20 backdrop-blur-sm rounded-lg">
            <Lightning weight="duotone" className="w-7 h-7 text-accent" />
          </div>
          <div>
            <h2 className="text-2xl font-semibold text-accent">Workflow Token Orchestrator</h2>
            <p className="text-sm text-muted-foreground">
              Execute cross-paradigm workflows with intelligent agent collaboration
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {allTokens.map((token) => {
            const execution = getTokenExecution(token.id);
            const isExecuting = !!execution;
            const isSelected = selectedToken === token.id;

            return (
              <motion.div
                key={token.id}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Card 
                  className={`p-4 cursor-pointer transition-all ${
                    isSelected ? 'ring-2 ring-accent shadow-lg' : ''
                  } ${isExecuting ? 'border-accent' : ''}`}
                  onClick={() => setSelectedToken(token.id)}
                >
                  <div className="flex items-start justify-between mb-3">
                    <span className="text-3xl">{token.icon}</span>
                    <div className="flex gap-1">
                      {token.createdAt && (
                        <Badge variant="outline" className="text-xs bg-primary/20 text-primary border-primary">
                          Custom
                        </Badge>
                      )}
                      {isExecuting && (
                        <Badge variant="outline" className="bg-accent/20 text-accent border-accent">
                          Running
                        </Badge>
                      )}
                    </div>
                  </div>

                  <h3 className="font-semibold text-lg mb-1">{token.name}</h3>
                  <p className="text-sm text-muted-foreground mb-3">{token.description}</p>

                  <div className="flex flex-wrap gap-1 mb-3">
                    {token.paradigms.map(paradigm => (
                      <Badge key={paradigm} variant="secondary" className="text-xs">
                        {paradigm}
                      </Badge>
                    ))}
                  </div>

                  {isExecuting && execution && (
                    <div className="space-y-2 mb-3">
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-muted-foreground">Progress</span>
                        <span className="font-mono font-semibold">
                          {execution.currentStage}/{token.stages.length}
                        </span>
                      </div>
                      <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                        <motion.div
                          className={`h-full bg-gradient-to-r ${token.color}`}
                          initial={{ width: 0 }}
                          animate={{ width: `${(execution.currentStage / token.stages.length) * 100}%` }}
                          transition={{ duration: 0.5 }}
                        />
                      </div>
                    </div>
                  )}

                  <Button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleExecuteWorkflow(token);
                    }}
                    disabled={orchestrating || isExecuting}
                    className="w-full"
                    variant={isExecuting ? "outline" : "default"}
                  >
                    {isExecuting ? (
                      <>
                        <Circle weight="fill" className="w-4 h-4 mr-2 animate-pulse" />
                        Executing
                      </>
                    ) : (
                      <>
                        <Lightning weight="duotone" className="w-4 h-4 mr-2" />
                        Execute
                      </>
                    )}
                  </Button>
                </Card>
              </motion.div>
            );
          })}
        </div>
      </Card>

      <WorkflowTokenFlowVisualizer agents={agents} activeWorkflow={activeWorkflow} />

      <AnimatePresence>
        {selected && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <span className="text-2xl">{selected.icon}</span>
                {selected.name} Pipeline
              </h3>

              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-semibold text-muted-foreground mb-2">Execution Stages</h4>
                  <div className="flex items-center gap-2">
                    {selected.stages.map((stage, idx) => {
                      const execution = getTokenExecution(selected.id);
                      const isCompleted = execution ? execution.currentStage > idx : false;
                      const isCurrent = execution ? execution.currentStage === idx : false;

                      return (
                        <div key={stage} className="flex items-center gap-2 flex-1">
                          <div className="flex-1">
                            <Card className={`p-3 ${isCurrent ? 'border-accent shadow-md' : ''}`}>
                              <div className="flex items-center gap-2">
                                {isCompleted ? (
                                  <CheckCircle weight="fill" className="w-4 h-4 text-green-500 flex-shrink-0" />
                                ) : isCurrent ? (
                                  <Circle weight="fill" className="w-4 h-4 text-accent animate-pulse flex-shrink-0" />
                                ) : (
                                  <Circle weight="regular" className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                                )}
                                <span className={`text-sm font-medium ${
                                  isCurrent ? 'text-accent' : isCompleted ? 'text-green-500' : 'text-muted-foreground'
                                }`}>
                                  {stage}
                                </span>
                              </div>
                            </Card>
                          </div>
                          {idx < selected.stages.length - 1 && (
                            <ArrowRight weight="bold" className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-semibold text-muted-foreground mb-2">Dependencies</h4>
                  {selected.dependencies && selected.dependencies.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                      {selected.dependencies.map(depId => {
                        const depToken = allTokens.find(t => t.id === depId);
                        return depToken ? (
                          <Badge key={depId} variant="outline" className="flex items-center gap-1">
                            <span>{depToken.icon}</span>
                            <span>{depToken.name}</span>
                          </Badge>
                        ) : null;
                      })}
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground">No dependencies</p>
                  )}
                </div>

                <div>
                  <h4 className="text-sm font-semibold text-muted-foreground mb-2">Active Physics Paradigms</h4>
                  <div className="grid grid-cols-3 gap-2">
                    {selected.paradigms.map((paradigm) => (
                      <Card key={paradigm} className="p-3 text-center">
                        <p className="text-xs font-medium capitalize">{paradigm}</p>
                      </Card>
                    ))}
                  </div>
                </div>
              </div>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
        </TabsContent>

        <TabsContent value="chains" className="space-y-6 mt-6">
          <OrchestrationChainBuilder 
            allTokens={allTokens} 
            onChainExecute={handleExecuteChain}
          />
        </TabsContent>

        <TabsContent value="dependencies" className="space-y-6 mt-6">
          <DependencyGraphVisualizer 
            tokens={allTokens}
            highlightedToken={selectedToken || undefined}
            executingTokens={executingTokenIds}
            completedTokens={completedTokenIds}
          />
        </TabsContent>
      </Tabs>
    </div>
  );
}
