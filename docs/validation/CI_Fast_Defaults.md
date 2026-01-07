# [Validation]: CI Fast Defaults Policy

> Generated: 2024-11-06 11:59:51 | Author: mbaetiong

Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5

## Policy

| Area | Default | Rationale |
|------|---------|-----------|
| Distributed/LoRA/Perf | Disabled | No GPU; Agent-run opt-in |
| Docs Build | SKIP_OPTIONAL=1 | Avoid optional deps |
| Strict Docs | OFF on PRs | Strict only on main |
| Baselines | Manual capture | Prevent auto-commits |

## Environment Variables

| Variable | CI Default | Agent-Run | Description |
|----------|------------|-----------|-------------|
| ACCELERATE_TEST | 0 | 1 | Enable distributed tests |
| RUN_LORA_TESTS | 0 | 1 | Enable LoRA tests |
| RUN_PERF_SMOKE | 0 | 1 | Enable performance tests |
| SKIP_OPTIONAL | 1 | 0 or 1 | Skip optional dependencies |
| FAIL_ON_MISSING | 0 | 1 (main) | Fail on missing imports |

## Workflow Behavior

### Pull Requests
- Fast tests only (all gates disabled)
- Docs build with SKIP_OPTIONAL=1
- No baseline capture
- JUnit reports uploaded as artifacts

### Main Branch
- Fast tests by default
- Strict docs (FAIL_ON_MISSING=1)
- Optional baseline capture (manual trigger)

### Agent-Run (Manual)
- All gates enabled via PR checkboxes
- Heavy tests executed
- Environment probe captured
- Results uploaded as artifacts

## Rationale

**Fast CI defaults ensure**:
- Quick feedback loop (<5 min)
- No external dependencies required
- Consistent behavior across environments
- Reduced CI resource usage

**Agent-run opt-in provides**:
- GPU-dependent tests
- Heavy integration tests
- Performance benchmarks
- Full validation when needed

## Compliance

All workflows must:
- Default to fast mode
- Document opt-in mechanisms
- Provide clear skip reasons in logs
- Upload artifacts for debugging
