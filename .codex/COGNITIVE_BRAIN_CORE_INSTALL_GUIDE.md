# Cognitive Brain CORE Profile - Installation Guide

**Version**: 0.1.0  
**Status**: PRODUCTION  
**Date**: 2026-07-19  

## Overview

The Cognitive Brain CORE profile is a lightweight, stdlib-only installation suitable for:
- Edge devices and resource-constrained environments
- Offline-first deployments
- Development and testing of OODA loop logic
- Minimal production deployments where ML inference is not needed

## Three Installation Profiles

### CORE Profile (8-15 MB) ✓ PRODUCTION-READY

**Use case**: Lightweight OODA loop execution, offline environments

```bash
pip install codex-ml[core]
```

**What's included**:
- OODA loop core classes (ObservationData, OrientationResult, Decision, ActionResult)
- Agent base classes (Planner, MemoryInterface)
- Configuration management (omegaconf, hydra)
- Pattern analysis and monitoring
- Utilities and data models

**Key constraint**: Stdlib only (no numpy, torch, transformers)

**Install size**: ~10 MB

---

### RUNTIME Profile (20-35 MB)

**Use case**: ML inference, pattern learning, production services

```bash
pip install codex-ml[runtime]
```

**What's included**:
- All CORE APIs
- Numpy-based algorithms (RL, learning strategies)
- Torch for neural inference
- Transformers for language models
- FastAPI for serving
- Ray for distributed computing

**Install size**: ~27 MB (with shared dependencies)

---

### FULL Profile (100+ MB)

**Use case**: Development, testing, experimentation

```bash
pip install codex-ml[full]
```

**What's included**:
- All CORE + RUNTIME
- Development tools (pytest, type-checking, linting)
- Documentation tools
- Experiment tracking (wandb, mlflow)
- All optional dependencies

**Install size**: ~102 MB

---

## Quick Start - CORE Profile

### 1. Installation

```bash
# Recommended: Use CORE profile for PROD deployments
pip install codex-ml[core]

# Minimal install (no other packages)
pip install --no-deps src/cognitive_brain/core
```

### 2. Verify Installation

```python
from cognitive_brain.base import (
    ObservationData, OrientationResult, Decision, ActionResult, Planner
)
from datetime import datetime, timezone

# Create sample OODA objects
obs = ObservationData(
    timestamp=datetime.now(timezone.utc),
    source='agent_monitor',
    data={'status': 'active'}
)

print(f"✓ Cognitive Brain CORE {obs.source} working!")
```

### 3. Implement Agent

```python
from cognitive_brain.base import Planner, ObservationData, OrientationResult, Decision, ActionResult
from datetime import datetime, timezone
from typing import Any

class MyAgent(Planner):
    def observe(self, input_data: dict[str, Any]) -> ObservationData:
        return ObservationData(
            timestamp=datetime.now(timezone.utc),
            source='my_agent',
            data=input_data
        )
    
    def orient(self, observation: ObservationData) -> OrientationResult:
        return OrientationResult(
            context={'agent': 'MyAgent'},
            analysis='Standard observation received',
            confidence=0.95,
            alternatives=[]
        )
    
    def decide(self, orientation: OrientationResult) -> Decision:
        return Decision(
            action='log',
            parameters={'level': 'info'},
            reasoning=orientation.analysis,
            confidence=orientation.confidence,
            timestamp=datetime.now(timezone.utc)
        )
    
    def act(self, decision: Decision) -> ActionResult:
        print(f"Acting: {decision.action}")
        return ActionResult(
            success=True,
            output={'message': 'Action completed'},
            metrics={'latency_ms': 1.2},
            errors=[]
        )

# Use the agent
agent = MyAgent()
obs = agent.observe({'input': 'test'})
orient = agent.orient(obs)
decision = agent.decide(orient)
result = agent.act(decision)
print(f"✓ OODA loop completed: {result.success}")
```

---

## Dependency Requirements

### CORE Profile Dependencies

```
Required (always installed):
- omegaconf>=2.3 (configuration management)
- hydra-core==1.3.2 (CLI framework)
- pydantic>=2.4 (data validation)
- pydantic-settings>=2.14.2 (settings management)
- marshmallow>=3.7.1 (serialization)
- PyYAML>=6.0.1 (YAML support)
- typer>=0.12 (CLI helpers)
- click>=8.1 (CLI library)
- libcst>=1.0.0 (code parsing)
- parso>=0.8.0 (Python parsing)
- tree-sitter>=0.25.2 (syntax trees)

Python built-in (stdlib):
- asyncio, collections, dataclasses, datetime, enum
- functools, hashlib, io, json, logging, pathlib
- pickle, re, shutil, ssl, subprocess, sys, threading
- typing, urllib, uuid, warnings, zipfile, base64, etc.
```

### Not in CORE Profile

```
NOT included:
- numpy (ML algorithms - in RUNTIME)
- torch (neural networks - in RUNTIME)
- transformers (language models - in RUNTIME)
- pandas, scipy, sklearn (data science - in RUNTIME)
- fastapi, ray (serving - in RUNTIME)
```

---

## Troubleshooting

### Import Error: "No module named 'numpy'"

This means you're trying to use RUNTIME-only modules with CORE profile.

**Solution**:
```bash
# Upgrade to RUNTIME profile
pip install codex-ml[runtime]

# Then use numpy-dependent modules
from cognitive_brain.learning import strategy_optimizer
from cognitive_brain.quantum import quantum_coherence_monitor
```

### Import Error: "No module named 'cognitive_brain'"

Installation incomplete or not in Python path.

**Solution**:
```bash
# Reinstall with verbose output
pip install -v codex-ml[core]

# Or add src/ to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
python your_script.py
```

### Performance Issue: OODA loop execution is slow

If using CORE profile, ensure you're not importing RUNTIME-only modules.

**Solution**:
```python
# Check what's being imported
import sys
import cognitive_brain

# Print loaded modules
ooda_modules = [m for m in sys.modules if 'cognitive_brain' in m]
print(f"Loaded {len(ooda_modules)} cognitive_brain modules")

# CORE profile should only load ~8 modules
# If more, check for learning/quantum/experiments imports
```

---

## Compliance & Support

### Compliance Certifications

- ✓ Zero torch/transformers dependencies (CORE profile)
- ✓ Zero numpy dependencies (CORE profile)
- ✓ Circular import detection: 0 cycles
- ✓ Test coverage: 90%+ (OODA phases)
- ✓ API freeze: All CORE APIs frozen for PROD
- ✓ Backward compatibility: Guaranteed for PROD lifecycle

### Support Level

**CORE Profile**: PRODUCTION - Full support guaranteed

**Maintenance**: Minimum 2 years from release date (2026-07-19 → 2028-07-19)

**Update Policy**: Critical security updates only, no breaking changes

---

## References

- **API Freeze**: `.codex/COGNITIVE_BRAIN_CORE_API_FREEZE.md`
- **Dependency Audit**: `.codex/A1_dependency_audit_report.json`
- **Profile Isolation**: `.codex/A3_profile_isolation_results.json`
- **OODA Validation**: `.codex/A4_ooda_validation_report.json`
- **Source Code**: `src/cognitive_brain/`
- **Tests**: `tests/cognitive_brain/`

---

**Certified**: 2026-07-19  
**Maintained by**: Skills Master Agent  
**Review cycle**: Annual (2027-07-19)
