# Repository-Wide QA Walkthrough Master Plan (Audit Report Continuation)

> **Scope:** Aries-Serpent/_codex_ monorepo (Distributed Intelligence Engine, Cognitive Runtime, Legacy Agents)
> **Mode:** Pre-Genesis advisory, execution-ready
> **Objective:** End-to-end QA walkthrough plan covering architecture, security, functional parity, and data integrity
> **Coverage Goal:** 100% path-to-coverage plan (minimum 70% immediate target) with risk-driven prioritization

---

## 0) Execution Protocol & Safety Gates

### 0.1 Mandatory Preconditions
- Confirm SAFE_MODE constraints and do not enable workflows without human approval.
- Verify **AI Codebase Agency Policy** compliance: all discovered issues must be addressed before sign-off.
- Use **tokenization-friendly** output: short headings, bullet lists, explicit file paths.
- Prefer **tree -L 4** for structure mapping (avoid `ls -R`).

### 0.2 Built-in Tooling & Agents (Required Leverage)
- **Utilities**
  - `python scripts/space_traversal/audit_runner.py run` (full audit)
  - `make space-audit-fast` (quick traversal)
  - `python scripts/security/check_dependencies.py` (dependency risk)
  - `python -m codex.logging.query_logs` (telemetry analysis)
- **Agents**
  - `ci-testing-agent` for CI/test diagnosis
  - **NEW:** `qa-walkthrough-agent` (this plan provides its responsibilities)

### 0.3 Test Environment Remediation (Required)
- Install test dependencies before running pytest:
  - `pip install --no-cache-dir -r requirements.txt`
  - `pip install --no-cache-dir -r requirements-test.txt`
- Ensure `pytest-timeout`, `hydra-core`, and `mlflow` are available to prevent:
  - `pytest: error: unrecognized arguments: --timeout=300 --timeout-method=thread`
  - `ModuleNotFoundError: No module named 'hydra'`
  - `ModuleNotFoundError: No module named 'mlflow'`

### 0.4 Evidence & Logging
- Record every step in:
  - `.codex/action_log.ndjson`
  - `.codex/change_log.md`
  - `.codex/results.md`

---

## 1) Root Governance & Build Baseline Audit

### 1.1 Enforcement Check (Constitution Validation)
**Targets:** `.importlinter`, `.fencefixer.yml`, `.dvcignore`

**Procedure:**
- Verify boundary enforcement: `agents/` ↔ `src/` ↔ `codex_ml/` ↔ `cognitive_app/`
- Validate markdown sanitization rules are active and applied to docs & prompts.
- Confirm `.dvcignore` protects datasets and checkpoints in `codex_ml/training/**`.

**Evidence:**
- Capture config summaries and mismatches.

### 1.2 Infrastructure Validation (Docker & .dockerignore)
**Targets:** `Dockerfile*`, `.dockerignore`

**Procedure:**
- Inventory all Dockerfiles (CPU/GPU/Embedding/Prod).
- Verify **multi-stage builds** for each.
- Confirm `.dockerignore` excludes:
  - `codex_ml/training/**`
  - `mlruns/**`
  - `*.ckpt`, `*.pth`, `*.pt`

**Acceptance Criteria:**
- No single-stage Dockerfile for production builds.
- No IP-leaking artifacts copied into image layers.

### 1.3 Dependency Mapping
**Targets:** `requirements*.txt`, `scripts/security/check_dependencies.py`

**Procedure:**
- Run dependency checker and compare with requirements files.
- Flag:
  - unpinned dependencies,
  - known vulnerable packages,
  - non-approved licenses.

**Deliverable:**
- Supply chain risk matrix with remediation steps.

---

## 2) Intelligence Engine & Split-Brain Remediation Audit

### 2.1 Authority Conflict Mapping
**Targets:** `agents/` vs `src/codex/`

**Procedure:**
- Build a mapping table of legacy modules to modern equivalents.
- **Priority:** deprecate `agents/zendesk_quantum_orchestrator.py` in favor of `src/codex/zendesk/quantum/orchestrator.py`.

**Acceptance Criteria:**
- Modern module is canonical import path.
- Legacy module routes or hard-deprecates.

### 2.2 Core Intelligence Verification
**Targets:** `codex_ml/`, `src/cognitive_brain/`

**Procedure:**
- Audit “System 2” reasoning logic and Quantum metaphors.
- Inspect `entanglement.py`, `superposition.py` for deterministic fallbacks.
- Confirm no duplicated reasoning logic in legacy `agents/`.

### 2.3 Data Persistence Shift (mlruns → DB)
**Targets:** `./mlruns`, DB config (SQLite/PostgreSQL)

