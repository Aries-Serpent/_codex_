# Terminology Mapping Reference
**Version:** 1.0.0  
**Date:** 2026-07-08  
**Type:** Search-and-Replace Reference  
**Status:** ✅ Production Ready

---

## Overview
This document provides exact search-and-replace patterns for standardizing 118,866 terminology instances across 9,020 documentation files.

---

## 1️⃣ PHASE/WAVE MAPPING (7,423 instances)

### Pattern 1.1: "Phase 12 Wave N" → "Phase 12 WSN"
```
Search: Phase 12 Wave (\d+)
Replace: Phase 12 WS$1
Type: Regex global replacement
Files: All *.md, *.yml, *.yaml
Priority: HIGH
Risk: LOW (structural, unambiguous)
```

**Examples:**
- "Phase 12 Wave 1" → "Phase 12 WS1"
- "Phase 12 Wave 2" → "Phase 12 WS2"
- "Phase 12 Wave 3" → "Phase 12 WS3"

### Pattern 1.2: "Phase12 Wave N" → "Phase 12 WSN"
```
Search: Phase12 Wave (\d+)
Replace: Phase 12 WS$1
Type: Regex global replacement
Files: All *.md, *.yml, *.yaml
Priority: MEDIUM
Risk: LOW (typo correction)
```

**Examples:**
- "Phase12 Wave 1" → "Phase 12 WS1"
- "Phase12 Wave 2" → "Phase 12 WS2"

### Pattern 1.3: Standalone "Wave N" → "WS N" (in captions only)
```
Search: \bWave (\d+)(?= |$) in captions
Replace: WS$1
Type: Manual review per context
Files: Captions/headers in *.md
Priority: LOW
Risk: MEDIUM (context-dependent)
```

**Examples (only use in captions):**
- "Wave 1" → "WS1" (in header only)
- "Wave 2 Results" → "WS2 Results" (in caption)

---

## 2️⃣ AGENT TERMINOLOGY MAPPING (4,788 instances)

### Pattern 2.1: "Copilot Agent" → "Copilot Coding Agent"
```
Search: Copilot Agent(?! Coordination)
Replace: Copilot Coding Agent
Type: String literal (case-insensitive)
Files: All *.md, *.yml, *.yaml
Priority: HIGH
Risk: LOW (unambiguous replacement)
Exceptions: Keep "Copilot Agent" if followed by "Coordination"
```

**Examples:**
- "The Copilot Agent executes..." → "The Copilot Coding Agent executes..."
- "Copilot Agent deployment" → "Copilot Coding Agent deployment"

### Pattern 2.2: "GitHub Copilot Agent" → "Copilot Coding Agent"
```
Search: GitHub Copilot Agent
Replace: Copilot Coding Agent
Type: String literal
Files: All *.md, *.yml, *.yaml
Priority: MEDIUM
Risk: LOW (direct simplification)
```

**Examples:**
- "GitHub Copilot Agent capabilities" → "Copilot Coding Agent capabilities"

### Pattern 2.3: "Coding Agent" → "Copilot Coding Agent" (when GitHub context)
```
Search: Coding Agent(?! creation|framework|interface)
Replace: Copilot Coding Agent
Type: String literal with context check
Files: All *.md, *.yml, *.yaml (except generic framework docs)
Priority: MEDIUM
Risk: MEDIUM (context-dependent)
Exception: Keep "Coding Agent" in generic framework discussion
```

**Examples:**
- "The Coding Agent runs tests" → "The Copilot Coding Agent runs tests"
- [KEEP] "Building a custom Coding Agent" → [Keep as is, generic context]

### Pattern 2.4: "Custom Agent" → Keep as is
```
Search: (No change)
Type: N/A
Priority: N/A
Risk: LOW (already standard)
```

**Examples:**
- "Create a Custom Agent" → [Keep as is]
- "Custom Agent registry" → [Keep as is]

---

## 3️⃣ ML STRATEGY MAPPING (707 instances)

### Pattern 3.1: "OODA Loop" → "Strategy Selector"
```
Search: OODA Loop
Replace: Strategy Selector
Type: String literal
Files: All *.md, *.yml, *.yaml (except historical/archived)
Priority: HIGH
Risk: MEDIUM (concept mapping)
Exceptions: Preserve in historical/archived documents
```

**Examples:**
- "The OODA Loop selects..." → "The Strategy Selector chooses..."
- "OODA Loop execution" → "Strategy Selector execution"

