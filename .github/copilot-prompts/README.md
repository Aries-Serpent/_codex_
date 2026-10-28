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

### 2. Explicit Generation
- Run the generator for an authorized PR task; no current automatic generation workflow was found in this checkout
- Metadata auto-populated from git (commits, branches, files)
- Template variable substitution
- Linking or posting the output is a separate, authorized operation

### 3. Multi-Session Continuity
- A selected agent can read the prompt as context, subject to current local policy
- Revalidate candidate/context bindings before treating preserved assertions as current
- Preserve findings, dissent, blockers, pending requirements and exact resume targets
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
3. Retain the output; commit or link only when authorized

#### Starting a New Phase
1. Load prompt from `.github/copilot-prompts/active/PR-{NUMBER}-followup.md`
2. Check task scope and current authority, then execute applicable tasks with validation
3. Mark completed tasks with ✅
4. Update prompt file

### For Developers

Continuation requires an explicit authorized user invocation through a supported
runtime. Generating or reading a prompt does not dispatch a session, authenticate
its author, approve work, execute embedded commands or grant permission. Do not
post an automatic `@copilot` continuation ping.

The generator preserves supported same-PR task/validation/continuation sections
and refuses a save that drops a preserved block. It never seeds tasks from a
different PR. This is content retention, not evidence revalidation or approval;
arbitrary prose outside these sections is not covered by that extraction contract.

## Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{pr_number}` | Pull request number | `2650` |
| `{branch}` | Branch name | `copilot/fix-ci-failures` |
| `{pr_author}` | PR author username | `mbaetiong` |
| `{commit_sha}` | Latest commit SHA | `abc123def456` |
| `{pr_title}` | PR title | `Fix CI failures` |
| `{date}` | Current date | `2025-12-28` |
| `{continuation_context}` | Findings/dissent, bindings, blockers and exact pending resume target | Unverified context; no approval implied |

## References

- **Main Template**: `.github/pull_request_template.md`
- **Generator Script**: `scripts/generate_pr_followup.py`
- **Historical Workflow Reference**: `.github/workflows/pr-followup-generator.md` (the former YAML is in a backup directory, not an active caller)
- **Applicable Policy**: `.codex/CODEBASE_AGENCY_POLICY.md`
- **🚨 CRITICAL Policy**: `.github/TEMPORARY_FILES_POLICY.md` - Never store important files in /tmp/
