# Cognitive Codex App - Integration Documentation

## Overview

This directory contains the Cognitive Codex Application, a React/Vite-based web interface for the `_codex_` quantum-enhanced code generation platform.

## Integration Status

✅ **Completed:**
- Unzipped and extracted all files from `cognitive_codex_app.zip`
- Organized into `/cognitive_app` directory
- Configured Vite build for GitHub Pages deployment
- Created GitHub Actions workflow for automated deployment
- All 125 files successfully integrated

## Directory Structure

```
cognitive_app/
├── .github/              # GitHub configuration
├── src/                  # Source code
│   ├── components/       # React components
│   │   ├── code/        # Code generation components (3)
│   │   ├── quantum/     # Quantum/cognitive components (27)
│   │   └── ui/          # UI component library (44)
│   ├── hooks/           # Custom React hooks (5)
│   ├── lib/             # Utility libraries (4)
│   └── styles/          # Theme and styling
├── CODEX_INTEGRATION_MASTER_PLAN.md
├── IMPLEMENTATION_STATUS.md
├── PRD.md
├── package.json
├── vite.config.ts
└── tsconfig.json
```

## Component Categories

### Quantum Components (27 files)
- QuantumDecisionEngine - Real-time cognitive brain metrics
- AgentOrchestrationPanel - 6 physics paradigms, tokenized workflows
- MemoryManagementDashboard - STM/LTM with 60% compression
- WorkflowTokenOrchestrator - Custom workflow execution
- DependencyGraphVisualizer - DAG visualization
- CascadingExecutionMonitor - Cascade tracking
- And 21 more specialized components

### UI Components (44 files)
Complete shadcn/ui library including:
- accordion, alert-dialog, avatar, badge, button
- card, calendar, carousel, chart, checkbox
- dialog, dropdown-menu, form, input, label
- tabs, table, tooltip, and many more

### Code Components (3 files)
- CodeGenerator - Natural language code generation
- CodeEditor - Monaco-based editor
- MetricsBar - Real-time metrics display

## Deployment

### GitHub Pages Access
Once deployed, the application will be accessible at:
```
https://aries-serpent.github.io/_codex_/cognitive_app/
```

### Build Commands
```bash
cd cognitive_app
npm install        # Install dependencies
npm run dev       # Development server
npm run build     # Production build
npm run preview   # Preview production build
```

## Backend Integration

The application is designed to connect to a FastAPI backend. According to the master plan:

### Required Backend Services
1. **Cognitive Brain API** - Quantum decision engine
2. **Agents API** - Agent orchestration and physics paradigms
3. **Memory API** - STM/LTM management
4. **Code Analysis API** - AST-based code analysis
5. **Metrics API** - Real-time metrics aggregation
6. **WebSocket Manager** - Real-time updates

### Backend Setup Location
Backend services should be implemented in:
```
services/api/
├── main.py                # FastAPI app
├── cognitive_api.py       # Cognitive brain endpoints
├── agents_api.py          # Agent orchestration
├── memory_api.py          # Memory management
├── code_api.py            # Code analysis
├── metrics_api.py         # Metrics aggregation
└── websocket_manager.py   # Real-time WebSocket
```

## Current Implementation Status

**Frontend:** 95% Complete ✅
- All UI components implemented
- Mock API client for development
- Ready for backend integration

**Backend:** 0% Complete ⚠️
- FastAPI services not yet implemented
- WebSocket manager pending
- Database integration pending

## Testing the Application

### Local Development
```bash
cd cognitive_app
npm install
npm run dev
```
Access at: http://localhost:5173

### Production Build
```bash
npm run build
npm run preview
```

## Features Implemented

### ✅ Quantum Decision Engine
- k₁ factor tracking (target: ≤0.35)
- Quantum advantage: 2.86×
- Coherence visualization
- Superposition state evaluation
- Wave function collapse animation

### ✅ Agent Orchestration
- 6 physics paradigms (chaos, fractal, fluid, EM, wave, relativity)
- Pre-built workflow tokens (AUDIT_EXEC, DOC_GEN, HEAL, etc.)
- Custom workflow token creation
- Dependency-based auto-execution
- Cascading execution monitoring

### ✅ Memory Management
- STM/LTM visualization
- 60% compression rate
- Cache hit rate: 32%
- Pattern library
- Memory search and filtering

### ✅ Metrics Dashboard
- Real-time quantum brain metrics
- Agent system status
- Memory system health
- Auto-refresh every 10 seconds

## Next Steps

### Immediate (for full functionality)
1. Install Node.js dependencies: `cd cognitive_app && npm install`
2. Test local development server: `npm run dev`
3. Build for production: `npm run build`
4. Deploy via GitHub Actions (automatic on push to main)

### Backend Integration (future)
1. Implement FastAPI services in `services/api/`
2. Connect to existing _codex_ backend systems
3. Add WebSocket real-time updates
4. Configure API endpoints in environment variables

### Testing & Validation
1. Verify all components render correctly
2. Test workflow orchestration
3. Validate metrics display
4. Test responsive design
5. Verify GitHub Pages deployment

## Dependencies

Key dependencies from package.json:
- React 19.0.0
- Vite 7.2.6
- TypeScript 5.7.2
- @github/spark >=0.43.1
- Tailwind CSS 4.1.11
- Radix UI components
- Phosphor Icons
- D3.js for visualizations
- Recharts for metrics

## Configuration Files

- **vite.config.ts** - Vite build configuration with GitHub Pages base path
- **tsconfig.json** - TypeScript compiler configuration
- **tailwind.config.js** - Tailwind CSS configuration
- **components.json** - shadcn/ui configuration
- **package.json** - npm dependencies and scripts

## Documentation Files

- **CODEX_INTEGRATION_MASTER_PLAN.md** - Complete integration strategy
- **IMPLEMENTATION_STATUS.md** - Implementation progress (95% complete)
- **PRD.md** - Product requirements document
- **README.md** - Original Spark template README

## Security

- **SECURITY.md** - Security policies
- All dependencies regularly updated
- No secrets in source code
- CORS configured for production

## Support

For issues or questions about the cognitive app:
1. Check IMPLEMENTATION_STATUS.md for known gaps
2. Review CODEX_INTEGRATION_MASTER_PLAN.md for architecture
3. Consult component README in src/components/quantum/README.md

## License

See LICENSE file in this directory.
