#!/usr/bin/env bash
# Publish Dashboard Tiles
# This script builds and prepares dashboard tiles for publishing.
# Per repository guidelines, automation artifacts are confined to .codex/
# and GitHub Actions workflows are prohibited.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

echo "[INFO] Building rate-limit dashboard tile..."

# Step 1: Build the tile JSON if data is available
if [ -f "reports/tiles/ratelimit_tile.json" ]; then
    echo "[INFO] Found reports/tiles/ratelimit_tile.json"
    
    # Step 2: Render HTML from JSON
    python scripts/dashboards/render_ratelimit_tile_html.py \
        --tile reports/tiles/ratelimit_tile.json \
        --out reports/tiles/ratelimit_tile.html
    echo "[INFO] Rendered HTML to reports/tiles/ratelimit_tile.html"
else
    echo "[WARN] Missing reports/tiles/ratelimit_tile.json; skipping render"
fi

# Step 3: Build tiles index
echo "[INFO] Building tiles index..."
python scripts/dashboards/build_tiles_index.py

echo "[INFO] Dashboard tiles prepared in public/tiles/"
echo "[INFO] To publish, follow manual deployment process per repository guidelines"
