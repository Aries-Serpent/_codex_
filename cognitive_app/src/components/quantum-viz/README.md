# Quantum Components Library

Complete documentation for the Quantum-Enhanced UI components in the Codex AI Assistant.

## Overview

This library contains React components that visualize and interact with the quantum-inspired cognitive brain system. All components are built with TypeScript, styled with Tailwind CSS, and animated with Framer Motion.

---

## Components

### MetricCard

A reusable card component for displaying metrics with trends, sparklines, and status indicators.

**Props:**

```typescript
interface MetricCardProps {
  title: string;              // Metric label
  value: string | number;     // Primary metric value
  unit?: string;              // Unit of measurement
  icon?: ReactNode;           // Icon component
  trend?: 'up' | 'down' | 'neutral';  // Trend direction
  trendValue?: string;        // Trend value display
  subtitle?: string;          // Additional description
  color?: string;             // Custom text color class
  target?: string;            // Target value display
  status?: 'optimal' | 'good' | 'warning' | 'critical';
  animated?: boolean;         // Enable pulse animation
  sparkline?: number[];       // Array of values for sparkline
}
```

**Usage:**

```tsx
import { MetricCard } from '@/components/quantum/MetricCard';
import { Brain } from '@phosphor-icons/react';

<MetricCard
  title="k₁ Factor"
  value="0.350"
  icon={<Brain weight="duotone" className="w-4 h-4 text-primary" />}
  status="optimal"
  target="≤0.35"
  trend="down"
  trendValue="2.5%"
  sparkline={[0.35, 0.34, 0.33, 0.35, 0.35]}
  animated
/>
```

**Status Colors:**
- `optimal`: Green (oklch(0.80 0.20 145))
- `good`: Green (oklch(0.75 0.18 140))
- `warning`: Yellow (oklch(0.70 0.15 60))
- `critical`: Red (oklch(0.55 0.22 25))

---

### EntanglementCard

Displays quantum entanglement between agent pairs with Bell states and metrics.

**Props:**

```typescript
interface EntanglementCardProps {
  pair: {
    agent1: string;
    agent2: string;
    entanglement_score: number;  // 0-1
    bell_state: string;          // Φ+, Φ-, Ψ+, Ψ-
    coherence: number;           // 0-1
    correlation: number;         // Correlation coefficient
  };
  index: number;  // For stagger animation
}
```

**Usage:**

```tsx
import { EntanglementCard } from '@/components/quantum/EntanglementCard';

<EntanglementCard
  pair={{
    agent1: "agent-001",
    agent2: "agent-003",
    entanglement_score: 0.85,
    bell_state: "Φ+",
    coherence: 0.92,
    correlation: 0.78
  }}
  index={0}
/>
```

**Bell State Colors:**
- `Φ+`: Magenta (oklch(0.55 0.25 350))
- `Φ-`: Purple (oklch(0.65 0.22 310))
- `Ψ+`: Cyan (oklch(0.70 0.18 200))
- `Ψ-`: Blue (oklch(0.60 0.20 285))

---

### QuantumMemoryViewer

Visualizes short-term and long-term memory with quantum metrics.

**Props:**

```typescript
interface QuantumMemoryViewerProps {
  memoryState: {
    stm_capacity: number;
    stm_used: number;
    ltm_capacity: number;
    ltm_used: number;
    cache_hit_rate: number;      // 0-1
    compression_rate: number;    // 0-1
    pattern_count: number;
    quantum_coherence: number;   // 0-1
  };
}
```

**Usage:**

```tsx
import { QuantumMemoryViewer } from '@/components/quantum/QuantumMemoryViewer';

<QuantumMemoryViewer
  memoryState={{
    stm_capacity: 50,
    stm_used: 35,
    ltm_capacity: 1000,
    ltm_used: 450,
    cache_hit_rate: 0.42,
    compression_rate: 0.65,
    pattern_count: 127,
    quantum_coherence: 0.88
  }}
/>
```

**Performance Targets:**
- Cache Hit Rate: ≥30%
- Compression Rate: ≥60%
- STM Usage: <80%

---

### TaskItem

Individual task display with status, agent assignment, and workflow token.

**Props:**

```typescript
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
```

**Usage:**

```tsx
import { TaskItem } from '@/components/quantum/TaskItem';

<TaskItem
  task={{
    id: "task-001",
    description: "Analyze code complexity",
    assigned_agent: "agent-003",
    status: "running",
    started_at: "2024-01-04T10:30:00Z",
    completed_at: null,
    priority: 1,
    workflow_token: "AUDIT_EXEC"
  }}
  index={0}
/>
```

**Status Icons:**
- `pending`: Clock
- `running`: Lightning (animated)
- `completed`: CheckCircle
- `failed`: XCircle

---

### ActionPathViewer

