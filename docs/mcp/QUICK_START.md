# MCP Package System - Quick Start Guide

**Get started in 5 minutes** with packaging your codebase for ChatGPT Projects.

---

## What is MCP Package System?

The MCP (Model Context Protocol) Package System lets you package any part of your codebase into a flat-structure archive optimized for ChatGPT Project uploads. Package by topic, capability, or custom file selection.

---

## Prerequisites

- Python 3.8+
- Bash
- `jq` (for validation)
- `zip` utility

---

## Quick Start: Create Your First Package

### Step 1: List Available Topics

```bash
cd /path/to/_codex_
./scripts/mcp/mcp-package --list
```

**Output**: See all 9 predefined topics (zendesk, agents, quantum, docs, mcp, workflows, python_dev, testing, security)

### Step 2: Preview a Package (Dry-Run)

```bash
./scripts/mcp/mcp-package --topic mcp --dry-run
```

**Output**: List of files that would be included (no package created)

### Step 3: Create a Package

```bash
./scripts/mcp/mcp-package --topic mcp
```

**Output**: `package_mcp_20251230.zip` created and validated

### Step 4: Validate the Package

```bash
# Check contents
unzip -l package_mcp_*.zip

# Inspect manifest
unzip -p package_mcp_*.zip manifest.json | jq .

# Verify file count
unzip -p package_mcp_*.zip manifest.json | jq '.files | length'
```

**Expected**: Valid JSON manifest with file metadata (SHA256, sizes, paths)

### Step 5: Upload to ChatGPT Project

1. Go to ChatGPT (chatgpt.com)
2. Create or open a Project
3. Click "Add files" or drag-and-drop the zip file
4. ChatGPT extracts and indexes automatically

### Step 6: Use the System Prompt

Copy the system prompt from `docs/mcp/ChatGPT_Project_SYSTEM_PROMPT.md` and paste into your ChatGPT Project instructions.

**Test it**:
```
User: "What files are in this dataset?"
User: "Where is the packaging guide?"
User: "Explain the MCP package system"
```

---

## Common Use Cases

### Use Case 1: Package MCP Documentation

```bash
./scripts/mcp/mcp-package --topic mcp --output mcp_docs.zip
```

**Result**: All MCP system documentation and tools (~24 files, ~0.1 MB)

### Use Case 2: Package Agent Implementations

```bash
./scripts/mcp/mcp-package --topic agents --output agents_code.zip
```

**Result**: All agent code, tests, and docs (~61 files, ~0.2 MB)

### Use Case 3: Package Specific Files (Custom)

```bash
./scripts/mcp/mcp-package \
  --custom "agents/workflow_navigator.py,agents/quantum_game_theory.py,tests/agents/test_*.py" \
  --output capability_workflow.zip
```

**Result**: Only the specified files and matching patterns

### Use Case 4: Package Testing Methodology

```bash
./scripts/mcp/mcp-package --topic testing --output testing_guide.zip
```

**Result**: All tests, pytest config, and testing docs (~1,600+ files)

---

## Via GitHub Actions (No CLI Required)

### Step 1: Navigate to Actions

Go to your repository → **Actions** tab → **Build ChatGPT Project Package**

### Step 2: Run Workflow

Click "Run workflow" and select:
- **Topic**: Choose from dropdown (e.g., "agents")
- **Glob filters**: (optional) Override topic with custom patterns
- **Output name**: (optional) Custom filename

### Step 3: Download Artifact

After workflow completes, download the artifact from the workflow run page.

---

## Command Reference

### Basic Commands

```bash
# List all topics
./scripts/mcp/mcp-package --list

# Package a topic
./scripts/mcp/mcp-package --topic <name>

# Custom package
./scripts/mcp/mcp-package --custom "pattern1,pattern2,..."

# Dry-run preview
./scripts/mcp/mcp-package --topic <name> --dry-run

# Custom output name
./scripts/mcp/mcp-package --topic <name> --output my_package.zip

# Verbose output
./scripts/mcp/mcp-package --topic <name> --verbose
```

### Available Topics

| Topic | Description | Typical Files | Size |
|-------|-------------|---------------|------|
| **zendesk** | Zendesk API integration | ~50-100 | 5-10 MB |
| **agents** | Agent architecture | ~60+ | 15-25 MB |
| **quantum** | Quantum game theory | ~30-80 | 3-8 MB |
| **docs** | All documentation | ~100-200 | 2-5 MB |
| **mcp** | MCP system itself | ~24 | 0.1-0.2 MB |
| **workflows** | CI/CD workflows | ~100-150 | 5-10 MB |
| **python_dev** | Python methodologies | ~5 | <1 MB |
| **testing** | TDD patterns | ~1,600+ | 20-30 MB |
| **security** | Security patterns | ~10-20 | 1-2 MB |

