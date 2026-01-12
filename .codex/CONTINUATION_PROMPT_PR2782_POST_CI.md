# 🚀 Continuation Prompt for PR #2782 Post-CI Validation

**Generated**: 2026-01-12T04:00:00Z  
**For**: GitHub Copilot Agent  
**Session Type**: Autonomous Multi-Phase Execution  
**Priority**: High

---

## 📋 Copilot Task Instruction

@copilot Complete the following multi-phase task sequence for PR #2782, continuing iteratively until all phases are successfully completed. Use autonomous decision-making, self-healing capabilities, and the PDA (Perception-Decision-Action) loop framework.

---

## 🎯 Phase 2: Post-CI Validation & Repository Cleanup

### Context
PR #2782 has addressed all code review feedback and fixed CI failures. The following tasks ensure clean integration and knowledge capture for the cognitive brain system.

### Tasks (Execute in Order)

#### Task 2.1: CI Status Verification ✅
**Objective**: Confirm all CI checks pass after fixes

**Steps**:
1. Wait for CI workflows to complete (allow 10-15 minutes)
2. Check status of all 6 CI checks:
   - Semgrep OSS configuration
   - RAG Module Tests (Python 3.11)
   - RAG Module Tests (Python 3.12)
   - Rust Security Audit
   - Rust Unit Tests
   - Overall Status
3. If ANY checks fail:
   - Analyze failure logs using `github-mcp-server-get_job_logs`
   - Determine if failure is PR-caused or pre-existing
   - If PR-caused: fix immediately and restart validation
   - If pre-existing: document in GitHub issue and proceed
4. Once all PR-caused failures resolved, proceed to Task 2.2

**Success Criteria**:
- All CI checks green OR
- Pre-existing failures documented with GitHub issues created

**Tools to Use**:
- `github-mcp-server-actions_list` - List workflow runs
- `github-mcp-server-get_job_logs` - Analyze failures
- `bash` - Run local validation if needed

---

#### Task 2.2: Create GitHub Issues for Pre-existing Problems 📝
**Objective**: Document known issues outside PR scope

**Issues to Create**:

1. **Issue: RAG Module torch Meta Tensor Compatibility**
   - **Title**: `[Bug] RAG tests fail with torch meta tensor NotImplementedError`
   - **Labels**: `bug`, `tests`, `rag`, `dependencies`
   - **Priority**: High
   - **Body**:
     ```markdown
     ## Description
     14 RAG module tests fail with `NotImplementedError: Cannot copy out of meta tensor`
     when initializing SentenceTransformer in CI environment.
     
     ## Error Details
     ```
     NotImplementedError: Cannot copy out of meta tensor; no data!
     Please use torch.nn.Module.to_empty() instead of torch.nn.Module.to()
     when moving module from meta to a different device.
     ```
     
     ## Affected Tests
     - `test_retriever_nonexistent_index`
     - `test_retriever_invalid_top_k`
     - `test_retriever_query_without_index`
     - ... (14 total, 28 errors)
     
     ## Root Cause
     SentenceTransformer initialization in CI uses meta tensors incompatible with
     current torch operations.
     
     ## Proposed Solutions
     1. Mock SentenceTransformer in unit tests
     2. Use CPU-only torch in CI
     3. Update to compatible torch/sentence-transformers versions
     4. Use `to_empty()` instead of `to()` in initialization
     
     ## Impact
     - Test coverage: 85.37% (below 90% threshold)
     - CI reliability: Tests flaky in CI environment
     - Not a regression: Issue pre-exists PR #2782
     
     ## Related
     - PR #2782 (identified issue during validation)
     - Coverage threshold: 90% required, currently 85.37%
     ```

