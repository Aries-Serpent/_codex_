# 📬 PR COMMENT RESOLUTION PROTOCOL — EXPLICIT RESPONSE GUIDE

**Purpose:** Ensure ALL unanswered PR comments receive explicit responses with commit SHA references  
**Requirement:** Zero unanswered comments per post-merge follow-up  
**Status:** Part of Lane 2 in POST_MERGE_FOLLOWUP_PROMPT.md  

---

## 🎯 PROTOCOL OVERVIEW

This protocol ensures that **every single unanswered PR comment receives an explicit response** that includes:

1. **The specific question** being answered (quote it)
2. **A clear, direct answer** (not vague)
3. **Evidence** (commit SHA, file path, line numbers)
4. **Justification** (why this approach)
5. **Links** to code, tests, or documentation

---

## 📋 RESPONSE TEMPLATE

Use this template for **EVERY** unanswered comment:

```markdown
**Comment ID:** [GitHub comment ID number]
**Question:** [Exact quote of the question]
**Status:** RESOLVED ✅

**Response:**
[Explicit answer - 1-3 sentences, direct and clear]

**Evidence:**
- **Commit:** [SHA] — [Commit message]
- **File:** [path/to/file.py]
- **Lines:** [line range, e.g., 45-67]
- **Change:** [What was changed/added/fixed]

**Verification:**
[How to verify this is correct - test command, reference, etc.]
```

---

## 🏷️ COMMENT CATEGORIES

Different comment types require different response depths:

### Category 1: CODE REVIEW QUESTIONS
**Example:** "Why was this function refactored?"

**Required Response Elements:**
- ✅ Explicit reason for the change
- ✅ Commit SHA showing the refactoring
- ✅ Code locations (before/after)
- ✅ Test verification

**Example Response:**
```
**Question:** Why was the async handler refactored?

**Response:**
Refactored to eliminate race condition in concurrent cache invalidation. 
The original code had a window where two threads could both see stale cache 
and both attempt to refresh, causing duplicate work.

**Evidence:**
- Commit: abc123def456 — "fix: eliminate cache race condition"
- File: src/codex/cache/invalidator.py
- Lines: 45-67 (added lock mechanism)
- Tests: tests/unit/test_cache_race.py (15 new tests covering race scenarios)
```

### Category 2: SECURITY ALERTS
**Example:** "Is this vulnerability addressed?"

**Required Response Elements:**
- ✅ Explicit confirmation yes/no
- ✅ Which commit addresses it
- ✅ What specific fix was applied
- ✅ Link to CVE or security advisory

**Example Response:**
```
**Question:** CVE-2024-XXXXX — Is urllib3 vulnerability addressed?

**Response:**
Yes. Upgraded urllib3 from 2.0.7 to 2.6.3+ which contains the fix for 
HTTP request smuggling vulnerability.

**Evidence:**
- Commit: def456abc123 — "security: upgrade urllib3 to 2.6.3"
- File: pyproject.toml
- Lines: 58 (urllib3>=2.6.3)
- Test: poetry lock validate confirms 2.6.3+ installed
```

### Category 3: TEST COVERAGE QUESTIONS
**Example:** "Why is this path untested?"

**Required Response Elements:**
- ✅ Explanation of why untested (if valid)
- ✅ OR commitment to add tests
- ✅ Test file and line references if added
- ✅ Coverage percentage proof

**Example Response:**
```
**Question:** Why is the error handler in line 89 untested?

**Response:**
This was a critical gap. Added comprehensive error handling tests 
in the same commit that introduced the handler.

**Evidence:**
- Commit: 789ghi012jkl — "test: add error handler coverage"
- Test File: tests/unit/test_error_handlers.py
- Lines: 145-210 (10 new test cases)
- Coverage Report: 89% → 94% for this module
```

### Category 4: DESIGN DECISION QUESTIONS
**Example:** "Why this approach vs. alternative?"

**Required Response Elements:**
- ✅ Comparison of approaches considered
- ✅ Rationale for chosen approach
- ✅ Trade-offs explained
- ✅ Links to architecture docs if applicable

