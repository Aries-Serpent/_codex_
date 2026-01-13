#!/bin/bash
# Test Repomix Local Consolidation
# Validates XML generation, file size, and security scanning

set -e

echo "🚀 Testing Repomix Local Consolidation"
echo "======================================="

# Check if repomix is installed
if ! command -v repomix >/dev/null 2>&1; then
    echo "⚠️  Repomix not found. Installing..."
    npm install -g repomix
fi

# Check if config exists
if [ ! -f "repomix.config.json" ]; then
    echo "❌ repomix.config.json not found"
    echo "Run this script from repository root"
    exit 1
fi

# Run consolidation
echo "📦 Running repomix consolidation..."
repomix --config repomix.config.json

# Check if output file exists
if [ ! -f "codex-architecture-sync.xml" ]; then
    echo "❌ XML file not generated"
    exit 1
fi

echo "✅ XML file generated successfully"

# Check file size
if command -v stat >/dev/null 2>&1; then
    # macOS and Linux compatible
    SIZE=$(stat -f%z codex-architecture-sync.xml 2>/dev/null || stat -c%s codex-architecture-sync.xml)
    SIZE_MB=$(echo "scale=2; $SIZE / 1024 / 1024" | bc)
    
    echo "📏 File size: ${SIZE_MB}MB"
    
    if [ $SIZE -lt 5242880 ]; then  # 5MB in bytes
        echo "✅ File size within target (< 5MB)"
    else
        echo "⚠️  File size exceeds target: ${SIZE_MB}MB (target: < 5MB)"
        echo "Consider enabling more aggressive Tree-sitter compression"
    fi
else
    echo "⚠️  Cannot determine file size (stat command not available)"
fi

# Security scanning
echo ""
echo "🔒 Running security scans..."

# Secretlint
if command -v secretlint >/dev/null 2>&1 || command -v npx >/dev/null 2>&1; then
    echo "Running Secretlint..."
    if npx secretlint codex-architecture-sync.xml; then
        echo "✅ Secretlint: No secrets detected"
    else
        echo "❌ Secretlint: Secrets detected!"
        exit 1
    fi
else
    echo "⚠️  Secretlint not available (install with: npm install -g secretlint)"
fi

# detect-secrets
if command -v detect-secrets >/dev/null 2>&1; then
    echo "Running detect-secrets..."
    if detect-secrets scan codex-architecture-sync.xml --baseline .secrets.baseline 2>/dev/null; then
        echo "✅ detect-secrets: No secrets detected"
    else
        echo "⚠️  detect-secrets: High-entropy strings detected (review manually)"
    fi
else
    echo "⚠️  detect-secrets not available (install with: pip install detect-secrets)"
fi

# XML validation
echo ""
echo "🔍 Validating XML structure..."
if command -v xmllint >/dev/null 2>&1; then
    if xmllint --noout codex-architecture-sync.xml 2>/dev/null; then
        echo "✅ XML structure valid"
    else
        echo "❌ XML structure invalid"
        exit 1
    fi
else
    echo "⚠️  xmllint not available (install with: brew install libxml2 or apt-get install libxml2-utils)"
fi

# Content validation
echo ""
echo "📊 Content analysis..."
LINE_COUNT=$(wc -l < codex-architecture-sync.xml)
echo "Lines: $LINE_COUNT"

FILE_TAG_COUNT=$(grep -c "<file_path>" codex-architecture-sync.xml || echo "0")
echo "Files included: $FILE_TAG_COUNT"

if [ $FILE_TAG_COUNT -gt 0 ]; then
    echo "✅ Content validation passed"
else
    echo "❌ No files found in XML"
    exit 1
fi

echo ""
echo "✅ All local tests passed!"
echo ""
echo "Next steps:"
echo "1. Review codex-architecture-sync.xml manually"
echo "2. Commit repomix.config.json to repository"
echo "3. Trigger notebooklm-sync.yml workflow in GitHub Actions"
