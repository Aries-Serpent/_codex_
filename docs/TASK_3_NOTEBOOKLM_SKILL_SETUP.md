# Task 3: Configure Agentic Troubleshooting Skill
# NotebookLM Claude Code Integration Guide

**Objective**: Enable direct AI-to-AI research of `_codex_` via Claude Code  
**Tool**: `notebooklm-skill` for Claude Code  
**Integration Level**: Deep (AI Architect queries)

---

## Prerequisites

- **Claude Code**: Claude Desktop App or Claude VS Code Extension
- **Python**: 3.9+ installed and in PATH
- **Google Account**: With NotebookLM access
- **NotebookLM Notebook**: Created with _codex_ source (from Task 2)

---

## Installation Steps

### Step 1: Clone notebooklm-skill Repository

```bash
# Create skills directory for Claude Code
mkdir -p ~/.claude/skills

# Clone the notebooklm-skill repository
git clone https://github.com/PleasePrompto/notebooklm-skill ~/.claude/skills/notebooklm

# Navigate to skill directory
cd ~/.claude/skills/notebooklm

# Verify clone successful
ls -la
```

**Expected Output**:
```
drwxr-xr-x  scripts/
drwxr-xr-x  src/
-rw-r--r--  README.md
-rw-r--r--  requirements.txt
-rw-r--r--  setup.py
```

### Step 2: Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt

# Verify installation
python -c "import notebooklm_skill; print('✅ Installation successful')"
```

### Step 3: Google Authentication Setup

```bash
# Run authentication manager
python scripts/run.py auth_manager.py setup

# This will:
# 1. Open browser for Google OAuth
# 2. Ask you to select Google account
# 3. Request permissions for Drive access
# 4. Save credentials securely
```

**Interactive Prompts**:
```
> Google Authentication Required
> Opening browser for OAuth flow...
> Please select your Google account and grant permissions
> 
> Permissions requested:
> - Read access to Google Drive files
> - Access to NotebookLM notebooks
> 
> After completing authentication in browser, return here...
```

**Verification**:
```bash
# Verify authentication successful
python scripts/run.py auth_manager.py verify
```

**Expected Output**:
```
✅ Authentication successful
✅ Drive API access: ENABLED
✅ NotebookLM access: ENABLED
✅ Credentials saved to: ~/.claude/skills/notebooklm/credentials.json
```

### Step 4: Add _codex_ Notebook to Skill

**Prerequisites**: 
- NotebookLM notebook created (from Task 2)
- Notebook URL available

**Commands**:
```bash
# Add notebook with descriptive name
python scripts/run.py notebook_manager.py add \
  --url "https://notebooklm.google.com/notebook/[YOUR_NOTEBOOK_ID]" \
  --name "codex_architecture" \
  --description "Codex Architecture Knowledge Base - AI-powered development platform"

# Verify notebook added
python scripts/run.py notebook_manager.py list
```

**Expected Output**:
```
📚 Registered Notebooks:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name: codex_architecture
Description: Codex Architecture Knowledge Base - AI-powered development platform
Notebook ID: [YOUR_NOTEBOOK_ID]
Sources: 1 (codex-architecture-sync.xml)
Status: ✅ Active
Last Updated: 2026-01-13T17:30:00Z
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Test Query**:
```bash
# Test basic query functionality
python scripts/run.py notebook_manager.py query \
  --notebook "codex_architecture" \
  --question "What is the architecture of the auto-remediation system?"
```

**Expected Response** (truncated):
```
🤖 Query: What is the architecture of the auto-remediation system?

📝 Response:
The auto-remediation system in _codex_ follows a multi-stage pipeline:

1. **Detection Phase**: 
   - ML Threat Detector identifies vulnerabilities
   - Pattern matching against known vulnerability database
   
2. **Analysis Phase**:
   - Context-aware code analysis
   - AST parsing for surgical edits
   
3. **Fix Generation Phase** (tools/auto_remediation/fix_generator.py):
   - Strategy selection based on vulnerability type
   - Code replacement with precision checks
   
4. **Verification Phase** (tools/auto_remediation/verifier.py):
   - Pre-fix snapshot capture
   - Fix application and validation
   - Regression detection
   
5. **PR Creation Phase** (tools/auto_remediation/pr_generator.py):
   - Branch creation
   - Commit and push
   - PR generation with review assignment

Key Components:
- fix_generator.py: Generates fixes using AST
- verifier.py: Validates fixes before/after
- pr_generator.py: Automates PR workflow
```

### Step 5: Configure Smart Context Loading

