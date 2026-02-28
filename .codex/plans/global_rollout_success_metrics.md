# Global Rollout Success Metrics Definition (Phase 4 Planset)

> **PLANSET ONLY — No Execution Until Explicit Approval**
>
> Source: comment-3977050660 (Cognitive Brain Integration, Phase 4)
> Session: S108 (2026-02-28)

## Overview

This planset defines the exact success metrics and rollout gates for expanding
from the internal pilot (`mbaetiong`) to global Copilot users.  Rollout is gated
on these metrics with zero automation of `autonomous_actions_enabled` elevation.

## Rollout Phases (Planset-Defined)

1. **Pre-commit 1–5:** Internal only (`mbaetiong`) — current plan execution ✅
2. **Pre-commit 6–10:** Expand to Aries-Serpent org members via RBAC tier
3. **Pre-commit 11–15:** GitHub Copilot Pro subscribers beta (feature flag)
4. **Pre-commit 16–20:** Global availability with observability dashboard
5. **Session N:** Autonomous actions elevation review (separate approval gate)

## Success Metrics by Phase

| Metric | Pilot Gate (Current) | Org Gate | Pro Beta Gate | Global Gate |
|--------|----------------------|----------|---------------|-------------|
| Session context injection success rate | ≥ 95% | ≥ 97% | ≥ 98% | ≥ 99% |
| P95 session start latency overhead | < 500 ms | < 300 ms | < 200 ms | < 100 ms |
| Pattern relevance accuracy (manual spot-check) | ≥ 80% | ≥ 85% | ≥ 90% | ≥ 95% |
| API failure reconstruction rate | 100% (never crashes) | 100% | 100% | 100% |
| `report_completion()` CI feedback coverage | ≥ 70% CI runs matched | ≥ 75% | ≥ 85% | ≥ 90% |
| New pattern auto-promotion rate | ≥ 1 per 10 sessions | ≥ 2 | Sustained | Sustained |
| Token budget compliance | 100% payloads ≤ 800 tokens | 100% | 100% | 100% |
| `store_memory` lesson on API failure | 100% | 100% | 100% | 100% |
| `autonomous_actions_enabled` gate | `false` (human-only) | `false` | `false` | Separate approval |

## Monitoring Stack (Planset)

- GitHub Actions workflow metrics → `brain.report_completion()` auto-called
- Session injection logs → `.codex/cognitive_brain/session_injection_log.jsonl`
- GitHub Insights dashboard tracking P95 latency and pattern hit rate
- Weekly pattern effectiveness review:
  `pattern_effectiveness_score = success_calls / total_calls` per pattern ID

## Rollback Gates (Per Phase)

- **Pilot → Org:** Rollback if injection rate < 97% OR latency > 300 ms OR relevance < 85%
- **Org → Pro Beta:** Rollback if reconstruction rate < 100% OR CI coverage < 85%
- **Pro Beta → Global:** Rollback if any security incident OR token budget violation

## Risk Mitigation (Planset)

- Feature flag: `cognitive_brain_injection_enabled` defaults to `false` outside pilot
- Gradual rollout: 10% → 25% → 50% → 100% user segments
- Emergency disable: `autonomous_actions_enabled` remains `false` until Session N

## Acceptance Criteria (Planset)

- [ ] Metrics defined and monitoring implemented
- [ ] Rollout phases with gates documented
- [ ] Risk mitigations in place
- [ ] Zero execution until Phase 4 approval
