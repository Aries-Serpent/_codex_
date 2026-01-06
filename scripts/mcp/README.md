# MCP Package System - ChatGPT Project Packager

**Purpose**: Repeatable, user-friendly system for packaging any part of the _codex_ codebase for ChatGPT Project use.

## Quick Start

```bash
# List available topics
./scripts/mcp/mcp-package --list

# Package a topic
./scripts/mcp/mcp-package --topic zendesk

# Package with custom filters
./scripts/mcp/mcp-package --custom "src/agents/**/*.py,tests/agents/**/*.py"

# Dry run to preview
./scripts/mcp/mcp-package --topic agents --dry-run
```

## System Components

### 1. User Interface
- **`scripts/mcp/mcp-package`** - Main CLI for Human Admin
  - User-friendly commands
  - Automatic validation
  - Clear progress feedback
  - Helpful error messages

### 2. Core Tools
- **`scripts/mcp/select_components.py`** - File selection by topic or glob
- **`scripts/mcp/package_flatten.sh`** - Flattening and manifest generation
- **`scripts/mcp/topics.json`** - Topic definitions

### 3. Automation
- **`.github/workflows/build-chatgpt-package.yml`** - GitHub Actions workflow
  - Workflow dispatch with inputs
  - Automated validation
  - Artifact upload

### 4. Documentation
- **`docs/mcp/PACKAGING_GUIDE.md`** - Comprehensive packaging guide
- **`docs/mcp/ChatGPT_Project_SYSTEM_PROMPT.md`** - Assistant system prompt template

## Architecture

```
Human Admin Request
        ↓
    mcp-package CLI
        ↓
    ┌─────────────────┐
    │ 1. Select Files │ → select_components.py
    └─────────────────┘
        ↓
    ┌─────────────────┐
    │ 2. Stage Files  │ → Copy to temp directory
    └─────────────────┘
        ↓
    ┌─────────────────┐
    │ 3. Flatten      │ → package_flatten.sh
    │    + Manifest   │    - Flatten paths
    │                 │    - Generate manifest.json
    │                 │    - Create README & index
    └─────────────────┘
        ↓
    ┌─────────────────┐
    │ 4. Validate     │ → Check manifest & size
    └─────────────────┘
        ↓
    package_<topic>_<date>.zip
        ↓
    ChatGPT Project Upload
```

## Usage Examples

### For Human Admin

#### Example 1: Package Zendesk Integration
```bash
./scripts/mcp/mcp-package --topic zendesk
# Output: package_zendesk_20251230.zip
```

#### Example 2: Package Specific Agent with Tests
```bash
./scripts/mcp/mcp-package \
    --custom "agents/workflow_navigator.py,agents/quantum_game_theory.py,tests/agents/test_*.py" \
    --output agent_core.zip
```

#### Example 3: Preview Before Packaging
```bash
./scripts/mcp/mcp-package --topic agents --dry-run
# Shows list of files without creating archive
```

#### Example 4: Package All Documentation
```bash
./scripts/mcp/mcp-package --topic docs --verbose
```

#### Example 5: Package MCP System Itself
```bash
./scripts/mcp/mcp-package --topic mcp
# Creates self-contained MCP documentation package
```

### Via GitHub Actions

1. Go to Actions tab
2. Select "Build ChatGPT Project Package"
3. Click "Run workflow"
4. Fill in:
   - **topic**: Choose from dropdown
   - **glob_filters**: (optional) Custom overrides
   - **output_name**: (optional) Custom filename
5. Download artifact when complete

## Repeatable Process Documentation

### Standard Operating Procedure

#### Process 1: Ad-hoc Package Request

**When**: Human Admin needs specific code subset for ChatGPT analysis

**Steps**:
1. Identify what to package:
   - Use predefined topic? → `--topic <name>`
   - Need custom selection? → `--custom "<globs>"`

2. Preview (optional):
   ```bash
   ./scripts/mcp/mcp-package --topic <name> --dry-run
   ```

3. Create package:
   ```bash
   ./scripts/mcp/mcp-package --topic <name>
   ```

4. Validate locally:
   ```bash
   unzip -l package_<topic>_<date>.zip
   unzip -p package_<topic>_<date>.zip manifest.json | jq .
   ```

5. Upload to ChatGPT Project

6. Use system prompt from `docs/mcp/ChatGPT_Project_SYSTEM_PROMPT.md`

**Expected Time**: 2-5 minutes

#### Process 2: Scheduled Topic Packaging

**When**: Regular updates of common topics (e.g., weekly agents package)

**Steps**:
1. Run via GitHub Actions or cron:
   ```bash
   ./scripts/mcp/mcp-package --topic agents --output agents_weekly.zip
   ```

2. Archive in designated location:
   ```bash
   mv agents_weekly.zip misc/mcp-packages/$(date +%Y-%m-%d)/
   ```

3. Update ChatGPT Project with new version

**Expected Time**: Automated, 5-10 minutes

#### Process 3: New Topic Definition

**When**: Need to package new category not in predefined topics

**Steps**:
1. Identify patterns needed:
   ```bash
   # Example: New "security" topic
   find . -path "*security*" -o -name "*auth*" -o -name "*crypto*"
   ```

2. Add to `scripts/mcp/topics.json`:
   ```json
   "security": [
     "src/security/**",
     "agents/*auth*.py",
     "tests/security/**",
     "docs/**/*security*"
   ]
   ```

