# Prompt Generator Interactive Demo Expansion Plan

**Document ID:** PGIDE-2026-01-06
**Version:** 1.0.0
**Status:** Ready for Implementation
**Estimated Effort:** 8-12 hours
**Priority:** High - Cognitive Brain Enhancement

---

## Executive Summary

This document outlines the comprehensive plan to expand the prompt generator with an interactive demo feature that executes and visualizes generated scripts in real-time within the cognitive app interface.

---

## 🎯 Objectives

### Primary Goals
1. Add interactive script execution environment to prompt generator
2. Provide real-time visualization of script outputs
3. Enable users to test generated prompts immediately
4. Create sandboxed execution environment for safety
5. Display execution metrics and performance data

### Success Criteria
- ✅ Scripts execute within 5 seconds of generation
- ✅ Real-time output streaming to UI
- ✅ Sandboxed environment prevents malicious code
- ✅ Visual feedback for execution status
- ✅ Error handling with clear messages
- ✅ Performance metrics displayed (execution time, memory usage)

---

## 📋 Implementation Phases

### Phase 1: Interactive Demo Infrastructure (3-4 hours)

#### 1.1 Create Interactive Demo Component
```typescript
// Location: cognitive_app/src/components/prompt/InteractiveDemo.tsx

interface InteractiveDemoProps {
  generatedScript: string;
  language: 'bash' | 'python' | 'javascript' | 'typescript';
  onExecute: (result: ExecutionResult) => void;
}

interface ExecutionResult {
  stdout: string;
  stderr: string;
  exitCode: number;
  executionTime: number;
  memoryUsage: number;
  timestamp: string;
}

export function InteractiveDemo({ generatedScript, language, onExecute }: InteractiveDemoProps) {
  // Component implementation
}
```

**Features:**
- Code editor with syntax highlighting (Monaco Editor or CodeMirror)
- Execute button with loading states
- Real-time output streaming
- Split-panel layout (code | output)
- Execution history
- Copy/download generated script

#### 1.2 Backend Execution API
```typescript
// Location: cognitive_app/src/lib/script-executor.ts

export class ScriptExecutor {
  async execute(script: string, language: string): Promise<ExecutionResult> {
    // Sandboxed execution
    // Real-time streaming
    // Resource limits
  }
}
```

**Safety Features:**
- Sandboxed container execution (Docker or VM)
- Resource limits (CPU, memory, time)
- Whitelist of allowed commands
- Input sanitization
- Output size limits

#### 1.3 WebSocket for Real-Time Streaming
```typescript
// Location: cognitive_app/src/lib/execution-stream.ts

export class ExecutionStream {
  connect(executionId: string): WebSocket;
  onOutput(callback: (data: string) => void): void;
  onError(callback: (error: string) => void): void;
  onComplete(callback: (result: ExecutionResult) => void): void;
  disconnect(): void;
}
```

---

### Phase 2: UI/UX Integration (2-3 hours)

#### 2.1 Enhanced Code Generator Layout
```
┌────────────────────────────────────────────────────────┐
│  Prompt Input                                          │
│  ┌──────────────────────────────────────────────────┐ │
│  │ [User prompt here]                               │ │
│  └──────────────────────────────────────────────────┘ │
│  [Generate] [Clear]                                   │
├────────────────────────────────────────────────────────┤
│  Generated Script          │  Interactive Demo         │
│  ┌───────────────────────┐ │ ┌──────────────────────┐ │
│  │ #!/bin/bash          │ │ │ [▶ Execute] [Stop]   │ │
│  │ echo "Hello"         │ │ ├──────────────────────┤ │
│  │ # Generated...       │ │ │ Output:              │ │
│  │                      │ │ │ Hello                │ │
│  └───────────────────────┘ │ │ Exit: 0 (120ms)     │ │
│  [Copy] [Download]        │ └──────────────────────┘ │
└────────────────────────────────────────────────────────┘
```

#### 2.2 Visual Components
- **Execution Status Badge:** Running | Success | Failed | Timeout
- **Progress Bar:** Real-time execution progress
- **Metrics Panel:** Time, memory, CPU usage
- **Output Highlighting:** Color-coded stdout/stderr
- **Interactive Controls:** Pause, resume, stop execution

#### 2.3 Responsive Design
- Desktop: Side-by-side layout
- Tablet: Tabbed interface
- Mobile: Stacked vertical layout

---

### Phase 3: Advanced Features (3-4 hours)

#### 3.1 Multi-Step Execution Visualization
```typescript
interface ExecutionStep {
  stepNumber: number;
  command: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  output: string;
  duration: number;
}

// Visualize each command in a script as separate steps
```

**UI Components:**
- Step-by-step progress timeline
- Expandable output for each step
- Jump to failed step
- Retry individual steps

