# AGENTS — Super-Agent Entrypoint
> Quick-start pointer to canonical AGENTS guide for GitHub Copilot and ChatGPT agents.
> **Last Updated:** 2025-11-09

---

## 📖 Canonical Documentation

**👉 For the complete Super-Agent guide, see:**  
**[_codex_/AGENTS.md](_codex_/AGENTS.md)** ← Comprehensive wavepoints, use rules, orchestration map

**📋 For the machine-readable manifest, see:**  
**[_codex_/codex_index.yaml](_codex_/codex_index.yaml)** ← Primary files, summaries, priorities

---

## ⚡ Priority Files (Read First)

1. **[docs/guides/AGENTS.md](docs/guides/AGENTS.md)** — Canonical agent guidelines, environment variables, tooling
2. **[AGENT_CONTINUATION_PROMPT.md](AGENT_CONTINUATION_PROMPT.md)** — Continuation protocol for multi-step tasks
3. **[codex_ready_task_sequence.yaml](codex_ready_task_sequence.yaml)** — Offline-first task pipeline
4. **[_codex_repo_map.json](_codex_repo_map.json)** — Complete file inventory and mappings
5. **[README.md](README.md)** — Repository overview and quick links

## 🎯 Common Tasks

### Run Tests
```bash
nox -s tests
pytest -m "not integration"  # Exclude integration tests
```

### Build Documentation
```bash
nox -s docs_build
# Or skip optional ML modules:
SKIP_OPTIONAL=1 nox -s docs_build
```

### Generate Status Update
```bash
# Generate comprehensive JSON status report
codex-status-audit --generate
# Or directly:
python tools/generate_status_update.py
```

### Format & Lint
```bash
pre-commit run --all-files
black src/ tests/
ruff check src/ tests/
```

### Execute Task Sequence
```bash
python codex_task_executor.py
```

## 🔒 Safety Rules

- ❌ **DO NOT** create or enable GitHub Actions workflows
- ❌ **DO NOT** make network calls (offline-first repo)
- ✅ **DO** check `.secrets.baseline` before committing
- ✅ **DO** keep automation artifacts in `.codex/`
- ✅ **DO** use deterministic seeds and offline-first approaches

## 📂 Directory Structure

```
_codex_/
├── docs/guides/AGENTS.md          ← Canonical agent guide
├── AGENT_CONTINUATION_PROMPT.md   ← Continuation protocol
├── codex_ready_task_sequence.yaml ← Task pipeline
├── codex_task_executor.py         ← Orchestration engine
├── PROMPTS/                        ← Prompt templates
├── examples/                       ← Runnable examples
├── src/codex_ml/                   ← ML framework
├── tests/                          ← Test suites
└── .codex/                         ← Internal artifacts
```

## 🔗 Key Manifests

- **[_codex_/codex_index.yaml](_codex_/codex_index.yaml)** — Primary file index with summaries
- **[_codex_repo_map.json](_codex_repo_map.json)** — Complete file mapping
- **[manifests/codex_eval_rules.v3.json](manifests/codex_eval_rules.v3.json)** — Evaluation rules
- **[inventory.md](inventory.md)** — File catalog with priorities
- **[schemas/codex_status_update.schema.json](schemas/codex_status_update.schema.json)** — Status update schema (v1.2)
- **[.codex/status/](. codex/status/)** — Generated status update reports

## 🧭 Navigation Wavepoints

| Wavepoint | Path | Read Depth | Purpose |
|-----------|------|------------|---------|
| **Entry** | README.md | Header (300 chars) | Quick orientation |
| **Agent Guide** | docs/guides/AGENTS.md | Full | Canonical instructions |
| **Continuation** | AGENT_CONTINUATION_PROMPT.md | Full | Multi-step protocol |
| **Orchestration** | codex_ready_task_sequence.yaml | Full | Task pipeline |
| **Executor** | codex_task_executor.py | Headings | Execution engine |
| **Prompts** | PROMPTS/ | Headers | Prompt templates |
| **Examples** | examples/ | Full (small files) | Runnable code |
| **Governance** | CODE_OF_CONDUCT.md, SECURITY.md | Headers | Policies |

## 🛡️ Governance

- **[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)** — Community standards
- **[SECURITY.md](SECURITY.md)** — Security policies and vulnerability reporting
- **[CONTRIBUTING.md](CONTRIBUTING.md)** — Contribution guidelines

---

**For comprehensive details, wavepoint explanations, orchestration maps, and validation checklists:**  
**📖 See [docs/guides/AGENTS.md](docs/guides/AGENTS.md)**
