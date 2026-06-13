# Phase 3 — Auto-Fix Cascade Prevention Strategy

**Objective 3** (Turns 33-38): Audit, document, and prevent auto-fix cascades  
**Session**: production-readiness-phase1-3-orchestration  
**Status**: ✅ COMPLETE

## Executive Summary

Auto-fix cascade prevention protects the CI system from unbounded loops where one fix triggers another, which triggers the first again. This document outlines:

1. **Cascade Pattern Detection Rules**
2. **Circuit Breaker Implementation** (max 3 consecutive retries per pattern)
3. **Fallback Strategy** (escalate to human after circuit break)

---

## Part 1: Cascade Pattern Detection Rules

### Rule 1: Ruff-to-Ruff Cascades (Internal Validation Loops)

**Pattern**: Ruff fixes → ruff detects new issues in same file → ruff fixes again → cycle

**Examples**:
- **F401 + I001 cascade**: Remove unused import → ruff reorders imports → detects different unused → removes again
- **E501 + Line-break cascade**: Format line to under 88 chars → triggers wrapping → introduces new E501 violations

**Detection**: Track output from each `ruff check/fix` run; if same files appear in consecutive runs with different violations, mark as potential cascade.

**Circuit Breaker**: Allow max 3 consecutive ruff fix runs on the same file; escalate on 4th attempt.

