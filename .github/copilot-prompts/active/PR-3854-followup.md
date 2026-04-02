# Session Resumption Prompt — PR #3854 (0D_base_)

> **Purpose:** Paste this entire block as a comment on PR #3854 to resume the
> next Copilot session. Updated after every session until merge.
> **Do NOT use as a post-merge hotfix** — this is for iterating on an open PR.

---

## 🔁 Resumption Command

```
@copilot+claude-sonnet-4.6 Resume CI fixing on PR #3854, branch 0D_base_.

Latest commit: S288 (current HEAD — see git log)
Context file:  .github/copilot-prompts/active/PR-3854-followup.md

Steps:
1. Load .codex/CODEBASE_AGENCY_POLICY.md and stored memories
2. Retrieve latest CI check results on commit 186708b using GitHub MCP tools
3. For each FAILING check: retrieve logs, identify root cause, fix, verify locally
4. For each new rescue comment posted since 186708b: address immediately
5. Run: python scripts/ci/mypy_baseline.py --require-baseline
6. Run: python -m ruff check src/ tests/
7. Run: python -m pytest tests/rag/ -q --tb=short
8. Push fixes via report_progress
9. Update this file (PR-3854-followup.md) with new session summary
10. Post follow-up resumption comment to PR
```

---

## 📍 Current State (as of S288 — see latest commit SHA)

### ✅ Fixed This PR (do NOT re-fix)

| Session | Fix | Files |
|---------|-----|-------|
| S282 | Zip Slip path-traversal fix | `src/codex/skills/compression.py` |
| S282 | OTel OTLP exporter (`_OTLP_PROVIDER_CONFIGURED` → list sentinel) | `src/codex/skills/telemetry.py` |
| S282 | CodeQL: 13 alerts (unused globals, empty excepts, self-import) | Multiple |
| S283 | Self-healing cascade brake (hourly cap ≥10, 30-min dedup) | `iterative-self-healing-ci.yml` |
| S283 | PDA Loop + AfterMath logger (14 patterns) | `scripts/ci/pda_failure_logger.py` |
| S285 | mypy 49→0 via `mypy.manager` skill (11 fix patterns) | 14 source files |
| S285 | actionlint `workflow_name`/`pr_number` outputs wired | `.github/workflows/` |
| S285 | FF section populated with 17 files | `workflow-execution-gate.yml` |
| S286 | mypy 23→0 after CodeQL unused-global/empty-except fixes | `telemetry.py`, `pda_failure_logger.py` |
| S286 | Unused imports removed from `test_mypy_manager.py` | Tests |
| S286 | RP-006: EOF newlines on 112 `.codex/` JSON files | `.codex/*.json` |
| S286 | RP-007: `.secrets.baseline` refreshed | `.secrets.baseline` |
| **S287** | **mypy 50→0: 47 stale `# type: ignore` removed across 21 files** | See list below |
| **S287** | **`importlib.util` attr-defined in `cli_zendesk.py`** | `src/codex/cli_zendesk.py` |
| **S287** | **Pre-commit EOF newlines (3 files)** | `.codex/webhook_*.json`, `PR_LIFECYCLE.md` |
| **S287** | **RAG 10 CI failures: mock chaining + patch targets + RAGIndexer.model** | `src/codex/rag/indexer.py` + 4 test files |
| **S288** | **Validation Pipeline: EOF newlines on 137 .codex JSON files** | `.codex/*.json` (commit 5b82487) |
| **S288** | **`check-shell-true` hook: comment in `compression.py:157` contained `shell=True` text** | `src/codex/skills/compression.py` |

### S287 Files Changed (do not revert)
`src/codex/{auth/github_app.py,cli/main.py,cli_zendesk.py,dynamics/model/sla.py,logging/query_logs.py,rag/indexer.py,security/storage.py,skills/registry.py}` · `src/codex_cli/app.py` · `src/codex_ml/cli/{checkpoint_validate,plugins_cli,tracking_decide,validate}.py` · `src/codex_ml/{config/settings,eval/eval_runner,monitoring/cli,serving/inference_server,utils/checkpoint_core}.py` · `src/ingestion/encoding_detect.py` · `src/integrations/github_app_auth.py` · `src/mcp/server/middleware/auth.py` · `src/services/workflow/parser.py` · `src/tokenization/cli.py` · `tests/rag/{test_device_placement,test_indexer_comprehensive,test_rag_integration,test_retriever_comprehensive}.py`

---

## 🚨 Critical Patterns (avoid re-breaking)

### RAG Mock Pattern
```python
# ALL SentenceTransformer mocks MUST include:
mock.to.return_value = mock
mock.to_empty.return_value = mock
mock.eval.return_value = mock
mock.encode.return_value = np.random.randn(N, 384).astype(np.float32)

# Patch at SOURCE (local import inside function body):
with patch("sentence_transformers.SentenceTransformer", return_value=mock): ...

# Simulate None sentinel (NOT side_effect=ImportError):
with patch("codex.rag.retriever.SentenceTransformer", new=None): ...
```

### mypy `type: ignore` Rule
```
# type: ignore MUST be first comment on line.
# With --ignore-missing-imports + --follow-imports=silent:
#   - [import-untyped] ignores are ALWAYS unused → remove them
#   - [assignment,misc] on `Foo = None` in except blocks → ALWAYS unused → remove
```

### mypy Baseline Verification
```bash
python -m venv /tmp/mypy-ci && \
  /tmp/mypy-ci/bin/pip install -q "mypy>=1.8.0" types-PyYAML types-requests && \
  /tmp/mypy-ci/bin/python scripts/ci/mypy_baseline.py --require-baseline
# .mypy_baseline = 0 — must stay at 0
```

---

## 🎯 Remaining Objectives (open, not yet fixed)

### Cognitive Brain (CB-001 → CB-006)
| ID | Task | Blocker |
|----|------|---------|
| CB-001 | Typer API migration `src/codex_cli/app.py` — `app.group()` → sub-apps | Structural, post-merge preferred |
| CB-002 | Confirm RAG coverage ≥95% gate holds | Verify after CI green on `186708b` |
| CB-003 | actionlint YAML multiline string fixes | 2 workflows outstanding |
| CB-004 | PDA pattern library >14 entries | AfterMath JSONL telemetry input needed |
| CB-005 | `max_concurrency` for `agent.aais.batch` | Implementation |
| CB-006 | Wire `ci.health.analyzer` history → `proactive-ci-monitor.py` | Implementation |

### Merge Gate Checklist
- [x] mypy Baseline green on current HEAD (0 errors locally + 003c452 CI: success)
- [x] PR Comment Review Gate green on 003c452 CI run
- [x] Deferral language gate passes (003c452 CI: success)
- [x] pre-merge-validation.yml (003c452 CI: success)
- [ ] Validation Pipeline / Fast Validation — pre-commit fixes in progress (S288)
- [ ] All required CI checks green on latest commit
- [ ] No open blocking review threads
- [ ] Safety confirmations checked in PR body

---

## 📋 How to Update This File Each Session

At the end of every session, before posting the follow-up comment:
1. Move completed items from "Remaining Objectives" → "Fixed This PR" table
2. Update "Current State" commit hash and session number
3. Add new "Critical Patterns" if a new recurring failure class was discovered
4. Keep "Resumption Command" commit hash current
5. `report_progress` to push the updated file

---
*Last updated: S288 · 2026-04-02 · all pre-commit hooks now passing locally*
