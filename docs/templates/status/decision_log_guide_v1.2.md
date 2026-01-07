# Guide: Decision Log (v1.2)
> Generated: 2024-11-02 15:26:48 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Decision Log Curator], [Secondary: Reviewer] ⚡ Energy: 5

Purpose
- Capture important choices with context and impact.

Fields
| Field | Type | Required |
|---|---|---:|
| id (Phase 12-XXX) | string | Yes |
| title | string | Yes |
| context | string | Yes |
| options | array<object> | No |
| chosen | string | Yes |
| owner | string | Yes |
| date_utc | date-time | Yes |
| impact | string | No |

Best Practices
- Keep options concise with pros/cons.
- Link to CAP-/PATCH-/issues when relevant.
