import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Agent } from '@/lib/codex-api-client';
import { Robot } from '@phosphor-icons/react';

interface AgentCardProps {
  agent: Agent;
}

const PARADIGM_ICONS: Record<string, string> = {
  chaos: '🌀',
  fractal: '🔺',
  fluid: '💧',
  electromagnetic: '⚡',
  wave: '〰️',
  relativity: '⏰',
};

const PARADIGM_COLORS: Record<string, string> = {
  chaos: 'text-red-500',
  fractal: 'text-orange-500',
  fluid: 'text-blue-500',
  electromagnetic: 'text-yellow-500',
  wave: 'text-purple-500',
  relativity: 'text-pink-500',
};

export function AgentCard({ agent }: AgentCardProps) {
  const statusConfig = {
    idle: { color: 'text-muted-foreground', bg: 'bg-muted', label: 'Idle', icon: '⚪' },
    active: { color: 'text-green-500', bg: 'bg-green-500/20', label: 'Active', icon: '🟢' },
    thinking: { color: 'text-yellow-500', bg: 'bg-yellow-500/20', label: 'Thinking', icon: '🟡' },
    error: { color: 'text-red-500', bg: 'bg-red-500/20', label: 'Error', icon: '🔴' },
  };

  const config = statusConfig[agent.status];
  const paradigmIcon = PARADIGM_ICONS[agent.paradigm] || '🤖';
  const paradigmColor = PARADIGM_COLORS[agent.paradigm] || 'text-accent';

  return (
    <Card className={`p-4 relative overflow-hidden group hover:shadow-lg transition-all ${
      agent.status === 'thinking' ? 'agent-thinking' : ''
    }`}>
      <div className={`absolute inset-0 ${config.bg} opacity-10`} />
      
      <div className="relative">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Robot weight="duotone" className="w-5 h-5 text-accent" />
            <h4 className="font-semibold">{agent.name}</h4>
          </div>
          <Badge variant="outline" className={`${config.color} border-current text-xs`}>
            {config.icon} {config.label}
          </Badge>
        </div>

        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="text-2xl">{paradigmIcon}</span>
            <div className="flex-1">
              <p className={`text-sm font-medium ${paradigmColor}`}>
                {agent.paradigm.charAt(0).toUpperCase() + agent.paradigm.slice(1)} Paradigm
              </p>
              <p className="text-xs text-muted-foreground">Physics-inspired optimization</p>
            </div>
          </div>

          {agent.current_task && (
            <div className="pt-2 border-t border-border">
              <p className="text-xs text-muted-foreground mb-1">Current Task:</p>
              <p className="text-sm font-medium truncate">{agent.current_task}</p>
            </div>
          )}
        </div>

        {agent.status === 'active' && (
          <div className="mt-3">
            <div className="h-1 bg-background rounded-full overflow-hidden">
              <div className="h-full bg-green-500 energy-flow w-full" />
            </div>
          </div>
        )}
      </div>
    </Card>
  );
}
