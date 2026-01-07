# Dependency Disk Pressure & Archival-Aligned Utilization Triage  
> Generated: 2024-11-12 16:24:19 UTC | Author: mbaetiong  
Ref: f40ff2bbcacf567eef3dc6bd8c95733859b927dc

## 0. Archival & Retention Alignment (New Section)

This revision incorporates the repository’s archival policy, tombstone governance, purge request workflow, and retention utilities to ensure dependency pruning never bypasses evidence or policy gates.

| Aspect | Source (example) | Alignment in this doc |
|--------|------------------|------------------------|
| Tombstone-first archival | docs/guides/codex_archive_runbook.md | Dependencies classified for archival create ADR + optional tombstone note in CHANGELOG before removal |
| Dual-control purge approvals | src/codex/archive/cli.py (prune-request, purge) | Heavy dependency hard removals require two approvers if purging shared artifact states |
| Evidence logging (JSONL) | .codex/evidence/archive_ops.jsonl | Large dependency removal batches recorded with summary line (planned automation hook) |
| Log/session retention (30 days) | docs/logging/log_rotation.md; tools/purge_session_logs.py | Purge scripts for vendor wheels keep separate evidence before uninstall snapshot |
| Checkpoint retention | src/codex_ml/utils/retention.py; src/codex_ml/checkpointing/best_k_retention.py | Mirrors rationale for dependency retention (keep last N heavy ML libs only where needed) |
| ADR requirement for removal | docs/arch/adr-template.md | High-impact stack (torch, ray, mlflow, jupyter) removal triggers ADR referencing planner score |
| Deprecated shims | tokenization/api.py; docs/guides/tokenization.md | For dependency-driven module changes, create Python shim + markdown pointer if path relocated |
| Archive planner scoring | src/codex/archive/plan.py | Conceptual adaptation to a “dependency plan” (age/usage analogs) |

---

## 1. Scope & Source
The failing CI job (`pip install -r requirements-dev.txt`) aborted with `[Errno 28] No space left on device`.  
Direct spec: `requirements-dev.txt` remains intentionally minimal (pytest/mypy/ruff/black + security tooling). Disk pressure arises from transitive, session-based, or unsegmented installs of heavyweight runtime and GPU stacks (torch + nvidia-* + notebook/visualization + scientific + distributed + evaluation metrics) not required for baseline unit coverage of `src/codex_ml`.

Archival-conscious adjustment: treat removal or segmentation of large dependency families as “hygiene archival” operations—document, evidence log, and (where code paths change) retain tombstone shims or ADR references.

---

## 2. Ranking Criteria (Extended with Archival Governance)

| Feasibility | Definition | Action | Archival / Evidence Hook |
|-------------|------------|--------|---------------------------|
| Keep | Core tests require; lean size | Remain in dev set | No archival action |
| Optional | Feature-flag / importorskip / shim fallback | Move to segmented requirements file | If removed from base spec: note in CHANGELOG |
| Defer | Only used in specialized workflows (evaluation, notebooks, distributed) | Install in dedicated nox session | Planner entry + ADR if broad removal |
| Purge | GPU vendor wheels in CPU posture or clearly wasteful | Block or uninstall + evidence log snapshot | Evidence line + optional `archive prune-request` if code stubs impacted |
| Consolidate | Overlapping libs where minimal subset suffices | Replace with slimmer stack | Markdown pointer or Python shim for deprecated sub-module paths |

---

## 3. High-Impact Space Consumers (Approximate Wheel Sizes)

| Package Family | Approx Size (MB) | Feasibility | Rationale | Archival Step |
|----------------|------------------|-------------|-----------|---------------|
| torch (CPU) | 180–220 | Optional/Defer | Only needed for training/checkpoint tests | ADR if removing or relocating training surfaces |
| triton | 60–80 | Purge (CPU CI) | GPU compiler not required for CPU-only CI | Vendor purge evidence |
| nvidia-* aggregate | 900–1200+ | Purge | CUDA slices unused; disk exhaustion risk | Automated purge + log snapshot |
| scipy + numpy + scikit-learn | 150–250 | Optional/Defer | Advanced metrics only | Segmented eval requirements |
| pandas | 40–60 | Optional/Defer | Data frame convenience | Defer; note if baseline removal |
| statsmodels | 30–40 | Optional/Defer | Evidently/analytics only | Defer |
| mlflow (+ skinny/tracing) | 40–60 | Optional | Opt-in local tracking | Feature flag + ADR if disabling entirely |
| jupyterlab stack | 180–250 | Defer | Not needed headless CI | Segmented notebook requirements |
| matplotlib | 30–40 | Optional/Defer | Visualization only | Defer |
| ray | 80–120 | Optional/Defer | Distributed evaluation only | Score & ADR if removal |
| transformers | 50–80 (CPU) | Optional | Tokenization/model tests | Minimized `--no-deps` install |
| sentencepiece | 5–7 | Optional | Adapter shim present; tests skip gracefully | Keep optional |
| peft + accelerate | 25–40 | Optional | LoRA fine-tuning | Dedicated ML session |
| lm-eval, rouge-score, sacrebleu, nltk | 30–45 | Optional | Text metrics evaluation | Segmented eval file |

