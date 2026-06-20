# 🎴 AGENT QUICK REFERENCE CARD

**Version:** 2.0.0  
**Generated:** 2026-06-20T06:54:05.369029  
**Purpose:** One-page cheat sheet for common tasks

---

## 🏆 TOP 10 MOST-USED AGENTS

### 1. unified-coverage-agent
```
Task: Improve test coverage
Usage: 50+ times/month
Command: @copilot use unified-coverage-agent
Mode: gap-fill, maintain, monitor, roadmap
Time: 5-15 min
Cost: ~$0.05
Model: Haiku 4.5
```

### 2. unified-security-scanner
```
Task: Security scanning (SAST + deps + secrets)
Usage: 40+ times/month
Command: @copilot use unified-security-scanner
Mode: sast, dependency, secrets, full-audit
Time: 20-45 min
Cost: ~$0.20
Model: Sonnet 4.6
```

### 3. github-guru-agent
```
Task: PR analysis & issue triage
Usage: 30+ times/month
Command: @copilot use github-guru-agent
Focus: analysis, triage, governance
Time: 3-5 min
Cost: <$0.01
Model: Haiku 4.5
```

### 4. autonomous-test-healer-agent
```
Task: Heal failing tests automatically
Usage: 25+ times/month
Command: @copilot use autonomous-test-healer-agent
Mode: diagnose, fix, verify
Time: 10-30 min
Cost: ~$0.15
Model: Sonnet 4.6
```

### 5. unified-doc-agent
```
Task: Documentation consolidation & quality
Usage: 20+ times/month
Command: @copilot use unified-doc-agent
Mode: consolidate, quality, freshness, align
Time: 10-30 min
Cost: ~$0.10
Model: Sonnet 4.6
```

### 6. ci-failure-resolution-agent
```
Task: Fix CI/CD pipeline failures
Usage: 20+ times/month
Command: @copilot use ci-failure-resolution-agent
Mode: diagnose, heal, verify
Time: 5-10 min
Cost: ~$0.10
Model: Sonnet 4.6
```

### 7. repository-hygiene-agent
```
Task: Repository cleanup & organization
Usage: 15+ times/month
Command: @copilot use repository-hygiene-agent
Focus: cleanup, hygiene, deprecation
Time: 10-20 min
Cost: ~$0.05
Model: Haiku 4.5
```

### 8. code-analysis-agent
```
Task: Static code analysis
Usage: 15+ times/month
Command: @copilot use code-analysis-agent
Focus: patterns, quality, anti-patterns
Time: 5-10 min
Cost: ~$0.05
Model: Haiku 4.5
```

### 9. fragile-test-guardian
```
Task: Detect and stabilize flaky tests
Usage: 10+ times/month
Command: @copilot use fragile-test-guardian
Mode: detect, stabilize, monitor
Time: 10-20 min
Cost: ~$0.15
Model: Sonnet 4.6
```

### 10. policy-coach-agent
```
Task: Policy validation & coaching
Usage: 10+ times/month
Command: @copilot use policy-coach-agent
Focus: validation, coaching, governance
Time: 1-2 min
Cost: <$0.01
Model: Haiku 4.5
```

---

## 🚀 QUICK TASK LOOKUP

### "My tests are failing"
→ fragile-test-guardian (if flaky) OR autonomous-test-healer-agent (if real)

### "Coverage is too low"
→ unified-coverage-agent (gap-fill mode)

### "CI/CD is broken"
→ ci-failure-resolution-agent (or ci-emergency-response-agent if critical)

### "I need security scanning"
→ unified-security-scanner (full mode)

### "Documentation is outdated"
→ unified-doc-agent (alignment mode)

### "PR needs review"
→ github-guru-agent (analysis mode)

### "Code quality check"
→ code-analysis-agent (patterns mode)

### "Repository cleanup"
→ repository-hygiene-agent

### "Policy enforcement"
→ policy-coach-agent or unified-governance-gate

### "Performance optimization"
→ cache-management-agent or performance-monitor-agent

---

## 📊 MODEL SELECTION

### Use Haiku 4.5 (Cheap, Fast)
- Simple checks (policy, validation)
- Straightforward analysis (code review)
- Quick fixes (config validation)
- Pre-commit gates
- **Agents:** policy-coach-agent, github-guru-agent, code-analysis-agent, etc

### Use Sonnet 4.6 (Smart, Thorough)
- Complex analysis (security, coverage)
- Multi-step reasoning (CI healing, test fixing)
- Comprehensive reports
- Pre-release audits
- **Agents:** unified-security-scanner, autonomous-test-healer-agent, unified-doc-agent, etc

---

## ⏱️ RUNTIME ESTIMATES