#### 3.2 Execution History & Comparison
```typescript
interface ExecutionHistory {
  id: string;
  script: string;
  timestamp: string;
  result: ExecutionResult;
  metadata: {
    promptUsed: string;
    language: string;
    version: string;
  };
}
```

**Features:**
- Save execution results
- Compare multiple runs
- Export history as JSON/CSV
- Search and filter history
- Performance trends over time

#### 3.3 Interactive Input Injection
```typescript
interface InteractiveInput {
  prompt: string;
  type: 'text' | 'password' | 'choice';
  required: boolean;
  defaultValue?: string;
}
```

**Use Cases:**
- Scripts requiring user input
- Environment variable injection
- Configuration parameters
- API keys (securely handled)

#### 3.4 Visualization Plugins
```typescript
interface VisualizationPlugin {
  name: string;
  supportedOutputs: string[]; // JSON, CSV, logs
  render(data: any): ReactNode;
}
```

**Built-in Plugins:**
- JSON Tree Viewer
- CSV Data Table
- Log File Analyzer
- Chart Generator (for numeric data)
- Network Request Visualizer

---

### Phase 4: Backend Integration (2-3 hours)

#### 4.1 Execution Backend Service
```python
# Location: src/codex/script_executor/executor.py

from typing import Dict, Any
import asyncio
import docker
import resource

class ScriptExecutor:
    def __init__(self, max_execution_time: int = 30):
        self.docker_client = docker.from_env()
        self.max_execution_time = max_execution_time

    async def execute_script(
        self,
        script: str,
        language: str,
        resource_limits: Dict[str, Any]
    ) -> ExecutionResult:
        """Execute script in sandboxed Docker container"""
        # Implementation
        pass

    async def stream_output(self, execution_id: str) -> AsyncIterator[str]:
        """Stream execution output in real-time"""
        # Implementation
        pass
```

#### 4.2 API Endpoints
```python
# FastAPI endpoints

@app.post("/api/v1/script/execute")
async def execute_script(request: ExecuteRequest) -> ExecuteResponse:
    """Start script execution"""
    pass

@app.get("/api/v1/script/{execution_id}/stream")
async def stream_execution(execution_id: str) -> EventSourceResponse:
    """SSE endpoint for real-time output"""
    pass

@app.post("/api/v1/script/{execution_id}/stop")
async def stop_execution(execution_id: str) -> StopResponse:
    """Stop running execution"""
    pass

@app.get("/api/v1/script/{execution_id}/result")
async def get_result(execution_id: str) -> ExecutionResult:
    """Get final execution result"""
    pass
```

#### 4.3 Docker Configuration
```dockerfile
# Sandbox container for script execution
FROM python:3.11-slim

# Security hardening
RUN useradd -m -u 1000 sandbox
USER sandbox

# Resource limits
ENV MAX_MEMORY=256M
ENV MAX_CPU=0.5

# Install minimal dependencies
RUN pip install --no-cache-dir \
    requests \
    pandas \
    numpy

WORKDIR /workspace
CMD ["python", "/workspace/script.py"]
```

---

## 🔒 Security Considerations

### Sandboxing Strategy
1. **Container Isolation:** Execute all scripts in isolated Docker containers
2. **Network Restrictions:** Disable network access by default (opt-in)
3. **Filesystem Access:** Read-only mount except /tmp
4. **User Permissions:** Non-root user execution
5. **Resource Limits:**
   - CPU: 0.5 cores
   - Memory: 256MB
   - Execution time: 30 seconds
   - Output size: 1MB

### Input Validation
```typescript
function validateScript(script: string, language: string): ValidationResult {
  const blockedPatterns = [
    /rm\s+-rf\s+\//, // Dangerous deletion
    /sudo/, // Privilege escalation
    /curl.*\|\s*bash/, // Remote execution
    /eval\(/, // Dynamic execution
  ];

  // Check for malicious patterns
  // Validate syntax
  // Check file size limits
}
```

### Rate Limiting
- 10 executions per minute per user
- 100 executions per hour per user
- Exponential backoff for failures

---

## 📊 Monitoring & Analytics

### Execution Metrics
```typescript
interface ExecutionMetrics {
  totalExecutions: number;
  successRate: number;
  averageExecutionTime: number;
  popularLanguages: Record<string, number>;
  errorFrequency: Record<string, number>;
  resourceUtilization: {
    avgCpu: number;
    avgMemory: number;
    peakCpu: number;
    peakMemory: number;
  };
}
```

### Dashboard Integration
- Real-time execution statistics
- User engagement metrics
- Error rate tracking
- Performance bottleneck identification

---

## 🎨 UI Components Specification

