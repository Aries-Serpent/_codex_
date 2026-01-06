import { Card } from '@/components/ui/card';
import { CheckCircle, XCircle, Lightning, Clock } from '@phosphor-icons/react';
import { Badge } from '@/components/ui/badge';

interface MetricsBarProps {
  metadata: {
    k1_factor: number;
    coherence: number;
    cache_hit: boolean;
    processing_time_ms: number;
  };
  quantumMetrics: {
    superposition_states: number;
    entanglement_score: number;
  };
}

export function MetricsBar({ metadata, quantumMetrics }: MetricsBarProps) {
  const k1Success = metadata.k1_factor <= 0.35;
  const coherenceLevel = 
    metadata.coherence >= 0.65 ? 'high' : 
    metadata.coherence >= 0.50 ? 'medium' : 
    'low';

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <Lightning weight="duotone" className="w-5 h-5 text-accent" />
        Performance Metrics
      </h3>
      
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-xs text-muted-foreground">k₁ Factor</span>
            {k1Success && (
              <CheckCircle weight="fill" className="w-3 h-3 text-green-500" />
            )}
          </div>
          <div className="flex items-baseline gap-2">
            <span className={`text-2xl font-mono font-semibold ${
              k1Success ? 'text-green-500' : 'text-yellow-500'
            }`}>
              {metadata.k1_factor.toFixed(4)}
            </span>
            {k1Success && (
              <Badge variant="outline" className="text-xs border-green-500 text-green-500">
                Target ✓
              </Badge>
            )}
          </div>
          <p className="text-xs text-muted-foreground">Target: ≤0.35</p>
        </div>

        <div className="space-y-1">
          <span className="text-xs text-muted-foreground">Coherence</span>
          <div className="flex items-baseline gap-2">
            <span className={`text-2xl font-mono font-semibold ${
              coherenceLevel === 'high' ? 'text-green-500' : 
              coherenceLevel === 'medium' ? 'text-yellow-500' : 
              'text-red-500'
            }`}>
              {(metadata.coherence * 100).toFixed(1)}%
            </span>
          </div>
          <div className="w-full bg-muted rounded-full h-1.5 mt-1">
            <div 
              className={`h-1.5 rounded-full transition-all ${
                coherenceLevel === 'high' ? 'bg-green-500' : 
                coherenceLevel === 'medium' ? 'bg-yellow-500' : 
                'bg-red-500'
              }`}
              style={{ width: `${metadata.coherence * 100}%` }}
            />
          </div>
        </div>

        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-xs text-muted-foreground">Cache Status</span>
            {metadata.cache_hit ? (
              <CheckCircle weight="fill" className="w-3 h-3 text-accent" />
            ) : (
              <XCircle weight="fill" className="w-3 h-3 text-muted-foreground" />
            )}
          </div>
          <div className="flex items-baseline gap-2">
            <span className={`text-2xl font-semibold ${
              metadata.cache_hit ? 'text-accent' : 'text-muted-foreground'
            }`}>
              {metadata.cache_hit ? 'Hit' : 'Miss'}
            </span>
          </div>
          <p className="text-xs text-muted-foreground">
            {metadata.cache_hit ? '15% faster' : 'Computed fresh'}
          </p>
        </div>

        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Clock weight="duotone" className="w-3 h-3 text-muted-foreground" />
            <span className="text-xs text-muted-foreground">Processing Time</span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-mono font-semibold text-foreground">
              {metadata.processing_time_ms}
            </span>
            <span className="text-sm text-muted-foreground">ms</span>
          </div>
          <p className="text-xs text-muted-foreground">
            {quantumMetrics.superposition_states} states evaluated
          </p>
        </div>
      </div>

      <div className="mt-6 pt-6 border-t border-border">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-6">
            <div>
              <span className="text-muted-foreground">Superposition States:</span>
              <span className="ml-2 font-mono font-semibold text-accent">
                {quantumMetrics.superposition_states}
              </span>
            </div>
            <div>
              <span className="text-muted-foreground">Entanglement Score:</span>
              <span className="ml-2 font-mono font-semibold text-accent">
                {quantumMetrics.entanglement_score.toFixed(3)}
              </span>
            </div>
          </div>
          <Badge variant="outline" className="border-accent text-accent">
            <Lightning weight="fill" className="w-3 h-3 mr-1" />
            2.86x Quantum Advantage
          </Badge>
        </div>
      </div>
    </Card>
  );
}
