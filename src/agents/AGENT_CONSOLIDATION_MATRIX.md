# Agent Consolidation Matrix

> **Generated:** 2026-05-24T23:00:00Z
> **Branch:** `copilot/analyze-test-coverage-and-documentation`
> **Hand-off agent:** `agent-orchestrator` (supporting: `skills-master-agent`, `cross-agent-knowledge-graph`, `agent-iq-scoring-gate`).
> **ADA citation:** [../.codex/CODEBASE_AGENCY_POLICY.md](../.codex/CODEBASE_AGENCY_POLICY.md)
> **Source of truth:** `.github/agents/AGENT_REGISTRY.yaml` (registry total 164; 148 active after final security-family consolidation; 16 archived).
> **Applied:** 2026-09-04 (final dedupe sweep: active count 150 → 148)
> **Security sweep complete:** 2 remaining duplicate family entries archived; unified-security-scanner remains the canonical entry point.

This matrix captures the Keep / Merge-into / Archive decisions for each agent family identified in the implementation plan. The orchestrator must apply these to `AGENT_REGISTRY.yaml` and add a deprecation note in each archived agent's prompt file (the file itself remains for backward compatibility until the next sweep).

---

## Decision legend

- **Keep** — agent has a distinct surface; remains canonical.
- **Merge → X** — agent is deprecated; capability folds into `X`. Add `deprecated: true` and `superseded_by: X` to the registry entry. Update prompt file with a deprecation banner pointing at `X`.
- **Archive** — agent is no longer reachable from any workflow/orchestrator path; move prompt file to an archive directory.

---

## A. Coverage family → `unified-coverage-agent` (confirmed; already in flight)

| Agent | Decision | Rationale |
|---|---|---|
| `unified-coverage-agent` | **Keep** | Single entry point for monitoring, gap-fill, maintenance, and roadmap gate enforcement. |
| `coverage-gapfill-agent` | Merge → `unified-coverage-agent` | Already marked DEPRECATED in tool catalog. |
| `coverage-maintenance-agent` | Merge → `unified-coverage-agent` | Already marked DEPRECATED. |
| `coverage-roadmap-agent` | Merge → `unified-coverage-agent` | Already marked DEPRECATED. |
| `test-coverage-agent` | Merge → `unified-coverage-agent` | Already marked DEPRECATED. |
| `test-coverage-monitor` | Merge → `unified-coverage-agent` | Already marked DEPRECATED. |

**Action:** No further consolidation needed — confirm the five deprecations are reflected in `AGENT_REGISTRY.yaml` and that all referencing workflows have been updated to invoke `unified-coverage-agent`.

---

## B. Documentation family → `unified-doc-agent`

| Agent | Decision | Rationale |
|---|---|---|
| `unified-doc-agent` | **Keep** | Single entry point for doc management. |
| `documentation-quality-agent` | Merge → `unified-doc-agent` | Quality assessment is a capability tag on the unified agent. |
| `documentation-consolidator` | Merge → `unified-doc-agent` | Consolidation is a capability tag. |
| `doc-freshness-checker` | **Keep (specialist)** | Distinct scheduled-job surface; runs link/timestamp checks asynchronously. |
| `doc-refactor-test-agent` | **Keep (specialist)** | Refactoring + tests-for-docs is a narrow surface; keep until coverage of that surface is folded into `unified-doc-agent`. |
| `link-validator-agent` | **Keep (specialist)** | Used by `post-merge-doc-alignment-agent` as a subroutine. |
| `terminology-consistency-agent` | **Keep (specialist)** | Cross-cutting linting; folds in only after a stable glossary lives in `agents/`. |
| `post-merge-doc-alignment-agent` | **Keep** | Distinct trigger (post-merge into `main`). |

**Action:** Merge two; defer five for next sweep.

---

## C. Security family → `unified-security-scanner`

| Agent | Decision | Rationale |
|---|---|---|
| `unified-security-scanner` | **Keep** | Canonical SAST + deps + secrets entry point. | <!-- pragma: allowlist secret -->
| `secret-detection-agent` | Merge → `unified-security-scanner` | Capability tag. | <!-- pragma: allowlist secret -->
| `dependency-vulnerability-scanner` | Merge → `unified-security-scanner` | Capability tag. |
| `dependency-security-review-agent` | Merge → `unified-security-scanner` | Capability tag (review variant). |
| `security-audit-agent` | Merge → `unified-security-scanner` | Capability tag. |
| `codeql-alert-resolution-agent` | **Keep (specialist)** | Distinct: it *fixes* alerts, others *detect*. Includes Playwright scraping (per tool catalog). |
| `code-scanning-remediation-agent` | **Keep (specialist)** | Distinct remediation surface for GHAS. |
| `security-alert-verification-agent` | **Keep (specialist)** | Verification distinct from detection/remediation. |
| `dependency-conflict-agent` | **Keep** | Solves pip-resolver conflicts, not security. |
| `bridge-security-monitor` | **Keep** | IPC bridge surface. |

**Action:** Merge the two remaining active duplicates (`dependency-vulnerability-scanner`, `secret-detection-agent`) into `unified-security-scanner`; keep the remaining specialist surfaces where the *action verb* (fix/verify/remediate) is distinct from scanning.

---

## D. CI healing family → `self-healing-orchestrator-agent` + `ci-auto-healer-agent`

