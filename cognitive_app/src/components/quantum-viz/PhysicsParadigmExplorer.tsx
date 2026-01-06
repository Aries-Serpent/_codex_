import { Card } from '@/components/ui/card';
import { Agent } from '@/lib/codex-api-client';

interface PhysicsParadigmExplorerProps {
  agents: Agent[];
}

const PARADIGM_INFO = {
  chaos: {
    icon: '🌀',
    name: 'Chaos Theory',
    description: 'Lyapunov exponent for instability detection',
    metric: 'Bifurcation Analysis',
  },
  fractal: {
    icon: '🔺',
    name: 'Fractal Geometry',
    description: 'Self-similar pattern recognition',
    metric: 'Box-Counting Dimension',
  },
  fluid: {
    icon: '💧',
    name: 'Fluid Dynamics',
    description: 'Flow optimization via Navier-Stokes',
    metric: 'Reynolds Number',
  },
  electromagnetic: {
    icon: '⚡',
    name: 'Electromagnetism',
    description: 'Field analysis using Poisson equation',
    metric: 'Field Strength',
  },
  wave: {
    icon: '〰️',
    name: 'Wave Propagation',
    description: 'Frequency and amplitude analysis',
    metric: 'Phase Coherence',
  },
  relativity: {
    icon: '⏰',
    name: 'Relativity',
    description: 'Time dilation and causal ordering',
    metric: 'Lorentz Transform',
  },
};

export function PhysicsParadigmExplorer({ agents }: PhysicsParadigmExplorerProps) {
  const paradigmCounts = agents.reduce((acc, agent) => {
    acc[agent.paradigm] = (acc[agent.paradigm] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return (
    <div>
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <span className="text-2xl">🔬</span>
        Physics Paradigms
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Object.entries(PARADIGM_INFO).map(([key, info]) => {
          const count = paradigmCounts[key] || 0;
          const isActive = count > 0;

          return (
            <Card 
              key={key} 
              className={`p-4 relative overflow-hidden transition-all ${
                isActive ? 'border-accent shadow-md' : 'opacity-60'
              }`}
            >
              {isActive && (
                <div className="absolute inset-0 bg-gradient-to-br from-accent/5 to-primary/5" />
              )}
              
              <div className="relative">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-3xl">{info.icon}</span>
                  {isActive && (
                    <div className="flex items-center gap-1">
                      <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                      <span className="text-xs font-mono font-semibold text-green-500">
                        {count} agent{count !== 1 ? 's' : ''}
                      </span>
                    </div>
                  )}
                </div>

                <h4 className="font-semibold text-lg mb-1">{info.name}</h4>
                <p className="text-sm text-muted-foreground mb-2">{info.description}</p>
                
                <div className="pt-2 border-t border-border">
                  <p className="text-xs text-muted-foreground">
                    <strong className="text-accent">Metric:</strong> {info.metric}
                  </p>
                </div>
              </div>
            </Card>
          );
        })}
      </div>

      <Card className="p-4 mt-4 bg-muted/30">
        <p className="text-sm text-muted-foreground">
          <strong className="text-accent">Physics-Inspired Orchestration:</strong> Agents leverage 
          6 classical physics paradigms to optimize decision-making. Each paradigm provides unique 
          mathematical frameworks for analyzing complexity, flow, patterns, and causality in 
          computational systems.
        </p>
      </Card>
    </div>
  );
}
