import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  ArrowsClockwise, 
  Database, 
  MagnifyingGlass, 
  Package, 
  Trash 
} from '@phosphor-icons/react';
import { motion } from 'framer-motion';
import { formatDistanceToNow } from 'date-fns';

interface MemoryOperation {
  id: string;
  type: 'store' | 'retrieve' | 'compress' | 'delete' | 'search';
  description: string;
  timestamp: string;
  duration_ms: number;
  success: boolean;
  metadata?: {
    entries_affected?: number;
    compression_ratio?: number;
    cache_hit?: boolean;
  };
}

interface OperationsLogProps {
  operations: MemoryOperation[];
  maxHeight?: string;
}

const operationIcons = {
  store: Database,
  retrieve: MagnifyingGlass,
  compress: Package,
  delete: Trash,
  search: MagnifyingGlass,
};

const operationColors = {
  store: 'text-[oklch(0.75_0.18_140)]',
  retrieve: 'text-[oklch(0.70_0.15_220)]',
  compress: 'text-[oklch(0.65_0.20_60)]',
  delete: 'text-[oklch(0.55_0.22_25)]',
  search: 'text-[oklch(0.60_0.20_285)]',
};

const operationBgColors = {
  store: 'bg-[oklch(0.75_0.18_140)]/20',
  retrieve: 'bg-[oklch(0.70_0.15_220)]/20',
  compress: 'bg-[oklch(0.65_0.20_60)]/20',
  delete: 'bg-[oklch(0.55_0.22_25)]/20',
  search: 'bg-[oklch(0.60_0.20_285)]/20',
};

export function OperationsLog({ operations, maxHeight = '400px' }: OperationsLogProps) {
  const getPerformanceLabel = (ms: number) => {
    if (ms < 50) return { label: 'Fast', color: 'text-[oklch(0.75_0.18_140)]' };
    if (ms < 200) return { label: 'Normal', color: 'text-[oklch(0.70_0.15_60)]' };
    return { label: 'Slow', color: 'text-[oklch(0.55_0.22_25)]' };
  };

  return (
    <Card className="p-4 bg-card border-border">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <ArrowsClockwise weight="duotone" className="w-5 h-5 text-accent" />
          <h3 className="text-sm font-semibold">Recent Operations</h3>
        </div>
        <Badge variant="outline" className="text-xs">
          {operations.length} operations
        </Badge>
      </div>

      <ScrollArea style={{ height: maxHeight }}>
        <div className="space-y-2 pr-4">
          {operations.length === 0 ? (
            <div className="text-center py-8">
              <Database weight="duotone" className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
              <p className="text-sm text-muted-foreground">
                No recent operations
              </p>
            </div>
          ) : (
            operations.map((operation, index) => {
              const OperationIcon = operationIcons[operation.type];
              const performance = getPerformanceLabel(operation.duration_ms);

              return (
                <motion.div
                  key={operation.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="flex items-start gap-3 p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors"
                >
                  <div className={`p-2 rounded-lg ${operationBgColors[operation.type]}`}>
                    <OperationIcon 
                      weight="duotone" 
                      className={`w-4 h-4 ${operationColors[operation.type]}`} 
                    />
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2 mb-1">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs font-semibold uppercase tracking-wide text-foreground">
                            {operation.type}
                          </span>
                          {operation.success ? (
                            <Badge className="text-xs bg-[oklch(0.75_0.18_140)]/20 text-[oklch(0.75_0.18_140)] border-0">
                              Success
                            </Badge>
                          ) : (
                            <Badge className="text-xs bg-[oklch(0.55_0.22_25)]/20 text-[oklch(0.55_0.22_25)] border-0">
                              Failed
                            </Badge>
                          )}
                        </div>
                        <p className="text-xs text-muted-foreground line-clamp-2">
                          {operation.description}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 mt-2 flex-wrap">
                      <div className={`text-xs ${performance.color}`}>
                        {operation.duration_ms}ms · {performance.label}
                      </div>

                      <div className="text-xs text-muted-foreground">
                        {formatDistanceToNow(new Date(operation.timestamp), { addSuffix: true })}
                      </div>

                      {operation.metadata?.cache_hit !== undefined && (
                        <Badge variant="outline" className="text-xs">
                          {operation.metadata.cache_hit ? '⚡ Cache Hit' : 'Cache Miss'}
                        </Badge>
                      )}

                      {operation.metadata?.entries_affected !== undefined && (
                        <Badge variant="outline" className="text-xs">
                          {operation.metadata.entries_affected} entries
                        </Badge>
                      )}

                      {operation.metadata?.compression_ratio !== undefined && (
                        <Badge variant="outline" className="text-xs">
                          {(operation.metadata.compression_ratio * 100).toFixed(0)}% compressed
                        </Badge>
                      )}
                    </div>
                  </div>
                </motion.div>
              );
            })
          )}
        </div>
      </ScrollArea>

      {operations.length > 0 && (
        <div className="mt-4 pt-4 border-t border-border">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-xs text-muted-foreground mb-1">Avg Duration</div>
              <div className="text-sm font-mono font-semibold text-foreground">
                {(operations.reduce((sum, op) => sum + op.duration_ms, 0) / operations.length).toFixed(0)}ms
              </div>
            </div>
            <div>
              <div className="text-xs text-muted-foreground mb-1">Success Rate</div>
              <div className="text-sm font-mono font-semibold text-[oklch(0.75_0.18_140)]">
                {((operations.filter(op => op.success).length / operations.length) * 100).toFixed(0)}%
              </div>
            </div>
            <div>
              <div className="text-xs text-muted-foreground mb-1">Total Ops</div>
              <div className="text-sm font-mono font-semibold text-foreground">
                {operations.length}
              </div>
            </div>
          </div>
        </div>
      )}
    </Card>
  );
}
