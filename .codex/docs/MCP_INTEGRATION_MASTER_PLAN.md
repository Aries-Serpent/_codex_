# MCP Integration Master Plan

> **Scope:** Aries-Serpent/_codex_ cognitive brain integration strategy for the full MCP surface  
> **Servers:** `github-mcp-server` + `playwright`  
> **Research basis:** `.codex/agent_context.json`, MCP reference docs, skill manifests/handlers, PDA loop state, and memory backends inspected on 2026-08-01

---

## 1. Executive Summary

- **Total MCP surface:** **57 tools** across **2 servers** (36 GitHub-side + 21 Playwright).
- **Current integration coverage:** **28/57** explicit repo-local references or integration paths found in `.codex/docs/`, `.github/agents/`, `docs/`, or `src/` (**estimate**, documentation/code scan rather than runtime telemetry).
- **Gaps identified:** **29 tools** have no clear first-class integration path today.
- **Inventory baseline:** companion references are aligned to the current **36 GitHub-side tools** and **21 Playwright tools**; reverify this dated runtime surface before changing counts.
- **Recommended P0 integrations:**
  1. Discussion-backed memory bridge: wire `get_discussion`, `get_discussion_comments`, `list_discussion_categories`, and `list_discussions` into continuation chains and STM→LTM promotion.
  2. Secret-scanning ingestion: wire `list_secret_scanning_alerts` + `get_secret_scanning_alert` into `unified-security-scanner` and `secret-detection-agent`.
  3. Issue/project queue awareness: wire `list_issues`, `list_issue_fields`, and `list_issue_types` into CI/security routing agents.
  4. Deployment observability: wire Playwright `network_requests`, `console_messages`, `wait_for`, `resize`, and `tabs` into Pages/cognitive-app verification.
  5. Agent-IQ telemetry: use `actions_get(get_workflow_run_usage)` + `actions_list` to score effectiveness, latency, and cost inside `agent-iq-scoring-gate`.

---

## 2. MCP Server Inventory

| Server | Version | Tool Count | Status |
|--------|---------|-----------:|--------|
| `github-mcp-server` | `remote-112de3b831975632257acbdeb73b577f32ea1762` | 36 | Active |
| `playwright` | `0.0.40` | 21 | Active |

> **Note:** the GitHub-side total follows the current agent-exposed surface used for this project. Variable/secret mutation is still **not** provided by the read-only GitHub MCP endpoint; writes remain `gh`/REST/agent-side workflows.

---

## 3. Cognitive Brain Objectives × MCP Tool Matrix