---

## Package Structure

Every package includes:

```
package_<topic>.zip
├── manifest.json           # File metadata and mappings
├── README_dataset.md       # Dataset overview
├── index.md               # Quick reference table
└── <flat_files>           # src__module__file.py format
```

### Manifest Fields

```json
{
  "version": "1.0",
  "generated_at": "2024-12-30T17:00:00Z",
  "repository": "Aries-Serpent/_codex_",
  "files": [
    {
      "flat_name": "src__agents__workflow.py",
      "original_path": "src/agents/workflow.py",
      "sha256": "abc123...",
      "size_bytes": 12345,
      "language": "python",
      "tags": "agents,source",
      "chunked": false
    }
  ],
  "total_files": 24,
  "total_size_bytes": 123456
}
```

---

## Troubleshooting

### Issue: Package Too Large (>50 MB)

**Solution**: Use more specific topic or custom filters

```bash
# Instead of "testing" (1,600+ files)
./scripts/mcp/mcp-package --custom "tests/agents/**/*.py"
```

### Issue: No Files Selected

**Cause**: Glob patterns didn't match any files

**Solution**: Test pattern first
```bash
find . -path "your/pattern/**"
```

### Issue: Workflow Fails with "custom topic but no glob_filters"

**Solution**: Select a predefined topic OR provide glob_filters with custom

```yaml
# Correct
topic: agents

# OR

topic: custom
glob_filters: "agents/**,tests/agents/**"
```

### Issue: Invalid Manifest JSON

**Solution**: Check with jq
```bash
unzip -p package.zip manifest.json | jq .
```

If invalid, re-run packaging command.

---

## Best Practices

### 1. Start with Predefined Topics

Use `--list` to see available topics. They're optimized for common use cases.

### 2. Use Dry-Run First

Always preview with `--dry-run` before creating large packages.

### 3. Keep Packages Small

Target <30 MB for optimal ChatGPT performance. Split large topics if needed.

### 4. Name Packages Descriptively

```bash
# Good
--output agents_workflow_2025-12-30.zip

# Avoid
--output package.zip
```

### 5. Validate Before Upload

Always check manifest and file count before uploading to ChatGPT.

---

## Next Steps

### Learn More

- **Full Guide**: [PACKAGING_GUIDE.md](PACKAGING_GUIDE.md)
- **Capabilities**: [PACKAGEABLE_CAPABILITIES.md](PACKAGEABLE_CAPABILITIES.md)
- **System Prompt**: [ChatGPT_Project_SYSTEM_PROMPT.md](ChatGPT_Project_SYSTEM_PROMPT.md)
- **Navigation**: [GENERIC_NAVIGATION_SYSTEM.md](GENERIC_NAVIGATION_SYSTEM.md)

### Advanced Usage

- Create custom topics in `scripts/mcp/topics.json`
- Package multiple related capabilities together
- Use workflow automation for scheduled packaging
- Generate navigation indexes for full codebase packages

### Get Help

- Check [scripts/mcp/README.md](../../scripts/mcp/README.md) for system overview
- Review test results in `.github/tmp/package_test_results.md`
- See examples in [PACKAGING_GUIDE.md](PACKAGING_GUIDE.md)

---

## Examples

### Example 1: Quick MCP System Package

```bash
# One command to package entire MCP system
./scripts/mcp/mcp-package --topic mcp

# Upload to ChatGPT, use system prompt, done!
```

### Example 2: Capability-Focused Package

```bash
# Package workflow navigation capability
./scripts/mcp/mcp-package \
  --custom "agents/workflow_navigator.py,agents/mental_mapping.py,tests/agents/test_workflow*.py,docs/agents/*workflow*.md" \
  --output workflow_capability.zip
```

### Example 3: Documentation Only

```bash
# Package all docs for offline reference
./scripts/mcp/mcp-package --topic docs --output codex_docs.zip
```

### Example 4: Automated via Workflow

1. Go to Actions → Build ChatGPT Project Package
2. Select topic: "agents"
3. Click "Run workflow"
4. Download artifact when complete

---

**Ready to start?** Run `./scripts/mcp/mcp-package --list` to see available topics!

**Questions?** Check the [full packaging guide](PACKAGING_GUIDE.md) or [FAQ](MCP_FAQ.md).

---

**Last Updated**: 2024-12-30  
**Version**: 1.0  
**Status**: Production Ready ✅
