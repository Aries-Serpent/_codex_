# ChatGPT Project Packaging Guide

Complete guide for packaging Aries-Serpent/_codex_ repository subsets for ChatGPT Project use.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Topic Selection](#topic-selection)
5. [Custom Filtering](#custom-filtering)
6. [Workflow Usage](#workflow-usage)
7. [Manual Packaging](#manual-packaging)
8. [Validation](#validation)
9. [Upload to ChatGPT](#upload-to-chatgpt)
10. [Troubleshooting](#troubleshooting)

## Overview

The ChatGPT Project packaging system creates flat-structure archives from nested repository directories, enabling ChatGPT Assistant to work with curated code subsets without direct Git access.

### Key Features

- **Flat file structure**: Nested paths encoded in filenames (`src/agents/foo.py` → `src__agents__foo.py`)
- **Manifest-driven**: `manifest.json` maps flat names to original paths with metadata
- **Topic-based selection**: Pre-configured topics (zendesk, agents, quantum, docs, workflows)
- **Custom filtering**: Glob pattern support for ad-hoc selections
- **Integrity verification**: SHA256 hashes for all files
- **Size-aware**: Warns if package exceeds ChatGPT limits (50 MB recommended)

## Prerequisites

- **Python 3.8+** for `select_components.py`
- **Bash** for `package_flatten.sh`
- **jq** for JSON processing (validation)
- **zip** utility

Install dependencies (Ubuntu/Debian):
```bash
sudo apt-get update && sudo apt-get install -y python3 jq zip
```

## Quick Start

Package the "zendesk" topic:

```bash
cd /path/to/_codex_

# 1. Select files
python scripts/mcp/select_components.py \
    --topic zendesk \
    --output /tmp/filelist.txt

# 2. Stage files
mkdir -p /tmp/stage
while IFS= read -r rel; do
    if [ -f "$rel" ]; then
        mkdir -p "/tmp/stage/$(dirname "$rel")"
        cp "$rel" "/tmp/stage/$rel"
    fi
done < /tmp/filelist.txt

# 3. Package and flatten
./scripts/mcp/package_flatten.sh /tmp/stage package_zendesk.zip

# 4. Validate
unzip -l package_zendesk.zip
unzip -p package_zendesk.zip manifest.json | jq .
```

Result: `package_zendesk.zip` ready for ChatGPT Project upload.

## Topic Selection

Available topics (defined in `scripts/mcp/topics.json`):

### 1. **zendesk**
- Zendesk API integration code
- Tests for Zendesk functionality
- Zendesk-related documentation

**Typical size**: 5-10 MB (50-100 files)

```bash
python scripts/mcp/select_components.py --topic zendesk --output /tmp/zendesk_files.txt
```

### 2. **agents**
- All agent implementations (cognitive, physics, workflow, etc.)
- Agent tests
- Agent documentation

**Typical size**: 15-25 MB (200-300 files)

```bash
python scripts/mcp/select_components.py --topic agents --output /tmp/agents_files.txt
```

### 3. **quantum**
- Quantum game theory implementations
- Quantum-related tests
- Quantum documentation

**Typical size**: 3-8 MB (30-80 files)

```bash
python scripts/mcp/select_components.py --topic quantum --output /tmp/quantum_files.txt
```

### 4. **docs**
- All documentation files
- README files
- Markdown guides

**Typical size**: 2-5 MB (100-200 files)

```bash
python scripts/mcp/select_components.py --topic docs --output /tmp/docs_files.txt
```

### 5. **mcp**
- MCP (Model Context Protocol) scripts
- ChatGPT packaging tools
- MCP documentation

**Typical size**: 1-2 MB (10-20 files)

```bash
python scripts/mcp/select_components.py --topic mcp --output /tmp/mcp_files.txt
```

### 6. **workflows**
- GitHub Actions workflows
- CI/CD scripts
- Copilot prompts

**Typical size**: 5-10 MB (100-150 files)

```bash
python scripts/mcp/select_components.py --topic workflows --output /tmp/workflows_files.txt
```

## Custom Filtering

Use `--overrides` to specify custom glob patterns (comma-separated):

```bash
# Package only Python files in src/agents
python scripts/mcp/select_components.py \
    --overrides "src/agents/**/*.py,tests/agents/**/*.py" \
    --output /tmp/custom_files.txt

# Package specific subdirectories
python scripts/mcp/select_components.py \
    --overrides "src/zendesk/**,docs/zendesk/**" \
    --output /tmp/zendesk_subset.txt

# Package all YAML files
python scripts/mcp/select_components.py \
    --overrides "**/*.yml,**/*.yaml" \
    --output /tmp/yaml_files.txt
```

## Workflow Usage

The GitHub Actions workflow automates packaging:

```yaml
# .github/workflows/build-chatgpt-package.yml
# Trigger: workflow_dispatch with inputs
```

**To run**:
1. Go to Actions tab in GitHub
2. Select "Build ChatGPT Project Package" workflow
3. Click "Run workflow"
4. Fill inputs:
   - **topic**: zendesk, agents, quantum, docs, mcp, or workflows
   - **glob_filters**: (optional) custom globs to override topic
   - **output_name**: (optional) output zip filename
5. Download artifact after completion

**Example workflow run**:
- Input: `topic = "agents"`
- Output artifact: `package_agents.zip`
- Download from workflow run page

## Manual Packaging

Full manual process:

```bash
#!/bin/bash
TOPIC="agents"
OUTPUT="package_${TOPIC}.zip"

# 1. Select files by topic
python scripts/mcp/select_components.py \
    --topic "$TOPIC" \
    --output /tmp/filelist.txt

# 2. Create staging directory
mkdir -p /tmp/stage
echo "Staging files..."
while IFS= read -r rel; do
    if [ -f "$rel" ]; then
        mkdir -p "/tmp/stage/$(dirname "$rel")"
        cp "$rel" "/tmp/stage/$rel"
    fi
done < /tmp/filelist.txt

# 3. Package with flattening
./scripts/mcp/package_flatten.sh /tmp/stage "$OUTPUT"

# 4. Verify
echo "Verifying package..."
unzip -l "$OUTPUT"
unzip -p "$OUTPUT" manifest.json | jq -r '.files | length'

# 5. Size check
SIZE_MB=$(stat -c%s "$OUTPUT" 2>/dev/null || stat -f%z "$OUTPUT")
SIZE_MB=$((SIZE_MB / 1024 / 1024))
echo "Package size: ${SIZE_MB} MB"

if [ "$SIZE_MB" -gt 50 ]; then
    echo "⚠️  Warning: Package exceeds 50 MB recommended limit"
fi

# 6. Cleanup
rm -rf /tmp/stage /tmp/filelist.txt

echo "✅ Package ready: $OUTPUT"
```

## Validation

### Validate Manifest

```bash
# Extract and validate manifest.json
unzip -p package_zendesk.zip manifest.json | jq . > /dev/null && echo "✅ Valid JSON" || echo "❌ Invalid JSON"

# Check file count
FILE_COUNT=$(unzip -p package_zendesk.zip manifest.json | jq '.files | length')
echo "Files in manifest: $FILE_COUNT"

# Check total size
TOTAL_SIZE=$(unzip -p package_zendesk.zip manifest.json | jq '.total_size_bytes')
TOTAL_MB=$((TOTAL_SIZE / 1024 / 1024))
echo "Total size: ${TOTAL_MB} MB"

# Check for duplicate flat names
DUPES=$(unzip -p package_zendesk.zip manifest.json | jq -r '.files[].flat_name' | sort | uniq -d)
if [ -z "$DUPES" ]; then
    echo "✅ No duplicate flat names"
else
    echo "❌ Duplicate flat names found:"
    echo "$DUPES"
fi
```

### Validate Package Contents

```bash
# List all files in package
unzip -l package_zendesk.zip

# Verify required files present
for REQUIRED in "manifest.json" "README_dataset.md" "index.md"; do
    unzip -l package_zendesk.zip | grep -q "$REQUIRED" && echo "✅ $REQUIRED" || echo "❌ Missing $REQUIRED"
done

# Extract and review index
unzip -p package_zendesk.zip index.md | head -20
```

### Test Extraction

```bash
# Extract to temporary directory
TEST_DIR=$(mktemp -d)
unzip -q package_zendesk.zip -d "$TEST_DIR"

# Verify file count matches manifest
MANIFEST_COUNT=$(jq -r '.files | length' "$TEST_DIR/manifest.json")
ACTUAL_COUNT=$(find "$TEST_DIR" -type f | wc -l)
echo "Manifest files: $MANIFEST_COUNT"
echo "Actual files: $ACTUAL_COUNT"

# Cleanup
rm -rf "$TEST_DIR"
```

## Upload to ChatGPT

### Option 1: Upload Zip Directly

1. Open ChatGPT (chatgpt.com)
2. Create new Project or select existing
3. Click "Add files" or drag-and-drop
4. Select `package_zendesk.zip`
5. ChatGPT will extract and index automatically

### Option 2: Upload Extracted Files

1. Extract package locally:
   ```bash
   mkdir extracted
   unzip package_zendesk.zip -d extracted/
   ```

2. Upload all files in `extracted/` to ChatGPT Project

3. Ensure `manifest.json` is uploaded first (if order matters)

### Configure System Prompt

1. In ChatGPT Project, go to "Instructions" or "System Prompt"
2. Copy prompt from `docs/mcp/ChatGPT_Project_SYSTEM_PROMPT.md`
3. Paste into system prompt field
4. Save

### Verify Load

Start chat and ask:
```
What files are in this dataset? List the first 10 with their original paths.
```

Assistant should respond with files from manifest, showing original paths.

## Troubleshooting

### Package Too Large (&gt;50 MB)

**Solution**: Filter to smaller subset

```bash
# Instead of full "agents" topic, select specific agent
python scripts/mcp/select_components.py \
    --overrides "src/agents/workflow_navigator.py,tests/agents/test_workflow_navigator.py,docs/agents/workflow_navigator.md" \
    --output /tmp/subset.txt
```

### Duplicate Flat Names

**Cause**: Two files with same name in different directories (e.g., `src/foo.py` and `tests/foo.py`)

**Solution**: Check manifest for duplicates and adjust:
```bash
unzip -p package.zip manifest.json | jq -r '.files[].flat_name' | sort | uniq -d
```

If duplicates found, the packaging script needs enhancement to handle this (e.g., append hash to flat name).

### Manifest Missing or Invalid

**Cause**: `package_flatten.sh` failed during manifest generation

**Solution**: Check temp directory permissions and re-run:
```bash
./scripts/mcp/package_flatten.sh /tmp/stage package.zip --help
```

### Files Not Found in Package

**Cause**: `select_components.py` didn't match expected files

**Solution**: Verify glob patterns in `topics.json` and re-select:
```bash
python scripts/mcp/select_components.py --topic zendesk --output /tmp/test.txt
cat /tmp/test.txt  # Review selected files
```

### ChatGPT Can't Load Manifest

**Cause**: Manifest JSON is malformed or missing

**Solution**: Validate manifest locally:
```bash
unzip -p package.zip manifest.json | jq . > /dev/null && echo "Valid" || echo "Invalid"
```

Re-package if needed.

## Advanced Usage

### Combine Multiple Topics

```bash
# Select files from multiple topics
python scripts/mcp/select_components.py \
    --overrides "$(jq -r '.zendesk + .agents | join(",")' scripts/mcp/topics.json)" \
    --output /tmp/combined.txt
```

### Filter by Language

```bash
# Package only Python files from agents
python scripts/mcp/select_components.py \
    --overrides "src/agents/**/*.py,agents/**/*.py,tests/agents/**/*.py" \
    --output /tmp/agents_python.txt
```

### Add Custom Metadata

Edit `package_flatten.sh` to include custom metadata in manifest:
- Repository commit SHA
- Branch name
- Packaging date
- Curator notes

## Best Practices

1. **Start small**: Test with docs or mcp topic first (&lt;5 MB)
2. **Validate locally**: Always check manifest before uploading
3. **Use topics**: Prefer predefined topics over custom globs for consistency
4. **Document overrides**: If using custom globs, document why
5. **Version packages**: Include date or commit in output filename (e.g., `package_agents_2025-12-30.zip`)
6. **Test ChatGPT load**: Verify assistant can parse manifest and answer queries
7. **Iterate**: Start broad, then narrow to specific files as needed

## Integration with Development Workflow

1. **After major changes**: Repackage affected topics
2. **Before external share**: Package relevant subset for collaborators
3. **For documentation**: Package docs + related code for context
4. **For debugging**: Package specific module + tests + docs

---

**Last Updated**: 2025-12-30  
**Maintainer**: Aries-Serpent/_codex_ team  
**Related Files**:
- `scripts/mcp/select_components.py`
- `scripts/mcp/package_flatten.sh`
- `scripts/mcp/topics.json`
- `docs/mcp/ChatGPT_Project_SYSTEM_PROMPT.md`
- `.github/workflows/build-chatgpt-package.yml`
