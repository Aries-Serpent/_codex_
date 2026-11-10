import { useState } from 'react';
import { createRoot } from 'react-dom/client';
import { CascadingExecutionMonitor } from '../../src/components/quantum/CascadingExecutionMonitor';
import type { WorkflowToken } from '../../src/lib/workflow-dependency-engine';
import '../../src/index.css';

const tokens: WorkflowToken[] = [{
  id: 'synthetic', name: 'Synthetic two-stage token', icon: 'T',
  description: 'Timing contract only', paradigms: [], stages: ['first', 'second'], color: 'blue',
}];

export default function Fixture() {
  const [completedAt, setCompletedAt] = useState<number | null>(null);
  return (
    <main>
      <CascadingExecutionMonitor tokens={tokens} onExecuteToken={async () => {
        setCompletedAt(Date.now());
        return true;
      }} />
      <output aria-label="Completed at">{completedAt ?? 'pending'}</output>
    </main>
  );
}

const root = document.getElementById('root');
if (!root) throw new Error('Missing cascade fixture root');
createRoot(root).render(<Fixture />);
