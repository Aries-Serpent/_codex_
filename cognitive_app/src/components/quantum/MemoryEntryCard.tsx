import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { MemoryEntry } from '@/lib/codex-api-client';
import { Lightbulb, BookOpen, Target, GraduationCap } from '@phosphor-icons/react';

interface MemoryEntryCardProps {
  entry: MemoryEntry;
}

const TYPE_CONFIG = {
  decision: { icon: Target, color: 'text-blue-500', bg: 'bg-blue-500/20', label: 'Decision' },
  fact: { icon: BookOpen, color: 'text-green-500', bg: 'bg-green-500/20', label: 'Fact' },
  pattern: { icon: Lightbulb, color: 'text-yellow-500', bg: 'bg-yellow-500/20', label: 'Pattern' },
  lesson: { icon: GraduationCap, color: 'text-purple-500', bg: 'bg-purple-500/20', label: 'Lesson' },
};

export function MemoryEntryCard({ entry }: MemoryEntryCardProps) {
  const config = TYPE_CONFIG[entry.type];
  const Icon = config.icon;
  const confidencePercent = (entry.confidence * 100).toFixed(0);
  const timeAgo = getTimeAgo(entry.timestamp);

  return (
    <Card className={`p-4 ${config.bg} border-l-4`}>
      <div className="flex items-start gap-3">
        <Icon weight="duotone" className={`w-6 h-6 ${config.color} flex-shrink-0 mt-1`} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2 mb-2">
            <Badge variant="outline" className={`${config.color} border-current text-xs`}>
              {config.label}
            </Badge>
            <span className="text-xs text-muted-foreground">{timeAgo}</span>
          </div>

          <p className="text-sm font-medium mb-2">{entry.content}</p>

          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">
              Category: <span className="font-medium">{entry.category}</span>
            </span>
            <div className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground">Confidence:</span>
              <div className="flex items-center gap-1">
                <div className="w-16 h-1.5 bg-background rounded-full overflow-hidden">
                  <div 
                    className={`h-full ${config.color.replace('text', 'bg')} transition-all`}
                    style={{ width: `${confidencePercent}%` }}
                  />
                </div>
                <span className={`text-xs font-mono font-semibold ${config.color}`}>
                  {confidencePercent}%
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
}

function getTimeAgo(timestamp: string): string {
  const now = new Date();
  const time = new Date(timestamp);
  const diffMs = now.getTime() - time.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  
  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins} min${diffMins !== 1 ? 's' : ''} ago`;
  
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
  
  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
}
