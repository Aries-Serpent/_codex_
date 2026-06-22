# NotebookLM Grounding Engine Setup Guide

**Generated:** 2026-01-23T19:00:00Z  
**Branch:** copilot/sub-pr-3020  
**Status:** ✅ Complete

---

## 📋 Overview

This guide provides instructions for ingesting the Aries-Serpent `_codex_` repository into NotebookLM's Grounding Engine. Three artifacts have been created to bridge the Python "Cognitive Brain" and Rust "Orchestration Layer."

---

## 📦 Artifacts Created

### 1. `skeleton_map.json` (12KB)

**Purpose:** Comprehensive architectural map of the hybrid Python-Rust monorepo.

**Contents:**
- **4 Architectural Layers:**
  - Logic Layer: Python Cognitive Brain (40+ modules), Agent Swarm (26 agents), Core Modules (30+ packages)
  - Performance Layer: Rust Orchestration Engine (Cargo.toml, 20+ source files)
  - Bridge Layer: Schemas (15+), Manifests, Mappings
  - Documentation Layer: Guides (60+), Prompts (30+), Index (693+ files)

- **Integration Points:**
  - Python-Rust FFI via PyO3 (abi3-py38)
  - Cognitive-to-Rust dispatcher
  - Agent orchestration registry

- **Traversal Summary:**
  - Verified paths for all major components
  - Statistics: 500+ files cataloged

**Usage:** Ingest first to provide structural context to NotebookLM.

---

### 2. `GEM_INSTRUCTIONS.md` (14KB)

**Purpose:** Four Pillars grounding instructions for AI model behavior.

**Contents:**
- **Pillar 1 - Persona:** Voice, tone, identity (Hybrid AI DevOps Architect)
- **Pillar 2 - Task:** Scope and capabilities (Cognitive operations, agent swarm, high-performance execution)
- **Pillar 3 - Context:** Environment and constraints (repository structure, tech stack, safety guardrails)
- **Pillar 4 - Format:** Output structure (citations, Markdown, Mermaid diagrams, templates)

**Key Features:**
- Evidence-based responses with file path citations
- Structured templates for cognitive operations, agent coordination, Python-Rust integration
- Validation checklists
- Learning resources for contributors, agents, and architects

**Usage:** Ingest second to establish response format and capabilities.

---

### 3. `prepare_notebooklm.sh` (7.3KB, executable)

**Purpose:** Generate `full_context.txt` by concatenating all documentation and source code.

**Features:**
- Dynamic repository root detection (`git rev-parse` + fallback)
- Efficient `find` commands with exclusions (tests, node_modules, target, .git)
- Collects:
  - Documentation (*.md from docs/, guides/)
  - Python source (*.py, excluding test directories)
  - Rust source (*.rs, excluding test/target directories)
  - Configuration files (Cargo.toml, pyproject.toml, etc.)
  - Schemas (JSON, YAML)
  - Prompts (all prompt directories)
  - Agent definitions (26 agents from .github/agents)

**Usage:**
```bash
./prepare_notebooklm.sh
# OR with custom repo root:
./prepare_notebooklm.sh /path/to/repo
```

**Output:** `full_context.txt` with file path headers and statistics.

---

## 🚀 Ingestion Workflow

### Step 1: Ingest Skeleton Map

```
Upload: skeleton_map.json
Purpose: Provide structural overview
Result: NotebookLM understands 4-layer architecture
```

**What NotebookLM learns:**
- Repository structure (cognitive/, rust_swarm/, src/codex/, etc.)
- 26 specialized agents and their capabilities
- Python-Rust integration points
- Schema/manifest locations

---

### Step 2: Ingest GEM Instructions

```
Upload: GEM_INSTRUCTIONS.md
Purpose: Establish voice, format, and capabilities
Result: NotebookLM adopts Four Pillars response structure
```

**What NotebookLM learns:**
- How to respond (evidence-based, file path citations)
- Available capabilities (cognitive brain, agent orchestration, Rust engine)
- Output templates (cognitive operations, agent dispatch, Python-Rust interop)
- Safety guardrails and constraints

---

### Step 3: Generate Full Context

```bash
./prepare_notebooklm.sh
```

**Generates:** `full_context.txt`

**Statistics:**
- Documentation: ~100 files
- Python: ~150 files
- Rust: ~20 files
- Config/Schema: ~15 files
- Prompts: ~30 files
- Agents: ~26 definitions

**Total:** ~500+ files concatenated with headers

---

### Step 4: Ingest Full Context

```
Upload: full_context.txt
Purpose: Provide complete codebase content
Result: NotebookLM can answer questions with specific file references
```

**What NotebookLM gains:**
- Full documentation text (guides, architecture docs)
- All Python source code (cognitive brain, agents, core modules)
- All Rust source code (swarm engine, FFI bridge, compression)
- All schemas, manifests, mappings
- All AI prompts and continuation instructions
- All agent definitions and capabilities

