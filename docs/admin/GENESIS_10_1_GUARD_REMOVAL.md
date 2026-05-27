# Genesis Phase 10.1 — Guard Removal Checklist

**Status**: ⏳ Awaiting Admin Approval  
**Owner**: @mbaetiong  
**Planset**: PS-17c  
**Last Updated**: 2026-02-12

---

## Overview

Genesis Phase 10.1 removes the three-layer safety guards that restrict autonomous agent operations. This is a controlled transition from advisory mode to supervised autonomous mode.

## Prerequisites (All Required)

- [x] CODEX_MASTER_KEY confirmed and available
- [x] CODEX_BACKUP_KEY confirmed and available
- [x] All 17 plansets (PS-01 through PS-16) ✅ Complete
- [x] AAIS V3.4 score 97.0/100 (A+) achieved
- [x] Fragile test coverage 99.4% (153/154 files guarded)
- [x] CacheManager integrated in 25/61 workflows (41%)
- [x] RAG centralized loader operational
- [ ] Admin approval granted (pending)

## 3-Step Guard Removal Protocol

### Step 1: Workflow Guard (`genesis-bootstrap.yml`)

**Current**: `if: false` (prevents workflow execution)  
**Target**: `if: true` (enables workflow execution)

```yaml
# Change: if: false → if: true
```

**Rollback**: Set `if: false` to immediately disable.

### Step 2: Script Guard (`autonomous_agent.py`)

**Current**: `SAFE_MODE = True` (blocks autonomous actions)  
**Target**: `SAFE_MODE = False` (enables supervised autonomous actions)

```python
# scripts/autonomous_agent.py
# Change: SAFE_MODE = True → SAFE_MODE = False
```

**Rollback**: Set `SAFE_MODE = True` to immediately revert.

### Step 3: Config Guard (`guardrails.md`)

**Current**: `autonomous_actions_enabled: false`  
**Target**: `autonomous_actions_enabled: true`

```yaml
# .codex/guardrails.md
# Change: autonomous_actions_enabled: false → autonomous_actions_enabled: true
```

**Rollback**: Set `autonomous_actions_enabled: false` to immediately revert.

## Execution Order

1. Step 3 (Config) — lowest risk, enables configuration
2. Step 2 (Script) — medium risk, enables agent logic
3. Step 1 (Workflow) — highest risk, enables CI execution

## Validation After Each Step

After each step, verify:
- [ ] No unauthorized actions triggered
- [ ] Healing loop reports healthy (`python scripts/cognitive/healing_loop.py --json`)
- [ ] Agent introspection shows expected capabilities
- [ ] No CI workflow failures

## Emergency Rollback

If any issues detected:
1. Immediately revert all 3 guards to their safe values
2. Run healing loop: `python scripts/cognitive/healing_loop.py --max-iterations 3`
3. Document the issue in `.codex/change_log.md`
4. Create escalation issue with `[ESCALATION]` tag

## Admin Approval

To execute Genesis 10.1, the repository admin must:
1. Review this checklist
2. Approve the PR containing this document
3. Execute the 3 steps in order on the main branch
4. Monitor for 24 hours before confirming completion
