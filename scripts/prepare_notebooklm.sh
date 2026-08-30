#!/bin/bash
# prepare_notebooklm.sh
# Prepares full codebase context for NotebookLM ingestion
# Generated: 2026-01-23T19:00:00Z
# Branch: copilot/sub-pr-3020

set -euo pipefail

OUTPUT_FILE="full_context.txt"
# Detect repository root dynamically, fallback to GitHub Actions path
REPO_ROOT="${1:-$(git -C "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)" rev-parse --show-toplevel 2>/dev/null || (cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd))}"

echo "🚀 Preparing NotebookLM Context for Aries-Serpent/_codex_"
echo "=================================================="
echo ""

# Clear output file
> "$OUTPUT_FILE"

# Header
cat >> "$OUTPUT_FILE" << 'EOF'
================================================================================
FULL CODEBASE CONTEXT FOR NOTEBOOKLM GROUNDING ENGINE
================================================================================
Repository: Aries-Serpent/_codex_
Branch: copilot/sub-pr-3020 (0D_base_ equivalent)
Generated: 2026-01-23T19:00:00Z
Purpose: Comprehensive context for AI model ingestion

Architecture: Hybrid Python-Rust Monorepo
- Logic Layer: Python Cognitive Brain (scripts/cognitive/, cognitive_app/)
- Performance Layer: Rust Orchestration Engine (rust_swarm/, src/*.rs)
- Bridge Layer: Schemas, Manifests, Mappings
- Documentation Layer: Guides, Prompts, Reference Docs

================================================================================

EOF

echo "📚 Collecting Documentation Files..."

# Find all markdown files in docs/ and guides/
MD_COUNT=0
while IFS= read -r file; do
    echo "================================================" >> "$OUTPUT_FILE"
    echo "FILE: $file" >> "$OUTPUT_FILE"
    echo "================================================" >> "$OUTPUT_FILE"
    cat "$file" >> "$OUTPUT_FILE"
    echo -e "\n\n" >> "$OUTPUT_FILE"
    ((MD_COUNT++))
done < <(find "$REPO_ROOT/docs" "$REPO_ROOT/guides" -type f -name "*.md" 2>/dev/null)

echo "  ✅ Collected $MD_COUNT documentation files"

echo "🐍 Collecting Python Source Files..."

# Find all Python files, excluding tests, node_modules, target, .git
PY_COUNT=0
while IFS= read -r file; do
    echo "================================================" >> "$OUTPUT_FILE"
    echo "FILE: $file" >> "$OUTPUT_FILE"
    echo "================================================" >> "$OUTPUT_FILE"
    cat "$file" >> "$OUTPUT_FILE"
    echo -e "\n\n" >> "$OUTPUT_FILE"
    ((PY_COUNT++))
done < <(find "$REPO_ROOT" -type f -name "*.py" \
    -not -path "*/tests/*" \
    -not -path "*/node_modules/*" \
    -not -path "*/target/*" \
    -not -path "*/.git/*" \
    -not -path "*/__pycache__/*" \
    -not -path "*/.pytest_cache/*" \
    -not -path "*/venv/*" \
    -not -path "*/.venv/*" \
    2>/dev/null)

echo "  ✅ Collected $PY_COUNT Python files"

echo "🦀 Collecting Rust Source Files..."

# Find all Rust files, excluding tests, target, .git
RS_COUNT=0
while IFS= read -r file; do
    echo "================================================" >> "$OUTPUT_FILE"
    echo "FILE: $file" >> "$OUTPUT_FILE"
    echo "================================================" >> "$OUTPUT_FILE"
    cat "$file" >> "$OUTPUT_FILE"
    echo -e "\n\n" >> "$OUTPUT_FILE"
    ((RS_COUNT++))
done < <(find "$REPO_ROOT" -type f -name "*.rs" \
    -not -path "*/tests/*" \
    -not -path "*/target/*" \
    -not -path "*/.git/*" \
    2>/dev/null)

echo "  ✅ Collected $RS_COUNT Rust files"

echo "📋 Collecting Configuration & Schema Files..."

# Collect key configuration files
CONFIG_COUNT=0
for file in \
    "$REPO_ROOT/Cargo.toml" \
    "$REPO_ROOT/pyproject.toml" \
    "$REPO_ROOT/setup.cfg" \
    "$REPO_ROOT/pytest.ini" \
    "$REPO_ROOT/.github/agents/AGENT_REGISTRY.yaml"; do

    if [[ -f "$file" ]]; then
        echo "================================================" >> "$OUTPUT_FILE"
        echo "FILE: $file" >> "$OUTPUT_FILE"
        echo "================================================" >> "$OUTPUT_FILE"
        cat "$file" >> "$OUTPUT_FILE"
        echo -e "\n\n" >> "$OUTPUT_FILE"
        ((CONFIG_COUNT++))
    fi
done

# Collect schema files using find to avoid shell glob expansion issues
while IFS= read -r file; do
    echo "================================================" >> "$OUTPUT_FILE"
    echo "FILE: $file" >> "$OUTPUT_FILE"
    echo "================================================" >> "$OUTPUT_FILE"
    cat "$file" >> "$OUTPUT_FILE"
    echo -e "\n\n" >> "$OUTPUT_FILE"
    ((CONFIG_COUNT++))
done < <(find "$REPO_ROOT/schemas" "$REPO_ROOT/.codex/schemas" -maxdepth 1 -type f \( -name "*.json" -o -name "*.yaml" \) 2>/dev/null || true)

echo "  ✅ Collected $CONFIG_COUNT configuration/schema files"

echo "🎯 Collecting Prompt Files..."

# Collect prompts from all locations
PROMPT_COUNT=0
for dir in "$REPO_ROOT/PROMPTS" "$REPO_ROOT/prompts" "$REPO_ROOT/.codex/prompts" "$REPO_ROOT/agents/prompts"; do
    if [[ -d "$dir" ]]; then
        while IFS= read -r file; do
            echo "================================================" >> "$OUTPUT_FILE"
            echo "FILE: $file" >> "$OUTPUT_FILE"
            echo "================================================" >> "$OUTPUT_FILE"
            cat "$file" >> "$OUTPUT_FILE"
            echo -e "\n\n" >> "$OUTPUT_FILE"
            ((PROMPT_COUNT++))
        done < <(find "$dir" -type f -name "*.md" 2>/dev/null)
    fi
done

echo "  ✅ Collected $PROMPT_COUNT prompt files"

echo "🤖 Collecting Agent Definition Files..."

# Collect agent definitions
AGENT_COUNT=0
for dir in "$REPO_ROOT/.github/agents" "$REPO_ROOT/agents" "$REPO_ROOT/.codex/agents"; do
    if [[ -d "$dir" ]]; then
        while IFS= read -r file; do
            if [[ "$file" == *".md" ]] || [[ "$file" == *".yml" ]] || [[ "$file" == *".yaml" ]]; then
                echo "================================================" >> "$OUTPUT_FILE"
                echo "FILE: $file" >> "$OUTPUT_FILE"
                echo "================================================" >> "$OUTPUT_FILE"
                cat "$file" >> "$OUTPUT_FILE"
                echo -e "\n\n" >> "$OUTPUT_FILE"
                ((AGENT_COUNT++))
            fi
        done < <(find "$dir" -maxdepth 2 -type f 2>/dev/null)
    fi
done

echo "  ✅ Collected $AGENT_COUNT agent definition files"

# Footer
cat >> "$OUTPUT_FILE" << EOF

================================================================================
CONTEXT GENERATION COMPLETE
================================================================================
Total Files Collected:
  - Documentation:   $MD_COUNT files
  - Python Source:   $PY_COUNT files
  - Rust Source:     $RS_COUNT files
  - Config/Schema:   $CONFIG_COUNT files
  - Prompts:         $PROMPT_COUNT files
  - Agent Defs:      $AGENT_COUNT files

Total: $((MD_COUNT + PY_COUNT + RS_COUNT + CONFIG_COUNT + PROMPT_COUNT + AGENT_COUNT)) files

Next Steps:
1. Ingest skeleton_map.json into NotebookLM
2. Ingest GEM_INSTRUCTIONS.md into NotebookLM
3. Ingest this file (full_context.txt) into NotebookLM

The AI model will now have complete context of the Aries-Serpent/_codex_ repository.
================================================================================
EOF

echo ""
echo "✅ SUCCESS: Context prepared in $OUTPUT_FILE"
echo ""
FILE_SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
echo "📊 Statistics:"
echo "  - Output File: $OUTPUT_FILE"
echo "  - File Size: $FILE_SIZE"
echo "  - Documentation: $MD_COUNT files"
echo "  - Python: $PY_COUNT files"
echo "  - Rust: $RS_COUNT files"
echo "  - Config/Schema: $CONFIG_COUNT files"
echo "  - Prompts: $PROMPT_COUNT files"
echo "  - Agents: $AGENT_COUNT files"
echo "  - Total: $((MD_COUNT + PY_COUNT + RS_COUNT + CONFIG_COUNT + PROMPT_COUNT + AGENT_COUNT)) files"
echo ""
echo "🎯 Ready for NotebookLM ingestion!"
