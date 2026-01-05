import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Task } from '@/lib/codex-api-client';
import { Clock, CheckCircle, XCircle, Hourglass } from '@phosphor-icons/react';

interface TaskQueueProps {
  tasks: Task[];
}

export function TaskQueue({ tasks }: TaskQueueProps) {
  const statusConfig = {
    pending: { color: 'text-muted-foreground', bg: 'bg-muted', icon: Hourglass, label: 'Pending' },
    running: { color: 'text-blue-500', bg: 'bg-blue-500/20', icon: Clock, label: 'Running' },
    completed: { color: 'text-green-500', bg: 'bg-green-500/20', icon: CheckCircle, label: 'Completed' },
    failed: { color: 'text-red-500', bg: 'bg-red-500/20', icon: XCircle, label: 'Failed' },
  };

  const sortedTasks = [...tasks].sort((a, b) => {
    const order = { running: 0, pending: 1, completed: 2, failed: 3 };
    return order[a.status] - order[b.status];
  });

  return (
    <div>
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <Clock weight="duotone" className="w-5 h-5 text-accent" />
        Task Queue ({tasks.length})
      </h3>

      {tasks.length === 0 ? (
        <Card className="p-8">
          <div className="text-center text-muted-foreground">
            <Clock weight="duotone" className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>No tasks in queue</p>
            <p className="text-sm mt-1">Execute a workflow to see tasks here</p>
          </div>
        </Card>
      ) : (
        <div className="space-y-3">
          {sortedTasks.slice(0, 10).map((task) => {
            const config = statusConfig[task.status];
            const Icon = config.icon;

            return (
              <Card key={task.id} className={`p-4 ${config.bg} border-l-4`}>
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3 flex-1">
                    <Icon weight="fill" className={`w-5 h-5 ${config.color} flex-shrink-0 mt-0.5`} />
                    <div className="flex-1 min-w-0">
                      <p className="font-medium truncate">{task.description}</p>
                      {task.assigned_agent && (
                        <p className="text-sm text-muted-foreground mt-1">
                          Assigned to: <span className="font-medium">{task.assigned_agent}</span>
                        </p>
                      )}
                      <div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
                        {task.started_at && (
                          <span>Started: {new Date(task.started_at).toLocaleTimeString()}</span>
                        )}
                        {task.completed_at && (
                          <span>Completed: {new Date(task.completed_at).toLocaleTimeString()}</span>
                        )}
                      </div>
                    </div>
                  </div>
                  <Badge variant="outline" className={`${config.color} border-current text-xs flex-shrink-0`}>
                    {config.label}
                  </Badge>
                </div>
              </Card>
            );
          })}

          {tasks.length > 10 && (
            <p className="text-center text-sm text-muted-foreground">
              Showing 10 of {tasks.length} tasks
            </p>
          )}
        </div>
      )}
    </div>
  );
}
