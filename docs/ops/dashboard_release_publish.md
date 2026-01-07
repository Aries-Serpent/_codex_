# Ops: Publish Dashboard as Release Asset
> Generated: Previous Cycle-11-02 16:00:04 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Publisher], [Secondary: Reviewer] ⚡ Energy: 5

Flow
| Step | Command/Action | Output |
|---|---|---|
| Build | bash scripts/status/build_trend_dashboard.sh | status_dashboard.json |
| Prepare | bash scripts/status/prepare_dashboard_assets.sh | dist/status_dashboard_*.json |
| Release | .github/workflows/publish_dashboard_release.yml | GitHub Release + asset |

Notes
- Weekly schedule; can also run manually via workflow_dispatch.
- Tag format: status-dashboard-YYYYMMDD
