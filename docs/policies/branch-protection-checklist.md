# Branch Protection Checklist (Archive & Hygiene)

This checklist aligns GitHub Branch Protection with our Archive & Hygiene workflow so that merges are gated on evidence, provenance, and governance.

> Apply to your default branch (usually `main`). Navigate: **Settings → Branches → Branch protection rules → Add rule**.

## 1) Branch name pattern
- **Branch name pattern**: `main` (or your default branch)

## 2) Protect matching branches
- [x] **Require a pull request before merging**
  - **Require approvals**: `1` (or more as needed)
  - [x] **Require review from Code Owners**
  - [x] **Dismiss stale pull request approvals when new commits are pushed**
  - [x] **Require conversation resolution before merging**
- [x] **Require status checks to pass before merging**
  - [x] **Require branches to be up to date before merging** (recommended)
  - **Status checks that are required** (match workflow job names):
    - `Lint commit messages (Conventional Commits)`
    - `Archive PR gates`
- [ ] **Require signed commits** (optional; enable if your org mandates it)
- [ ] **Require linear history** (optional; recommended for simpler audit trails)
- [ ] **Include administrators** (optional; recommended if you want policy enforced org-wide)

## 3) Push restrictions (optional)
- [ ] **Restrict who can push to matching branches** (leave off unless necessary)

## 4) Allowances
- Leave “Allow force pushes” **off** for protected branches.
- Leave “Allow deletions” **off** for protected branches.

## 5) Why these checks?
- **Commit messages**: The `commitlint` job enforces Conventional Commits for clearer CHANGELOGs and deprecation signals.
- **Archive PR gates**: Validates evidence log append-only updates and required fields, checks for provenance attestation references, nudges CHANGELOG updates, and runs the SBOM hook.

## 6) Verify check names
The required status checks must match the **job names** from the workflow:

```yaml
jobs:
  commitlint:
    name: Lint commit messages (Conventional Commits)
  gates:
    name: Archive PR gates
```

If you rename the jobs, update the branch protection required checks accordingly.

## 7) Related files
- Workflow: `.github/workflows/archive-gates.yml.disabled` (rename to `.yml` when policy allows activation)
- CODEOWNERS: `.github/CODEOWNERS`
- Policy: `docs/policies/archive-policy.md`
- PR template: `.github/pull_request_template.md`

## 8) Operational notes
- The SBOM step is **non-blocking** by default; set `STRICT_SBOM=1` in repo secrets or job env to make it fail on issues.
- Scheduled hygiene runs (`hygiene` job) do not block PRs; they support regular planner/summary/vacuum cycles.

## 9) Troubleshooting
- **Required check not appearing**: Trigger a PR to the protected branch so GitHub discovers the new workflow jobs, then refresh the branch protection rules to pick them.
- **Append-only failure on evidence**: Ensure only `+` lines modify `.codex/evidence/archive_ops.jsonl` in the PR diff, and that new JSON lines include `id`, `path`, `sha256`, `provenance`.

---

> Once configured, open a test PR that archives a small, unused doc using a tombstone stub and evidence entry. Confirm: CODEOWNERS request fires, commitlint passes, gates validate evidence/provenance, and CHANGELOG gets updated.
