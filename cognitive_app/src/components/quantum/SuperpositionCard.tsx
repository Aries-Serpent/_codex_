import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { SuperpositionScenario } from '@/lib/codex-api-client';

interface SuperpositionCardProps {
  scenario: SuperpositionScenario;
  index: number;
}

export function SuperpositionCard({ scenario, index }: SuperpositionCardProps) {
  const probabilityPercent = (scenario.probability * 100).toFixed(1);
  const energyLevel = scenario.energy > 1.5 ? 'High' : scenario.energy > 0.8 ? 'Medium' : 'Low';

  return (
    <Card className="p-4 relative overflow-hidden group hover:shadow-lg transition-shadow">
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-accent/5 opacity-0 group-hover:opacity-100 transition-opacity" />
      
      <div className="relative">
        <div className="flex items-center justify-between mb-3">
          <h4 className="font-semibold text-lg">{scenario.state}</h4>
          {scenario.bell_state && (
            <Badge variant="outline" className="border-accent text-accent text-xs">
              {scenario.bell_state}
            </Badge>
          )}
        </div>

        <div className="space-y-3">
          <div>
            <div className="flex items-center justify-between text-sm mb-1">
              <span className="text-muted-foreground">Probability</span>
              <span className="font-mono font-semibold text-accent">{probabilityPercent}%</span>
            </div>
            <div className="h-2 bg-background rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-primary to-accent transition-all quantum-pulse"
                style={{ width: `${probabilityPercent}%` }}
              />
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between text-sm mb-1">
              <span className="text-muted-foreground">Energy</span>
              <span className="font-mono font-semibold">{scenario.energy.toFixed(2)}</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="flex-1 h-2 bg-background rounded-full overflow-hidden">
                <div 
                  className={`h-full transition-all ${
                    energyLevel === 'High' ? 'bg-red-500' :
                    energyLevel === 'Medium' ? 'bg-yellow-500' :
                    'bg-green-500'
                  }`}
                  style={{ width: `${Math.min((scenario.energy / 2) * 100, 100)}%` }}
                />
              </div>
              <span className="text-xs text-muted-foreground">{energyLevel}</span>
            </div>
          </div>

          {scenario.bell_state && (
            <div className="pt-2 border-t border-border">
              <p className="text-xs text-muted-foreground">
                <strong className="text-accent">Entangled:</strong> This state is quantum-entangled 
                with other decision nodes, enabling coordinated evaluation.
              </p>
            </div>
          )}
        </div>
      </div>
    </Card>
  );
}
