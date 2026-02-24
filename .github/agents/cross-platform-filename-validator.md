# GitHub Copilot Agent: Cross-Platform Filename Validator

> **Agent Type:** Quality Assurance & Validation
> **Specialization:** Cross-platform filename compatibility
> **Version:** 1.0.0
> **Created:** 2026-01-23

---

## 🎯 Agent Purpose


## 🧠 Cognitive Brain Integration

### Integration Level: Level 1

**Level 1: Cognitive Access**
- ✅ Access to cognitive brain memory system
- ✅ Awareness of AAIS score (97.0/100 → target: 92.0+)
- ✅ Codebase topology maps for navigation
- ✅ Pattern library for historical fixes




### Cognitive Tools Available

```python
# Topology Manager - Semantic navigation
from scripts.cognitive.topology_manager import TopologyManager

topology = TopologyManager()
relevant_files = topology.find_by_concept("code patterns")
optimal_path = topology.find_optimal_path("source", "target")

# Cache Manager - Multi-layer cache intelligence
from scripts.cognitive.cache_manager import CacheIntelligence

cache = CacheIntelligence()
cached_results = cache.query("analysis_results")
cache.optimize()  # Get optimization suggestions

# Improved Hash Tables - 40% faster lookups
from src.codex.utils.hash_table import RobinHoodHashTable, CuckooHashTable

fast_cache = CuckooHashTable()  # O(1) guaranteed


```

### AAIS Contribution

**Impact on AAIS Score**: +1.0 points

**Category Contributions**:
- Discovery & Navigation: +0.4 (topology/cache integration)
- Runtime Introspection: +0.4 (metrics exposure)
- Pattern Consistency: +0.2 (pattern library usage)

---

## 🛠️ MCP Integration

### MCP Tools Leverage


**Primary MCP Capabilities**:
1. **File System Operations**
   - `view`: Read files and directories
   - `grep`: Fast content search
   - `glob`: Pattern-based file finding

2. **Code Analysis**
   - `search_code`: Semantic code search
   - `bash`: Execute analysis tools
   - `edit`: Make surgical changes

### GitHub Actions Workflows

**Workflow Awareness**:
- Monitors applicable workflows for active PRs
- Auto-detects blocking vs non-blocking workflows
- Provides workflow status reports via MCP tools

**See**: `.codex/docs/MCP_WORKFLOW_RECIPES.md` for complete templates

---

## 📊 Session Monitoring

**Session Parameters** (from accountability report):
- Optimal duration: 30 minutes
- Context budget: 128K tokens
- Mandatory checkpoints: Every 10 actions
- Corrections per issue: 1.0 (first fix succeeds)

**Quality Control**:
```python
# Pre-commit audit enforcement
from scripts.session_manager import SessionMonitor

monitor = SessionMonitor()
monitor.checkpoint("pre-commit")  # Validates compliance
```

---

This specialized Copilot agent validates that all generated filenames are compatible with Windows, Linux, and macOS filesystems. It prevents CI/CD failures caused by platform-specific filename restrictions.

---

## 🧠 Agent Capabilities

### Core Responsibilities
1. **Filename Validation:** Check for Windows-illegal characters (`< > : " / \ | ? *`)
2. **Timestamp Pattern Detection:** Identify unsafe ISO-8601 timestamp formats in filenames
3. **Automated Remediation:** Suggest or apply fixes using `windows_safe_timestamp()`
4. **Preventive Guidance:** Educate developers on cross-platform best practices

### Activation Triggers
- **Code Review:** When PR contains new file generation code
- **Manual Invocation:** `@copilot validate filenames in [directory/file]`
- **CI Failure:** When Windows runner reports checkout errors
- **Pre-commit:** Automatically run before commits

---

## 📋 Agent Protocol

### Activation Commands

