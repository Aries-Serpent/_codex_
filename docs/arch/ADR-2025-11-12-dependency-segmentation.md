# ADR-2025-11-12: Dependency Segmentation & Archival-Aligned Hygiene  
> Generated: 2025-11-12T16:40:00Z | Author: mbaetiong  
> Status: Accepted

## 1. Context
CI and local development environments experienced disk exhaustion (`Errno 28`) driven by heavyweight transitive dependency installs (CUDA vendor wheels, scientific stacks, notebook tooling) not required for baseline unit correctness. Previous monolithic installs inflated virtual environment sizes and slowed cold-start validations. Auditability was limited: dependency modifications were not tracked with the same rigor as tombstone archive operations.

## 2. Problem Statement
We must reduce baseline environment footprint ≥ 2 GB without sacrificing:
- Functional correctness of core modules (`src/codex_ml`, tokenization shims).
- Archival governance (evidence, dual-control purge semantics where applicable).
- Reproducibility guarantees (CPU posture, deterministic minimal augmentation).

## 3. Decision
Segment dependencies into dedicated requirement surfaces:
| Surface | File | Purpose |
|---------|------|---------|
| Baseline dev | `requirements-dev.txt` | Unit tests, linting, security gates |
| ML (CPU) | `requirements-ml-cpu.txt` | Torch + transformers + minimal training stack |
| Evaluation | `requirements-eval.txt` | Metrics, scientific analysis |
| Notebook | `requirements-notebook.txt` | Interactive docs / visualization |

Adopt multi-session Nox orchestration:
- `tests` (baseline), `ml_tests`, `eval_tests`, `notebook_env`.
- Auxiliary sessions: `verify_hygiene`, `evidence_check`, `dependency_plan`, `rollback_smoke`.

Integrate evidence logging in environment scripts (`setup.sh`, `maintenance.sh`) to append JSON lines to `.codex/evidence/dependency_ops.jsonl`. Actions recorded: vendor scans, purges (fallback/primary), lock prune (dryrun/applied), minimal augmentation, torch preinstall/reinstall.

Enforce CPU-only posture by default (`CODEX_FORCE_CPU=1`) while enabling *strict fail* via optional `CODEX_ABORT_ON_GPU_PULL=1`.

## 4. Decision Drivers
| Driver | Notes |
|--------|------|
| Disk pressure relief | Multi-GB vendor and ML wheels removed from baseline |
| Auditability | Evidence parity with archive_ops JSONL |
| Determinism | CPU index pin; minimal augmentation variants |
| Reversibility | Removal of segmented files + session edits restore previous state |
| Governance | ADR & CHANGELOG entries for high-impact removal families |

## 5. Considered Alternatives
| Alternative | Rejected Because |
|-------------|------------------|
| Single requirements file (remove heavy deps ad-hoc) | Lacked explicit session boundaries; rollback ambiguous |
| Docker layer slimming only | Did not address Python-level footprint or evidence visibility |
| On-demand pip installs per test module | Increased complexity, slowed per-test isolation |
| Hard-coded uninstall script in CI without evidence | Non-auditable; divergence risk with maintenance processes |

## 6. Consequences

### Positive
- Significant baseline footprint reduction (estimated 2.2–2.5 GB).
- Faster cold-start CI & reduced network egress.
- Clear contract for where heavy families belong (ml/eval/notebook).
- Evidence trail supports compliance & forensics.

### Negative
- Increased complexity (multiple requirement files).
- Potential developer friction when running ML tests locally.
- Additional maintenance for dependency version alignment across segmented files.

### Mitigations
- Nox sessions advertising missing surfaces.
- `rollback_smoke` session to guide reversibility.
- Evidence schema validation to prevent silent drift.

## 7. Risk Assessment
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-----------|
| Forgetting to update segmented files | Medium | Version drift | dependency_plan + reviewer checklist |
| GPU vendor wheels slipping into lock file | Low (CPU index pin) | Disk bloat | lock prune dry-run + vendor guard |
| Evidence file growth > retention target | Medium | Large repo diff noise | Weekly rotation if >1MB |
| Developer misusing baseline for ML tasks | Medium | Hidden failures | Explicit marker usage & session docs |

## 8. Implementation Sketch
1. Commit segmented requirement files.
2. Update `noxfile.py` with session matrix.
3. Replace `setup.sh` / `maintenance.sh` (rc5) enabling evidence logging support.
4. Introduce vendor guard script (CI pre-step).
5. Append segmentation section to `AGENTS.md`.
6. Create this ADR.
7. Add CHANGELOG entry summarizing segmentation and savings.
8. Post-merge: enable `CODEX_CPU_MINIMAL=1` in baseline if safe (optional optimization).

## 9. Evidence & Provenance
| Artifact | Path |
|----------|------|
| Triage document | `docs/analysis/dependency_space_triage.md` |
| Evidence log (dependency) | `.codex/evidence/dependency_ops.jsonl` |
| Archive policy | `docs/arch/_archive-policy/canonical-archiving-policy.md` |
| Setup script version tag | `scripts/setup.sh` (Version: 5.5.2-rc5) |
| Maintenance script version tag | `scripts/maintenance.sh` (Version: 5.5.2-rc5) |

## 10. Compliance Alignment
- Mirrors archive model (append-only, auditable operations).
- Supports retention: dependency logs can be rotated similar to session logs—backup + compress + preserve hash chain.
- Enables later integration with signature/attestation pipeline (future in-toto compatibility).

## 11. Rollback Procedure (Summary)
```bash
git rm requirements-ml-cpu.txt requirements-eval.txt requirements-notebook.txt
# Edit noxfile.py: remove ml_tests, eval_tests, notebook_env sessions
# Optional: set CODEX_DEPENDENCY_EVIDENCE_ENABLE=0 (not recommended)
```text
Evidence historical lines remain; do NOT delete `.codex/evidence/dependency_ops.jsonl`.

## 12. Monitoring Post-Deployment
| Metric | Source | Threshold |
|--------|--------|-----------|
| Vendor recurrence | maintenance summary JSON | >1 recurrence hash under fail policy triggers review |
| Evidence size | file size | Rotate >1MB |
| Disk savings | CI artifact du logs | Maintain ≥2GB reduction vs. pre-change baseline |
| Lock prune application | evidence lines | Evaluate if repeated GPU refs persist in diffs |

## 13. Future Enhancements
| Enhancement | Description | Priority |
|-------------|-------------|----------|
| Signed evidence records | Sigstore OIDC signing per line | Medium |
| Automated dependency plan gating | Score & propose removal ADR drafts | Medium |
| GPU vendor diff visualizer | Show lock & purge delta in PR comment | Low |
| Memory pressure telemetry integration | Capture virtualenv disk footprint metrics JSON | High |

## 14. Acceptance Criteria
- Baseline CI job completes without space errors.
- `.codex/evidence/dependency_ops.jsonl` contains all action types for initial run.
- Nox sessions functional (tests separated cleanly).
- ADR merged & referenced in CHANGELOG.
- Vendor residue = empty after purge steps in both setup & maintenance scripts.

## 15. Decision Record
Accepted on: 2025-11-12  
Approvers: Platform Maintainers / QA Sign-off  
Link to PR(s): (to be populated)  

---

*End of ADR-2025-11-12-dependency-segmentation*