3. Test new topic:
   ```bash
   ./scripts/mcp/mcp-package --topic security --dry-run
   ```

4. Package:
   ```bash
   ./scripts/mcp/mcp-package --topic security
   ```

5. Document in PACKAGING_GUIDE.md

**Expected Time**: 10-15 minutes

## Predefined Topics

| Topic | Description | Typical Size | Use Case |
|-------|-------------|--------------|----------|
| **zendesk** | Zendesk integration | 5-10 MB | API development, troubleshooting |
| **agents** | All agent systems | 15-25 MB | Agent architecture review |
| **quantum** | Quantum game theory | 3-8 MB | Advanced physics analysis |
| **docs** | All documentation | 2-5 MB | Documentation review/generation |
| **mcp** | MCP packaging system | 1-2 MB | Meta-documentation |
| **workflows** | CI/CD & GitHub Actions | 5-10 MB | Workflow optimization |

## Best Practices

### 1. Topic Selection
- **Start with predefined topics** for common use cases
- **Use custom globs** for one-off requests
- **Define new topics** if pattern repeats 3+ times

### 2. Size Management
- **Target: < 30 MB** for optimal ChatGPT performance
- **Hard limit: < 50 MB** (ChatGPT recommendation)
- **If too large**: Split into multiple packages or filter more

### 3. Naming Convention
```
package_<topic>_<YYYYMMDD>[_<variant>].zip

Examples:
- package_zendesk_20251230.zip
- package_agents_20251230_core.zip
- package_custom_20251230_142530.zip
```

### 4. Validation Checklist
- [ ] Manifest is valid JSON
- [ ] No duplicate flat names
- [ ] All required files present (manifest.json, README_dataset.md, index.md)
- [ ] Size within limits (< 50 MB)
- [ ] SHA256 hashes computed for all files

### 5. Documentation Trail
- **Record what was packaged**: Topic or custom filters used
- **Record when**: Date and commit SHA
- **Record why**: Purpose of package
- **Store metadata**: In package README or external log

## Integration Points

### With CI/CD
```yaml
# In other workflows, trigger package creation
- name: Create diagnostic package
  uses: ./.github/workflows/build-chatgpt-package.yml
  with:
    topic: agents
    output_name: debug_agents.zip
```

### With Issue Templates
```markdown
### Code Review Request
To package relevant code for ChatGPT review:
\`\`\`bash
./scripts/mcp/mcp-package --custom "path/to/code/**,tests/path/**"
\`\`\`
```

### With Documentation
```markdown
### Deep Dive: Agent Architecture
Download pre-packaged subset:
[package_agents_latest.zip](link)

Or create fresh package:
\`\`\`bash
./scripts/mcp/mcp-package --topic agents
\`\`\`
```

## Troubleshooting

### Issue: "Package too large"
**Solution**: Use custom filters to narrow scope
```bash
./scripts/mcp/mcp-package --custom "src/agents/workflow*.py"
```

### Issue: "Duplicate flat names"
**Cause**: Two files with same name in different directories

**Solution**: Check manifest for duplicates
```bash
unzip -p package.zip manifest.json | jq -r '.files[].flat_name' | sort | uniq -d
```

If found, this is currently a known limitation. Workaround:
1. Exclude one of the duplicate files using more specific globs
2. Or manually rename in staging (enhancement needed in package_flatten.sh)

### Issue: "Topic not found"
**Solution**: Check available topics
```bash
./scripts/mcp/mcp-package --list
```

### Issue: "No files selected"
**Cause**: Glob patterns didn't match any files

**Solution**: Test patterns
```bash
# Test glob pattern
python scripts/mcp/select_components.py \
    --custom "your/pattern/**" \
    --output /tmp/test.txt
cat /tmp/test.txt
```

## Maintenance

### Regular Tasks

**Weekly**:
- [ ] Review package sizes for growth trends
- [ ] Check if new topics are needed (recurring custom patterns)

**Monthly**:
- [ ] Update topics.json if codebase structure changed
- [ ] Review and archive old packages
- [ ] Update PACKAGING_GUIDE.md with new examples

**Quarterly**:
- [ ] Review system prompt template for improvements
- [ ] Collect feedback on packaged dataset usefulness
- [ ] Optimize flatten script for performance

### Enhancement Ideas

**Short-term**:
- [ ] Add package size estimation before creation
- [ ] Add file type filtering (e.g., `--only python`)
- [ ] Add exclude patterns support

**Medium-term**:
- [ ] Handle duplicate flat names automatically (append hash)
- [ ] Support package diff (compare two packages)
- [ ] Add package merging (combine multiple packages)

**Long-term**:
- [ ] Interactive mode with file tree selection
- [ ] Package versioning and changelog
- [ ] Smart topic recommendation based on recent work

## Support

### For Help
```bash
./scripts/mcp/mcp-package --help
```

### Documentation
- Comprehensive guide: `docs/mcp/PACKAGING_GUIDE.md`
- System prompt: `docs/mcp/ChatGPT_Project_SYSTEM_PROMPT.md`
- This README: `scripts/mcp/README.md`

### Examples
See "Usage Examples" section above and PACKAGING_GUIDE.md

---

**Last Updated**: Previous Cycle-12-30  
**Version**: 1.0  
**Maintainer**: Aries-Serpent/_codex_ team  
**Status**: Production Ready ✅
