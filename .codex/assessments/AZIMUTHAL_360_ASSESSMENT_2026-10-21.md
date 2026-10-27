# 360° Azimuthal Assessment — Autonomous Recursive Self-Improvement

**Date:** 2026-10-21
**Branch:** `copilot/develop-evidence-based-assessment`
**Method:** 1 sequential prerequisite lane (dependency spine) + 4 parallel
independent validation lanes (governance, runtime, integration, packaging),
consolidated into a single actionable gap-closure plan.

---

## 0. Verdict

The seven-link loop (signal → pattern → proposal → gates → PR → post-merge
measurement → confidence update) is **fully built and green offline**
(`tests/self_improvement/` 58/58; SDK 14 passed + 1 designed skip). It is
**not yet a live runtime**: no CI/production path invokes it, and several
correctness/security defects must be fixed before it can run autonomously.
Per the honesty rule, the system remains **partially integrated components**.

---

## 1. Dependency spine (sequential prerequisite)

Critical path is acyclic with explicit file-backed prerequisites:

```
authority (Tier0) ─▶ evidence_store (Tier1) ─▶ pipeline(3A)/executor(3B)
     └─▶ outcome_tracker(3C) ─▶ evaluator(3D) ─▶ loop_runner (Tier4)
```

Blocking file seams that must exist before a live run:
`pattern_learning_store.json`, `.codex/improvement/evidence.jsonl`,
`.codex/improvement/executions.jsonl`. No circular deps detected; kernel
must boot before reasoning; authority before pipeline/executor.

---

## 2. Consolidated deficiencies (all lanes, ranked)

### P0 — Blocking (must fix before any autonomous run)

| ID | Surface | Deficiency | Fix |
|----|---------|-----------|-----|
| A1 | `authority.py:57-67` | Path traversal: fnmatch doesn't normalize; `src/../etc/passwd` matches `src/**` | Normalize/resolve paths, reject `..` and absolute paths before matching |
| A2 | `isolated_execution.py:213-221` | `git apply` not constrained to allowlisted `files` | `git apply --check`; verify `git diff --name-only` ⊆ allowlist |
| A3 | `isolated_execution.py:64-88` | IdempotencyLedger race (no lock/atomic CAS) | File lock + atomic append; rebuild `_seen` per op |
| A4 | `authority.py:102` + `improvement_pipeline.py:194` | `diff_lines` self-reported/spoofable | Compute real diff size from applied patch, not proposer input |
| B1 | `reasoning_engine.py:583-586` | Strategy filter checks only `o.decision_id` truthy → same outcomes rescored for every strategy | Filter by resolved decision's `.strategy == strategy` |
| B2 | `reasoning_engine.py:552,556` | `_decision_index` grows unbounded → OOM | Sliding-window prune (e.g. last 10k) in `improve()` |
| B3 | `calibration.py:103` | Calibration formula dimensionally wrong (`raw*acc/(raw+ε)`) | Normalize correctly (e.g. `raw*(1+(acc-0.5))`) |
| C1 | `.github/workflows/cognitive-analysis-feed.yml:94-97` | References missing `scripts/cognitive/aftermath_evaluator.py` | Create the script or remove the broken step |
| C2 | — | **Loop is offline-only**: `improvement_loop_runner` never invoked from CI | Add CI step feeding `.codex/aftermath/pda_iterations.jsonl` to the runner |
| C3 | — | `EvidenceStore.record_outcome`/`OutcomeTracker.process_outcome` never called in production | Post-merge hook that re-measures signal + records outcome |
| D1 | `pyproject.toml:1-12` | `[tool.maturin]` dead under `setuptools.build_meta`; root wheel has no `codex_swarm` | Pick one backend contract; document Rust as separate optional wheel |

### P1 — High (weaken guarantees / mislead)