### 1. InteractiveDemoPanel Component
```tsx
<InteractiveDemoPanel>
  <ExecutionControls>
    <PlayButton onClick={handleExecute} disabled={isRunning} />
    <StopButton onClick={handleStop} disabled={!isRunning} />
    <ClearButton onClick={handleClear} />
  </ExecutionControls>

  <ExecutionStatus>
    <StatusBadge status={executionStatus} />
    <ProgressBar progress={executionProgress} />
    <ElapsedTime time={elapsedTime} />
  </ExecutionStatus>

  <OutputPanel>
    <TabList>
      <Tab>Output</Tab>
      <Tab>Errors</Tab>
      <Tab>Metrics</Tab>
      <Tab>Visualization</Tab>
    </TabList>
    <TabPanels>
      <StdoutPanel content={stdout} />
      <StderrPanel content={stderr} />
      <MetricsPanel metrics={metrics} />
      <VisualizationPanel data={visualizationData} />
    </TabPanels>
  </OutputPanel>

  <ExecutionHistory items={history} />
</InteractiveDemoPanel>
```

### 2. Styling & Theming
```typescript
const interactiveDemoTheme = {
  colors: {
    running: '#3b82f6', // Blue
    success: '#10b981', // Green
    error: '#ef4444', // Red
    warning: '#f59e0b', // Amber
    info: '#6366f1', // Indigo
  },
  fonts: {
    code: 'Monaco, Menlo, "Ubuntu Mono", monospace',
    ui: 'Inter, system-ui, sans-serif',
  },
  spacing: {
    panel: '1rem',
    gutter: '0.5rem',
  },
};
```

---

## 🧪 Testing Strategy

### Unit Tests
```typescript
describe('InteractiveDemo', () => {
  it('should execute script and display output', async () => {
    // Test implementation
  });

  it('should handle execution errors gracefully', async () => {
    // Test implementation
  });

  it('should stop running execution', async () => {
    // Test implementation
  });

  it('should stream output in real-time', async () => {
    // Test implementation
  });
});
```

### Integration Tests
- Backend API execution flow
- WebSocket connection stability
- Container orchestration
- Resource limit enforcement
- Security validation

### E2E Tests (Playwright)
```typescript
test('execute bash script and view output', async ({ page }) => {
  await page.goto('/code-generator');
  await page.fill('[data-testid="prompt-input"]', 'Create a hello world script');
  await page.click('[data-testid="generate-button"]');
  await page.waitForSelector('[data-testid="generated-script"]');
  await page.click('[data-testid="execute-button"]');
  await page.waitForSelector('[data-testid="execution-success"]');

  const output = await page.textContent('[data-testid="stdout"]');
  expect(output).toContain('Hello');
});
```

---

## 📚 Documentation Requirements

### User Guide
1. **Getting Started:** How to use interactive demo
2. **Execution Controls:** Play, stop, clear explained
3. **Understanding Output:** Stdout, stderr, metrics
4. **Security Notes:** What's allowed, what's blocked
5. **Troubleshooting:** Common errors and solutions

### Developer Guide
1. **Architecture Overview:** Component structure
2. **API Reference:** Backend endpoints
3. **Adding Visualizations:** Plugin system
4. **Extending Languages:** Adding new runtime support
5. **Security Guidelines:** Safe execution practices

---

## 🚀 Deployment Plan

### Phase 1: Development Environment
- Local Docker setup
- Mock execution backend
- Development-only features

### Phase 2: Staging Environment
- Real Docker orchestration
- Rate limiting enabled
- Full monitoring stack

### Phase 3: Production Rollout
- Feature flag controlled
- A/B testing (50% users)
- Performance monitoring
- Security audits

---

## 📈 Success Metrics

### User Engagement
- **Target:** 60% of generated scripts executed
- **Measurement:** Execution rate per generation
- **Timeline:** Track weekly

### Performance
- **Target:** <3s average execution time
- **Measurement:** P50, P95, P99 latency
- **Timeline:** Real-time monitoring

### Reliability
- **Target:** 99.5% success rate
- **Measurement:** Failed executions / total executions
- **Timeline:** Daily reports

### Security
- **Target:** Zero security incidents
- **Measurement:** Sandbox escapes, malicious code blocks
- **Timeline:** Continuous monitoring

---

## 🔄 Future Enhancements

### Phase 5: Collaborative Features
- Share execution results via URL
- Collaborative debugging sessions
- Live execution viewing
- Comment on outputs

### Phase 6: AI-Powered Insights
- Suggest optimizations for generated scripts
- Detect performance bottlenecks
- Recommend best practices
- Auto-fix common errors

### Phase 7: Advanced Visualizations
- 3D data visualization
- Interactive charts
- Network topology graphs
- Real-time system monitoring

---

## 📝 Implementation Checklist

