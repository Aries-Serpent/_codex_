# 🎯 Next Phase Plansets & Promptsets

**Version:** 1.0.0  
**Generated:** 2026-01-06  
**Purpose:** Actionable plansets for continued _codex_ development

---

## Planset 1: Documentation Reorganization (IMMEDIATE)

**Priority:** HIGH  
**Duration:** 2 hours  
**Status:** IN PROGRESS

### Objectives
- Organize root directory documentation
- Create centralized knowledge base
- Archive session-specific documents
- Establish maintainable structure

### Tasks

#### Task 1.1: Create Directory Structure
```bash
mkdir -p .codex/cognitive_brain
mkdir -p .codex/archive/sessions
mkdir -p .codex/archive/historical
mkdir -p .codex/documentation/guides
mkdir -p .codex/documentation/api
```

#### Task 1.2: Move Session Documents
```bash
# Move to archive/sessions/
mv SESSION_*.md .codex/archive/sessions/
mv WORK_COMPLETION_SUMMARY.md .codex/archive/sessions/
mv SESSION_FINAL_COMPLETION_*.md .codex/archive/sessions/
```

#### Task 1.3: Move Historical Documents
```bash
# Move to archive/historical/
mv FIX_PLAN.md .codex/archive/historical/
mv PHASE1_PHASE2_CONTINUATION_ACTIVE.md .codex/archive/historical/
mv CODEGENERATOR_FIX_PLANSET.md .codex/archive/historical/
```

#### Task 1.4: Organize Active Documents
```bash
# Keep in root:
# - README.md
# - CONTRIBUTING.md
# - SECURITY.md
# - QUICKSTART.md
# - CHANGELOG.md
# - COGNITIVE_BRAIN_UNIFIED_V4.md (NEW)

# Move to .codex/cognitive_brain/
mv PHASE2_COMPLETE_100PERCENT.md .codex/cognitive_brain/
mv FINAL_STATUS_PHASE1_93PERCENT.md .codex/cognitive_brain/
mv SELF_REVIEW_ITERATION_4_AND_CONTINUATION.md .codex/cognitive_brain/
```

#### Task 1.5: Create Documentation Index
Create `.codex/README.md` with links to all major documents.

### Validation
- [ ] Root directory has ≤10 .md files
- [ ] All session docs in archive
- [ ] Links verified and updated
- [ ] Documentation index created

### Promptset for AI Agent
```markdown
@copilot Execute documentation reorganization planset:

1. Create directory structure as specified in Planset 1, Task 1.1
2. Move all session documents to .codex/archive/sessions/
3. Move historical plansets to .codex/archive/historical/
4. Organize active cognitive brain docs in .codex/cognitive_brain/
5. Create documentation index at .codex/README.md
6. Update all internal links to reflect new paths
7. Validate organization with checklist

Success criteria:
- Clean root directory (≤10 .md files)
- All documents properly categorized
- No broken links
- Documentation index complete

Commit message: "Docs: Reorganize documentation structure, create centralized knowledge base"
```

---

## Planset 2: PR Review Issue Fixes (QUICK WINS)

**Priority:** HIGH  
**Duration:** 1 hour  
**Status:** NOT STARTED

### Objectives
- Fix all issues identified in PR review
- Improve code quality
- Remove unused code

### Tasks

#### Task 2.1: Fix App.tsx
**File:** `cognitive_app/src/App.tsx:15`  
**Issue:** Unused variable `setGeneratedCode`

**Fix:**
```typescript
// BEFORE:
const [generatedCode, setGeneratedCode] = useState<string>('');

// AFTER:
const [generatedCode] = useState<string>('');
```

#### Task 2.2: Fix CodeGenerator.comprehensive.test.tsx
**File:** `cognitive_app/src/components/code/__tests__/CodeGenerator.comprehensive.test.tsx:343-344`  
**Issue:** Unused variable `initialCheckCount`

**Fix:** Remove the variable declaration or use it in assertions.

#### Task 2.3: Fix CodeGenerator.test.tsx
**File:** `cognitive_app/src/components/code/__tests__/CodeGenerator.test.tsx:344`  
**Issue:** Unused variable `clickSpy`

**Fix:** Either use the spy or remove it.

#### Task 2.4: Fix MetricCard.test.tsx
**File:** `cognitive_app/src/components/quantum/__tests__/MetricCard.test.tsx:1`  
**Issue:** Unused import `vi`

**Fix:**
```typescript
// Remove from imports if not used
import { vi } from 'vitest'; // Remove this line if vi is not used
```

#### Task 2.5: Fix QuantumVisualizer.test.tsx
**File:** `cognitive_app/src/components/quantum/__tests__/QuantumVisualizer.test.tsx:6`  
**Issue:** Unused variable `mockCanvas`

