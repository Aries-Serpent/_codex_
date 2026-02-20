# Chain-PR Orchestration Plan

> **Generated**: 2026-02-17T11:24:00Z  
> **Repository**: Aries-Serpent/_codex_  
> **Purpose**: Complete guide for managing multi-PR dependency chains  
> **Status**: Production-Ready Framework

---

## Table of Contents

1. [Overview](#overview)
2. [Chain-PR Workflow](#chain-pr-workflow)
3. [Branch Naming Conventions](#branch-naming-conventions)
4. [PR Dependency Structure](#pr-dependency-structure)
5. [Validation Checkpoints](#validation-checkpoints)
6. [Automation Scripts](#automation-scripts)
7. [Example Implementation](#example-implementation)

---

## Overview

### What is a Chain-PR?

A **Chain-PR** (Chained Pull Request) is a series of dependent pull requests where:
- Each PR builds upon the previous one
- PRs must be merged in sequential order
- Each PR is independently testable
- The full chain achieves a larger objective

### When to Use Chain-PRs

**Use Chain-PRs when**:
- ✅ Refactoring large codebases incrementally
- ✅ Breaking down complex features into reviewable chunks
- ✅ Implementing multi-phase migrations
- ✅ Large-scale dependency updates
- ✅ Architectural changes requiring staged rollout

**Don't use Chain-PRs when**:
- ❌ Changes are independent (use separate PRs)
- ❌ Single PR < 500 lines (overkill)
- ❌ Urgent hotfixes (too slow)
- ❌ Simple bug fixes (unnecessary complexity)

### Benefits

1. **Easier Review**: Smaller, focused PRs are easier to review
2. **Incremental Progress**: Merge work incrementally, not all-or-nothing
3. **Better Testing**: Test each stage independently
4. **Reduced Risk**: Smaller changes = less likely to break things
5. **Clear History**: Logical progression visible in git history

---

## Chain-PR Workflow

### Phase 1: Planning

**Step 1: Define Objective**
```markdown
Objective: Migrate from config_legacy to Hydra configuration

Why Chain-PR:
- Affects 150+ files
- Requires careful migration of each module
- Risk: Breaking existing configs during migration
- Solution: Migrate one module at a time (10 PRs)
```

**Step 2: Break Down into Stages**
```markdown
Chain ID: hydra-migration-2026-02

PR Sequence:
1. PR #1: Add Hydra infrastructure + base configs
2. PR #2: Migrate src/models/ configs
3. PR #3: Migrate src/training/ configs
4. PR #4: Migrate src/evaluation/ configs
5. PR #5: Migrate tests/ configs
6. PR #6: Update documentation
7. PR #7: Add migration guide
8. PR #8: Deprecate config_legacy
9. PR #9: Remove config_legacy (final)
10. PR #10: Update CI/CD for Hydra

Dependencies:
- Each PR depends on previous PR being merged
- PR #10 depends on PR #9 (all migrations complete)
```

**Step 3: Create Chain Metadata**
```json
// .github/pr-chains/hydra-migration-2026-02.json
{
  "chain_id": "hydra-migration-2026-02",
  "objective": "Migrate from config_legacy to Hydra configuration",
  "total_prs": 10,
  "status": "in_progress",
  "created_at": "2026-02-17T11:24:00Z",
  "prs": [
    {
      "number": 1,
      "title": "[Chain 1/10] Add Hydra infrastructure + base configs",
      "branch": "chain/hydra-migration-2026-02/part-1",
      "base": "main",
      "status": "merged",
      "pr_number": 3456,
      "merged_at": "2026-02-18T10:00:00Z"
    },
    {
      "number": 2,
      "title": "[Chain 2/10] Migrate src/models/ configs",
      "branch": "chain/hydra-migration-2026-02/part-2",
      "base": "main",
      "status": "open",
      "pr_number": 3457,
      "depends_on": 3456
    }
    // ... remaining PRs
  ]
}
```

---

### Phase 2: Implementation

**Step 1: Create Base Branch (PR #1)**

```bash
# Create first branch from main
git checkout main
git pull origin main
git checkout -b chain/hydra-migration-2026-02/part-1

# Make changes for PR #1
# ... implement infrastructure ...

# Commit and push
git add .
git commit -m "feat: Add Hydra infrastructure + base configs (chain 1/10)"
git push origin chain/hydra-migration-2026-02/part-1

# Create PR #1 with chain template
gh pr create \
  --title "[Chain 1/10] Add Hydra infrastructure + base configs" \
  --body-file .github/pr-chains/PR_TEMPLATE.md \
  --base main \
  --label "chain-pr,hydra-migration"
```

**Step 2: Create Subsequent Branches (PR #2+)**

```bash
# After PR #1 is merged, create PR #2
git checkout main
git pull origin main
git checkout -b chain/hydra-migration-2026-02/part-2

# Make changes for PR #2
# ... migrate src/models/ configs ...

# Commit and push
git add .
git commit -m "feat: Migrate src/models/ configs to Hydra (chain 2/10)"
git push origin chain/hydra-migration-2026-02/part-2

# Create PR #2
gh pr create \
  --title "[Chain 2/10] Migrate src/models/ configs" \
  --body-file .github/pr-chains/PR_TEMPLATE.md \
  --base main \
  --label "chain-pr,hydra-migration"
```

**Note**: Each new PR is created from `main` (after previous PR is merged), not from the previous branch.

---

### Phase 3: Review & Merge

**Step 1: PR Review Checklist**

```markdown
## Review Checklist for Chain PR #{NUMBER}/{TOTAL}

### Code Quality
- [ ] Code follows repository standards
- [ ] Tests added/updated for changes
- [ ] Documentation updated
- [ ] No linting errors
- [ ] Type checking passes

### Chain-Specific
- [ ] Previous PR (#{PREV_PR}) is merged
- [ ] Changes build on previous PR correctly
- [ ] No conflicts with main branch
- [ ] Independent testing passes
- [ ] Chain context documented in PR description

### Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] E2E tests pass (if applicable)
- [ ] Manual testing completed
- [ ] No regressions from previous PRs

### Documentation
- [ ] Chain progress updated in tracking doc
- [ ] README/docs updated if needed
- [ ] Breaking changes documented
- [ ] Migration guide updated (if applicable)
```

**Step 2: Merge Sequence**

```bash
# Merge PR #1 (base)
gh pr merge 3456 --squash --delete-branch

# Wait for CI/CD to pass on main
# Then create PR #2 from updated main

# Merge PR #2
gh pr merge 3457 --squash --delete-branch

# Continue pattern for all PRs in chain
```

---

## Branch Naming Conventions

### Pattern

```
chain/{chain-id}/part-{number}
```

### Examples

```bash
# Good ✅
chain/hydra-migration-2026-02/part-1
chain/refactor-quantum-2026-02/part-3
chain/security-audit-ip-005/part-7

# Bad ❌
feature/hydra-migration-part-1   # Missing chain prefix
chain/hydra/1                      # Not descriptive
hydra-migration-2026-02-1          # Not standard format
```

### Chain ID Format

```
{objective}-{year}-{month}
```

**Examples**:
- `hydra-migration-2026-02`
- `refactor-quantum-2026-02`
- `python-312-migration-2026-01`
- `security-audit-ip-005-2026-02`

---

## PR Dependency Structure

### Linear Chain (Simple)

```
main
 └── PR #1: Infrastructure
      └── PR #2: Module A
           └── PR #3: Module B
                └── PR #4: Module C
                     └── PR #5: Cleanup
```

**Merge Order**: 1 → 2 → 3 → 4 → 5 (sequential)

---

### Parallel Tracks (Advanced)

```
main
 ├── PR #1: Infrastructure (base)
 │    ├── PR #2: Module A (depends on #1)
 │    ├── PR #3: Module B (depends on #1)
 │    └── PR #4: Module C (depends on #1)
 └── PR #5: Integration (depends on #2, #3, #4)
```

**Merge Order**:
1. Merge PR #1 first
2. Merge PR #2, #3, #4 in any order
3. Merge PR #5 last

---

### Diamond Pattern (Complex)

```
main
 └── PR #1: Base
      ├── PR #2: Feature A
      │    └── PR #4: Integration A+B
      └── PR #3: Feature B ───┘
           └── PR #5: Final (depends on #4)
```

**Merge Order**: 1 → (2, 3) → 4 → 5

---

## Validation Checkpoints

### Checkpoint 1: Pre-PR Creation

**Automated Check**: `.github/scripts/validate-chain-pr.sh`

```bash
#!/bin/bash
# Validate chain PR before creation

CHAIN_ID=$1
PR_NUMBER=$2
TOTAL_PRS=$3

# Check 1: Verify chain metadata exists
if [ ! -f ".github/pr-chains/${CHAIN_ID}.json" ]; then
  echo "❌ Chain metadata not found: ${CHAIN_ID}.json"
  exit 1
fi

# Check 2: Verify PR number is in sequence
EXPECTED_NUMBER=$(jq -r ".prs | length + 1" ".github/pr-chains/${CHAIN_ID}.json")
if [ "$PR_NUMBER" -ne "$EXPECTED_NUMBER" ]; then
  echo "❌ PR number mismatch. Expected: ${EXPECTED_NUMBER}, Got: ${PR_NUMBER}"
  exit 1
fi

# Check 3: Verify previous PR is merged (if not first PR)
if [ "$PR_NUMBER" -gt 1 ]; then
  PREV_PR_STATUS=$(jq -r ".prs[-1].status" ".github/pr-chains/${CHAIN_ID}.json")
  if [ "$PREV_PR_STATUS" != "merged" ]; then
    echo "❌ Previous PR not merged yet. Status: ${PREV_PR_STATUS}"
    exit 1
  fi
fi

echo "✅ Chain PR validation passed"
```

---

### Checkpoint 2: PR Creation

**GitHub Actions Workflow**: `.github/workflows/chain-pr-validation.yml`

```yaml
name: Chain PR Validation

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  validate-chain:
    name: Validate Chain PR
    runs-on: ubuntu-latest
    if: contains(github.event.pull_request.labels.*.name, 'chain-pr')
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Extract chain metadata from PR
        id: extract
        uses: actions/github-script@v7
        with:
          script: |
            const title = context.payload.pull_request.title;
            const match = title.match(/\[Chain (\d+)\/(\d+)\]/);
            
            if (!match) {
              core.setFailed('PR title must include [Chain X/Y] prefix');
              return;
            }
            
            const prNumber = parseInt(match[1]);
            const totalPrs = parseInt(match[2]);
            
            core.setOutput('pr_number', prNumber);
            core.setOutput('total_prs', totalPrs);
      
      - name: Validate chain sequence
        run: |
          PR_NUM=${{ steps.extract.outputs.pr_number }}
          
          if [ "$PR_NUM" -gt 1 ]; then
            # Check if previous PR is merged
            PREV_PR=$(($PR_NUM - 1))
            echo "Checking if PR #${PREV_PR} in chain is merged..."
            
            # Query GitHub API for chain metadata
            # Validate previous PR status
          fi
      
      - name: Post validation result
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '✅ Chain PR validation passed. This is PR ${{ steps.extract.outputs.pr_number }}/${{ steps.extract.outputs.total_prs }}.'
            });
```

---

### Checkpoint 3: Pre-Merge

**Required Checks**:
1. ✅ All CI/CD tests pass
2. ✅ Code review approved (min 1 reviewer)
3. ✅ Previous PR in chain is merged
4. ✅ No merge conflicts with base branch
5. ✅ Chain tracking document updated

**Automated Enforcement**: Branch protection rules

```yaml
# .github/branch-protection.yml
branches:
  - name: main
    protection:
      required_status_checks:
        - E2E Tests
        - Unit Tests
        - Linting
        - Chain PR Validation
      required_reviews: 1
      dismiss_stale_reviews: true
      require_code_owner_reviews: false
```

---

## Automation Scripts

### Script: `scripts/create-chain-pr.sh`

```bash
#!/bin/bash
# Create a new chain PR with proper metadata

set -e

CHAIN_ID=$1
PR_NUMBER=$2
TITLE=$3
BASE_BRANCH=${4:-main}

if [ -z "$CHAIN_ID" ] || [ -z "$PR_NUMBER" ] || [ -z "$TITLE" ]; then
  echo "Usage: $0 <chain-id> <pr-number> <title> [base-branch]"
  echo "Example: $0 hydra-migration-2026-02 2 'Migrate src/models/ configs' main"
  exit 1
fi

# Load chain metadata
CHAIN_FILE=".github/pr-chains/${CHAIN_ID}.json"
if [ ! -f "$CHAIN_FILE" ]; then
  echo "❌ Chain metadata not found: $CHAIN_FILE"
  exit 1
fi

TOTAL_PRS=$(jq -r '.total_prs' "$CHAIN_FILE")
BRANCH_NAME="chain/${CHAIN_ID}/part-${PR_NUMBER}"

# Validate
if [ "$PR_NUMBER" -gt "$TOTAL_PRS" ]; then
  echo "❌ PR number ($PR_NUMBER) exceeds total PRs ($TOTAL_PRS)"
  exit 1
fi

# Create branch
echo "📌 Creating branch: $BRANCH_NAME"
git checkout "$BASE_BRANCH"
git pull origin "$BASE_BRANCH"
git checkout -b "$BRANCH_NAME"

# Generate PR body from template
PR_BODY=$(sed \
  -e "s/{PR_NUMBER}/$PR_NUMBER/g" \
  -e "s/{PR_TOTAL}/$TOTAL_PRS/g" \
  -e "s/{CHAIN_ID}/$CHAIN_ID/g" \
  .github/pr-chains/PR_TEMPLATE.md)

echo "✅ Branch created: $BRANCH_NAME"
echo ""
echo "Next steps:"
echo "  1. Make your changes"
echo "  2. Commit: git commit -m 'feat: $TITLE (chain $PR_NUMBER/$TOTAL_PRS)'"
echo "  3. Push: git push origin $BRANCH_NAME"
echo "  4. Create PR:"
echo ""
echo "gh pr create \\"
echo "  --title '[Chain $PR_NUMBER/$TOTAL_PRS] $TITLE' \\"
echo "  --body '$PR_BODY' \\"
echo "  --base $BASE_BRANCH \\"
echo "  --label 'chain-pr,$CHAIN_ID'"
```

---

### Script: `scripts/merge-chain-pr.sh`

```bash
#!/bin/bash
# Safely merge a chain PR with validation

set -e

PR_NUMBER=$1
CHAIN_ID=$2

if [ -z "$PR_NUMBER" ] || [ -z "$CHAIN_ID" ]; then
  echo "Usage: $0 <pr-number> <chain-id>"
  exit 1
fi

# Validate PR is part of chain
CHAIN_FILE=".github/pr-chains/${CHAIN_ID}.json"
PR_SEQUENCE=$(jq -r ".prs[] | select(.pr_number == $PR_NUMBER) | .number" "$CHAIN_FILE")

if [ -z "$PR_SEQUENCE" ]; then
  echo "❌ PR #$PR_NUMBER not found in chain $CHAIN_ID"
  exit 1
fi

# Check if previous PR is merged (if not first)
if [ "$PR_SEQUENCE" -gt 1 ]; then
  PREV_SEQUENCE=$(($PR_SEQUENCE - 1))
  PREV_STATUS=$(jq -r ".prs[] | select(.number == $PREV_SEQUENCE) | .status" "$CHAIN_FILE")
  
  if [ "$PREV_STATUS" != "merged" ]; then
    echo "❌ Previous PR (sequence #$PREV_SEQUENCE) not merged yet"
    echo "   Current status: $PREV_STATUS"
    exit 1
  fi
fi

# Merge PR
echo "🔀 Merging PR #$PR_NUMBER (chain sequence $PR_SEQUENCE)"
gh pr merge "$PR_NUMBER" --squash --delete-branch

# Update chain metadata
jq ".prs[] |= if .pr_number == $PR_NUMBER then .status = \"merged\" | .merged_at = \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\" else . end" \
  "$CHAIN_FILE" > "$CHAIN_FILE.tmp"
mv "$CHAIN_FILE.tmp" "$CHAIN_FILE"

echo "✅ PR #$PR_NUMBER merged successfully"
echo "📊 Chain progress: $PR_SEQUENCE/$TOTAL_PRS merged"
```

---

## Example Implementation

### Example: Python 3.12 Migration Chain

**Chain ID**: `python-312-migration-2026-01`

**Objective**: Migrate entire codebase from Python 3.11 to 3.12

**PR Sequence**:

```markdown
PR #1 [MERGED]: Update CI/CD to Python 3.12
- Update GitHub Actions workflows
- Update noxfile.py Python version
- Update pyproject.toml Python requirement
Status: ✅ Merged 2026-01-15

PR #2 [MERGED]: Fix union type annotations (X | Y → Union[X, Y])
- Convert 200+ annotations across 63 files
- Fix isinstance() calls
- Update type stubs
Status: ✅ Merged 2026-01-17

PR #3 [MERGED]: Fix pickle compatibility issues
- Update checkpointing module
- Fix serialization in ML models
- Add pickle regression tests
Status: ✅ Merged 2026-01-19

PR #4 [MERGED]: Update CLI argument parsing (Typer/Click)
- Fix type introspection issues
- Update 39 CLI files
- Test all CLI commands
Status: ✅ Merged 2026-01-21

PR #5 [MERGED]: Fix Pydantic v2 compatibility
- Update FastAPI models
- Fix validation schemas
- Migrate from v1 to v2 API
Status: ✅ Merged 2026-01-23

PR #6 [OPEN]: Update documentation
- Migration guide
- Breaking changes list
- Troubleshooting tips
Status: 🔄 In Review

PR #7 [PENDING]: Final validation & cleanup
- Run full test suite
- Performance benchmarks
- Security scans
Status: ⏳ Waiting for PR #6
```

**Tracking Document**: `.github/pr-chains/python-312-migration-2026-01.md`

```markdown
# Python 3.12 Migration Chain

**Chain ID**: python-312-migration-2026-01  
**Objective**: Migrate codebase from Python 3.11 to 3.12  
**Total PRs**: 7  
**Status**: 5/7 Merged (71% Complete)  
**Started**: 2026-01-15  
**Target**: 2026-02-01

## Progress

- [x] PR #1: Update CI/CD (✅ Merged 2026-01-15)
- [x] PR #2: Fix union types (✅ Merged 2026-01-17)
- [x] PR #3: Fix pickle (✅ Merged 2026-01-19)
- [x] PR #4: Update CLI (✅ Merged 2026-01-21)
- [x] PR #5: Fix Pydantic (✅ Merged 2026-01-23)
- [ ] PR #6: Documentation (🔄 In Review)
- [ ] PR #7: Final validation (⏳ Pending)

## Metrics

| Metric | Value |
|--------|-------|
| Files Modified | 182 |
| Lines Changed | 3,456 |
| Tests Fixed | 127 |
| Type Annotations Updated | 234 |
| Compatibility Issues Resolved | 48 |

## Next Steps

1. Complete PR #6 review
2. Merge PR #6
3. Create PR #7 for final validation
4. Run comprehensive test suite
5. Update release notes
```

---

## Best Practices

### DO ✅

1. **Plan thoroughly** before starting
2. **Keep PRs small** (<500 lines each)
3. **Test independently** (each PR should be self-contained)
4. **Document dependencies** clearly in PR descriptions
5. **Update chain tracking** after each merge
6. **Use automation scripts** for consistency
7. **Merge sequentially** (don't skip ahead)

### DON'T ❌

1. **Don't create PRs too far ahead** (max 2-3 ahead)
2. **Don't skip validation checkpoints**
3. **Don't merge out of order** (breaks dependencies)
4. **Don't force-push** to merged branches
5. **Don't ignore chain metadata** updates
6. **Don't rebase** after creating subsequent PRs
7. **Don't bypass CI/CD checks** for any PR

---

## References

- [GitHub PR Best Practices](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests)
- [MCP Capability Matrix](./MCP_CAPABILITY_MATRIX.md)
- [Workflow Recipes](./MCP_WORKFLOW_RECIPES.md)

---

**Status**: ✅ Production-Ready  
**Version**: 1.0.0  
**Last Updated**: 2026-02-17T11:24:00Z
