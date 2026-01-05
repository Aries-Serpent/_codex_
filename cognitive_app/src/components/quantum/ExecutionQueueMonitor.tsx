import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Clock, CheckCircle, XCircle, Circle, HourglassHigh } from '@phosphor-icons/react';
import { motion, AnimatePresence } from 'framer-motion';

interface QueuedExecution {
  tokenId: string;
  tokenName: string;
  tokenIcon: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'blocked';
  progress: number;
  blockedBy?: string[];
  startTime?: number;
  estimatedCompletion?: number;
}

interface ExecutionQueueMonitorProps {
  executions: QueuedExecution[];
}

export function ExecutionQueueMonitor({ executions }: ExecutionQueueMonitorProps) {
  const activeExecutions = executions.filter(e => e.status === 'running' || e.status === 'pending');
  const completedExecutions = executions.filter(e => e.status === 'completed');
  const failedExecutions = executions.filter(e => e.status === 'failed');
  const blockedExecutions = executions.filter(e => e.status === 'blocked');

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <Circle weight="fill" className="w-4 h-4 text-accent animate-pulse" />;
      case 'completed':
        return <CheckCircle weight="fill" className="w-4 h-4 text-green-500" />;
      case 'failed':
        return <XCircle weight="fill" className="w-4 h-4 text-destructive" />;
      case 'blocked':
        return <HourglassHigh weight="fill" className="w-4 h-4 text-yellow-500" />;
      default:
        return <Clock weight="fill" className="w-4 h-4 text-muted-foreground" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'border-accent bg-accent/5';
      case 'completed':
        return 'border-green-500 bg-green-500/5';
      case 'failed':
        return 'border-destructive bg-destructive/5';
      case 'blocked':
        return 'border-yellow-500 bg-yellow-500/5';
      default:
        return 'border-border bg-muted/30';
    }
  };

  const formatTime = (ms?: number) => {
    if (!ms) return '--';
    const seconds = Math.floor(ms / 1000);
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    return `${minutes}m ${seconds % 60}s`;
  };

  if (executions.length === 0) {
    return null;
  }

  return (
    <Card className="p-6 bg-gradient-to-br from-card to-[oklch(0.27_0.03_270)]">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold">Execution Queue</h3>
          <p className="text-sm text-muted-foreground">
            Real-time workflow execution monitoring
          </p>
        </div>
        <div className="flex gap-3">
          <div className="flex items-center gap-2">
            <Circle weight="fill" className="w-3 h-3 text-accent" />
            <span className="text-sm font-mono">{activeExecutions.length}</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle weight="fill" className="w-3 h-3 text-green-500" />
            <span className="text-sm font-mono">{completedExecutions.length}</span>
          </div>
          {failedExecutions.length > 0 && (
            <div className="flex items-center gap-2">
              <XCircle weight="fill" className="w-3 h-3 text-destructive" />
              <span className="text-sm font-mono">{failedExecutions.length}</span>
            </div>
          )}
          {blockedExecutions.length > 0 && (
            <div className="flex items-center gap-2">
              <HourglassHigh weight="fill" className="w-3 h-3 text-yellow-500" />
              <span className="text-sm font-mono">{blockedExecutions.length}</span>
            </div>
          )}
        </div>
      </div>

      <div className="space-y-3">
        <AnimatePresence mode="popLayout">
          {executions.map((execution) => (
            <motion.div
              key={execution.tokenId}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              layout
            >
              <Card className={`p-4 border-2 transition-all ${getStatusColor(execution.status)}`}>
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3 flex-1">
                    <span className="text-2xl">{execution.tokenIcon}</span>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-semibold">{execution.tokenName}</h4>
                        {getStatusIcon(execution.status)}
                        <Badge 
                          variant="outline" 
                          className={`text-xs ${
                            execution.status === 'running' ? 'border-accent text-accent' :
                            execution.status === 'completed' ? 'border-green-500 text-green-500' :
                            execution.status === 'failed' ? 'border-destructive text-destructive' :
                            execution.status === 'blocked' ? 'border-yellow-500 text-yellow-500' :
                            ''
                          }`}
                        >
                          {execution.status}
                        </Badge>
                      </div>
                      
                      {execution.status === 'blocked' && execution.blockedBy && (
                        <div className="text-xs text-yellow-500 flex items-center gap-1">
                          <HourglassHigh weight="fill" className="w-3 h-3" />
                          <span>Waiting for: {execution.blockedBy.join(', ')}</span>
                        </div>
                      )}

                      {(execution.status === 'running' || execution.status === 'pending') && (
                        <div className="mt-2">
                          <div className="flex items-center justify-between text-xs mb-1">
                            <span className="text-muted-foreground">Progress</span>
                            <span className="font-mono font-semibold">{execution.progress}%</span>
                          </div>
                          <Progress value={execution.progress} className="h-1.5" />
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="text-right text-xs text-muted-foreground">
                    {execution.startTime && execution.status === 'running' && (
                      <div className="flex items-center gap-1">
                        <Clock weight="fill" className="w-3 h-3" />
                        <span>{formatTime(Date.now() - execution.startTime)}</span>
                      </div>
                    )}
                    {execution.estimatedCompletion && execution.status === 'running' && (
                      <div className="mt-1">
                        ETA: {formatTime(execution.estimatedCompletion - Date.now())}
                      </div>
                    )}
                  </div>
                </div>
              </Card>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {activeExecutions.length === 0 && completedExecutions.length > 0 && (
        <div className="mt-4 p-3 bg-green-500/10 border border-green-500/20 rounded-lg text-center">
          <CheckCircle weight="fill" className="w-6 h-6 mx-auto mb-2 text-green-500" />
          <p className="text-sm text-green-500 font-semibold">All workflows completed successfully</p>
        </div>
      )}
    </Card>
  );
}