**Procedure:**
- Validate migration steps: counts, run IDs, tags, metrics parity.
- Ensure no data loss and rollback/dual-write plan is explicit.

---

## 3) Runtime, Service Mesh, & API Contract Audit

### 3.1 Hybrid Runtime Audit
**Targets:** `cognitive_app/`

**Procedure:**
- Investigate `cognitive_app/src/orchestrator.py` anomaly.
- Verify bundling pipeline does not ship backend code to frontend.

### 3.2 Service Layer Validation
**Targets:** `services/ita`, `services/msp_gateway`, `tenant_context.py`

**Procedure:**
- Validate tenant isolation in all request entry points.
- Confirm explicit tenant validation and no default tenant fallbacks.

### 3.3 Synaptic Bridge Hardening
**Targets:** `temp/bridge_codex_copilot_bridge`

**Procedure:**
- Confirm move from loopback TCP to authenticated Linux FIFO.
- Ensure `0o600` permissions and enforced auth checks.

---

## 4) Security, Privacy, & DataOps Integrity Audit

### 4.1 PII & Sanitization Lifecycle
**Targets:** `src/codex/knowledge/pii.py`, `pgvector_store.py`

**Procedure:**
- Trace PII scrubber usage before vectorization.
- Verify enforced call paths in ingestion pipeline.

### 4.2 Static Analysis Governance
**Targets:** `semgrep_rules/`, `.gitleaks.toml`

**Procedure:**
- Confirm custom rule enforcement for `pickle_load.yml`, `subprocess_shell.yml`.
- Verify rules are referenced in CI configs.

### 4.3 Token Management Neutralization
**Targets:** `scripts/security/copilot_token_decoder.py`, `verify_token_scope.py`

**Procedure:**
- Ensure decoder script removed/deprecated.
- Validate `verify_token_scope.py` uses `x-oauth-scopes` header.

---

## 5) Operational Observability & CI/CD Gating Audit

### 5.1 Manual Gating Policy
**Targets:** `.github/_workflows_disabled/`

**Procedure:**
- Verify manual workflow activation process is documented.
- Ensure non-autonomous activation remains enforced.

### 5.2 Self-Hosted Constraint Check
**Targets:** `.github/workflows/*`

**Procedure:**
- Confirm `runs-on: [self-hosted, linux]` in all active workflows.
- Validate `[skip ci]` logic for resource gating.

### 5.3 Telemetry Stream Audit
**Targets:** `audit_artifacts/`, `logs/`

**Procedure:**
- Confirm security events write to immutable `audit.jsonl`.
- Ensure sensitive data is not logged to standard logs.

---

## 6) Coverage Path-to-100% Plan (Minimum 70% Target)

### 6.1 Coverage Inventory
- Generate coverage report for:
  - core orchestration in `src/codex/`
  - data persistence migration paths
  - tenant isolation logic
  - PII scrubbing workflows

### 6.2 Gap Prioritization
- Rank by blast radius:
  1) Auth / tenant context
  2) Data persistence migration
  3) PII pipeline
  4) Service mesh routing
  5) Legacy agent deprecations

### 6.3 Execution Steps
- Add tests to close critical gaps (start with tenant isolation + PII).
- Target 70% coverage in first pass; iterate to 100%.

**Deliverables:**
- Coverage delta report.
- Test additions with deterministic assertions.

---

## 7) Required Outputs (Tokenization-Friendly)
- **Repo Map**: `tree -L 4` snapshot (stored as text artifact).
- **Conflict Matrix**: legacy vs modern modules.
- **Security Compliance**: static analysis enforcement status.
- **Migration Report**: mlruns → DB parity.
- **CI/CD Gate**: workflow status & runner constraints.
- **Coverage Plan**: prioritized test coverage backlog.

---

## 8) QA Walkthrough Agent Responsibilities (New Agent)

### `qa-walkthrough-agent` (Purpose)
- Execute this plan with deterministic output.
- Coordinate audits across phases.
- Produce consolidated findings and remediation actions.

### Activation Example
```markdown
@copilot Use qa-walkthrough-agent to execute the repository-wide QA walkthrough plan.
```

---

## 9) Immediate Next Steps
1. Generate repo map via `tree -L 4`.
2. Run `make space-audit-fast`.
3. Run `python scripts/security/check_dependencies.py`.
4. Create conflict matrix (agents vs src/codex).
5. Start coverage inventory.

---

## 10) Acceptance Criteria
- All audit phases executed with evidence.
- All discovered issues remediated or escalated.
- Coverage plan committed with timeline.
- No policy violations (SAFE_MODE respected).
