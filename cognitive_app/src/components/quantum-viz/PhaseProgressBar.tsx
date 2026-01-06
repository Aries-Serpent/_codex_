import { Card } from '@/components/ui/card';
import { CheckCircle, Circle } from '@phosphor-icons/react';

interface PhaseProgressBarProps {
  currentPhase: number;
  targetPhase: number;
}

export function PhaseProgressBar({ currentPhase, targetPhase }: PhaseProgressBarProps) {
  const phases = [
    { phase: 8.0, label: 'Weight Optimization', complete: currentPhase >= 8.0 },
    { phase: 8.1, label: 'Memory Compression', complete: currentPhase >= 8.1 },
    { phase: 8.2, label: 'GHZ Entanglement', complete: currentPhase >= 8.2 },
    { phase: 8.3, label: 'Caching Strategy', complete: currentPhase >= 8.3 },
    { phase: 8.4, label: 'Full Integration', complete: currentPhase >= 8.4 },
  ];

  const progress = ((currentPhase - 8.0) / (targetPhase - 8.0)) * 100;

  return (
    <Card className="p-4 bg-muted/20">
      <div className="mb-3">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-muted-foreground">Phase 8 Progress</span>
          <span className="text-sm font-mono font-semibold text-accent">
            {currentPhase.toFixed(1)} / {targetPhase.toFixed(1)}
          </span>
        </div>
        <div className="h-3 bg-background rounded-full overflow-hidden">
          <div 
            className="h-full bg-gradient-to-r from-primary via-secondary to-accent transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      <div className="grid grid-cols-5 gap-2">
        {phases.map((p) => (
          <div key={p.phase} className="flex flex-col items-center">
            {p.complete ? (
              <CheckCircle weight="fill" className="w-5 h-5 text-green-500 mb-1" />
            ) : (
              <Circle weight="regular" className="w-5 h-5 text-muted-foreground mb-1" />
            )}
            <span className={`text-xs font-mono ${
              p.complete ? 'text-green-500' : 'text-muted-foreground'
            }`}>
              {p.phase.toFixed(1)}
            </span>
            <span className="text-[10px] text-muted-foreground text-center mt-1">
              {p.label}
            </span>
          </div>
        ))}
      </div>
    </Card>
  );
}