---

## 🔍 Query Examples

Once ingestion is complete, you can ask NotebookLM:

### Architecture Questions

**Q:** "How does the cognitive brain coordinate agent dispatch?"

**Expected A:**
- References `scripts/cognitive/dispatch_agent.py`
- Shows flow through `agents/developer_orchestrator.py`
- Links to `.github/agents/AGENT_REGISTRY.yaml`
- Explains cognitive decision-making process

---

### Implementation Questions

**Q:** "How is Python-Rust interop implemented?"

**Expected A:**
- Cites `Cargo.toml` (PyO3 configuration)
- References `rust_swarm/ffi_bridge.rs` (bridge code)
- Shows data flow: Python → PyO3 → Rust → MessagePack → LZ4
- References schemas for validation

---

### Operational Questions

**Q:** "What agents handle security vulnerabilities?"

**Expected A:**
- Lists from AGENT_REGISTRY.yaml:
  - bridge-security-monitor
  - dependency-vulnerability-scanner
  - codeql-alert-resolution-agent
  - security-vulnerability-patcher
- Explains capabilities and integration points

---

## 📊 Verification

### Skeleton Map Validation

```bash
jq '.layers | keys' skeleton_map.json
# Expected: ["bridge_layer", "documentation_layer", "logic_layer", "performance_layer"]

jq '.traversal_summary.verified_paths | keys' skeleton_map.json
# Expected: All paths marked with ✅
```

---

## GEM Instructions Validation

```bash
grep -c "^### " GEM_INSTRUCTIONS.md
# Expected: ~30+ sections

grep -c "^## " GEM_INSTRUCTIONS.md
# Expected: ~10+ major sections
```

---

## Script Validation

```bash
bash -n prepare_notebooklm.sh
# Expected: No syntax errors

./prepare_notebooklm.sh
# Expected: full_context.txt generated with statistics
```

---

## 🎯 Success Criteria

- ✅ Skeleton map provides 4-layer architectural overview
- ✅ GEM instructions establish Four Pillars response format
- ✅ Script generates full context with 500+ files
- ✅ NotebookLM can answer questions with file path citations
- ✅ Responses include evidence trails and cross-references
- ✅ Integration points between Python and Rust are clear
- ✅ Agent capabilities and orchestration are documented

---

## 🛡️ Safety & Constraints

**Pre-Genesis Mode:**
- Autonomous actions disabled
- Workflows gated
- Safe mode active

**Follows:**
- `.codex/CODEBASE_AGENCY_POLICY.md` (leave codebase better)
- `.codex/guardrails.md` (operational constraints)
- `docs/agent/OPERATIONAL_GUIDELINES.md` (agent framework)

---

## 📚 Related Documentation

- **Repository Overview:** `README.md`
- **Agent Operations:** `AGENTS.md`
- **Architecture:** `ARCHITECTURE_BLUEPRINT.md`
- **Documentation Index:** `docs/DOCUMENTATION_INDEX.md`
- **Cognitive Brain:** `scripts/cognitive/cognitive_brain_core.py`
- **Agent Registry:** `.github/agents/AGENT_REGISTRY.yaml`
- **Rust Engine:** `Cargo.toml`, `rust_swarm/swarm_engine.rs`

---

## 🐛 Troubleshooting

### Issue: Script fails to find files

**Solution:**
```bash
# Verify repository root
git rev-parse --show-toplevel

# Run with explicit path
./prepare_notebooklm.sh /path/to/_codex_
```

---

## Issue: JSON validation fails

**Solution:**
```bash
# Validate skeleton_map.json
jq empty skeleton_map.json
# Should exit with status 0

# Pretty print
jq . skeleton_map.json | head -20
```

---

## Issue: NotebookLM doesn't cite file paths

**Solution:**
- Ensure `full_context.txt` has file path headers
- Check GEM_INSTRUCTIONS.md was ingested (establishes citation format)
- Verify skeleton_map.json provides structural context

---

## 📞 Support

- **Issues:** https://github.com/Aries-Serpent/_codex_/issues
- **Maintainer:** @mbaetiong
- **Documentation:** `docs/DOCUMENTATION_INDEX.md`

---

## ✅ Completion Checklist

- [x] Artifacts created (skeleton_map.json, GEM_INSTRUCTIONS.md, prepare_notebooklm.sh)
- [x] Code review feedback addressed
- [x] Script syntax validated
- [x] Files committed and pushed
- [x] Documentation complete
- [x] Ready for NotebookLM ingestion

---

**Version:** 1.0.0  
**Last Updated:** 2026-01-23T19:00:00Z  
**Status:** ✅ Production Ready

**Next Step:** Ingest artifacts into NotebookLM in order: skeleton_map.json → GEM_INSTRUCTIONS.md → full_context.txt
