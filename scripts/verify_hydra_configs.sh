#!/bin/bash
# Verify all Hydra config groups referenced in tests exist

set -e

echo "🔍 Analyzing Hydra config coverage..."

# Extract config references from tests (use -h to suppress filenames)
config_refs=$(grep -rh "experiment=" tests/ 2>/dev/null | grep -o "experiment=[a-z_]*" | cut -d= -f2 | sort -u)

if [ -z "$config_refs" ]; then
    echo "ℹ️  No experiment config references found in tests"
    exit 0
fi

echo "📋 Found config references:"
echo "$config_refs"

missing_configs=()

for config in $config_refs; do
    config_file="config/experiment/${config}.yaml"
    if [ ! -f "$config_file" ]; then
        echo "❌ Missing: $config_file"
        missing_configs+=("$config")
    else
        echo "✅ Found: $config_file"
    fi
done

if [ ${#missing_configs[@]} -gt 0 ]; then
    echo ""
    echo "⚠️  ${#missing_configs[@]} missing config file(s)"
    echo "Create these files or update tests to use existing configs"
    exit 1
else
    echo ""
    echo "✅ All referenced configs exist"
fi
