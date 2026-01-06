import { useEffect, useState } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Atom, Brain, Database, Lightning, TrendUp } from '@phosphor-icons/react';
import { MetricCard } from '@/components/quantum/MetricCard';
import { motion } from 'framer-motion';
import { useQuantumState } from '@/hooks/use-quantum-state';
import { useAgentOrchestration } from '@/hooks/use-agent-orchestration';
import { useMemorySystem } from '@/hooks/use-memory-system';

export function MetricsDashboard() {
  const { state: quantumState } = useQuantumState(true, 10000);
  const { state: agentState } = useAgentOrchestration(true, 10000);
  const { state: memoryState } = useMemorySystem(true, 10000);
  
  const [sparklines, setSparklines] = useState({
    k1: [] as number[],
    advantage: [] as number[],
    cacheHit: [] as number[],
    activeAgents: [] as number[],
  });

  useEffect(() => {
    if (quantumState) {
      setSparklines(prev => ({
        ...prev,
        k1: [...prev.k1.slice(-19), quantumState.k1_factor / 0.5].slice(0, 20),
        advantage: [...prev.advantage.slice(-19), quantumState.quantum_advantage / 5].slice(0, 20),
      }));
    }
  }, [quantumState]);

  useEffect(() => {
    if (memoryState) {
      setSparklines(prev => ({
        ...prev,
        cacheHit: [...prev.cacheHit.slice(-19), memoryState.cache_hit_rate].slice(0, 20),
      }));
    }
  }, [memoryState]);

  useEffect(() => {
    if (agentState) {
      const activeCount = agentState.agents.filter(a => a.status === 'active' || a.status === 'thinking').length;
      setSparklines(prev => ({
        ...prev,
        activeAgents: [...prev.activeAgents.slice(-19), activeCount / Math.max(agentState.agents.length, 1)].slice(0, 20),
      }));
    }
  }, [agentState]);

  const getQuantumStatus = () => {
    if (!quantumState) return 'good';
    if (quantumState.accuracy >= 0.9 && quantumState.coherence >= 0.7) return 'optimal';
    if (quantumState.accuracy >= 0.8 && quantumState.coherence >= 0.6) return 'good';
    if (quantumState.accuracy >= 0.7) return 'warning';
    return 'critical';
  };

  const getAgentStatus = () => {
    if (!agentState) return 'good';
    const activeCount = agentState.agents.filter(a => a.status === 'active' || a.status === 'thinking').length;
    const errorCount = agentState.agents.filter(a => a.status === 'error').length;
    
    if (activeCount >= 3 && errorCount === 0) return 'optimal';
    if (activeCount >= 2 && errorCount <= 1) return 'good';
    if (activeCount >= 1) return 'warning';
    return 'critical';
  };

  const getMemoryStatus = () => {
    if (!memoryState) return 'good';
    if (memoryState.cache_hit_rate >= 0.5 && memoryState.compression_rate >= 0.6) return 'optimal';
    if (memoryState.cache_hit_rate >= 0.3 && memoryState.compression_rate >= 0.5) return 'good';
    if (memoryState.cache_hit_rate >= 0.2) return 'warning';
    return 'critical';
  };

  const calculateSuccessRate = () => {
    if (!agentState) return 0;
    const completedTasks = agentState.tasks.filter(t => t.status === 'completed').length;
    const failedTasks = agentState.tasks.filter(t => t.status === 'failed').length;
    const total = completedTasks + failedTasks;
    return total > 0 ? (completedTasks / total) * 100 : 0;
  };

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h2 className="text-2xl font-bold gradient-text">System Metrics Dashboard</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Real-time cognitive brain performance monitoring
          </p>
        </div>
        <Badge variant="outline" className="text-xs">
          Auto-refresh: 10s
        </Badge>
      </motion.div>

      <div className="space-y-4">
        <Card className="p-4 bg-card border-border">
          <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
            <Atom weight="duotone" className="w-4 h-4 text-primary" />
            Quantum Brain Metrics
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <MetricCard
              title="k₁ Factor"
              value={quantumState?.k1_factor.toFixed(3) || '0.000'}
              icon={<Brain weight="duotone" className="w-4 h-4 text-primary" />}
              status={getQuantumStatus()}
              target="≤0.35"
              trend={quantumState && quantumState.k1_factor <= 0.35 ? 'down' : 'up'}
              trendValue={quantumState ? `${(quantumState.k1_factor * 100).toFixed(1)}%` : '0%'}
              sparkline={sparklines.k1}
            />
            
            <MetricCard
              title="Quantum Advantage"
              value={quantumState?.quantum_advantage.toFixed(2) || '0.00'}
              unit="×"
              icon={<Lightning weight="duotone" className="w-4 h-4 text-accent" />}
              status={quantumState && quantumState.quantum_advantage >= 2.5 ? 'optimal' : 'good'}
              target="≥2.86×"
              trend="up"
              trendValue={`${quantumState?.quantum_advantage.toFixed(1) || '0'}×`}
              sparkline={sparklines.advantage}
            />
            
            <MetricCard
              title="Coherence"
              value={quantumState ? (quantumState.coherence * 100).toFixed(1) : '0.0'}
              unit="%"
              icon={<span className="text-lg">⚛️</span>}
              status={quantumState && quantumState.coherence >= 0.65 ? 'optimal' : 'good'}
              target="≥65%"
              trend={quantumState && quantumState.coherence >= 0.65 ? 'up' : 'neutral'}
              trendValue={`${quantumState ? (quantumState.coherence * 100).toFixed(0) : '0'}%`}
            />
            
            <MetricCard
              title="Accuracy"
              value={quantumState ? (quantumState.accuracy * 100).toFixed(1) : '0.0'}
              unit="%"
              icon={<TrendUp weight="duotone" className="w-4 h-4 text-[oklch(0.75_0.18_140)]" />}
              status={quantumState && quantumState.accuracy >= 0.85 ? 'optimal' : 'good'}
              target="≥85%"
              trend="up"
              trendValue={`${quantumState ? (quantumState.accuracy * 100).toFixed(0) : '0'}%`}
            />
          </div>
        </Card>

        <Card className="p-4 bg-card border-border">
          <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
            <Lightning weight="duotone" className="w-4 h-4 text-[oklch(0.75_0.18_140)]" />
            Agent Orchestration Metrics
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <MetricCard
              title="Active Agents"
              value={agentState?.agents.filter(a => a.status === 'active' || a.status === 'thinking').length || 0}
              icon={<span className="text-lg">🤖</span>}
              status={getAgentStatus()}
              subtitle={`of ${agentState?.agents.length || 0} total`}
              sparkline={sparklines.activeAgents}
            />
            
            <MetricCard
              title="Task Queue"
              value={agentState?.tasks.filter(t => t.status === 'pending' || t.status === 'running').length || 0}
              icon={<Database weight="duotone" className="w-4 h-4 text-accent" />}
              status="good"
              subtitle={`${agentState?.tasks.filter(t => t.status === 'completed').length || 0} completed`}
            />
            
            <MetricCard
              title="Success Rate"
              value={calculateSuccessRate().toFixed(1)}
              unit="%"
              icon={<TrendUp weight="duotone" className="w-4 h-4 text-[oklch(0.75_0.18_140)]" />}
              status={calculateSuccessRate() >= 90 ? 'optimal' : calculateSuccessRate() >= 75 ? 'good' : 'warning'}
              target="≥90%"
              trend={calculateSuccessRate() >= 80 ? 'up' : 'neutral'}
            />
            
            <MetricCard
              title="Avg Response Time"
              value="125"
              unit="ms"
              icon={<Lightning weight="duotone" className="w-4 h-4 text-accent" />}
              status="optimal"
              target="<200ms"
              trend="down"
              trendValue="15ms"
            />
          </div>
        </Card>

        <Card className="p-4 bg-card border-border">
          <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
            <Database weight="duotone" className="w-4 h-4 text-[oklch(0.60_0.15_220)]" />
            Memory System Metrics
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <MetricCard
              title="Cache Hit Rate"
              value={memoryState ? (memoryState.cache_hit_rate * 100).toFixed(1) : '0.0'}
              unit="%"
              icon={<Lightning weight="duotone" className="w-4 h-4 text-accent" />}
              status={getMemoryStatus()}
              target="≥30%"
              trend={memoryState && memoryState.cache_hit_rate >= 0.3 ? 'up' : 'neutral'}
              trendValue={`${memoryState ? (memoryState.cache_hit_rate * 100).toFixed(0) : '0'}%`}
              sparkline={sparklines.cacheHit}
            />
            
            <MetricCard
              title="Pattern Count"
              value={memoryState?.patterns.length || 0}
              icon={<Database weight="duotone" className="w-4 h-4 text-[oklch(0.65_0.18_280)]" />}
              status="good"
              subtitle="Active patterns"
            />
            
            <MetricCard
              title="Compression Rate"
              value={memoryState ? (memoryState.compression_rate * 100).toFixed(1) : '0.0'}
              unit="%"
              icon={<span className="text-lg">📦</span>}
              status={memoryState && memoryState.compression_rate >= 0.6 ? 'optimal' : 'good'}
              target="≥60%"
              trend={memoryState && memoryState.compression_rate >= 0.6 ? 'up' : 'neutral'}
            />
            
            <MetricCard
              title="STM Usage"
              value={
                memoryState && memoryState.capacity > 0
                  ? ((memoryState.stm_count / memoryState.capacity) * 100).toFixed(0)
                  : '0'
              }
              unit="%"
              icon={<Lightning weight="duotone" className="w-4 h-4 text-[oklch(0.70_0.18_40)]" />}
              status={
                memoryState && memoryState.capacity > 0 && (memoryState.stm_count / memoryState.capacity) >= 0.8
                  ? 'warning'
                  : 'good'
              }
              subtitle={`${memoryState?.stm_count || 0} entries`}
            />
          </div>
        </Card>
      </div>
    </div>
  );
}
