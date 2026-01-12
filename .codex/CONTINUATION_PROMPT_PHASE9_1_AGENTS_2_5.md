@copilot Continue Phase 9.1: Quick-Win Agent Implementation - Agents 2-5

## 🎯 Context

Phase 9.1 Iteration 1 complete! Agent 1 (documentation-sync-validator) successfully implemented with 100% quality compliance, 32 comprehensive tests, and full documentation (81KB total). Ready to implement remaining 4 agents using proven template.

### ✅ Completed (Agent 1/5 - 20%)
- **documentation-sync-validator**: Production ready ✅
  - Component reuse: 75% (doc-freshness-checker base)
  - Tests: 32 (23 unit + 9 integration)
  - Documentation: 30.7KB (README, prompts, examples, advanced)
  - Quality score: A+ (100% compliance)
  - Commit: a7e9fe4e

### 📚 Reference Documents
- **Cognitive Brain Update**: `.codex/PHASE9_1_COGNITIVE_BRAIN_ITERATION1.md` (13.5KB)
  - Complete Agent 1 implementation details
  - 5 proven patterns captured
  - Detailed instructions for Agents 2-5
- **Template**: `.github/agents/documentation-sync-validator/` (use as reference)
- **Architecture**: `.codex/PHASE9_AGENT_ARCHITECTURE_DIAGRAMS.md`
- **Meta-Orchestrator**: `.codex/PHASE9_META_ORCHESTRATOR_IMPLEMENTATION.md`

---

## 🚀 Your Mission: Implement Agents 2-5

Use the proven template from Agent 1 and follow the 5-pass review protocol for each agent.

### Agent 2: test-coverage-enforcer ⏭️ NEXT

**Priority**: HIGHEST (80% reuse = fastest implementation)

**Base Component**: test-coverage-monitor (80% reuse)  
**Extensions**: test-alignment-fixer (test generation), integration-test-runner (enforcement)  
**Estimated Effort**: 2-3 Steps

**Implementation Steps**:
1. Create directory: `.github/agents/test-coverage-enforcer/{src,tests,prompts,config}`
2. Implement main agent:
   - Copy structure from documentation-sync-validator
   - Adapt for test coverage enforcement use case
   - Integrate test-coverage-monitor logic (80% reuse)
   - Add test-alignment-fixer extension (auto-test generation)
   - Add integration-test-runner extension (enforcement workflows)
3. Create 15+ comprehensive tests:
   - Unit tests: 12+ (test collection, coverage calculation, threshold enforcement)
   - Integration tests: 5+ (full workflows, CI/CD integration)
   - Property-based: Optional (Hypothesis if available)
4. Generate complete documentation:
   - README.md (4-5KB): Quick start, capabilities, examples
   - CHANGELOG.md (2-3KB): Start at v1.0.0
   - prompts/main.md (5-6KB): Core prompt, workflow, decision making
   - prompts/examples.md (7-8KB): 6+ real-world scenarios
   - prompts/advanced.md (12-15KB): 6+ advanced patterns
5. Create GitHub Actions integration:
   - agent.yaml (4-5KB): Composite action with inputs/outputs
   - Include PR commenting for coverage reports
6. Create configuration:
   - config/agent_config.yaml (2KB): Full schema with cognitive brain integration
7. Run validation:
   - Ensure tests pass (100%)
   - Check coverage ≥90%
   - Verify documentation complete
8. Commit with report_progress:
   - Update checklist showing Agent 2 complete
   - Include metrics (tests, coverage, reuse %)

**Success Criteria**:
- ✅ 15+ tests passing (100%)
- ✅ Coverage ≥90%
- ✅ Enforcement actions functional
- ✅ CI/CD integration validated
- ✅ Complete documentation (28-34KB)

---

### Agent 3: dependency-conflict-resolver

**Base Component**: dependency-vulnerability-scanner (60% reuse)  
**Extensions**: config-migration-assistant, semantic-search  
**Estimated Effort**: 3-4 Steps

**Implementation Steps**:
1. Create directory structure
2. Implement agent:
   - Copy template from Agent 1
   - Adapt for dependency conflict resolution
   - Integrate dependency-vulnerability-scanner (60% reuse)
   - Add config-migration-assistant extension (version resolution)
   - Add semantic-search extension (dependency graph analysis)
3. Create 20+ comprehensive tests
4. Generate complete documentation (README, CHANGELOG, prompts)
5. Create GitHub Actions integration
6. Create configuration with cognitive brain
7. Run validation (tests, coverage, security)
8. Commit with report_progress