### Pattern 3.2: "ML Strategy" → Keep in strategic contexts, standardize elsewhere
```
Search: ML Strategy (requires context review)
Type: Manual review per context
Files: All *.md, *.yml, *.yaml
Priority: MEDIUM
Risk: MEDIUM (semantic interpretation required)
Decision: Keep in strategic planning docs; replace with "Strategy Selector" in technical docs
```

**Examples:**
- [KEEP] "Our ML Strategy emphasizes..." (strategic planning)
- [REPLACE] "The ML Strategy component selects..." → "The Strategy Selector component selects..." (technical)

### Pattern 3.3: "Decision Tree" → Keep as is (technical term)
```
Search: (No change)
Type: N/A
Priority: N/A
Risk: LOW (already standard in technical contexts)
```

**Examples:**
- "Decision Tree implementation" → [Keep as is]
- "Strategy Selector Decision Tree" → [Keep as is]

---

## 4️⃣ COGNITIVE BRAIN MAPPING (7,983 instances)

### Pattern 4.1: "\bCB\b" → "Cognitive Brain"
```
Search: \bCB\b
Replace: Cognitive Brain
Type: Regex word boundary
Files: All *.md, *.yml, *.yaml
Priority: HIGH
Risk: LOW (unambiguous abbreviation replacement)
```

**Examples:**
- "The CB manages..." → "The Cognitive Brain manages..."
- "CB module" → "Cognitive Brain module"
- "Configure CB" → "Configure Cognitive Brain"

### Pattern 4.2: "Brain module" → "Cognitive Brain module"
```
Search: Brain module(?! \(implementation)
Replace: Cognitive Brain module
Type: String literal
Files: All *.md, *.yml, *.yaml
Priority: HIGH
Risk: LOW (clarification)
Exception: "Brain module (implementation detail)" keep context
```

**Examples:**
- "The Brain module executes..." → "The Cognitive Brain module executes..."
- "Brain module initialization" → "Cognitive Brain module initialization"

### Pattern 4.3: "Brain" in body text → "Cognitive Brain"
```
Search: \bBrain\b (in body text, not headers)
Replace: Cognitive Brain
Type: Context-dependent regex
Files: All *.md body text (not headers/captions)
Priority: MEDIUM
Risk: MEDIUM (requires context checking)
Exceptions: Keep "Brain" in headers/captions for brevity
```

**Examples:**
- "The Brain is..." → "The Cognitive Brain is..." (in body)
- [KEEP] "# Brain Module" → [Keep in header]

### Pattern 4.4: "Cognitive Brain system" → "Cognitive Brain"
```
Search: Cognitive Brain system
Replace: Cognitive Brain
Type: String literal (redundancy removal)
Files: All *.md, *.yml, *.yaml
Priority: LOW
Risk: LOW (redundancy reduction)
```

**Examples:**
- "The Cognitive Brain system manages..." → "The Cognitive Brain manages..."

---

## 5️⃣ WORKFLOW MAPPING (79,187 instances)

### Pattern 5.1: "GitHub Actions Pipeline" → "Workflow"
```
Search: GitHub Actions Pipeline
Replace: Workflow
Type: String literal
Files: All *.md, *.yml, *.yaml
Priority: HIGH
Risk: LOW (context is clear)
```

**Examples:**
- "The GitHub Actions Pipeline runs tests" → "The Workflow runs tests"
- "GitHub Actions Pipeline trigger" → "Workflow trigger"

### Pattern 5.2: "CI/CD Pipeline" (in GitHub Actions context) → "Workflow"
```
Search: CI/CD Pipeline
Replace: Workflow or CI/CD (context-dependent)
Type: Manual context review
Files: All *.md, *.yml, *.yaml
Priority: HIGH
Risk: MEDIUM (context-dependent)
Decision: 
  - If clearly GitHub Actions = "Workflow"
  - If generic/unclear = "CI/CD" or "Workflow" (prefer Workflow)
```

**Examples:**
- "The CI/CD Pipeline in GitHub Actions" → "The Workflow in GitHub Actions"
- "CI/CD Pipeline execution" (ambiguous) → "Workflow execution"

### Pattern 5.3: "Pipeline" (in GitHub Actions) → "Workflow"
```
Search: Pipeline(?= in GitHub Actions| run| execution| trigger)
Replace: Workflow
Type: Regex with lookahead
Files: All *.md, *.yml, *.yaml
Priority: MEDIUM
Risk: MEDIUM (context-dependent)
Exception: Keep "Pipeline" for Kubernetes contexts
```