| Objective | MCP tools used / planned | Priority | Implementation notes |
|-----------|--------------------------|----------|----------------------|
| Session context pre-load | `pull_request_read(get_comments/get_check_runs)`, `actions_list(list_workflow_runs)`, `get_file_contents`, `search_code`; local `.codex/` reads remain primary. | **P0** | Wire MCP PR/CI reads into `cognitive-brain-session-injector` so pre-load can enrich local repo state with live PR comments, checks, and remote file context. |
| PDA loop (observe → orient → decide → act) | `actions_list`, `actions_get`, `get_job_logs`, `pull_request_read`, `list_code_scanning_alerts`; backed today by `pda.loop.logger` and `ci.health.analyzer`. | **P0** | This is the most mature path today: CI evidence can already be observed and classified; next step is turning every fix/result into a canonical MCP evidence bundle. |
| Memory sync (STM → LTM) | `get_discussion`, `get_discussion_comments`, `list_discussion_categories`, `list_discussions` planned; local SQLite/JSONL backends are active today. | **P0** | Current memory backends are local (`JSONLMemoryBackend`, `SQLiteMemoryBackend`). MCP gap is externalizing/promoting memory to GitHub Discussions for cross-session retrieval. |
| CI health monitoring | `actions_list`, `actions_get`, `get_job_logs`, `pull_request_read(get_check_runs)`, `list_issues`, `search_issues` planned. | **P0** | Maps directly to `ci.monitor.proactive`, `ci.health.analyzer`, `workflow-health-monitor`, and `ci-health-alert-agent`; should feed `CODEX_CI_FAILURE_RATE` and related variables. |
| Security scanning | `list_code_scanning_alerts`, `get_code_scanning_alert`, `list_secret_scanning_alerts`, `get_secret_scanning_alert`, `search_code`, `get_commit`, `web_search`. | **P0** | Read-only GitHub MCP is sufficient for triage; mutation still happens through `gh`/REST. Missing piece is scheduled ingestion of secret-scanning and code-scanning alerts into memory. |
| Agent IQ scoring | `actions_get(get_workflow_run_usage)`, `actions_list`, `list_commits`, `search_pull_requests` planned. | **P1** | Tie workflow usage, latency, and recovery success back to `agent-iq-scoring-gate`; no end-to-end MCP wiring exists yet. |
| Code quality gates | `pull_request_read(get_reviews/get_review_comments/get_files/get_status)`, `get_job_logs`, `search_code`, `get_file_contents`. | **P1** | Enough surface exists to synthesize reviewer feedback, changed-file context, and failing checks into one quality gate summary. |
| Documentation freshness | `get_file_contents`, `search_code`, `list_commits`, `get_commit`, `get_latest_release`, `get_release_by_tag`, `web_search`. | **P1** | Best fit for `doc.refresh.agent`, `documentation-quality-agent`, and `doc-freshness-checker`; should compare code, docs, release notes, and live pages. |
| Deployment verification | `actions_list`, `actions_get`, `get_job_logs` + Playwright `navigate`, `snapshot`, `network_requests`, `console_messages`, `take_screenshot`, `wait_for`. | **P0** | This closes the loop from CI success to live-surface verification for Pages, docs, and the cognitive app. |

---

## 4. Variable Wiring Specification

> **Important:** `github-mcp-server` is read-only for Actions variables/secrets. In practice, MCP provides **read/derive/validate** inputs, while **writes** still flow through `gh api`, workflow automation, or `repo-var-sync-agent`.

