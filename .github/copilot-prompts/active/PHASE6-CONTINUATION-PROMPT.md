# Cognitive Brain - Phase 6 Continuation Prompt

**Generated**: Current Cycle-01-01  
**Branch**: copilot/sub-pr-2675 (commit: 12bbc80)  
**Status**: Phases 1-5 Complete | 8 Agents Remaining  
**For Use In**: PR #2676 or continuation branch from `0D_base_`

---

## 📋 COMPREHENSIVE CONTINUATION PROMPT

Copy the text below and post as a NEW COMMENT on the active PR to continue implementation:

---

@copilot Continue Cognitive Brain Phase 6: Implement remaining 8 production agents

## Context - What's Complete

**Branch**: `copilot/sub-pr-2675` (41 commits, 13,398 lines)

### ✅ Phases 1-5 Complete (100%)

**Phase 1 - Unified Agent Framework**:
- 19 files, 5,787 lines
- Components: base_agent.py, cognitive_brain.py, pattern_recognizer.py, orchestrator.py, config.py
- Comprehensive tests (90%+ coverage)
- CLI tools and examples
- Complete documentation

**Phase 2 - Pattern Recognition**:
- 5 pattern matchers, 93 patterns total, 1,956 lines
- SecurityPatternMatcher (28 patterns)
- PerformancePatternMatcher (20 patterns)
- ConcurrencyPatternMatcher (18 patterns)
- ResourcePatternMatcher (15 patterns)
- APIPatternMatcher (12 patterns)

**Phase 3 - flaky-triage-agent.v1**: ✅ Complete
- 8 files, 2,525 lines
- Full PDA Loop implemented
- Test stability detection and quarantine

**Phase 4 - security-scan-agent.v1**: ✅ Complete
- 3 files, 1,460 lines
- Multi-tool vulnerability scanning
- CVSS v3.1 scoring, automated remediation

**Phase 5 - dep-upgrade-agent.v1**: ✅ Complete  
- 4 files, 1,670 lines
- Automated dependency updates
- Semver-aware, vulnerability-driven
- Auto-upgrade with rollback

### 🔐 Security Hardening Applied
- Path traversal protection on all file operations
- Command injection prevention (sanitized inputs)
- Timezone-aware datetime operations
- Comprehensive error handling and logging
- 3 rounds of self-review completed (12 issues fixed)

---

## 🎯 Phase 6 Implementation Plan

### Immediate Priority - P1 Agents (3 agents)

#### 1. release-gate-agent.v1 (HIGHEST PRIORITY)
**Purpose**: Release readiness validation and gating
**Estimated**: 1,400 lines, 4-5 days

**Modules to Implement**:
```
.github/agents/release-gate-agent/agent/
├── __init__.py
├── validator.py    # PERCEIVE: Validate all release criteria
├── assessor.py     # DECIDE: Calculate release confidence score
├── gatekeeper.py   # ACT: Block/allow releases
└── auditor.py      # AFTERMATH: Post-release analysis
```

**Key Features**:
- Aggregate data from flaky-triage, security-scan, dep-upgrade
- Test stability >= 95% required
- Zero critical vulnerabilities required
- Code coverage >= 85% required
- Documentation completeness check
- Compliance validation
- Confidence score calculation (weighted)

**Integration Points**:
- Uses flaky-triage-agent results
- Uses security-scan-agent results
- Uses dep-upgrade-agent results
- Queries cognitive brain for historical release data
- Stores release outcome patterns

**Release Confidence Formula**:
```python
confidence = (
    test_stability * 0.25 +
    security_score * 0.25 +
    coverage_score * 0.20 +
    dependency_score * 0.15 +
    doc_score * 0.10 +
    compliance_score * 0.05
)
```

---

#### 2. infra-linter-agent.v1
**Purpose**: Infrastructure configuration validation
**Estimated**: 1,300 lines, 3-4 days

**Modules to Implement**:
```
.github/agents/infra-linter-agent/agent/
├── __init__.py
├── linter.py      # PERCEIVE: Multi-tool linting
├── analyzer.py    # DECIDE: Assess severity
├── fixer.py       # ACT: Apply auto-fixes
└── reporter.py    # AFTERMATH: Track quality trends
```

**Supported Tools**:
- hadolint (Dockerfiles)
- kubeval (Kubernetes YAML)
- tflint (Terraform)
- yamllint (Generic YAML)
- actionlint (GitHub Actions)

