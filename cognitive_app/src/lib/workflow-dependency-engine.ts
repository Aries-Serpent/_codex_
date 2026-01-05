export interface WorkflowToken {
  id: string;
  name: string;
  icon: string;
  description: string;
  paradigms: string[];
  stages: string[];
  color: string;
  createdAt?: number;
  dependencies?: string[];
  outputs?: string[];
  triggers?: TriggerCondition[];
  priority?: number;
}

export interface TriggerCondition {
  type: 'on_complete' | 'on_failure' | 'on_output' | 'time_delay' | 'manual';
  tokenId?: string;
  outputKey?: string;
  delayMs?: number;
}

export interface WorkflowExecution {
  tokenId: string;
  currentStage: number;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'blocked';
  startTime?: number;
  endTime?: number;
  outputs?: Record<string, any>;
  blockedBy?: string[];
  triggeredBy?: string;
}

export interface OrchestrationChain {
  id: string;
  name: string;
  description: string;
  tokens: string[];
  autoExecute: boolean;
  createdAt: number;
}

export class WorkflowDependencyEngine {
  private executions: Map<string, WorkflowExecution> = new Map();
  private completionCallbacks: Map<string, ((execution: WorkflowExecution) => void)[]> = new Map();

  analyzeDependencies(token: WorkflowToken, allTokens: WorkflowToken[]): {
    dependencies: WorkflowToken[];
    dependents: WorkflowToken[];
    canExecute: boolean;
    blockedReason?: string;
  } {
    const dependencies = token.dependencies
      ? allTokens.filter(t => token.dependencies!.includes(t.id))
      : [];

    const dependents = allTokens.filter(t => 
      t.dependencies?.includes(token.id)
    );

    const canExecute = dependencies.every(dep => {
      const execution = this.executions.get(dep.id);
      return execution?.status === 'completed';
    });

    const blockedReason = !canExecute
      ? `Waiting for: ${dependencies.filter(d => {
          const exec = this.executions.get(d.id);
          return exec?.status !== 'completed';
        }).map(d => d.name).join(', ')}`
      : undefined;

    return { dependencies, dependents, canExecute, blockedReason };
  }

  buildExecutionChain(
    startTokenId: string,
    allTokens: WorkflowToken[]
  ): WorkflowToken[] {
    const chain: WorkflowToken[] = [];
    const visited = new Set<string>();
    const visiting = new Set<string>();

    const visit = (tokenId: string) => {
      if (visited.has(tokenId)) return;
      if (visiting.has(tokenId)) {
        throw new Error(`Circular dependency detected involving ${tokenId}`);
      }

      const token = allTokens.find(t => t.id === tokenId);
      if (!token) return;

      visiting.add(tokenId);

      if (token.dependencies) {
        token.dependencies.forEach(depId => visit(depId));
      }

      visiting.delete(tokenId);
      visited.add(tokenId);
      chain.push(token);
    };

    visit(startTokenId);
    return chain;
  }

  sortByPriority(tokens: WorkflowToken[]): WorkflowToken[] {
    return [...tokens].sort((a, b) => {
      const priorityA = a.priority ?? 50;
      const priorityB = b.priority ?? 50;
      return priorityB - priorityA;
    });
  }

  createExecution(tokenId: string): WorkflowExecution {
    const execution: WorkflowExecution = {
      tokenId,
      currentStage: 0,
      status: 'pending',
      outputs: {},
    };
    this.executions.set(`${tokenId}-${Date.now()}`, execution);
    return execution;
  }

  startExecution(executionKey: string) {
    const execution = this.executions.get(executionKey);
    if (execution) {
      execution.status = 'running';
      execution.startTime = Date.now();
    }
  }

  completeExecution(executionKey: string, outputs?: Record<string, any>) {
    const execution = this.executions.get(executionKey);
    if (execution) {
      execution.status = 'completed';
      execution.endTime = Date.now();
      execution.outputs = outputs;

      const callbacks = this.completionCallbacks.get(execution.tokenId) || [];
      callbacks.forEach(cb => cb(execution));
    }
  }

  failExecution(executionKey: string, error: string) {
    const execution = this.executions.get(executionKey);
    if (execution) {
      execution.status = 'failed';
      execution.endTime = Date.now();
      execution.outputs = { error };
    }
  }

  onTokenComplete(tokenId: string, callback: (execution: WorkflowExecution) => void) {
    if (!this.completionCallbacks.has(tokenId)) {
      this.completionCallbacks.set(tokenId, []);
    }
    this.completionCallbacks.get(tokenId)!.push(callback);
  }

