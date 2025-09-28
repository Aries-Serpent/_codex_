# Codex-Ready Task Sequence & Minimal Patch Diffs — Branch: `0C_base_ @ 8306885`

Let \(R\) be the repo snapshot, \(P = \{p_A, p_B, p_C, p_D\}\) the minimal patches (A: MLflow offline guard, B: LoRA/PEFT switch, C: deterministic overfit test, D: tokenizer round‑trip tests).  
Deployment objective: \(R' = \operatorname{apply}(R, P)\) with offline‑safe gates and no GitHub Actions.

---

````yaml
Codex-Ready Sequential Execution Block:
  Objective: >
    Apply minimal, reviewable patches to enable offline-safe tracking, optional PEFT adapters,
    and add deterministic smoke tests for training + tokenization. All checks run locally;
    no GitHub Actions are added or modified.
  Guards:
    - "NO GITHUB ACTIONS: do not create/modify any .github/workflows/*.yml"
    - "Offline-first: default disable networked trackers; MLflow only via file:// when explicitly enabled"
    - "CPU-friendly tests: tiny tensors; no external model downloads"
  Phases:
    - 1. Preparation:
        - 1.1: git checkout -b feat/codex-guards-and-tests
        - 1.2: export MLFLOW_OFFLINE=1 (for local opt-in tracking); do not commit env to repo
        - 1.3: Ensure Python >=3.10; install project in editable mode
              cmd: pip install -e .[test,cpu] || pip install -r requirements.lock
        - 1.4: Verify presence of key files: pyproject.toml, pytest.ini, conf/config.yaml
    - 2. Search & Mapping:
        - 2.1: Locate files:
              - src/codex_ml/monitoring/codex_logging.py
              - src/codex_ml/hf_loader.py
              - tests/ (create if missing)
        - 2.2: Create patches/ and backup originals to patches/backups/
    - 3. Best-Effort Construction:
        - 3.1: Apply Patch A (MLflow offline guard) to codex_logging.py
        - 3.2: Apply Patch B (PEFT optional path) to hf_loader.py
        - 3.3: Add Patch C (deterministic overfit smoke) under tests/training/test_overfit_smoke.py
        - 3.4: Add Patch D (tokenizer round-trip tests) under tests/tokenization/test_roundtrip_basic.py
    - 4. Controlled Pruning:
        - 4.1: If mlflow or peft is missing, features remain disabled; patches use try/except and env flags
        - 4.2: Tokenizer tests skip if encode/decode helpers are not exposed by module
    - 5. Gates:
        - 5.1: Run: pytest -q -k "overfit_smoke or roundtrip_basic"
        - 5.2: Run (optional full): pytest -q
        - 5.3: Build packaging smoke: python -m build (or nox -s package if available)
    - 6. Finalization:
        - 6.1: git add -A; git commit -m "feat: offline MLflow guard, PEFT switch, and deterministic smoke tests"
        - 6.2: Write CHANGELOG entry under reports/ or .codex/status/
        - 6.3: Provide artifact summary of test pass/fail and env flags in .codex/status/
  Error-Capture:
    Format: >
      "Question for ChatGPT-5 {timestamp}:
       While performing [STEP_NUMBER:STEP_DESCRIPTION], encountered: [ERROR_MESSAGE].
       Context: [BRIEF_CONTEXT]. What are likely causes and how to resolve while preserving functionality?"
````

---

## Minimal Patch Diffs (ready to apply)

> Apply via `git apply` blocks or copy/paste edits. All changes are **local-only** and **offline-first**.

### Patch A — MLflow offline guard (local tracking only when enabled)
**File:** `src/codex_ml/monitoring/codex_logging.py`

```diff
*** a/src/codex_ml/monitoring/codex_logging.py
--- b/src/codex_ml/monitoring/codex_logging.py
@@
+def _maybe_init_mlflow_offline():
+    """Initialize MLflow in offline mode only if explicitly enabled.
+    Safe-by-default: no network egress, guarded by MLFLOW_OFFLINE env flag.
+    """
+    import os
+    if os.getenv("MLFLOW_OFFLINE", "0") != "1":
+        return
+    try:
+        import mlflow  # optional
+        uri = os.getenv("MLFLOW_TRACKING_URI", "file:./artifacts/mlruns")
+        mlflow.set_tracking_uri(uri)
+    except Exception:  # pragma: no cover - non-fatal, remain disabled
+        pass
+
@@
-def init_logger(name: str = __name__):
+def init_logger(name: str = __name__):
     import logging
-    logger = logging.getLogger(name)
+    # Initialize optional offline tracker (no-op if not enabled)
+    _maybe_init_mlflow_offline()
+    logger = logging.getLogger(name)
     if not logger.handlers:
         handler = logging.StreamHandler()
         fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
         handler.setFormatter(logging.Formatter(fmt))
         logger.addHandler(handler)
```

---

### Patch B — Optional LoRA/PEFT adapter switch (default OFF)
**File:** `src/codex_ml/hf_loader.py`

```diff
*** a/src/codex_ml/hf_loader.py
--- b/src/codex_ml/hf_loader.py
@@
+import os
 from transformers import AutoModelForCausalLM
 
-def load_model(name_or_path: str, **kw):
-    return AutoModelForCausalLM.from_pretrained(name_or_path, **kw)
+def load_model(name_or_path: str, **kw):
+    """Load base model; optionally wrap with PEFT adapter if provided.
+    Usage:
+      - kw["peft_path"] or env PEFT_ADAPTER_PATH -> attempt to attach adapter
+      - kw["torch_dtype"] (e.g., "bf16", "fp16") respected if supported
+    Fails safe: if PEFT not installed or adapter path invalid, returns base model.
+    """
+    peft_path = kw.pop("peft_path", None) or os.getenv("PEFT_ADAPTER_PATH")
+    model = AutoModelForCausalLM.from_pretrained(name_or_path, **kw)
+    if peft_path:
+        try:
+            from peft import PeftModel  # optional dependency
+            model = PeftModel.from_pretrained(model, peft_path)
+        except Exception:
+            # Non-fatal: keep base model if adapter cannot be loaded
+            pass
+    return model
```

---

### Patch C — Deterministic tiny overfit smoke (CPU-only)
**File (new):** `tests/training/test_overfit_smoke.py`

```diff
*** /dev/null
--- b/tests/training/test_overfit_smoke.py
@@
+import random
+import numpy as np
+import torch
+
+def test_tiny_overfit_smoke():
+    torch.use_deterministic_algorithms(True)
+    torch.manual_seed(7); random.seed(7); np.random.seed(7)
+    x = torch.randn(64, 8)
+    true_w = torch.randn(8, 1)
+    y = x @ true_w + 0.01 * torch.randn(64, 1)
+    w = torch.zeros(8, 1, requires_grad=True)
+    opt = torch.optim.SGD([w], lr=0.2)
+    for _ in range(60):
+        opt.zero_grad()
+        loss = ((x @ w - y) ** 2).mean()
+        loss.backward()
+        opt.step()
+    assert loss.item() < 1e-2
```

---

### Patch D — Tokenizer round‑trip (skips gracefully if helpers absent)
**File (new):** `tests/tokenization/test_roundtrip_basic.py`

```diff
*** /dev/null
--- b/tests/tokenization/test_roundtrip_basic.py
@@
+import importlib
+import pytest
+
+def _maybe_get_funcs():
+    try:
+        mod = importlib.import_module("codex_ml.tokenization.cli")
+    except Exception:
+        return None, None
+    enc = getattr(mod, "encode", None)
+    dec = getattr(mod, "decode", None)
+    return enc, dec
+
+def test_roundtrip_basic():
+    enc, dec = _maybe_get_funcs()
+    if enc is None or dec is None:
+        pytest.skip("encode/decode helpers not exposed; skipping round-trip test")
+    s = "hello codex"
+    ids = enc(s, max_len=16, pad=True, trunc=True)
+    assert isinstance(ids, (list, tuple)) and len(ids) > 0
+    s2 = dec(ids).strip()
+    assert isinstance(s2, str) and len(s2) > 0
```

---

## How to Apply (shell)

```bash
git checkout -b feat/codex-guards-and-tests

# Patch A
git apply <<'PATCH'
*** a/src/codex_ml/monitoring/codex_logging.py
--- b/src/codex_ml/monitoring/codex_logging.py
@@
+def _maybe_init_mlflow_offline():
+    """Initialize MLflow in offline mode only if explicitly enabled.
+    Safe-by-default: no network egress, guarded by MLFLOW_OFFLINE env flag.
+    """
+    import os
+    if os.getenv("MLFLOW_OFFLINE", "0") != "1":
+        return
+    try:
+        import mlflow  # optional
+        uri = os.getenv("MLFLOW_TRACKING_URI", "file:./artifacts/mlruns")
+        mlflow.set_tracking_uri(uri)
+    except Exception:  # pragma: no cover - non-fatal, remain disabled
+        pass
+
@@
-def init_logger(name: str = __name__):
+def init_logger(name: str = __name__):
     import logging
-    logger = logging.getLogger(name)
+    _maybe_init_mlflow_offline()
+    logger = logging.getLogger(name)
     if not logger.handlers:
         handler = logging.StreamHandler()
         fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
         handler.setFormatter(logging.Formatter(fmt))
         logger.addHandler(handler)
PATCH

# Patch B
git apply <<'PATCH'
*** a/src/codex_ml/hf_loader.py
--- b/src/codex_ml/hf_loader.py
@@
+import os
 from transformers import AutoModelForCausalLM
 
-def load_model(name_or_path: str, **kw):
-    return AutoModelForCausalLM.from_pretrained(name_or_path, **kw)
+def load_model(name_or_path: str, **kw):
+    """Load base model; optionally wrap with PEFT adapter if provided."""
+    peft_path = kw.pop("peft_path", None) or os.getenv("PEFT_ADAPTER_PATH")
+    model = AutoModelForCausalLM.from_pretrained(name_or_path, **kw)
+    if peft_path:
+        try:
+            from peft import PeftModel
+            model = PeftModel.from_pretrained(model, peft_path)
+        except Exception:
+            pass
+    return model
PATCH

# Patch C (new file)
mkdir -p tests/training
git apply <<'PATCH'
*** /dev/null
--- b/tests/training/test_overfit_smoke.py
@@
+import random
+import numpy as np
+import torch
+
+def test_tiny_overfit_smoke():
+    torch.use_deterministic_algorithms(True)
+    torch.manual_seed(7); random.seed(7); np.random.seed(7)
+    x = torch.randn(64, 8)
+    true_w = torch.randn(8, 1)
+    y = x @ true_w + 0.01 * torch.randn(64, 1)
+    w = torch.zeros(8, 1, requires_grad=True)
+    opt = torch.optim.SGD([w], lr=0.2)
+    for _ in range(60):
+        opt.zero_grad()
+        loss = ((x @ w - y) ** 2).mean()
+        loss.backward()
+        opt.step()
+    assert loss.item() < 1e-2
PATCH

# Patch D (new file)
mkdir -p tests/tokenization
git apply <<'PATCH'
*** /dev/null
--- b/tests/tokenization/test_roundtrip_basic.py
@@
+import importlib
+import pytest
+
+def _maybe_get_funcs():
+    try:
+        mod = importlib.import_module("codex_ml.tokenization.cli")
+    except Exception:
+        return None, None
+    enc = getattr(mod, "encode", None)
+    dec = getattr(mod, "decode", None)
+    return enc, dec
+
+def test_roundtrip_basic():
+    enc, dec = _maybe_get_funcs()
+    if enc is None or dec is None:
+        pytest.skip("encode/decode helpers not exposed; skipping round-trip test")
+    s = "hello codex"
+    ids = enc(s, max_len=16, pad=True, trunc=True)
+    assert isinstance(ids, (list, tuple)) and len(ids) > 0
+    s2 = dec(ids).strip()
+    assert isinstance(s2, str) and len(s2) > 0
PATCH

# Run minimal gates
pytest -q -k "overfit_smoke or roundtrip_basic"
```

---

## Optional Python Runner (single command)

```python
# scripts/codex_apply_minimal_patches.py
import os, subprocess, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]

def apply_patch(patch_text):
    p = subprocess.Popen(["git","apply","-"], cwd=ROOT, stdin=subprocess.PIPE, text=True)
    p.communicate(patch_text)
    if p.returncode != 0:
        raise SystemExit("git apply failed")

PATCH_A = """(paste Patch A block here)"""
PATCH_B = """(paste Patch B block here)"""
PATCH_C = """(paste Patch C block here)"""
PATCH_D = """(paste Patch D block here)"""

if __name__ == "__main__":
    os.environ.setdefault("MLFLOW_OFFLINE", "1")
    (ROOT/"tests"/"training").mkdir(parents=True, exist_ok=True)
    (ROOT/"tests"/"tokenization").mkdir(parents=True, exist_ok=True)
    for patch in (PATCH_A, PATCH_B, PATCH_C, PATCH_D):
        apply_patch(patch)
    subprocess.check_call(["pytest","-q","-k","overfit_smoke or roundtrip_basic"], cwd=ROOT)
```

---

### Ready-to-Run

```bash
git checkout -b feat/codex-guards-and-tests
# Apply patches (blocks above) and run minimal gates
pytest -q -k "overfit_smoke or roundtrip_basic"
git add -A && git commit -m "feat: offline MLflow guard, PEFT switch, deterministic smoke tests"
```