| Variable | MCP producer/update path | Consumers (agents / skills) | Frequency | Current status |
|----------|--------------------------|------------------------------|-----------|----------------|
| `AGENT_HANDOFF_TIMEOUT_SECONDS` | No MCP write path; read from `.codex/agent_context.json` snapshot or `get_file_contents`. | `agent-orchestrator`, `orchestrator-agent`, handoff logic. | Per-session | **wired** |
| `AGENT_TOOLSDIRECTORY` | No MCP write path; environment snapshot only. | Build/runner-aware agents, packaging/test automation. | Per-session | **wired** |
| `AUTO_PROMOTE_TIER_ENABLED` | Derived from repo-var snapshot; no MCP writer today. | `agent-iq-scoring-gate`, `unified-governance-gate`. | Per-PR / admin toggle | **planned** |
| `CODEX_CI_FAILURE_RATE` | `actions_list` + `pull_request_read(get_check_runs)` derive value; write still via `gh`/REST or `repo-var-sync-agent`. | `ci.monitor.proactive`, `ci-health-alert-agent`, `workflow-health-monitor`. | Per-PR + daily | **wired** |
| `CODEX_CI_FAILURE_THRESHOLD` | Read from snapshot; future derivation can use `actions_get(get_workflow_run_usage)` + historical runs. | `ci.monitor.proactive`, `ci.triage-pipeline-agent`. | Daily / admin | **planned** |
| `CODEX_CI_LAST_GREEN_SHA` | `actions_list`/`actions_get` can identify source SHA; write still external to MCP. | `workflow-health-monitor`, `claim-verification-agent`, release verification. | Per-green-run | **wired** |
| `CODEX_CLI_API_URL` | Read from snapshot; Playwright `navigate` and GitHub run metadata can verify reachability. | `cognitive-brain-cli-agent`, `cognitive-ooda-loop-agent`. | Per-session | **wired** |
| `CODEX_COVERAGE_THRESHOLD` | Read from snapshot; future enforcement can combine `pull_request_read(get_check_runs)` + test artifacts. | `unified-coverage-agent`, `test-coverage-monitor`. | Per-PR / admin | **planned** |
| `CODEX_LOG_LEVEL` | Snapshot only; no MCP write path. | CLI/runtime logging stack. | Per-session / admin | **gap** |
| `CODEX_NETWORK_MODE` | Snapshot only; validate with Playwright/browser and workflow telemetry, but no MCP writer. | `bridge-security-monitor`, `owner-approval-guard`. | Per-session / admin | **planned** |
| `COGNITIVE_BRAIN_ALLOWED_ACTORS` | `list_repository_collaborators`/`search_users` can validate roster; writes remain gh/REST. | `owner-approval-guard`, `policy-coach-agent`, auth workflows. | Daily / policy change | **planned** |
| `COGNITIVE_BRAIN_INJECTION_ENABLED` | `get_file_contents` validates config and docs; session injector consumes locally. | `cognitive-brain-session-injector`, `session_hook.py`. | Per-session / admin | **wired** |
| `COGNITIVE_BRAIN_LTM_RETENTION_DAYS` | Snapshot only; future memory-sync dashboards can read and enforce. | `memory.sync.consolidation`, `memory-sync-agent`. | Daily / admin | **planned** |
| `COGNITIVE_BRAIN_MAX_CONTEXT_TOKENS` | Snapshot only; local injector enforces budget. | `cognitive-brain-session-injector`, `session_hook.py`. | Per-session / admin | **wired** |
| `COGNITIVE_BRAIN_MEMORY_TIER` | `get_discussion*`/memory sync tools planned to externalize tier behavior; current writes non-MCP. | `memory.sync.consolidation`, `memory-sync-agent`, `session_hook.py`. | Per-session / admin | **planned** |
| `COGNITIVE_BRAIN_PATTERN_MIN_CONFIDENCE` | Security/CI/doc pipelines can use MCP evidence as scoring input; current storage is snapshot-only. | `pattern_discovery`, `memory-sync-agent`, `agent-iq-scoring-gate`. | Per-session / admin | **planned** |
| `COGNITIVE_BRAIN_SESSION_NUMBER` | `get_discussion_comments`, `pull_request_read`, and CI telemetry can stamp session lineage; write remains gh/REST. | `session_hook.py`, `pda.loop.logger`, continuation chains. | Per-session | **wired** |
| `COPILOT_AGENT_AUTH_ENABLED` | `pull_request_read`/`list_repository_collaborators` can verify policy context; value is owner-managed. | All autonomous agents; WEC/governance logic. | Per-session | **wired** |
| `COPILOT_AGENT_CCA_VERSION_LOCK` | `get_file_contents` validates docs/config; no MCP writer required. | `cognitive-brain-session-injector`, multi-turn agent loops. | Per-session / admin | **wired** |
| `COPILOT_AGENT_DEDUPLICATION_ENABLED` | `get_file_contents` validates runtime contract; no MCP writer required. | `cognitive-brain-session-injector`, integrated system deduplicator. | Per-session / admin | **wired** |
| `COPILOT_AGENT_FIREWALL_ENABLED` | Security triage tools (`list_secret_scanning_alerts`, `list_code_scanning_alerts`) can justify flips; write is non-MCP. | `bridge-security-monitor`, `unified-security-scanner`. | Per-incident | **planned** |
| `COPILOT_AGENT_MAX_AUTONOMY_LEVEL` | Snapshot only; can be checked during PR/workflow review. | `agent-iq-scoring-gate`, `unified-governance-gate`. | Per-session / admin | **wired** |
| `COPILOT_AGENT_SESSION_RESTORE_ENABLED` | `get_discussion_comments`/memory sync planned for recovery context; current state from snapshot. | `cognitive-brain-session-injector`, resume flows. | Per-session / admin | **planned** |
| `COPILOT_AGENT_TURN_ISOLATION_ENABLED` | `get_file_contents` validates runtime contract; no MCP writer required. | `cognitive-brain-session-injector`, integrated multi-turn loops. | Per-session / admin | **wired** |
| `COPILOT_CLI_BASE_URL` | Playwright `navigate`/`wait_for`/`network_requests` validate service availability; value itself is snapshot-managed. | `cognitive-brain-cli-agent`, `github-pages-manager`. | Per-session | **wired** |
| `COPILOT_CLI_ENABLED` | Validated via Pages/CLI/browser flows; no MCP write path. | `cognitive-brain-cli-agent`, `cognitive-ooda-loop-agent`. | Per-session / admin | **wired** |
| `EMBEDDING_INDEX_AUTO_REBUILD` | `search_code` + Actions telemetry can detect staleness/rebuild need; current writer is non-MCP. | `rag-index-manager`, `rag-freshness-loop-agent`, `semantic-search`. | Daily / on-change | **planned** |