**Fix:** Remove or use the variable.

#### Task 2.6: Fix WorkflowTokenOrchestrator.test.tsx
**File:** `cognitive_app/src/components/quantum/__tests__/WorkflowTokenOrchestrator.test.tsx:2`  
**Issue:** Unused import `fireEvent`

**Fix:**
```typescript
// BEFORE:
import { render, screen, waitFor, fireEvent } from '@testing-library/react';

// AFTER:
import { render, screen, waitFor } from '@testing-library/react';
```

#### Task 2.7: Fix eslint.config.js
**File:** `cognitive_app/eslint.config.js:38`  
**Issue:** Comment doesn't match intent

**Fix:**
```javascript
// BEFORE:
// Allow console in development

// AFTER:
// Allow specific console methods (warn, error, info)
```

### Validation
- [ ] All 7 issues fixed
- [ ] Tests still passing (166/166)
- [ ] Lint check passing
- [ ] Build successful

### Promptset for AI Agent
```markdown
@copilot Fix all PR review issues identified by copilot-pull-request-reviewer:

1. Remove unused variable setGeneratedCode in App.tsx
2. Fix or remove initialCheckCount in CodeGenerator.comprehensive.test.tsx
3. Fix or remove clickSpy in CodeGenerator.test.tsx
4. Remove unused import vi in MetricCard.test.tsx
5. Remove unused variable mockCanvas in QuantumVisualizer.test.tsx
6. Remove unused import fireEvent in WorkflowTokenOrchestrator.test.tsx
7. Update eslint.config.js comment to match intent

After each fix, validate:
- npm test (must still show 166/166 passing)
- npm run lint (must show 0 errors)
- npm run build (must succeed)

Commit message: "Fix: Address PR review issues - remove unused variables and imports"
```

---

## Planset 3: Quantum Framework Testing (SPRINT 2)

**Priority:** HIGH  
**Duration:** 8-10 hours (2 weeks)  
**Status:** NOT STARTED

### Objectives
- Achieve comprehensive test coverage for quantum framework
- Validate mathematical correctness
- Ensure integration stability

### Test Categories

#### Category 1: QuantumAgent Unit Tests (20 tests)
```typescript
describe('QuantumAgent', () => {
  // Configuration
  test('should initialize with valid configuration');
  test('should validate required configuration fields');
  test('should reject invalid configuration');
  test('should deep clone configuration to prevent mutation');
  
  // Energy Computation
  test('should compute energy correctly for standard config');
  test('should respect energy weights (λ values)');
  test('should handle edge cases (zero weights, extreme values)');
  test('should compute energy components independently');
  
  // Optimization
  test('should optimize configuration to reduce energy');
  test('should respect domain constraints (Ω)');
  test('should converge to stable configuration');
  test('should handle multiple optimization runs');
  
  // Response Generation
  test('should generate responses using policy function');
  test('should apply capability operators correctly');
  test('should handle empty/invalid queries gracefully');
  test('should respect source constraints');
  
  // State Management
  test('should maintain configuration state');
  test('should update state atomically');
  test('should rollback on failed optimizations');
  test('should persist state correctly');
});
```

#### Category 2: Energy Computation Tests (15 tests)
```typescript
describe('Energy Computation', () => {
  // Hallucination Loss
  test('should compute hallucination loss for source alignment');
  test('should penalize responses not grounded in sources');
  test('should reward accurate source citations');
  
  // Formatting Loss
  test('should compute formatting loss for structure');
  test('should validate output format compliance');
  test('should handle multiple format requirements');
  
  // Source Compliance Loss
  test('should compute source compliance score');
  test('should measure relevance to query');
  test('should handle multiple sources correctly');
  
  // Coherence Loss
  test('should compute coherence for response quality');
  test('should measure internal consistency');
  test('should detect contradictions');
  
  // Integration
  test('should combine all loss components correctly');
  test('should respect weight configuration');
  test('should normalize energy values appropriately');
});
```

#### Category 3: Source Projection Tests (10 tests)
```typescript
describe('Source Hilbert Space Projections', () => {
  test('should project query onto source basis');
  test('should compute inner products correctly');
  test('should rank sources by relevance');
  test('should handle orthogonal sources');
  test('should normalize projection vectors');
  test('should support dynamic source addition');
  test('should handle source removal gracefully');
  test('should compute superposition of sources');
  test('should measure entanglement between sources');
  test('should validate Hilbert space properties');
});
```

