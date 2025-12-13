# RAG + Verification Stack Backlog — Batchset Plan

## Current state
- Scanned 81 expected artifacts; 74 are missing. Existing files: `README.md`, `LICENSE`, `.gitignore`, `.env.example`, `.github/workflows/ci.yml`, and the repo root itself. All other architecture, RAG, tooling, verification, evaluation, and infra files listed in the consolidated spec are absent and require creation.
- Goal: drive iterative creation of every missing artifact to production readiness with explicit acceptance criteria, tests, and verification.

## Work batches
Each batch groups related missing files. Run batches sequentially; complete acceptance and verification before moving on. Prompts are intended for GPT-5.1-Codex-Max (planner) with o4-mini/o3 for verification steps.

### B1 — Config & Governance
**Missing files:**
- `configs/models.yaml`
- `configs/rag_config.yaml`
- `configs/tools.schema.json`
- `configs/verification_policy.yaml`
- `configs/security_policies.yaml`
- `configs/logging.yaml`
- `configs/evals_config.yaml`
- `configs/routing.yaml`

**Prompt:**
> Draft minimal-yet-production-ready YAML/JSON configs for models, RAG sources, tools schema, verification policy, security policies, logging, evals, and routing. Use environment-variable placeholders for secrets/IDs. Keep defaults backward-compatible and documented.

**Acceptance criteria:**
- Schemas parse (YAML/JSON) and include comments where helpful.
- Roles mapped to concrete model IDs; RAG sources, chunking, embedding, and index settings present.
- Verification policy enforces VERIFIED only with evidence and defines UNKNOWN fallback.
- Security policy enforces read/write separation and prod restrictions.
- Logging config defines levels/format/sinks; evals/routing configs wire suites to pipelines.

**Verification:**
- `python -m py_compile` on config loader modules (once created) if applicable.
- `python - <<'PY'` snippet to load each YAML/JSON via `yaml.safe_load`/`json.load`.

### B2 — System Prompts & Templates
**Missing files:**
- `prompts/system/agent_core.md`
- `prompts/system/verification_pipeline.md`
- `prompts/system/tool_usage_guidelines.md`
- `prompts/templates/cove_answer.yaml`
- `prompts/templates/error_reporting.yaml`
- `prompts/templates/task_templates/` (seed with README and exemplar)
- `prompts/domains/infra_change_policy.md`
- `prompts/domains/code_review_policy.md`

**Prompt:**
> Author concise, low-fluff system prompts covering role, truth policy, tool/RAG usage, and CoVe steps. Provide structured template for CoVe answers, error reporting format, and starter task templates. Include domain policies for infra change and code review.

**Acceptance criteria:**
- Prompts are explicit on UNKNOWN vs VERIFIED states and when to call tools/RAG.
- CoVe template matches verification policy fields.
- Domain prompts include risk checks and safe rollout rules.

**Verification:**
- Manual lint for clarity; ensure YAML templates parse via `yamllint` or `python -c "import yaml; yaml.safe_load(open(...))"`.

### B3 — AI-Facing & Human Docs
**Missing files:**
- `docs/human-facing/architecture.md`
- `docs/human-facing/deployment.md`
- `docs/human-facing/security_and_risks.md`
- `docs/human-facing/evals_and_metrics.md`
- `docs/ai-facing/tools_reference.md`
- `docs/ai-facing/domain_facts/infra_basics.md`
- `docs/ai-facing/domain_facts/coding_standards.md`
- `docs/ai-facing/domain_facts/business_rules.md`
- `docs/ai-facing/glossary.md`

**Prompt:**
> Draft concise docs covering architecture, deployment/rollback, security risks, and eval metrics for the agent stack. Create AI-facing tools reference and stable domain fact sheets plus glossary.

**Acceptance criteria:**
- Architecture doc includes diagrams/flows (text or Mermaid) and data lineage.
- Deployment doc describes env vars, migrations, rollback steps.
- Security doc covers PII/tenant isolation and tooling permissions.
- Evals doc lists metrics, thresholds, and gating rules.
- AI-facing docs are succinct and align with tools/configs.

**Verification:**
- Internal links resolve; run `python -m compileall docs` to ensure UTF-8 readability.

### B4 — Agent Core & Adapters
**Missing files:**
- `src/agent/orchestrator.py`
- `src/agent/state_models.py`
- `src/agent/runners/cli_runner.py`
- `src/agent/runners/api_runner.py`
- `src/agent/adapters/openai_responses_client.py`
- `src/agent/adapters/tracing_adapter.py`

**Prompt:**
> Implement PLAN→ACT→OBSERVE→VERIFY state machine with Responses API/tool calls, using typed state models. Provide CLI and API runners, plus adapters for OpenAI Responses client and tracing. Respect verification policy and token budgeting.

**Acceptance criteria:**
- Orchestrator supports retries, aborts, and integrates RAG + tools + CoVe.
- State models typed with enums for claim states.
- CLI/API runners runnable with config paths.
- Adapters isolate external deps; safe fallbacks for missing creds.

