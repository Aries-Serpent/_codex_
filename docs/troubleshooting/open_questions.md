# Open Questions & Next Steps — Run 4 (Previous Cycle-10-05)

## Offline Hardening Integration Notes
- Deterministic dataset assignments now flow through `src/codex_ml/data/splits.py` and the JSONL/CSV loaders so every record carries a stable `split` keyed by its hashed identifier.
- Evaluation runs can fan metrics into local CSV/NDJSON sinks via `codex evaluate --metrics-sink {csv|ndjson} --metrics-path <file>`; see `src/codex_ml/metrics/sinks.py`.
- LoRA/PEFT hooks remain opt-in: use `codex train --enable-peft` (or `CODEX_ENABLE_PEFT=1`) to exercise `src/codex_ml/interfaces/peft_hooks.py`.
- Capture reproducibility context with `python tools/env/export_env_json.py` which writes `artifacts/env_snapshot.json`.
- Generate the per-capability open question digest with `python tools/docs/gen_open_questions.py` (writes `docs/reference/open_questions_by_capability.md`).
- `Dockerfile.local` is a local-only build aid with a digest-pinned base image; it is intentionally excluded from CI wiring.
- Asset provenance now lives in `assets/manifest.json`; validate before hand-off with `python tools/assets/verify_manifest.py`.
- Deterministic mode helper `src/codex_ml/utils/determinism.py` backs the shared seeding path and respects `CUBLAS_WORKSPACE_CONFIG` requirements.

## Menu Items Covered This Run
- ✅ **Observability (5)** — Closed the system-metrics telemetry gap by wiring `log_system_metrics` and the collector surfaced in the Phase 10 status update.【F:reports/gap_risk_resolution.md†L9-L11】【F:src/codex_ml/training/__init__.py†L90-L156】
- ✅ **Docs polish (7)** — Authored the gap→risk→resolution register so subsequent runs inherit a prioritized mitigation backlog.【F:reports/gap_risk_resolution.md†L1-L15】
- ✅ **Self-management (8)** — Refreshed the high-signal dashboard to highlight remaining open items (advanced modeling, security, deployment).【F:reports/high_signal_findings.md†L1-L7】

## Proposed Menu Focus for Run 5
1. **ChatGPT Codex Modeling (2)** — Deliver guarded Hugging Face model loading and LoRA tests to close the open modeling item.【F:reports/_codex_status_update-Previous Cycle-10-05.md†L53-L53】
2. **Security (4)** — Add SBOM tooling plus moderation adapters to satisfy the outstanding safety mitigation.【F:reports/_codex_status_update-Previous Cycle-10-05.md†L60-L60】
3. **Deployment (6)** — Produce offline container/Makefile assets for reproducible installs.【F:reports/_codex_status_update-Previous Cycle-10-05.md†L62-L62】

## Outstanding Questions
- Which AutoModel targets and tokenizer configs should be validated first to exercise the LoRA pipeline without exceeding offline resource limits?【F:reports/_codex_status_update-Previous Cycle-10-05.md†L53-L53】
- What SBOM format (SPDX vs CycloneDX) best fits the offline toolchain while covering Python and system packages?【F:reports/_codex_status_update-Previous Cycle-10-05.md†L60-L60】
- Where should the Dockerfile live to avoid clashing with existing deployment scripts, and how do we wire it into the make-based workflow?【F:reports/_codex_status_update-Previous Cycle-10-05.md†L62-L62】
- Do we need additional automation to surface gap status changes (e.g., `pre-commit` hook or `nox` task) now that the tracker exists?【F:reports/gap_risk_resolution.md†L1-L15】

---

## Historical Snapshot
### Run 3 (Previous Cycle-09-22)
- Covered Menu items: Docs polish (7), Quality gates (3), Self-management (8).【F:AUDIT_PROMPT.md†L5-L72】【F:scripts/codex_local_audit.sh†L1-L72】
- Outcomes: offline-first audit prompt, reusable local audit runner, and prompt copy workflow for deterministic artefacts.【F:AUDIT_PROMPT.md†L5-L72】【F:scripts/codex_local_audit.sh†L1-L72】
### Run 2 (Previous Cycle-09-22)
- Covered Menu items: Security (4), Observability (5), Self-management (8).
- Added security sweep and observability templates plus shared audit artefact library.
- Outstanding automation and reproducibility questions rolled forward above.

### Run 1 (Previous Cycle-09-22)
- Covered Menu items: Repo map (1), Quality gates (3), Docs polish (7).
- Seeded foundational audit reports, fence validator, and prompt refresh.
- Pending investigations captured above remain relevant until resolved.