```bash
# Enable automatic context loading for relevant queries
python scripts/run.py config.py set --auto-context true

# Set context window size (max tokens for context)
python scripts/run.py config.py set --context-window 128000

# Enable caching for faster subsequent queries
python scripts/run.py config.py set --enable-cache true

# Set cache TTL (time to live) in seconds
python scripts/run.py config.py set --cache-ttl 3600

# Configure query timeout
python scripts/run.py config.py set --query-timeout 30

# View all configuration
python scripts/run.py config.py show
```

**Expected Configuration Output**:
```
🔧 NotebookLM Skill Configuration:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
auto_context: true
context_window: 128000
enable_cache: true
cache_ttl: 3600
query_timeout: 30
default_notebook: codex_architecture
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Claude Code Integration

### Step 6: Test in Claude Code

**In Claude Code (VS Code Extension or Desktop App)**:

**Test Query 1: Basic Architecture**
```
@architect What are the main modules in _codex_ and their purposes?
```

**Expected Behavior**:
- Skill activates automatically on `@architect` mention
- Queries NotebookLM notebook "codex_architecture"
- Returns structured architectural overview
- Provides code references with file paths
- Suggests related components to explore

**Test Query 2: Deep Dive**
```
@architect Explain the auto-remediation pipeline in detail, including all files involved
```

**Expected Response Structure**:
1. Pipeline overview
2. File-by-file breakdown
3. Data flow diagrams (if applicable)
4. Key functions and their roles
5. Integration points

**Test Query 3: Security Analysis**
```
@architect What security measures are implemented in the MSP Gateway?
```

**Test Query 4: Troubleshooting**
```
@architect How does the CI diagnostic agent determine root causes of failures?
```

**Test Query 5: Dependency Mapping**
```
@architect Show me the dependency structure of the monitoring module
```

### Step 7: Create Custom Commands

**File**: `~/.claude/skills/notebooklm/custom_commands.json`

```json
{
  "commands": [
    {
      "name": "health_check",
      "trigger": "@architect health check",
      "prompt": "Perform a comprehensive health check of the _codex_ repository architecture. Analyze: 1) Module dependencies, 2) Security posture, 3) Code quality metrics, 4) Test coverage, 5) Technical debt. Provide a structured report with scores (0-100) for each category.",
      "notebook": "codex_architecture",
      "followup_questions": [
        "Are there any circular dependencies?",
        "What are the highest-risk security areas?",
        "Which modules need refactoring most urgently?"
      ]
    },
    {
      "name": "dependency_analysis",
      "trigger": "@architect analyze dependencies",
      "prompt": "Generate a dependency graph for the _codex_ repository. Identify: 1) Circular dependencies, 2) Tightly coupled modules, 3) God classes (>500 LOC, >10 dependencies), 4) Unused dependencies. Output as Mermaid diagram.",
      "notebook": "codex_architecture",
      "output_format": "mermaid"
    },
    {
      "name": "security_audit",
      "trigger": "@architect security audit",
      "prompt": "Conduct a security audit of _codex_. Check for: 1) Unvalidated inputs, 2) Injection vulnerabilities (SQL, XSS, command), 3) Weak cryptography, 4) Authentication issues, 5) Secrets in code. Prioritize findings by severity (Critical, High, Medium, Low).",
      "notebook": "codex_architecture",
      "severity_levels": true
    },
    {
      "name": "refactoring_suggestions",
      "trigger": "@architect suggest refactoring for {module}",
      "prompt": "Analyze the {module} module in _codex_ and suggest refactoring improvements. Consider: 1) Code complexity (cyclomatic), 2) Duplication, 3) Performance bottlenecks, 4) Maintainability. Provide specific code examples and before/after comparisons.",
      "notebook": "codex_architecture",
      "include_examples": true
    },
    {
      "name": "test_coverage",
      "trigger": "@architect check test coverage",
      "prompt": "Analyze test coverage for _codex_. Identify: 1) Untested code paths, 2) Missing edge cases, 3) Flaky tests (non-deterministic), 4) Test duplication. Suggest new test cases for critical paths with high business impact.",
      "notebook": "codex_architecture",
      "prioritize_critical": true
    },
    {
      "name": "performance_analysis",
      "trigger": "@architect analyze performance",
      "prompt": "Perform performance analysis of _codex_. Identify: 1) N+1 query patterns, 2) Inefficient algorithms (O(n²) or worse), 3) Missing caching opportunities, 4) Memory leaks. Provide optimization recommendations with estimated impact.",
      "notebook": "codex_architecture",
      "include_metrics": true
    },
    {
      "name": "integration_points",
      "trigger": "@architect show integration points",
      "prompt": "Map all integration points in _codex_. Include: 1) External APIs, 2) Database connections, 3) Message queues, 4) File systems, 5) Third-party services. Document authentication methods and error handling for each.",
      "notebook": "codex_architecture",
      "include_auth": true
    },
    {
      "name": "recursive_analysis",
      "trigger": "@architect deep dive {topic}",
      "prompt": "Perform recursive deep-dive analysis on {topic} in _codex_. Start with high-level overview, then progressively drill down into implementation details. After each level, ask yourself: 'Is that ALL you need to know?' Continue until all logic bottlenecks are resolved and you have complete understanding.",
      "notebook": "codex_architecture",
      "recursive": true,
      "max_depth": 5
    }
  ]
}
```

**Load Custom Commands**:
```bash
# Reload skill with custom commands
python scripts/run.py config.py reload

