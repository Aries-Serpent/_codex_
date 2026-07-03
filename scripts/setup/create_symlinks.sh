#!/bin/bash
# Setup script for creating symlinks on Unix systems
# This is necessary because Windows doesn't support symlinks without admin privileges

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

echo "Creating symlinks for cross-platform compatibility..."

# Create symlinks only on Unix-like systems
if [[ "$OSTYPE" != "msys" && "$OSTYPE" != "win32" && "$OSTYPE" != "cygwin" ]]; then
    # .codex directory symlinks
    if [ ! -e ".codex/security_vulnerability_scan_latest.md" ] && [ -f ".codex/security_vulnerability_scan_2025-12-26.md" ]; then
        ln -s security_vulnerability_scan_2025-12-26.md .codex/security_vulnerability_scan_latest.md
        echo "✅ Created .codex/security_vulnerability_scan_latest.md"
    fi
    
    # configs directory symlinks
    if [ ! -e "configs/data" ] && [ -d "training/data" ]; then
        ln -s training/data configs/data
        echo "✅ Created configs/data"
    fi
    
    if [ ! -e "configs/model" ] && [ -d "training/model" ]; then
        ln -s training/model configs/model
        echo "✅ Created configs/model"
    fi
    
    if [ ! -e "configs/tracking" ] && [ -d "training/tracking" ]; then
        ln -s training/tracking configs/tracking
        echo "✅ Created configs/tracking"
    fi
    
    if [ ! -e "configs/train" ] && [ -d "training/profiles" ]; then
        ln -s training/profiles configs/train
        echo "✅ Created configs/train"
    fi
    
    # scripts directory symlinks
    if [ ! -e "scripts/audit_pipeline.py" ] && [ -f "src/codex_ml/cli/audit_pipeline.py" ]; then
        ln -s ../src/codex_ml/cli/audit_pipeline.py scripts/audit_pipeline.py
        echo "✅ Created scripts/audit_pipeline.py"
    fi
    
    if [ ! -e "scripts/ci/session_preload.py" ] && [ -f ".github/scripts/session_preload.py" ]; then
        ln -s ../../.github/scripts/session_preload.py scripts/ci/session_preload.py
        echo "✅ Created scripts/ci/session_preload.py"
    fi
    
    echo ""
    echo "✅ All symlinks created successfully"
else
    echo "⚠️  Running on Windows or Windows-like system"
    echo "   Symlinks cannot be created automatically"
    echo "   See .codex/WINDOWS_SYMLINK_SETUP.md for manual setup instructions"
fi