---

## 5. Process Integration Map (Mermaid)

```mermaid
flowchart TD
    A[Session start] --> B[Local pre-load\nAGENTIC_REPO_STATE + policy + accountability + PDA + agent_context]
    B --> C[GitHub MCP enrichers\npull_request_read + actions_list + get_file_contents]
    C --> D[Cognitive brain initialization\nsession_hook.py + session injector]
    D --> E{Objective routing}

    E --> F[CI trigger / failing run]
    F --> G[actions_list / actions_get / get_job_logs]
    G --> H[ci.health.analyzer + pda.loop.logger]
    H --> I[Update PDA store + derive CODEX_CI_FAILURE_RATE]
    I --> J[memory.sync.consolidation]

    E --> K[Security signal]
    K --> L[list_code_scanning_alerts / get_code_scanning_alert / list_secret_scanning_alerts]
    L --> M[unified-security-scanner / secret-detection-agent]
    M --> J

    E --> N[Deployment or docs verification]
    N --> O[actions_get + Playwright navigate/snapshot/network_requests/console_messages]
    O --> P[github-pages-manager / documentation-quality-agent]
    P --> Q[Evidence bundle + variable write via gh/REST]

    J --> R[Discussion-backed memory sync (planned)\nget_discussion + get_discussion_comments]
    Q --> S[Downstream agents consume refreshed variables\nand continuation-chain context]
```

---

## 6. Implementation Roadmap

### Phase 1 — Immediate (P0 gaps)
- Reverify the dated runtime surface before publication and keep all companion references aligned to 57 tools (36 GitHub-side + 21 Playwright).
- Implement discussion-backed memory sync and continuation-chain harvesting.
- Add secret-scanning alert ingestion and issue/project queue ingestion to CI/security agents.
- Add Playwright deployment-observability primitives (`network_requests`, `console_messages`, `wait_for`) to `github-pages-manager` and `qa-walkthrough-agent` playbooks.
- Define a write-capable variable bridge contract because GitHub MCP remains read-only for Actions variables/secrets.

### Phase 2 — Next sprint (P1 gaps)
- Wire Actions usage metrics and commit/PR search into agent IQ scoring and governance trend analysis.
- Extend documentation freshness checks with release/tag/commit provenance and live-site Playwright checks.
- Add collaborator/user discovery to owner-approval and actor-governance flows.
- Publish a canonical “MCP evidence bundle” schema shared by CI, security, docs, and deployment workflows.

### Phase 3 — Future (P2/P3 enhancements)
- Add release/tag dashboards, cross-repo benchmarking, and browser multi-tab regression patrols.
- Promote MCP evidence into embeddings/semantic search for recall during future sessions.
- Introduce automated gap scoring so each tool’s integration maturity is measurable over time.

---

## 7. Cross-Reference Index

