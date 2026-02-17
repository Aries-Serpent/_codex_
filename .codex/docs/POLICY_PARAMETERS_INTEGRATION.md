# Policy Parameters Integration Guide

> **Generated**: 2026-02-17T12:00:00Z  
> **Repository**: Aries-Serpent/_codex_  
> **Purpose**: Integrate all repository policies as configurable agent parameters  
> **Status**: ✅ PRODUCTION SPECIFICATION

---

## Executive Summary

This document integrates **three critical policy systems** as operational parameters for AI agents and custom agents:

1. **Codebase Agency Policy** - Comprehensive issue resolution requirements
2. **LFS Policy** - Binary artifact management rules  
3. **GitHub Actions Workflow Awareness** - PR-specific workflow applicability

**Key Insight**: Policies are not just guidelines—they are **mandatory operational parameters** that must be enforced through code, not just documentation.

---

## Table of Contents

1. [Codebase Agency Policy Parameters](#codebase-agency-policy-parameters)
2. [LFS Policy Parameters](#lfs-policy-parameters)
3. [GitHub Actions Workflow Awareness](#github-actions-workflow-awareness)
4. [Unified Parameter System](#unified-parameter-system)
5. [Agent Integration](#agent-integration)
6. [Enforcement Mechanisms](#enforcement-mechanisms)

---

## Codebase Agency Policy Parameters

### Policy Source

**File**: `.codex/CODEBASE_AGENCY_POLICY.md`  
**Version**: 1.0.0  
**Status**: Mandatory for ALL AI agents  
**Enforcement**: Policy violations require immediate correction

### Core Parameters

```python
# Codebase Agency Policy Parameters
class CodebaseAgencyParameters:
    """Mandatory operational parameters from Codebase Agency Policy."""
    
    # Core Principles (Boolean enforcement)
    LEAVE_CODEBASE_BETTER = True  # Always improve beyond task
    ADDRESS_ALL_CONCERNS = True  # Never claim "not my responsibility"
    NO_DEFERRAL_WITHOUT_PLAN = True  # Document all deferred work
    
    # Iteration Requirements
    MIN_ITERATION_ATTEMPTS = 5  # Minimum attempts before giving up
    REQUIRE_ROOT_CAUSE_ANALYSIS = True  # Don't just fix symptoms
    DOCUMENT_LESSONS_LEARNED = True  # Store patterns for future
    
    # Pre-Existing Issue Handling
    FIX_BROKEN_LINKS = True  # Even if you didn't create them
    RESOLVE_CODE_QUALITY_ISSUES = True  # In files you touch
    UPDATE_OUTDATED_DOCS = True  # When encountered
    REMOVE_DEPRECATED_PATTERNS = True  # Proactively clean up
    
    # Planning Requirements
    PLAN_BEFORE_EXECUTION = True  # MUST create plan first
    USE_MARKDOWN_CHECKLISTS = True  # Track progress visibly
    REPORT_PROGRESS_EARLY = True  # Share plan in first commit
    UPDATE_PLAN_AS_WORK_PROGRESSES = True  # Keep current
    
    # Timeline Terminology (Standardized)
    TIMELINE_FORMAT = "ISO_8601"  # 2026-02-17T12:00:00Z
    AVOID_SUBJECTIVE_TERMS = True  # No "soon", "later", "eventually"
    USE_CONCRETE_TIMEFRAMES = True  # "Within 24 hours", "Next sprint"
    
    # CI Data Handling
    USE_MCP_FIRST = True  # GitHub MCP tools for ALL CI data
    MIN_MCP_ATTEMPTS = 3  # Try 3+ MCP approaches first
    DOCUMENT_MCP_EXHAUSTION = True  # If MCP truly can't solve
    NO_SILENT_BASH_FALLBACK = False  # Never silently switch to bash
    
    # Self-Review Requirements
    REQUIRE_CODE_REVIEW_TOOL = True  # Use code_review before finalizing
    REQUIRE_CODEQL_CHECK = True  # Run codeql_checker before merge
    ADDRESS_REVIEW_FEEDBACK = True  # Fix all identified issues
    RE_REVIEW_IF_SIGNIFICANT_CHANGES = True  # Get review again
    
    # Code Quality Standards
    MIN_TEST_COVERAGE = 0.70  # 70% coverage minimum
    REQUIRE_TYPE_HINTS = True  # Python: all functions typed
    REQUIRE_DOCSTRINGS = True  # All public APIs documented
    NO_HARDCODED_SECRETS = True  # Use environment variables
    VALIDATE_SECURITY = True  # Check for vulnerabilities
    
    # Documentation Standards
    UPDATE_DOCS_WITH_CODE = True  # Document code changes
    FIX_DOC_LINKS = True  # Repair broken references
    ADD_EXAMPLES = True  # Include usage examples
    MAINTAIN_CHANGELOG = True  # Update .codex/change_log.md
    
    # AfterMath/PDA Loop Integration
    USE_PDA_LOOP = True  # Plan-Do-Assess for all work
    TAG_AFTERMATH_COMMENTS = True  # Use #AfterMath tags
    STORE_PATTERNS = True  # Save learnings for future agents
    TRACK_COGNITIVE_METRICS = True  # Monitor quantum decision quality
    
    # Follow-Up Prompt Requirements
    GENERATE_FOLLOWUP_PROMPT = True  # Create continuation guidance
    DOCUMENT_NEXT_STEPS = True  # Clear handoff to next agent
    LINK_RELATED_WORK = True  # Connect to other PRs/issues
```

### Prohibited Statements (Enforcement)

```python
# Statements that trigger policy violations
PROHIBITED_STATEMENTS = [
    # "Not my responsibility" variants
    "This is not related to my PR",
    "These are pre-existing issues",
    "My PR only adds files to X",
    "That's someone else's problem",
    "I only changed X, not Y",
    "This was already broken",
    
    # Deferral without plan
    "I'll skip fixing this",
    "We can address this later",
    "Future work",  # without documented plan
    "TODO: fix this",  # without detailed steps
    
    # Quality compromises
    "Good enough for now",
    "This is quick and dirty",
    "Just a temporary fix",
    "We'll refactor later",  # without plan
]

def validate_statement(statement: str) -> Tuple[bool, Optional[str]]:
    """Validate statement against prohibited patterns."""
    for prohibited in PROHIBITED_STATEMENTS:
        if prohibited.lower() in statement.lower():
            return False, f"Policy violation: '{prohibited}' detected"
    return True, None
```

### Policy Enforcement Checkpoints

```python
class PolicyEnforcementCheckpoint:
    """Enforce Codebase Agency Policy at key checkpoints."""
    
    def __init__(self):
        self.violations = []
        self.parameters = CodebaseAgencyParameters()
    
    def pre_commit_check(self, changes: Dict) -> bool:
        """Pre-commit policy validation."""
        checks = []
        
        # Check 1: Plan documented?
        if not changes.get("plan_documented"):
            self.violations.append("Missing plan documentation")
            checks.append(False)
        
        # Check 2: All issues addressed?
        if changes.get("known_issues_count", 0) > 0:
            self.violations.append(f"{changes['known_issues_count']} issues left unaddressed")
            checks.append(False)
        
        # Check 3: Documentation updated?
        if changes.get("code_changed") and not changes.get("docs_updated"):
            self.violations.append("Code changed but docs not updated")
            checks.append(False)
        
        # Check 4: Tests added?
        if changes.get("code_changed") and not changes.get("tests_added"):
            self.violations.append("Code changed but no tests added")
            checks.append(False)
        
        # Check 5: Review completed?
        if not changes.get("code_review_passed"):
            self.violations.append("code_review tool not run")
            checks.append(False)
        
        return all(checks)
    
    def pre_pr_check(self, pr_data: Dict) -> bool:
        """Pre-PR policy validation."""
        checks = []
        
        # Check 1: Follow-up prompt?
        if not pr_data.get("followup_prompt_generated"):
            self.violations.append("Missing follow-up prompt")
            checks.append(False)
        
        # Check 2: Changelog updated?
        if not pr_data.get("changelog_updated"):
            self.violations.append("Changelog not updated")
            checks.append(False)
        
        # Check 3: All links valid?
        if pr_data.get("broken_links_count", 0) > 0:
            self.violations.append(f"{pr_data['broken_links_count']} broken links")
            checks.append(False)
        
        return all(checks)
```

---

## LFS Policy Parameters

### Policy Source

**File**: `docs/guides/lfs_policy.md`  
**Purpose**: Prevent binary bloat in Git repository  
**Enforcement**: Pre-commit hooks + CI validation

### Core Parameters

```python
# LFS Policy Parameters
class LFSPolicyParameters:
    """Git LFS policy enforcement parameters."""
    
    # File Size Thresholds (bytes)
    MAX_FILE_SIZE_WITHOUT_LFS = 1_048_576  # 1 MB
    WARNING_SIZE = 524_288  # 512 KB (warn but allow)
    CRITICAL_SIZE = 5_242_880  # 5 MB (block without LFS)
    
    # File Type Rules
    NEVER_COMMIT = [
        # Build artifacts
        "*.pyc", "*.pyo", "*.so", "*.dll", "*.dylib",
        "__pycache__", "*.egg-info", "dist/", "build/",
        "node_modules/", ".next/", ".nuxt/",
        
        # IDE/Editor files
        ".vscode/", ".idea/", "*.swp", "*.swo", "*~",
        
        # OS files
        ".DS_Store", "Thumbs.db", "desktop.ini",
        
        # Temporary files
        "*.tmp", "*.temp", "*.log", "*.cache",
        
        # Large data files (require LFS)
        "*.db", "*.sqlite", "*.sql.gz",
    ]
    
    REQUIRE_LFS = [
        # Models and weights
        "*.h5", "*.pkl", "*.pth", "*.onnx", "*.pb",
        
        # Large datasets
        "*.parquet", "*.feather", "*.hdf5",
        
        # Media files
        "*.mp4", "*.mov", "*.avi", "*.mkv",
        "*.mp3", "*.wav", "*.flac",
        "*.png", "*.jpg", "*.jpeg",  # if > 1MB
        
        # Archives
        "*.zip", "*.tar.gz", "*.7z", "*.rar",
    ]
    
    ALLOWED_EXCEPTIONS = [
        # Small test fixtures
        "tests/fixtures/*.png",  # if < 100KB
        "docs/images/*.jpg",  # if < 500KB
        
        # Small data samples
        "examples/data/*.csv",  # if < 1MB
    ]
    
    # Documentation Requirements
    REQUIRE_DOCUMENTATION_FOR_LFS = True  # Explain why LFS needed
    LFS_DOCUMENTATION_PATH = ".codex/lfs_inventory.md"
    
    # Artifact Storage
    ARTIFACT_DIRECTORY = ".codex/"  # Artifacts go here
    ARTIFACT_GITIGNORE = True  # .codex/ in .gitignore
    ARTIFACT_RETENTION_DAYS = 30  # How long to keep artifacts
```

### LFS Enforcement

```python
class LFSPolicyEnforcer:
    """Enforce LFS policy at pre-commit."""
    
    def __init__(self):
        self.params = LFSPolicyParameters()
        self.violations = []
    
    def check_file(self, file_path: str, file_size: int) -> Tuple[bool, Optional[str]]:
        """Check if file complies with LFS policy."""
        
        # Check 1: Never commit patterns
        for pattern in self.params.NEVER_COMMIT:
            if self._matches_pattern(file_path, pattern):
                return False, f"File matches NEVER_COMMIT pattern: {pattern}"
        
        # Check 2: Size threshold
        if file_size > self.params.CRITICAL_SIZE:
            # Check if LFS enabled
            if not self._is_lfs_tracked(file_path):
                return False, f"File {file_size/1_048_576:.1f}MB exceeds limit without LFS"
        
        # Check 3: Requires LFS by extension
        for pattern in self.params.REQUIRE_LFS:
            if self._matches_pattern(file_path, pattern):
                if not self._is_lfs_tracked(file_path):
                    # Check exception list
                    if not self._is_exception(file_path):
                        return False, f"File type requires LFS: {pattern}"
        
        # Check 4: LFS files must be documented
        if self._is_lfs_tracked(file_path):
            if not self._is_documented_in_lfs_inventory(file_path):
                return False, "LFS file not documented in .codex/lfs_inventory.md"
        
        return True, None
    
    def _matches_pattern(self, path: str, pattern: str) -> bool:
        """Check if path matches glob pattern."""
        import fnmatch
        return fnmatch.fnmatch(path, pattern)
    
    def _is_lfs_tracked(self, path: str) -> bool:
        """Check if file is tracked by Git LFS."""
        # Check .gitattributes
        import subprocess
        result = subprocess.run(
            ["git", "check-attr", "filter", path],
            capture_output=True,
            text=True
        )
        return "lfs" in result.stdout
    
    def _is_exception(self, path: str) -> bool:
        """Check if file is in exception list."""
        for pattern in self.params.ALLOWED_EXCEPTIONS:
            if self._matches_pattern(path, pattern):
                return True
        return False
    
    def _is_documented_in_lfs_inventory(self, path: str) -> bool:
        """Check if LFS file is documented."""
        inventory_path = Path(self.params.LFS_DOCUMENTATION_PATH)
        if not inventory_path.exists():
            return False
        
        with open(inventory_path) as f:
            return path in f.read()
```

### LFS Inventory Template

```markdown
# Git LFS Inventory

This file documents all Git LFS tracked files and explains why they require LFS.

## Active LFS Files

| File | Size | Reason | Added By | Date |
|------|------|--------|----------|------|
| models/bert_weights.h5 | 438 MB | BERT model weights for RAG | @mbaetiong | 2026-02-01 |
| datasets/training_data.parquet | 125 MB | Training dataset | @mbaetiong | 2026-01-15 |

## LFS Configuration

```gitattributes
# Models
*.h5 filter=lfs diff=lfs merge=lfs -text
*.pth filter=lfs diff=lfs merge=lfs -text
*.onnx filter=lfs diff=lfs merge=lfs -text

# Datasets
*.parquet filter=lfs diff=lfs merge=lfs -text
*.hdf5 filter=lfs diff=lfs merge=lfs -text

# Media (large only)
*.mp4 filter=lfs diff=lfs merge=lfs -text
*.mov filter=lfs diff=lfs merge=lfs -text
```

## Alternative Storage

For artifacts that don't need version control:
- Use `.codex/` directory (gitignored)
- Use GitHub Actions artifacts (30-180 day retention)
- Use external object storage (S3, GCS, Azure Blob)
```

---

## GitHub Actions Workflow Awareness

### Workflow Analysis

**Total Workflows**: 68 active workflows  
**PR-Triggered**: 34 workflows (50%)  
**Purpose**: Custom agents must know which workflows apply to active PRs

### Workflow Categories

```python
class WorkflowCategories:
    """Categorize workflows by purpose and trigger."""
    
    # PR Quality Gates (MUST pass for merge)
    PR_QUALITY_GATES = [
        "auto-fix-pr-check.yml",  # Auto-fix validation
        "code-quality-coverage-suite.yml",  # Code quality + coverage
        "coverage-with-timeout.yml",  # Coverage thresholds
        "data-quality-suite.yml",  # Data quality checks
        "detect-duplicates.yml",  # Duplicate code detection
        "html_visual_regression.yml",  # Visual regression
        "pre-merge-validation.yml",  # Pre-merge checks
        "test-suite-comprehensive.yml",  # Full test suite
    ]
    
    # PR Enhancement (Optional but recommended)
    PR_ENHANCEMENT = [
        "documentation-link-checker.yml",  # Link validation
        "pr-labeler.yml",  # Auto-label PRs
        "pr-size-checker.yml",  # PR size warnings
        "test-report-comment.yml",  # Test result comments
    ]
    
    # Security Checks (MUST pass)
    SECURITY_CHECKS = [
        "codeql-analysis.yml",  # CodeQL scanning
        "dependency-scan.yml",  # Dependency vulnerabilities
        "secret-scanning.yml",  # Secret detection
        "security-audit.yml",  # Security audit
    ]
    
    # Scheduled Maintenance (Not PR-related)
    SCHEDULED_MAINTENANCE = [
        "artifact-monitoring.yml",  # Every 3-6 hours
        "audit-qa-suite.yml",  # Weekly
        "ci-health-monitor.yml",  # Every 6 hours
        "cognitive-action-decision.yml",  # Every 6 hours
        "cognitive-analysis-feed.yml",  # Daily
        "cognitive-perception.yml",  # Every 6 hours
        "copilot-evolution-suite.yml",  # Every 4 hours
        "dependency-scan.yml",  # Daily
    ]
    
    # Manual Dispatch (On-demand)
    MANUAL_DISPATCH = [
        "app-package-download.yml",
        "auto-fix-common-issues.yml",
        "batch-ci-triage.yml",
        "dependabot-sheriff.yml",
    ]
    
    # Workflow Orchestration (Triggered by other workflows)
    ORCHESTRATION = [
        "agent-orchestration-unified.yml",  # Master orchestrator
        "workflow-health-monitor.yml",  # Health monitoring
    ]
```

### PR Workflow Applicability Matrix

```python
class PRWorkflowApplicability:
    """Determine which workflows apply to a PR."""
    
    def __init__(self, pr_number: int, pr_data: Dict):
        self.pr_number = pr_number
        self.pr_data = pr_data
        self.applicable_workflows = []
    
    def analyze(self) -> List[Dict]:
        """Analyze which workflows apply to this PR."""
        
        # Always applicable (all PRs)
        self.applicable_workflows.extend([
            {
                "workflow": "auto-fix-pr-check.yml",
                "reason": "All PRs checked for auto-fixable issues",
                "required": True,
                "blocking": True,
            },
            {
                "workflow": "code-quality-coverage-suite.yml",
                "reason": "All PRs must pass quality + coverage checks",
                "required": True,
                "blocking": True,
            },
        ])
        
        # Code changes → test suite
        if self._has_code_changes():
            self.applicable_workflows.append({
                "workflow": "test-suite-comprehensive.yml",
                "reason": "Code changes require comprehensive tests",
                "required": True,
                "blocking": True,
            })
        
        # Python code → type checking
        if self._has_python_changes():
            self.applicable_workflows.append({
                "workflow": "type-checking.yml",
                "reason": "Python changes require type validation",
                "required": True,
                "blocking": True,
            })
        
        # Documentation changes → link checking
        if self._has_doc_changes():
            self.applicable_workflows.append({
                "workflow": "documentation-link-checker.yml",
                "reason": "Documentation changes require link validation",
                "required": True,
                "blocking": False,  # Warning only
            })
        
        # Large PR → size warning
        if self._is_large_pr():
            self.applicable_workflows.append({
                "workflow": "pr-size-checker.yml",
                "reason": "Large PR (>500 lines) requires review",
                "required": False,
                "blocking": False,
            })
        
        # Security-sensitive changes → security audit
        if self._has_security_changes():
            self.applicable_workflows.extend([
                {
                    "workflow": "codeql-analysis.yml",
                    "reason": "Security-sensitive changes require CodeQL",
                    "required": True,
                    "blocking": True,
                },
                {
                    "workflow": "security-audit.yml",
                    "reason": "Security changes require comprehensive audit",
                    "required": True,
                    "blocking": True,
                },
            ])
        
        # Dependency changes → scan
        if self._has_dependency_changes():
            self.applicable_workflows.append({
                "workflow": "dependency-scan.yml",
                "reason": "Dependency changes require vulnerability scan",
                "required": True,
                "blocking": True,
            })
        
        # Visual changes → regression test
        if self._has_visual_changes():
            self.applicable_workflows.append({
                "workflow": "html_visual_regression.yml",
                "reason": "Visual changes require regression tests",
                "required": True,
                "blocking": False,  # Can review manually
            })
        
        return self.applicable_workflows
    
    def _has_code_changes(self) -> bool:
        """Check if PR has code changes."""
        changed_files = self.pr_data.get("changed_files", [])
        code_extensions = {".py", ".js", ".ts", ".go", ".rs", ".java"}
        return any(
            Path(f).suffix in code_extensions
            for f in changed_files
        )
    
    def _has_python_changes(self) -> bool:
        """Check if PR has Python changes."""
        changed_files = self.pr_data.get("changed_files", [])
        return any(f.endswith(".py") for f in changed_files)
    
    def _has_doc_changes(self) -> bool:
        """Check if PR has documentation changes."""
        changed_files = self.pr_data.get("changed_files", [])
        return any(f.endswith(".md") for f in changed_files)
    
    def _is_large_pr(self) -> bool:
        """Check if PR is large (>500 lines)."""
        return self.pr_data.get("additions", 0) + self.pr_data.get("deletions", 0) > 500
    
    def _has_security_changes(self) -> bool:
        """Check if PR touches security-sensitive files."""
        changed_files = self.pr_data.get("changed_files", [])
        security_patterns = [
            "src/security/",
            "src/auth/",
            "*/permissions.py",
            "*.secrets.yml",
            ".github/workflows/",
        ]
        return any(
            any(pattern in f for pattern in security_patterns)
            for f in changed_files
        )
    
    def _has_dependency_changes(self) -> bool:
        """Check if PR changes dependencies."""
        changed_files = self.pr_data.get("changed_files", [])
        dependency_files = {
            "pyproject.toml",
            "requirements.txt",
            "package.json",
            "package-lock.json",
            "Cargo.toml",
            "go.mod",
        }
        return any(
            Path(f).name in dependency_files
            for f in changed_files
        )
    
    def _has_visual_changes(self) -> bool:
        """Check if PR has visual/UI changes."""
        changed_files = self.pr_data.get("changed_files", [])
        visual_patterns = [
            "*.html",
            "*.css",
            "*.scss",
            "*.jsx",
            "*.tsx",
            "*/components/",
            "*/templates/",
        ]
        return any(
            any(f.endswith(ext) or pattern in f for ext in [".html", ".css", ".scss"] for pattern in visual_patterns)
            for f in changed_files
        )
```

### Agent Workflow Awareness

```python
class AgentWorkflowAwareness:
    """Make custom agents aware of applicable workflows."""
    
    def __init__(self, pr_number: int):
        self.pr_number = pr_number
        self.pr_data = self._fetch_pr_data()
        self.applicability = PRWorkflowApplicability(pr_number, self.pr_data)
        self.applicable_workflows = self.applicability.analyze()
    
    def get_required_workflows(self) -> List[str]:
        """Get list of required workflows for this PR."""
        return [
            w["workflow"]
            for w in self.applicable_workflows
            if w["required"]
        ]
    
    def get_blocking_workflows(self) -> List[str]:
        """Get list of blocking workflows (must pass for merge)."""
        return [
            w["workflow"]
            for w in self.applicable_workflows
            if w["blocking"]
        ]
    
    def check_workflow_status(self) -> Dict[str, str]:
        """Check status of all applicable workflows."""
        # Use MCP GitHub Actions tools
        from github_mcp_server import actions_list, actions_get
        
        statuses = {}
        for workflow in self.applicable_workflows:
            workflow_name = workflow["workflow"]
            
            # Get latest run for this PR
            runs = actions_list(
                method="list_workflow_runs",
                owner="Aries-Serpent",
                repo="_codex_",
                resource_id=workflow_name,
                workflow_runs_filter={
                    "event": "pull_request",
                    "branch": self.pr_data["head_ref"],
                }
            )
            
            if runs and len(runs) > 0:
                latest_run = runs[0]
                statuses[workflow_name] = {
                    "status": latest_run["status"],
                    "conclusion": latest_run.get("conclusion"),
                    "required": workflow["required"],
                    "blocking": workflow["blocking"],
                }
        
        return statuses
    
    def generate_workflow_report(self) -> str:
        """Generate human-readable workflow status report."""
        statuses = self.check_workflow_status()
        
        report = f"## Workflow Status for PR #{self.pr_number}\n\n"
        
        # Blocking workflows
        report += "### 🚦 Blocking Workflows (Must Pass)\n\n"
        for workflow_name, status in statuses.items():
            if status["blocking"]:
                icon = "✅" if status["conclusion"] == "success" else "❌"
                report += f"- {icon} **{workflow_name}**: {status['status']} ({status.get('conclusion', 'pending')})\n"
        
        # Required but non-blocking
        report += "\n### ⚠️ Required Workflows (Should Pass)\n\n"
        for workflow_name, status in statuses.items():
            if status["required"] and not status["blocking"]:
                icon = "✅" if status["conclusion"] == "success" else "⚠️"
                report += f"- {icon} **{workflow_name}**: {status['status']} ({status.get('conclusion', 'pending')})\n"
        
        # Optional
        report += "\n### 💡 Optional Workflows\n\n"
        for workflow_name, status in statuses.items():
            if not status["required"]:
                icon = "✅" if status["conclusion"] == "success" else "ℹ️"
                report += f"- {icon} **{workflow_name}**: {status['status']} ({status.get('conclusion', 'pending')})\n"
        
        return report
    
    def _fetch_pr_data(self) -> Dict:
        """Fetch PR data using MCP tools."""
        from github_mcp_server import pull_request_read
        
        pr_data = pull_request_read(
            method="get",
            owner="Aries-Serpent",
            repo="_codex_",
            pullNumber=self.pr_number
        )
        
        return pr_data
```

---

## Unified Parameter System

### Complete Parameter Configuration

```json
{
  "version": "2.0.0",
  "generated": "2026-02-17T12:00:00Z",
  
  "codebase_agency_policy": {
    "version": "1.0.0",
    "enabled": true,
    "enforcement_level": "strict",
    
    "core_principles": {
      "leave_codebase_better": true,
      "address_all_concerns": true,
      "no_deferral_without_plan": true
    },
    
    "iteration_requirements": {
      "min_attempts": 5,
      "require_root_cause_analysis": true,
      "document_lessons_learned": true
    },
    
    "pre_existing_issues": {
      "fix_broken_links": true,
      "resolve_code_quality": true,
      "update_outdated_docs": true,
      "remove_deprecated_patterns": true
    },
    
    "planning": {
      "plan_before_execution": true,
      "use_markdown_checklists": true,
      "report_progress_early": true,
      "update_plan_continuously": true
    },
    
    "ci_data_handling": {
      "use_mcp_first": true,
      "min_mcp_attempts": 3,
      "document_mcp_exhaustion": true,
      "no_silent_bash_fallback": true
    },
    
    "quality_control": {
      "require_code_review": true,
      "require_codeql_check": true,
      "address_review_feedback": true,
      "re_review_if_significant_changes": true
    }
  },
  
  "lfs_policy": {
    "version": "1.0.0",
    "enabled": true,
    "enforcement_level": "strict",
    
    "size_thresholds": {
      "max_without_lfs_bytes": 1048576,
      "warning_size_bytes": 524288,
      "critical_size_bytes": 5242880
    },
    
    "require_lfs_patterns": [
      "*.h5", "*.pkl", "*.pth", "*.onnx",
      "*.parquet", "*.hdf5",
      "*.mp4", "*.mov", "*.mp3"
    ],
    
    "never_commit_patterns": [
      "*.pyc", "__pycache__", "node_modules/",
      ".DS_Store", "*.tmp", "*.log"
    ],
    
    "documentation": {
      "require_for_lfs": true,
      "inventory_path": ".codex/lfs_inventory.md"
    },
    
    "artifacts": {
      "directory": ".codex/",
      "gitignore": true,
      "retention_days": 30
    }
  },
  
  "workflow_awareness": {
    "version": "1.0.0",
    "enabled": true,
    "total_workflows": 68,
    "pr_triggered_workflows": 34,
    
    "categories": {
      "pr_quality_gates": 8,
      "pr_enhancement": 4,
      "security_checks": 4,
      "scheduled_maintenance": 8,
      "manual_dispatch": 4,
      "orchestration": 2
    },
    
    "applicability_detection": {
      "analyze_changed_files": true,
      "detect_security_sensitive": true,
      "check_dependency_changes": true,
      "identify_visual_changes": true
    },
    
    "status_monitoring": {
      "use_mcp_tools": true,
      "check_blocking_workflows": true,
      "generate_reports": true
    }
  },
  
  "session_parameters": {
    "version": "1.0.0",
    "optimal_duration_minutes": 30,
    "max_duration_minutes": 60,
    "context_budget_tokens": 128000,
    
    "compliance_targets": {
      "memory_application_rate": 1.0,
      "corrections_per_issue": 1.0,
      "pre_commit_audit_rate": 1.0,
      "mcp_first_compliance": 1.0,
      "custom_agent_usage_rate": 1.0
    }
  }
}
```

---

## Agent Integration

### Custom Agent Template Updates

All custom agents must include policy awareness:

```markdown
## Policy Compliance

### Codebase Agency Policy
- ✅ Address ALL issues found (no "not my responsibility")
- ✅ Minimum 5 iteration attempts before escalation
- ✅ Fix pre-existing problems in work area
- ✅ Document root causes and solutions
- ✅ Generate follow-up prompts for continuity

### LFS Policy  
- ✅ Check file sizes before committing
- ✅ Use LFS for files >1MB
- ✅ Document LFS files in .codex/lfs_inventory.md
- ✅ Never commit build artifacts or node_modules

### Workflow Awareness
- ✅ Identify applicable workflows for PR
- ✅ Monitor blocking workflow status
- ✅ Address workflow failures comprehensively
- ✅ Use MCP tools for workflow data

### Session Optimization
- ✅ Create memory directive checklist
- ✅ Self-checkpoint every 10 actions
- ✅ Maintain <90% context utilization
- ✅ Invoke required custom agents
```

### Agent Activation with Policy Context

```python
def activate_agent_with_policy_context(
    agent_name: str,
    pr_number: int,
    task: str
) -> Dict:
    """Activate custom agent with full policy context."""
    
    # Load all policy parameters
    params = load_unified_parameters()
    
    # Analyze PR workflow applicability
    workflow_awareness = AgentWorkflowAwareness(pr_number)
    applicable_workflows = workflow_awareness.applicable_workflows
    blocking_workflows = workflow_awareness.get_blocking_workflows()
    
    # Create policy-aware context
    context = {
        "agent_name": agent_name,
        "pr_number": pr_number,
        "task": task,
        
        "policies": {
            "codebase_agency": params["codebase_agency_policy"],
            "lfs": params["lfs_policy"],
            "session": params["session_parameters"],
        },
        
        "workflows": {
            "applicable": applicable_workflows,
            "blocking": blocking_workflows,
            "must_pass_before_merge": [
                w for w in blocking_workflows
                if w["required"] and w["blocking"]
            ],
        },
        
        "mandatory_actions": [
            "Create plan with markdown checklist",
            "Invoke code_review before finalizing",
            "Invoke codeql_checker before merge",
            "Address ALL issues found",
            "Check file sizes for LFS compliance",
            "Monitor applicable workflow status",
            "Generate follow-up prompt",
        ],
    }
    
    return context
```

---

## Enforcement Mechanisms

### Pre-Commit Hooks

```python
# .git/hooks/pre-commit
#!/usr/bin/env python3
"""Pre-commit hook enforcing all policies."""

import sys
from pathlib import Path

# Import policy enforcers
from codex.policies import (
    CodebaseAgencyEnforcer,
    LFSPolicyEnforcer,
    WorkflowAwarenessChecker,
)

def main():
    """Run all policy checks."""
    
    # Get staged files
    import subprocess
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True
    )
    staged_files = result.stdout.strip().split("\n")
    
    violations = []
    
    # Check 1: LFS Policy
    lfs_enforcer = LFSPolicyEnforcer()
    for file in staged_files:
        if Path(file).exists():
            size = Path(file).stat().st_size
            valid, reason = lfs_enforcer.check_file(file, size)
            if not valid:
                violations.append(f"LFS: {file} - {reason}")
    
    # Check 2: Codebase Agency Policy
    agency_enforcer = CodebaseAgencyEnforcer()
    # ... check for prohibited statements in commit message
    
    # Report violations
    if violations:
        print("❌ Pre-commit policy violations:")
        for v in violations:
            print(f"  - {v}")
        print("\nCommit blocked. Fix violations and try again.")
        return 1
    
    print("✅ All policy checks passed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### GitHub Actions Integration

```yaml
# .github/workflows/policy-enforcement.yml
name: Policy Enforcement

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  enforce-policies:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Check Codebase Agency Policy
        run: |
          python scripts/policies/check_agency_policy.py \
            --pr-number ${{ github.event.pull_request.number }}
      
      - name: Check LFS Policy
        run: |
          python scripts/policies/check_lfs_policy.py \
            --changed-files "$(git diff --name-only origin/main)"
      
      - name: Check Workflow Awareness
        run: |
          python scripts/policies/check_workflow_awareness.py \
            --pr-number ${{ github.event.pull_request.number }} \
            --report-applicable-workflows
      
      - name: Generate Policy Report
        if: always()
        run: |
          python scripts/policies/generate_policy_report.py \
            --pr-number ${{ github.event.pull_request.number }} \
            --output .codex/policy-report.md
      
      - name: Comment Policy Report
        if: always()
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('.codex/policy-report.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: report
            });
```

---

## References

**Policy Documents**:
- [Codebase Agency Policy](../../.codex/CODEBASE_AGENCY_POLICY.md)
- [LFS Policy](../../docs/guides/lfs_policy.md)
- [Accountability Report](../../.codex/ACCOUNTABILITY_REPORT_2026_02_16.md)

**Related Documentation**:
- [Long Session Parameters](./LONG_SESSION_PARAMETERS_AND_PROTOCOLS.md)
- [Enhanced Agent Design](./ENHANCED_AGENT_COGNITIVE_DESIGN.md)
- [MCP Workflow Recipes](./MCP_WORKFLOW_RECIPES.md)

**Implementation Files**:
- Session Parameters: `.codex/session_parameters.json`
- Unified Parameters: `.codex/unified_parameters.json`
- LFS Inventory: `.codex/lfs_inventory.md`

---

**Status**: ✅ PRODUCTION SPECIFICATION  
**Version**: 2.0.0  
**Last Updated**: 2026-02-17T12:00:00Z  
**Integration**: Complete with all agent documentation
