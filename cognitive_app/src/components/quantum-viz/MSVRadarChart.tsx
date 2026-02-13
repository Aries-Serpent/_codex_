import { useMemo } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Brain, TrendUp } from '@phosphor-icons/react';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from 'recharts';
import { useMSVMetrics } from '@/hooks/use-msv-metrics';

interface MSVDimension {
  dimension: string;
  current: number;
  target: number;
  fullMark: number;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{
    name: string;
    value: number;
    payload: MSVDimension;
  }>;
}

const CustomTooltip = ({ active, payload }: CustomTooltipProps) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="bg-card border border-border rounded-lg p-3 shadow-lg">
        <p className="text-sm font-semibold mb-2">{data.dimension}</p>
        <div className="space-y-1 text-xs">
          <div className="flex justify-between gap-4">
            <span className="text-muted-foreground">Current:</span>
            <span className="font-medium text-primary">{data.current}/100</span>
          </div>
          <div className="flex justify-between gap-4">
            <span className="text-muted-foreground">Target:</span>
            <span className="font-medium text-accent">{data.target}/100</span>
          </div>
          <div className="flex justify-between gap-4">
            <span className="text-muted-foreground">Gap:</span>
            <span className={`font-medium ${data.current >= data.target ? 'text-[oklch(0.75_0.18_140)]' : 'text-[oklch(0.70_0.18_40)]'}`}>
              {data.current >= data.target ? '✓' : `${(data.target - data.current).toFixed(1)}`}
            </span>
          </div>
        </div>
      </div>
    );
  }
  return null;
};

