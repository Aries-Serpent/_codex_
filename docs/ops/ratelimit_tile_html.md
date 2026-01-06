# Ops: HTML Renderer for Rate-Limit Tile
> Generated: Previous Cycle-11-02 16:45:24 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Publisher], [Secondary: Integration Lead] ⚡ Energy: 5

Purpose
- Render reports/tiles/ratelimit_tile.json into a simple, dependency-free HTML (inline SVG) for sharing.

Commands
- Build tile JSON:
  - python scripts/dashboards/build_ratelimit_tile.py
- Render HTML:
  - python scripts/dashboards/render_ratelimit_tile_html.py --tile reports/tiles/ratelimit_tile.json --out reports/tiles/ratelimit_tile.html

Notes
- Uses inline SVG lines + points for core/search/graphql series.
- Summaries are displayed in a table (min/avg/max).
