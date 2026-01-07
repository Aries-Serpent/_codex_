# Copilot Follow-Up Prompt System

**Purpose**: Persistent, version-controlled storage for PR continuation prompts that maintain context across Copilot Agent sessions.

## Architecture

```
.github/copilot-prompts/
├── README.md                        # System documentation (this file)
├── templates/                       # Reusable prompt templates
│   ├── pr-continuation.md           # Standard PR follow-up
│   ├── ci-fix-continuation.md       # CI/CD fixes
│   ├── multi-phase-implementation.md # Multi-phase projects
│   └── consolidation.md             # Workflow consolidation
├── active/                          # Current PR prompts
│   └── PR-{number}-followup.md      # Active prompt files
└── archived/                        # Completed PR prompts
    └── PR-{number}-{date}.md        # Historical reference
```

## Core Concepts

### 1. Persistence Over Ephemeral Storage
- **ALL prompts stored in git** (never /tmp or temporary directories)
- Survives cache clearing, session restarts, and workflow failures
- Fully traceable through commit history
- Searchable across repository

### 2. Automated Generation
- Prompts auto-created on PR open via GitHub Actions
- Metadata auto-populated from git (commits, branches, files)
- Template variable substitution
- Linked automatically in PR descriptions

### 3. Multi-Session Continuity
- Copilot Agent reads persistent prompt on `@copilot continue`
- Updates prompt file with completed tasks (✅)
- Creates new continuation prompts for remaining work
- Enables iterative refinement across multiple sessions

## Usage

### For Copilot Agent

#### Wrapping Up a PR Session
1. Identify incomplete tasks
2. Generate continuation prompt:
   ```bash
   python3 scripts/generate_pr_followup.py {PR_NUMBER} \
     --immediate "Fix remaining CI failures" \
     --validation "Run full test suite"
   ```
3. Commit and link in PR

#### Starting a New Phase
1. Load prompt from `.github/copilot-prompts/active/PR-{NUMBER}-followup.md`
2. Execute Priority 1 tasks with validation
3. Mark completed tasks with ✅
4. Update prompt file

### For Developers

Comment `@copilot continue` on any PR to trigger continuation.

## Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{pr_number}` | Pull request number | `2650` |
| `{branch}` | Branch name | `copilot/fix-ci-failures` |
| `{pr_author}` | PR author username | `mbaetiong` |
| `{commit_sha}` | Latest commit SHA | `abc123def456` |
| `{pr_title}` | PR title | `Fix CI failures` |
| `{date}` | Current date | `2025-12-28` |

## References

- **Main Template**: `.github/pull_request_template.md`
- **Generator Script**: `scripts/generate_pr_followup.py`
- **Auto-Generation Workflow**: `.github/workflows/pr-followup-generator.yml`
- **🚨 CRITICAL Policy**: `.github/TEMPORARY_FILES_POLICY.md` - Never store important files in /tmp/
