import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Agent } from '@/lib/codex-api-client';
import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

interface CollaborationLink {
  from: string;
  to: string;
  paradigmFrom: string;
  paradigmTo: string;
  strength: number;
}

interface ParadigmCollaborationVisualizerProps {
  agents: Agent[];
}

const PARADIGM_COLORS = {
  chaos: { bg: 'bg-[oklch(0.50_0.25_30)]', border: 'border-[oklch(0.50_0.25_30)]', text: 'text-[oklch(0.50_0.25_30)]' },
  fractal: { bg: 'bg-[oklch(0.55_0.22_60)]', border: 'border-[oklch(0.55_0.22_60)]', text: 'text-[oklch(0.55_0.22_60)]' },
  fluid: { bg: 'bg-[oklch(0.60_0.20_220)]', border: 'border-[oklch(0.60_0.20_220)]', text: 'text-[oklch(0.60_0.20_220)]' },
  electromagnetic: { bg: 'bg-[oklch(0.65_0.20_180)]', border: 'border-[oklch(0.65_0.20_180)]', text: 'text-[oklch(0.65_0.20_180)]' },
  wave: { bg: 'bg-[oklch(0.70_0.18_250)]', border: 'border-[oklch(0.70_0.18_250)]', text: 'text-[oklch(0.70_0.18_250)]' },
  relativity: { bg: 'bg-[oklch(0.50_0.20_320)]', border: 'border-[oklch(0.50_0.20_320)]', text: 'text-[oklch(0.50_0.20_320)]' },
};

const PARADIGM_ICONS = {
  chaos: '🌀',
  fractal: '🔺',
  fluid: '💧',
  electromagnetic: '⚡',
  wave: '〰️',
  relativity: '⏰',
};

