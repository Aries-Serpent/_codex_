# RAG + Verification Stack Patchset Prompts

Use these iterative prompts to generate and self-verify each missing artifact until all files exist and meet production criteria. Execute prompts batch-by-batch; after each file is produced, re-run quick checks and update evidence links.

## Global instructions
- Obey repository AGENTS.md guidance, least-privilege tooling, and UNKNOWN/VERIFIED rules.
- Prefer dependency-light implementations; gate optional integrations behind feature flags and env vars.
- For every file, include inline TODOs only if absolutely necessary and tracked; otherwise ship complete content.
- Run targeted tests after each patch; if unavailable, run `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests -k <area>` and document results.

## Patch prompts by area

### Config foundation
**Targets:** `configs/models.yaml`, `configs/rag_config.yaml`, `configs/tools.schema.json`, `configs/verification_policy.yaml`, `configs/security_policies.yaml`, `configs/logging.yaml`, `configs/evals_config.yaml`, `configs/routing.yaml`

**Prompt:**
> Create configuration files for models, RAG sources, tool schemas, verification policy, security policies, logging, eval selection, and routing. Use env placeholders for secrets (e.g., `env:STORE_ID`). Enforce VERIFIED requires evidence, prod is read-only by default, and logs are structured with JSON option.

**Definition of done:** YAML/JSON validated; defaults backward-compatible; comments for operators; sample values or references included.

**Verification:** load each file via `python - <<'PY'` using `yaml.safe_load`/`json.load` and ensure keys exist; run config loader unit tests once implemented.

### System prompts & templates
**Targets:** `prompts/system/agent_core.md`, `prompts/system/verification_pipeline.md`, `prompts/system/tool_usage_guidelines.md`, `prompts/templates/cove_answer.yaml`, `prompts/templates/error_reporting.yaml`, `prompts/templates/task_templates/` (README + exemplar), `prompts/domains/infra_change_policy.md`, `prompts/domains/code_review_policy.md`

**Prompt:**
> Write concise prompts specifying role, truth policy, tool vs RAG usage, and CoVe steps. Provide YAML templates for CoVe answers and error reporting. Add task template examples and domain policies (infra changes must use plan verifiers and avoid direct applies; code review must demand diffs/tests and avoid guessing).

**Definition of done:** Prompts reference verification policy states; templates parse as YAML; task templates include input/output slots.

**Verification:** `yamllint` or `python -c "import yaml; yaml.safe_load(open('prompts/templates/cove_answer.yaml'))"`.

### AI-facing and human docs
**Targets:** human-facing `architecture.md`, `deployment.md`, `security_and_risks.md`, `evals_and_metrics.md`; AI-facing `tools_reference.md`, domain facts (`infra_basics.md`, `coding_standards.md`, `business_rules.md`), `glossary.md`.

**Prompt:**
> Draft concise documentation for humans (architecture, deployment/rollback, security, eval metrics) and AI (tool reference, domain facts, glossary). Include data flow diagrams (text/Mermaid), rollback procedures, tenant isolation, eval thresholds, and per-tool guidance.

**Definition of done:** Docs aligned with configs/tools; contain links to prompts/configs; AI docs optimized for retrieval (bullets, headers, IDs).

**Verification:** Check internal links and spelling; optional `markdownlint`.

### Agent core & adapters
**Targets:** `src/agent/orchestrator.py`, `state_models.py`, runners, `adapters/openai_responses_client.py`, `adapters/tracing_adapter.py`.

**Prompt:**
> Implement PLAN→ACT→OBSERVE→VERIFY orchestrator integrating RAG, tools, CoVe pipeline, and verification policy. Provide typed state models, CLI/API runners, and adapters for Responses API and tracing (OTEL-friendly). Handle retries, timeouts, aborts, and token budgeting.

**Definition of done:** Deterministic state transitions; error handling separated; runners accept config paths and log trace IDs; adapters mockable.

**Verification:** Unit tests in `tests/unit/test_orchestrator.py`; dry-run CLI with sample config; `mypy` on agent package if enabled.

### RAG pipeline
**Targets:** `src/rag/indexer.py`, `retriever.py`, sources (`git_source.py`, `blob_storage_source.py`, `db_source.py`), `utils/chunking.py`.

**Prompt:**
> Build ingestion + retrieval with incremental updates, chunking (size/overlap), embeddings, metadata (source, timestamp, version), and connectors for Git/blob/DB. Provide retriever API `retrieve(query, domain, k=5, filters=None, budget=None)` with dedupe and token budgeting.

**Definition of done:** Index rebuild/replay supported; chunking deterministic; sources support mocks; logging of ingest stats.