| Tool | Server | Document | Skill | Variable | Agent |
|------|--------|----------|-------|----------|-------|
| `github-mcp-server-actions_get` | `github-mcp-server` | `docs/ci/GITHUB_API_COPILOT_AGENT_REFERENCE.md` | `ci.monitor.proactive` | `CODEX_CI_LAST_GREEN_SHA` | `workflow-health-monitor` |
| `github-mcp-server-actions_list` | `github-mcp-server` | `.codex/docs/COPILOT_MCP_TOOL_REFERENCE.md` | `ci.monitor.proactive` | `CODEX_CI_FAILURE_RATE` | `ci-health-alert-agent` |
| `github-mcp-server-get_code_scanning_alert` | `github-mcp-server` | `.codex/docs/MCP_INTEGRATION_MASTER_PLAN.md` | `—` (planned security bridge) | `COPILOT_AGENT_FIREWALL_ENABLED` | `security-alert-verification-agent` |
| `github-mcp-server-get_commit` | `github-mcp-server` | `docs/ci/GITHUB_API_COPILOT_AGENT_REFERENCE.md` | `code.search.extract` | `COGNITIVE_BRAIN_SESSION_NUMBER` | `claim-verification-agent` |
| `github-mcp-server-get_discussion` | `github-mcp-server` | `.codex/docs/MCP_INTEGRATION_MASTER_PLAN.md` | `memory.sync.consolidation` | `COGNITIVE_BRAIN_MEMORY_TIER` | `cross-agent-knowledge-graph` |
| `github-mcp-server-get_discussion_comments` | `github-mcp-server` | `.codex/docs/MCP_INTEGRATION_MASTER_PLAN.md` | `pda.loop.logger` | `COGNITIVE_BRAIN_SESSION_NUMBER` | `cross-agent-knowledge-graph` |
| `github-mcp-server-get_file_contents` | `github-mcp-server` | `.codex/docs/GITHUB_API_AND_MCP_REFERENCE.md` | `doc.refresh.agent` | `COGNITIVE_BRAIN_INJECTION_ENABLED` | `documentation-quality-agent` |
| `github-mcp-server-get_job_logs` | `github-mcp-server` | `.codex/docs/COPILOT_MCP_TOOL_REFERENCE.md` | `ci.health.analyzer` | `CODEX_CI_FAILURE_RATE` | `ci-log-retrieval-agent` |
| `github-mcp-server-get_label` | `github-mcp-server` | `.codex/docs/MCP_INTEGRATION_MASTER_PLAN.md` | `—` (planned issue routing) | `COPILOT_AGENT_AUTH_ENABLED` | `policy-coach-agent` |
| `github-mcp-server-get_latest_release` | `github-mcp-server` | `.codex/docs/MCP_INTEGRATION_MASTER_PLAN.md` | `doc.refresh.agent` | `CODEX_CI_LAST_GREEN_SHA` | `pypi-publishing-operations-agent` |
| `github-mcp-server-get_release_by_tag` | `github-mcp-server` | `.codex/docs/MCP_INTEGRATION_MASTER_PLAN.md` | `doc.refresh.agent` | `CODEX_CI_LAST_GREEN_SHA` | `github-pages-manager` |
| `github-mcp-server-get_secret_scanning_alert` | `github-mcp-server` | `docs/ci/GITHUB_API_COPILOT_AGENT_REFERENCE.md` | `—` (planned security bridge) | `COPILOT_AGENT_FIREWALL_ENABLED` | `secret-detection-agent` |
| `github-mcp-server-get_tag` | `github-mcp-server` | `.codex/docs/MCP_INTEGRATION_MASTER_PLAN.md` | `doc.refresh.agent` | `CODEX_CI_LAST_GREEN_SHA` | `github-pages-manager` |
| `github-mcp-server-issue_read` | `github-mcp-server` | `.codex/docs/COPILOT_MCP_TOOL_REFERENCE.md` | `ci.monitor.proactive` | `CODEX_CI_FAILURE_THRESHOLD` | `ci-triage-pipeline-agent` |
| `github-mcp-server-list_branches` | `github-mcp-server` | `.codex/docs/MCP_INTEGRATION_MASTER_PLAN.md` | `code.search.extract` | `COPILOT_AGENT_SESSION_RESTORE_ENABLED` | `branch-divergence-resolution-agent` |
| `github-mcp-server-list_code_scanning_alerts` | `github-mcp-server` | `docs/ci/GITHUB_API_COPILOT_AGENT_REFERENCE.md` | `—` (planned security bridge) | `COPILOT_AGENT_FIREWALL_ENABLED` | `codeql-alert-resolution-agent` |
| `github-mcp-server-list_commits` | `github-mcp-server` | `docs/ci/GITHUB_API_COPILOT_AGENT_REFERENCE.md` | `doc.refresh.agent` | `CODEX_CI_LAST_GREEN_SHA` | `claim-verification-agent` |
| `github-mcp-server-list_discussion_categories` | `github-mcp-server` | `.codex/docs/MCP_INTEGRATION_MASTER_PLAN.md` | `memory.sync.consolidation` | `COGNITIVE_BRAIN_MEMORY_TIER` | `cross-agent-knowledge-graph` |
| `github-mcp-server-list_discussions` | `github-mcp-server` | `.codex/docs/MCP_INTEGRATION_MASTER_PLAN.md` | `memory.sync.consolidation` | `COGNITIVE_BRAIN_MEMORY_TIER` | `cross-agent-knowledge-graph` |
| `github-mcp-server-list_issue_fields` | `github-mcp-server` | `.codex/docs/MCP_INTEGRATION_MASTER_PLAN.md` | `—` (planned issue routing) | `CODEX_CI_FAILURE_THRESHOLD` | `ci-triage-pipeline-agent` |
| `github-mcp-server-list_issue_types` | `github-mcp-server` | `.codex/docs/MCP_INTEGRATION_MASTER_PLAN.md` | `—` (planned issue routing) | `CODEX_CI_FAILURE_THRESHOLD` | `ci-triage-pipeline-agent` |
| `github-mcp-server-list_issues` | `github-mcp-server` | `.codex/docs/MCP_INTEGRATION_MASTER_PLAN.md` | `ci.monitor.proactive` | `CODEX_CI_FAILURE_RATE` | `ci-health-alert-agent` |
| `github-mcp-server-list_label` | `github-mcp-server` | `.codex/docs/MCP_INTEGRATION_MASTER_PLAN.md` | `—` (planned issue routing) | `COPILOT_AGENT_AUTH_ENABLED` | `policy-coach-agent` |
| `github-mcp-server-list_pull_requests` | `github-mcp-server` | `.codex/docs/COPILOT_MCP_TOOL_REFERENCE.md` | `ci.monitor.proactive` | `COGNITIVE_BRAIN_SESSION_NUMBER` | `pr-check-remediation-agent` |
| `github-mcp-server-list_releases` | `github-mcp-server` | `.codex/docs/MCP_INTEGRATION_MASTER_PLAN.md` | `doc.refresh.agent` | `CODEX_CI_LAST_GREEN_SHA` | `pypi-publishing-operations-agent` |
| `github-mcp-server-list_repository_collaborators` | `github-mcp-server` | `.codex/docs/MCP_INTEGRATION_MASTER_PLAN.md` | `—` (planned governance bridge) | `COGNITIVE_BRAIN_ALLOWED_ACTORS` | `owner-approval-guard` |
| `github-mcp-server-list_secret_scanning_alerts` | `github-mcp-server` | `.codex/docs/MCP_INTEGRATION_MASTER_PLAN.md` | `—` (planned security bridge) | `COPILOT_AGENT_FIREWALL_ENABLED` | `unified-security-scanner` |
| `github-mcp-server-list_tags` | `github-mcp-server` | `.codex/docs/MCP_INTEGRATION_MASTER_PLAN.md` | `doc.refresh.agent` | `CODEX_CI_LAST_GREEN_SHA` | `github-pages-manager` |
| `github-mcp-server-pull_request_read` | `github-mcp-server` | `.codex/docs/COPILOT_MCP_TOOL_REFERENCE.md` | `ci.monitor.proactive` | `COPILOT_AGENT_AUTH_ENABLED` | `pr-check-remediation-agent` |
| `github-mcp-server-search_code` | `github-mcp-server` | `.codex/docs/COPILOT_MCP_TOOL_REFERENCE.md` | `code.search.extract` | `EMBEDDING_INDEX_AUTO_REBUILD` | `semantic-search` |
| `github-mcp-server-search_commits` | `github-mcp-server` | `.codex/docs/MCP_INTEGRATION_MASTER_PLAN.md` | `—` (planned provenance bridge) | `CODEX_CI_LAST_GREEN_SHA` | `claim-verification-agent` |
| `github-mcp-server-search_issues` | `github-mcp-server` | `.codex/docs/MCP_INTEGRATION_MASTER_PLAN.md` | `ci.monitor.proactive` | `CODEX_CI_FAILURE_RATE` | `ci-health-alert-agent` |
| `github-mcp-server-search_pull_requests` | `github-mcp-server` | `.codex/docs/MCP_INTEGRATION_MASTER_PLAN.md` | `ci.monitor.proactive` | `COGNITIVE_BRAIN_SESSION_NUMBER` | `github-guru-agent` |
| `github-mcp-server-search_repositories` | `github-mcp-server` | `.codex/docs/GITHUB_API_AND_MCP_REFERENCE.md` | `doc.refresh.agent` | `COGNITIVE_BRAIN_ALLOWED_ACTORS` | `github-guru-agent` |
| `github-mcp-server-search_users` | `github-mcp-server` | `.codex/docs/MCP_INTEGRATION_MASTER_PLAN.md` | `—` (planned governance bridge) | `COGNITIVE_BRAIN_ALLOWED_ACTORS` | `owner-approval-guard` |
| `web_search` | `github-mcp-server` | `.codex/docs/GITHUB_API_AND_MCP_REFERENCE.md` | `doc.refresh.agent` | `COGNITIVE_BRAIN_PATTERN_MIN_CONFIDENCE` | `documentation-quality-agent` |
| `playwright-browser_click` | `playwright` | `.codex/docs/MCP_PLAYWRIGHT_RECIPE.md` | `—` (planned UI verification skill) | `COPILOT_CLI_BASE_URL` | `qa-walkthrough-agent` |
| `playwright-browser_close` | `playwright` | `.codex/docs/MCP_INTEGRATION_MASTER_PLAN.md` | `—` (planned UI verification skill) | `COPILOT_CLI_ENABLED` | `github-pages-manager` |
| `playwright-browser_console_messages` | `playwright` | `.codex/docs/MCP_INTEGRATION_MASTER_PLAN.md` | `—` (planned UI verification skill) | `COPILOT_CLI_ENABLED` | `github-pages-manager` |
| `playwright-browser_drag` | `playwright` | `.codex/docs/MCP_INTEGRATION_MASTER_PLAN.md` | `—` (planned UI verification skill) | `CODEX_CLI_API_URL` | `qa-walkthrough-agent` |
| `playwright-browser_evaluate` | `playwright` | `.codex/docs/MCP_PLAYWRIGHT_RECIPE.md` | `—` (planned UI verification skill) | `COPILOT_CLI_BASE_URL` | `github-pages-manager` |
| `playwright-browser_file_upload` | `playwright` | `.codex/docs/MCP_PLAYWRIGHT_RECIPE.md` | `—` (planned UI verification skill) | `COPILOT_CLI_BASE_URL` | `integration-test-runner` |
| `playwright-browser_fill_form` | `playwright` | `.codex/docs/MCP_PLAYWRIGHT_RECIPE.md` | `—` (planned UI verification skill) | `CODEX_CLI_API_URL` | `qa-walkthrough-agent` |
| `playwright-browser_handle_dialog` | `playwright` | `.codex/docs/MCP_INTEGRATION_MASTER_PLAN.md` | `—` (planned UI verification skill) | `COPILOT_CLI_ENABLED` | `qa-walkthrough-agent` |
| `playwright-browser_hover` | `playwright` | `.codex/docs/MCP_INTEGRATION_MASTER_PLAN.md` | `—` (planned UI verification skill) | `CODEX_CLI_API_URL` | `qa-walkthrough-agent` |
| `playwright-browser_install` | `playwright` | `.codex/docs/COPILOT_MCP_TOOL_REFERENCE.md` | `—` (planned UI verification skill) | `AGENT_TOOLSDIRECTORY` | `integration-test-runner` |
| `playwright-browser_navigate` | `playwright` | `.codex/docs/MCP_PLAYWRIGHT_RECIPE.md` | `—` (planned UI verification skill) | `COPILOT_CLI_BASE_URL` | `github-pages-manager` |
| `playwright-browser_navigate_back` | `playwright` | `.codex/docs/MCP_INTEGRATION_MASTER_PLAN.md` | `—` (planned UI verification skill) | `COPILOT_CLI_BASE_URL` | `qa-walkthrough-agent` |
| `playwright-browser_network_requests` | `playwright` | `.codex/docs/MCP_INTEGRATION_MASTER_PLAN.md` | `—` (planned UI verification skill) | `CODEX_CLI_API_URL` | `github-pages-manager` |
| `playwright-browser_press_key` | `playwright` | `.codex/docs/MCP_PLAYWRIGHT_RECIPE.md` | `—` (planned UI verification skill) | `CODEX_CLI_API_URL` | `qa-walkthrough-agent` |
| `playwright-browser_resize` | `playwright` | `.codex/docs/MCP_INTEGRATION_MASTER_PLAN.md` | `—` (planned UI verification skill) | `COPILOT_CLI_ENABLED` | `qa-walkthrough-agent` |
| `playwright-browser_select_option` | `playwright` | `.codex/docs/MCP_PLAYWRIGHT_RECIPE.md` | `—` (planned UI verification skill) | `CODEX_CLI_API_URL` | `qa-walkthrough-agent` |
| `playwright-browser_snapshot` | `playwright` | `.codex/docs/MCP_PLAYWRIGHT_RECIPE.md` | `—` (planned UI verification skill) | `COPILOT_CLI_ENABLED` | `github-pages-manager` |
| `playwright-browser_tabs` | `playwright` | `.codex/docs/MCP_INTEGRATION_MASTER_PLAN.md` | `—` (planned UI verification skill) | `COPILOT_CLI_BASE_URL` | `qa-walkthrough-agent` |
| `playwright-browser_take_screenshot` | `playwright` | `.codex/docs/MCP_PLAYWRIGHT_RECIPE.md` | `doc.refresh.agent` | `COPILOT_CLI_ENABLED` | `github-pages-manager` |
| `playwright-browser_type` | `playwright` | `.codex/docs/MCP_PLAYWRIGHT_RECIPE.md` | `—` (planned UI verification skill) | `CODEX_CLI_API_URL` | `qa-walkthrough-agent` |
| `playwright-browser_wait_for` | `playwright` | `.codex/docs/MCP_INTEGRATION_MASTER_PLAN.md` | `—` (planned UI verification skill) | `COPILOT_CLI_BASE_URL` | `github-pages-manager` |

---

## Synthesis Notes

- The strongest **current** integrations are CI triage (`actions_list`, `get_job_logs`, `pull_request_read`) plus local cognitive-brain skills (`ci.monitor.proactive`, `ci.health.analyzer`, `pda.loop.logger`).
- The largest structural gap is **state mutation**: GitHub MCP can observe nearly everything needed for routing, but it still cannot mutate repository variables/secrets, so the cognitive brain needs a durable write bridge.
- The largest unused value pool is the **discussion + issue/project** surface, which can convert one-off session outputs into durable memory, triage queues, and governance signals.
- The largest Playwright gap is **observability tooling** (`network_requests`, `console_messages`, `wait_for`, `tabs`, `resize`) for post-deploy verification; navigation and screenshots alone are not enough for reliable cognitive-app/Pages validation.
