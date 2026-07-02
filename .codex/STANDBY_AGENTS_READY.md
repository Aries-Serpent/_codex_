# Tier 2 Standby Agents - Ready for Deployment
**Status:** QUEUED - Awaiting Agent Slot Availability
**Deployment Trigger:** When Tier 1 agent completes (expected ~19:08:30Z)

## Agent 1: Validation Failure Resolution
**Agent Type:** ci-failure-resolution-agent
**Agent ID (when deployed):** phase3-validation-crisis
**Target Failure:** Validation Pipeline - Fast Validation (FAILED 3m)
**Deployment Condition:** Next available agent slot

**Task Brief:**
```
Diagnose and fix: Validation Pipeline → Fast Validation (FAILED 180s)
Root cause candidates:
  - Validation schema mismatch
  - Missing dependencies (jsonschema, pydantic)
  - Input file corruption/missing
  - Data type validation failures

Fetch logs: https://github.com/Aries-Serpent/_codex_/actions/runs/28614444377/job/84854874862

Resolution path:
1. Fetch full job logs + extract error messages
2. Classify error type (schema/data/dependency)
3. Apply fix (auto-fix for patterns P1-P4)
4. Validate locally with test data
5. Re-run validation to confirm success
```

## Agent 2: Audit Trail Logging (Standby)
**Agent Type:** logging-system-agent
**Agent ID (when deployed):** phase3-logging-system-crisis
**Target Failure:** Phase 9.3 Router - Log Routing Decision (FAILED 12s)
**Deployment Condition:** If session-analysis-agent stalls >3min

**Task Brief:**
```
Fix: Phase 9.3 Router → Log Routing Decision to Audit Trail (FAILED 12s)
Root cause candidates:
  - Audit logger initialization failure
  - Missing audit trail configuration
  - Incorrect log routing setup
  - Session context not injected

Fetch logs: https://github.com/Aries-Serpent/_codex_/actions/runs/28614444356/job/84855599243

Resolution path:
1. Fetch job logs + diagnose logging failure
2. Check audit trail configuration in .codex/
3. Validate logger initialization code
4. Fix configuration or code as needed
5. Test logging with sample session data
```

## Agent 3: Governance Generation (Standby)
**Agent Type:** policy-coach-agent
**Agent ID (when deployed):** phase3-policy-governance-crisis
**Target Failure:** Machine Readable Governance - governance generation (FAILED 3m)
**Deployment Condition:** If governance-crisis stalls >3min

**Task Brief:**
```
Fix: Machine Readable Governance → machine-readable-governance (FAILED 3m)
Root cause candidates:
  - Governance script syntax/import error
  - Configuration file missing or corrupted
  - Schema validation failure in generation
  - Insufficient permissions for artifact output

Fetch logs: https://github.com/Aries-Serpent/_codex_/actions/runs/28614444235/job/84854829410

Resolution path:
1. Fetch job logs + extract error stack
2. Validate governance generation script syntax
3. Check all dependencies available
4. Verify input files and permissions
5. Regenerate governance artifacts
6. Verify output schema is correct
```

## Deployment Sequence (Estimated)

```
NOW (19:04:00Z):
  ├─ Tier 1 agents still in progress (governance, session, rag, orchestrator)
  └─ Tier 2 agents standing by in queue

~19:08:30Z (Expected):
  ├─ Tier 1 agents complete (4-5 min total)
  ├─ Agent slots open
  └─ Deploy phase3-validation-crisis immediately

~19:10:00Z (If needed):
  └─ Deploy phase3-logging-system-crisis (if session agent stalled)

~19:11:00Z (If needed):
  └─ Deploy phase3-policy-governance-crisis (if governance agent stalled)

~19:13:30Z (Deadline):
  └─ All 7 failures must be resolved
```

## Failure Resolution Status Tracking

| Failure | Agent | Status | Next Step |
|---------|-------|--------|-----------|
| RAG Governance Block | governance-crisis | DIAGNOSING | Await result |
| Compliance Check | governance-crisis | DIAGNOSING | Await result |
| Audit Trail | session-audit-crisis | DIAGNOSING | Await result |
| Session Tracker | session-audit-crisis | DIAGNOSING | Await result |
| FAISS Build | rag-crisis | DIAGNOSING | Await result |
| Validation Check | validation-crisis | ⏳ QUEUED | Deploy when slot opens |
| Governance Gen | policy-governance-crisis | ⏳ QUEUED | Deploy if stall detected |

## Success Criteria for Tier 2

✅ **Validation crisis agent:**
- Fixes validation pipeline failure
- Confirms schema validation passes
- Test data validates successfully

✅ **Logging system agent (if deployed):**
- Fixes audit trail routing
- Logger initialization succeeds
- Session logging works end-to-end

✅ **Policy governance agent (if deployed):**
- Regenerates governance artifacts
- Output schema is valid
- All governance files present

## Campaign Status After Tier 2

Upon successful resolution of all 7 failures:
1. Crisis resolved = campaign proceeds
2. Tier 1 workflows complete → green ✅
3. Tier 2 workflows start (remaining 28)
4. Real-time monitoring continues
5. Escalation watches for new failures

---

**Status:** READY FOR DEPLOYMENT
**Waiting:** Agent slot availability (~5-10 minutes)
**Deadline:** 2026-07-02T19:13:30Z (9+ minutes)