---

## 4. Dependency Utilization & Archival Table

| Dependency | Category | Feasibility | Code Presence (examples) | Flag / Guard | Est Size MB | Recommendation | Archival/Evidence Path |
|------------|----------|-------------|---------------------------|--------------|-------------|----------------|------------------------|
| pytest / pytest-cov | Dev/Test | Keep | configs/development/pytest.ini | N/A | <5 | Retain | — |
| ruff / black / mypy / isort | Dev/QC | Keep | Pre-commit config | N/A | <10 | Retain | — |
| pip-audit / bandit / detect-secrets | Security | Keep | Security docs & hooks | N/A | <15 | Retain | — |
| jsonschema / types-jsonschema | Config | Keep | Validation tooling | N/A | <10 | Retain | — |
| pydantic / hydra-core / omegaconf | Runtime config | Keep | Training config store | N/A | 10–20 | Retain | — |
| requests / defusedxml | Core util | Keep | HTTP, safe XML | N/A | <5 | Retain | — |
| psutil | Monitoring | Keep | System metrics sampler | N/A | 3–5 | Retain | — |
| sentencepiece | Tokenization | Optional | Shim stub path | Importorskip | ~6 | Move to ML/eval segment | CHANGELOG note if removed |
| transformers | ML stack | Optional | Tokenizer + model surfaces | Feature/flag tests | ~60 | Slim via `--no-deps` | Evidence summary if removed |
| accelerate | Training util | Optional | LoRA/trainer integration | Env flag | 15–20 | Defer | Add to segmented ML file |
| peft | LoRA | Optional | LoRA config tests | CODEX_ENABLE_PEFT | 10–15 | Defer | Segmented ML spec |
| torch (CPU) | Core ML | Optional/Defer | Checkpoint & training | Test markers | ~200 | ML-only session | ADR if removal; stub shim retained |
| triton | GPU compiler | Purge | Not used CPU | Vendor purge | ~70 | Purge in CPU CI | Evidence log line |
| nvidia-* family | GPU vendor | Purge | Not referenced in code (only audit tools) | Purge logic | 1000+ | Block & purge | Evidence + purge-request record |
| scikit-learn / scipy / statsmodels | Scientific | Optional/Defer | Metrics/evaluation | Eval session | 150–200 | Segmented eval | Planner entry if removal from base |
| pandas | Data | Optional/Defer | Utilities/tests | Eval/data session | ~50 | Defer | CHANGELOG note |
| jupyterlab / notebook / nbconvert / nbformat | Notebook | Defer | Interactive only | Notebook session | ~200 | Remove from default CI | ADR if removal large-scale |
| matplotlib | Viz | Optional | Minor docs/tests | Notebook/eval | ~35 | Defer | Optional segment |
| lm-eval / metrics libs | Eval metrics | Optional | Evaluation commands | Eval session | 30–45 | Segmented install | Evidence if purged |
| ray | Distributed | Optional/Defer | Possibly evaluation harness | Flag | ~100 | Defer to distributed session | ADR if removal |
| mlflow (+ tracing) | Tracking | Optional | mlflow_run context | CODEX_ENABLE_MLFLOW | ~50 | Defer | ADR + CHANGELOG if removed |
| fastapi / starlette | API | Optional | Service endpoints | Markers | 25–35 | Keep minimal subset | Document partial consolidation |
| safetensors / tokenizers | Model I/O | Optional (lean) | Checkpoint & tokenizer | With transformers | 10–15 | Keep minimal | — |
| uvicorn | Serve | Optional | API dev server | Integration tests | ~5 | Defer | — |

