# LANE B: JavaScript CodeQL Fix Execution Checklist

**Date:** 2026-07-13  
**Total Items:** 37 findings → 8 unique issues to fix  
**Estimated Total Effort:** 2-3 hours  
**Priority:** LOW (all code quality, no security issues)

---

## Quick Summary

| Priority | Issues | Time | Status |
|----------|--------|------|--------|
| **CRITICAL** | 0 | - | ✅ NONE |
| **HIGH** | 0 | - | ✅ NONE |
| **MEDIUM** | 4 | 1 hour | 📋 Fix logic |
| **LOW** | 32 | 1-2 hours | 📋 Code cleanup |

---

## Fix Execution Plan

### Phase 1: Assessment (15 min)

- [ ] Review all findings in detail
- [ ] Assess impact on functionality
- [ ] Run existing test suite to establish baseline
- [ ] Document current behavior

**Commands:**
```bash
# Review findings
cat .codex/LANE_B_CODEQL_JAVASCRIPT_ANALYSIS.md

# Run existing tests
npm test
# or
yarn test
```

---

### Phase 2: MEDIUM Priority Fixes (1 hour) 

#### 2.1 Fix Trivial Conditionals (3 instances)

**Issue:** Variables that always evaluate to true/false

**Findings:**
- `site/assets/javascripts/lunr/wordcut.js:2505` - `needDir` always true
- `site/assets/javascripts/lunr/wordcut.js:2985` - `needDir` always true
- `site/assets/javascripts/lunr/wordcut.js:3573` - `inClass` always true

**Fix Steps:**

1. **Open file:** `site/assets/javascripts/lunr/wordcut.js`

2. **Find line 2505:**
   ```javascript
   // Before
   if (needDir) {
       path = path + '/';
   }
   
   // After - Option A: Remove condition
   path = path + '/';
   
   // After - Option B: Restore proper logic
   needDir = someCondition(path);
   if (needDir) {
       path = path + '/';
   }
   ```

3. **Find line 2985:** Repeat same fix pattern

4. **Find line 3573:** Review `inClass` usage pattern

5. **Test after fixes:**
   ```bash
   npm test
   ```

**Effort:** 15-20 minutes

---

#### 2.2 Fix Use Before Declaration (1 instance)

**Issue:** `tinyseg.js:117` - Variable `i` used before declaration

**Finding:**
- `site/assets/javascripts/lunr/tinyseg.js:117`

**Fix Steps:**

1. **Open file:** `site/assets/javascripts/lunr/tinyseg.js`

2. **Find line 117:**
   ```javascript
   // Before
   for (let i = 0; i < length; i++) {
       // i used in initialization before declaration
   }
   
   // After - Move declaration before use
   let i;
   for (i = 0; i < length; i++) {
       // proper usage
   }
   ```

3. **Test:**
   ```bash
   npm test
   ```

**Effort:** 5-10 minutes

---

#### 2.3 Fix Unneeded Defensive Code (1 instance)

**Issue:** `tinyseg.js:110` - Guard always evaluates to false

**Finding:**
- `site/assets/javascripts/lunr/tinyseg.js:110`

**Fix Steps:**

1. **Open file:** `site/assets/javascripts/lunr/tinyseg.js`

2. **Find line 110:**
   ```javascript
   // Before - Guard always false (dead code)
   if (falseGuard) {
       // Never executes
   }
   
   // After - Remove dead code
   // (delete the if block entirely)
   
   // Or restore proper guard
   if (properGuard) {
       // Valid code
   }
   ```

3. **Test:**
   ```bash
   npm test
   ```

**Effort:** 5-10 minutes

---

### Phase 3: LOW Priority Fixes (1-2 hours)

#### 3.1 Remove Unused Variables (22 instances)

**Issue:** Variables declared but never used