**Verification:**
- Unit tests: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests/unit/test_orchestrator.py` (once authored).
- Type hints validated via `mypy` when available.

### B5 — RAG Pipeline
**Missing files:**
- `src/rag/indexer.py`
- `src/rag/retriever.py`
- `src/rag/sources/git_source.py`
- `src/rag/sources/blob_storage_source.py`
- `src/rag/sources/db_source.py`
- `src/rag/utils/chunking.py`

**Prompt:**
> Build ingestion/indexing with chunking, embeddings, and incremental updates. Provide retriever abstraction and source connectors for Git, blob storage, and optional DB. Include chunking utilities with overlap controls.

**Acceptance criteria:**
- Idempotent ingestion, metadata captured (source, timestamp, version).
- Retriever supports filters and top-k; token budgeting respected.
- Git/blob/DB sources configurable and mockable.

**Verification:**
- Unit tests for chunking and retrieval; dry-run ingest with sample repo/blobs.

### B6 — Tools Layer
**Missing files:**
- `src/tools/git_tools.py`
- `src/tools/devops_tools.py`
- `src/tools/db_tools.py`
- `src/tools/http_tools.py`

**Prompt:**
> Implement typed tool functions with schema validation, clear error semantics, and read/write separation. Include branch/commit/diff tools, devops monitors, read-only DB queries, and allowlisted HTTP fetcher.

**Acceptance criteria:**
- Tools expose schema metadata; reject bad inputs deterministically.
- Safe defaults for prod (read-only unless allowed).

**Verification:**
- Unit tests under `tests/unit/test_tools_git.py` etc.; run with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests/unit -k tools`.

### B7 — Verifiers & Verification Engine
**Missing files:**
- `src/verifiers/package_registry_verifier.py`
- `src/verifiers/schema_verifier.py`
- `src/verifiers/infra_plan_verifier.py`
- `src/verifiers/code_quality_verifier.py`
- `src/verification/policy_engine.py`
- `src/verification/cove_pipeline.py`
- `src/verification/result_annotator.py`

**Prompt:**
> Build deterministic verifiers (package registry, schema, infra plan, code quality) and connect them via policy engine + CoVe pipeline + result annotator. Enforce VERIFIED requires trusted evidence.

**Acceptance criteria:**
- Verifier outputs structured pass/fail with reasons.
- Policy engine applies states per claim with trusted-source rules.
- CoVe pipeline supports multi-pass verification and annotations.

**Verification:**
- Unit tests: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests/unit/test_verification_policy.py tests/unit/test_cove_pipeline.py`.

### B8 — Evaluation Harness & Suites
**Missing files:**
- `src/evaluation/harness.py`
- `src/evaluation/suites/regression_suite.json`
- `src/evaluation/suites/domain_specific/infra_evals.json`
- `src/evaluation/suites/domain_specific/code_evals.json`

**Prompt:**
> Implement evaluation harness that runs scenarios and reports grounding/hallucination metrics. Seed regression and domain-specific eval JSON suites.

**Acceptance criteria:**
- Harness runnable via CLI; metrics aggregated with thresholds.
- Suites include expected claim states and notes.

**Verification:**
- Unit: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests/evals/test_eval_harness.py` (once authored).

### B9 — Utilities
**Missing files:**
- `src/utils/logging_utils.py`
- `src/utils/config_loader.py`
- `src/utils/error_types.py`
- `src/utils/time_utils.py`

**Prompt:**
> Provide shared utilities for logging setup, layered config loading, error type enums, and time helpers with deterministic behavior.

**Acceptance criteria:**
- Utilities are dependency-light and tested; config loader supports env overrides.

**Verification:**
- Unit: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests/unit -k "logging_utils or config_loader or error_types"`.

### B10 — Test Suites
**Missing files:**
- `tests/unit/test_rag.py`
- `tests/unit/test_verification_policy.py`
- `tests/unit/test_tools_git.py`
- `tests/unit/test_cove_pipeline.py`
- `tests/unit/test_orchestrator.py`
- `tests/integration/test_end_to_end_agent.py`
- `tests/integration/test_high_risk_flows.py`
- `tests/evals/test_eval_harness.py`

**Prompt:**
> Author unit/integration tests covering RAG, tools, verification policy, CoVe, orchestrator, and eval harness. Use fixtures/mocks to avoid live calls; enforce UNKNOWN/VERIFIED semantics.

**Acceptance criteria:**
- Tests deterministic; skip markers for heavy deps; coverage targets >=80% for touched modules.

**Verification:**
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests` with relevant markers.

### B11 — Scripts & Infra
**Missing files:**
- `scripts/run_ingest.sh`
- `scripts/run_agent_local.sh`
- `scripts/run_evals.sh`
- `infra/docker/Dockerfile.agent`
- `infra/docker/Dockerfile.ingest`
- `infra/k8s/deployment-agent.yaml`
- `infra/k8s/deployment-ingest.yaml`
- `infra/terraform/main.tf`
- `infra/terraform/variables.tf`
- `.github/workflows/deploy.yml`

**Prompt:**
> Provide runnable scripts for ingest, local agent, and evals; containerize agent and ingest workers; optional k8s/terraform scaffolds; and deploy workflow gated behind approvals and non-prod defaults.

**Acceptance criteria:**
- Shell scripts are executable and documented.
- Dockerfiles build without GPU by default; configurable via args.
- k8s/terraform templates parameterized and safe defaults; deploy workflow disabled or approval-gated.

**Verification:**
- `shellcheck` on scripts; `docker build` dry-run (if env permits); YAML lint on k8s/terraform; CI workflow passes `act` dry-run if available.

## Execution guidance
- Tackle batches in order; keep commits small per batch.
- Use CoVe/self-critique after each batch; record evidence links.
- Maintain docs/prompts in sync with configs and tools; rerun targeted tests after each batch.