Displays energy optimization paths with physics paradigms.

**Props:**

```typescript
interface ActionPathViewerProps {
  paths: Array<{
    path_id: string;
    description: string;
    paradigm: 'chaos' | 'fractal' | 'fluid' | 'electromagnetic' | 'wave' | 'relativity';
    potential_energy: number;
    kinetic_energy: number;
    total_energy: number;
    efficiency: number;         // 0-1
    steps: string[];
  }>;
}
```

**Usage:**

```tsx
import { ActionPathViewer } from '@/components/quantum/ActionPathViewer';

<ActionPathViewer
  paths={[
    {
      path_id: "path-001",
      description: "Optimize using fluid dynamics",
      paradigm: "fluid",
      potential_energy: 45.2,
      kinetic_energy: 32.8,
      total_energy: 78.0,
      efficiency: 0.87,
      steps: ["Initialize", "Analyze", "Transform", "Verify"]
    }
  ]}
/>
```

**Paradigm Colors:**
- Chaos: `oklch(0.50 0.25 30)` 🌀
- Fractal: `oklch(0.55 0.22 60)` 🔺
- Fluid: `oklch(0.60 0.20 220)` 💧
- Electromagnetic: `oklch(0.65 0.20 180)` ⚡
- Wave: `oklch(0.70 0.18 250)` 〰️
- Relativity: `oklch(0.50 0.20 320)` ⏰

---

### ForceVectorBar

Visualizes force vectors with magnitude, direction, and animated indicators.

**Props:**

```typescript
interface ForceVectorBarProps {
  vector: {
    name: string;
    magnitude: number;   // 0-100
    direction: number;   // Degrees 0-360
    color: string;       // CSS color
  };
  index: number;
  maxMagnitude?: number;
}
```

**Usage:**

```tsx
import { ForceVectorBar } from '@/components/quantum/ForceVectorBar';

<ForceVectorBar
  vector={{
    name: "Gravitational Force",
    magnitude: 65.5,
    direction: 270,
    color: "oklch(0.60 0.20 220)"
  }}
  index={0}
  maxMagnitude={100}
/>
```

**Direction Labels:**
- 0°: E (East)
- 45°: NE (Northeast)
- 90°: N (North)
- 135°: NW (Northwest)
- 180°: W (West)
- 225°: SW (Southwest)
- 270°: S (South)
- 315°: SE (Southeast)

---

### OperationsLog

Timeline of memory operations with performance metrics.

**Props:**

```typescript
interface OperationsLogProps {
  operations: Array<{
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
  }>;
  maxHeight?: string;
}
```

**Usage:**

```tsx
import { OperationsLog } from '@/components/quantum/OperationsLog';

<OperationsLog
  operations={[
    {
      id: "op-001",
      type: "store",
      description: "Stored decision pattern",
      timestamp: "2024-01-04T10:30:00Z",
      duration_ms: 45,
      success: true,
      metadata: {
        entries_affected: 1,
        cache_hit: false
      }
    }
  ]}
  maxHeight="400px"
/>
```

**Performance Labels:**
- Fast: <50ms (green)
- Normal: 50-200ms (yellow)
- Slow: >200ms (red)

---

### MetricsDashboard

Aggregated real-time metrics dashboard with auto-refresh.

**Props:**

None - uses hooks internally.

**Usage:**

```tsx
import { MetricsDashboard } from '@/components/quantum/MetricsDashboard';

<MetricsDashboard />
```

**Features:**
- Auto-refresh every 10 seconds
- Quantum brain metrics (k₁, advantage, coherence, accuracy)
- Agent orchestration metrics (active agents, tasks, success rate)
- Memory system metrics (cache hit, patterns, compression, STM)
- Sparkline charts for trending data
- Status indicators with color coding

---

## Integration Guide

### 1. Install Dependencies

All dependencies are pre-installed in the spark-template:
- `react` (19.2.0)
- `framer-motion` (12.23.25)
- `@phosphor-icons/react` (2.1.10)
- `date-fns` (3.6.0)

### 2. Import Components

```tsx
import { MetricCard } from '@/components/quantum/MetricCard';
import { EntanglementCard } from '@/components/quantum/EntanglementCard';
import { QuantumMemoryViewer } from '@/components/quantum/QuantumMemoryViewer';
import { TaskItem } from '@/components/quantum/TaskItem';
import { ActionPathViewer } from '@/components/quantum/ActionPathViewer';
import { ForceVectorBar } from '@/components/quantum/ForceVectorBar';
import { OperationsLog } from '@/components/quantum/OperationsLog';
import { MetricsDashboard } from '@/components/quantum/MetricsDashboard';
```

### 3. Use Custom Hooks

