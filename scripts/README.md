# Automation & Utilities (`scripts/`)

**Purpose**: Automation scripts, utilities, and the MCP Package System for ChatGPT Project packaging.

---

## 📁 Structure

```
scripts/
├── mcp/                          # MCP Package System (ChatGPT Projects)
│   ├── mcp-package              # Main CLI tool
│   ├── select_components.py     # Component selection
│   ├── package_flatten.sh       # Flat packaging + manifest
│   ├── topics.json              # Topic definitions
│   └── README.md                # MCP system guide
├── autonomous_agent.py          # Agent orchestrator
├── archive_paths.sh             # Archival utilities
├── refresh_requirements_lock.py # Dependency management
└── space_traversal/             # Repository analysis tools
    └── audit_runner.py          # Audit execution
```

---

## 🚀 Key Systems

### 1. **MCP Package System** (`mcp/`)
Package codebase subsets for ChatGPT Projects.

**Main CLI**: `./scripts/mcp/mcp-package`

**Usage**:
```bash
# List available topics
./scripts/mcp/mcp-package --list

# Package by topic
./scripts/mcp/mcp-package --topic agents

# Custom patterns
./scripts/mcp/mcp-package --custom "agents/**/*.py,tests/agents/**/*.py"

# Dry-run preview
./scripts/mcp/mcp-package --topic mcp --dry-run

# Custom output name
./scripts/mcp/mcp-package --topic docs --output my_docs.zip
```

**Available Topics** (9 total):
1. `zendesk` - Zendesk API integration
2. `agents` - Agent architecture  
3. `quantum` - Quantum game theory
4. `docs` - Documentation
5. `mcp` - MCP system itself
6. `workflows` - CI/CD workflows
7. `python_dev` - Python development methodologies
8. `testing` - TDD patterns
9. `security` - Security patterns

**Output Structure**:
```
package_<topic>.zip
├── manifest.json           # File metadata (SHA256, sizes, paths)
├── README_dataset.md       # Dataset overview
├── index.md               # Quick reference
└── <flat_files>           # src__agents__file.py format
```

**Documentation**:
- [MCP System Overview](mcp/README.md)
- [Quick Start Guide](../docs/mcp/QUICK_START.md)
- [Complete Packaging Guide](../docs/mcp/PACKAGING_GUIDE.md)
- [Advanced Features Roadmap](../docs/mcp/ADVANCED_FEATURES_PLANSET.md)

**GitHub Actions**: `.github/workflows/build-chatgpt-package.yml` (dropdown menu)

### 2. **Autonomous Agent** (`autonomous_agent.py`)
Agent orchestrator for autonomous operations.

**Status**: SAFE_MODE = True (awaiting Genesis Protocol activation)

**Configuration**: `.codex/autonomous_agent.yaml`

**Setup**: [Genesis Setup Guide](../docs/admin/GENESIS_SETUP_GUIDE.md)

### 3. **Space Traversal** (`space_traversal/`)
Repository analysis and audit execution tools.

**Agent Interface**:
```bash
python -m scripts.space_traversal.audit_runner agent-interface --output agent_interface.html
```

**Features**:
- Audit pipeline execution
- Report generation
- ChatGPT 5.1 Agent Mode interface
- Machine-readable outputs

### 4. **Utilities**
Various automation and maintenance scripts.

**Archive Management**: `archive_paths.sh`
- Verify no active references before archiving
- Anti-/tmp/ protection compliance

**Dependency Management**: `refresh_requirements_lock.py`
- Update locked dependencies
- Sync requirements files

---

## 🔧 Development

### Testing MCP System
```bash
# Validate syntax
python -m py_compile scripts/mcp/select_components.py scripts/mcp/mcp-package
bash -n scripts/mcp/package_flatten.sh

# Test packaging
./scripts/mcp/mcp-package --topic mcp --dry-run
./scripts/mcp/mcp-package --topic mcp --output test.zip

# Validate output
unzip -p test.zip manifest.json | jq .
```

### Best Practices
1. **Anti-/tmp/ Protection**: Use `.github/tmp/` instead of `/tmp/`
2. **Shebang Format**: `#! /usr/bin/env python3` (space after #!)
3. **Error Handling**: Catch specific exceptions, preserve KeyboardInterrupt
4. **Cross-Platform**: Test BSD and GNU command variants

---

## 📚 Documentation

### MCP System (93+ KB total)
- [README.md](mcp/README.md) - System overview (9.9 KB)
- [QUICK_START.md](../docs/mcp/QUICK_START.md) - 5-minute guide (8.3 KB)
- [PACKAGING_GUIDE.md](../docs/mcp/PACKAGING_GUIDE.md) - Complete workflows (11.7 KB)
- [PACKAGEABLE_CAPABILITIES.md](../docs/mcp/PACKAGEABLE_CAPABILITIES.md) - Capability transfer (13.5 KB)
- [ChatGPT_Project_SYSTEM_PROMPT.md](../docs/mcp/ChatGPT_Project_SYSTEM_PROMPT.md) - AI prompt (6.3 KB)
- [GENERIC_NAVIGATION_SYSTEM.md](../docs/mcp/GENERIC_NAVIGATION_SYSTEM.md) - Universal navigation (25.5 KB)
- [ADVANCED_FEATURES_PLANSET.md](../docs/mcp/ADVANCED_FEATURES_PLANSET.md) - Roadmap Cycle 1-Phase 3 (Current Cycle) (18.4 KB)

### General
- [Cognitive Map](../docs/system/CODEBASE_COGNITIVE_MAP.md) - Architecture
- [Contributing Guide](../docs/CONTRIBUTING.md) - Development workflow

---

## 🎯 Common Tasks

### Package Code for ChatGPT
```bash
# Quick package
./scripts/mcp/mcp-package --topic agents

# Custom capability package
./scripts/mcp/mcp-package --custom "agents/workflow_navigator.py,tests/agents/test_*.py,docs/agents/*.md" --output workflow_capability.zip
```

### Run Repository Audit
```bash
python -m scripts.space_traversal.audit_runner agent-interface
```

### Update Dependencies
```bash
python scripts/refresh_requirements_lock.py
```

---

## 🚀 Future Features (Cycle 1-Phase 3 (Current Cycle))

Planned MCP enhancements:
1. **Size Estimation** (--estimate flag) - 2-3 days
2. **Exclude Patterns** (--exclude parameter) - 2-3 days
3. **Duplicate Resolution** (hash suffix) - 3-4 days
4. **Package Diff Tool** (compare packages) - 3-4 days
5. **Package Merge Tool** (combine with strategies) - 4-5 days
6. **Interactive Mode** (TUI selector) - 5-7 days
7. **Smart Recommendations** (git analysis) - 3-4 days

See [ADVANCED_FEATURES_PLANSET.md](../docs/mcp/ADVANCED_FEATURES_PLANSET.md) for details.

---

## 🤝 Contributing

See [Contributing Guide](../docs/CONTRIBUTING.md) for development workflow.

---

**Owner**: DevOps + Automation Team  
**Last Updated**: 2025-12-30