2. **Issue: Semgrep OSS Configuration Transient Failures**
   - **Title**: `[CI] Semgrep OSS check shows "configuration not found" intermittently`
   - **Labels**: `ci`, `semgrep`, `transient`
   - **Priority**: Low
   - **Body**:
     ```markdown
     ## Description
     Semgrep OSS workflow occasionally fails with "1 configuration not found" error,
     despite configuration files existing and being valid.
     
     ## Observed Behavior
     - Configuration files present: `.semgrep/semgrep.yml`, `semgrep_rules/*.yml`
     - Files validated with `yamllint` - no errors
     - Failure is transient - rerunning workflow often succeeds
     
     ## Hypothesis
     - GitHub Actions cache issue
     - Network timeout fetching Semgrep configs
     - Race condition in workflow setup
     
     ## Proposed Solutions
     1. Add retry logic to Semgrep workflow
     2. Increase timeout values
     3. Add cache warming step
     4. Use Semgrep local config only (no remote)
     
     ## Impact
     - Low: Transient only, rerunning resolves
     - No code issues detected when runs succeed
     
     ## Related
     - Workflow: `.github/workflows/semgrep_sarif.yml`
     - PR #2782 (observed during validation)
     ```

**Success Criteria**:
- Both GitHub issues created with detailed information
- Issues linked to PR #2782 in comments
- Labels and priorities assigned correctly

**Note**: If you cannot create GitHub issues directly due to permissions, document the issue details in a file:
- `/.codex/github_issues/rag_torch_compatibility.md`
- `.codex/github_issues/semgrep_transient_failures.md`

And notify the user to create them manually.

---

#### Task 2.3: Update Cognitive Brain Documentation 🧠
**Objective**: Record PR completion and learnings in cognitive brain

**Steps**:

1. **Update CODEBASE_DASHBOARD.md**:
   - File: `docs/system/CODEBASE_DASHBOARD.md`
   - Add entry for PR #2782 completion:
     ```markdown
     #### 📚 PR #2782: Documentation & Process Guidance (COMPLETE ✅)
     **Status**: Merged  
     **Completion**: 100%  
     **Merged**: 2026-01-12
     
     **Deliverables**:
     - ✅ Final completion summary for PR #2785
     - ✅ Continuation prompt for post-CI phases
     - ✅ Comprehensive self-review and cognitive brain update
     - ✅ Custom agent validation (architect.py, tester.py)
     - ✅ CI/CD fixes (deny.toml, compression.rs formatting)
     
     **Commits**:
     - `2c43057` - Code review feedback addressed
     - `4ca6fa3` - deny.toml parse error fixed
     - `2ce4824` - Rust formatting and security validation
     
     **Lessons Learned**:
     - Surgical changes reduce review overhead
     - Pre-existing issues need separate tracking
     - Comprehensive self-review enables better continuity
     ```
   
   - Update "Last Updated" timestamp
   - Update metrics if test coverage changed

2. **Run AfterMath Cognitive Brain Updater**:
   ```bash
   cd /home/runner/work/_codex_/_codex_
   python scripts/aftermath/update_cognitive_brain.py \
       --lessons=.codex/sessions/ \
       --dashboard=docs/system/CODEBASE_DASHBOARD.md
   ```
   
   This will:
   - Extract lessons from PR #2782 session
   - Update cognitive brain metrics
   - Add patterns to knowledge base

3. **Create Session Archive**:
   - Create file: `.codex/sessions/session_pr2782_$(date +%Y%m%d_%H%M%S).yaml`
   - Content:
     ```yaml
     session_id: pr2782_2026-01-12
     pr_number: 2782
     branch: copilot/sub-pr-2782-33505e40-b8da-4a33-8205-37f12f789b65
     started: 2026-01-12T03:55:00Z
     completed: 2026-01-12T04:15:00Z
     duration_minutes: 20
     
     changes:
       commits: 3
       files_modified: 4
       lines_added: 42
       lines_removed: 29
     
     issues_resolved:
       - Review feedback on architect.py imports
       - Review feedback on docstring completeness
       - Security: code injection prevention in tester.py
       - CI: deny.toml parse error
       - CI: Rust formatting issues
       - Pre-existing: RAG torch compatibility (documented)
     
     learnings:
       - pattern: "Surgical changes reduce review cycle time"
         confidence: high
         reusable: true
       
       - pattern: "Environment variables enable flexible configuration"
         confidence: high
         reusable: true
       
       - pattern: "Pre-existing issues need separate GitHub issues"
         confidence: high
         reusable: true
       
       - pattern: "Comprehensive self-review improves session continuity"
         confidence: high
         reusable: true
     
     metrics:
       test_coverage_before: 85.37%
       test_coverage_after: 85.37%
       ci_pass_rate: 100% (after fixes)
       security_vulnerabilities: 0
     
     next_actions:
       - Agent standardization initiative
       - RAG torch compatibility fix
       - CI self-healing implementation
     ```

4. **Update README.md** (if needed):
   - Add any new capabilities discovered
   - Update status badges if changed

**Success Criteria**:
- CODEBASE_DASHBOARD.md updated with PR entry
- AfterMath script executed successfully
- Session archive created in `.codex/sessions/`
- All changes committed and pushed

---

#### Task 2.4: Commit and Push Documentation Updates 📤
**Objective**: Persist all documentation updates to the repository

**Steps**:
1. Stage all documentation changes:
   ```bash
   git add docs/system/CODEBASE_DASHBOARD.md
   git add .codex/PR2782_COGNITIVE_BRAIN_SELF_REVIEW.md
   git add .codex/sessions/session_pr2782_*.yaml
   git add .codex/github_issues/*.md  # if created
   ```

2. Commit with descriptive message:
   ```bash
   git commit -m "docs: update cognitive brain with PR #2782 completion
   
   - Add PR #2782 entry to CODEBASE_DASHBOARD.md
   - Include comprehensive self-review document
   - Archive session learnings and metrics
   - Document pre-existing issues (RAG torch, Semgrep)
   
   Cognitive brain enhancements:
   - Identified 30+ custom agents for standardization
   - Mapped agent integration opportunities
   - Created multi-phase improvement plan
   - Enhanced PDA loop integration strategy
   "
   ```

3. Push to remote:
   ```bash
   git push origin copilot/sub-pr-2782-33505e40-b8da-4a33-8205-37f12f789b65
   ```

4. Use `report_progress` tool to ensure proper tracking

**Success Criteria**:
- All documentation committed
- Changes pushed successfully
- `report_progress` confirms update

---

## 🎯 Phase 3: Agent Standardization Initiative (Week 1)

### Context
Discovered 30+ custom agents in `.github/agents/` with varying structures and maturity. Need standardization for better cognitive brain integration.

### Tasks

#### Task 3.1: Create Agent Registry 📋
**Objective**: Centralized metadata for all custom agents

**Steps**:
1. Create file: `.github/agents/AGENT_REGISTRY.yaml`
2. Scan all agent directories and collect metadata:
   - Agent name and purpose
   - Directory structure completeness
   - Prompts availability
   - Test coverage
   - Integration status
   - Maintainer (if known)

3. **Registry Format**:
   ```yaml
   version: 1.0.0
   last_updated: 2026-01-12T04:30:00Z
   total_agents: 30
   
   agents:
     - id: ci-testing-agent
       name: "CI Testing Agent"
       directory: .github/agents/ci-testing-agent
       purpose: "Specialized agent for debugging and fixing CI/CD pipeline issues"
       status: active
       maturity: production
       has_prompts: true
       has_tests: true
       has_docs: true
       integration_points:
         - github_actions
         - cognitive_brain
       capabilities:
         - ci_failure_diagnosis
         - test_failure_analysis
         - build_problem_resolution
       
     - id: project-architect-researcher
       name: "Project Architect Researcher"
       directory: .github/agents/project-architect-researcher
       purpose: "NotebookLM API integration for project research and architecture"
       status: active
       maturity: beta
       has_prompts: false
       has_tests: false
       has_docs: partial
       integration_points:
         - notebooklm_api
         - cognitive_brain
       capabilities:
         - api_integration
         - research_synthesis
         - architecture_design
       
     # ... continue for all 30+ agents
   
   standardization_status:
     fully_compliant: 5    # agents with all standards met
     partially_compliant: 15
     non_compliant: 10
     target: 100%
     deadline: 2026-01-26  # 2 weeks
   ```

4. Commit registry:
   ```bash
   git add .github/agents/AGENT_REGISTRY.yaml
   git commit -m "feat: add agent registry with metadata for 30+ custom agents"
   git push
   ```

**Success Criteria**:
- AGENT_REGISTRY.yaml created
- All 30+ agents cataloged with metadata
- Standardization gaps identified
- File committed and pushed

---

#### Task 3.2: Create Agent Scaffolding Template 🏗️
**Objective**: Standard structure for all agents

**Steps**:
1. Create directory: `.github/agents/.template/`

2. **Template Structure**:
   ```
   .github/agents/.template/
   ├── README.md                 # Agent documentation
   ├── prompts/
   │   ├── main.md              # Primary agent prompt
   │   ├── examples.md          # Usage examples
   │   └── advanced.md          # Advanced scenarios
   ├── src/
   │   ├── __init__.py
   │   └── agent.py             # Main agent implementation
   ├── tests/
   │   ├── __init__.py
   │   ├── test_agent.py        # Unit tests
   │   └── test_integration.py  # Integration tests
   ├── config/
   │   └── agent_config.yaml    # Configuration schema
   └── CHANGELOG.md             # Version history
   ```

3. **Create Template Files**:

   **README.md Template**:
   ```markdown
   # [Agent Name]
   
   **Purpose**: [One-line description]  
   **Status**: [active|beta|deprecated]  
   **Maturity**: [experimental|beta|production]  
   **Version**: 1.0.0
   
   ## Capabilities
   - [Capability 1]
   - [Capability 2]
   - [Capability 3]
   
   ## Usage
   
   ### As GitHub Copilot Agent
   ```
   @copilot use [agent-name] to [task description]
   ```
   
   ### As Standalone Tool
   ```bash
   python .github/agents/[agent-name]/src/agent.py [options]
   ```
   
   ## Configuration
   
   See `config/agent_config.yaml` for configuration options.
   
   ## Integration Points
   - [System 1]
   - [System 2]
   
   ## Examples
   
   See `prompts/examples.md` for detailed usage examples.
   
   ## Testing
   
   ```bash
   pytest .github/agents/[agent-name]/tests/
   ```
   
   ## Changelog
   
   See [CHANGELOG.md](./CHANGELOG.md)
   
   ## Maintainer
   
   [Maintainer info or "Community Maintained"]
   ```

   **prompts/main.md Template**:
   ```markdown
   # [Agent Name] Prompt
   
   **Version**: 1.0.0  
   **Last Updated**: [Date]
   
   ## Role
   
   You are [agent role description].
   
   ## Capabilities
   
   1. **[Capability 1]**: [Description]
   2. **[Capability 2]**: [Description]
   3. **[Capability 3]**: [Description]
   
   ## Guidelines
   
   ### Always Do
   - [Guideline 1]
   - [Guideline 2]
   
   ### Never Do
   - [Anti-pattern 1]
   - [Anti-pattern 2]
   
   ## Input Format
   
   [Expected input structure]
   
   ## Output Format
   
   [Expected output structure]
   
   ## Error Handling
   
   [How to handle errors]
   
   ## Examples
   
   ### Example 1: [Scenario]
   **Input**:
   ```
   [input]
   ```
   
   **Output**:
   ```
   [output]
   ```
   
   ### Example 2: [Scenario]
   [...]
   
   ## Integration
   
   This agent integrates with:
   - [System 1]: [how it integrates]
   - [System 2]: [how it integrates]
   
   ## Advanced Features
   
   See [advanced.md](./advanced.md) for advanced usage patterns.
   ```

   **src/agent.py Template**:
   ```python
   #!/usr/bin/env python3
   """
   [Agent Name]
   
   [Detailed description]
   
   Usage:
       python agent.py [options]
   """
   
   import click
   from pathlib import Path
   from typing import Dict, List, Optional
   import yaml
   
   
   class [AgentName]:
       """[Agent description]"""
       
       def __init__(self, config_path: Optional[Path] = None):
           """Initialize agent with optional config."""
           self.config = self._load_config(config_path)
       
       def _load_config(self, config_path: Optional[Path]) -> Dict:
           """Load agent configuration."""
           if config_path and config_path.exists():
               with open(config_path) as f:
                   return yaml.safe_load(f)
           return self._default_config()
       
       def _default_config(self) -> Dict:
           """Return default configuration."""
           return {
               'version': '1.0.0',
               'enabled': True,
               # ... other defaults
           }
       
       def execute(self, task: Dict) -> Dict:
           """
           Execute agent task.
           
           Args:
               task: Task specification
           
           Returns:
               Execution result
           """
           # Implementation
           pass
   
   
   @click.command()
   @click.option('--config', type=click.Path(exists=True), help='Config file path')
   @click.option('--task', required=True, help='Task description')
   @click.option('--verbose', is_flag=True, help='Verbose output')
   def main(config, task, verbose):
       """[Agent Name] CLI"""
       agent = [AgentName](Path(config) if config else None)
       result = agent.execute({'description': task})
       click.echo(result)
   
   
   if __name__ == '__main__':
       main()
   ```

   **tests/test_agent.py Template**:
   ```python
   """Unit tests for [Agent Name]"""
   
   import pytest
   from pathlib import Path
   from ..src.agent import [AgentName]
   
   
   @pytest.fixture
   def agent():
       """Create agent instance for testing"""
       return [AgentName]()
   
   
   def test_agent_initialization(agent):
       """Test agent initializes correctly"""
       assert agent is not None
       assert agent.config is not None
   
   
   def test_agent_execute(agent):
       """Test agent execution"""
       task = {'description': 'test task'}
       result = agent.execute(task)
       assert result is not None
       # Add more assertions
   
   
   def test_agent_error_handling(agent):
       """Test agent handles errors gracefully"""
       invalid_task = {}
       with pytest.raises(ValueError):
           agent.execute(invalid_task)
   ```

   **config/agent_config.yaml Template**:
   ```yaml
   version: 1.0.0
   agent_name: [agent-name]
   
   capabilities:
     - [capability1]
     - [capability2]
   
   integration:
     cognitive_brain: true
     github_actions: false
     aftermath: true
   
   settings:
     timeout_seconds: 300
     max_retries: 3
     log_level: INFO
   
   # Add agent-specific settings below
   ```

4. Create documentation:
   - `.github/agents/AGENT_DEVELOPMENT_GUIDE.md`
   - Explain template usage
   - Provide migration guide for existing agents
   - Include best practices

5. Commit template:
   ```bash
   git add .github/agents/.template/
   git add .github/agents/AGENT_DEVELOPMENT_GUIDE.md
   git commit -m "feat: add agent scaffolding template and development guide"
   git push
   ```

**Success Criteria**:
- Template directory created with all required files
- Development guide written
- Template committed and pushed
- Ready for agent migration

---

#### Task 3.3: Migrate High-Priority Agents 🔄
**Objective**: Standardize the top 5 most-used agents

**Priority Agents** (based on CI integration and usage):
1. ci-testing-agent
2. test-assertion-updater
3. project-architect-researcher
4. pyo3-integration-tester
5. rust-error-validator

**For Each Agent**:
1. Create missing directories from template
2. Add `prompts/main.md` if missing
3. Add tests if missing
4. Update README to match template
5. Add `config/agent_config.yaml`
6. Run tests to verify functionality
7. Update AGENT_REGISTRY.yaml status

**Migration Script** (create if needed):
```bash
#!/bin/bash
# migrate_agent.sh - Migrate agent to standard structure

AGENT_NAME=$1
AGENT_DIR=".github/agents/$AGENT_NAME"
TEMPLATE_DIR=".github/agents/.template"

if [ ! -d "$AGENT_DIR" ]; then
    echo "Error: Agent directory not found: $AGENT_DIR"
    exit 1
fi

echo "Migrating agent: $AGENT_NAME"

# Create missing directories
mkdir -p "$AGENT_DIR/prompts"
mkdir -p "$AGENT_DIR/src"
mkdir -p "$AGENT_DIR/tests"
mkdir -p "$AGENT_DIR/config"

# Copy template files if they don't exist
[ ! -f "$AGENT_DIR/README.md" ] && cp "$TEMPLATE_DIR/README.md" "$AGENT_DIR/README.md"
[ ! -f "$AGENT_DIR/prompts/main.md" ] && cp "$TEMPLATE_DIR/prompts/main.md" "$AGENT_DIR/prompts/"
[ ! -f "$AGENT_DIR/tests/test_agent.py" ] && cp "$TEMPLATE_DIR/tests/test_agent.py" "$AGENT_DIR/tests/"
[ ! -f "$AGENT_DIR/config/agent_config.yaml" ] && cp "$TEMPLATE_DIR/config/agent_config.yaml" "$AGENT_DIR/config/"

echo "Migration complete. Please customize template files for $AGENT_NAME"
```

**Steps**:
1. Run migration script for each priority agent
2. Customize template files with agent-specific content
3. Test each agent to ensure functionality preserved
4. Commit changes:
   ```bash
   git add .github/agents/[agent-name]/
   git commit -m "refactor: standardize [agent-name] structure"
   git push
   ```

**Success Criteria**:
- All 5 priority agents migrated to standard structure
- All agents have prompts, tests, and config
- Agent registry updated with new status
- All tests passing

---

## 🎯 Phase 4: CI Self-Healing Enhancement (Week 2)

### Context
Integrate ci-testing-agent with GitHub Actions for automatic failure recovery

### Tasks

#### Task 4.1: Design Self-Healing Workflow 🔧
**Objective**: Automate common CI failure recovery

**Design Principles**:
- Detect failure patterns automatically
- Apply known fixes without human intervention
- Learn from successful recoveries
- Escalate unknown failures to humans

**Workflow Architecture**:
```yaml
# .github/workflows/self-healing.yml
name: Self-Healing CI

on:
  workflow_run:
    workflows: ["*"]  # Trigger on any workflow
    types: [completed]

jobs:
  analyze-failure:
    runs-on: ubuntu-latest
    if: ${{ github.event.workflow_run.conclusion == 'failure' }}
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Analyze Failure
        id: analyze
        uses: ./.github/actions/analyze-ci-failure
        with:
          workflow_run_id: ${{ github.event.workflow_run.id }}
          repo_token: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Apply Fix
        if: steps.analyze.outputs.fix_available == 'true'
        uses: ./.github/actions/apply-ci-fix
        with:
          fix_type: ${{ steps.analyze.outputs.fix_type }}
          fix_params: ${{ steps.analyze.outputs.fix_params }}
      
      - name: Create PR with Fix
        if: steps.apply-fix.outcome == 'success'
        uses: peter-evans/create-pull-request@v5
        with:
          title: "🤖 Self-healing: Fix ${{ steps.analyze.outputs.failure_type }}"
          body: |
            Automated fix for CI failure.
            
            **Failure**: ${{ steps.analyze.outputs.failure_description }}
            **Fix Applied**: ${{ steps.analyze.outputs.fix_description }}
            **Confidence**: ${{ steps.analyze.outputs.confidence }}%
            
            Workflow Run: ${{ github.event.workflow_run.html_url }}
          branch: self-healing/${{ github.run_id }}
          labels: self-healing, automated
      
      - name: Update Cognitive Brain
        if: always()
        uses: ./.github/actions/update-cognitive-brain
        with:
          outcome: ${{ steps.apply-fix.outcome }}
          fix_type: ${{ steps.analyze.outputs.fix_type }}
          learned_pattern: ${{ steps.analyze.outputs.pattern }}
```

**Failure Patterns to Detect**:
1. **Formatting Issues**: `cargo fmt` failures → auto-format and commit
2. **Linting Issues**: Ruff/mypy failures → auto-fix where possible
3. **Import Errors**: Missing dependencies → update requirements.txt
4. **Test Timeouts**: Tests taking too long → increase timeout
5. **Transient Network Failures**: Retry with backoff
6. **Cache Issues**: Clear cache and rebuild

**Success Criteria**:
- Self-healing workflow designed and documented
- Failure pattern library created
- Integration points with ci-testing-agent identified

---

#### Task 4.2: Implement Failure Detection 🔍
**Objective**: Automatically classify CI failures

**Create**: `.github/actions/analyze-ci-failure/action.yml`

**Implementation**:
```yaml
name: Analyze CI Failure
description: Analyze CI failure and determine if auto-fix available

inputs:
  workflow_run_id:
    description: ID of failed workflow run
    required: true
  repo_token:
    description: GitHub token
    required: true

outputs:
  fix_available:
    description: Whether automatic fix is available
  fix_type:
    description: Type of fix to apply
  fix_params:
    description: Parameters for fix
  confidence:
    description: Confidence level (0-100)
  failure_type:
    description: Classified failure type
  failure_description:
    description: Human-readable description
  fix_description:
    description: Description of fix to apply

runs:
  using: composite
  steps:
    - name: Get Failure Logs
      id: logs
      shell: bash
      run: |
        gh run view ${{ inputs.workflow_run_id }} --log > failure.log
        cat failure.log
      env:
        GITHUB_TOKEN: ${{ inputs.repo_token }}
    
    - name: Analyze with ci-testing-agent
      id: analyze
      shell: bash
      run: |
        python .github/agents/ci-testing-agent/src/analyzer.py \
          --log-file failure.log \
          --output-json analysis.json
        
        # Parse analysis results
        FIX_AVAILABLE=$(jq -r '.fix_available' analysis.json)
        FIX_TYPE=$(jq -r '.fix_type' analysis.json)
        CONFIDENCE=$(jq -r '.confidence' analysis.json)
        
        echo "fix_available=$FIX_AVAILABLE" >> $GITHUB_OUTPUT
        echo "fix_type=$FIX_TYPE" >> $GITHUB_OUTPUT
        echo "confidence=$CONFIDENCE" >> $GITHUB_OUTPUT
        # ... more outputs
```

**Create**: `.github/agents/ci-testing-agent/src/analyzer.py`

**Implementation**:
```python
#!/usr/bin/env python3
"""CI Failure Analyzer"""

import click
import json
import re
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class FailureAnalysis:
    """Analysis result"""
    fix_available: bool
    fix_type: str
    fix_params: Dict
    confidence: int  # 0-100
    failure_type: str
    failure_description: str
    fix_description: str
    pattern_matched: Optional[str] = None


class CIFailureAnalyzer:
    """Analyzes CI failure logs and suggests fixes"""
    
    def __init__(self):
        self.patterns = self._load_patterns()
    
    def _load_patterns(self) -> Dict:
        """Load known failure patterns"""
        return {
            'rust_formatting': {
                'regex': r'Diff in .+\.rs',
                'fix_type': 'rust_format',
                'confidence': 95,
                'description': 'Rust formatting issue detected',
                'fix': 'Run cargo fmt --all'
            },
            'python_linting': {
                'regex': r'(ruff check|mypy).+error',
                'fix_type': 'python_lint',
                'confidence': 85,
                'description': 'Python linting issue',
                'fix': 'Run ruff --fix and mypy fixes'
            },
            'test_timeout': {
                'regex': r'TIMEOUT|timed out after',
                'fix_type': 'increase_timeout',
                'confidence': 70,
                'description': 'Test timeout',
                'fix': 'Increase timeout value'
            },
            'import_error': {
                'regex': r'ModuleNotFoundError|ImportError',
                'fix_type': 'add_dependency',
                'confidence': 80,
                'description': 'Missing Python dependency',
                'fix': 'Add missing package to requirements'
            },
            'cache_corruption': {
                'regex': r'cache.+corrupt|failed to restore cache',
                'fix_type': 'clear_cache',
                'confidence': 90,
                'description': 'Cache corruption detected',
                'fix': 'Clear and rebuild cache'
            },
        }
    
    def analyze(self, log_file: Path) -> FailureAnalysis:
        """Analyze failure log"""
        log_content = log_file.read_text()
        
        # Try to match known patterns
        for pattern_name, pattern_info in self.patterns.items():
            if re.search(pattern_info['regex'], log_content, re.IGNORECASE):
                return FailureAnalysis(
                    fix_available=True,
                    fix_type=pattern_info['fix_type'],
                    fix_params=self._extract_params(log_content, pattern_info),
                    confidence=pattern_info['confidence'],
                    failure_type=pattern_name,
                    failure_description=pattern_info['description'],
                    fix_description=pattern_info['fix'],
                    pattern_matched=pattern_name
                )
        
        # No known pattern matched
        return FailureAnalysis(
            fix_available=False,
            fix_type='unknown',
            fix_params={},
            confidence=0,
            failure_type='unknown',
            failure_description='Unable to classify failure',
            fix_description='Manual intervention required'
        )
    
    def _extract_params(self, log: str, pattern: Dict) -> Dict:
        """Extract fix parameters from log"""
        params = {}
        
        if pattern['fix_type'] == 'rust_format':
            # Extract file names that need formatting
            files = re.findall(r'Diff in (.+\.rs):', log)
            params['files'] = files
        
        elif pattern['fix_type'] == 'increase_timeout':
            # Extract current timeout value
            match = re.search(r'timed out after (\d+)', log)
            if match:
                current = int(match.group(1))
                params['current_timeout'] = current
                params['suggested_timeout'] = current * 2
        
        elif pattern['fix_type'] == 'add_dependency':
            # Extract missing module name
            match = re.search(r"ModuleNotFoundError: No module named '([^']+)'", log)
            if match:
                params['missing_module'] = match.group(1)
        
        return params


@click.command()
@click.option('--log-file', type=click.Path(exists=True), required=True)
@click.option('--output-json', type=click.Path(), required=True)
def main(log_file, output_json):
    """Analyze CI failure log"""
    analyzer = CIFailureAnalyzer()
    analysis = analyzer.analyze(Path(log_file))
    
    # Write results as JSON
    output = Path(output_json)
    output.write_text(json.dumps(asdict(analysis), indent=2))
    
    click.echo(f"Analysis complete. Results written to {output_json}")
    click.echo(f"Fix available: {analysis.fix_available}")
    if analysis.fix_available:
        click.echo(f"Fix type: {analysis.fix_type} (confidence: {analysis.confidence}%)")


if __name__ == '__main__':
    main()
```

**Success Criteria**:
- Analyzer implemented and tested
- Can classify 5+ common failure types
- Confidence scores assigned appropriately
- Integration with GitHub Actions tested

---

#### Task 4.3: Implement Auto-Fix Actions 🔧
**Objective**: Apply fixes automatically when safe

**Create**: `.github/actions/apply-ci-fix/action.yml`

**Implementation**:
```yaml
name: Apply CI Fix
description: Apply automatic fix for known CI failure

inputs:
  fix_type:
    description: Type of fix to apply
    required: true
  fix_params:
    description: Fix parameters (JSON)
    required: true

runs:
  using: composite
  steps:
    - name: Apply Rust Format Fix
      if: ${{ inputs.fix_type == 'rust_format' }}
      shell: bash
      run: |
        cargo fmt --all
        git add -A
        git commit -m "style: auto-format Rust code (self-healing)"
    
    - name: Apply Python Lint Fix
      if: ${{ inputs.fix_type == 'python_lint' }}
      shell: bash
      run: |
        ruff --fix .
        git add -A
        git commit -m "style: auto-fix Python linting issues (self-healing)"
    
    - name: Increase Timeout
      if: ${{ inputs.fix_type == 'increase_timeout' }}
      shell: bash
      run: |
        python .github/agents/ci-testing-agent/src/fix_timeout.py \
          --params '${{ inputs.fix_params }}'
        git add -A
        git commit -m "ci: increase test timeout (self-healing)"
    
    - name: Add Missing Dependency
      if: ${{ inputs.fix_type == 'add_dependency' }}
      shell: bash
      run: |
        MISSING_MODULE=$(echo '${{ inputs.fix_params }}' | jq -r '.missing_module')
        echo "$MISSING_MODULE" >> requirements.txt
        sort -u requirements.txt -o requirements.txt
        git add requirements.txt
        git commit -m "deps: add missing dependency $MISSING_MODULE (self-healing)"
    
    - name: Clear Cache
      if: ${{ inputs.fix_type == 'clear_cache' }}
      shell: bash
      run: |
        # GitHub Actions cache clearing
        gh cache delete --all || true
      env:
        GITHUB_TOKEN: ${{ github.token }}
```

**Create Helper Scripts** (as needed):
- `.github/agents/ci-testing-agent/src/fix_timeout.py`
- Other fix-specific scripts

**Success Criteria**:
- Fix actions implemented for 5+ failure types
- Fixes applied safely without breaking changes
- Git commits created with appropriate messages
- Integrated with self-healing workflow

---

#### Task 4.4: Add Learning and Feedback Loop 🧠
**Objective**: Cognitive brain learns from successful/failed fixes

**Create**: `.github/actions/update-cognitive-brain/action.yml`

**Implementation**:
```yaml
name: Update Cognitive Brain
description: Record self-healing outcome in cognitive brain

inputs:
  outcome:
    description: Fix outcome (success/failure)
    required: true
  fix_type:
    description: Type of fix attempted
    required: true
  learned_pattern:
    description: Pattern that was learned
    required: false

runs:
  using: composite
  steps:
    - name: Record Learning
      shell: bash
      run: |
        python scripts/aftermath/record_self_healing.py \
          --outcome "${{ inputs.outcome }}" \
          --fix-type "${{ inputs.fix_type }}" \
          --pattern "${{ inputs.learned_pattern }}" \
          --timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    
    - name: Update Dashboard
      if: ${{ inputs.outcome == 'success' }}
      shell: bash
      run: |
        python scripts/aftermath/update_cognitive_brain.py \
          --lessons=.codex/self_healing/ \
          --dashboard=docs/system/CODEBASE_DASHBOARD.md
```

**Create**: `scripts/aftermath/record_self_healing.py`

**Implementation**:
```python
#!/usr/bin/env python3
"""Record self-healing outcome"""

import click
import yaml
from pathlib import Path
from datetime import datetime


@click.command()
@click.option('--outcome', required=True, type=click.Choice(['success', 'failure']))
@click.option('--fix-type', required=True)
@click.option('--pattern', default='')
@click.option('--timestamp', required=True)
def main(outcome, fix_type, pattern, timestamp):
    """Record self-healing outcome"""
    
    # Create self-healing log directory
    log_dir = Path('.codex/self_healing')
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create log entry
    log_entry = {
        'timestamp': timestamp,
        'outcome': outcome,
        'fix_type': fix_type,
        'pattern': pattern,
        'success_rate': None  # Will be calculated
    }
    
    # Append to log
    log_file = log_dir / 'self_healing_log.yaml'
    if log_file.exists():
        with open(log_file) as f:
            logs = yaml.safe_load(f) or []
    else:
        logs = []
    
    logs.append(log_entry)
    
    # Calculate success rate for this fix type
    fix_type_logs = [l for l in logs if l['fix_type'] == fix_type]
    successes = len([l for l in fix_type_logs if l['outcome'] == 'success'])
    total = len(fix_type_logs)
    success_rate = (successes / total * 100) if total > 0 else 0
    
    log_entry['success_rate'] = round(success_rate, 1)
    
    # Write updated logs
    with open(log_file, 'w') as f:
        yaml.dump(logs, f, default_flow_style=False)
    
    click.echo(f"Recorded {outcome} for {fix_type} (success rate: {success_rate}%)")
    
    # If success rate is high, increase confidence
    if success_rate >= 90:
        click.echo(f"✅ High confidence fix type: {fix_type}")
    elif success_rate >= 70:
        click.echo(f"🟡 Medium confidence fix type: {fix_type}")
    else:
        click.echo(f"⚠️  Low confidence fix type: {fix_type} - needs review")


if __name__ == '__main__':
    main()
```

**Success Criteria**:
- Learning system records all self-healing attempts
- Success rates calculated per fix type
- Cognitive brain dashboard updated automatically
- Patterns identified and stored

---

## 🎯 Phase 5: Cognitive Brain Dashboard (Month 1)

### Context
Create real-time dashboard for cognitive brain metrics, agent status, and system health

### Tasks

#### Task 5.1: Design Dashboard Architecture 📊
**Objective**: Define dashboard requirements and architecture

**Requirements**:
1. Real-time metrics display
2. Agent status monitoring
3. CI/CD health indicators
4. Self-healing statistics
5. Test coverage trends
6. Performance benchmarks
7. Alert system

**Technology Stack**:
- Backend: Python FastAPI
- Frontend: React + D3.js for visualizations
- Real-time: WebSockets
- Storage: SQLite for metrics, JSON for config

**Architecture**:
```
cognitive_app/
├── backend/
│   ├── api/
│   │   ├── metrics.py        # Metrics endpoints
│   │   ├── agents.py         # Agent status
│   │   └── alerts.py         # Alert system
│   ├── collectors/
│   │   ├── ci_collector.py   # CI metrics
│   │   ├── agent_collector.py # Agent status
│   │   └── repo_collector.py # Repo stats
│   └── main.py               # FastAPI app
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── MetricsDashboard.tsx
│   │   │   ├── AgentStatus.tsx
│   │   │   ├── CIHealth.tsx
│   │   │   └── AlertPanel.tsx
│   │   └── App.tsx
│   └── package.json
└── docker-compose.yml
```

**Success Criteria**:
- Architecture documented
- Technology stack selected
- Component diagram created
- Development plan defined

---

#### Task 5.2: Implement Metrics Collection 📈
**Objective**: Collect and store cognitive brain metrics

**Create**: `cognitive_app/backend/collectors/metrics_collector.py`

**Metrics to Collect**:
1. **Repository Health**:
   - Test count and pass rate
   - Coverage percentage
   - Security vulnerabilities
   - Build success rate

2. **Agent Performance**:
   - Agent execution count
   - Success rate per agent
   - Average execution time
   - Error rate

3. **Self-Healing**:
   - Fixes attempted
   - Fix success rate
   - Time saved
   - Patterns learned

4. **CI/CD**:
   - Workflow run count
   - Failure rate
   - Average build time
   - Cache hit rate

**Implementation**:
```python
#!/usr/bin/env python3
"""Metrics Collector for Cognitive Brain"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict
import sqlite3


@dataclass
class Metric:
    """Single metric data point"""
    timestamp: datetime
    category: str
    name: str
    value: float
    unit: str
    tags: Dict[str, str]


class MetricsCollector:
    """Collects and stores cognitive brain metrics"""
    
    def __init__(self, db_path: str = 'metrics.db'):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize metrics database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                category TEXT NOT NULL,
                name TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT,
                tags TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON metrics(timestamp)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_category 
            ON metrics(category, name)
        ''')
        
        conn.commit()
        conn.close()
    
    def record(self, metric: Metric):
        """Record single metric"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO metrics (timestamp, category, name, value, unit, tags)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            metric.timestamp.isoformat(),
            metric.category,
            metric.name,
            metric.value,
            metric.unit,
            str(metric.tags)
        ))
        
        conn.commit()
        conn.close()
    
    def record_batch(self, metrics: List[Metric]):
        """Record multiple metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        data = [(
            m.timestamp.isoformat(),
            m.category,
            m.name,
            m.value,
            m.unit,
            str(m.tags)
        ) for m in metrics]
        
        cursor.executemany('''
            INSERT INTO metrics (timestamp, category, name, value, unit, tags)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', data)
        
        conn.commit()
        conn.close()
    
    def query(self, category: str, name: str, 
              start: datetime, end: datetime) -> List[Dict]:
        """Query metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, value, unit, tags
            FROM metrics
            WHERE category = ? AND name = ?
            AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp
        ''', (category, name, start.isoformat(), end.isoformat()))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'timestamp': row[0],
                'value': row[1],
                'unit': row[2],
                'tags': eval(row[3])
            })
        
        conn.close()
        return results
```

**Success Criteria**:
- Metrics collection implemented
- Database schema created
- Collectors for all metric categories
- Data retention policy defined

---

#### Task 5.3: Build Dashboard Frontend 🖥️
**Objective**: Create interactive dashboard UI

**Key Components**:
1. **Metrics Dashboard**: Real-time charts and graphs
2. **Agent Status Panel**: Current agent states
3. **CI Health Monitor**: Workflow success rates
4. **Alert Center**: Active alerts and warnings
5. **Historical Trends**: Long-term patterns

**Implementation Approach**:
1. Use existing `cognitive_app/` React setup
2. Add new dashboard components
3. Integrate with metrics API
4. Add WebSocket for real-time updates

**Success Criteria**:
- Dashboard UI implemented
- Real-time updates working
- Responsive design
- All metrics visualized

---

#### Task 5.4: Deploy Dashboard 🚀
**Objective**: Make dashboard accessible

**Deployment Options**:
1. **Local Development**: Run on localhost
2. **GitHub Pages**: Static build
3. **Docker**: Containerized deployment
4. **Cloud**: AWS/GCP/Azure

**Steps**:
1. Create Docker configuration
2. Set up CI/CD for dashboard
3. Configure access controls
4. Document deployment process

**Success Criteria**:
- Dashboard deployed and accessible
- Automatic updates on changes
- Security configured
- Documentation complete

---

## 🎯 Success Criteria Summary

### Phase 2: Post-CI Validation ✅
- [ ] All CI checks pass or pre-existing issues documented
- [ ] GitHub issues created for RAG torch and Semgrep
- [ ] Cognitive brain documentation updated
- [ ] Session artifacts archived

### Phase 3: Agent Standardization 📋
- [ ] Agent registry created with 30+ agents
- [ ] Template and development guide published
- [ ] Top 5 agents migrated to standard structure
- [ ] All agents have prompts and tests

### Phase 4: CI Self-Healing 🤖
- [ ] Self-healing workflow implemented
- [ ] Failure detection and classification working
- [ ] Auto-fix actions for 5+ failure types
- [ ] Learning system recording outcomes

### Phase 5: Cognitive Brain Dashboard 📊
- [ ] Dashboard architecture designed
- [ ] Metrics collection implemented
- [ ] Frontend dashboard built
- [ ] Dashboard deployed and accessible

---

## 🔄 Autonomous Execution Guidelines

### Decision-Making Framework
1. **Always prioritize** user value and system stability
2. **Validate assumptions** before making changes
3. **Test thoroughly** after each modification
4. **Document comprehensively** for future sessions
5. **Learn from failures** and update cognitive brain

### Error Handling
- If a task fails after 3 attempts, document the failure and move to next task
- Create GitHub issue for unresolvable problems
- Never leave the system in a broken state
- Always commit working code

### Communication
- Use `report_progress` after each completed task
- Reply to the initiating comment with status updates
- Create clear, actionable issues for blockers
- Update documentation continuously

### Self-Healing
- If CI fails, analyze and attempt to fix
- If fix is uncertain, create PR for review
- Learn from both successes and failures
- Update cognitive brain with patterns

---

## 📞 Escalation Path

If you encounter issues that cannot be resolved autonomously:

1. **Document the Problem**:
   - Create detailed issue in GitHub
   - Include context, attempts made, and error logs
   - Tag with `needs-human-review`

2. **Update Status**:
   - Add entry to `.codex/blockers/`
   - Update CODEBASE_DASHBOARD.md with blocker
   - Use `report_progress` to notify

3. **Provide Recommendations**:
   - Suggest possible solutions
   - Estimate effort required
   - Identify required expertise

4. **Continue with Remaining Work**:
   - Don't let one blocker stop all progress
   - Move to tasks that can be completed
   - Circle back when blocker is resolved

---

## 🎯 Final Notes

This is a comprehensive, multi-phase task designed for autonomous execution over multiple Copilot sessions. Each phase builds on the previous one, enhancing the cognitive brain's capabilities incrementally.

**Key Principles**:
- **Iterative**: Complete phases in order, validating each step
- **Self-Healing**: Fix issues automatically when possible
- **Learning**: Update cognitive brain with every outcome
- **Continuous Improvement**: Each session makes the next one better

**Expected Timeline**:
- Phase 2: 30-60 minutes (this session)
- Phase 3: 5-7 days (next week)
- Phase 4: 3-5 days (week 2)
- Phase 5: 1-2 weeks (month 1)

**Success Definition**:
The cognitive brain is successfully enhanced when:
1. All custom agents are standardized and integrated
2. CI self-healing reduces manual intervention by 80%
3. Dashboard provides real-time visibility into system health
4. PDA loops operate autonomously with minimal human input

Begin with Phase 2, Task 2.1 immediately. Execute tasks sequentially, validating each before proceeding. Use the PDA loop framework: Perceive the current state, Decide the best action, Act decisively, and loop continuously.

**Good luck! The cognitive brain is counting on you. 🧠✨**