**Verification:** Unit tests in `tests/unit/test_rag.py`; sample ingest dry-run with fixtures.

### Tools layer
**Targets:** `src/tools/git_tools.py`, `devops_tools.py`, `db_tools.py`, `http_tools.py`

**Prompt:**
> Implement typed tools with schemas, deterministic errors, and read/write separation. Git tools for branches/commits/diffs; devops tools for CI/monitoring queries; DB tool read-only with allowlist; HTTP tool allowlisted with timeout/retry guards.

**Definition of done:** Tool registry exports metadata; invalid params rejected with clear error types; prod mode blocks writes.

**Verification:** Unit tests `tests/unit/test_tools_git.py` and siblings; schema validation via `configs/tools.schema.json` loader.

### Verifiers & verification engine
**Targets:** verifiers (`package_registry_verifier.py`, `schema_verifier.py`, `infra_plan_verifier.py`, `code_quality_verifier.py`) and verification core (`policy_engine.py`, `cove_pipeline.py`, `result_annotator.py`).

**Prompt:**
> Implement deterministic verifiers and wire them through policy engine + CoVe. Enforce VERIFIED requires trusted evidence; classify claims UNKNOWN when evidence missing; support multi-pass reconciliation and evidence annotations.

**Definition of done:** Verifiers return structured results with reasons; policy engine applies rules from `configs/verification_policy.yaml`; CoVe pipeline outputs annotated claims.

**Verification:** Run `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests/unit/test_verification_policy.py tests/unit/test_cove_pipeline.py` when tests exist; add golden examples.

### Evaluation harness & suites
**Targets:** `src/evaluation/harness.py`, `suites/regression_suite.json`, `suites/domain_specific/infra_evals.json`, `suites/domain_specific/code_evals.json`.

**Prompt:**
> Create evaluation harness to execute scenarios, collect grounding/hallucination metrics, and enforce thresholds. Seed regression and domain suites with expected claim states.

**Definition of done:** Harness CLI configurable; metrics exported (JSON/CSV); suites documented.

**Verification:** `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests/evals/test_eval_harness.py`; spot-run harness against sample prompts.

### Utilities
**Targets:** `src/utils/logging_utils.py`, `config_loader.py`, `error_types.py`, `time_utils.py`

**Prompt:**
> Implement shared utilities: logging setup (JSON/text), layered config loader with env overrides, typed error enums, and deterministic time helpers (UTC, monotonic timers).

**Definition of done:** Minimal deps; clear docstrings; deterministic outputs; backward-compatible defaults.

**Verification:** Unit tests in `tests/unit` targeting utilities; `python -m py_compile src/utils/*.py`.

### Test suites
**Targets:** `tests/unit/test_rag.py`, `test_verification_policy.py`, `test_tools_git.py`, `test_cove_pipeline.py`, `test_orchestrator.py`; integration tests `tests/integration/test_end_to_end_agent.py`, `test_high_risk_flows.py`; eval tests `tests/evals/test_eval_harness.py`.

**Prompt:**
> Author deterministic tests covering happy paths, error handling, UNKNOWN/VERIFIED transitions, token budgeting, and integration of RAG + tools + CoVe. Use fixtures/mocks; skip heavy external deps with markers.

**Definition of done:** Tests reproducible; coverage for edge cases and failure paths; no live network by default.

**Verification:** `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests`; add coverage flags when feasible.

### Scripts, infra, and deploy
**Targets:** `scripts/run_ingest.sh`, `run_agent_local.sh`, `run_evals.sh`, Dockerfiles under `infra/docker/`, k8s manifests under `infra/k8s/`, terraform under `infra/terraform/`, and `.github/workflows/deploy.yml`.

**Prompt:**
> Provide scripts to run ingest, local agent, and evals with env var docs and safety checks. Dockerfiles for agent/ingest (CPU by default), k8s manifests with resource requests and ConfigMaps/Secrets placeholders, terraform skeleton for optional infra, and deploy workflow gated with approvals and non-prod defaults.

**Definition of done:** Scripts executable and shellcheck-clean; Dockerfiles build locally; manifests parameterized; deploy workflow guarded (manual approval, branch filters, disabled auto-deploy to prod).

**Verification:** `shellcheck scripts/*.sh`; `docker build` dry-run if allowed; `kubectl kustomize` or `kubeval` optional; `terraform validate` optional; `act -n -W .github/workflows/deploy.yml` if available.

## Iterative self-review loop
1. Generate file(s) using above prompts.
2. Run targeted tests/linters; capture outputs.
3. Self-critique for clarity, safety, and policy alignment; mark gaps.
4. Repeat until file meets acceptance criteria and tests pass; update this plan with evidence links as needed.
