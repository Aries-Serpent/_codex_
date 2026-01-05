import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Database, Lightning, Package, TrendUp } from '@phosphor-icons/react';
import { motion } from 'framer-motion';

interface QuantumMemoryState {
  stm_capacity: number;
  stm_used: number;
  ltm_capacity: number;
  ltm_used: number;
  cache_hit_rate: number;
  compression_rate: number;
  pattern_count: number;
  quantum_coherence: number;
}

interface QuantumMemoryViewerProps {
  memoryState: QuantumMemoryState;
}

export function QuantumMemoryViewer({ memoryState }: QuantumMemoryViewerProps) {
  const stmPercent = (memoryState.stm_used / memoryState.stm_capacity) * 100;
  const ltmPercent = (memoryState.ltm_used / memoryState.ltm_capacity) * 100;
  
  const getMemoryColor = (percent: number) => {
    if (percent >= 90) return 'text-[oklch(0.55_0.22_25)]';
    if (percent >= 70) return 'text-[oklch(0.65_0.20_60)]';
    return 'text-[oklch(0.75_0.18_140)]';
  };

  const getCacheColor = (rate: number) => {
    if (rate >= 0.5) return 'text-[oklch(0.75_0.18_140)]';
    if (rate >= 0.3) return 'text-[oklch(0.70_0.15_60)]';
    return 'text-[oklch(0.55_0.22_25)]';
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="p-4 bg-card border-border">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg bg-[oklch(0.70_0.18_40)]/20">
              <Lightning weight="duotone" className="w-5 h-5 text-[oklch(0.70_0.18_40)]" />
            </div>
            <div>
              <h3 className="text-sm font-semibold">Short-Term Memory</h3>
              <p className="text-xs text-muted-foreground">Active working memory</p>
            </div>
          </div>

          <div className="space-y-3">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-muted-foreground">Capacity</span>
                <span className={`text-sm font-mono ${getMemoryColor(stmPercent)}`}>
                  {memoryState.stm_used} / {memoryState.stm_capacity}
                </span>
              </div>
              <Progress 
                value={stmPercent} 
                className="h-2"
              />
            </div>

            <div className="pt-3 border-t border-border">
              <div className="flex items-center justify-between">
                <span className="text-xs text-muted-foreground">Usage</span>
                <motion.span 
                  className={`text-lg font-bold ${getMemoryColor(stmPercent)}`}
                  animate={{ scale: [1, 1.05, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  {stmPercent.toFixed(1)}%
                </motion.span>
              </div>
            </div>
          </div>
        </Card>

        <Card className="p-4 bg-card border-border">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg bg-[oklch(0.60_0.15_220)]/20">
              <Database weight="duotone" className="w-5 h-5 text-[oklch(0.60_0.15_220)]" />
            </div>
            <div>
              <h3 className="text-sm font-semibold">Long-Term Memory</h3>
              <p className="text-xs text-muted-foreground">Consolidated patterns</p>
            </div>
          </div>

          <div className="space-y-3">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-muted-foreground">Capacity</span>
                <span className={`text-sm font-mono ${getMemoryColor(ltmPercent)}`}>
                  {memoryState.ltm_used} / {memoryState.ltm_capacity}
                </span>
              </div>
              <Progress 
                value={ltmPercent} 
                className="h-2"
              />
            </div>

            <div className="pt-3 border-t border-border">
              <div className="flex items-center justify-between">
                <span className="text-xs text-muted-foreground">Usage</span>
                <span className={`text-lg font-bold ${getMemoryColor(ltmPercent)}`}>
                  {ltmPercent.toFixed(1)}%
                </span>
              </div>
            </div>
          </div>
        </Card>
      </div>

      <Card className="p-4 bg-card border-border">
        <h3 className="text-sm font-semibold mb-4">Quantum Memory Metrics</h3>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <TrendUp weight="duotone" className="w-4 h-4 text-accent" />
              <span className="text-xs text-muted-foreground">Cache Hit Rate</span>
            </div>
            <div className="flex items-baseline gap-1">
              <span className={`text-2xl font-bold font-mono ${getCacheColor(memoryState.cache_hit_rate)}`}>
                {(memoryState.cache_hit_rate * 100).toFixed(1)}
              </span>
              <span className="text-sm text-muted-foreground">%</span>
            </div>
            <div className="h-1 bg-muted rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-gradient-to-r from-primary to-accent"
                initial={{ width: '0%' }}
                animate={{ width: `${memoryState.cache_hit_rate * 100}%` }}
                transition={{ duration: 1, ease: 'easeOut' }}
              />
            </div>
            {memoryState.cache_hit_rate >= 0.3 ? (
              <Badge variant="outline" className="text-xs border-[oklch(0.75_0.18_140)] text-[oklch(0.75_0.18_140)]">
                Target: ≥30%
              </Badge>
            ) : (
              <Badge variant="outline" className="text-xs border-[oklch(0.55_0.22_25)] text-[oklch(0.55_0.22_25)]">
                Below Target
              </Badge>
            )}
          </div>

          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Package weight="duotone" className="w-4 h-4 text-accent" />
              <span className="text-xs text-muted-foreground">Compression</span>
            </div>
            <div className="flex items-baseline gap-1">
              <span className="text-2xl font-bold font-mono text-[oklch(0.55_0.20_160)]">
                {(memoryState.compression_rate * 100).toFixed(1)}
              </span>
              <span className="text-sm text-muted-foreground">%</span>
            </div>
            <div className="h-1 bg-muted rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-[oklch(0.55_0.20_160)]"
                initial={{ width: '0%' }}
                animate={{ width: `${memoryState.compression_rate * 100}%` }}
                transition={{ duration: 1, ease: 'easeOut' }}
              />
            </div>
            {memoryState.compression_rate >= 0.6 ? (
              <Badge variant="outline" className="text-xs border-[oklch(0.75_0.18_140)] text-[oklch(0.75_0.18_140)]">
                Target: ≥60%
              </Badge>
            ) : (
              <Badge variant="outline" className="text-xs border-[oklch(0.65_0.20_60)] text-[oklch(0.65_0.20_60)]">
                In Progress
              </Badge>
            )}
          </div>

          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Database weight="duotone" className="w-4 h-4 text-accent" />
              <span className="text-xs text-muted-foreground">Pattern Count</span>
            </div>
            <div className="flex items-baseline gap-1">
              <span className="text-2xl font-bold font-mono text-[oklch(0.65_0.18_280)]">
                {memoryState.pattern_count}
              </span>
            </div>
            <div className="text-xs text-muted-foreground mt-1">
              Active patterns in library
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="text-accent">⚛️</span>
              <span className="text-xs text-muted-foreground">Coherence</span>
            </div>
            <div className="flex items-baseline gap-1">
              <span className="text-2xl font-bold font-mono text-[oklch(0.60_0.20_285)]">
                {(memoryState.quantum_coherence * 100).toFixed(1)}
              </span>
              <span className="text-sm text-muted-foreground">%</span>
            </div>
            <div className="h-1 bg-muted rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-[oklch(0.60_0.20_285)] quantum-pulse"
                initial={{ width: '0%' }}
                animate={{ width: `${memoryState.quantum_coherence * 100}%` }}
                transition={{ duration: 1, ease: 'easeOut' }}
              />
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