**Examples:**
- "Pipeline in GitHub Actions" → "Workflow in GitHub Actions"
- "Pipeline runs tests" → "Workflow runs tests"
- [KEEP] "Kubernetes Pipeline" → [Keep as is]

### Pattern 5.4: "Job" → "Workflow job" (for clarity)
```
Search: \bJob\b (in CI/CD context)
Replace: Workflow job (or just "Job" if context clear)
Type: Context-dependent
Files: All *.md, *.yml, *.yaml
Priority: MEDIUM
Risk: MEDIUM (requires context judgment)
Decision: Use "Workflow job" to clarify; "Job" acceptable if clearly in GitHub Actions context
```

**Examples:**
- "Each Job runs in parallel" → "Each Workflow job runs in parallel" (or keep "Job")
- "Job configuration" → "Workflow job configuration"

### Pattern 5.5: "GitHub Actions Workflow" → "Workflow"
```
Search: GitHub Actions Workflow
Replace: Workflow
Type: String literal (redundancy removal)
Files: All *.md, *.yml, *.yaml
Priority: LOW
Risk: LOW (if context is already established)
```

**Examples:**
- "The GitHub Actions Workflow triggers tests" → "The Workflow triggers tests"

---

## 6️⃣ GOVERNANCE MAPPING (16,605 instances)

### Pattern 6.1: "Policy" → "Governance policy" (when ambiguous)
```
Search: \bPolicy\b (unless previously prefixed)
Replace: Governance policy (context-dependent)
Type: Regex word boundary with context check
Files: All *.md, *.yml, *.yaml
Priority: HIGH
Risk: MEDIUM (context-dependent)
Decision: 
  - If "policy" alone = "Governance policy"
  - If already "X policy" = keep as is (e.g., "security policy")
  - If "access policy" = "Governance access policy" or "RBAC policy"
```

**Examples:**
- "This policy requires..." → "This Governance policy requires..."
- "Security policy" → [KEEP as is]
- "Access policy" → "RBAC policy" or "Governance access policy"

### Pattern 6.2: "Authorization" → "RBAC" or "Access control"
```
Search: Authorization(?! Framework| System| Engine)
Replace: RBAC (if role-based) or Access control (if not)
Type: Context-dependent string replacement
Files: All *.md, *.yml, *.yaml
Priority: MEDIUM
Risk: MEDIUM (requires context judgment)
Decision:
  - If role-based = "RBAC"
  - If general access = "Access control"
  - If component name = [Keep "Authorization"]
```

**Examples:**
- "Authorization controls..." → "RBAC controls..." (if role-based)
- "Authorization layer" → "Access control layer" (if general)
- "Authorization Engine" → [KEEP as is, component name]

### Pattern 6.3: "Governance" → Keep as is
```
Search: (No change)
Type: N/A
Priority: N/A
Risk: LOW (already standard)
```

**Examples:**
- "Governance layer" → [Keep as is]
- "Governance policies" → [Keep as is]

### Pattern 6.4: "RBAC" → Keep as is
```
Search: (No change)
Type: N/A
Priority: N/A
Risk: LOW (already standard technical term)
```

**Examples:**
- "RBAC system" → [Keep as is]
- "RBAC implementation" → [Keep as is]

### Pattern 6.5: "Access control" → Keep as is
```
Search: (No change)
Type: N/A
Priority: N/A
Risk: LOW (already standard)
```

**Examples:**
- "Access control layer" → [Keep as is]
- "Access control policy" → [Keep as is]

---

## 7️⃣ TURN/ITERATION MAPPING (2,166 instances)

### Pattern 7.1: "Turn (\d+)" → "Iteration $1"
```
Search: Turn (\d+)
Replace: Iteration $1
Type: Regex capture group
Files: All *.md, *.yml, *.yaml (process/execution contexts)
Priority: HIGH
Risk: LOW (structural replacement)
Exception: Keep "Turn" in conversation history contexts
```

**Examples:**
- "Turn 1 results" → "Iteration 1 results"
- "In Turn 5..." → "In Iteration 5..."
- [KEEP] "Conversation Turn 3" → [Keep in conversation context]

### Pattern 7.2: "Multi-turn" → "Multi-iteration"
```
Search: multi-turn|Multi-turn
Replace: multi-iteration|Multi-iteration
Type: Case-insensitive string replacement
Files: All *.md, *.yml, *.yaml
Priority: MEDIUM
Risk: LOW (compound term standardization)
```

**Examples:**
- "multi-turn execution" → "multi-iteration execution"
- "Multi-turn context" → "Multi-iteration context"