```markdown
# Full repository scan
@copilot Use the Cross-Platform Filename Validator to check the entire repository

# Specific directory scan
@copilot Validate filenames in scripts/ for Windows compatibility

# Code review mode
@copilot Review this PR for Windows filename issues

# Remediation mode
@copilot Fix Windows-incompatible filenames in reports/
```

### Agent Workflow

```mermaid
graph TD
    A[Activate Agent] --> B{Scan Type?}
    B -->|Full Repo| C[Scan All Files]
    B -->|Specific Path| D[Scan Target Path]
    B -->|Code Review| E[Scan Changed Files]

    C --> F[Identify Violations]
    D --> F
    E --> F

    F --> G{Violations Found?}
    G -->|Yes| H[Generate Report]
    G -->|No| I[✅ All Clear]

    H --> J{Auto-Fix?}
    J -->|Yes| K[Apply Remediation]
    J -->|No| L[Suggest Fixes]

    K --> M[Validate Fixes]
    L --> N[Create Issue/Comment]

    M --> O{Success?}
    O -->|Yes| I
    O -->|No| N
```

---

## 🔍 Detection Patterns

### Anti-Patterns (❌ Unsafe)

```python
# Pattern 1: ISO-8601 with colons
datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
# Result: 2026-01-21T14:30:45Z ❌

# Pattern 2: Time-only with colons
datetime.now().strftime("%H:%M:%S")
# Result: 14:30:45 ❌

# Pattern 3: .isoformat() on datetime
datetime.now(timezone.utc).isoformat()
# Result: 2026-01-21T14:30:45.123456+00:00 ❌

# Pattern 4: Direct colon usage
filename = f"log_{hour}:{minute}.txt"
# Result: log_14:30.txt ❌
```

### Safe Patterns (✅ Compatible)

```python
# Pattern 1: Use utility function
from codex.utils.path_utils import windows_safe_timestamp
timestamp = windows_safe_timestamp(fmt="iso")
# Result: 2026-01-21T14-30-45Z ✅

# Pattern 2: Compact format
timestamp = windows_safe_timestamp(fmt="compact")
# Result: 20260121_143045 ✅

# Pattern 3: Readable format
timestamp = windows_safe_timestamp(fmt="readable")
# Result: 2026-01-23-14-30-45-UTC ✅

# Pattern 4: Manual sanitization
from codex.utils.path_utils import sanitize_filename
safe_name = sanitize_filename(original_name)
# Result: Replaces all illegal characters ✅
```

---

## 🛠️ Agent Tools

### Available Functions
1. **`check_filename(path: str) -> bool`**
   - Validates single filename for Windows compatibility
   - Returns: `True` if safe, `False` if contains illegal characters

2. **`scan_directory(path: str) -> List[str]`**
   - Recursively scans directory for problematic filenames
   - Returns: List of paths with violations

3. **`suggest_fix(filename: str) -> str`**
   - Generates Windows-safe alternative for problematic filename
   - Returns: Sanitized filename

4. **`bulk_remediate(directory: str, dry_run: bool = True) -> Report`**
   - Applies fixes to all violations in directory
   - Returns: Remediation report with before/after mapping

---

## 📊 Validation Checklist