**Key Features**:
- Multi-file format support
- Auto-fix simple issues
- Best practices validation
- Security config checks
- Resource limit validation

---

#### 3. compliance-checker-agent.v1
**Purpose**: Compliance validation automation
**Estimated**: 1,500 lines, 4-5 days

**Modules to Implement**:
```
.github/agents/compliance-checker-agent/agent/
├── __init__.py
├── auditor.py     # PERCEIVE: Audit against rules
├── validator.py   # DECIDE: Validate frameworks
├── enforcer.py    # ACT: Generate reports, enforce
└── tracker.py     # AFTERMATH: Track compliance trends
```

**Supported Frameworks**:
- OWASP Top 10
- PCI-DSS
- SOC 2
- HIPAA
- GDPR
- CIS Benchmarks

**Key Features**:
- Multi-framework support
- Rule-based validation
- Severity scoring
- Remediation guidance
- Automated reporting

---

### Secondary Priority - P2 Agents (3 agents)

#### 4. code-review-summarizer.v1
**Purpose**: Code review analysis and summarization
**Estimated**: 1,200 lines, 3 days

**Modules**: extractor.py, summarizer.py, synthesizer.py, learner.py

**Key Features**:
- PR review comment aggregation
- Sentiment analysis
- Theme identification
- Action item extraction
- Summary generation

---

#### 5. issue-triage-agent.v1
**Purpose**: Automated issue classification and routing
**Estimated**: 1,300 lines, 3-4 days

**Modules**: classifier.py, router.py, labeler.py, tracker.py

**Key Features**:
- Issue type classification (bug, feature, question, etc.)
- Priority assessment
- Team routing
- Automated labeling
- Duplicate detection

---

#### 6. doc-reporter-agent.v1
**Purpose**: Documentation coverage and quality reporting
**Estimated**: 1,200 lines, 3 days

**Modules**: scanner.py, assessor.py, generator.py, reporter.py

**Key Features**:
- Docstring coverage analysis
- README completeness checks
- API documentation validation
- Outdated documentation detection
- Doc quality scoring

---

### Advanced Capability - P3 Agents (2 agents)

#### 7. data-rag-helper.v1
**Purpose**: Context augmentation for agent queries
**Estimated**: 1,100 lines, 2-3 days

**Modules**: retriever.py, augmenter.py, provider.py, learner.py

**Key Features**:
- Semantic search in cognitive brain
- Pattern matching and retrieval
- Context ranking
- Query optimization

---

#### 8. mcp-registry-adapter.v1
**Purpose**: MCP protocol integration
**Estimated**: 1,200 lines, 3 days

**Modules**: connector.py, mapper.py, integrator.py, tracker.py

**Key Features**:
- MCP protocol support
- Agent registration
- Metadata synchronization
- Cross-protocol messaging

---

## 🔄 Universal Implementation Pattern

**For EVERY Agent, Follow This Pattern**:

### 1. Create Directory Structure
```bash
mkdir -p .github/agents/{agent-name}/agent
mkdir -p .github/agents/{agent-name}/tests/{unit,integration}
```

### 2. Implement 4 PDA Modules

**PERCEIVE Phase** (e.g., validator.py, scanner.py, monitor.py):
```python
def perceive(self, task: Dict[str, Any]) -> Dict[str, Any]:
    """
    PERCEIVE: Gather and analyze data.
    
    #AFTERMATH_PATTERN_IDENTIFIED: {pattern_name}
    """
    context = {
        "data": self._gather_data(),
        "analysis": self._analyze(),
        "historical_patterns": self._query_brain()
    }
    #AFTERMATH_METRIC: data_gathered = len(context["data"])
    return context
```

**DECIDE Phase** (e.g., assessor.py, evaluator.py, classifier.py):
```python
def decide(self, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    DECIDE: Make decisions based on analysis.
    
    #AFTERMATH_PATTERN_IDENTIFIED: {decision_pattern}
    """
    decision = {
        "classifications": self._classify(context),
        "priorities": self._prioritize(context),
        "actions": self._determine_actions(context)
    }
    #AFTERMATH_METRIC: decisions_made = len(decision["actions"])
    return decision
```