> Disk savings estimate if all Optional/Defer/Purge entries are removed from default dev test context: ~2.2–2.5 GB.

---

## 5. Recommended Separation of Requirements

### a) Keep `requirements-dev.txt` Lean
Do not add heavy ML dependencies here.

### b) `requirements-ml-cpu.txt` (Install only in targeted nox session)
```text
torch==2.8.0 --index-url https://download.pytorch.org/whl/cpu
transformers==4.56.0
tokenizers==0.22.0
safetensors==0.6.2
accelerate==0.29.0
peft==0.17.1
sentencepiece==0.2.1
```text

### c) `requirements-eval.txt`
```text
scikit-learn==1.7.2
scipy==1.16.2
statsmodels==0.14.5
pandas==2.3.2
lm-eval==0.4.9.1
rouge-score==0.1.2
sacrebleu==2.5.1
nltk==3.9.2
```text

### d) `requirements-notebook.txt`
```text
jupyterlab==4.4.9
notebook==7.4.7
nbconvert==7.16.6
matplotlib==3.10.6
```text

### e) Blocking GPU Vendor Wheels (Guard)
```bash
python - <<'PY'
import sys, pkgutil, json, time, os
allow_triton=os.getenv("CODEX_ALLOW_TRITON_CPU","1")=="1"
vendors=[m.name for m in pkgutil.iter_modules() if (m.name.startswith("nvidia-") or m.name in {"triton","torchtriton"})]
if allow_triton:
    vendors=[v for v in vendors if v!="triton"]
record={
  "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
  "action": "DEPENDENCY_VENDOR_SCAN",
  "vendors": vendors,
  "cpu_only": True
}
if vendors:
    print(json.dumps(record), file=sys.stderr)
    sys.exit(1)
print(json.dumps(record))
PY
```text

---

## 6. CI Adjustments

| Step | Adjustment | Outcome |
|------|------------|---------|
| Pre-install cleanup | Remove dotnet, android SDK, GH components | Frees 4–6 GB |
| Split sessions | `nox -s tests` (no ML) then `nox -s ml_tests` (installs `requirements-ml-cpu.txt`), `nox -s eval_tests` | Avoid heavy deps for baseline job |
| CPU enforcement | `CODEX_FORCE_CPU=1` + CPU index before torch | Blocks CUDA vendor wheels |
| Minimal augmentation | `uv pip install --no-deps transformers tokenizers safetensors accelerate` | Smaller ML session |
| Vendor purge | Ensure `CODEX_VENDOR_PURGE=1` and audit logs succeed | Removes stray GPU wheels |
| Fast fail on vendor detection | Early guard | Prevents disk churn |

---

## 7. Example Revised Nox Sessions

```python
@nox.session(name="tests")
def tests(session):
    session.install("-r", "requirements-dev.txt")
    session.run("pytest", "-q", "--disable-warnings", "-m", "not requires_torch")

@nox.session(name="ml_tests")
def ml_tests(session):
    session.install("-r", "requirements-dev.txt")
    session.install("-r", "requirements-ml-cpu.txt")
    session.run("pytest", "-q", "-m", "requires_torch or requires_transformers")

@nox.session(name="eval_tests")
def eval_tests(session):
    session.install("-r", "requirements-dev.txt")
    session.install("-r", "requirements-eval.txt")
    session.run("pytest", "-q", "-m", "eval or metrics")
```text

---

## 8. Purge / Constrain Strategy Summary

| Strategy | Implementation | Effect |
|----------|----------------|--------|
| CPU index pin | `PIP_INDEX_URL=https://download.pytorch.org/whl/cpu` | Avoids GPU wheels for torch |
| Vendor purge var | `CODEX_VENDOR_PURGE=1` | Activates purge phase in environment scripts |
| Minimal CPU mode | `CODEX_CPU_MINIMAL=1` | Installs only lean ML subset |
| Strict abort | `CODEX_ABORT_ON_GPU_PULL=1` | Hard fail if vendor wheel slips in |
| Post-purge relock | `CODEX_RELOCK_AFTER_VENDOR_PURGE=1` | Ensures lock excludes GPU packages |
| Guard script | Early check in CI | Prevents proceeding with heavy footprint |

---

## 9. Priority Removal Order (Fastest Space Relief)