export function ParadigmCollaborationVisualizer({ agents }: ParadigmCollaborationVisualizerProps) {
  const [collaborations, setCollaborations] = useState<CollaborationLink[]>([]);
  const [hoveredParadigm, setHoveredParadigm] = useState<string | null>(null);

  useEffect(() => {
    const activeAgents = agents.filter(a => a.status === 'active' || a.status === 'thinking');
    const links: CollaborationLink[] = [];

    for (let i = 0; i < activeAgents.length; i++) {
      for (let j = i + 1; j < activeAgents.length; j++) {
        const agent1 = activeAgents[i];
        const agent2 = activeAgents[j];

        if (agent1.paradigm !== agent2.paradigm) {
          links.push({
            from: agent1.id,
            to: agent2.id,
            paradigmFrom: agent1.paradigm,
            paradigmTo: agent2.paradigm,
            strength: Math.random() * 0.5 + 0.5,
          });
        }
      }
    }

    setCollaborations(links);
  }, [agents]);

  const paradigmGroups = agents.reduce((acc, agent) => {
    if (!acc[agent.paradigm]) {
      acc[agent.paradigm] = [];
    }
    acc[agent.paradigm].push(agent);
    return acc;
  }, {} as Record<string, Agent[]>);

  const activeParadigms = Object.keys(paradigmGroups).filter(
    p => paradigmGroups[p].some(a => a.status === 'active' || a.status === 'thinking')
  );

  const getParadigmPosition = (paradigm: string, index: number) => {
    const angle = (index / activeParadigms.length) * 2 * Math.PI - Math.PI / 2;
    const radius = 140;
    return {
      x: Math.cos(angle) * radius,
      y: Math.sin(angle) * radius,
    };
  };

  return (
    <div className="space-y-6">
      <Card className="p-6 bg-gradient-to-br from-card via-card to-[oklch(0.28_0.03_260)]">
        <div className="flex items-center gap-3 mb-6">
          <div className="flex items-center justify-center w-12 h-12 bg-primary/20 backdrop-blur-sm rounded-lg">
            <span className="text-2xl">🔗</span>
          </div>
          <div>
            <h2 className="text-2xl font-semibold text-accent">Cross-Paradigm Collaboration</h2>
            <p className="text-sm text-muted-foreground">
              Real-time visualization of agent interactions across physics paradigms
            </p>
          </div>
        </div>

        <div className="relative h-[400px] flex items-center justify-center overflow-hidden bg-background/50 rounded-lg border border-border">
          <svg className="absolute inset-0 w-full h-full pointer-events-none">
            <defs>
              <radialGradient id="glow" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stopColor="oklch(0.75 0.15 195)" stopOpacity="0.3" />
                <stop offset="100%" stopColor="oklch(0.75 0.15 195)" stopOpacity="0" />
              </radialGradient>
            </defs>

            {collaborations.map((link, idx) => {
              const fromIdx = activeParadigms.indexOf(link.paradigmFrom);
              const toIdx = activeParadigms.indexOf(link.paradigmTo);
              
              if (fromIdx === -1 || toIdx === -1) return null;

              const fromPos = getParadigmPosition(link.paradigmFrom, fromIdx);
              const toPos = getParadigmPosition(link.paradigmTo, toIdx);

              const isHighlighted = 
                hoveredParadigm === link.paradigmFrom || 
                hoveredParadigm === link.paradigmTo;

              return (
                <motion.line
                  key={`${link.from}-${link.to}-${idx}`}
                  x1={fromPos.x + 200}
                  y1={fromPos.y + 200}
                  x2={toPos.x + 200}
                  y2={toPos.y + 200}
                  stroke={isHighlighted ? 'oklch(0.75 0.15 195)' : 'oklch(0.35 0.02 250)'}
                  strokeWidth={isHighlighted ? 3 : 1.5}
                  strokeOpacity={isHighlighted ? 0.8 : 0.3}
                  strokeDasharray="5,5"
                  initial={{ pathLength: 0, opacity: 0 }}
                  animate={{ 
                    pathLength: 1, 
                    opacity: 1,
                    strokeDashoffset: [0, -10]
                  }}
                  transition={{ 
                    pathLength: { duration: 1, delay: idx * 0.1 },
                    opacity: { duration: 0.5 },
                    strokeDashoffset: { duration: 2, repeat: Infinity, ease: "linear" }
                  }}
                />
              );
            })}
          </svg>

          <div className="relative">
            {activeParadigms.map((paradigm, index) => {
              const pos = getParadigmPosition(paradigm, index);
              const agentsInParadigm = paradigmGroups[paradigm];
              const activeCount = agentsInParadigm.filter(
                a => a.status === 'active' || a.status === 'thinking'
              ).length;
              const colors = PARADIGM_COLORS[paradigm as keyof typeof PARADIGM_COLORS];
              const icon = PARADIGM_ICONS[paradigm as keyof typeof PARADIGM_ICONS];

              return (
                <motion.div
                  key={paradigm}
                  className="absolute"
                  style={{
                    left: `${pos.x}px`,
                    top: `${pos.y}px`,
                    transform: 'translate(-50%, -50%)',
                  }}
                  initial={{ scale: 0, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ delay: index * 0.1, type: 'spring' }}
                  onMouseEnter={() => setHoveredParadigm(paradigm)}
                  onMouseLeave={() => setHoveredParadigm(null)}
                >
                  <Card 
                    className={`p-4 min-w-[120px] text-center cursor-pointer transition-all ${
                      hoveredParadigm === paradigm ? 'ring-2 ring-accent shadow-2xl scale-110' : ''
                    } ${colors.border} border-2`}
                  >
                    <div className="relative">
                      {activeCount > 0 && (
                        <div className="absolute -top-2 -right-2 w-6 h-6 bg-green-500 text-white text-xs font-bold rounded-full flex items-center justify-center animate-pulse">
                          {activeCount}
                        </div>
                      )}
                      <div className="text-3xl mb-2">{icon}</div>
                      <p className="text-xs font-semibold capitalize">{paradigm}</p>
                      <Badge variant="secondary" className="mt-2 text-xs">
                        {agentsInParadigm.length} agents
                      </Badge>
                    </div>
                  </Card>

                  {hoveredParadigm === paradigm && (
                    <motion.div
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="absolute top-full left-1/2 -translate-x-1/2 mt-2 z-10"
                    >
                      <Card className="p-3 min-w-[200px] shadow-xl">
                        <p className="text-xs font-semibold mb-2">Active Agents:</p>
                        <div className="space-y-1">
                          {agentsInParadigm.map(agent => (
                            <div key={agent.id} className="flex items-center gap-2">
                              <div className={`w-2 h-2 rounded-full ${
                                agent.status === 'active' || agent.status === 'thinking' 
                                  ? 'bg-green-500 animate-pulse' 
                                  : 'bg-gray-500'
                              }`} />
                              <span className="text-xs">{agent.name}</span>
                            </div>
                          ))}
                        </div>
                      </Card>
                    </motion.div>
                  )}
                </motion.div>
              );
            })}
          </div>

          <motion.div
            className="absolute inset-0 pointer-events-none"
            animate={{
              background: [
                'radial-gradient(circle at 50% 50%, oklch(0.45 0.18 295 / 0.05) 0%, transparent 70%)',
                'radial-gradient(circle at 50% 50%, oklch(0.75 0.15 195 / 0.05) 0%, transparent 70%)',
                'radial-gradient(circle at 50% 50%, oklch(0.45 0.18 295 / 0.05) 0%, transparent 70%)',
              ],
            }}
            transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }}
          />
        </div>
      </Card>

      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Collaboration Metrics</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="p-4 bg-muted/30">
            <div className="text-2xl font-bold text-accent mb-1">
              {collaborations.length}
            </div>
            <p className="text-sm text-muted-foreground">Active Connections</p>
          </Card>

          <Card className="p-4 bg-muted/30">
            <div className="text-2xl font-bold text-accent mb-1">
              {activeParadigms.length}
            </div>
            <p className="text-sm text-muted-foreground">Paradigms Collaborating</p>
          </Card>

          <Card className="p-4 bg-muted/30">
            <div className="text-2xl font-bold text-accent mb-1">
              {agents.filter(a => a.status === 'active' || a.status === 'thinking').length}
            </div>
            <p className="text-sm text-muted-foreground">Active Agents</p>
          </Card>
        </div>

        <div className="mt-6 p-4 bg-muted/20 rounded-lg border border-border">
          <h4 className="text-sm font-semibold mb-2 text-accent">Physics Synergy</h4>
          <p className="text-xs text-muted-foreground leading-relaxed">
            Agents from different physics paradigms collaborate by exchanging computational tokens 
            and insights. Each paradigm contributes unique analytical perspectives: 
            <strong className="text-foreground"> Chaos</strong> detects instabilities, 
            <strong className="text-foreground"> Fractal</strong> identifies patterns, 
            <strong className="text-foreground"> Fluid</strong> optimizes flow, 
            <strong className="text-foreground"> Electromagnetic</strong> analyzes fields, 
            <strong className="text-foreground"> Wave</strong> processes oscillations, and 
            <strong className="text-foreground"> Relativity</strong> manages temporal dependencies.
          </p>
        </div>
      </Card>
    </div>
  );
}