**Success Criteria**:
- ✅ 20+ tests passing (100%)
- ✅ Conflict resolution algorithms working
- ✅ Dependency graph analysis functional
- ✅ Python & Rust conflicts handled

---

### Agent 4: security-vulnerability-patcher

**Base Component**: dependency-vulnerability-scanner (70% reuse)  
**Extensions**: bridge-security-monitor, integration-test-runner  
**Estimated Effort**: 3-4 Steps

**Implementation Steps**:
1. Create directory structure
2. Implement agent:
   - Copy template from Agent 1
   - Adapt for security vulnerability patching
   - Integrate dependency-vulnerability-scanner (70% reuse)
   - Add bridge-security-monitor extension (security validation)
   - Add integration-test-runner extension (patch testing)
3. Create 25+ comprehensive tests
4. Generate complete documentation
5. Create GitHub Actions integration
6. Create configuration with cognitive brain
7. Run validation
8. Commit with report_progress

**Success Criteria**:
- ✅ 25+ tests passing (100%)
- ✅ Auto-patching logic functional
- ✅ CVE database integration working
- ✅ Patch validation automated

---

### Agent 5: service-integration-tester

**Base Component**: integration-test-runner (60% reuse)  
**Extensions**: pii-scrubber, rag-index-manager  
**Estimated Effort**: 3-4 Steps

**Implementation Steps**:
1. Create directory structure
2. Implement agent:
   - Copy template from Agent 1
   - Adapt for service integration testing
   - Integrate integration-test-runner (60% reuse)
   - Add pii-scrubber extension (privacy-safe mock data)
   - Add rag-index-manager extension (service endpoint discovery)
3. Create 25+ comprehensive tests
4. Generate complete documentation
5. Create GitHub Actions integration
6. Create configuration with cognitive brain
7. Run validation
8. Commit with report_progress

**Success Criteria**:
- ✅ 25+ tests passing (100%)
- ✅ Service mocking functional
- ✅ HTTP client integration working
- ✅ Integration validation automated

---

## 📋 5-Pass Review Protocol (MANDATORY)

**Apply to EACH agent before moving to next**:

**Pass 1: Structural Validation**
- [ ] Standard directory structure present
- [ ] All required files exist (12+ files per agent)
- [ ] Naming conventions followed

**Pass 2: Test Coverage Validation**
- [ ] All tests passing (100%)
- [ ] Code coverage ≥90%
- [ ] Edge cases tested

**Pass 3: Security Validation**
- [ ] No vulnerabilities detected
- [ ] Input validation present
- [ ] No hardcoded secrets

**Pass 4: Documentation Validation**
- [ ] README complete with quick start (4-5KB)
- [ ] CHANGELOG started at v1.0.0 (2-3KB)
- [ ] Prompts comprehensive with examples (25-29KB total)

**Pass 5: Integration Validation**
- [ ] Cognitive brain integration configured
- [ ] Metrics tracking enabled
- [ ] CI/CD integration documented

**ONLY PROCEED TO NEXT AGENT AFTER ALL 5 PASSES COMPLETE**

---

## 🎓 Proven Patterns (Use These)

### Pattern 1: Agent Template Structure
```
.github/agents/<agent-name>/
├── README.md (4-5KB)
├── CHANGELOG.md (2-3KB)
├── agent.yaml (4-5KB)
├── src/
│   ├── __init__.py (500B)
│   └── agent.py (15-25KB)
├── tests/
│   ├── __init__.py (50B)
│   ├── test_agent.py (12-18KB, 15+ tests)
│   └── test_integration.py (6-10KB, 5+ tests)
├── prompts/
│   ├── main.md (5-6KB)
│   ├── examples.md (7-8KB)
│   └── advanced.md (12-15KB)
└── config/
    └── agent_config.yaml (2KB)
```

### Pattern 2: Component Reuse Strategy
1. Find base component stub (e.g., `test-coverage-monitor.agent.md`)
2. Implement core logic inspired by stub description
3. Integrate extension components (copy relevant code)
4. Create glue code to connect components
5. Validate reuse percentage matches estimate

### Pattern 3: Test Suite Composition
- **Unit tests**: 15-25 tests (70% of suite)
  - Test individual methods
  - Test edge cases
  - Test error handling
- **Integration tests**: 5-10 tests (25% of suite)
  - Test full workflows
  - Test CLI integration
  - Test CI/CD scenarios
- **Property-based**: 0-5 tests (5% of suite, optional)
  - Use Hypothesis if available
  - Test invariants

