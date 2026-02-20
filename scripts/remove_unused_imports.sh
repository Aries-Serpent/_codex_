#!/usr/bin/env bash
# Remove unused imports flagged by CodeQL bot

set -euo pipefail

echo "Removing unused imports..."

# Fix scripts/empty_toc_resolver.py (line 18)
if [ -f scripts/empty_toc_resolver.py ]; then
    sed -i 's/from typing import Dict, List, Tuple/from typing import Dict, List/' scripts/empty_toc_resolver.py
    echo "✅ Fixed scripts/empty_toc_resolver.py"
fi

# Fix scripts/phase3_stage1_processor.py (line 10)
if [ -f scripts/phase3_stage1_processor.py ]; then
    sed -i 's/from typing import Dict, List, Set, Tuple/from typing import List, Tuple/' scripts/phase3_stage1_processor.py
    echo "✅ Fixed scripts/phase3_stage1_processor.py"
fi

# Fix scripts/phase3_categorization.py (remove 're' import and fix typing)
if [ -f scripts/phase3_categorization.py ]; then
    sed -i '/^import re$/d' scripts/phase3_categorization.py
    sed -i 's/from typing import Dict, List, Tuple/from typing import Dict/' scripts/phase3_categorization.py
    echo "✅ Fixed scripts/phase3_categorization.py"
fi

echo "✅ Unused imports removed"

# Verify with ruff
if command -v ruff &> /dev/null; then
    echo "Running ruff to verify..."
    ruff check --select F401,F841 scripts/ || true
else
    echo "⚠️ ruff not installed - skipping verification"
fi