  checkTriggers(
    token: WorkflowToken,
    completedExecution: WorkflowExecution
  ): boolean {
    if (!token.triggers || token.triggers.length === 0) return false;

    return token.triggers.some(trigger => {
      switch (trigger.type) {
        case 'on_complete':
          return trigger.tokenId === completedExecution.tokenId &&
                 completedExecution.status === 'completed';
        
        case 'on_failure':
          return trigger.tokenId === completedExecution.tokenId &&
                 completedExecution.status === 'failed';
        
        case 'on_output':
          return trigger.tokenId === completedExecution.tokenId &&
                 trigger.outputKey &&
                 completedExecution.outputs?.[trigger.outputKey] !== undefined;
        
        default:
          return false;
      }
    });
  }

  detectCircularDependencies(tokens: WorkflowToken[]): string[] {
    const cycles: string[] = [];

    tokens.forEach(token => {
      try {
        this.buildExecutionChain(token.id, tokens);
      } catch (error) {
        if (error instanceof Error && error.message.includes('Circular dependency')) {
          cycles.push(token.id);
        }
      }
    });

    return cycles;
  }

  suggestOptimizations(chain: OrchestrationChain, allTokens: WorkflowToken[]): string[] {
    const suggestions: string[] = [];
    const chainTokens = allTokens.filter(t => chain.tokens.includes(t.id));

    const paradigmCounts = new Map<string, number>();
    chainTokens.forEach(token => {
      token.paradigms.forEach(p => {
        paradigmCounts.set(p, (paradigmCounts.get(p) || 0) + 1);
      });
    });

    const maxParadigm = Array.from(paradigmCounts.entries())
      .sort((a, b) => b[1] - a[1])[0];

    if (maxParadigm && maxParadigm[1] / chainTokens.length > 0.6) {
      suggestions.push(`Consider rebalancing: ${maxParadigm[0]} paradigm is used in ${Math.round(maxParadigm[1] / chainTokens.length * 100)}% of tokens`);
    }

    const parallelizable = chainTokens.filter(t => !t.dependencies || t.dependencies.length === 0);
    if (parallelizable.length > 1) {
      suggestions.push(`${parallelizable.length} tokens can run in parallel at the start`);
    }

    const totalStages = chainTokens.reduce((sum, t) => sum + t.stages.length, 0);
    if (totalStages > 20) {
      suggestions.push(`Long chain detected (${totalStages} stages). Consider splitting into sub-chains`);
    }

    return suggestions;
  }

  calculateChainMetrics(chain: OrchestrationChain, allTokens: WorkflowToken[]): {
    totalStages: number;
    estimatedDuration: number;
    paradigmsUsed: string[];
    parallelizableTokens: number;
    criticalPathLength: number;
  } {
    const chainTokens = allTokens.filter(t => chain.tokens.includes(t.id));
    
    const totalStages = chainTokens.reduce((sum, t) => sum + t.stages.length, 0);
    const estimatedDuration = totalStages * 1500;

    const paradigmsUsed = Array.from(new Set(
      chainTokens.flatMap(t => t.paradigms)
    ));

    const parallelizableTokens = chainTokens.filter(t => 
      !t.dependencies || t.dependencies.length === 0
    ).length;

    const criticalPathLength = this.calculateCriticalPath(chainTokens);

    return {
      totalStages,
      estimatedDuration,
      paradigmsUsed,
      parallelizableTokens,
      criticalPathLength,
    };
  }

  private calculateCriticalPath(tokens: WorkflowToken[]): number {
    const depths = new Map<string, number>();
    
    const calculateDepth = (token: WorkflowToken): number => {
      if (depths.has(token.id)) {
        return depths.get(token.id)!;
      }

      if (!token.dependencies || token.dependencies.length === 0) {
        depths.set(token.id, token.stages.length);
        return token.stages.length;
      }

      const dependencyTokens = tokens.filter(t => token.dependencies!.includes(t.id));
      const maxDepth = Math.max(...dependencyTokens.map(calculateDepth));
      const totalDepth = maxDepth + token.stages.length;
      depths.set(token.id, totalDepth);
      return totalDepth;
    };

    return Math.max(...tokens.map(calculateDepth));
  }

  clearExecutions() {
    this.executions.clear();
  }

  getActiveExecutions(): WorkflowExecution[] {
    return Array.from(this.executions.values()).filter(
      e => e.status === 'running' || e.status === 'pending'
    );
  }

  getExecutionHistory(): WorkflowExecution[] {
    return Array.from(this.executions.values()).filter(
      e => e.status === 'completed' || e.status === 'failed'
    );
  }
}

export const workflowDependencyEngine = new WorkflowDependencyEngine();
