import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ArrowRight, Lightning } from '@phosphor-icons/react';
import { motion } from 'framer-motion';

interface ActionPath {
  path_id: string;
  description: string;
  paradigm: string;
  potential_energy: number;
  kinetic_energy: number;
  total_energy: number;
  efficiency: number;
  steps: string[];
}

interface ActionPathViewerProps {
  paths: ActionPath[];
}

const paradigmColors: Record<string, string> = {
  chaos: 'oklch(0.50 0.25 30)',
  fractal: 'oklch(0.55 0.22 60)',
  fluid: 'oklch(0.60 0.20 220)',
  electromagnetic: 'oklch(0.65 0.20 180)',
  wave: 'oklch(0.70 0.18 250)',
  relativity: 'oklch(0.50 0.20 320)',
};

const paradigmEmojis: Record<string, string> = {
  chaos: '🌀',
  fractal: '🔺',
  fluid: '💧',
  electromagnetic: '⚡',
  wave: '〰️',
  relativity: '⏰',
};

export function ActionPathViewer({ paths }: ActionPathViewerProps) {
  const getEnergyColor = (energy: number) => {
    if (energy >= 80) return 'text-[oklch(0.55_0.22_25)]';
    if (energy >= 50) return 'text-[oklch(0.70_0.15_60)]';
    return 'text-[oklch(0.75_0.18_140)]';
  };

  const getEfficiencyColor = (efficiency: number) => {
    if (efficiency >= 0.8) return 'text-[oklch(0.75_0.18_140)]';
    if (efficiency >= 0.6) return 'text-[oklch(0.70_0.15_60)]';
    return 'text-[oklch(0.55_0.22_25)]';
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Energy Optimization Paths</h3>
        <Badge variant="outline" className="text-xs">
          {paths.length} paths analyzed
        </Badge>
      </div>

      <div className="space-y-3">
        {paths.map((path, index) => {
          const paradigmColor = paradigmColors[path.paradigm] || 'oklch(0.5 0.2 280)';
          const emoji = paradigmEmojis[path.paradigm] || '🔬';

          return (
            <motion.div
              key={path.path_id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card className="p-4 bg-card border-border hover:border-primary/40 transition-colors">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2 flex-1">
                    <span className="text-2xl">{emoji}</span>
                    <div className="flex-1 min-w-0">
                      <h4 className="text-sm font-semibold text-foreground capitalize">
                        {path.paradigm} Path
                      </h4>
                      <p className="text-xs text-muted-foreground line-clamp-1">
                        {path.description}
                      </p>
                    </div>
                  </div>
                  <Badge
                    variant="outline"
                    style={{
                      borderColor: paradigmColor,
                      color: paradigmColor,
                    }}
                    className="text-xs shrink-0"
                  >
                    Path {index + 1}
                  </Badge>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                  <div>
                    <div className="text-xs text-muted-foreground mb-1">Potential</div>
                    <div className={`text-lg font-bold font-mono ${getEnergyColor(path.potential_energy)}`}>
                      {path.potential_energy.toFixed(1)}
                    </div>
                    <div className="h-1.5 bg-muted rounded-full overflow-hidden mt-1">
                      <motion.div
                        className="h-full bg-gradient-to-r from-primary to-accent"
                        initial={{ width: '0%' }}
                        animate={{ width: `${path.potential_energy}%` }}
                        transition={{ duration: 0.8, ease: 'easeOut' }}
                      />
                    </div>
                  </div>

                  <div>
                    <div className="text-xs text-muted-foreground mb-1">Kinetic</div>
                    <div className={`text-lg font-bold font-mono ${getEnergyColor(path.kinetic_energy)}`}>
                      {path.kinetic_energy.toFixed(1)}
                    </div>
                    <div className="h-1.5 bg-muted rounded-full overflow-hidden mt-1">
                      <motion.div
                        className="h-full bg-gradient-to-r from-accent to-primary"
                        initial={{ width: '0%' }}
                        animate={{ width: `${path.kinetic_energy}%` }}
                        transition={{ duration: 0.8, ease: 'easeOut' }}
                      />
                    </div>
                  </div>

                  <div>
                    <div className="text-xs text-muted-foreground mb-1">Total Energy</div>
                    <div className={`text-lg font-bold font-mono ${getEnergyColor(path.total_energy)}`}>
                      {path.total_energy.toFixed(1)}
                    </div>
                    <div className="flex items-center gap-1 mt-1">
                      <Lightning weight="fill" className={`w-3 h-3 ${getEnergyColor(path.total_energy)}`} />
                      <span className="text-xs text-muted-foreground">J</span>
                    </div>
                  </div>

                  <div>
                    <div className="text-xs text-muted-foreground mb-1">Efficiency</div>
                    <div className={`text-lg font-bold font-mono ${getEfficiencyColor(path.efficiency)}`}>
                      {(path.efficiency * 100).toFixed(0)}%
                    </div>
                    <div className="h-1.5 bg-muted rounded-full overflow-hidden mt-1">
                      <motion.div
                        className={`h-full ${getEfficiencyColor(path.efficiency)}`}
                        style={{
                          background: `linear-gradient(90deg, ${paradigmColor}, ${paradigmColor})`
                        }}
                        initial={{ width: '0%' }}
                        animate={{ width: `${path.efficiency * 100}%` }}
                        transition={{ duration: 0.8, ease: 'easeOut' }}
                      />
                    </div>
                  </div>
                </div>

                {path.steps.length > 0 && (
                  <div className="pt-3 border-t border-border">
                    <div className="text-xs text-muted-foreground mb-2">Execution Steps</div>
                    <div className="flex flex-wrap items-center gap-2">
                      {path.steps.map((step, stepIndex) => (
                        <div key={stepIndex} className="flex items-center gap-2">
                          <Badge variant="secondary" className="text-xs">
                            {step}
                          </Badge>
                          {stepIndex < path.steps.length - 1 && (
                            <ArrowRight weight="bold" className="w-3 h-3 text-muted-foreground" />
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </Card>
            </motion.div>
          );
        })}
      </div>

      {paths.length === 0 && (
        <Card className="p-8 bg-card border-border border-dashed">
          <div className="text-center">
            <Lightning weight="duotone" className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
            <p className="text-sm text-muted-foreground">
              No action paths available. Start a workflow to generate optimization paths.
            </p>
          </div>
        </Card>
      )}
    </div>
  );
}