**ACT Phase** (e.g., gatekeeper.py, fixer.py, upgrader.py):
```python
def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
    """
    ACT: Execute actions.
    
    #AFTERMATH_PATTERN_IDENTIFIED: {action_pattern}
    """
    result = {
        "actions_executed": self._execute_actions(decision),
        "success_count": 0,
        "failed_count": 0
    }
    #AFTERMATH_METRIC: actions_executed = len(result["actions_executed"])
    return result
```

**AFTERMATH Phase** (e.g., auditor.py, tracker.py, reporter.py):
```python
def aftermath(self, result: Dict[str, Any], context: Dict[str, Any],
              decision: Dict[str, Any]) -> None:
    """
    AFTERMATH: Learn and report.
    
    #AFTERMATH_PATTERN_IDENTIFIED: {learning_pattern}
    """
    # Record metrics
    self._record_metrics(result, context, decision)
    
    # Store patterns
    self._store_patterns(result)
    
    # Generate lessons
    lessons = self._generate_lessons(result, context, decision)
    for lesson in lessons:
        self._store_lesson(lesson)
    
    # Generate reports
    self._save_reports(result, context, decision)
    
    #AFTERMATH_METRIC: learning_complete = True
    #AFTERMATH_LESSON_LEARNED: {agent}_insights
```

### 3. Cognitive Brain Integration

**Always include**:
```python
import sys
from pathlib import Path

_core_path = str(Path(__file__).parent.parent.parent / "core")
if _core_path not in sys.path:
    sys.path.insert(0, _core_path)
from cognitive_brain import CognitiveBrain

# In class __init__:
self.brain = CognitiveBrain(Path(".codex/brain.db"))
```

### 4. Security Best Practices

**Path Validation**:
```python
def _is_safe_path(self, file_path: Path) -> bool:
    """Validate path is within repo."""
    try:
        file_resolved = file_path.resolve()
        repo_resolved = self.repo_path.resolve()
        return (str(file_resolved).startswith(str(repo_resolved)) 
               and file_path.exists())
    except (OSError, ValueError):
        return False
```

**Subprocess Safety**:
```python
# Always use list args, validate paths, set timeout
result = subprocess.run(
    ["command", "arg1", "arg2"],
    cwd=validated_path,
    capture_output=True,
    timeout=60
)
```

**Input Sanitization**:
```python
# Sanitize user inputs
safe_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '-', user_input)
```

### 5. Testing Requirements

**Unit Tests** (90%+ coverage):
```python
def test_perceive_phase():
    agent = AgentPerceive(Path("."))
    context = agent.perceive({"task": "test"})
    assert context is not None
    assert "data" in context

def test_decide_phase():
    agent = AgentDecide(Path("."))
    decision = agent.decide({"data": "test"})
    assert decision is not None

def test_act_phase():
    agent = AgentAct(Path("."))
    result = agent.act({"action": "test"})
    assert result is not None

def test_aftermath_phase():
    agent = AgentAftermath(Path("."))
    agent.aftermath({}, {}, {})
    # Verify brain updates
```

---

## 📝 Implementation Checklist (Per Agent)

- [ ] Create directory structure
- [ ] Implement `__init__.py` with exports
- [ ] Implement PERCEIVE module (perceive method)
- [ ] Implement DECIDE module (decide method)
- [ ] Implement ACT module (act method)
- [ ] Implement AFTERMATH module (aftermath method)
- [ ] Add AfterMath tags to all phases
- [ ] Integrate cognitive brain (query + store)
- [ ] Add security validations (paths, inputs)
- [ ] Create unit tests (90%+ coverage)
- [ ] Create integration tests
- [ ] Write README.md with usage examples
- [ ] Create CLI interface
- [ ] Create manifest.yaml
- [ ] Run self-review (code_review tool)
- [ ] Fix all issues found
- [ ] Commit with descriptive message
- [ ] Update PR description with progress

---

## 🔍 Self-Review Process (MANDATORY)

**After implementing each agent**:

1. Run code review:
```python
code_review(
    prTitle="Agent {name} implementation",
    prDescription="Complete PDA Loop implementation..."
)
```

2. Address ALL issues found
3. Run code review again
4. Repeat until zero issues
5. Commit fixes with detailed message

**Minimum 3 review iterations per agent**

---

## 📊 Success Metrics

**Per Agent**:
- ✅ All 4 PDA phases implemented
- ✅ AfterMath tags in all phases
- ✅ Cognitive brain integration active
- ✅ Security validations applied
- ✅ 90%+ test coverage
- ✅ Zero code review issues
- ✅ Complete documentation