**Example Response:**
```
**Question:** Why use FAISS embedding over traditional vector search?

**Response:**
FAISS chosen for O(1) nearest-neighbor lookup vs O(n) traditional search. 
Trade-off: 5% accuracy loss but 100x faster for 1M+ vectors. 
Acceptable for this use case (ranking, not precision).

**Evidence:**
- Commit: 012jkl345mno — "design: implement FAISS routing"
- Docs: docs/architecture/ROUTING_ENGINE_DESIGN.md (lines 45-78)
- Benchmarks: .codex/FAISS_vs_TRADITIONAL_BENCHMARK.md
```

### Category 5: DOCUMENTATION GAPS
**Example:** "Where is this feature documented?"

**Required Response Elements:**
- ✅ Link to documentation
- ✅ File path where documented
- ✅ Section or anchor reference
- ✅ If not documented, commit to add

**Example Response:**
```
**Question:** Where is the new cache invalidation strategy documented?

**Response:**
Documented in the API reference and implementation guide.

**Evidence:**
- Docs: docs/reference/API_CACHE.md (section "Invalidation Strategies")
- Commit: 345mno678pqr — "docs: document cache invalidation strategy"
- Example: docs/examples/cache_usage.md (lines 120-140)
```

### Category 6: ACKNOWLEDGMENT REQUIRED
**Example:** "Got it, thanks for the note"

**Required Response Elements:**
- ✅ Clear acknowledgment
- ✅ Action taken (if applicable)
- ✅ Reference to related commit

**Example Response:**
```
**Question:** Please ensure this is backward compatible.

**Response:**
Acknowledged. Maintained backward compatibility by supporting 
both old and new API signatures with deprecation warnings.

**Evidence:**
- Commit: 678pqr901stu — "compat: maintain backward compatibility"
- Migration: docs/migration/v0.2_to_v0.3.md
```

---

## ✅ VERIFICATION CHECKLIST

Before marking a comment as "RESOLVED":

- [ ] The question is explicitly answered (not implied)
- [ ] Answer includes commit SHA
- [ ] File path(s) referenced
- [ ] Line numbers provided (or range)
- [ ] Can someone find the code by following the reference?
- [ ] Evidence validates the answer
- [ ] Tone is professional and clear
- [ ] No vague phrases like "we addressed this" or "it's handled"

---

## 🚫 ANTI-PATTERNS (What NOT to Do)

### ❌ BAD: Vague Responses
```
"We addressed this in the refactoring."
"This was fixed in the latest commit."
"It's covered in the tests."
```

### ✅ GOOD: Explicit Responses
```
"Fixed in commit abc123def (line 45-67) by adding cache lock mechanism."
"Added tests in tests/unit/test_cache_race.py (15 new tests)."
"Coverage increased from 65% to 94% in this module."
```

### ❌ BAD: Deflecting
```
"This is addressed in a future PR."
"We'll fix this later."
"Out of scope for this change."
```

### ✅ GOOD: Direct Answers
```
"Not addressed in this PR because [reason]. Tracked in issue #1234."
"Added in commit abc123def as prerequisite for this feature."
"Scope: This PR handles X, related feature Y is in PR #5000."
```

---

## 📊 COMMENT TRACKING SPREADSHEET

Use this format to track all PR comments:

| Comment ID | Author | Question Summary | Category | Status | Commit SHA | Response Posted |
|------------|--------|------------------|----------|--------|------------|-----------------|
| 5018166215 | @maintainer | Why refactor async handler? | Code Review | RESOLVED | abc123def | ✅ Yes |
| 5018168672 | @reviewer | CVE-2024-XXXXX urllib3? | Security | RESOLVED | def456abc | ✅ Yes |
| 5018170001 | @reviewer | Test coverage gap? | Test | RESOLVED | 789ghi012 | ✅ Yes |
| 5018171234 | @reviewer | Design decision? | Design | RESOLVED | 012jkl345 | ✅ Yes |
| 5018172456 | @reviewer | Documentation? | Docs | RESOLVED | 345mno678 | ✅ Yes |

---

## 🔄 EXECUTION FLOW (Lane 2)

