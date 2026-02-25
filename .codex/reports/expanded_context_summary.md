# Expanded Context Audit Summary

## Overview

- Total files scanned: 2951
- Features detected: 11
- Features complete (≥75%): 9

## Detected Features

- ✅ **vectorstore** (Score: 75/100, Files: 33)
  - `scripts/expanded_context_audit.py`
  - `scripts/space_traversal/detectors/vector_store_detector.py`
  - `src/codex/agents/memory/protocol.py`
  - ... and 30 more
- ✅ **embeddings** (Score: 100/100, Files: 14)
  - `scripts/expanded_context_audit.py`
  - `src/codex/retrieval/__init__.py`
  - `src/codex/retrieval/embed.py`
  - ... and 11 more
- ✅ **rag** (Score: 75/100, Files: 779)
  - `.codex/ai_agent_toolkit.py`
  - `.codex/codex_repo_scout.py`
  - `.codex/run_db_utils_workflow.py`
  - ... and 776 more
- ✅ **session_logging** (Score: 75/100, Files: 65)
  - `.codex/run_db_utils_workflow.py`
  - `.codex/run_workflow.py`
  - `.codex/smoke/import_check.py`
  - ... and 62 more
- ❌ **copilot_bridge** (Score: 25/100, Files: 2)
  - `scripts/expanded_context_audit.py`
  - `src/bridge_manager.py`
- ✅ **retriever** (Score: 75/100, Files: 84)
  - `agents/codex_client/codex_client/bridge.py`
  - `agents/interpretability/__init__.py`
  - `agents/interpretability/sparse_probes.py`
  - ... and 81 more
- ✅ **indexer** (Score: 75/100, Files: 28)
  - `scripts/analytics/openai_usage_dashboard.py`
  - `scripts/cognitive/collect_git_data.py`
  - `scripts/cognitive/model_retraining_automation.py`
  - ... and 25 more
- ✅ **summarization** (Score: 75/100, Files: 413)
  - `.codex/ai_agent_toolkit.py`
  - `.codex/codex_repo_scout.py`
  - `.codex/run_repo_scout.py`
  - ... and 410 more
- ✅ **provenance** (Score: 75/100, Files: 58)
  - `scripts/env/print_env_info.py`
  - `scripts/environment_snapshot.py`
  - `scripts/expanded_context_audit.py`
  - ... and 55 more
- ✅ **subagent_orchestrator** (Score: 75/100, Files: 167)
  - `agents/__init__.py`
  - `agents/advanced_physics_calculators.py`
  - `agents/agent_memory.py`
  - ... and 164 more
- ⚠️ **cache** (Score: 50/100, Files: 3)
  - `scripts/expanded_context_audit.py`
  - `src/codex/cli_archive.py`
  - `src/codex_bridge/github_client.py`

## Missing/Partial Areas (Prioritized)

### P1 Priority

- **copilot_bridge** (Score: 25/100, Files: 2)

## Recommendations