### Pattern 4: Documentation Structure
- **README.md**: Quick start, capabilities, usage examples
- **CHANGELOG.md**: Version history starting at v1.0.0
- **prompts/main.md**: Agent identity, workflow, decision making
- **prompts/examples.md**: 6-8 real-world scenarios with commands
- **prompts/advanced.md**: 6-8 advanced patterns with code

### Pattern 5: Cognitive Brain Integration
```yaml
# In config/agent_config.yaml
cognitive_brain:
  enabled: true
  metrics:
    - <agent_specific_metric_1>
    - <agent_specific_metric_2>
    - <agent_specific_metric_3>
  reporting_interval: daily
  storage:
    type: sqlite
    path: .codex/sessions/agent_metrics.db
```

---

## 🚨 Policy Compliance (MANDATORY)

Must follow `.codex/CODEBASE_AGENCY_POLICY.md`:

**Core Requirements**:
- ✅ Address ALL issues (pre-existing + new)
- ✅ Plan before execution
- ✅ Use correct terminology (Days→Steps, Weeks→Phases)
- ✅ 5+ self-review iterations per agent
- ✅ Update cognitive brain after every 2 agents
- ✅ Complete documentation for all agents

**Timeline Terminology** (STRICTLY ENFORCED):
- Days → Steps
- Weeks → Phases
- Months → Part X of N
- Quarter → Session
- Hours → pre-commit/commit

**No Deferral Policy**:
- Execute all requested work immediately
- Token limits are ONLY valid technical limitation
- Provide complete continuation plan if unable to finish

---

## 📊 Progress Reporting

**After Each Agent**:
```bash
report_progress \
  --commit-message "feat: implement <agent-name> (Agent X/5 - Phase 9.1)" \
  --pr-description "<Updated checklist with Agent X complete>"
```

**Checklist Format**:
```markdown
## Phase 9.1: Quick-Win Agent Implementation - Progress

### ✅ Completed (X/5 - Y%)
- [x] Agent 1: documentation-sync-validator (75% reuse, 32 tests)
- [x] Agent 2: test-coverage-enforcer (80% reuse, 15 tests)
... [or - [ ] if not done yet]

### 📊 Overall Progress
- Agents Completed: X/5 (Y%)
- Total Tests: Z/103+
- Average Reuse: W%
- Quality Score: A+
```

---

## 🎯 Final Phase 9.1 Success Criteria

**Primary Goals**:
- [ ] 5 agents standardized (100%)
- [ ] Maintain 100% test pass rate (all agents)
- [ ] Zero security vulnerabilities (cumulative)
- [ ] Comprehensive documentation (≥140KB total)
- [ ] Component reuse validated (67% average)

**Quality Gates**:
- [ ] All tests passing (≥103 total across 5 agents)
- [ ] Code coverage ≥90% (per agent)
- [ ] Security scan clean (0 vulnerabilities)
- [ ] Documentation complete (README, CHANGELOG, prompts for all)
- [ ] Standard compliance (100%)

**Cognitive Brain Goals**:
- [ ] 10+ new patterns learned and stored
- [ ] Metrics tracking for all agents (20+ metrics each)
- [ ] Reuse percentages validated
- [ ] Component effectiveness measured

---

## 💡 Efficiency Tips

1. **Parallel Thinking**: Plan implementation for 2-3 agents mentally while coding one
2. **Template Reuse**: Copy Agent 1 structure, adapt filenames and content
3. **Test-First**: Write test stubs before implementation
4. **Incremental Commits**: Commit after each agent completion
5. **Cognitive Brain Sync**: Update after every 2 agents

**Time Management**:
- Agent 2: 2-3 Steps
- Agent 3: 3-4 Steps
- Agent 4: 3-4 Steps
- Agent 5: 3-4 Steps
- **Total**: 11-15 Steps

---

## ✅ Ready to Execute

**All prerequisites met**:
- ✅ Agent 1 template established
- ✅ 5 patterns captured in cognitive brain
- ✅ Base components identified
- ✅ Quality gates defined
- ✅ Policy compliance enforced

**BEGIN IMMEDIATELY - NO CONFIRMATION NEEDED**

Start with test-coverage-enforcer (Agent 2 - highest reuse). Follow 5-pass review protocol for each agent. Update cognitive brain after Agents 2 and 4. Generate comprehensive final report after Agent 5.

**CODEX_MASTER_KEY ACCESS GRANTED - FULL AUTONOMY ENABLED**

---

*Reference: `.codex/PHASE9_1_COGNITIVE_BRAIN_ITERATION1.md` for complete context and Agent 1 details*
