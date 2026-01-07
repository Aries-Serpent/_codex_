# T4: Strict Resume RNG - Autonomous Copilot Prompt

🎯 **COPILOT INSTRUCTION:** @workspace Execute with prerequisite expansion

## Metadata
```yaml
task_id: T4
priority: P1
phase: phase_2_reproducibility
effort: 1-2 days
dependencies: [T1]  # Coverage infrastructure useful for testing
```

## Context
- **Gap:** RNG state not enforced on resume (non-deterministic)
- **Target:** Add --strict-resume flag requiring RNG sidecar
- **Impact:** +12% reproducibility

## Implementation

### 1. Add CLI Flag
**File:** `cli/train_codex.py`
```python
parser.add_argument(
    "--strict-resume",
    action="store_true",
    default=False,
    help="Require RNG sidecar file when resuming training"
)
```

### 2. Implement RNG Sidecar Validation
**File:** `src/codex_ml/training/rng_checkpoint.py`
```python
import json
from pathlib import Path

class RNGCheckpoint:
    def save(self, checkpoint_dir):
        rng_state = {
            "python": random.getstate(),
            "numpy": np.random.get_state(),
            "torch": torch.get_rng_state(),
            "torch_cuda": [torch.cuda.get_rng_state(i) for i in range(torch.cuda.device_count())],
        }
        path = Path(checkpoint_dir) / ".rng.json"
        with open(path, "w") as f:
            json.dump(self._serialize(rng_state), f)
        return path
    
    def load(self, checkpoint_dir, strict=False):
        path = Path(checkpoint_dir) / ".rng.json"
        
        if not path.exists():
            if strict:
                raise FileNotFoundError(
                    f"Strict resume enabled but RNG sidecar missing: {path}\n"
                    f"Cannot guarantee deterministic resume."
                )
            else:
                print(f"⚠️ RNG sidecar not found, resume Phase 5 not be deterministic")
                return None
        
        with open(path) as f:
            rng_state = self._deserialize(json.load(f))
        
        random.setstate(rng_state["python"])
        np.random.set_state(rng_state["numpy"])
        torch.set_rng_state(rng_state["torch"])
        for i, state in enumerate(rng_state["torch_cuda"]):
            torch.cuda.set_rng_state(state, i)
        
        return rng_state
```

### 3. Integrate into Trainer
```python
def resume_training(checkpoint_path, strict_resume=False):
    # Load model/optimizer checkpoints
    load_checkpoint(checkpoint_path)
    
    # Load RNG state
    rng_checkpoint = RNGCheckpoint()
    rng_checkpoint.load(checkpoint_path, strict=strict_resume)
    
    # Continue training
    train()
```

## Testing
```python
def test_strict_resume_requires_rng():
    with pytest.raises(FileNotFoundError, match="RNG sidecar missing"):
        resume_training("checkpoint_without_rng", strict_resume=True)

def test_non_strict_resume_warns():
    with pytest.warns(UserWarning, match="not deterministic"):
        resume_training("checkpoint_without_rng", strict_resume=False)

def test_rng_sidecar_restores_state():
    # Save state
    rng_cp = RNGCheckpoint()
    rng_cp.save("test_checkpoint")
    
    # Generate random number
    value1 = np.random.rand()
    
    # Load state and generate again
    rng_cp.load("test_checkpoint")
    value2 = np.random.rand()
    
    assert value1 == value2
```

## Validation
```bash
# Should fail
python cli/train_codex.py --resume checkpoint_no_rng --strict-resume
# Expected: FileNotFoundError

# Should warn
python cli/train_codex.py --resume checkpoint_no_rng
# Expected: Warning about non-deterministic resume

# Should succeed
python cli/train_codex.py --resume checkpoint_with_rng --strict-resume
```

## Acceptance
- [ ] --strict-resume flag added to CLI
- [ ] RNG sidecar (.rng.json) saved with checkpoints
- [ ] Strict mode raises error if sidecar missing
- [ ] Non-strict mode warns but continues
- [ ] RNG state correctly restored (test validates)
- [ ] Documentation updated

## Audit Reference
- `reports/_codex_task_sequences-20251206.md` lines 29-34
- `workbench/exhaustive_audit/reproducibility_checklist.md` → RNG checkpointing

🤖 **Auto-expand:** Generate sub-prompt for checkpoint_manager.py integration if needed