| Task | Agent | Time | Model |
|------|-------|------|-------|
| Quick lint | policy-coach-agent | <1 min | Haiku |
| PR analysis | github-guru-agent | 3 min | Haiku |
| Secret scan | secret-detection-agent | 3 min | Haiku |
| Code analysis | code-analysis-agent | 5 min | Haiku |
| CI fix | ci-failure-resolution-agent | 8 min | Sonnet |
| Coverage analysis | unified-coverage-agent | 10 min | Haiku |
| Test healing | autonomous-test-healer-agent | 15 min | Sonnet |
| Security scan | unified-security-scanner | 25 min | Sonnet |
| Full audit | unified-security-scanner | 45 min | Sonnet |

---

## 💰 COST ESTIMATES

| Profile | Agents | Time | Cost |
|---------|--------|------|------|
| Fast | 3 quick agents | 5 min | <0.01 |
| Standard | 5 agents | 15 min | ~0.10 |
| Comprehensive | 8 agents | 40 min | ~0.50 |
| Critical | 10+ agents | 60+ min | >1.00 |

---

## 🎯 COMMON WORKFLOWS

### Workflow 1: Every Commit (2 min)
```
1. policy-coach-agent
2. secret-detection-agent
3. link-validator (basic)
Cost: <$0.01
```

### Workflow 2: Every PR (10 min)
```
1. github-guru-agent (analysis)
2. code-analysis-agent (quality)
3. test-alignment-fixer (if code changed)
Cost: ~$0.05
```

### Workflow 3: Pre-Merge (20 min)
```
1. autonomous-test-healer-agent (tests)
2. unified-coverage-agent (coverage check)
3. ci-failure-resolution-agent (CI)
Cost: ~$0.20
```

### Workflow 4: Pre-Release (45 min)
```
1. unified-security-scanner (full)
2. mutation-testing-agent (quality)
3. autonomous-test-healer-agent (tests)
4. unified-doc-agent (documentation)
Cost: ~$0.50
```

---

## 🔥 WHEN TO USE TOP AGENTS

### unified-coverage-agent
**When:** Coverage below threshold  
**Impact:** High (coverage gate blocker)  
**Time:** 10 min  
**Frequency:** Every sprint

### unified-security-scanner
**When:** Before release  
**Impact:** Critical (security gate)  
**Time:** 30 min  
**Frequency:** Before merge + release

### autonomous-test-healer-agent
**When:** Tests failing  
**Impact:** High (CI blocker)  
**Time:** 15 min  
**Frequency:** As needed (daily during active development)

### unified-doc-agent
**When:** Post-merge or on request  
**Impact:** Medium (doc consistency)  
**Time:** 20 min  
**Frequency:** Weekly

### github-guru-agent
**When:** PR review needed  
**Impact:** Medium (PR quality)  
**Time:** 5 min  
**Frequency:** Every PR

---

## 🎮 ACTIVATION EXAMPLES

### Example 1: Fix Failing Test
```bash
@copilot use autonomous-test-healer-agent
Task: "Fix failing tests in test_auth.py after authentication refactor"
```

### Example 2: Improve Coverage
```bash
@copilot use unified-coverage-agent
Task: "Increase coverage for src/auth/ from 42% to 80%"
Mode: gap-fill
```

### Example 3: Security Scan
```bash
@copilot use unified-security-scanner
Task: "Full security scan of PR #1234 before merging to main"
Mode: full-audit
```

### Example 4: Analyze PR
```bash
@copilot use github-guru-agent
Task: "Analyze PR #5000 for code quality, testing, and architecture"
```

---

## 📋 DECISION MATRIX

| Need | Agent | Time | Cost | Model |
|------|-------|------|------|-------|
| Policy check | policy-coach-agent | 1m | <0.01 | Haiku |
| PR review | github-guru-agent | 3m | 0.01 | Haiku |
| Code analysis | code-analysis-agent | 5m | 0.05 | Haiku |
| Coverage check | unified-coverage-agent | 10m | 0.05 | Haiku |
| CI fix | ci-failure-resolution-agent | 8m | 0.10 | Sonnet |
| Test healing | autonomous-test-healer-agent | 15m | 0.15 | Sonnet |
| Doc quality | unified-doc-agent | 20m | 0.10 | Sonnet |
| Security scan | unified-security-scanner | 25m | 0.20 | Sonnet |

---

## 🔗 RELATED DOCUMENTS

- **Full Catalog:** AGENT_ECOSYSTEM_CATALOG.md (20K+ lines)
- **Decision Tree:** AGENT_SELECTION_DECISION_TREE.md
- **Performance Guide:** AGENT_PERFORMANCE_GUIDE.md
- **Patterns:** CUSTOM_AGENT_PATTERNS.md
- **Executive Summary:** PHASE_D_EXECUTION_SUMMARY.md

---

## METADATA

- **Generated:** 2026-06-20T06:54:05.369051
- **Quick Reference Format:** One-page reference card
- **Authority:** @mbaetiong
- **Next Update:** 2026-07-20

