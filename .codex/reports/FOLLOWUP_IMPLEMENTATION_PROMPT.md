# Follow-up Implementation Prompt for GitHub Copilot Agent

> **Purpose**: Complete Phase 1 implementation of CI optimization based on PR #3248 analysis  
> **Generated**: 2026-02-15T11:00:00Z  
> **For**: Next GitHub Copilot Agent session  
> **Base Branch**: `0D_base_` (or `main` after PR #3248 merges)

---

## 🎯 Quick Start for Copilot Agent

**Activation Command**:
```
@copilot Implement Phase 1 of CI optimization following FOLLOWUP_IMPLEMENTATION_PROMPT.md.
Create all 5 components with tests. Reference: .codex/CI_OPTIMIZATION_PLANSETS.md
```

**Context Files**:
- `.codex/CI_OPTIMIZATION_PLANSETS.md` (39KB) - Complete implementation specs
- `.codex/CI_FAILURE_PATTERN_ANALYSIS.md` (11KB) - Problem context
- `.codex/WORKFLOW_ARCHITECTURE_REVIEW.md` (28KB) - Workflow structure

**Expected Duration**: 30-45 minutes continuous execution  
**Token Budget**: ~150-200K tokens (15-20% of 1M budget)

---

## 📋 Phase 1 Implementation Checklist

### Component 1: PR Size Analyzer Workflow ✅

**File**: `.github/workflows/pr-size-analyzer.yml`

**Requirements**:
```yaml
name: PR Size Analyzer
on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  analyze-size:
    runs-on: ubuntu-latest
    outputs:
      pr_size: ${{ steps.analyze.outputs.pr_size }}
      changed_files_count: ${{ steps.analyze.outputs.changed_files_count }}
      validation_strategy: ${{ steps.analyze.outputs.validation_strategy }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Analyze PR Size
        id: analyze
        run: |
          # Count changed files
          CHANGED_FILES=$(git diff --name-only ${{ github.event.pull_request.base.sha }} ${{ github.sha }} | wc -l)
          echo "changed_files_count=$CHANGED_FILES" >> $GITHUB_OUTPUT
          
          # Determine size tier
          if [ $CHANGED_FILES -lt 20 ]; then
            echo "pr_size=small" >> $GITHUB_OUTPUT
            echo "validation_strategy=full_validation" >> $GITHUB_OUTPUT
          elif [ $CHANGED_FILES -lt 100 ]; then
            echo "pr_size=medium" >> $GITHUB_OUTPUT
            echo "validation_strategy=targeted_tests" >> $GITHUB_OUTPUT
          elif [ $CHANGED_FILES -lt 500 ]; then
            echo "pr_size=large" >> $GITHUB_OUTPUT
            echo "validation_strategy=smoke_tests" >> $GITHUB_OUTPUT
          else
            echo "pr_size=refactor" >> $GITHUB_OUTPUT
            echo "validation_strategy=import_validation" >> $GITHUB_OUTPUT
          fi
      
      - name: Report Size
        run: |
          echo "PR Size: ${{ steps.analyze.outputs.pr_size }}"
          echo "Changed Files: ${{ steps.analyze.outputs.changed_files_count }}"
          echo "Strategy: ${{ steps.analyze.outputs.validation_strategy }}"
```

**Validation**: Test with sample PRs of different sizes (10, 50, 200, 1000 files)

---

### Component 2: Telemetry Collection Script ✅

**File**: `scripts/ci/collect_telemetry.py`

**Requirements**:
```python
#!/usr/bin/env python3
"""
CI Telemetry Collection Script

Collects workflow runs, jobs, and artifacts from GitHub Actions.
Maps failures to 5 identified patterns for automated analysis.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import requests


class TelemetryCollector:
    """Collects and analyzes CI telemetry data."""
    
    # Pattern keywords for automatic classification
    PATTERN_KEYWORDS = {
        "auto-fix": ["auto-fix", "detect-and-fix", "detect ci issues"],
        "test-infrastructure": ["resilient", "validation-suite", "test-runner"],
        "coverage-timeout": ["coverage", "pytest-cov", "coverage report"],
        "filesystem-deadlock": ["root-org", "file-validation", "directory"],
        "pre-merge-cascade": ["pre-merge", "final-checks", "merge validation"]
    }
    
    def __init__(self, owner: str, repo: str, token: str):
        self.owner = owner
        self.repo = repo
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json"
        }
    
    def collect_workflow_runs(self, branch: str, days: int = 7) -> List[Dict]:
        """Collect workflow runs from specified branch."""
        since = (datetime.utcnow() - timedelta(days=days)).isoformat()
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/actions/runs"
        params = {
            "branch": branch,
            "per_page": 100,
            "created": f">={since}"
        }
        
        runs = []
        page = 1
        while True:
            params["page"] = page
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            runs.extend(data["workflow_runs"])
            
            if len(data["workflow_runs"]) < 100:
                break
            page += 1
        
        return runs
    
    def collect_job_details(self, run_id: int) -> List[Dict]:
        """Collect job details for a workflow run."""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/actions/runs/{run_id}/jobs"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()["jobs"]
    
    def collect_artifacts(self, run_id: int) -> List[Dict]:
        """Collect artifacts for a workflow run."""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/actions/runs/{run_id}/artifacts"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()["artifacts"]
    
    def classify_failure(self, run: Dict, jobs: List[Dict]) -> Optional[str]:
        """Classify failure into one of 5 patterns."""
        run_name = run["name"].lower()
        job_names = " ".join([j["name"].lower() for j in jobs])
        
        for pattern, keywords in self.PATTERN_KEYWORDS.items():
            for keyword in keywords:
                if keyword in run_name or keyword in job_names:
                    return pattern
        
        return "unknown"
    
    def generate_report(self, branch: str, days: int = 7, output: str = "telemetry_report.json"):
        """Generate comprehensive telemetry report."""
        print(f"Collecting workflow runs from {branch} (last {days} days)...")
        runs = self.collect_workflow_runs(branch, days)
        
        # Filter to failed runs
        failed_runs = [r for r in runs if r["conclusion"] in ["failure", "cancelled", "timed_out"]]
        print(f"Found {len(failed_runs)} failed runs out of {len(runs)} total")
        
        telemetry_data = {
            "generated_at": datetime.utcnow().isoformat(),
            "repository": f"{self.owner}/{self.repo}",
            "branch": branch,
            "days_analyzed": days,
            "summary": {
                "total_runs": len(runs),
                "failed_runs": len(failed_runs),
                "failure_rate": len(failed_runs) / len(runs) if runs else 0
            },
            "pattern_distribution": {},
            "failed_runs": []
        }
        
        # Collect details for each failed run
        for run in failed_runs:
            print(f"  Processing run {run['id']}: {run['name']}")
            
            jobs = self.collect_job_details(run["id"])
            artifacts = self.collect_artifacts(run["id"])
            pattern = self.classify_failure(run, jobs)
            
            # Update pattern distribution
            telemetry_data["pattern_distribution"][pattern] = \
                telemetry_data["pattern_distribution"].get(pattern, 0) + 1
            
            telemetry_data["failed_runs"].append({
                "run_id": run["id"],
                "run_name": run["name"],
                "run_html_url": run["html_url"],
                "conclusion": run["conclusion"],
                "created_at": run["created_at"],
                "pattern": pattern,
                "jobs": [{
                    "job_id": j["id"],
                    "job_name": j["name"],
                    "job_html_url": j["html_url"],
                    "status": j["status"],
                    "conclusion": j["conclusion"]
                } for j in jobs],
                "artifacts": [{
                    "artifact_id": a["id"],
                    "artifact_name": a["name"],
                    "size_bytes": a["size_in_bytes"],
                    "expired": a["expired"]
                } for a in artifacts]
            })
        
        # Write report
        with open(output, "w") as f:
            json.dump(telemetry_data, f, indent=2)
        
        print(f"\nTelemetry report written to {output}")
        print("\nPattern Distribution:")
        for pattern, count in telemetry_data["pattern_distribution"].items():
            percentage = (count / len(failed_runs)) * 100 if failed_runs else 0
            print(f"  {pattern}: {count} ({percentage:.1f}%)")
        
        return telemetry_data


def main():
    parser = argparse.ArgumentParser(description="Collect CI telemetry data")
    parser.add_argument("--owner", required=True, help="Repository owner")
    parser.add_argument("--repo", required=True, help="Repository name")
    parser.add_argument("--branch", default="main", help="Branch to analyze")
    parser.add_argument("--days", type=int, default=7, help="Days to analyze")
    parser.add_argument("--output", default="telemetry_report.json", help="Output file")
    parser.add_argument("--token", help="GitHub token (or use GITHUB_TOKEN env var)")
    
    args = parser.parse_args()
    
    token = args.token or os.getenv("GITHUB_TOKEN") or os.getenv("CODEX_MASTER_KEY")
    if not token:
        print("Error: GitHub token required (--token or GITHUB_TOKEN/CODEX_MASTER_KEY env var)")
        sys.exit(1)
    
    collector = TelemetryCollector(args.owner, args.repo, token)
    collector.generate_report(args.branch, args.days, args.output)


if __name__ == "__main__":
    main()
```

**Dependencies**: Add to `requirements.txt`: `requests>=2.31.0`

**Validation**: Test with `python scripts/ci/collect_telemetry.py --owner Aries-Serpent --repo _codex_ --branch 0D_base_ --days 7`

---

### Component 3: Auto-Fix with Rollback ✅

**File**: `scripts/ci/auto_fix_with_rollback.py`

**Requirements**: See Planset 1 in CI_OPTIMIZATION_PLANSETS.md for complete specification.

**Key Features**:
- Pre-flight validation (git state, permissions)
- Per-fix isolation with rollback context manager
- Retry logic with exponential backoff
- Comprehensive logging

---

### Component 4: Coverage Timeout Guards ✅

**File**: `.github/workflows/coverage-with-timeout.yml`

**Requirements**: See Planset 3 in CI_OPTIMIZATION_PLANSETS.md for complete specification.

**Key Features**:
- pytest-timeout plugin integration (7 min per test)
- Per-shard isolation
- Partial coverage reporting on timeout
- Graceful degradation

---

### Component 5: Validation Test Suite ✅

**Files**:
- `tests/ci/test_pr_size_analyzer.py`
- `tests/ci/test_telemetry_collection.py`
- `tests/ci/test_auto_fix_rollback.py`

**Requirements**:
- Test edge cases (boundary conditions)
- Mock GitHub API calls
- Validate pattern mapping accuracy
- Test rollback mechanisms

---

## 🔧 Implementation Guidelines

### 1. Execution Strategy

**Follow 60-Second Urgency Rule**:
- Start execution within 60 seconds
- No planning delays
- Continuous progress reporting

**Incremental Commits**:
- Commit after each component completion
- Include validation results in commits
- Report progress every 10-15 minutes

### 2. Testing Requirements

**For Each Component**:
- Create focused unit tests
- Test edge cases and error conditions
- Mock external dependencies (GitHub API)
- Validate against known failure patterns

**Test Coverage Target**: 80%+ for new code

### 3. Validation Checklist

Before marking complete:
- [ ] All 5 components created and committed
- [ ] All tests passing (pytest validation)
- [ ] Documentation updated with usage examples
- [ ] Integration tested with existing workflows
- [ ] Code review tool run successfully

### 4. Documentation Requirements

**Update These Files**:
- `README.md` - Add usage examples for new scripts
- `.codex/CI_OPTIMIZATION_PLANSETS.md` - Mark Phase 1 as IMPLEMENTED
- Create `docs/ci/IMPLEMENTATION_LOG.md` - Track what was implemented

---

## 📊 Success Criteria

### Component Completion

| Component | Files Created | Tests Added | Status |
|-----------|---------------|-------------|--------|
| PR Size Analyzer | 1 workflow | 3+ tests | ⏳ |
| Telemetry Collection | 1 script | 5+ tests | ⏳ |
| Auto-Fix Rollback | 1 script | 5+ tests | ⏳ |
| Coverage Timeout | 1 workflow | 3+ tests | ⏳ |
| Validation Suite | 3 test files | N/A | ⏳ |

### Quality Metrics

- **Code Quality**: All linting passes (ruff, mypy)
- **Test Coverage**: 80%+ for new code
- **Documentation**: Usage examples for all scripts
- **Integration**: Works with existing CI workflows

### Expected Impact

After Phase 1 implementation:
- Auto-fix success rate: 0% → 90%+
- Coverage collection: Timeout → 95%+ success
- PR size detection: 100% accuracy
- Telemetry automation: Manual 15min → automated 2min

---

## 🚀 Follow-up Phases

### Phase 2 - Core Improvements (After Phase 1)

1. Test layer architecture (Smoke → Unit → Integration → Slow)
2. Progressive validation integration (use PR size analyzer)
3. Workflow consolidation (implement telemetry-based triggers)
4. Monitoring dashboard (visualize telemetry data)

### Phase 3 - Advanced Optimizations (After Phase 2)

1. Async file operations (100x performance)
2. Incremental coverage (95% time savings)
3. Conditional workflow triggers (50% resource reduction)
4. Pattern detection alerting (real-time monitoring)

### Phase 4 - Monitoring & Continuous Improvement (After Phase 3)

1. Dashboard deployment
2. Retrospective documentation
3. Performance metrics tracking
4. Optimization recommendations

---

## 📝 Session Notes for Copilot Agent

### Context Loading

**Read These First** (in order):
1. `.codex/CI_FAILURE_PATTERN_ANALYSIS.md` - Understand the problems
2. `.codex/CI_OPTIMIZATION_PLANSETS.md` - Get implementation specs
3. This file (`FOLLOWUP_IMPLEMENTATION_PROMPT.md`) - Execution plan

### Best Practices

**Policy Compliance**:
- Follow Emotion-Safe Urgency Guardrails (60s execution)
- Use DevOps terminology (phases, not weeks)
- Apply Codebase Agency Policy (complete, don't defer)

**Technical Execution**:
- Use existing repository patterns for consistency
- Follow Python style guide (Black, Ruff, isort)
- Add comprehensive docstrings
- Include type hints

**Progress Reporting**:
- Commit after each component
- Update progress in commit messages
- Report blockers immediately
- Store learnings in permanent memory

### Common Pitfalls to Avoid

❌ **DON'T**:
- Plan endlessly without executing
- Create documentation instead of code
- Claim completion without validation
- Skip testing "to save time"

✅ **DO**:
- Start coding within 60 seconds
- Test each component before moving on
- Commit frequently with proof
- Validate everything works

---

## 🎯 Expected Outcomes

### Immediate (This PR)

**Deliverables**:
- 2 GitHub Actions workflows
- 2 Python scripts (with CLI interfaces)
- 3 test modules (with 15+ tests total)
- Updated documentation

**Value**:
- Functional CI improvements
- Proven optimization patterns
- Foundation for Phase 2-4

### Medium-term (Phase 2-3)

**Impact**:
- 50% resource reduction
- 67% faster feedback for large PRs
- 90%+ fix success rate
- Automated pattern detection

### Long-term (Phase 4+)

**Transformation**:
- Self-optimizing CI system
- Real-time monitoring and alerts
- Continuous improvement loop
- Proven framework for scale

---

## ✅ Ready to Execute

**This prompt provides everything needed for Phase 1 implementation:**
- Complete specifications (Planset documents)
- Code templates and examples
- Testing requirements
- Success criteria
- Policy compliance guidelines

**Estimated Timeline**:
- Phase 1: 30-45 minutes (this session)
- Phase 2: 45-60 minutes (next session)
- Phase 3: 45-60 minutes (future session)
- Phase 4: 30 minutes (final session)

**Total**: ~3 hours for complete CI optimization implementation

---

**Status**: Ready for Copilot Agent execution  
**Reference**: PR #3248 analysis and plansets  
**Next**: Create PR with Phase 1 implementation  
**Success**: All 5 components working with tests passing
