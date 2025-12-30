#!/usr/bin/env bash
# Package Flatten Script for ChatGPT Project
# Flattens directory structure and generates manifest.json

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Usage
usage() {
    cat <<EOF
Usage: $0 <source_dir> <output_zip> [options]

Arguments:
    source_dir    Directory containing files to package (staged selection)
    output_zip    Output zip filename (e.g., package_zendesk.zip)

Options:
    --repo-root <path>   Repository root for relative path calculation (default: auto-detect)
    --help               Show this help message

Example:
    $0 /tmp/stage package_zendesk.zip
    
This script:
  1. Flattens nested directory structure (path/to/file.py -> path__to__file.py)
  2. Computes SHA256 and size for each file
  3. Generates manifest.json with metadata
  4. Creates README_dataset.md and index.md
  5. Produces a zip archive ready for ChatGPT Project upload
EOF
    exit 1
}

# Parse arguments
if [ $# -lt 2 ]; then
    usage
fi

SOURCE_DIR="$1"
OUTPUT_ZIP="$2"
shift 2

# Parse options
while [ $# -gt 0 ]; do
    case "$1" in
        --repo-root)
            REPO_ROOT="$2"
            shift 2
            ;;
        --help)
            usage
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

# Validate inputs
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Source directory not found: $SOURCE_DIR"
    exit 1
fi

# Create temp working directory
WORK_DIR=$(mktemp -d)
trap 'rm -rf "$WORK_DIR"' EXIT

echo "=========================================="
echo "ChatGPT Project Package Builder"
echo "=========================================="
echo "Source: $SOURCE_DIR"
echo "Output: $OUTPUT_ZIP"
echo "Working directory: $WORK_DIR"
echo ""

# Initialize manifest
MANIFEST_FILE="$WORK_DIR/manifest.json"
cat > "$MANIFEST_FILE" <<EOF
{
  "version": "1.0",
  "generated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "repository": "Aries-Serpent/_codex_",
  "files": [
EOF

FILE_COUNT=0
TOTAL_SIZE=0

# Function to flatten filename
flatten_filename() {
    local path="$1"
    # Replace / and \ with __
    # Replace spaces with _
    # Preserve file extension
    echo "$path" | sed 's|/|__|g' | sed 's|\\|__|g' | sed 's| |_|g'
}

# Function to detect language
detect_language() {
    local filename="$1"
    case "${filename##*.}" in
        py) echo "python" ;;
        js) echo "javascript" ;;
        ts) echo "typescript" ;;
        sh) echo "bash" ;;
        md) echo "markdown" ;;
        yml|yaml) echo "yaml" ;;
        json) echo "json" ;;
        txt) echo "text" ;;
        *) echo "unknown" ;;
    esac
}

# Function to extract tags from path
extract_tags() {
    local path="$1"
    local tags=""
    
    # Extract directory-based tags
    if [[ "$path" == *"/agents/"* ]]; then tags="${tags},agents"; fi
    if [[ "$path" == *"/tests/"* ]]; then tags="${tags},tests"; fi
    if [[ "$path" == *"/docs/"* ]]; then tags="${tags},docs"; fi
    if [[ "$path" == *"/src/"* ]]; then tags="${tags},source"; fi
    if [[ "$path" == *"zendesk"* ]]; then tags="${tags},zendesk"; fi
    if [[ "$path" == *"quantum"* ]]; then tags="${tags},quantum"; fi
    if [[ "$path" == *"/workflows/"* ]]; then tags="${tags},workflows"; fi
    if [[ "$path" == *"/scripts/"* ]]; then tags="${tags},scripts"; fi
    
    # Remove leading comma
    tags="${tags#,}"
    echo "$tags"
}

# Process all files
echo "Processing files..."
INDEX_ROWS=""

while IFS= read -r -d '' filepath; do
    # Get relative path from source dir
    REL_PATH="${filepath#$SOURCE_DIR/}"
    
    # Skip if it's a directory
    [ -f "$filepath" ] || continue
    
    # Flatten filename
    FLAT_NAME=$(flatten_filename "$REL_PATH")
    
    # Copy to work directory with flat name
    cp "$filepath" "$WORK_DIR/$FLAT_NAME"
    
    # Compute metadata
    SHA256=$(sha256sum "$filepath" | awk '{print $1}')
    SIZE=$(stat -c%s "$filepath" 2>/dev/null || stat -f%z "$filepath")
    LANGUAGE=$(detect_language "$REL_PATH")
    TAGS=$(extract_tags "$REL_PATH")
    
    # Add to manifest
    if [ $FILE_COUNT -gt 0 ]; then
        echo "," >> "$MANIFEST_FILE"
    fi
    
    cat >> "$MANIFEST_FILE" <<EOF
    {
      "flat_name": "$FLAT_NAME",
      "original_path": "$REL_PATH",
      "sha256": "$SHA256",
      "size_bytes": $SIZE,
      "language": "$LANGUAGE",
      "tags": "$TAGS",
      "chunked": false
    }
