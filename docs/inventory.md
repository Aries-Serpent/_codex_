# Repository File Inventory
> Generated: 2024-11-09  
> Purpose: Comprehensive catalog of files scanned for AGENTS.md creation

| Path | Type | Size (KB) | 1-Line Summary | Priority | Read Depth |
|------|------|-----------|----------------|----------|------------|
| README.md | doc | 13.2 | Offline-first ML repo with reproducible training, schema-validated configs | high | header-only |
| docs/guides/AGENTS.md | doc | 10.0 | Guidelines for contributors and Codex automation | high | full |
| AGENT_CONTINUATION_PROMPT.md | prompt | 10.3 | Agent continuation protocol for S-14, S-15, S-02 implementation | high | full |
| CHATGPT_CONTINUATION.md | prompt | 7.9 | Pagination and resume contract for long responses | high | full |
| _codex_repo_map.json | manifest | 253.0 | Repository file mapping with sizes and categories | high | header-only |
| codex_ready_task_sequence.yaml | orchestration | 6.0 | Offline-first remediation pipeline task sequence | high | full |
| codex_task_executor.py | orchestration | 39.0 | Sequential task block executor with phase management | high | headings |
| codex_task_sequence.py | orchestration | 1.0 | Task sequence helper utilities | medium | full |
| codex_task_report.md | doc | 1.0 | Task execution summary report | medium | header-only |
| CODE_OF_CONDUCT.md | governance | 3.1 | Contributor Covenant Code of Conduct | high | header-only |
| SECURITY.md | governance | 7.9 | Security policies and vulnerability reporting | high | header-only |
| CONTRIBUTING.md | governance | 2.1 | Contribution guidelines | high | header-only |
| .secrets.baseline | security | 719.0 | Detect-secrets baseline for secret scanning | high | header-only |
| .gitignore | config | 3.3 | Git ignore patterns | medium | header-only |
| PROMPTS/CHATGPT_SEARCH_RECIPES.md | prompt | 10.0 | ChatGPT search recipe examples | medium | headings |
| examples/chat_finetune.py | example | 1.1 | Chat finetuning example | medium | full |
| examples/train_toy.py | example | 0.8 | Toy training script | medium | full |
| examples/evaluate_toy.py | example | 0.5 | Toy evaluation script | medium | full |
| examples/tokenize.py | example | 0.6 | Tokenization example | medium | full |
| examples/mlflow_offline.py | example | 4.2 | MLflow offline tracking example | medium | full |
| models/chat_model.py | code | 5.6 | Chat model implementation | medium | headings |
| models/peft_utils.py | code | 1.2 | PEFT (LoRA) utilities | medium | full |
| scripts/codex_ready_task_runner.py | orchestration | est. 5 | Codex task runner script | medium | headings |
| scripts/train.py | code | est. 10 | Training script entrypoint | medium | headings |
| scripts/agent/probe_env.py | code | est. 3 | Environment probe for agent runs | medium | full |
| scripts/env/export_env_json.py | code | est. 2 | Export environment to JSON | low | header-only |
| scripts/space_traversal/audit_runner.py | code | est. 5 | Audit execution runner | medium | headings |
| tools/codex_task_runner.py | orchestration | est. 4 | Codex task CLI runner | medium | headings |
| manifests/codex_eval_rules.v3.json | manifest | 3.7 | Evaluation rules v3 schema | medium | header-only |
| manifests/selection_guard_rules.json | manifest | 0.8 | Selection guard configuration | low | header-only |
| pyproject.toml | config | 8.5 | Python project configuration and dependencies | high | headings |
| noxfile.py | config | 12.2 | Nox automation sessions | medium | headings |
| pytest.ini | config | 0.4 | Pytest configuration | low | header-only |
| Makefile | config | 3.2 | Make targets for common tasks | medium | headings |
| src/codex_ml/ | code | (dir) | ML framework source code | high | (navigate as needed) |
| tests/ | code | (dir) | Test suites | high | (navigate as needed) |
| docs/ | doc | (dir) | Documentation root | high | (navigate as needed) |
| .codex/ | internal | (dir) | Internal codex artifacts and logs | medium | (selective) |
| _codex_/docs/guides/AGENTS.md | doc | 10.0 | Canonical AGENTS guide (same as docs/guides/AGENTS.md) | high | full |
| _codex_/docs/templates/README.md | doc | est. 1 | Template README | low | header-only |

## File Categories Summary

**Orchestration (7 files):**
- codex_ready_task_sequence.yaml
- codex_task_executor.py
- codex_task_sequence.py
- scripts/codex_ready_task_runner.py
- tools/codex_task_runner.py

**Prompts (3 files):**
- AGENT_CONTINUATION_PROMPT.md
- CHATGPT_CONTINUATION.md
- PROMPTS/CHATGPT_SEARCH_RECIPES.md

**Examples (5 files):**
- examples/chat_finetune.py
- examples/train_toy.py
- examples/evaluate_toy.py
- examples/tokenize.py
- examples/mlflow_offline.py

**Governance (3 files):**
- CODE_OF_CONDUCT.md
- SECURITY.md
- CONTRIBUTING.md

**Manifests (3 files):**
- _codex_repo_map.json
- manifests/codex_eval_rules.v3.json
- manifests/selection_guard_rules.json

**Configuration (5 files):**
- pyproject.toml
- noxfile.py
- pytest.ini
- Makefile
- .gitignore

## Variables and Placeholders Discovered

**Environment Variables:**
- CODEX_ENV_PYTHON_VERSION
- CODEX_ENV_NODE_VERSION
- CODEX_SESSION_ID
- CODEX_SESSION_LOG_DIR
- CODEX_LOG_DB_PATH
- CODEX_SQLITE_POOL
- ACCELERATE_TEST
- RUN_LORA_TESTS
- RUN_PERF_SMOKE
- SKIP_OPTIONAL
- FAIL_ON_MISSING
- PYTEST_DISABLE_PLUGIN_AUTOLOAD

**Template Placeholders:**
- {logs_dir}
- {reports_dir}
- {seed}
- {API_KEY}
- {model}
- {i}/{N} (chunk pagination)
- {section}
- {t} (token count)

## Priority Wavepoints

1. **Entry** → README.md (quick orientation)
2. **Agent Guide** → docs/guides/AGENTS.md (canonical agent instructions)
3. **Continuation** → AGENT_CONTINUATION_PROMPT.md (resume protocol)
4. **Orchestration** → codex_ready_task_sequence.yaml (task pipeline)
5. **Executor** → codex_task_executor.py (execution engine)
6. **Map** → _codex_repo_map.json (file inventory)
7. **Prompts** → PROMPTS/ (prompt templates)
8. **Examples** → examples/ (runnable code)
9. **Governance** → CODE_OF_CONDUCT.md, SECURITY.md (policies)
10. **Config** → pyproject.toml, noxfile.py (build/test setup)

## Files Flagged as MISSING

*(None - all listed files exist)*

## Large Files (>50KB) - Header Only

- _codex_repo_map.json (253 KB) - JSON file mapping
- .secrets.baseline (719 KB) - Detect-secrets baseline

## Notes

- All paths validated to exist
- No secret patterns detected in scanned content
- Prompts are < 4k tokens (largest ~10KB)
- Repository uses offline-first approach
- GitHub Actions workflow creation is prohibited