export function MSVRadarChart() {
  const { metrics, loading, error } = useMSVMetrics(true, 10000);

  const chartData: MSVDimension[] = useMemo(() => {
    if (!metrics) {
      return [
        { dimension: 'Correctness', current: 0, target: 96, fullMark: 100 },
        { dimension: 'Conflict', current: 0, target: 95, fullMark: 100 },
        { dimension: 'Importance', current: 0, target: 96, fullMark: 100 },
        { dimension: 'Experience', current: 0, target: 94, fullMark: 100 },
        { dimension: 'Adaptive', current: 0, target: 95, fullMark: 100 },
      ];
    }

    return [
      {
        dimension: 'Correctness',
        current: metrics.correctness_awareness,
        target: 96,
        fullMark: 100,
      },
      {
        dimension: 'Conflict',
        current: metrics.conflict_detection,
        target: 95,
        fullMark: 100,
      },
      {
        dimension: 'Importance',
        current: metrics.importance_assessment,
        target: 96,
        fullMark: 100,
      },
      {
        dimension: 'Experience',
        current: metrics.experience_matching,
        target: 94,
        fullMark: 100,
      },
      {
        dimension: 'Adaptive',
        current: metrics.adaptive_response,
        target: 95,
        fullMark: 100,
      },
    ];
  }, [metrics]);

  const compositeScore = useMemo(() => {
    if (!metrics) return 0;
    const scores = [
      metrics.correctness_awareness,
      metrics.conflict_detection,
      metrics.importance_assessment,
      metrics.experience_matching,
      metrics.adaptive_response,
    ];
    return scores.reduce((sum, val) => sum + val, 0) / scores.length;
  }, [metrics]);

  const getScoreGrade = (score: number): string => {
    if (score >= 97) return 'A+';
    if (score >= 93) return 'A';
    if (score >= 90) return 'A-';
    if (score >= 87) return 'B+';
    return 'B';
  };

  const getScoreColor = (score: number): string => {
    if (score >= 96) return 'text-[oklch(0.75_0.18_140)]';
    if (score >= 93) return 'text-primary';
    if (score >= 90) return 'text-accent';
    return 'text-[oklch(0.70_0.18_40)]';
  };

  if (loading) {
    return (
      <Card className="p-4 bg-card border-border">
        <div className="flex items-center gap-2 mb-4">
          <Brain weight="duotone" className="w-5 h-5 text-primary animate-pulse" />
          <h3 className="text-sm font-semibold">Metacognitive State Vector (MSV)</h3>
        </div>
        <div className="flex items-center justify-center h-64">
          <div className="text-sm text-muted-foreground">Loading MSV metrics...</div>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="p-4 bg-card border-border">
        <div className="flex items-center gap-2 mb-4">
          <Brain weight="duotone" className="w-5 h-5 text-primary" />
          <h3 className="text-sm font-semibold">Metacognitive State Vector (MSV)</h3>
        </div>
        <div className="flex items-center justify-center h-64">
          <div className="text-sm text-muted-foreground">{error}</div>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-4 bg-card border-border">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Brain weight="duotone" className="w-5 h-5 text-primary" />
          <h3 className="text-sm font-semibold">Metacognitive State Vector (MSV)</h3>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="text-xs">
            Auto-refresh: 10s
          </Badge>
          <Badge 
            variant="outline" 
            className={`text-sm font-bold ${getScoreColor(compositeScore)}`}
          >
            {compositeScore.toFixed(1)} ({getScoreGrade(compositeScore)})
          </Badge>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="flex items-center justify-center">
          <ResponsiveContainer width="100%" height={320}>
            <RadarChart data={chartData}>
              <PolarGrid stroke="hsl(var(--border))" />
              <PolarAngleAxis 
                dataKey="dimension" 
                tick={{ fill: 'hsl(var(--foreground))', fontSize: 12 }}
              />
              <PolarRadiusAxis 
                angle={90} 
                domain={[0, 100]}
                tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 10 }}
              />
              <Radar
                name="Current"
                dataKey="current"
                stroke="hsl(var(--primary))"
                fill="hsl(var(--primary))"
                fillOpacity={0.3}
                strokeWidth={2}
              />
              <Radar
                name="Target (V3→V4)"
                dataKey="target"
                stroke="hsl(var(--accent))"
                fill="hsl(var(--accent))"
                fillOpacity={0.1}
                strokeWidth={1}
                strokeDasharray="5 5"
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend 
                wrapperStyle={{ fontSize: '12px' }}
                iconType="circle"
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        <div className="space-y-3">
          <div className="text-xs text-muted-foreground mb-3">
            <p className="mb-2">
              The MSV measures AI self-awareness across 5 cognitive dimensions.
              Based on <a 
                href="https://research.sethi.org/ricky/selected_publications/courchaine_sethi_2026-thewebconf.pdf"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline"
              >
                TheWebConf 2026 research
              </a>.
            </p>
          </div>

          <div className="space-y-2">
            {chartData.map((dim, idx) => {
              const progress = (dim.current / dim.target) * 100;
              const isOnTrack = dim.current >= dim.target * 0.95;
              
              return (
                <div key={idx} className="space-y-1">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-medium">{dim.dimension}</span>
                    <div className="flex items-center gap-2">
                      <span className={getScoreColor(dim.current)}>
                        {dim.current.toFixed(0)}/100
                      </span>
                      {isOnTrack && (
                        <TrendUp weight="bold" className="w-3 h-3 text-[oklch(0.75_0.18_140)]" />
                      )}
                    </div>
                  </div>
                  <div className="w-full bg-muted rounded-full h-1.5">
                    <div
                      className={`h-1.5 rounded-full transition-all ${
                        progress >= 100
                          ? 'bg-[oklch(0.75_0.18_140)]'
                          : progress >= 95
                          ? 'bg-primary'
                          : 'bg-accent'
                      }`}
                      style={{ width: `${Math.min(progress, 100)}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>

          <div className="pt-3 border-t border-border">
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">Path to 97.0 (A+)</span>
              <span className={`font-bold ${getScoreColor(compositeScore)}`}>
                Current: {compositeScore.toFixed(1)}/100
              </span>
            </div>
            <div className="flex items-center justify-between text-xs mt-1">
              <span className="text-muted-foreground">Gap to target</span>
              <span className="font-medium">
                {(97.0 - compositeScore).toFixed(1)} points
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-border">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 text-xs">
          {chartData.map((dim, idx) => (
            <div key={idx} className="text-center">
              <div className={`text-lg font-bold ${getScoreColor(dim.current)}`}>
                {dim.current.toFixed(0)}
              </div>
              <div className="text-muted-foreground">{dim.dimension}</div>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
}