- **A5** secret-env regex missing `CREDENTIAL|AUTH|CERT|AUTHORIZATION` → widen pattern, case-insensitive.
- **A6** no `git apply --check` / patch-target validation.
- **A7** IdempotencyLedger `_seen` mutable/poisonable → frozenset + JSON validation.
- **A8** `human_approved` is a bare boolean, unenforced/audited → signed approval token.
- **B4** simulated ML strategy (hard-coded 0.78/0.65, "Simulated ML prediction") reaching production → disable or replace with real model.
- **B5** dual pattern stores (`reasoning/kb.json` vs `pattern_learning_store.json`) unsynced → consolidate to one canonical store.
- **B6** strategy-weight normalization `ZeroDivisionError` edge → guard zero total.
- **B7** per-category calibration never flows back to improve loop → wire category through FeedbackLayer.
- **C4** `.codex/improvement/` not initialized/persisted across workflow runs → durable CI-writable store.
- **D2** Rust swarm is identity transport, not execution; README overstates → clarify or implement.
- **D3** `phase_9_3_concurrent_executor` not wired to Rust swarm → wire dispatcher or document as experiment.
- **D4** publish workflow import-checks only; never runs the offline wheel functional gate → run `test_wheel_functional.py` in CI.

### P2 — Medium / Low

- A9 evaluator read-only is contractual, not enforced → read-only store wrapper.
- A10 fnmatch case-sensitivity inconsistency vs shell_policy → standardize.
- A11 ledger silently swallows corrupted JSON lines → raise/log.
- A12 GIT_* env scrubbing incomplete (author/committer/credential.helper).
- A14 `_hash_paths` silently skips symlinks → explicit check.
- B8 dual OODA (`aries_serpent_core/brain/ooda_orchestrator`) not integrated with kernel.
- B10/11 `numpy` hard import breaks minimal installs; misleading `get_outcomes_for_category("")`.
- C5/6/7 dead wiring: signal→pipeline→outcome never bridged in one workflow.
- D5 version incoherence (root 0.3.0 vs packages 0.1.0a1) → documented version contract.
- D7 FFI bridge has no credential-pattern rejection → add test/boundary.
- D9 unsubstantiated Rust perf claims → benchmark or remove.
- Doc inconsistency: agent counts still diverge across docs (`soft_to_GROUNDED.md` 193, `READINESS_AUDIT_ANALYSIS.md` 152) vs canonical `.codex/agents/AGENT_INVENTORY.md`.

---

## 3. Actionable plan (continuous improvement → E2E gap closure)

**Phase 1 — Safety hardening (P0 governance + runtime correctness):**
A1, A2, A3, A4, B1, B2, B3. Gate: new exploit/regression tests for each;
`tests/self_improvement/` stays green.

**Phase 2 — Live wiring (P0 integration):**
C1 (create/remove `aftermath_evaluator.py`), C2 (CI step feeding PDA →
runner), C3 (post-merge outcome hook), C4 (durable CI store path), D1
(build-backend contract documented). Gate: one fixture event flows
CI-side signal→proposal→gates offline in the workflow.

**Phase 3 — Integrity & trust (P1):**
A5–A8, B4–B7, C/D high items. Gate: secrets can't leak into executor;
calibration is category-aware; single canonical pattern store.

**Phase 4 — Proven end-to-end run (success criterion):**
Execute one real CI-health improvement on a low-risk target; capture the
full 7-link evidence chain in `EvidenceStore`; `improvement_evaluator`
returns `complete`. Only then drop the "partially integrated" caveat.

**Phase 5 — Release & optional Rust (P2):**
D2–D9, version contract, CI offline-gate enforcement. Rust remains an
optional bounded executor with a credential-free FFI boundary.

---

## 4. Execution & PR

All fixes land on `copilot/develop-evidence-based-assessment`. After the
phase objectives are committed and validated, a pull request is opened
against `0D_base_` summarizing the consolidated gap closure (see PR body
checklist mapping each P0/P1 item to its commit and test).
