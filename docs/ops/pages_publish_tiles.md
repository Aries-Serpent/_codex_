# Ops: Publish Dashboard Tiles via Pages
> Generated: 2025-11-02 17:01:20 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Publisher], [Secondary: Reviewer] ⚡ Energy: 5

Flow
| Step | Action | Output |
|---|---|---|
| Build tile | python scripts/dashboards/build_ratelimit_tile.py | reports/tiles/ratelimit_tile.json |
| Render HTML | python scripts/dashboards/render_ratelimit_tile_html.py | reports/tiles/ratelimit_tile.html |
| Index | python scripts/dashboards/build_tiles_index.py | public/tiles/index.html |
| Automation | bash .codex/scripts/publish_dashboard_tiles.sh | Builds tiles and prepares for publishing |
| Deploy | manual copy or approved CLI tool (see repository guidelines) | GitHub Pages (tiles/) |