**Findings in wordcut.js:**
```
Line 1: module, exports
Line 64: glob
Line 308: WordcutCore
Line 323: self
Line 489: sys
Line 1123: identity (function)
Line 1859: Minimatch
Line 1867: alphasort, alphasorti
Line 2231: newPattern
Line 2332: self
Line 2512: exists
Line 2576: Minimatch, Glob, util
Line 2577: (skipped in prev)
Line 2578: (skipped in prev)
Line 2583: alphasort
Line 2584: alphasorti
Line 2781: abs
Line 2808: stat
Line 2830: entries
Line 2992: exists
```

**Fix Steps:**

1. **Using automated linting (RECOMMENDED):**
   ```bash
   # Install ESLint if not already installed
   npm install --save-dev eslint
   
   # Generate ESLint config
   npx eslint --init
   
   # Find unused variables
   npx eslint site/assets/javascripts/lunr/wordcut.js --fix
   npx eslint site/assets/javascripts/lunr/tinyseg.js --fix
   ```

2. **Manual approach:**
   - Open `wordcut.js`
   - For each unused variable, check:
     - Is it part of API contract? (keep)
     - Is it required for compatibility? (keep)
     - Is it truly unused? (remove)
   - Delete each unused line
   - Test after each removal

3. **Test:**
   ```bash
   npm test
   ```

**Effort:** 1-1.5 hours

---

#### 3.2 Fix Automatic Semicolon Insertion (6 instances)

**Issue:** Inconsistent statement termination

**Findings:**
- wordcut.js: Lines 1193, 4374, 4511
- tinyseg.js: Lines 42, 49, 119

**Fix Steps:**

1. **Choose strategy:** Use semicolons everywhere OR nowhere

2. **Recommended:** Use Prettier to auto-format:
   ```bash
   # Install Prettier
   npm install --save-dev prettier
   
   # Format files
   npx prettier --write site/assets/javascripts/lunr/wordcut.js
   npx prettier --write site/assets/javascripts/lunr/tinyseg.js
   ```

3. **Or manually add semicolons:**
   - Find each line mentioned above
   - Add `;` at end of statement
   - Ensure consistency throughout file

4. **Test:**
   ```bash
   npm test
   ```

**Effort:** 15-30 minutes

---

#### 3.3 Fix Useless Expressions (2 instances)

**Issue:** Expressions with no effect

**Findings:**
- wordcut.js:1683
- wordcut.js:4130

**Fix Steps:**

1. **Open `wordcut.js`**

2. **Find line 1683:**
   ```javascript
   // Before - No effect
   someValue;
   
   // After - Either use it or remove
   result = someValue;
   // OR delete the line
   ```

3. **Find line 4130:** Repeat same pattern

4. **Test:**
   ```bash
   npm test
   ```

**Effort:** 5 minutes

---

#### 3.4 Fix Useless Assignment (1 instance)

**Issue:** Initial value always overwritten

**Finding:**
- wordcut.js:1778

**Fix Steps:**

1. **Open `wordcut.js:1778`:**
   ```javascript
   // Before - Initial value unused
   var abs = initialValue;
   abs = otherValue;  // Always overwritten
   
   // After - Remove unused initial
   var abs;
   abs = otherValue;
   ```

2. **Test:**
   ```bash
   npm test
   ```

**Effort:** 5 minutes

---

#### 3.5 Fix Regex Pattern (1 instance)

**Issue:** Unmatchable regex assertion

**Finding:**
- wordcut.js - Regex with unmatchable caret

**Fix Steps:**

1. **Search for problematic regex in wordcut.js**
2. **Review the pattern and assertion**
3. **Fix the assertion pattern**
4. **Test:** `npm test`

**Effort:** 10-15 minutes

---

### Phase 4: Testing & Verification (30 min)

```bash
# Run full test suite
npm test

# Run specific library tests
npm test -- lunr

# Lint to catch any new issues
npx eslint site/assets/javascripts/lunr/

# Build if applicable
npm run build
```

---

### Phase 5: Re-scan with CodeQL (30 min)

```bash
# Re-run CodeQL analysis to verify fixes
codeql database create codeql-db --language=javascript --source-root=.
codeql database analyze codeql-db codeql/javascript-queries --format=sarif-latest --output=new-results.sarif

# Compare results
codeql tools interpret-results new-results.sarif
```

