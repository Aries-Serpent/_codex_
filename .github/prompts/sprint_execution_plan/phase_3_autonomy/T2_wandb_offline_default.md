# T2: W&B Offline Default - Autonomous Copilot Prompt

🎯 **COPILOT INSTRUCTION:** @workspace Execute autonomously

## Metadata
```yaml
task_id: T2
priority: P1
phase: phase_3_autonomy
effort: 0.5-1 day
dependencies: []
```

## Context
- **Gap:** W&B defaults to online mode (network risk)
- **Target:** Default WANDB_MODE=offline in sitecustomize.py
- **Impact:** +8% autonomy, offline safety enforced

## Implementation

### 1. Create/Update sitecustomize.py
**File:** `sitecustomize.py` (in site-packages or project root)
```python
"""Site customization for offline ML workflows."""
import os

# Default W&B to offline mode unless explicitly overridden
if "WANDB_MODE" not in os.environ:
    os.environ["WANDB_MODE"] = "offline"
    print("ℹ️ W&B defaulted to offline mode (set WANDB_MODE=online to override)")
```

### 2. Verify in logging_utils
**File:** `src/logging_utils.py` or relevant logging module
```python
import os
import wandb

def init_wandb(**kwargs):
    mode = os.getenv("WANDB_MODE", "offline")
    wandb.init(mode=mode, **kwargs)
```

### 3. Add fallback writer
```python
class LogWriter:
    def __init__(self):
        self.wandb_available = self._check_wandb()
        
    def _check_wandb(self):
        try:
            import wandb
            return os.getenv("WANDB_MODE") != "disabled"
        except:
            return False
    
    def log(self, metrics):
        if self.wandb_available:
            wandb.log(metrics)
        else:
            # Fallback to NDJSON
            self._write_ndjson(metrics)
```

## Testing
```python
def test_wandb_offline_default():
    import os
    import sitecustomize  # Triggers env var setting
    assert os.getenv("WANDB_MODE") == "offline"

def test_wandb_fallback():
    os.environ["WANDB_MODE"] = "disabled"
    writer = LogWriter()
    assert not writer.wandb_available
```

## Validation
```bash
python -c "import sitecustomize; import os; print(os.getenv('WANDB_MODE'))"
# Expected: offline

python -c "import wandb; wandb.init(project='test')"
# Should not attempt network connection
```

## Acceptance
- [ ] sitecustomize.py sets WANDB_MODE=offline by default
- [ ] Can override with explicit WANDB_MODE=online
- [ ] Fallback writer handles disabled mode
- [ ] Documentation updated

## Audit Reference
- `reports/_codex_task_sequences-20251206.md` lines 13-19

🤖 **Auto-execute:** Self-validate with test suite