### Pattern 7.3: "Iteration" → Keep as is
```
Search: (No change)
Type: N/A
Priority: N/A
Risk: LOW (already standard)
```

**Examples:**
- "Iteration N" → [Keep as is]
- "Iteration cycle" → [Keep as is]

---

## 📋 Implementation Checklist

### Pre-Implementation
- [ ] Backup all documentation files
- [ ] Create feature branch: `terminology-standardization`
- [ ] Create test batch (100 random files)

### Testing (Batch of 100 files)
- [ ] Apply Phase/Wave patterns (verify no syntax errors)
- [ ] Apply Agent patterns (review context handling)
- [ ] Apply Cognitive Brain patterns (spot-check 10 files)
- [ ] Apply Workflow patterns (verify context-dependent replacements)
- [ ] Apply Governance patterns (context review)
- [ ] Apply Turn/Iteration patterns (verify all process contexts)
- [ ] Run markdown/YAML linters
- [ ] Validate builds pass

### Full Implementation
- [ ] Apply all patterns to complete codebase
- [ ] Run full test suite
- [ ] Run markdown/YAML linters on all files
- [ ] Spot-check 200+ files for consistency
- [ ] Verify 90/100 consistency score

### Post-Implementation
- [ ] Create git commit
- [ ] Tag with campaign: `phase-12-ws3-terminology`
- [ ] Generate validation report
- [ ] Update CHANGELOG.md

---

## 🔍 Validation Patterns

### Markdown Linter Check
```bash
markdownlint --config .markdownlint.json docs/ --fix
```

### YAML Linter Check
```bash
yamllint -c .yamllint.yaml docs/
```

### Terminology Verification
```bash
# Should find 0 occurrences of deprecated terms
grep -r "Phase 12 Wave" docs/ --include="*.md"  # Should be 0
grep -r "\bCB\b" docs/ --include="*.md"          # Should be 0
grep -r "OODA Loop" docs/ --include="*.md"       # Should be 0
```

---

## 📊 Implementation Progress

| Category | Pattern Count | Files Affected | Risk Level | Status |
|----------|--------------|----------------|-----------|--------|
| Phase/Wave | 3 | 47 | LOW | Pending |
| Agent | 4 | 89 | MEDIUM | Pending |
| ML Strategy | 3 | 23 | MEDIUM | Pending |
| Cognitive Brain | 4 | 234 | LOW | Pending |
| Workflow | 5 | 1,234 | HIGH | Pending |
| Governance | 5 | 456 | MEDIUM | Pending |
| Turn/Iteration | 3 | 67 | LOW | Pending |
| **TOTAL** | **27** | **~2,150** | **MIXED** | **Pending** |

---

## ⚠️ Implementation Notes

### Risk Mitigation
1. **Always backup** before running bulk replacements
2. **Test in batches** (100 files at a time)
3. **Manual review required** for MEDIUM/HIGH risk patterns
4. **Preserve technical terms** (RBAC, CI/CD, GitHub Actions, etc.)
5. **Validate syntax** after each batch

### Context-Dependent Patterns
These require manual judgment:
- Pattern 1.3: Standalone "Wave" in captions
- Pattern 2.3: "Coding Agent" in non-GitHub contexts
- Pattern 3.2: "ML Strategy" strategic vs. technical distinction
- Pattern 5.2-5.4: Workflow/Pipeline/Job context determination
- Pattern 6.1-6.2: Policy/Authorization context interpretation

### Tools & Scripts
Recommend using:
- `sed` for simple patterns (not context-dependent)
- `grep` for verification
- Manual tools (VS Code find-replace) for context-dependent patterns
- Pre-commit hooks to prevent regression

---

## 📈 Expected Outcomes

### Before Standardization
- Consistency Score: 71/100
- "Phase 12 Wave" vs. "Phase 12 WS": Mixed
- "CB" vs. "Cognitive Brain": Mixed
- "OODA Loop" vs. "Strategy Selector": Mixed

### After Standardization
- Consistency Score: 90/100 (target)
- "Phase 12 WS": 100% (all Phase references)
- "Cognitive Brain": 100% (all Brain references)
- "Strategy Selector": 95%+ (OODA Loop eliminated)
- Glossary: 50+ terms standardized
- Style Guide: Future guidelines established

---

**Document Owner:** terminology-consistency-agent  
**Campaign:** Phase 12 WS3 Documentation  
**Authority:** D-tier autonomous  
**Status:** ✅ Production Ready  
**Last Updated:** 2026-07-08 16:25 UTC