#### Category 4: Policy Function Tests (15 tests)
```typescript
describe('Policy Function', () => {
  // Basics
  test('should implement softmax correctly');
  test('should generate valid probability distributions');
  test('should respect temperature parameter');
  
  // Response Selection
  test('should select high-probability responses');
  test('should support sampling from distribution');
  test('should handle deterministic selection');
  
  // Conditioning
  test('should condition on sources correctly');
  test('should apply capability operators');
  test('should integrate query context');
  
  // Edge Cases
  test('should handle empty response candidates');
  test('should gracefully degrade on failures');
  test('should validate response constraints');
  
  // Performance
  test('should compute policy efficiently');
  test('should scale with number of candidates');
  test('should support batched policy computation');
});
```

#### Category 5: Integration Tests (10 tests)
```typescript
describe('Quantum Framework Integration', () => {
  // With AI Generation Layer
  test('should integrate with SparkLLMClient');
  test('should enhance code generation quality');
  test('should reduce hallucinations measurably');
  
  // With Agent Orchestration
  test('should select optimal agents by energy');
  test('should coordinate multiple agents');
  test('should handle agent failures gracefully');
  
  // With Quantum Processing
  test('should leverage quantum visualization');
  test('should display energy metrics in UI');
  test('should support real-time optimization monitoring');
  
  // End-to-End
  test('should complete full query-response cycle');
});
```

### Implementation Strategy

**Week 1:**
- Days 1-2: Categories 1-2 (Unit tests + Energy)
- Days 3-4: Category 3 (Source projections)
- Day 5: Review and refinement

**Week 2:**
- Days 1-2: Category 4 (Policy functions)
- Days 3-4: Category 5 (Integration)
- Day 5: Full suite validation + documentation

### Validation
- [ ] 70 new tests implemented
- [ ] All tests passing
- [ ] 100% coverage maintained
- [ ] Documentation updated
- [ ] Performance benchmarks established

### Promptset for AI Agent
```markdown
@copilot Implement comprehensive quantum framework testing per Planset 3:

**Week 1 Tasks:**
1. Create test file: quantum-agent-framework.test.ts
2. Implement Category 1: QuantumAgent unit tests (20 tests)
3. Implement Category 2: Energy computation tests (15 tests)
4. Implement Category 3: Source projection tests (10 tests)
5. Validate all pass, update documentation

**Week 2 Tasks:**
1. Implement Category 4: Policy function tests (15 tests)
2. Implement Category 5: Integration tests (10 tests)
3. Run full suite: npm test (expect 236/236 passing)
4. Update COGNITIVE_BRAIN_UNIFIED_V4.md with results
5. Create performance benchmarks

Success criteria:
- 70 new tests passing
- 100% coverage maintained (now 236/236 total)
- Mathematical correctness validated
- Integration stability confirmed

Commit after each category completion with descriptive messages.
```

---

## Planset 4: Performance Optimization (SPRINT 3)

**Priority:** MEDIUM  
**Duration:** 10 hours (2 weeks)  
**Status:** NOT STARTED

### Objectives
- Reduce bundle size to <500KB
- Improve load time to <3s
- Implement progressive loading

### Tasks

#### Task 4.1: Bundle Analysis
```bash
cd cognitive_app
npm run build -- --report
# Analyze bundle composition
# Identify largest dependencies
# Find optimization opportunities
```

#### Task 4.2: Code Splitting
```typescript
// Implement lazy loading for routes
import { lazy, Suspense } from 'react';

const CodeGenerator = lazy(() => import('./components/code/CodeGenerator'));
const InteractiveDemo = lazy(() => import('./components/code/InteractiveDemo'));
const QuantumVisualizer = lazy(() => import('./components/quantum/QuantumVisualizer'));

// Use with Suspense
<Suspense fallback={<Loading />}>
  <CodeGenerator />
</Suspense>
```

#### Task 4.3: Tree Shaking
- Review imports for unused exports
- Use named imports instead of default
- Configure Vite for optimal tree shaking

#### Task 4.4: Asset Optimization
- Compress images (WebP format)
- Minify SVGs
- Optimize fonts (subset, woff2)

#### Task 4.5: Service Worker
```typescript
// Implement offline support
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js');
}
```

### Target Metrics
- Bundle size: 788.90 kB → <500 kB (36% reduction)
- Load time: Current → <3s (p95)
- Lighthouse score: → >90

### Validation
- [ ] Bundle size <500KB
- [ ] Load time <3s (p95)
- [ ] Lighthouse score >90
- [ ] All tests still passing
- [ ] No functionality regressions