# Verify custom commands loaded
python scripts/run.py config.py list-commands
```

---

## Advanced Usage

### Recursive Analysis Protocol

For deep troubleshooting, use the recursive follow-up approach:

**Initial Query**:
```
@architect deep dive auto-remediation fix verification
```

**Follow-up Questions** (automatic):
1. "Is that ALL you need to know about the verification process?"
2. "What edge cases exist in fix validation?"
3. "How are regressions detected and prevented?"
4. "What happens if verification fails?"
5. "Are there any security implications in the verification logic?"

**Termination Condition**: When response indicates complete understanding with no remaining logic bottlenecks

### Multi-Step Research Loops

For complex queries, enable multi-step research:

```
@architect Investigate the root cause of CI failures in the determinism workflow. 
Use multi-step research to:
1. Analyze workflow configuration
2. Check for non-deterministic code patterns
3. Review historical failure logs
4. Identify common failure modes
5. Suggest comprehensive fixes

After each step, ask: "Is that ALL you need to know?" and continue until bottlenecks resolved.
```

---

## Troubleshooting

### Issue: Authentication Fails

**Symptoms**: "Authentication failed" or "Invalid credentials"

**Solutions**:
```bash
# Clear existing credentials
rm ~/.claude/skills/notebooklm/credentials.json

# Re-run authentication
python scripts/run.py auth_manager.py setup

# Check browser for popup blockers
# Ensure cookies enabled for accounts.google.com
```

### Issue: Notebook Not Found

**Symptoms**: "Notebook ID not found" or "Access denied"

**Solutions**:
```bash
# Verify notebook URL is correct
# Format: https://notebooklm.google.com/notebook/[NOTEBOOK_ID]

# Check notebook sharing settings
# Ensure authenticated Google account has access

# Re-add notebook
python scripts/run.py notebook_manager.py remove codex_architecture
python scripts/run.py notebook_manager.py add --url [CORRECT_URL] --name codex_architecture
```

### Issue: Queries Timeout

**Symptoms**: "Query timeout exceeded" or "No response"

**Solutions**:
```bash
# Increase timeout
python scripts/run.py config.py set --query-timeout 60

# Check NotebookLM API status
# https://status.notebooklm.google.com

# Reduce query complexity or split into smaller queries
```

### Issue: Skill Not Recognized in Claude Code

**Symptoms**: `@architect` doesn't trigger skill

**Solutions**:
```bash
# Verify skill directory structure
ls -la ~/.claude/skills/notebooklm/

# Check Claude Code skill settings
# Settings → Extensions → Claude Skills → Refresh

# Restart Claude Code application
```

---

## Validation Checklist

- [ ] notebooklm-skill cloned to `~/.claude/skills/notebooklm/`
- [ ] Dependencies installed successfully
- [ ] Google authentication completed
- [ ] Credentials saved and verified
- [ ] _codex_ notebook registered as "codex_architecture"
- [ ] Test query returns accurate results
- [ ] Smart context loading configured
- [ ] Cache enabled for performance
- [ ] Custom commands loaded
- [ ] `@architect` trigger works in Claude Code
- [ ] Multi-step research functional
- [ ] Recursive analysis operational

---

## Next Steps

After successful installation:

1. **Test All Custom Commands**: Verify each command works as expected
2. **Perform Health Check**: `@architect health check` to establish baseline
3. **Document Findings**: Record initial architectural insights
4. **Integrate with Workflow**: Use architect during code reviews and refactoring
5. **Train Team**: Share custom commands and best practices with team

---

## Support & Resources

- **notebooklm-skill GitHub**: https://github.com/PleasePrompto/notebooklm-skill
- **Claude Code Docs**: https://docs.anthropic.com/claude/docs
- **NotebookLM Help**: https://support.google.com/notebooklm
- **_codex_ Documentation**: See `PHASE_10_MASTER_INTEGRATION_PLANSET.md`

---

**Task Status**: READY FOR EXECUTION  
**Prerequisites**: Task 1 & 2 must be complete  
**Estimated Time**: 2 hours  
**Cognitive Brain Impact**: Self-Healing +3, Knowledge Synthesis +5
