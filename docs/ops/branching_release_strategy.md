# Ops: Branching & Release Strategy (v1.2)
> Generated: 2024-11-02 15:30:24 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Release Manager], [Secondary: Maintainer] ⚡ Energy: 5

Branches
- main/master: Stable, protected
- 0D_base_: Integration for status/validation bootstrap
- feature/* or copilot/*: Short-lived feature branches

Release Flow
| Step | Action | Gate |
|---|---|---|
| 1 | Branch from 0D_base_ | CI smoke |
| 2 | PR -> 0D_base_ | status_validation, security_gates, nox_gates |
| 3 | Squash & merge | Label, changelog entry |
| 4 | Release draft | release_drafter |
| 5 | Promote to main | All CI green |

Tags
- vX.Y.Z semantic versioning; patch for docs/tooling, minor for new optional sections, major for breaking schema

Backports
- Cherry-pick fixes from 0D_base_ to main when needed
