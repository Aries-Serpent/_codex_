import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { TrendUp, TrendDown, Minus } from '@phosphor-icons/react';
import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface MetricCardProps {
  title: string;
  value: string | number;
  unit?: string;
  icon?: ReactNode;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  subtitle?: string;
  color?: string;
  target?: string;
  status?: 'optimal' | 'good' | 'warning' | 'critical';
  animated?: boolean;
  sparkline?: number[];
}

const statusColors = {
  optimal: 'text-[oklch(0.80_0.20_145)]',
  good: 'text-[oklch(0.75_0.18_140)]',
  warning: 'text-[oklch(0.70_0.15_60)]',
  critical: 'text-[oklch(0.55_0.22_25)]',
};

const statusBadges = {
  optimal: 'bg-[oklch(0.80_0.20_145)]/20 text-[oklch(0.80_0.20_145)] border-[oklch(0.80_0.20_145)]',
  good: 'bg-[oklch(0.75_0.18_140)]/20 text-[oklch(0.75_0.18_140)] border-[oklch(0.75_0.18_140)]',
  warning: 'bg-[oklch(0.70_0.15_60)]/20 text-[oklch(0.70_0.15_60)] border-[oklch(0.70_0.15_60)]',
  critical: 'bg-[oklch(0.55_0.22_25)]/20 text-[oklch(0.55_0.22_25)] border-[oklch(0.55_0.22_25)]',
};

const trendColors = {
  up: 'text-[oklch(0.75_0.18_140)]',
  down: 'text-[oklch(0.55_0.22_25)]',
  neutral: 'text-muted-foreground',
};

export function MetricCard({
  title,
  value,
  unit,
  icon,
  trend,
  trendValue,
  subtitle,
  color,
  target,
  status = 'good',
  animated = true,
  sparkline,
}: MetricCardProps) {
  const TrendIcon = trend === 'up' ? TrendUp : trend === 'down' ? TrendDown : Minus;
  const valueColor = color || statusColors[status];

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      whileHover={{ scale: 1.02 }}
    >
      <Card className="p-4 bg-card border-border hover:border-primary/50 transition-all metric-card">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2">
            {icon && (
              <div className="p-1.5 rounded-lg bg-primary/10">
                {icon}
              </div>
            )}
            <div>
              <h3 className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                {title}
              </h3>
              {subtitle && (
                <p className="text-xs text-muted-foreground/70 mt-0.5">
                  {subtitle}
                </p>
              )}
            </div>
          </div>
          {status && (
            <Badge variant="outline" className={`text-xs ${statusBadges[status]}`}>
              {status}
            </Badge>
          )}
        </div>

        <div className="flex items-baseline gap-2 mb-2" style={animated ? { willChange: 'transform' } : undefined}>
          {animated ? (
            <motion.span
              className={`text-3xl font-bold font-mono ${valueColor}`}
              animate={{ scale: [1, 1.02, 1] }}
              transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
            >
              {value}
            </motion.span>
          ) : (
            <span className={`text-3xl font-bold font-mono ${valueColor}`}>
              {value}
            </span>
          )}
          {unit && (
            <span className="text-sm text-muted-foreground">
              {unit}
            </span>
          )}
        </div>

        {sparkline && sparkline.length > 0 && (
          <div className="mb-3">
            <svg
              role="img"
              aria-label="Sparkline chart"
              viewBox={`0 0 ${sparkline.length * 10} 30`}
              className="w-full h-8"
              preserveAspectRatio="none"
            >
              <motion.polyline
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className={valueColor}
                points={sparkline
                  .map((val, i) => `${i * 10},${30 - val * 30}`)
                  .join(' ')}
                initial={{ pathLength: 0, opacity: 0 }}
                animate={{ pathLength: 1, opacity: 0.6 }}
                transition={{ duration: 1, ease: 'easeOut' }}
              />
            </svg>
          </div>
        )}

        <div className="flex items-center justify-between pt-3 border-t border-border">
          {trend && trendValue && (
            <div className={`flex items-center gap-1 text-xs ${trendColors[trend]}`}>
              <TrendIcon weight="bold" className="w-3 h-3" />
              <span className="font-medium">{trendValue}</span>
            </div>
          )}
          {target && (
            <div className="text-xs text-muted-foreground">
              Target: <span className="font-mono">{target}</span>
            </div>
          )}
        </div>
      </Card>
    </motion.div>
  );
}
