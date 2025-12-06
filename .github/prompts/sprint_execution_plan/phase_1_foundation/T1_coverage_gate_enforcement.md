# T1: Coverage Gate Enforcement - Autonomous Copilot Prompt

🎯 **COPILOT INSTRUCTION: START HERE**

@workspace Execute this task using autonomous protocol:
1. READ entire prompt  
2. CHECK prerequisites (auto-generate sub-prompts if missing)
3. IMPLEMENT with inline validation  
4. TEST continuously  
5. SELF-CORRECT on failures (max 5 attempts)
6. VERIFY acceptance criteria
7. UPDATE progress section

## Metadata
```yaml
task_id: T1
priority: P0
phase: phase_1_foundation
effort: 3-5 days
dependencies: []
autonomous: ["self-validate", "self-diagnose", "self-correct", "self-expand"]
```

## Context
- **Current:** No coverage enforcement (0%)
- **Gap:** CI/Test score 0.35, needs +0.35
- **Target:** ≥70% coverage gate enforced
- **Impact:** Foundation for quality + reproducibility

## Implementation

### 1. Detect Config Strategy
```python
config = "pyproject.toml" if exists("pyproject.toml") else "pytest.ini"
```

### 2. Configure pytest
**Add to config file:**
```toml
[tool.pytest.ini_options]
addopts = [
    "--cov=src", "--cov=training",
    "--cov-report=term-missing",
    "--cov-report=html", "--cov-report=xml",
    "--cov-fail-under=70",
]
```

### 3. Create Deterministic Fixture
**File:** `tests/conftest.py`
```python
import random, numpy as np, pytest

@pytest.fixture(autouse=True)
def deterministic_seed():
    seed = 42
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch
        torch.manual_seed(seed)
        torch.use_deterministic_algorithms(True, warn_only=True)
    except: pass
    yield seed
```

### 4. Update noxfile.py
```python
@nox.session
def tests(session):
    session.install("-e", ".[dev]")
    session.run("pytest", "--cov=src", "--cov-fail-under=70")
```

## Testing
```bash
pytest --cov=src --cov-fail-under=70
nox -s tests
pytest -k test_deterministic
```

## Acceptance Criteria
- [ ] Config has `--cov-fail-under=70`
- [ ] Deterministic fixture created with autouse=True
- [ ] Nox tests session enforces coverage
- [ ] Tests run twice produce identical results
- [ ] Coverage gate fails when < 70%

## Validation Commands
```bash
grep "cov-fail-under" pytest.ini pyproject.toml
pytest --cov=src --cov-fail-under=70
nox -s tests
```

## Audit References
- `reports/_codex_task_sequences-20251206.md` lines 5-11
- `audit_artifacts/capabilities_scored.json` → ci-test: 0.35
- Expected improvement: 0.35 → 0.70

## Self-Healing Protocol
```python
for attempt in range(5):
    implement_step()
    if validate(): return SUCCESS
    diagnose_and_fix()
```

**Common fixes:**
- Missing pytest-cov → `pip install pytest-cov`
- No tests found → Check testpaths config
- Import errors → Verify PYTHONPATH

## Progress
```yaml
status: NOT_STARTED
completed_steps: []
blockers: []
```

🤖 **Copilot:** Execute autonomously with self-validation. Report blocking issues only.