### Infrastructure (Phase 1)
- [ ] Create InteractiveDemo component
- [ ] Implement ScriptExecutor backend
- [ ] Set up WebSocket streaming
- [ ] Configure Docker containers
- [ ] Add resource limits

### UI/UX (Phase 2)
- [ ] Design split-panel layout
- [ ] Add execution controls
- [ ] Implement output streaming UI
- [ ] Create status indicators
- [ ] Build responsive layouts

### Advanced Features (Phase 3)
- [ ] Multi-step visualization
- [ ] Execution history
- [ ] Interactive input injection
- [ ] Visualization plugins
- [ ] Performance metrics

### Backend (Phase 4)
- [ ] FastAPI endpoints
- [ ] Docker orchestration
- [ ] Real-time streaming
- [ ] Security hardening
- [ ] Rate limiting

### Testing
- [ ] Unit tests (90% coverage)
- [ ] Integration tests
- [ ] E2E tests
- [ ] Security tests
- [ ] Performance tests

### Documentation
- [ ] User guide
- [ ] Developer guide
- [ ] API documentation
- [ ] Security documentation
- [ ] Deployment guide

---

## 🎯 IMMEDIATE NEXT STEPS (Copy this as PR comment)

```markdown
@copilot Implement Interactive Demo for Prompt Generator

## Context
Expand the existing prompt generator (cognitive_app/src/components/code/CodeGenerator.tsx) with an interactive execution demo feature that allows users to run and visualize generated scripts in real-time.

## Objectives
1. Add interactive script execution environment
2. Display real-time output streaming
3. Implement sandboxed Docker execution backend
4. Create visual execution status indicators
5. Add performance metrics dashboard

## Phase 1 Tasks (Start Here - 3-4 hours)

### Task 1.1: Create InteractiveDemo Component
**Location:** `cognitive_app/src/components/prompt/InteractiveDemo.tsx`

**Requirements:**
- Monaco editor for code display/editing
- Execute/Stop/Clear control buttons
- Real-time output panel (stdout/stderr split)
- Execution status badge (Running/Success/Failed)
- Progress bar for execution
- Metrics display (time, memory, CPU)

**Dependencies:**
```bash
npm install @monaco-editor/react ws
```

**Component Structure:**
```tsx
export function InteractiveDemo({
  script,
  language,
  onExecute
}: InteractiveDemoProps) {
  // State management
  // WebSocket connection
  // Execution control handlers
  // Output streaming
}
```

### Task 1.2: Backend Execution API
**Location:** `src/codex/script_executor/executor.py`

**Requirements:**
- FastAPI endpoints for execution
- Docker container orchestration
- WebSocket/SSE for streaming
- Resource limits enforcement
- Security sandboxing

**API Endpoints:**
- POST `/api/v1/script/execute`
- GET `/api/v1/script/{id}/stream` (SSE)
- POST `/api/v1/script/{id}/stop`
- GET `/api/v1/script/{id}/result`

### Task 1.3: Integration with CodeGenerator
**Location:** `cognitive_app/src/components/code/CodeGenerator.tsx`

**Changes:**
- Add "Interactive Demo" toggle/tab
- Integrate InteractiveDemo component
- Pass generated script to demo
- Handle execution results
- Update UI layout (split-panel)

## Validation Requirements
- [ ] All 14 existing tests pass (100%)
- [ ] Build successful
- [ ] Script execution completes in <5s
- [ ] Output streams in real-time
- [ ] Sandbox prevents malicious code
- [ ] Resource limits enforced
- [ ] Error handling works

## Safety Measures
1. Docker container isolation
2. Resource limits (CPU: 0.5, Memory: 256MB, Time: 30s)
3. Network disabled by default
4. Input validation and sanitization
5. Rate limiting (10/min per user)

## Documentation
- Update DEV_TEST_COMPREHENSIVE_WALKTHROUGH.md
- Add Interactive Demo section to README
- Document API endpoints
- Security guidelines

## Success Criteria
✅ Scripts execute within sandboxed environment
✅ Real-time output visible in UI
✅ Status indicators update correctly
✅ Performance metrics displayed
✅ Error handling graceful
✅ All existing tests passing
✅ Build successful
✅ Zero security vulnerabilities

## Estimated Time: 8-12 hours total
- Phase 1 (Infrastructure): 3-4 hours ← START HERE
- Phase 2 (UI/UX): 2-3 hours
- Phase 3 (Advanced): 3-4 hours
- Phase 4 (Backend): 2-3 hours

Execute Phase 1 now, validate, then proceed to Phase 2.
```

---

**Document Status:** ✅ Ready for Implementation
**Next Action:** Post above prompt as PR comment and execute
**Maintenance:** Update after each phase completion
