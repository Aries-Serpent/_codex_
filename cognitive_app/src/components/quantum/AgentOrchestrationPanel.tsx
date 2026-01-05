import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Robot } from '@phosphor-icons/react';
import { useAgentOrchestration } from '@/hooks/use-agent-orchestration';
import { AgentCard } from './AgentCard';
import { TaskQueue } from './TaskQueue';
import { PhysicsParadigmExplorer } from './PhysicsParadigmExplorer';
import { WorkflowTokenOrchestrator } from './WorkflowTokenOrchestrator';
import { ParadigmCollaborationVisualizer } from './ParadigmCollaborationVisualizer';

export function AgentOrchestrationPanel() {
  const { state, loading, error } = useAgentOrchestration(true, 5000);

  if (loading && !state) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center py-12">
          <Robot weight="duotone" className="w-8 h-8 text-accent animate-pulse" />
          <span className="ml-3 text-muted-foreground">Loading agent system...</span>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="p-6 border-destructive">
        <div className="text-destructive">
          <strong>Error:</strong> {error}
        </div>
      </Card>
    );
  }

  if (!state) return null;

  const activeAgents = state.agents.filter(a => a.status === 'active' || a.status === 'thinking').length;
  const totalAgents = state.agents.length;
  const runningTasks = state.tasks.filter(t => t.status === 'running').length;
  const completedTasks = state.tasks.filter(t => t.status === 'completed').length;

  return (
    <div className="space-y-6">
      <Card className="p-6 bg-gradient-to-br from-card via-card to-[oklch(0.28_0.03_260)]">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-12 h-12 bg-primary/20 backdrop-blur-sm rounded-lg">
              <Robot weight="duotone" className="w-7 h-7 text-primary" />
            </div>
            <div>
              <h2 className="text-2xl font-semibold text-accent">Agent Orchestration Hub</h2>
              <p className="text-sm text-muted-foreground">
                {activeAgents} of {totalAgents} agents active · {runningTasks} tasks running
              </p>
            </div>
          </div>
          <Badge variant="outline" className="border-accent text-accent">
            {completedTasks} Completed
          </Badge>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {state.agents.map((agent) => (
            <AgentCard key={agent.id} agent={agent} />
          ))}
        </div>
      </Card>

      <WorkflowTokenOrchestrator />

      <ParadigmCollaborationVisualizer agents={state.agents} />

      <TaskQueue tasks={state.tasks} />

      <PhysicsParadigmExplorer agents={state.agents} />
    </div>
  );
}