| Agent | Decision | Rationale |
|---|---|---|
| `self-healing-orchestrator-agent` | **Keep** (orchestrator) | Coordinates the loop. |
| `ci-auto-healer-agent` | **Keep** (worker) | Generic auto-fix executor. |
| `ci-failure-resolution-agent` | Merge → `ci-auto-healer-agent` | Overlapping surface. |
| `ci-triage-pipeline-agent` | **Keep (specialist)** | Severity routing — distinct from healing itself. |
| `ci-importerror-agent` | **Keep (specialist)** | Distinct pattern surface (sys.path + missing deps + path-shadow imports per `scripts/metrics/__init__.py` memory). |
| `ci-parameter-mismatch-healer` | **Keep (specialist)** | Distinct pattern surface (workflow caller vs reusable). |
| `ci-docker-build-healer` | **Keep (specialist)** | Distinct pattern surface (Dockerfile multi-stage + src-layout). |
| `ci-resilience-emergency-response-agent` | Merge → `ci-emergency-response-agent` | Both are emergency-class; collapse into one. |
| `ci-emergency-response-agent` | **Keep** | Canonical rapid-response. |
| `ci-log-retrieval-agent` | **Keep (specialist)** | Distinct read-only surface. |
| `ci-pattern-guardian` | **Keep** | Enforces pattern KG; distinct from healing. |
| `ci-health-alert-agent` | **Keep** | Auto-responds to `ci-health-alert` issues; distinct trigger. |
| `ci-optimization-agent` | **Keep** | Performance, not healing. |
| `ci-testing-agent` | **Keep** | Distinct: debugs collection/import errors during dev. |

**Action:** Merge two (`ci-failure-resolution-agent`, `ci-resilience-emergency-response-agent`).

---

## E. Governance family → `unified-governance-gate`

| Agent | Decision | Rationale |
|---|---|---|
| `unified-governance-gate` | **Keep** | Canonical PR/deploy gate. |
| `owner-approval-guard` | **Keep (specialist)** | Distinct enforcement surface (owner-only ops). |
| `policy-coach-agent` | **Keep (specialist)** | Coaching is read-only; distinct from gating. |
| `workflow-compliance-guardian` | **Keep (specialist)** | Concurrency + timeout enforcement; distinct surface. |
| `claim-verification-agent` | **Keep** | Verifies PR/commit claims; distinct surface. |

**Action:** No merges. Five-agent governance lattice is intentional separation of concerns.

---

## F. Workflow / cache family → `workflow-management-agent`

| Agent | Decision | Rationale |
|---|---|---|
| `workflow-management-agent` | **Keep** | Canonical workflow CRUD. |
| `workflow-optimization-agent` | **Keep (specialist)** | Performance/parallelism. |
| `workflow-ci-fixer` | **Keep (specialist)** | Syntax/config fixes. |
| `workflow-analytics-agent` | **Keep** | Read-only analytics. |
| `workflow-health-monitor` | **Keep** | Live health. |
| `workflow-health-monitor.deprecated` | **Archive** | Already marked deprecated by `.deprecated` suffix. |
| `cache-management-agent` | **Keep** | Canonical 4-layer cache. |
| `cache-manager-integration` | Merge → `cache-management-agent` | Integration is a sub-capability. |

**Action:** Archive one (`workflow-health-monitor.deprecated`); merge one (`cache-manager-integration`).

---

## G. RAG / knowledge family — already mostly consolidated

| Agent | Decision |
|---|---|
| `rag-index-manager` | **Keep** |
| `rag-module-management-agent` | **Keep** |
| `rag-freshness-loop-agent` | **Keep** |
| `rag-meta-tensor-guardian` | **Keep** |
| `rag-meta-tensor-regression-agent` | **Keep (specialist)** |
| `meta-tensor-validator` | **Keep** (broader scope than just RAG) |

No merges proposed; the meta-tensor surface is high-risk enough to warrant separate guard/regression/validation agents.

---

## Summary of proposed changes

| Category | Merge | Archive | Net delta |
|---|---:|---:|---:|
| Coverage | 5 (already in flight) | 0 | confirmed |
| Docs | 2 | 0 | −2 |
| Security | 2 | 0 | −2 |
| CI healing | 2 | 0 | −2 |
| Governance | 0 | 0 | 0 |
| Workflow/cache | 1 | 1 | −2 |
| **Total this sweep** | **2 merges** | **0 archives** | **−2 (150 → 148)** |

After the final active-family dedupe pass, the active agent count moves from **150 → 148** while archived entries increase to **16** in the canonical registry.

---

## Required follow-up by `agent-orchestrator`

1. Edit `.github/agents/AGENT_REGISTRY.yaml`:
   - For each row above marked **Merge**, set `deprecated: true` and `superseded_by: <unified-agent>`.
   - For each row marked **Archive**, move the YAML entry to an `archive:` section and remove from active set.
2. Edit each deprecated/archived agent's prompt file under `.github/agents/`:
   - Prepend a deprecation banner with `Superseded by <unified-agent>` and the ADA citation.
3. Grep all `.github/workflows/*.yml` for the deprecated agent names and update calls to invoke the unified agents instead.
4. Re-run `agent-iq-scoring-gate` on the unified agents to confirm IQ thresholds remain green after capability folding.
5. Update `agents/AGENT_REGISTRY.md`, `agents/AGENT_ECOSYSTEM_MAP.md`, `agents/AGENT_SELECTION_GUIDE.md` with the new active count and the deprecation notices.
6. Post a PDA Loop → AfterMath turn citing this matrix.

This Copilot session deliberately produces the matrix as the input artifact; the orchestrator and skills-master agents are responsible for the registry mutation since this session lacks read/write access to `.github/agents/`.