### Promptset for AI Agent
```markdown
@copilot Execute performance optimization planset (Sprint 3):

**Week 1: Analysis & Code Splitting**
1. Run bundle analysis: npm run build -- --report
2. Identify top 10 largest dependencies
3. Implement code splitting for all routes
4. Implement lazy loading for heavy components
5. Validate: tests passing, functionality intact

**Week 2: Optimization & Service Worker**
1. Configure Vite for optimal tree shaking
2. Optimize all images (WebP, compression)
3. Minify and optimize SVGs
4. Implement service worker for offline support
5. Validate: bundle <500KB, load time <3s

Success criteria:
- Bundle size reduced by 36% (to <500KB)
- Load time <3s (p95)
- Lighthouse score >90
- 166/166 tests still passing
- No functionality lost

Create performance report with before/after metrics.
```

---

## Planset 5: Production Deployment (HUMAN ADMIN)

**Priority:** HIGH  
**Duration:** 2 hours  
**Status:** READY FOR HUMAN ADMIN

### Prerequisites
- ✅ PR #2714 ready to merge
- ✅ All tests passing (166/166)
- ✅ Build successful
- ✅ Documentation complete

### Human Admin Tasks

#### Step 1: Merge PR
```bash
# On GitHub web interface:
1. Navigate to PR #2714
2. Review final changes
3. Click "Merge pull request"
4. Confirm merge to main branch
5. Delete feature branch (optional)
```

#### Step 2: Verify GitHub Pages
```bash
# On GitHub repository settings:
1. Navigate to Settings > Pages
2. Verify source: Deploy from branch
3. Branch: main
4. Folder: / (root)
5. Save if not already configured
```

#### Step 3: Monitor Deployment
```bash
# On GitHub Actions tab:
1. Watch for deployment workflow
2. Verify successful completion
3. Note any errors or warnings
```

#### Step 4: Validate Deployment
```bash
# In browser:
1. Navigate to: https://aries-serpent.github.io/_codex_/cognitive_app/
2. Verify app loads correctly
3. Test key features:
   - Code generation
   - Interactive demo
   - Quantum visualization
4. Check browser console for errors
```

#### Step 5: Post-Deployment
```bash
# Optional monitoring setup:
1. Configure error tracking (Sentry/similar)
2. Set up analytics (Google Analytics/similar)
3. Create deployment announcement
4. Update README with live URL
```

### Rollback Plan
If issues are found:
1. Revert merge commit on main
2. Push to trigger redeployment
3. Investigate issues offline
4. Fix and re-attempt deployment

---

## Master Promptset for Continued Development

```markdown
@copilot Continue _codex_ development following unified cognitive brain roadmap:

## Context
- Repository: Aries-Serpent/_codex_
- Current Status: 100% test coverage, quantum framework integrated, production ready
- Documentation: COGNITIVE_BRAIN_UNIFIED_V4.md (central hub)
- Roadmap: .codex/plans/COGNITIVE_BRAIN_ROADMAP_2026.md

## Current Sprint: Documentation & Quality (Week 1-2)

Execute plansets in order:
1. Planset 1: Documentation reorganization (2 hours)
2. Planset 2: PR review issue fixes (1 hour)
3. Update status documents
4. Commit with clear messages

## Next Sprint: Quantum Testing (Week 3-4)

Execute:
1. Planset 3: Quantum framework testing (10 hours)
2. Achieve 70 new tests
3. Maintain 100% coverage
4. Update cognitive brain status

## Success Criteria
- Clean, organized documentation structure
- All PR review issues resolved
- 70+ quantum tests passing
- 100% coverage maintained
- Clear path to Q2 milestones

## Guidelines
- Follow AI AGENT POLICY (no deferral)
- Validate after each major change
- Update documentation continuously
- Commit incrementally with descriptive messages
- Report progress using report_progress tool

## References
- Central Hub: COGNITIVE_BRAIN_UNIFIED_V4.md
- Roadmap: .codex/plans/COGNITIVE_BRAIN_ROADMAP_2026.md
- Status: .codex/reports/REPOSITORY_STATUS_MATRIX.md
- This File: .codex/plans/NEXT_PHASE_PLANSETS.md

Execute systematically. Do not defer work. Update cognitive brain after each milestone.
```

---

## Conclusion

These plansets provide clear, actionable paths for continued _codex_ development. Each planset includes:
- Clear objectives
- Detailed tasks
- Validation criteria
- Promptsets for AI agents
- Time estimates
- Priority levels

The phased approach ensures manageable scope while maintaining the high quality standards established in Phases 1-3.

**Next Actions:**
1. Execute Planset 1 (Documentation) - IMMEDIATELY
2. Execute Planset 2 (PR fixes) - WEEK 1
3. Human admin: Execute Planset 5 (Deployment) - WEEK 1
4. Execute Planset 3 (Quantum tests) - WEEK 3-4
5. Execute Planset 4 (Performance) - WEEK 5-6

---

*Created by: AI Agent*  
*Date: 2026-01-06*  
*Version: 1.0.0*