```tsx
import { useQuantumState } from '@/hooks/use-quantum-state';
import { useAgentOrchestration } from '@/hooks/use-agent-orchestration';
import { useMemorySystem } from '@/hooks/use-memory-system';

function MyComponent() {
  const { state: quantumState, loading, error } = useQuantumState(true, 10000);
  const { state: agentState, orchestrateTask } = useAgentOrchestration();
  const { state: memoryState, searchMemories } = useMemorySystem();
  
  // Component logic
}
```

---

## Theming

All components use the design system colors defined in `index.css`:

```css
:root {
  /* Quantum States */
  --quantum-superposition: oklch(0.65 0.22 310);
  --quantum-entangled: oklch(0.55 0.25 350);
  --quantum-collapsed: oklch(0.70 0.18 200);
  --quantum-coherence: oklch(0.60 0.20 285);

  /* Agent Status */
  --agent-active: oklch(0.75 0.18 140);
  --agent-thinking: oklch(0.65 0.20 280);
  --agent-idle: oklch(0.50 0.05 260);
  --agent-error: oklch(0.55 0.22 25);

  /* Memory Hierarchy */
  --memory-stm: oklch(0.70 0.18 40);
  --memory-ltm: oklch(0.60 0.15 220);
  --memory-compressed: oklch(0.55 0.20 160);
  --memory-pattern: oklch(0.65 0.18 280);
}
```

---

## Performance Optimization

### Memoization

Components use `useMemo` and `useCallback` for expensive calculations:

```tsx
const expensiveCalculation = useMemo(() => {
  return computeMetrics(data);
}, [data]);
```

### Animation Performance

All animations use GPU-accelerated properties:
- `transform` (translate, scale, rotate)
- `opacity`

Avoid animating:
- `width`/`height` (use `scale` instead)
- `top`/`left` (use `transform` instead)

### Virtualization

For large lists (>50 items), consider using `react-window`:

```tsx
import { FixedSizeList } from 'react-window';

<FixedSizeList
  height={400}
  itemCount={operations.length}
  itemSize={80}
>
  {({ index, style }) => (
    <div style={style}>
      <TaskItem task={tasks[index]} index={index} />
    </div>
  )}
</FixedSizeList>
```

---

## Troubleshooting

### Issue: Animations not working

**Solution:** Ensure `framer-motion` is installed:
```bash
npm install framer-motion@12.23.25
```

### Issue: Icons not displaying

**Solution:** Check `@phosphor-icons/react` installation:
```bash
npm install @phosphor-icons/react@2.1.10
```

### Issue: Dates showing "Invalid Date"

**Solution:** Ensure timestamps are ISO 8601 format:
```tsx
timestamp: new Date().toISOString()  // ✓ Correct
timestamp: "2024-01-04 10:30:00"     // ✗ Incorrect
```

### Issue: Colors not applying

**Solution:** Verify Tailwind config includes OKLCH colors and that `index.css` is imported in `main.css`.

---

## Testing

### Unit Tests

```tsx
import { render, screen } from '@testing-library/react';
import { MetricCard } from '@/components/quantum/MetricCard';

test('renders metric value', () => {
  render(<MetricCard title="Test" value="42" />);
  expect(screen.getByText('42')).toBeInTheDocument();
});
```

### Integration Tests

```tsx
import { render, screen, waitFor } from '@testing-library/react';
import { MetricsDashboard } from '@/components/quantum/MetricsDashboard';

test('displays quantum metrics', async () => {
  render(<MetricsDashboard />);
  
  await waitFor(() => {
    expect(screen.getByText(/k₁ Factor/i)).toBeInTheDocument();
  });
});
```

---

## API Reference

### CodexAPIClient

```typescript
class CodexAPIClient {
  async getQuantumState(): Promise<QuantumStateResponse>
  async getAgentState(): Promise<AgentStateResponse>
  async getMemoryState(): Promise<MemoryStateResponse>
  async orchestrateTask(description: string, token?: string): Promise<void>
  async searchMemories(query: string): Promise<MemoryEntry[]>
}
```

### Mock Client

For development without backend:

```typescript
import { MockCodexAPIClient } from '@/lib/mock-api-client';

const client = new MockCodexAPIClient();
const state = await client.getQuantumState();
```

---

## Contributing

When adding new components:

1. **Follow naming conventions**: PascalCase for components
2. **Use TypeScript**: Define all props interfaces
3. **Add documentation**: Include props, usage, and examples
4. **Write tests**: Unit tests for logic, integration for hooks
5. **Optimize performance**: Use memoization and virtualization
6. **Maintain accessibility**: ARIA labels, keyboard navigation
7. **Follow design system**: Use OKLCH colors and Tailwind utilities

---

## Support

For questions or issues:
- Check troubleshooting section
- Review component examples
- Consult Codex master plan document

**Version:** 1.0.0  
**Last Updated:** 2025-01-04