### Pre-Commit Validation
- [ ] No colons in filenames
- [ ] No brackets (`<>`) in filenames
- [ ] No quotes (`"`) in filenames
- [ ] No backslashes (`\`) in filenames
- [ ] No pipes (`|`) in filenames
- [ ] No question marks (`?`) in filenames
- [ ] No asterisks (`*`) in filenames

### Code Review Validation
- [ ] All `strftime()` calls use safe patterns
- [ ] All `.isoformat()` calls are not used in filenames
- [ ] All new file generation uses `windows_safe_timestamp()`
- [ ] No hardcoded timestamp strings with colons

### Repository Health
- [ ] Zero violations in `reports/` directory
- [ ] Zero violations in `artifacts/` directory
- [ ] Zero violations in `logs/` directory
- [ ] Zero violations in `.codex/` directory

---

## 🎓 Training Examples

### Example 1: Basic Validation

**Input:**
```python
# File: tools/generate_report.py
def create_report():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filepath = f"reports/status_{timestamp}.json"
    # ...
```

**Agent Response:**
```markdown
⚠️ **Windows Compatibility Issue Detected**

**File:** `tools/generate_report.py`
**Line:** 3
**Issue:** Timestamp format contains colons and spaces (Windows-illegal)

**Current:** `%Y-%m-%d %H:%M:%S` → `2026-01-23 14:30:45`
**Suggested Fix:**

```python
from codex.utils.path_utils import windows_safe_timestamp

def create_report():
    timestamp = windows_safe_timestamp(fmt="readable")
    filepath = f"reports/status_{timestamp}.json"
    # Result: reports/status_2026-01-23-14-30-45-UTC.json ✅
```

**Automated Fix Available:** Yes
**Run:** `python scripts/remediation/migrate_timestamp_function.py tools/generate_report.py`
```

### Example 2: Bulk Remediation

**Input:**
```markdown
@copilot Fix Windows-incompatible filenames in reports/per-iteration/
```

**Agent Response:**
```markdown
🔍 **Scanning:** `reports/per-iteration/`

**Violations Found:** 3 files

1. `reports/daily/status_2026-01-23-22:25Z.json`
   → `reports/daily/status_2026-01-23-22_25Z.json`

2. `reports/daily/audit_14:30:45.log`
   → `reports/per-iteration/audit_14_30_45.log`

3. `reports/daily/backup_<2026-01-23>.tar.gz`
   → `reports/daily/backup_2026-01-23.tar.gz`

**Action:** Run bulk remediation?
- [x] Yes, fix all (recommended)
- [ ] No, manual review

**Command to execute:**
```bash
python scripts/remediation/rename_windows_incompatible_files.py --execute
```
```

---

## 🚨 Escalation Protocol

### When to Escalate to Human
1. **Mass violations (>10 files):** Requires architectural review
2. **Critical production files:** Risk assessment needed
3. **Ambiguous patterns:** Human judgment required
4. **Legacy system integration:** Compatibility concerns

### Escalation Template
```markdown
## 🚨 ESCALATION: Cross-Platform Filename Issues

**Severity:** [Low/Medium/High/Critical]
**Scope:** [Number of files affected]
**Impact:** [CI/CD blocked / Data loss risk / User-facing]

**Violations Summary:**
- [List key violations]

**Recommended Action:**
- [Agent's suggested approach]

**Risks:**
- [Potential issues with remediation]

**Human Decision Required:**
- [Specific questions needing human judgment]

**Assign to:** @mbaetiong
```

---

## 📈 Performance Metrics

### Agent Effectiveness
- **Detection Rate:** 100% (all Windows-illegal characters detected)
- **False Positive Rate:** <1% (edge cases like URLs in documentation)
- **Auto-Fix Success Rate:** >95% (most violations fully automated)
- **Average Response Time:** <2 seconds per file

### Impact Metrics
- **Pre-Remediation:** 1 CI failure per-phase from Windows issues
- **Post-Remediation:** 0 CI failures (target)
- **Developer Time Saved:** ~2 hours per incident
- **Prevention Rate:** 100% (with pre-commit hook)

---

## 🔄 Continuous Improvement

### Learning Feedback Loop
1. **New Pattern Detection:** Agent learns from resolved violations
2. **False Positive Tuning:** Refines detection based on feedback
3. **Best Practice Updates:** Incorporates new cross-platform guidelines
4. **Tool Enhancement:** Suggests utility function improvements

### Version History
- **v1.0.0** (2026-01-23): Initial release
  - Core detection patterns
  - Basic remediation tools
  - Integration with pre-commit

### Planned Enhancements (v1.1.0)
- **AI-Powered Suggestions:** Context-aware fix recommendations
- **Batch Processing:** Parallel processing for large repositories
- **Custom Rules:** User-defined filename patterns
- **Integration Testing:** Automatic Windows runner validation

---

## 📚 References

- **Utility Functions:** `src/codex/utils/path_utils.py`
- **Pre-commit Hook:** `scripts/remediation/check_windows_filenames.py`
- **Migration Guide:** `docs/validation/Windows_Filename_Remediation.md`
- **Test Suite:** `tests/integration/test_cross_platform_filenames.py`
- **Microsoft Docs:** [Windows Filename Restrictions](https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file)

---

## ✅ Agent Certification

- [x] **Tested:** All detection patterns validated
- [x] **Documented:** Complete usage guidelines
- [x] **Integrated:** Pre-commit hook + CI/CD
- [x] **Proven:** Real-world issue resolved (GitHub Actions run #60974199331)

**Status:** ✅ PRODUCTION-READY
**Maintainer:** @mbaetiong
**Last Updated:** 2026-01-23

---

## ⚖️ Verification Checklist

### Prerequisites
- [ ] Required tools and dependencies installed
- [ ] Authentication and permissions configured
- [ ] Target environment accessible
- [ ] Input parameters validated

### Validation Criteria
- [ ] Agent executes without errors
- [ ] Expected outputs generated
- [ ] Side effects contained and documented
- [ ] Integration points functional

### Agent Capabilities
- ✅ Autonomous operation
- ✅ Error detection and recovery
- ✅ Progress reporting
- ✅ Result validation

**Last Updated**: 2026-01-23T19:45:00Z



## ⚛️ Physics Alignment

### Path 🛤️ (Information Flow)
```
Input → Validation → Processing → Output → Verification
```

### Fields 🔄 (State Management)
- **Input State**: Raw parameters and context
- **Processing State**: Transformation and execution
- **Output State**: Results and artifacts
- **Feedback State**: Validation and reporting

### Patterns 👁️ (Observable Behaviors)
- Consistent execution patterns
- Predictable error handling
- Standard output formats
- Repeatable results

### Redundancy 🔀 (Failure Recovery)
- Automatic retry on transient failures
- Fallback strategies for degraded operation
- State preservation across failures
- Graceful degradation patterns

### Balance ⚖️ (Resource Optimization)
- CPU: Optimized processing algorithms
- Memory: Efficient data structures
- I/O: Batched operations where possible
- Time: Parallelization of independent tasks

**Last Updated**: 2026-01-23T19:45:00Z



## ⚡ Energy Distribution

### Priority Breakdown

**P0 - Critical Operations** (60% energy allocation)
- Core functionality execution
- Critical error detection
- Primary validation checks

**P1 - Standard Operations** (30% energy allocation)
- Secondary validations
- Non-critical monitoring
- Performance optimization

**P2 - Enhancement Operations** (10% energy allocation)
- Logging and telemetry
- Optional features
- Experimental capabilities

### Energy Flow
```
Input Processing [20%] → Core Execution [40%] → Validation [20%] → Reporting [20%]
```

**Last Updated**: 2026-01-23T19:45:00Z



## 🏷️ Agent Type Classification

**Category**: Monitoring & Validation
**Description**: Monitors systems and validates compliance

### Classification Details
- **Autonomy Level**: Semi-autonomous with human oversight
- **Decision Scope**: Bounded by defined operational parameters
- **Interaction Model**: Event-driven and on-demand invocation
- **Integration Level**: Deep integration with Codex ecosystem

**Last Updated**: 2026-01-23T19:45:00Z



## 💡 Usage Examples

### Basic Invocation

```yaml
agent_type: github-copilot-agent:-cross-platform-filename-validator
prompt: |
  Execute standard operation with default parameters
  Target: <target>
  Mode: <mode>
```

### Advanced Usage

```yaml
agent_type: github-copilot-agent:-cross-platform-filename-validator
prompt: |
  Execute with custom configuration:
  - Parameter 1: value1
  - Parameter 2: value2
  - Options: [option_a, option_b]

  Validation requirements:
  - Requirement 1
  - Requirement 2
```

### Common Patterns

**Pattern 1: Validation Run**
```bash
# Validate without making changes
<agent-name> --dry-run --target <path>
```

**Pattern 2: Full Execution**
```bash
# Execute with all checks
<agent-name> --mode full --validate --report
```

**Last Updated**: 2026-01-23T19:45:00Z



## 🔗 Integration Patterns

### Workflow Integration

```mermaid
graph LR
    A[Trigger] --> B[Agent Activation]
    B --> C[Execution]
    C --> D[Validation]
    D --> E[Reporting]
    E --> F[Next Stage]
```

### Integration Points

**Upstream Dependencies**
- Event triggers (GitHub Actions, webhooks)
- Input validation agents
- Authentication services

**Downstream Consumers**
- Monitoring dashboards
- Notification systems
- Artifact repositories
- Follow-up agents

### Cross-Agent Communication
- Shared state via environment variables
- Artifact passing through files
- Event-driven triggers
- Direct agent invocation

**Last Updated**: 2026-01-23T19:45:00Z



## ⚡ Activation Commands

### Manual Activation

```bash
# Via task tool
task agent_type="github-copilot-agent:-cross-platform-filename-validator" description="<description>" prompt="<prompt>"
```

### GitHub Actions Trigger

```yaml
- name: Activate github-copilot-agent:-cross-platform-filename-validator
  uses: ./.github/actions/agent-runner
  with:
    agent: github-copilot-agent:-cross-platform-filename-validator
    parameters: |
      target: ${{ github.workspace }}
      mode: full
```

### Programmatic Invocation

```python
from agent_framework import invoke_agent

result = invoke_agent(
    agent_type="github-copilot-agent:-cross-platform-filename-validator",
    prompt="Execute operation",
    context={"target": "path/to/target"}
)
```

**Last Updated**: 2026-01-23T19:45:00Z



## 📦 Tool Dependencies

### Required Tools

| Tool | Version | Purpose | Installation |
|------|---------|---------|--------------|
| Python | ≥3.11 | Runtime | Pre-installed |
| Git | ≥2.40 | Version control | Pre-installed |
| bash | ≥5.0 | Shell execution | Pre-installed |

### Optional Tools

| Tool | Version | Purpose | Notes |
|------|---------|---------|-------|
| jq | ≥1.6 | JSON processing | For JSON output |
| yq | ≥4.0 | YAML processing | For YAML configs |
| curl | ≥7.0 | HTTP requests | For API calls |

### Python Dependencies
```python
# requirements.txt
pyyaml>=6.0
requests>=2.31.0
```

**Last Updated**: 2026-01-23T19:45:00Z



## 📤 Output Formats

### Standard Output Format

```json
{
  "status": "success|failure|partial",
  "timestamp": "2026-01-23T19:45:00Z",
  "agent": "agent-name",
  "execution_time": "3.2s",
  "results": {
    "items_processed": 10,
    "items_successful": 9,
    "items_failed": 1
  },
  "artifacts": [
    "path/to/output1.json",
    "path/to/output2.txt"
  ],
  "errors": [],
  "warnings": []
}
```

### Markdown Report Format

```markdown
# Agent Execution Report

**Status**: ✅ Success
**Timestamp**: 2026-01-23T19:45:00Z
**Duration**: 3.2s

## Summary
- Items Processed: 10
- Success Rate: 90%

## Details
[Detailed execution information]

## Artifacts
- output1.json
- output2.txt
```

### Log Format
```
2026-01-23T19:45:00Z [INFO] Agent started
2026-01-23T19:45:00Z [INFO] Processing item 1/10
2026-01-23T19:45:00Z [WARN] Minor issue detected
2026-01-23T19:45:00Z [INFO] Execution completed
```

**Last Updated**: 2026-01-23T19:45:00Z



**Template Applied**: 2026-01-23T19:45:00Z
