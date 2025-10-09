# [Prompt]: 0A_base_ Integration Validation — Code, Tests, Docs  
> Generated: 2025-10-09 20:32:46 UTC | Author: mbaetiong  
Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5

System
- You are Codex validating the integration of newly added files on branch 0A_base_ in Aries-Serpent/_codex_.
- Operate offline by default. Only run online steps if explicitly flagged.

Preconditions
- Git branch: 0A_base_
- Python: 3.10+ recommended
- Ensure a clean virtualenv

Environment (offline defaults)
```bash
export CODEX_NET_MODE=offline
unset MLFLOW_TRACKING_URI
unset WANDB_MODE
```

Step 1 — Install optional dev deps (non-fatal if skipped)
```bash
pip install -q jsonschema z3-solver pyjwt
```
Note: Tests will skip gracefully if these are absent.

Step 2 — Fast test subset (CPU-only, offline)
```bash
pytest -q \
  tests/training/test_checkpoint_integrity.py::test_roundtrip_and_integrity \
  tests/training/test_checkpoint_integrity.py::test_best_k_retention \
  tests/training/test_checkpoint_rng_restore.py \
  tests/tracking/test_tracking_guards.py \
  tests/data/test_shard_integrity.py \
  tests/tokenization/test_deprecation.py \
  tests/specs/test_cli_normalization.py \
  tests/specs/test_regex_props.py
```

Step 3 — Optional spec tests (if deps present)
```bash
# JSON Schema validation
pytest -q tests/specs/test_metrics_schema.py -q || true
# SMT policy (requires z3)
pytest -q tests/specs/test_smt_policy.py -q || true
```

Step 4 — Validate CODEOWNERS (offline tool)
```bash
python -c "from src.tools.codeowners_validate import validate_repo_codeowners; \
rep=validate_repo_codeowners('.'); \
import json; print(json.dumps({k:getattr(rep,k) for k in ('exists','default_rule','owners_ok','coverage','errors','warnings')}, indent=2))"
```
Expected: exists:true (if you adopt the template), owners_ok:true, default_rule:true, coverage flags mostly true.

Step 5 — Offline tracking guards behavior
```bash
python - <<'PY'
import os, tempfile
from pathlib import Path
from src.codex_utils.tracking.guards import ensure_mlflow_offline, ensure_wandb_offline
with tempfile.TemporaryDirectory() as d:
    os.environ.pop("MLFLOW_TRACKING_URI", None)
    os.environ["CODEX_ALLOWLIST_HOSTS"] = ""
    uri = ensure_mlflow_offline(Path(d))
    mode = ensure_wandb_offline()
    print("MLFLOW_TRACKING_URI:", uri)
    print("WANDB_MODE:", mode)
PY
```
Expected: MLFLOW_TRACKING_URI starts with file://; WANDB_MODE == offline.

Step 6 — Documentation spot check (local)
- Open docs/index.md and confirm links resolve to:
  - docs/how-to/offline_tracking.md
  - docs/how-to/checkpoint_metadata.md
  - docs/how-to/dataset_manifest.md
  - docs/how-to/codeowners_validation.md
  - docs/ops/repo_rulesets_vs_protection.md
- No external calls required.

Step 7 — Optional online (explicit opt-in)
Only if you intend to test runner bootstrap:
```bash
export CODEX_NET_MODE=online_allowlist
export CODEX_ALLOWLIST_HOSTS=api.github.com
export GITHUB_APP_ID=<id>
export GITHUB_APP_INSTALLATION_ID=<inst_id>
export GITHUB_APP_PRIVATE_KEY_PATH=/secure/github-app.pem
python -m scripts.ops.bootstrap_self_hosted_runner --owner <org> --repo <name> --dry-run
```
Expected: prints plan and config commands; no token persisted.

Step 8 — Determinism smoke (rerun)
Run the fast subset twice and confirm identical pass results. For checkpoint tests, ensure top-k pruning is stable (3 files remain).

Troubleshooting
- If any test fails:
  - For checksum mismatches: re-run from a clean tmp dir.
  - For DeprecationWarning test: ensure warnings filter is set to always in test; skip adapters if missing.
  - For tracking guards: confirm env allowlist is empty to force file:// coercion.

Exit Criteria (Success)
- All Step 2 tests pass.
- Optional Step 3 tests pass or are skipped.
- CODEOWNERS report indicates exists:true (if adopted) and owners_ok:true.
- Offline guard outputs match expectations.
- Docs links render locally.

Appendix — Quick All-in-One
```bash
pytest -q tests/training/test_checkpoint_integrity.py tests/training/test_checkpoint_rng_restore.py \
           tests/tracking/test_tracking_guards.py tests/data/test_shard_integrity.py \
           tests/tokenization/test_deprecation.py tests/specs/test_cli_normalization.py tests/specs/test_regex_props.py \
           tests/specs/test_metrics_schema.py tests/specs/test_smt_policy.py || true
```

*End of Prompt*