# T3: EarlyStopping Integration - Autonomous Copilot Prompt

🎯 **COPILOT INSTRUCTION:** @workspace Execute with self-healing

## Metadata
```yaml
task_id: T3
priority: P1
phase: phase_3_autonomy
effort: 1-2 days
dependencies: []
```

## Context
- **Gap:** No early stopping in HF trainer
- **Target:** Auto-inject EarlyStoppingCallback when eval dataset present
- **Impact:** Prevents overfitting, saves compute

## Implementation

### 1. Modify HF Trainer Init
**File:** `training/engine_hf_trainer.py` or `src/codex_ml/training/hf_trainer_wrapper.py`

```python
from transformers import EarlyStoppingCallback

class CodexTrainer:
    def __init__(self, model, args, train_dataset, eval_dataset=None, **kwargs):
        callbacks = kwargs.get('callbacks', [])
        
        # Auto-inject EarlyStopping if eval dataset provided
        if eval_dataset is not None:
            has_early_stopping = any(
                isinstance(cb, EarlyStoppingCallback) for cb in callbacks
            )
            if not has_early_stopping:
                early_stop_cb = EarlyStoppingCallback(
                    early_stopping_patience=3,
                    early_stopping_threshold=0.0
                )
                callbacks.append(early_stop_cb)
                print("✓ EarlyStoppingCallback auto-injected (patience=3)")
        
        kwargs['callbacks'] = callbacks
        self.trainer = Trainer(model, args, train_dataset, eval_dataset, **kwargs)
```

### 2. Add Configuration
```python
@dataclass
class TrainingConfig:
    early_stopping_patience: int = 3
    early_stopping_threshold: float = 0.0
    early_stopping_metric: str = "eval_loss"
```

### 3. Testing
```python
def test_early_stopping_injection():
    trainer = CodexTrainer(model, args, train_ds, eval_ds)
    callbacks = trainer.trainer.callback_handler.callbacks
    assert any(isinstance(cb, EarlyStoppingCallback) for cb in callbacks)

def test_early_stopping_triggers():
    # Mock training with plateau
    trainer = CodexTrainer(...)
    # Simulate 3 epochs without improvement
    # Verify training stops early
```

## Validation
```bash
python -c "
from training.engine_hf_trainer import CodexTrainer
# Should log callback injection
"

grep -r "EarlyStoppingCallback" training/
```

## Acceptance
- [ ] EarlyStopping auto-injected when eval dataset present
- [ ] No duplicate callbacks
- [ ] Logs callback creation
- [ ] Configuration allows patience override
- [ ] Tests verify early stop triggers

## Audit Reference
- `reports/_codex_task_sequences-20251206.md` lines 21-27
- `reports/_capability_completeness_gapmap-20251206.md` → training-engine

🤖 **Self-heal:** Retry with alternate callback injection strategy if initial approach fails
