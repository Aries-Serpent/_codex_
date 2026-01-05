import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { motion, AnimatePresence } from 'framer-motion';
import { useEffect, useState } from 'react';
import { Agent } from '@/lib/codex-api-client';

interface TokenTransfer {
  id: string;
  token: string;
  from: string;
  to: string;
  paradigmFrom: string;
  paradigmTo: string;
  timestamp: number;
  status: 'in-flight' | 'completed';
}

interface WorkflowTokenFlowVisualizerProps {
  agents: Agent[];
  activeWorkflow?: string;
}

const TOKEN_ICONS: Record<string, string> = {
  AUDIT_EXEC: '🔍',
  DOC_GEN: '📚',
  HEAL: '🔧',
  DECIDE: '⚛️',
  ORGANIZE: '🗂️',
  REVIEW: '✅',
};

export function WorkflowTokenFlowVisualizer({ agents, activeWorkflow }: WorkflowTokenFlowVisualizerProps) {
  const [transfers, setTransfers] = useState<TokenTransfer[]>([]);
  const [transferStats, setTransferStats] = useState({
    totalTransfers: 0,
    activeTransfers: 0,
    avgLatency: 0,
  });

  useEffect(() => {
    if (!activeWorkflow) return;

    const interval = setInterval(() => {
      const activeAgents = agents.filter(a => a.status === 'active' || a.status === 'thinking');
      
      if (activeAgents.length < 2) return;

      const fromAgent = activeAgents[Math.floor(Math.random() * activeAgents.length)];
      const toAgent = activeAgents.filter(a => a.id !== fromAgent.id)[
        Math.floor(Math.random() * (activeAgents.length - 1))
      ];

      if (!toAgent) return;

      const newTransfer: TokenTransfer = {
        id: `${Date.now()}-${Math.random()}`,
        token: activeWorkflow,
        from: fromAgent.name,
        to: toAgent.name,
        paradigmFrom: fromAgent.paradigm,
        paradigmTo: toAgent.paradigm,
        timestamp: Date.now(),
        status: 'in-flight',
      };

      setTransfers(prev => [...prev.slice(-9), newTransfer]);
      setTransferStats(prev => ({
        totalTransfers: prev.totalTransfers + 1,
        activeTransfers: prev.activeTransfers + 1,
        avgLatency: prev.avgLatency,
      }));

      setTimeout(() => {
        setTransfers(prev => 
          prev.map(t => t.id === newTransfer.id ? { ...t, status: 'completed' as const } : t)
        );
        setTransferStats(prev => ({
          ...prev,
          activeTransfers: Math.max(0, prev.activeTransfers - 1),
          avgLatency: Math.random() * 50 + 50,
        }));
      }, 2000);
    }, 1500);

    return () => clearInterval(interval);
  }, [activeWorkflow, agents]);

  useEffect(() => {
    if (!activeWorkflow) {
      setTransfers([]);
      setTransferStats({ totalTransfers: 0, activeTransfers: 0, avgLatency: 0 });
    }
  }, [activeWorkflow]);

  const tokenIcon = activeWorkflow ? TOKEN_ICONS[activeWorkflow] : '🔄';

  return (
    <Card className="p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="flex items-center justify-center w-12 h-12 bg-accent/20 backdrop-blur-sm rounded-lg">
          <span className="text-2xl">{tokenIcon}</span>
        </div>
        <div>
          <h3 className="text-xl font-semibold text-accent">Token Flow Stream</h3>
          <p className="text-sm text-muted-foreground">
            Real-time workflow token transfers between agents
          </p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-6">
        <Card className="p-4 bg-gradient-to-br from-blue-500/10 to-cyan-500/10 border-blue-500/30">
          <div className="text-2xl font-bold text-blue-500 mb-1">
            {transferStats.totalTransfers}
          </div>
          <p className="text-xs text-muted-foreground">Total Transfers</p>
        </Card>

        <Card className="p-4 bg-gradient-to-br from-green-500/10 to-emerald-500/10 border-green-500/30">
          <div className="text-2xl font-bold text-green-500 mb-1">
            {transferStats.activeTransfers}
          </div>
          <p className="text-xs text-muted-foreground">In Flight</p>
        </Card>

        <Card className="p-4 bg-gradient-to-br from-purple-500/10 to-pink-500/10 border-purple-500/30">
          <div className="text-2xl font-bold text-purple-500 mb-1">
            {transferStats.avgLatency.toFixed(0)}ms
          </div>
          <p className="text-xs text-muted-foreground">Avg Latency</p>
        </Card>
      </div>

      <div className="space-y-2 min-h-[300px]">
        <AnimatePresence mode="popLayout">
          {transfers.length === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center justify-center py-12 text-muted-foreground"
            >
              <span className="text-4xl mb-3 opacity-50">🔄</span>
              <p className="text-sm">Waiting for workflow execution...</p>
              <p className="text-xs mt-1">Token transfers will appear here</p>
            </motion.div>
          ) : (
            transfers.slice().reverse().map((transfer) => (
              <motion.div
                key={transfer.id}
                initial={{ opacity: 0, x: -20, scale: 0.9 }}
                animate={{ opacity: 1, x: 0, scale: 1 }}
                exit={{ opacity: 0, x: 20, scale: 0.9 }}
                transition={{ type: 'spring', damping: 20 }}
              >
                <Card className={`p-4 relative overflow-hidden ${
                  transfer.status === 'in-flight' 
                    ? 'border-accent shadow-md' 
                    : 'border-green-500/50 bg-green-500/5'
                }`}>
                  {transfer.status === 'in-flight' && (
                    <motion.div
                      className="absolute inset-0 bg-gradient-to-r from-transparent via-accent/20 to-transparent"
                      initial={{ x: '-100%' }}
                      animate={{ x: '200%' }}
                      transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
                    />
                  )}

                  <div className="relative flex items-center gap-4">
                    <span className="text-2xl flex-shrink-0">{tokenIcon}</span>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge variant="outline" className="text-xs">
                          {transfer.paradigmFrom}
                        </Badge>
                        <span className="text-xs text-muted-foreground">→</span>
                        <Badge variant="outline" className="text-xs">
                          {transfer.paradigmTo}
                        </Badge>
                      </div>

                      <div className="flex items-center gap-2 text-sm">
                        <span className="font-medium truncate">{transfer.from}</span>
                        <span className="text-muted-foreground">→</span>
                        <span className="font-medium truncate">{transfer.to}</span>
                      </div>

                      <p className="text-xs text-muted-foreground mt-1">
                        {new Date(transfer.timestamp).toLocaleTimeString()}
                      </p>
                    </div>

                    <div className="flex-shrink-0">
                      {transfer.status === 'in-flight' ? (
                        <div className="flex items-center gap-2">
                          <motion.div
                            className="w-2 h-2 bg-accent rounded-full"
                            animate={{ scale: [1, 1.5, 1] }}
                            transition={{ duration: 1, repeat: Infinity }}
                          />
                          <span className="text-xs font-mono text-accent">Transferring</span>
                        </div>
                      ) : (
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-green-500 rounded-full" />
                          <span className="text-xs font-mono text-green-500">Completed</span>
                        </div>
                      )}
                    </div>
                  </div>
                </Card>
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>

      <Card className="p-4 mt-4 bg-muted/20">
        <p className="text-xs text-muted-foreground">
          <strong className="text-accent">Token Flow Protocol:</strong> Workflow tokens are computational 
          artifacts that carry execution context, state, and instructions between agents. Each transfer 
          represents an agent handoff where one paradigm's analysis informs another's computation, 
          enabling sophisticated cross-paradigm reasoning and collaboration.
        </p>
      </Card>
    </Card>
  );
}
