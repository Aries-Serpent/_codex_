# Guide: Automation — Connectors (v1.2)
> Generated: Previous Cycle-11-02 17:01:20 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Integration Lead], [Secondary: Status Author] ⚡ Energy: 5

Purpose
- Capture API connector health (rate-limit, status) inside status.json for daily visibility.

Fields (automation.connectors.github)
| Field | Type | Notes |
|---|---|---|
| captured_utc | string | Snapshot timestamp |
| status | string | OK | ERROR | OFFLINE |
| endpoint | string | e.g., https://api.github.com |
| resources | object | { core: {remaining}, search: {remaining}, graphql: {remaining} } |

Commands
- Capture and merge:
  - python scripts/connectors/capture_rate_limit.py
  - python scripts/connectors/ratelimit_to_status.py --report reports/daily/$(date -u +%Y-%m-%d).json