EOF
    
    # Add to index
    SIZE_KB=$((SIZE / 1024))
    INDEX_ROWS="${INDEX_ROWS}| \`${FLAT_NAME}\` | \`${REL_PATH}\` | ${SIZE_KB} KB | ${LANGUAGE} |\n"
    
    FILE_COUNT=$((FILE_COUNT + 1))
    TOTAL_SIZE=$((TOTAL_SIZE + SIZE))
    
    echo "  [$FILE_COUNT] $REL_PATH -> $FLAT_NAME (${SIZE_KB} KB)"
done < <(find "$SOURCE_DIR" -type f -print0)

# Close manifest
cat >> "$MANIFEST_FILE" <<EOF

  ],
  "total_files": $FILE_COUNT,
  "total_size_bytes": $TOTAL_SIZE
}
EOF

echo ""
echo "Processed $FILE_COUNT files ($(($TOTAL_SIZE / 1024)) KB total)"

# Create README_dataset.md
echo "Creating README_dataset.md..."
cat > "$WORK_DIR/README_dataset.md" <<EOF
# ChatGPT Project Dataset

This archive contains a curated subset of the **Aries-Serpent/_codex_** repository, packaged for use with ChatGPT Projects.

## Dataset Information

- **Total Files**: $FILE_COUNT
- **Total Size**: $(($TOTAL_SIZE / 1024)) KB ($(($TOTAL_SIZE / 1024 / 1024)) MB)
- **Generated**: $(date -u +%Y-%m-%d)
- **Repository**: https://github.com/Aries-Serpent/_codex_

## Structure

This dataset uses a **flat file structure** where nested directory paths are encoded in filenames:

- Original: \`src/agents/workflow_navigator.py\`
- Flattened: \`src__agents__workflow_navigator.py\`

## Manifest

The \`manifest.json\` file contains the authoritative mapping of flat filenames to original repository paths, along with metadata:

- \`flat_name\`: Flattened filename in this archive
- \`original_path\`: Original path in repository
- \`sha256\`: File integrity hash
- \`size_bytes\`: File size
- \`language\`: Detected programming language
- \`tags\`: Topic/category tags
- \`chunked\`: Whether file is split across multiple parts (always false for now)

## Usage with ChatGPT Assistant

1. **Load manifest first**: Parse \`manifest.json\` to build an index
2. **Reference original paths**: When discussing code, use \`original_path\` for clarity
3. **Verify integrity**: Use \`sha256\` to verify file contents if needed
4. **Filter by tags**: Use \`tags\` field to find related files

See \`index.md\` for a quick reference table of all files.

## System Prompt

Use the system prompt in \`docs/mcp/ChatGPT_Project_SYSTEM_PROMPT.md\` when starting a ChatGPT Project session with this dataset.
EOF

# Create index.md
echo "Creating index.md..."
cat > "$WORK_DIR/index.md" <<EOF
# Dataset Index

Quick reference table for all files in this dataset.

| Flat Filename | Original Path | Size | Language |
|---------------|---------------|------|----------|
$(echo -e "$INDEX_ROWS")

**Total**: $FILE_COUNT files
EOF

# Create the zip archive
echo ""
echo "Creating zip archive: $OUTPUT_ZIP"
cd "$WORK_DIR"
zip -q -r "$REPO_ROOT/$OUTPUT_ZIP" ./*

cd "$REPO_ROOT"
ZIP_SIZE=$(stat -c%s "$OUTPUT_ZIP" 2>/dev/null || stat -f%z "$OUTPUT_ZIP")
ZIP_SIZE_MB=$((ZIP_SIZE / 1024 / 1024))

echo ""
echo "=========================================="
echo "✅ Package Complete"
echo "=========================================="
echo "Output: $OUTPUT_ZIP"
echo "Size: $ZIP_SIZE_MB MB"
echo "Files: $FILE_COUNT"
echo ""
echo "Validation:"
echo "  - Manifest entries: $(jq '.files | length' "$MANIFEST_FILE")"
echo "  - Total size: $(jq '.total_size_bytes' "$MANIFEST_FILE") bytes"
echo ""

if [ "$ZIP_SIZE_MB" -gt 50 ]; then
    echo "⚠️  WARNING: Package exceeds 50 MB (ChatGPT Project recommended limit)"
    echo "   Consider filtering to a smaller subset"
fi

echo "Next steps:"
echo "  1. Validate: unzip -l $OUTPUT_ZIP"
echo "  2. Check manifest: unzip -p $OUTPUT_ZIP manifest.json | jq ."
echo "  3. Upload to ChatGPT Project"
echo "=========================================="