```
1. EXTRACT PHASE
   └─ Fetch all PR comments
   └─ Filter: Only unanswered ones
   └─ Create: Comment tracking spreadsheet

2. ANALYSIS PHASE
   └─ For each unanswered comment:
      ├─ Read question carefully
      ├─ Determine: Needs investigation? Code change? Evidence?
      ├─ Research: Related commits, code, tests
      └─ Find: Evidence (commit SHA, file, line numbers)

3. RESPONSE PHASE
   └─ For each comment:
      ├─ Use response template
      ├─ Quote the original question
      ├─ Provide explicit answer
      ├─ Include commit SHA + evidence
      └─ Post reply to PR

4. VERIFICATION PHASE
   └─ Confirm: Every comment has response
   └─ Validate: Each response has evidence
   └─ Check: No unanswered comments remain
   └─ Generate: PR_COMMENT_RESOLUTION_SUMMARY.md
```

---

## 📝 DELIVERABLE: PR_COMMENT_RESOLUTION_SUMMARY.md

This is the output document Lane 2 produces:

```markdown
# PR #5367 — Comment Resolution Summary

**Status:** ✅ COMPLETE — All 12 comments answered
**Date Generated:** 2026-07-20T02:53:41Z

## Summary Table
| ID | Author | Category | Status | Commit |
|----|----|----------|--------|--------|
| [table of all comments with commit refs] |

## Detailed Responses

### Comment #1: Code Review — async refactoring
[Full response with template format]

### Comment #2: Security — CVE vulnerability
[Full response with template format]

... [12 total responses]

## Verification
- ✅ All 12 comments addressed
- ✅ Each response includes commit SHA
- ✅ All evidence links valid
- ✅ No vague responses
- ✅ Coverage includes: 4 code reviews, 3 security, 2 tests, 2 design, 1 docs
```

---

## 🎯 SUCCESS CRITERIA FOR LANE 2

Lane 2 (PR Comment Resolution) is **COMPLETE** when:

- ✅ All unanswered comments identified (0 missed)
- ✅ Every comment receives explicit response with template format
- ✅ 100% of responses include commit SHA reference
- ✅ 100% of responses include file path + line numbers
- ✅ All evidence links are valid and clickable
- ✅ No vague or deflecting responses
- ✅ Responses posted to PR as comment replies
- ✅ Summary document generated: `PR_COMMENT_RESOLUTION_SUMMARY.md`
- ✅ Zero unanswered comments remain

---

## 📚 EXAMPLES BY REPO CONTEXT

### PyPI Release Issues (Current Repo)

```
**Question:** Why did the PyPI publish fail with OIDC token error?

**Response:**
OIDC token scope mismatch. The token was generated correctly but wasn't 
scoped to the specific PyPI project. This is different from v0.2.2 release 
which used legacy token auth.

**Evidence:**
- Commit: abc123def — "fix: validate OIDC token scopes"
- File: .codex/RELEASE_SUCCESS_COMPARISON_ANALYSIS.md (lines 45-78)
- Reference: Comparing successful v0.2.2 to failed v0.3.0+ releases
- Fix: docs/operations/pypi-trusted-publishing-setup.md (step-by-step)
```

### Multi-Agent Delegation

```
**Question:** How do the 5 lanes coordinate their work?

**Response:**
Lanes execute in parallel with Lane 2 (PR comments) acting as critical 
path. Each lane produces independent deliverable. Final consolidation 
happens after all lanes complete.

**Evidence:**
- Design: .codex/POST_MERGE_FOLLOWUP_PROMPT.md (lines 12-45)
- Diagram: .codex/POST_MERGE_SYSTEM_IMPLEMENTATION_GUIDE.md (Execution Flow)
- Activation: scripts/ci/activate_post_merge_followup.py (line 55+)
```

---

## 🚀 HOW TO ACTIVATE FOR YOUR PR

```bash
# 1. Extract PR comments (for a specific PR)
gh pr view 5367 --json comments

# 2. Identify unanswered ones
# (Filter comments without [RESOLVED] tag)

# 3. Use the Lane 2 prompt from POST_MERGE_FOLLOWUP_PROMPT.md
cat .codex/POST_MERGE_FOLLOWUP_PROMPT.md | grep -A 50 "Lane 2"

# 4. Post responses using template above

# 5. Generate summary
# (Post-merge agent does this automatically)

# 6. Verify: 0 unanswered comments remain
gh pr view 5367 --json comments | grep -c "unanswered"
# Expected output: 0
```

---

**This protocol ensures complete, explicit, evidence-backed responses to every PR comment, eliminating ambiguity and providing maintainers with full transparency into what changed and why.**
