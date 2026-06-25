# Component 5: Enhanced Session Bootstrap - Technical Specification

**Status:** Ready for Delegation  
**Assigned to:** workflow-ci-fixer agent (or workflow-compliance-guardian)  
**Priority:** HIGH  
**Complexity:** HIGH (critical workflow modification)

---

## Objective

Enhance `.github/workflows/copilot-setup-steps.yml` to pre-load aggregated context from the data aggregation system, reducing session startup time from 24-48 hours to <5 minutes.

---

## Requirements

### R1: Context Pre-Loading
- [ ] At session startup (Step: "🧠 Session Context Pre-load" ~line 141-147)
- [ ] Load `.codex/session_context_manifest.json` if it exists
- [ ] Parse: phase_state, in_flight_agents, recent_patterns, delegation_recommendations
- [ ] Inject as environment variables for downstream steps

### R2: Manifest Injection
- [ ] Set `SESSION_CONTEXT_PHASE` = current phase from manifest
- [ ] Set `SESSION_CONTEXT_AGENTS_COUNT` = number of in-flight agents
- [ ] Set `SESSION_CONTEXT_PATTERNS` = top 5 recent patterns (JSON)
- [ ] Set `SESSION_CONTEXT_RECOMMENDATIONS` = delegation recommendations
- [ ] Set `SESSION_CONTEXT_LAST_UPDATED` = manifest timestamp

### R3: Fallback Behavior
- [ ] If manifest doesn't exist: Skip silently (no errors)
- [ ] If manifest is invalid JSON: Log warning, continue
- [ ] If manifest is stale (>24h old): Log warning, regenerate
- [ ] Ensure job never fails due to missing context

### R4: Syntax Constraints (CRITICAL)

⚠️ **MUST FOLLOW THESE CONSTRAINTS:**

```yaml
# Line 141-147: Use block scalar syntax `run: |`
# Use brace-free shell: if ! ... ; then ... ; fi (NOT { } braces)
# NO complex nested structures that break YAML parsing

✅ CORRECT:
- name: 🧠 Session Context Pre-load
  run: |
    if ! [ -f ".codex/session_context_manifest.json" ]; then
      echo "⚠️ Manifest not found, skipping pre-load"
      exit 0
    fi
    # Parse logic here...

❌ INCORRECT (causes YAML parse errors):
- name: 🧠 Session Context Pre-load
  run: if ! [ -f ".codex/session_context_manifest.json" ]; then ... ; fi
  # ✗ No block scalar
  # ✗ Bare braces can cause parsing issues
```

### R5: Performance Impact
- [ ] Pre-load step must complete in <30 seconds
- [ ] Use lightweight JSON parsing (jq or Python, NOT sed/awk chains)
- [ ] Do NOT fetch remote data (use only local .codex/ files)
- [ ] Do NOT call external APIs

### R6: Logging & Observability
- [ ] Log: "✅ Context loaded: <phase> | <agent_count> agents | <pattern_count> patterns"
- [ ] Log: Timestamp when manifest was generated
- [ ] Log: Any warnings (stale manifest, invalid JSON, etc.)
- [ ] Add to $GITHUB_STEP_SUMMARY for visibility

---

## Implementation Approach

### Step 1: Locate Insertion Point

**Current:** `.github/workflows/copilot-setup-steps.yml` line 141-147 (Session Pre-load step)

**Current Code (Example):**
```yaml
- name: 🧠 Session Context Pre-load
  run: |
    # Existing logic...
    if ! command -v python3 >/dev/null 2>&1; then
      echo "Python not found"
      exit 1
    fi
```

### Step 2: Add Context Loading Logic

**Add this section AFTER existing pre-load checks:**

```yaml
# Load aggregated session context (Component 5)
if [ -f ".codex/session_context_manifest.json" ]; then
  MANIFEST=".codex/session_context_manifest.json"

  # Parse manifest
  PHASE=$(python3 -c "import json; print(json.load(open('$MANIFEST')).get('phase_state', {}).get('current_phase', 'unknown'))" 2>/dev/null || echo "unknown")
  AGENTS=$(python3 -c "import json; print(len(json.load(open('$MANIFEST')).get('in_flight_agents', [])))" 2>/dev/null || echo "0")
  PATTERNS=$(python3 -c "import json; print(len(json.load(open('$MANIFEST')).get('recent_patterns', [])))" 2>/dev/null || echo "0")

  echo "export SESSION_CONTEXT_PHASE='$PHASE'" >> $GITHUB_ENV
  echo "export SESSION_CONTEXT_AGENTS_COUNT=$AGENTS" >> $GITHUB_ENV
  echo "export SESSION_CONTEXT_PATTERNS=$PATTERNS" >> $GITHUB_ENV

  echo "✅ Context pre-loaded: $PHASE | $AGENTS agents | $PATTERNS patterns"
else
  echo "ℹ️ Manifest not found (.codex/session_context_manifest.json)"
  echo "export SESSION_CONTEXT_PHASE='unknown'" >> $GITHUB_ENV
fi
```

### Step 3: Use Context in Downstream Steps

**For agents delegation step:**
```yaml
- name: Delegate Agents Based on Context
  if: env.SESSION_CONTEXT_AGENTS_COUNT < 5
  run: |
    # If <5 agents in-flight, delegate more based on recommendations
    gh workflow run adaptive-agent-delegation.yml \
      -f delegation_mode=parallel \
      -f max_agents=5
```

---

## Testing Checklist

- [ ] Syntax validation: `yamllint .github/workflows/copilot-setup-steps.yml`
- [ ] Dry-run: Trigger workflow with `--dry-run` flag
- [ ] Integration: Verify context variables set correctly
- [ ] Fallback: Test with missing manifest (should not fail)
- [ ] Fallback: Test with invalid JSON (should not fail)
- [ ] Performance: Verify pre-load completes in <30 seconds
- [ ] Logging: Verify step summary shows context loaded
- [ ] Downstream: Verify agents delegated based on context

---

## Constraints & Warnings

⚠️ **CRITICAL:** Do not modify lines 141-147 carelessly
- These lines handle shell brace logic with YAML parsing
- Any change must preserve `run: |` block scalar syntax
- Test thoroughly with `yamllint` before commit

⚠️ **NO BREAKING CHANGES:**
- Session bootstrap must never fail due to context loading
- Ensure fallbacks for all error conditions
- Default behavior when manifest missing: continue as normal

---

## Rollback Plan

If enhancement breaks session bootstrap:
1. Revert to previous workflow version
2. Remove context pre-load step
3. File incident report with details
4. Schedule re-implementation with workflow-ci-fixer agent

---

## Success Criteria

✅ **Session startup time reduced:**
- Before: 24-48 hours (waiting for data collection)
- After: <5 minutes (context pre-loaded)

✅ **No regressions:**
- Session bootstrap still works without manifest
- All downstream steps execute normally
- YAML syntax valid (yamllint passes)

✅ **Observability:**
- Context injection logged in step summary
- Phase state visible to all downstream jobs
- Agent delegation recommendations available

---

## Resources

- **Integration Guide:** `.codex/DATA_AGGREGATION_INTEGRATION_GUIDE.md`
- **Pattern Library:** `scripts/ci/workflow_pattern_library.py`
- **Delegation Engine:** `scripts/ci/rapid_delegation_engine.py`
- **Current Workflow:** `.github/workflows/copilot-setup-steps.yml`

---

**Specification Created:** 2026-06-22T00:32:00Z  
**Ready for Agent Delegation**
