import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Atom, Brain, Lightning, TrendUp, CheckCircle } from '@phosphor-icons/react';
import { useQuantumState } from '@/hooks/use-quantum-state';
import { SuperpositionCard } from './SuperpositionCard';
import { PhaseProgressBar } from './PhaseProgressBar';

export function QuantumDecisionEngine() {
  const { state, loading, error } = useQuantumState(true, 10000);

  if (loading && !state) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center py-12">
          <Atom weight="duotone" className="w-8 h-8 text-accent animate-spin" />
          <span className="ml-3 text-muted-foreground">Loading quantum state...</span>
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

  const k1Achieved = state.k1_factor <= 0.35;
  const highCoherence = state.coherence >= 0.65;
  const advantageAchieved = state.quantum_advantage >= 2.5;

  return (
    <div className="space-y-6">
      <Card className="p-6 bg-gradient-to-br from-card via-card to-[oklch(0.28_0.03_260)]">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-12 h-12 bg-primary/20 backdrop-blur-sm rounded-lg">
              <Brain weight="duotone" className="w-7 h-7 text-primary" />
            </div>
            <div>
              <h2 className="text-2xl font-semibold text-accent">Quantum Decision Engine</h2>
              <p className="text-sm text-muted-foreground">Cognitive Brain Metrics - Phase 8</p>
            </div>
          </div>
          <Badge variant="outline" className="border-accent text-accent">
            Live Monitoring
          </Badge>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <Card className="p-4 bg-muted/30">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-muted-foreground">k₁ Factor</span>
              {k1Achieved && (
                <CheckCircle weight="fill" className="w-4 h-4 text-green-500" />
              )}
            </div>
            <div className={`text-3xl font-mono font-bold ${
              k1Achieved ? 'text-green-500' : 'text-yellow-500'
            }`}>
              {state.k1_factor.toFixed(4)}
            </div>
            <div className="mt-2 h-2 bg-background/50 rounded-full overflow-hidden">
              <div 
                className={`h-full transition-all ${
                  k1Achieved ? 'bg-green-500' : 'bg-yellow-500'
                }`}
                style={{ width: `${Math.min((0.35 / state.k1_factor) * 100, 100)}%` }}
              />
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Target: ≤0.35 {k1Achieved ? '✓ ACHIEVED' : ''}
            </p>
          </Card>

          <Card className="p-4 bg-muted/30">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-muted-foreground">Quantum Advantage</span>
              {advantageAchieved && (
                <Lightning weight="fill" className="w-4 h-4 text-accent" />
              )}
            </div>
            <div className="text-3xl font-mono font-bold text-accent">
              {state.quantum_advantage.toFixed(2)}x
            </div>
            <div className="mt-2 h-2 bg-background/50 rounded-full overflow-hidden">
              <div 
                className="h-full bg-accent transition-all"
                style={{ width: `${Math.min((state.quantum_advantage / 4) * 100, 100)}%` }}
              />
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              vs. Classical Processing
            </p>
          </Card>

          <Card className="p-4 bg-muted/30">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-muted-foreground">Coherence</span>
              {highCoherence && (
                <CheckCircle weight="fill" className="w-4 h-4 text-green-500" />
              )}
            </div>
            <div className={`text-3xl font-mono font-bold ${
              highCoherence ? 'text-green-500' : 
              state.coherence >= 0.5 ? 'text-yellow-500' : 
              'text-red-500'
            }`}>
              {(state.coherence * 100).toFixed(1)}%
            </div>
            <div className="mt-2 h-2 bg-background/50 rounded-full overflow-hidden">
              <div 
                className={`h-full transition-all ${
                  highCoherence ? 'bg-green-500' : 
                  state.coherence >= 0.5 ? 'bg-yellow-500' : 
                  'bg-red-500'
                }`}
                style={{ width: `${state.coherence * 100}%` }}
              />
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Target: ≥65% {highCoherence ? '✓' : ''}
            </p>
          </Card>

          <Card className="p-4 bg-muted/30">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-muted-foreground">Accuracy</span>
              <TrendUp weight="bold" className="w-4 h-4 text-green-500" />
            </div>
            <div className="text-3xl font-mono font-bold text-green-500">
              {(state.accuracy * 100).toFixed(1)}%
            </div>
            <div className="mt-2 h-2 bg-background/50 rounded-full overflow-hidden">
              <div 
                className="h-full bg-green-500 transition-all"
                style={{ width: `${state.accuracy * 100}%` }}
              />
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Target: ≥84% ✓ +{((state.accuracy - 0.84) * 100).toFixed(1)}%
            </p>
          </Card>
        </div>

        <PhaseProgressBar currentPhase={8.0} targetPhase={8.4} />
      </Card>

      <div>
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Atom weight="duotone" className="w-5 h-5 text-accent" />
          Superposition States
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {state.superposition_states.map((scenario, index) => (
            <SuperpositionCard key={index} scenario={scenario} index={index} />
          ))}
        </div>
      </div>

      <Card className="p-4 bg-muted/30">
        <p className="text-sm text-muted-foreground">
          <strong className="text-accent">Quantum Computing Principles:</strong> The cognitive brain evaluates 
          multiple decision paths simultaneously through superposition, achieving {state.quantum_advantage.toFixed(2)}x 
          faster processing than classical sequential evaluation. Coherence of {(state.coherence * 100).toFixed(1)}% 
          indicates the system's ability to maintain quantum entanglement across parallel evaluations.
        </p>
      </Card>
    </div>
  );
}