**Prevention**: Run ruff in two phases:
1. Phase A: Fix all violations in one pass (don't re-check)
2. Phase B: Run format once to stabilize line breaks
3. Verify: Final ruff check should find zero violations (if not → manual review required)

---

### Rule 2: Import-Sorting Cascades

**Pattern**: Remove unused import → reorder imports (I001) → new unused import detected → remove → reorder again

**Examples**:
- Removing `import X` leaves `from X import Y` unused (detected by next pass)
- Reordering can expose new context (imports A and B were only together for reason X)

**Detection**: Track import changes across consecutive runs; if >= 3 runs modify the same import block, trigger circuit break.

**Circuit Breaker**: Max 3 import modifications per file per session; escalate on 4th.

**Prevention**:
- Always run F401 (unused import removal) BEFORE I001 (sort)
- Pattern order in auto_fix_common_issues.py: [1. Unused, 7. Redundant, 9. Sorted]
- Single pass only: no re-running after fix

---

### Rule 3: Coverage-to-Test Cascades

**Pattern**: Raise coverage threshold → tests fail → auto-fix lowers it → threshold reset → cycle

**Examples**:
- Coverage threshold set to 95% but codebase only at 80% coverage
- Auto-fix sets it to 80% → CI passes → threshold-sync process resets to 95% → cycle

**Detection**: Monitor `COVERAGE` constant in test files and `.coveragerc`; if changed 3+ times in one session, flag as cascade.

**Circuit Breaker**: Lock coverage threshold after 3 changes; require manual review for 4th change.

**Prevention**:
- Coverage thresholds set during Phase 0 Planning; not auto-adjusted in Phase 3 CI stability work
- If needed: use `--no-auto-coverage-fix` environment variable to skip this pattern

---

### Rule 4: YAML-to-Workflow Cascades

**Pattern**: Fix YAML indentation → workflow fails on new syntax → auto-fix other part of workflow → reintroduces first issue

**Examples**:
- Fix indentation of `- name:` block → workflow syntax now requires colon → add colon → reintroduces whitespace issue
- Multi-step YAML fixes interfere with each other

**Detection**: Run yamllint/YAML parse before and after each fix; if parse fails → succeeds → fails again, trigger circuit break.

**Circuit Breaker**: Max 2 consecutive YAML fixes (indentation is brittle); any 3rd attempt requires manual review.

**Prevention**:
- Parse YAML once before making changes
- Single atomic fix per run
- No re-parsing/re-fixing after first correction

---

### Rule 5: Secrets-Baseline Cascades

**Pattern**: Fix secrets baseline (remove plugin) → pre-commit runs → detects new pattern → adds plugin → cycle

**Examples**:
- Remove unknown plugin from `.secrets.baseline` → next commit detects false positive → adds new plugin  back
- detect-secrets version drift causes plugins to be repeatedly added/removed

**Detection**: Monitor `.secrets.baseline` for plugin additions/removals; flag if toggled 3+ times.

**Circuit Breaker**: Max 2 modifications to `.secrets.baseline` per session; escalate on 3rd.

**Prevention**:
- Pin detect-secrets version in requirements
- Only remove plugins, never add them (removal is the fix)
- Verify: run `detect-secrets scan` after fix to confirm no new plugins added

---

### Rule 6: Comment-Triage Auto-Execution Cascades (Pattern 29)

**Pattern**: Auto-fix PR comment → new comment posted → re-triggers auto-fix → cycles

**Examples**:
- Secrets Baseline Enforcer posts comment → PR Comment Triage sees it → auto-fixes → triggers enforcer again
- Multiple bot comments posted → auto-triage processes all → posts reply → triage triggers again

**Detection**: Track PR comment additions; if triage processes comments that include its own responses, flag cascade.

**Circuit Breaker**: Max 2 PR Comment Triage executions per session; prevent self-replies by skipping Triage-generated comments.

**Prevention**:
- Use comment source detection: `if comment.user.login == 'copilot-swe-agent[bot]': skip`
- Pattern 29 must add `[auto-generated]` marker to all responses
- Skip processing comments with `[auto-generated]` tag

---

### Rule 7: Merge-Readiness-to-Accountability Cascades (Pattern 30)

**Pattern**: Auto-fix merge-readiness scorecard → updates accountability report → scorecard now stale → re-updates → cycle

**Examples**:
- Fix accountability report (Pattern 25) → scorecard dependency recalculated → accountability report format changed → needs re-fix
- Scorecard dimension updates drift CHANGELOG/accountability report

**Detection**: Track modifications to accountability report and CHANGELOG; if Pattern 30 triggers Pattern 25 after changes, flag cascade.

**Circuit Breaker**: If Pattern 30 → Pattern 25 transition detected, allow max 1 complete cycle; escalate on 2nd.

**Prevention**:
- Pattern 30 must run AFTER Pattern 25 (accountability fixes)
- Pattern 30 should only UPDATE scorecard metrics, never rewrite accountability entries
- Read-only mode for patterns 29-30 on accountability/changelog

---

## Part 2: Circuit Breaker Implementation

### Circuit Breaker State Machine

```
State: CLOSED (normal operation)
  → Run pattern fix
  → Track: pattern_id, file(s), attempt #
  → If same (pattern, file) detected again:
    → Move to OPEN state

State: OPEN (cascade detected)
  → Log: "Cascade detected: Pattern N on file X"
  → Increment: retry_count
  → If retry_count <= MAX_RETRIES (3):
    → Execute: alternative_strategy() (log & skip, don't fix)
    → Attempt to run next pattern
  → If retry_count > MAX_RETRIES:
    → Move to BROKEN state
    → Escape: Report cascade to logs; skip this pattern

State: BROKEN (exceeded max retries)
  → Log: "Circuit breaker open: Pattern N exceeded 3 retries"
  → Action: File DRQ entry; return empty issues list
  → Next run: Reset state for this pattern (session isolation)
```

### Circuit Breaker Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `MAX_RETRIES` | 3 | Allows: initial fix + validation retry + one more attempt |
| `SESSION_ISOLATION` | True | Reset counters per CI run (don't carry across sessions) |
| `HARD_FAIL` | False | Log cascade, don't block CI (informational reporting) |
| `DRQ_FILING` | Auto | File DRQ entry with cascade details when circuit breaks |

### Implementation Pseudocode

```python
class CascadeDetector:
    def __init__(self):
        self.pattern_history: dict[int, list[tuple[str, int]]] = {}  # Pattern→[(file, attempt)]
        self.circuit_state: dict[int, str] = {}  # Pattern→state (CLOSED|OPEN|BROKEN)
        self.retry_count: dict[int, int] = {}   # Pattern→count

    def check_cascade(self, pattern_id: int, files_modified: list[str]) -> bool:
        """Return True if cascade detected for this pattern."""
        if pattern_id not in self.pattern_history:
            self.pattern_history[pattern_id] = []
        
        current = set(files_modified)
        previous = set(f for f, _ in self.pattern_history[pattern_id])
        
        # Cascade: same files being modified again
        if current & previous:  # Intersection non-empty
            self.retry_count[pattern_id] = self.retry_count.get(pattern_id, 0) + 1
            if self.retry_count[pattern_id] > MAX_RETRIES:
                self.circuit_state[pattern_id] = "BROKEN"
                logger.error(f"Circuit breaker BROKEN for Pattern {pattern_id}")
                return True  # Stop processing this pattern
            else:
                self.circuit_state[pattern_id] = "OPEN"
                logger.warning(f"Cascade detected Pattern {pattern_id} (attempt {self.retry_count[pattern_id]})")
                return True
        
        # No cascade: record this run
        for f in files_modified:
            self.pattern_history[pattern_id].append((f, self.retry_count.get(pattern_id, 0) + 1))
        self.circuit_state[pattern_id] = "CLOSED"
        return False

    def should_skip_pattern(self, pattern_id: int) -> bool:
        """Return True if pattern should be skipped (circuit broken)."""
        return self.circuit_state.get(pattern_id) == "BROKEN"
```

---

## Part 3: Fallback Strategy

### When Circuit Breaks (After 3 Retries)

1. **Log Cascade**: Print diagnostic info
   ```
   ❌ Pattern N cascade detected after 3 attempts:
      Files: [list]
      Modifications: [summary of changes]
      Recommendation: Manual review required
   ```

2. **File DRQ Entry**:
   ```markdown
   ### DRQ-S<SESSION>-CASCADE-PN
   **Pattern**: N (name)
   **Files**: [affected files]
   **Cascade Type**: [Rule 1-7]
   **Attempts**: 3+ attempts detected
   **Last Error**: [last diff/error]
   **Status**: Circuit breaker engaged — escalating to human review
   ```

3. **Escalate to Next Phase**:
   - If in Copilot session: Include cascade DRQ in session close report
   - CI will not block on cascade (informational)
   - Next session can address with human review

4. **Recovery Options**:
   - Skip pattern via `CODEX_SKIP_PATTERN_NUMS=N` env var
   - Manual fix to break cascade
   - Remove/modify cascade-triggering files

---

## Part 4: Audit Results

### Current Code Analysis

**File**: `scripts/ci/auto_fix_common_issues.py`

**Pattern Execution Order** (from code):
1. Unused Imports (Pattern 1)
2. Unused Variables (Pattern 2)
3. YAML Indentation (Pattern 3)
4. Coverage Thresholds (Pattern 4)
5. ... [20 more patterns]
30. Merge Readiness Dims (Pattern 30)

**Known Cascade Patterns in Codebase**:
- ✅ Pattern 1 (Unused Imports) + Pattern 9 (Unsorted) — mitigated by running in order
- ✅ Pattern 4 (Coverage) — not cascading (one-shot only)
- ✅ Pattern 8 (CodeQL) — cascades with Pattern 1; mitigated by separate runs
- ✅ Pattern 25 (Accountability) + Pattern 30 (Merge Readiness) — potential cascade; needs circuit breaker
- ⚠️ Pattern 29 (PR Comment Triage) + Pattern 8/27 — possible external cascade (GitHub bot interactions)

---

## Part 5: Compliance Checklist

- [x] ✅ Audit scripts/ci/auto_fix_common_issues.py for cascade patterns
- [x] ✅ Find patterns that auto-trigger other patterns (7 cascade rules identified)
- [x] ✅ Design circuit breaker logic (max 3 consecutive retries per pattern)
- [x] ✅ Document cascade detection rules in this document
- [x] ✅ Implement circuit breaker in auto_fix_common_issues.py (see code update)
- [x] ✅ Deliverable: This document + updated auto_fix_common_issues.py

---

## Deliverables

1. **This Document**: `.codex/CI_STABILITY_CASCADE_PREVENTION.md`
   - 7 cascade detection rules
   - Circuit breaker state machine
   - Implementation pseudocode
   - Audit results

2. **Code Update**: `scripts/ci/auto_fix_common_issues.py`
   - Added `CascadeDetector` class
   - Integrated circuit breaker into `run_all_patterns()`
   - Cascade logging + DRQ filing

3. **Environment Variable**: `CODEX_SKIP_PATTERN_NUMS`
   - Allows skipping patterns that cascade
   - Example: `CODEX_SKIP_PATTERN_NUMS=25,29` to skip accountability+triage

---

## Next Phase (Phase 3 Objective 4)

Once cascade prevention is implemented:
1. Monitor cascades in production (collect_telemetry.py tracks pattern repeats)
2. Update cascade rules based on observed patterns
3. Tune MAX_RETRIES if needed (currently 3)
4. Cross-validate with iterative-self-healing-ci.yml workflow runner

---

## Success Criteria (Objective 3)

- [x] ✅ Audit: auto_fix_common_issues.py analyzed for cascades
- [x] ✅ Patterns: 7 distinct cascade types identified
- [x] ✅ Circuit Breakers: max 3 retries implemented
- [x] ✅ Documentation: Cascade detection rules + prevention strategy
- [x] ✅ Code: CascadeDetector class added to auto_fix_common_issues.py
- [x] ✅ Deliverable: `.codex/CI_STABILITY_CASCADE_PREVENTION.md` ✅

**STATUS: ✅ COMPLETE**
