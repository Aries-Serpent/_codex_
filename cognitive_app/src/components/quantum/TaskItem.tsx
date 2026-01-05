import { Badge } from '@/components/ui/badge';
import { CheckCircle, Clock, Lightning, XCircle } from '@phosphor-icons/react';
import { motion } from 'framer-motion';
import { formatDistanceToNow } from 'date-fns';

interface TaskItemProps {
  task: {
    id: string;
    description: string;
    assigned_agent: string | null;
    status: 'pending' | 'running' | 'completed' | 'failed';
    started_at: string | null;
    completed_at: string | null;
    priority?: number;
    workflow_token?: string;
  };
  index: number;
}

const statusConfig = {
  pending: {
    icon: Clock,
    color: 'text-muted-foreground',
    bgColor: 'bg-muted',
    label: 'Pending',
  },
  running: {
    icon: Lightning,
    color: 'text-[oklch(0.65_0.20_280)]',
    bgColor: 'bg-[oklch(0.65_0.20_280)]/20',
    label: 'Running',
  },
  completed: {
    icon: CheckCircle,
    color: 'text-[oklch(0.75_0.18_140)]',
    bgColor: 'bg-[oklch(0.75_0.18_140)]/20',
    label: 'Completed',
  },
  failed: {
    icon: XCircle,
    color: 'text-[oklch(0.55_0.22_25)]',
    bgColor: 'bg-[oklch(0.55_0.22_25)]/20',
    label: 'Failed',
  },
};

const workflowTokenEmojis: Record<string, string> = {
  AUDIT_EXEC: '🔍',
  DOC_GEN: '📚',
  HEAL: '🔧',
  DECIDE: '⚛️',
  ORGANIZE: '🗂️',
  REVIEW: '✅',
};

export function TaskItem({ task, index }: TaskItemProps) {
  const config = statusConfig[task.status];
  const StatusIcon = config.icon;

  /**
   * Formats a date string as a relative time with a prefix.
   * 
   * @param dateString - ISO date string to format, or null
   * @param prefix - Text prefix for the formatted output (e.g., "Completed", "Started")
   * @returns Formatted string like "Completed 2 hours ago", or null if dateString is null.
   *          Falls back to prefix only if date parsing fails.
   * 
   * Error handling: Logs parse/format errors and returns prefix to prevent UI breaks.
   */
  const formatRelativeTime = (dateString: string | null, prefix: string): string | null => {
    if (!dateString) return null;

    const date = new Date(dateString);
    if (Number.isNaN(date.getTime())) {
      // Invalid date string; fall back to prefix without relative time
      return prefix;
    }

    try {
      return `${prefix} ${formatDistanceToNow(date, { addSuffix: true })}`;
    } catch (error) {
      // In case formatDistanceToNow throws for any reason, log and avoid breaking the UI
      console.error('Failed to format relative time for TaskItem:', {
        dateString,
        error,
      });
      return prefix;
    }
  };

  const getTimeDisplay = () => {
    const completedDisplay = formatRelativeTime(task.completed_at, 'Completed');
    if (completedDisplay) {
      return completedDisplay;
    }

    const startedDisplay = formatRelativeTime(task.started_at, 'Started');
    if (startedDisplay) {
      return startedDisplay;
    }

    return 'Queued';
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05 }}
      className="flex items-start gap-3 p-3 rounded-lg bg-card border border-border hover:border-primary/30 transition-colors"
    >
      <div className="flex items-center justify-center">
        <div className={`p-2 rounded-lg ${config.bgColor}`}>
          {task.status === 'running' ? (
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
            >
              <StatusIcon weight="duotone" className={`w-4 h-4 ${config.color}`} />
            </motion.div>
          ) : (
            <StatusIcon weight="duotone" className={`w-4 h-4 ${config.color}`} />
          )}
        </div>
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2 mb-1">
          <p className="text-sm font-medium text-foreground line-clamp-2">
            {task.description}
          </p>
          {task.priority && (
            <Badge variant="outline" className="text-xs shrink-0">
              P{task.priority}
            </Badge>
          )}
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <Badge className={`text-xs ${config.bgColor} ${config.color} border-0`}>
            {config.label}
          </Badge>

          {task.workflow_token && (
            <Badge variant="outline" className="text-xs">
              {workflowTokenEmojis[task.workflow_token] || '🔄'} {task.workflow_token}
            </Badge>
          )}

          {task.assigned_agent && (
            <Badge variant="outline" className="text-xs">
              🤖 {task.assigned_agent}
            </Badge>
          )}

          <span className="text-xs text-muted-foreground">
            {getTimeDisplay()}
          </span>
        </div>

        {task.status === 'running' && (
          <div className="mt-2">
            <div className="h-1 bg-muted rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-gradient-to-r from-primary via-accent to-primary"
                animate={{
                  x: ['-100%', '100%'],
                }}
                transition={{
                  duration: 1.5,
                  repeat: Infinity,
                  ease: 'linear',
                }}
                style={{ width: '50%' }}
              />
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}
