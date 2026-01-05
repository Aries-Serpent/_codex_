import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Link } from '@phosphor-icons/react';
import { motion } from 'framer-motion';

interface EntanglementPair {
  agent1: string;
  agent2: string;
  entanglement_score: number;
  bell_state: string;
  coherence: number;
  correlation: number;
}

interface EntanglementCardProps {
  pair: EntanglementPair;
  index: number;
}

const getBellStateColor = (state: string) => {
  switch (state) {
    case 'Φ+': return 'bg-[oklch(0.55_0.25_350)]';
    case 'Φ-': return 'bg-[oklch(0.65_0.22_310)]';
    case 'Ψ+': return 'bg-[oklch(0.70_0.18_200)]';
    case 'Ψ-': return 'bg-[oklch(0.60_0.20_285)]';
    default: return 'bg-muted';
  }
};

const getEntanglementStrength = (score: number) => {
  if (score >= 0.8) return { label: 'Strong', color: 'text-[oklch(0.75_0.18_140)]' };
  if (score >= 0.5) return { label: 'Moderate', color: 'text-[oklch(0.70_0.15_60)]' };
  return { label: 'Weak', color: 'text-[oklch(0.55_0.22_25)]' };
};

export function EntanglementCard({ pair, index }: EntanglementCardProps) {
  const strength = getEntanglementStrength(pair.entanglement_score);
  const bellColor = getBellStateColor(pair.bell_state);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
    >
      <Card className="p-4 bg-card border-border hover:border-primary/50 transition-colors">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="relative">
              <Link weight="duotone" className="w-5 h-5 text-primary" />
              <motion.div
                className="absolute inset-0"
                animate={{ 
                  scale: [1, 1.2, 1],
                  opacity: [0.5, 0.8, 0.5]
                }}
                transition={{ 
                  duration: 2, 
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              >
                <Link weight="duotone" className="w-5 h-5 text-accent" />
              </motion.div>
            </div>
            <span className="text-sm font-medium">Pair {index + 1}</span>
          </div>
          <Badge className={`${bellColor} text-white`}>
            {pair.bell_state}
          </Badge>
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Agent 1:</span>
            <span className="font-mono text-foreground">{pair.agent1}</span>
          </div>
          
          <div className="flex items-center justify-center py-2">
            <div className="relative w-full h-1 bg-muted rounded-full overflow-hidden">
              <motion.div
                className="absolute inset-y-0 left-0 bg-gradient-to-r from-primary via-accent to-primary"
                initial={{ width: '0%' }}
                animate={{ 
                  width: `${pair.entanglement_score * 100}%`,
                  backgroundPosition: ['0% 50%', '100% 50%', '0% 50%']
                }}
                transition={{ 
                  width: { duration: 0.8, ease: 'easeOut' },
                  backgroundPosition: { duration: 2, repeat: Infinity, ease: 'linear' }
                }}
                style={{ backgroundSize: '200% 100%' }}
              />
            </div>
          </div>

          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Agent 2:</span>
            <span className="font-mono text-foreground">{pair.agent2}</span>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-2 mt-4 pt-4 border-t border-border">
          <div className="text-center">
            <div className="text-xs text-muted-foreground mb-1">Strength</div>
            <div className={`text-sm font-semibold ${strength.color}`}>
              {strength.label}
            </div>
          </div>
          <div className="text-center">
            <div className="text-xs text-muted-foreground mb-1">Coherence</div>
            <div className="text-sm font-mono text-foreground">
              {(pair.coherence * 100).toFixed(1)}%
            </div>
          </div>
          <div className="text-center">
            <div className="text-xs text-muted-foreground mb-1">Correlation</div>
            <div className="text-sm font-mono text-foreground">
              {pair.correlation.toFixed(3)}
            </div>
          </div>
        </div>

        <div className="mt-3">
          <div className="text-xs text-muted-foreground mb-1">Entanglement Score</div>
          <div className="flex items-center gap-2">
            <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-gradient-to-r from-primary to-accent"
                initial={{ width: '0%' }}
                animate={{ width: `${pair.entanglement_score * 100}%` }}
                transition={{ duration: 0.8, ease: 'easeOut' }}
              />
            </div>
            <span className="text-xs font-mono text-foreground min-w-[3ch]">
              {pair.entanglement_score.toFixed(2)}
            </span>
          </div>
        </div>
      </Card>
    </motion.div>
  );
}
