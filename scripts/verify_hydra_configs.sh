#!/bin/bash
# Verify all Hydra config groups referenced in tests exist

set -e

echo "🔍 Analyzing Hydra config coverage..."

# Extract Hydra override references from tests / docs examples.
# Match quoted strings like "experiment=debug" or "+experiment=debug" but
# ignore unrelated keyword arguments such as experiment="exp".
config_refs=$(
  python - <<'PY'
from pathlib import Path
import re

pattern = re.compile(r"""['"\[]\+?experiment=([a-z_][a-z0-9_]*)['"]""")
refs = set()
for path in Path("tests").rglob("*.py"):
    try:
        refs.update(pattern.findall(path.read_text(encoding="utf-8", errors="ignore")))
    except OSError:
        continue
for ref in sorted(refs):
    print(ref)
PY
)

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
