import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { 
  Lightning, 
  CheckCircle, 
  Circle, 
  ArrowRight, 
  Pause, 
  Play,
  Stop,
  Timer,
  GitBranch,
  Rocket
} from '@phosphor-icons/react';
import { motion, AnimatePresence } from 'framer-motion';
import { useState, useEffect } from 'react';
import { WorkflowToken } from '@/lib/workflow-dependency-engine';

interface CascadeNode {
  tokenId: string;
  token: WorkflowToken;
  status: 'waiting' | 'ready' | 'executing' | 'completed' | 'failed';
  progress: number;
  startTime?: number;
  endTime?: number;
  triggeredBy?: string;
  autoTriggered: boolean;
  depth: number;
  parallelGroup: number;
}

interface CascadingExecutionMonitorProps {
  tokens: WorkflowToken[];
  onExecuteToken?: (token: WorkflowToken) => Promise<boolean>;
  showVisualization?: boolean;
}

export function CascadingExecutionMonitor({ 
  tokens,
  onExecuteToken,
  showVisualization = true
}: CascadingExecutionMonitorProps) {
  const [cascadeNodes, setCascadeNodes] = useState<CascadeNode[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [completedCount, setCompletedCount] = useState(0);
  const [totalExecutionTime, setTotalExecutionTime] = useState(0);
  const [cascadeStartTime, setCascadeStartTime] = useState<number | null>(null);

  useEffect(() => {
    if (isRunning && !isPaused && cascadeStartTime) {
      const interval = setInterval(() => {
        setTotalExecutionTime(Date.now() - cascadeStartTime);
      }, 100);
      return () => clearInterval(interval);
    }
  }, [isRunning, isPaused, cascadeStartTime]);

  const calculateCascadeStructure = (): CascadeNode[] => {
    const nodes: CascadeNode[] = [];
    const depths = new Map<string, number>();
    const parallelGroups = new Map<string, number>();
    
    const calculateDepth = (token: WorkflowToken): number => {
      if (depths.has(token.id)) return depths.get(token.id)!;
      
      if (!token.dependencies || token.dependencies.length === 0) {
        depths.set(token.id, 0);
        return 0;
      }
      
      const depTokens = tokens.filter(t => token.dependencies!.includes(t.id));
      const maxDepth = depTokens.length > 0 ? Math.max(...depTokens.map(calculateDepth)) : 0;
      const depth = maxDepth + 1;
      depths.set(token.id, depth);
      return depth;
    };

    tokens.forEach(token => calculateDepth(token));

    const depthGroups = new Map<number, WorkflowToken[]>();
    tokens.forEach(token => {
      const depth = depths.get(token.id) || 0;
      if (!depthGroups.has(depth)) {
        depthGroups.set(depth, []);
      }
      depthGroups.get(depth)!.push(token);
    });

    tokens.forEach(token => {
      const depth = depths.get(token.id) || 0;
      const tokensAtDepth = depthGroups.get(depth) || [];
      const parallelGroup = tokensAtDepth.indexOf(token);
      
      nodes.push({
        tokenId: token.id,
        token,
        status: depth === 0 ? 'ready' : 'waiting',
        progress: 0,
        autoTriggered: false,
        depth,
        parallelGroup,
      });
    });

    return nodes.sort((a, b) => {
      if (a.depth !== b.depth) return a.depth - b.depth;
      return a.parallelGroup - b.parallelGroup;
    });
  };

  const startCascade = async () => {
    const structure = calculateCascadeStructure();
    setCascadeNodes(structure);
    setIsRunning(true);
    setIsPaused(false);
    setCompletedCount(0);
    setCascadeStartTime(Date.now());
    
    await executeCascade(structure);
  };

  const executeCascade = async (nodes: CascadeNode[]) => {
    const nodesToExecute = [...nodes];
    
    while (nodesToExecute.length > 0 && !isPaused) {
      const readyNodes = nodesToExecute.filter(node => {
        if (node.status === 'completed' || node.status === 'failed') return false;
        
        const dependencies = node.token.dependencies || [];
        return dependencies.every(depId => {
          const depNode = cascadeNodes.find(n => n.tokenId === depId);
          return depNode?.status === 'completed';
        });
      });

      if (readyNodes.length === 0) break;

      await Promise.all(
        readyNodes.map(async (node) => {
          updateNodeStatus(node.tokenId, 'executing', 0);
          
          const success = await simulateExecution(node);
          
          updateNodeStatus(
            node.tokenId, 
            success ? 'completed' : 'failed',
            100
          );
          
          if (success) {
            setCompletedCount(prev => prev + 1);
            triggerDependents(node.tokenId);
          }
        })
      );

      nodesToExecute.splice(0, readyNodes.length);
      await new Promise(resolve => setTimeout(resolve, 500));
    }
    
    setIsRunning(false);
  };

  const simulateExecution = async (node: CascadeNode): Promise<boolean> => {
    const stages = node.token.stages.length;
    const stageTime = 800;
    
    for (let i = 0; i < stages; i++) {
      if (isPaused) {
        await new Promise(resolve => {
          const checkPause = setInterval(() => {
            if (!isPaused) {
              clearInterval(checkPause);
              resolve(true);
            }
          }, 100);
        });
      }
      
      const progress = Math.round(((i + 1) / stages) * 100);
      updateNodeStatus(node.tokenId, 'executing', progress);
      await new Promise(resolve => setTimeout(resolve, stageTime));
    }
    
    if (onExecuteToken) {
      return await onExecuteToken(node.token);
    }
    
    return true;
  };

  const updateNodeStatus = (
    tokenId: string, 
    status: CascadeNode['status'], 
    progress: number
  ) => {
    setCascadeNodes(prev => prev.map(node => {
      if (node.tokenId === tokenId) {
        return {
          ...node,
          status,
          progress,
          startTime: status === 'executing' && !node.startTime ? Date.now() : node.startTime,
          endTime: (status === 'completed' || status === 'failed') ? Date.now() : node.endTime,
        };
      }
      return node;
    }));
  };

  const triggerDependents = (completedTokenId: string) => {
    setCascadeNodes(prev => prev.map(node => {
      if (node.token.dependencies?.includes(completedTokenId)) {
        const allDepsComplete = node.token.dependencies.every(depId => {
          const depNode = prev.find(n => n.tokenId === depId);
          return depNode?.status === 'completed';
        });
        
        if (allDepsComplete) {
          return {
            ...node,
            status: 'ready',
            autoTriggered: true,
            triggeredBy: completedTokenId,
          };
        }
      }
      return node;
    }));
  };

  const stopCascade = () => {
    setIsRunning(false);
    setIsPaused(false);
    setCascadeNodes([]);
    setCompletedCount(0);
    setTotalExecutionTime(0);
    setCascadeStartTime(null);
  };

  const togglePause = () => {
    setIsPaused(prev => !prev);
  };

  const formatTime = (ms: number) => {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    const remainingMs = Math.floor((ms % 1000) / 100);
    
    if (minutes > 0) {
      return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}.${remainingMs}`;
    }
    return `${remainingSeconds}.${remainingMs}s`;
  };

  const getNodesByDepth = () => {
    const grouped = new Map<number, CascadeNode[]>();
    cascadeNodes.forEach(node => {
      if (!grouped.has(node.depth)) {
        grouped.set(node.depth, []);
      }
      grouped.get(node.depth)!.push(node);
    });
    return Array.from(grouped.entries()).sort((a, b) => a[0] - b[0]);
  };

  const getStatusColor = (status: CascadeNode['status']) => {
    switch (status) {
      case 'waiting':
        return 'bg-muted border-border text-muted-foreground';
      case 'ready':
        return 'bg-blue-500/10 border-blue-500 text-blue-400';
      case 'executing':
        return 'bg-accent/10 border-accent text-accent';
      case 'completed':
        return 'bg-green-500/10 border-green-500 text-green-500';
      case 'failed':
        return 'bg-destructive/10 border-destructive text-destructive';
    }
  };

  const getStatusIcon = (status: CascadeNode['status']) => {
    switch (status) {
      case 'waiting':
        return <Circle className="w-4 h-4" weight="regular" />;
      case 'ready':
        return <Rocket className="w-4 h-4 animate-bounce" weight="fill" />;
      case 'executing':
        return <Circle className="w-4 h-4 animate-pulse" weight="fill" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4" weight="fill" />;
      case 'failed':
        return <Circle className="w-4 h-4" weight="fill" />;
    }
  };

  const nodesByDepth = getNodesByDepth();
  const totalNodes = cascadeNodes.length;
  const overallProgress = totalNodes > 0 ? Math.round((completedCount / totalNodes) * 100) : 0;

  return (
    <Card className="p-6 bg-gradient-to-br from-card via-[oklch(0.26_0.03_260)] to-[oklch(0.24_0.04_270)]">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-12 h-12 bg-gradient-to-br from-primary to-accent rounded-lg">
            <Lightning weight="duotone" className="w-7 h-7 text-primary-foreground" />
          </div>
          <div>
            <h2 className="text-2xl font-semibold text-primary">Cascading Execution Monitor</h2>
            <p className="text-sm text-muted-foreground">
              Watch tokens auto-trigger as dependencies complete
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {!isRunning ? (
            <Button 
              onClick={startCascade}
              disabled={tokens.length === 0}
              className="flex items-center gap-2"
            >
              <Play weight="fill" className="w-4 h-4" />
              Start Cascade
            </Button>
          ) : (
            <>
              <Button 
                onClick={togglePause}
                variant="outline"
                className="flex items-center gap-2"
              >
                {isPaused ? (
                  <>
                    <Play weight="fill" className="w-4 h-4" />
                    Resume
                  </>
                ) : (
                  <>
                    <Pause weight="fill" className="w-4 h-4" />
                    Pause
                  </>
                )}
              </Button>
              <Button 
                onClick={stopCascade}
                variant="destructive"
                className="flex items-center gap-2"
              >
                <Stop weight="fill" className="w-4 h-4" />
                Stop
              </Button>
            </>
          )}
        </div>
      </div>

      {isRunning && (
        <div className="mb-6 space-y-4">
          <Card className="p-4 bg-card/50 border-2 border-primary/30">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <Timer weight="fill" className="w-5 h-5 text-primary" />
                  <span className="text-2xl font-mono font-bold text-primary">
                    {formatTime(totalExecutionTime)}
                  </span>
                </div>
                <div className="h-8 w-px bg-border" />
                <div className="text-sm">
                  <span className="text-muted-foreground">Progress: </span>
                  <span className="font-mono font-semibold">{completedCount}/{totalNodes}</span>
                  <span className="text-muted-foreground ml-2">({overallProgress}%)</span>
                </div>
              </div>
              {isPaused && (
                <Badge variant="outline" className="border-yellow-500 text-yellow-500">
                  PAUSED
                </Badge>
              )}
            </div>
            <Progress value={overallProgress} className="h-2" />
          </Card>
        </div>
      )}

      {showVisualization && cascadeNodes.length > 0 && (
        <div className="space-y-6 mb-6">
          <AnimatePresence mode="popLayout">
            {nodesByDepth.map(([depth, nodes], depthIndex) => (
              <motion.div
                key={depth}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ delay: depthIndex * 0.1 }}
              >
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="font-mono">
                      Level {depth}
                    </Badge>
                    {nodes.length > 1 && (
                      <Badge variant="secondary" className="text-xs">
                        {nodes.length} parallel
                      </Badge>
                    )}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {nodes.map((node, nodeIndex) => (
                      <motion.div
                        key={node.tokenId}
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: nodeIndex * 0.05 }}
                      >
                        <Card 
                          className={`p-4 border-2 transition-all ${getStatusColor(node.status)}`}
                        >
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <span className="text-2xl">{node.token.icon}</span>
                              <div>
                                <h4 className="font-semibold text-sm">{node.token.name}</h4>
                                {node.autoTriggered && node.triggeredBy && (
                                  <div className="flex items-center gap-1 text-xs text-blue-400 mt-1">
                                    <Lightning weight="fill" className="w-3 h-3" />
                                    <span>Auto-triggered</span>
                                  </div>
                                )}
                              </div>
                            </div>
                            {getStatusIcon(node.status)}
                          </div>

                          {node.status === 'executing' && (
                            <div className="mt-3">
                              <div className="flex items-center justify-between text-xs mb-1">
                                <span className="text-muted-foreground">
                                  {node.token.stages[Math.floor((node.progress / 100) * node.token.stages.length)] || 'Processing'}
                                </span>
                                <span className="font-mono font-semibold">{node.progress}%</span>
                              </div>
                              <Progress value={node.progress} className="h-1.5" />
                            </div>
                          )}

                          {node.status === 'completed' && node.startTime && node.endTime && (
                            <div className="mt-2 text-xs text-green-500 flex items-center gap-1">
                              <Timer weight="fill" className="w-3 h-3" />
                              <span>{formatTime(node.endTime - node.startTime)}</span>
                            </div>
                          )}

                          {node.status === 'waiting' && node.token.dependencies && (
                            <div className="mt-2 text-xs text-muted-foreground">
                              Waiting for {node.token.dependencies.length} {node.token.dependencies.length === 1 ? 'dependency' : 'dependencies'}
                            </div>
                          )}

                          {node.token.dependencies && node.token.dependencies.length > 0 && (
                            <div className="mt-3 pt-3 border-t border-border/50">
                              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                <GitBranch weight="bold" className="w-3 h-3" />
                                <div className="flex flex-wrap gap-1">
                                  {node.token.dependencies.map(depId => {
                                    const depNode = cascadeNodes.find(n => n.tokenId === depId);
                                    return (
                                      <Badge 
                                        key={depId} 
                                        variant="outline" 
                                        className={`text-xs ${
                                          depNode?.status === 'completed' 
                                            ? 'border-green-500/50 text-green-500' 
                                            : ''
                                        }`}
                                      >
                                        {depNode?.token.icon}
                                      </Badge>
                                    );
                                  })}
                                </div>
                              </div>
                            </div>
                          )}
                        </Card>
                      </motion.div>
                    ))}
                  </div>

                  {depthIndex < nodesByDepth.length - 1 && (
                    <div className="flex items-center justify-center py-2">
                      <ArrowRight weight="bold" className="w-6 h-6 text-muted-foreground rotate-90" />
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}

      {cascadeNodes.length === 0 && !isRunning && (
        <div className="text-center py-12">
          <Lightning weight="duotone" className="w-16 h-16 mx-auto mb-4 text-muted-foreground opacity-50" />
          <p className="text-muted-foreground mb-2">No cascade running</p>
          <p className="text-sm text-muted-foreground">
            Click "Start Cascade" to watch automatic execution
          </p>
        </div>
      )}

      {cascadeNodes.length > 0 && !isRunning && completedCount === totalNodes && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <Card className="p-6 bg-gradient-to-br from-green-500/10 to-green-500/5 border-2 border-green-500/30">
            <div className="text-center">
              <CheckCircle weight="fill" className="w-16 h-16 mx-auto mb-4 text-green-500" />
              <h3 className="text-xl font-semibold text-green-500 mb-2">
                Cascade Completed Successfully!
              </h3>
              <div className="flex items-center justify-center gap-6 text-sm">
                <div className="flex items-center gap-2">
                  <Timer weight="fill" className="w-4 h-4 text-green-500" />
                  <span className="text-muted-foreground">Total Time:</span>
                  <span className="font-mono font-semibold">{formatTime(totalExecutionTime)}</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle weight="fill" className="w-4 h-4 text-green-500" />
                  <span className="text-muted-foreground">Tokens:</span>
                  <span className="font-mono font-semibold">{completedCount}</span>
                </div>
              </div>
            </div>
          </Card>
        </motion.div>
      )}
    </Card>
  );
}