---

## Issue-by-Issue Checklist

### wordcut.js

**Unused Variables (17):**
- [ ] Line 1: module
- [ ] Line 1: exports
- [ ] Line 64: glob
- [ ] Line 308: WordcutCore
- [ ] Line 323: self
- [ ] Line 489: sys
- [ ] Line 1123: identity
- [ ] Line 1859: Minimatch
- [ ] Line 1867: alphasort
- [ ] Line 1868: alphasorti
- [ ] Line 2231: newPattern
- [ ] Line 2332: self
- [ ] Line 2512: exists
- [ ] Line 2576: Minimatch
- [ ] Line 2577: Glob
- [ ] Line 2578: util
- [ ] Line 2781: abs
- [ ] Line 2808: stat
- [ ] Line 2830: entries
- [ ] Line 2992: exists

**Trivial Conditionals (3):**
- [ ] Line 2505: needDir always true
- [ ] Line 2985: needDir always true
- [ ] Line 3573: inClass always true

**Semicolon Issues (3):**
- [ ] Line 1193: Add semicolon
- [ ] Line 4374: Add semicolon
- [ ] Line 4511: Add semicolon

**Useless Expressions (2):**
- [ ] Line 1683: Remove or use
- [ ] Line 4130: Remove or use

**Other (2):**
- [ ] Line 1778: Remove unused initial value (abs)
- [ ] Regex: Fix unmatchable assertion

### tinyseg.js

**Semicolon Issues (3):**
- [ ] Line 42: Add semicolon
- [ ] Line 49: Add semicolon
- [ ] Line 119: Add semicolon

**Use Before Declaration (1):**
- [ ] Line 117: Move declaration before use

**Unneeded Defensive Code (1):**
- [ ] Line 110: Remove dead code

---

## Git Workflow

```bash
# Create fix branch
git checkout -b fix/codeql-javascript-findings

# Make fixes (follow phases above)
# ... edit files ...

# Stage changes
git add site/assets/javascripts/lunr/

# Verify tests pass
npm test

# Commit fixes
git commit -m "Fix CodeQL JavaScript findings (Lane B - 37 issues)

- Remove unused variables (22)
- Fix trivial conditionals (3)
- Fix semicolon insertion (6)
- Remove useless expressions (2)
- Fix declaration order (1)
- Remove dead code (1)
- Other fixes (1)

All changes in third-party libraries. No security impact."

# Create pull request
git push origin fix/codeql-javascript-findings
```

---

## Rollback Plan

If tests fail after fixes:

```bash
# Revert to original
git checkout site/assets/javascripts/lunr/

# Or specific file
git checkout site/assets/javascripts/lunr/wordcut.js

# Re-run tests
npm test
```

---

## Success Criteria

- [ ] All 37 findings addressed
- [ ] Existing test suite passes
- [ ] No new issues introduced
- [ ] CodeQL re-scan shows 0 findings (or significant reduction)
- [ ] Changes merged to main
- [ ] PR approved and closed

---

## Estimated Timeline

| Phase | Duration | Status |
|-------|----------|--------|
| Phase 1: Assessment | 15 min | ⏳ |
| Phase 2: MEDIUM Fixes | 30-40 min | ⏳ |
| Phase 3: LOW Fixes | 1-1.5 hours | ⏳ |
| Phase 4: Testing | 30 min | ⏳ |
| Phase 5: Re-scan | 30 min | ⏳ |
| **Total** | **~3 hours** | ⏳ |

---

## Dependencies

- Node.js (any LTS version)
- npm or yarn
- ESLint (optional but recommended)
- Prettier (optional but recommended)
- CodeQL (for re-scan verification)

---

## Notes

1. **All findings are in third-party libraries** - Consider updating libraries instead of fixing directly
2. **No security vulnerabilities** - Fixes are optional for functionality
3. **Can be deferred** - Include in regular maintenance cycle
4. **Low risk** - Minimal test coverage required

---

**Generated:** 2026-07-13  
**Status:** Ready for execution
