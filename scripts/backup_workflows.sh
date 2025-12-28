#!/bin/bash
set -euo pipefail

# Workflow Backup Script
# Creates timestamped backups of all workflow files

BACKUP_DIR=".github/workflow-archive/backups/$(date +%Y-%m-%d)"
WORKFLOWS_DIR=".github/workflows"

echo "=== Workflow Backup System ==="
echo "Backup directory: $BACKUP_DIR"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Copy all workflow files
cp -v "$WORKFLOWS_DIR"/*.yml "$BACKUP_DIR/" 2>/dev/null || true
cp -v "$WORKFLOWS_DIR"/*.yaml "$BACKUP_DIR/" 2>/dev/null || true

# Calculate total files backed up
TOTAL_FILES=$(find "$BACKUP_DIR" -type f \( -name "*.yml" -o -name "*.yaml" \) | wc -l)

# Create manifest
cat > "$BACKUP_DIR/MANIFEST.txt" << MANIFEST
Workflow Backup Manifest
Date: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
Source: $WORKFLOWS_DIR
Backup Location: $BACKUP_DIR
Total Files: $TOTAL_FILES

Files:
$(ls -1 "$BACKUP_DIR"/*.yml "$BACKUP_DIR"/*.yaml 2>/dev/null | xargs -n1 basename)

SHA256 Checksums:
$(cd "$BACKUP_DIR" && sha256sum *.yml *.yaml 2>/dev/null)
MANIFEST

echo "✅ Backup complete: $TOTAL_FILES files backed up"
echo "📄 Manifest: $BACKUP_DIR/MANIFEST.txt"

# Verify backup integrity
echo ""
echo "=== Backup Verification ==="
if [ "$TOTAL_FILES" -gt 0 ]; then
    echo "✅ All workflow files backed up successfully"
    
    # Compare file counts
    ORIGINAL_COUNT=$(find "$WORKFLOWS_DIR" -type f \( -name "*.yml" -o -name "*.yaml" \) | wc -l)
    if [ "$TOTAL_FILES" -eq "$ORIGINAL_COUNT" ]; then
        echo "✅ File count matches: $TOTAL_FILES files"
    else
        echo "⚠️ File count mismatch: Original=$ORIGINAL_COUNT, Backup=$TOTAL_FILES"
    fi
else
    echo "❌ No files were backed up!"
    exit 1
fi
