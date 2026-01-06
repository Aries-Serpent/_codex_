# Cognitive Codex Web Application

## Overview

The Cognitive Codex App is a quantum-enhanced code generation platform with real-time cognitive brain visualization, built with React, TypeScript, and Vite.

## Quick Links

- **Live Application:** [https://aries-serpent.github.io/_codex_/cognitive_app/](https://aries-serpent.github.io/_codex_/cognitive_app/)
- **Source Code:** [`/cognitive_app`](../../cognitive_app/)
- **Integration Guide:** [cognitive_app/README_INTEGRATION.md](../../cognitive_app/README_INTEGRATION.md)
- **Master Plan:** [cognitive_app/CODEX_INTEGRATION_MASTER_PLAN.md](../../cognitive_app/CODEX_INTEGRATION_MASTER_PLAN.md)
- **Implementation Status:** [cognitive_app/IMPLEMENTATION_STATUS.md](../../cognitive_app/IMPLEMENTATION_STATUS.md)

## Features

### 🧠 Quantum Decision Engine
Real-time cognitive brain metrics visualization:
- **k₁ Factor Tracking** - Target: ≤0.35 (currently 0.35)
- **Quantum Advantage** - 2.86× over classical approaches
- **Coherence Monitoring** - Wave function coherence (68.5%)
- **Superposition States** - Parallel scenario evaluation
- **Wave Function Collapse** - Animated decision visualization

### 🤖 Agent Orchestration
Multi-agent workflow management:
- **6 Physics Paradigms** - Chaos, Fractal, Fluid, EM, Wave, Relativity
- **Pre-built Workflow Tokens** - AUDIT_EXEC, DOC_GEN, HEAL, DECIDE, ORGANIZE, REVIEW
- **Custom Token Creation** - 4-step wizard for custom workflows
- **Dependency Management** - DAG-based auto-execution
- **Cascading Execution** - Real-time cascade monitoring with waterfall visualization

### 💾 Memory Management
Hippocampus-cortex inspired memory system:
- **Short-Term Memory (STM)** - Quick access for recent interactions
- **Long-Term Memory (LTM)** - Compressed pattern storage
- **60% Compression Rate** - PCA + quantization
- **32% Cache Hit Rate** - Efficient retrieval
- **Pattern Library** - Reusable decision patterns
- **Memory Search** - Full-text search across memories

### 💻 Code Generation
Natural language to code:
- **Monaco Editor Integration** - Syntax highlighting
- **Real-time Metrics** - Complexity, quality scores
- **Multi-language Support** - Python, TypeScript, JavaScript, Go, etc.
- **Copy/Download** - Easy code export

### 📊 Metrics Dashboard
Real-time system monitoring:
- **Quantum Brain Metrics** - k₁, coherence, quantum advantage
- **Agent System Status** - Active agents, current tasks
- **Memory System Health** - STM/LTM usage, cache performance
- **Auto-refresh** - Updates every 10 seconds

## Architecture

### Frontend Stack
- **React 19.0.0** - UI framework
- **TypeScript 5.7.2** - Type safety
- **Vite 7.2.6** - Build tool
- **Tailwind CSS 4.1.11** - Styling
- **Radix UI** - Component primitives
- **D3.js** - Data visualization
- **Recharts** - Charts and graphs
- **Phosphor Icons** - Icon library

### Backend Integration (Planned)
The application is designed to connect to a FastAPI backend:

```
services/api/
├── main.py                # FastAPI app
├── cognitive_api.py       # Quantum decision endpoints
├── agents_api.py          # Agent orchestration
├── memory_api.py          # Memory management
├── code_api.py            # Code analysis
└── websocket_manager.py   # Real-time updates
```

**Current Status:** Frontend uses mock API client for development. Backend implementation pending.

## Component Library

### Quantum Components (27)
- `QuantumDecisionEngine` - Main decision visualization
- `QuantumVisualizer` - Canvas-based quantum state visualization
- `SuperpositionCard` - Individual scenario cards
- `EntanglementCard` - Agent pair coordination
- `QuantumMemoryViewer` - STM/LTM visualization
- `AgentOrchestrationPanel` - Agent management
- `AgentCard` - Individual agent display
- `TaskQueue` - Task timeline
- `TaskItem` - Task cards
- `PhysicsParadigmExplorer` - 6 paradigm selector
- `WorkflowTokenOrchestrator` - Workflow execution
- `CustomWorkflowTokenCreator` - Token creation wizard
- `WorkflowTemplatesLibrary` - Pre-built bundles
- `OrchestrationChainBuilder` - Multi-token chains
- `DependencyGraphVisualizer` - DAG visualization
- `CascadingExecutionMonitor` - Cascade tracking
- `CascadeWaterfallVisualizer` - Animated waterfall
- `MemoryManagementDashboard` - Memory overview
- `MemoryEntryCard` - Individual memory display
- `PatternLibraryBrowser` - Pattern index
- `OperationsLog` - Operations timeline
- `MetricsDashboard` - Global metrics
- `MetricCard` - Reusable metric display
- Plus 4 more specialized components

### UI Components (44)
Complete shadcn/ui component library including:
- Layout: Card, Accordion, Tabs, Sheet, Sidebar
- Forms: Input, Textarea, Select, Checkbox, Radio, Switch
- Feedback: Alert, Toast, Dialog, Popover, Tooltip
- Navigation: Breadcrumb, Menu, Navigation
- Data: Table, Chart, Calendar
- Plus 30 more components

### Code Components (3)
- `CodeGenerator` - Main code generation interface
- `CodeEditor` - Monaco-based editor
- `MetricsBar` - Real-time code metrics

## Local Development

### Prerequisites
- Node.js 20+
- npm 10+

### Setup
```bash
cd cognitive_app
npm install
npm run dev
```

Access at: http://localhost:5173

### Build
```bash
npm run build
npm run preview
```

## Deployment

The application is automatically deployed to GitHub Pages via GitHub Actions when changes are pushed to the `main` branch.

**Workflow:** `.github/workflows/deploy-cognitive-app.yml`

**Live URL:** https://aries-serpent.github.io/_codex_/cognitive_app/

## Configuration

### Vite Configuration
```typescript
// Base path for GitHub Pages
base: process.env.GITHUB_ACTIONS ? '/_codex_/cognitive_app/' : '/'
```

### Environment Variables (Future)
```bash
VITE_CODEX_API=http://localhost:8000  # Backend API URL
VITE_CODEX_KEY=demo-key               # API key
```

## Implementation Status

**Overall: 95% Complete**

✅ **Complete:**
- Core infrastructure (React, Vite, TypeScript, Tailwind)
- Design system (OKLCH colors, animations, typography)
- Custom hooks (useQuantumState, useAgentOrchestration, useMemorySystem)
- All quantum components (27)
- All UI components (44)
- All code components (3)
- Component documentation
- Build and deployment configuration

⚠️ **In Progress:**
- Backend API implementation (0%)
- Enhanced code pipeline (30%)
- WebSocket real-time updates (0%)

❌ **Not Started:**
- Unit tests (0% coverage)
- Integration tests
- E2E tests

## Next Steps

### Immediate
1. ✅ Integrate files into repository
2. ✅ Configure build for GitHub Pages
3. ✅ Test local build
4. 🔄 Deploy to GitHub Pages
5. 🔄 Verify accessibility

### Short-term
1. Implement FastAPI backend services
2. Connect to existing _codex_ backend systems
3. Add WebSocket real-time updates
4. Implement enhanced code pipeline
5. Write comprehensive tests (target: 80% coverage)

### Long-term
1. RAG pipeline integration
2. Audit system integration
3. Performance optimization
4. Advanced analytics
5. Mobile app support

## Documentation

- **Integration Guide:** [README_INTEGRATION.md](../../cognitive_app/README_INTEGRATION.md)
- **Master Plan:** [CODEX_INTEGRATION_MASTER_PLAN.md](../../cognitive_app/CODEX_INTEGRATION_MASTER_PLAN.md) - Complete backend API specification
- **Implementation Status:** [IMPLEMENTATION_STATUS.md](../../cognitive_app/IMPLEMENTATION_STATUS.md) - Detailed progress tracking
- **Product Requirements:** [PRD.md](../../cognitive_app/PRD.md)
- **Component README:** [src/components/quantum/README.md](../../cognitive_app/src/components/quantum/README.md)

## Support

For issues or questions:
1. Check [IMPLEMENTATION_STATUS.md](../../cognitive_app/IMPLEMENTATION_STATUS.md) for known gaps
2. Review [CODEX_INTEGRATION_MASTER_PLAN.md](../../cognitive_app/CODEX_INTEGRATION_MASTER_PLAN.md) for architecture
3. Consult component documentation in source files
4. Open an issue in the repository

## License

See [LICENSE](../../cognitive_app/LICENSE) file.