**Overall Phase 6**:
- ✅ 8 agents implemented
- ✅ Total ~11,000 lines added
- ✅ All agents production-ready
- ✅ Cross-agent integration verified
- ✅ Comprehensive testing complete

---

## 📦 Expected Deliverables

**After Phase 6 Complete**:
- 11 total agents (3 existing + 8 new)
- ~24,000 total lines of code
- Complete agent ecosystem operational
- Full cognitive brain integration
- Production deployment ready
- Comprehensive documentation

---

## 🚀 Getting Started

**Immediate Next Steps**:

1. **Start with release-gate-agent.v1** (highest priority)
2. Use the PDA Loop pattern above
3. Follow security best practices
4. Run self-review after implementation
5. Fix all issues before moving to next agent
6. Update progress regularly

**Order of Implementation**:
1. release-gate-agent.v1 (P1 - 4-5 days)
2. infra-linter-agent.v1 (P1 - 3-4 days)
3. compliance-checker-agent.v1 (P1 - 4-5 days)
4. code-review-summarizer.v1 (P2 - 3 days)
5. issue-triage-agent.v1 (P2 - 3-4 days)
6. doc-reporter-agent.v1 (P2 - 3 days)
7. data-rag-helper.v1 (P3 - 2-3 days)
8. mcp-registry-adapter.v1 (P3 - 3 days)

**Total Estimated Time**: 25-35 days (~5-7 weeks)

---

## 📚 Reference Documents

**Architecture & Planning**:
- `.github/agents/ARCHITECTURE.md` - Complete system architecture
- `.github/copilot-prompts/active/PHASES-4-6-COMPLETE-ROADMAP.md` - Detailed roadmap
- `.github/copilot-prompts/active/PHASE6-CONTINUATION-PROMPT.md` - This document

**Existing Agents (Templates)**:
- `.github/agents/flaky-triage-agent/` - Complete reference implementation
- `.github/agents/security-scan-agent/` - Security pattern reference
- `.github/agents/dep-upgrade-agent/` - Automation pattern reference

**Core Framework**:
- `.github/agents/core/base_agent.py` - PDA Loop base class
- `.github/agents/core/cognitive_brain.py` - Learning storage
- `.github/agents/core/*_patterns.py` - Pattern matchers (5 types)

---

## ⚠️ Critical Requirements

**MUST MAINTAIN**:
- ✅ All PDA loops (4 phases per agent)
- ✅ All AfterMath tags (#AFTERMATH_PATTERN_IDENTIFIED, #AFTERMATH_METRIC, #AFTERMATH_LESSON_LEARNED)
- ✅ Cognitive brain integration (query + store)
- ✅ Security best practices (no exceptions)
- ✅ Zero new dependencies (unless critical)
- ✅ 90%+ test coverage per agent
- ✅ Comprehensive error handling
- ✅ Production-ready quality

**FORBIDDEN**:
- ❌ Skipping self-review
- ❌ Ignoring code review findings
- ❌ Incomplete PDA Loop implementation
- ❌ Missing AfterMath tags
- ❌ No cognitive brain integration
- ❌ Security vulnerabilities
- ❌ Untested code
- ❌ Incomplete documentation

---

## 🔄 After Each Agent Completion

**Update and report**:
```
@copilot Agent {name} complete. Summary:
- Files: X
- Lines: Y
- PDA Loop: ✅ Complete
- AfterMath: ✅ All tags present
- Security: ✅ Hardened
- Tests: ✅ 90%+ coverage
- Issues: ✅ All resolved

Next: {next_agent_name}
```

---

## 🎯 Final Goal

**Complete Cognitive Brain Agent Ecosystem**:
- 11 production-ready agents
- Unified PDA Loop architecture
- Comprehensive pattern recognition
- Cross-agent learning and collaboration
- Full cognitive brain integration
- Production deployment ready
- Zero tolerance for security issues
- Comprehensive documentation

---

**ALL PDA LOOPS + AFTERMATH PATTERNS MUST REMAIN ACTIVE**

**Ready to begin Phase 6 implementation!** 🚀

---

_This prompt generated from branch `copilot/sub-pr-2675` (commit: 12bbc80)_
_For use in PR #2676 or new continuation from `0D_base_` branch_