| Order | Package Family | Removal Impact | Justification |
|-------|----------------|----------------|---------------|
| 1 | nvidia-* + triton | Huge | Purely GPU; not required for CPU-only tests |
| 2 | jupyterlab stack | Large | Not needed for headless CI |
| 3 | torch (baseline) | Large | Many tests skip if torch absent |
| 4 | Scientific eval (scipy/sklearn/statsmodels) | Large/Medium | Gate behind eval session |
| 5 | ML eval metrics (lm-eval, rouge-score, sacrebleu, nltk) | Medium | Evaluation only |
| 6 | pandas / matplotlib | Medium | Visualization/data convenience only |
| 7 | ray / mlflow | Medium | Feature-flagged; install conditionally |
| 8 | sentencepiece | Small | Adapter shim allows skip |
| 9 | accelerate / peft | Small/Medium | Training fine-tuning only |

---

## 10. Proposed Minimal Baseline (CI Unit Coverage)

Keep:
- `pytest`, `pytest-cov` (if coverage needed)
- `ruff`, `black`, `isort`, `mypy`, `bandit`, `pip-audit`, `defusedxml`, `jsonschema`, `pydantic`, `hydra-core`, `omegaconf`, `requests`, `psutil`

Skip initially (baseline job):
- ML training/eval & GPU families until specialized sessions

Estimated baseline footprint: < 250 MB vs multi-GB current.

---

## 11. Validation Checklist

| Check | Command | Pass Condition |
|-------|---------|----------------|
| No vendor wheels | Guard script (above) | Prints OK JSON vendors=[] |
| Baseline tests w/o ML | `nox -s tests` | All non-ML tests green |
| ML tests isolated | `nox -s ml_tests` | Pass or gracefully skip when optional deps absent |
| Eval tests isolated | `nox -s eval_tests` | Pass or gracefully skip when optional deps absent |
| Disk usage before/after | `df -h` | >6 GB free during install phase |
| Coverage artifact present | `pytest --cov=src/codex_ml` | Coverage OK (torch-dependent tests marked) |
| Purge logged | setup/maint logs | Shows purge phase executed |

---

## 12. Actionable Next Steps

1. Add segmented requirements files (`requirements-ml-cpu.txt`, `requirements-eval.txt`, `requirements-notebook.txt`).
2. Update `noxfile.py` to split ML/eval sessions.
3. Introduce early vendor guard step in CI job(s).
4. Enforce CPU index + `CODEX_FORCE_CPU=1`.
5. Remove notebook & evaluation stacks from default dev install.
6. Re-run CI; confirm disk space stable and coverage flows unaffected.

---

## 13. Reference Links (Ref Commit)

| File | Purpose |
|------|---------|
| requirements-dev.txt | Base dev spec |
| scripts/setup.sh | Vendor purge logic & minimal augmentation |
| sentencepiece/__init__.py | Optional dependency shim |
| torch/__init__.py | Torch stub for optional absence |
| src/codex_ml/utils/torch_checks.py | Torch policy & diagnostics |
| docs/maintenance/Torch_CPU_Policy.md | CPU-only torch policy |
| configs/development/pytest.ini | Test markers (`requires_*`) |
| scripts/maintenance.sh | Purge flow mirrored in maintenance phase |
| scripts/vendor_audit_setup.sh | Audit & vendor distribution sizing |
| _codex_reports/errors_2025-10-19.md | Historical heavy install evidence |

(All links pegged to ref commit: f40ff2bbcacf567eef3dc6bd8c95733859b927dc.)

---

## 14. Optional: Draft Minimal Replacement Dev Spec

```text
# requirements-dev-min.txt
pytest==9.0.0
pytest-cov>=4.1.0
ruff>=0.6.2
black>=24.10.0
mypy>=1.10.0
isort>=6.0.0
pip-audit>=2.7.0
bandit>=1.7.5
types-jsonschema
jsonschema>=4.22.0
pydantic>=2.5.0
hydra-core>=1.3.2
omegaconf==2.3.0
defusedxml>=0.7.1
requests>=2.31.0
psutil>=7.0.0
```text

---

## 15. Summary

By reframing dependency pruning within the established archival policy and retention tooling, we ensure disk relief actions are:
- Auditably recorded (evidence logs),
- Governed (ADR for high-impact removals),
- Reversible (segmented install paths + shims),
- Deterministic (CPU index pin + lock relock),
- Aligned with purge functions (`purge_and_measure`) and retention constructs (checkpoint pruning).

Outcome: Space reduction > 2 GB while strengthening governance and reproducibility; dependency hygiene becomes a first-class archival operation.