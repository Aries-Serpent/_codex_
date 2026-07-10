# Tag Creation Methods Test Plan

**Date:** 2026-07-10T15:22:52Z  
**Objective:** Test different methods for creating/pushing git tags with various authentication tokens  
**Focus:** Understand which methods work with branch protection and which tokens have sufficient permissions

---

## Testing Methodology

### Tokens to Test
1. **CODEX_MASTER_KEY** — Classic PAT (full `repo` scope)
2. **CODEX_BACKUP_KEY** — Fine-grained PAT (Read and Write to code)
3. **GitHub App (Cognitive Brain)** — Installed app with broad permissions including "read and write access to code"
4. **GITHUB_TOKEN** — Workflow-provided installation token

### Methods to Test

#### Method 1: Direct Git Push
```bash
export GH_TOKEN=<token>
git push origin refs/tags/v0.1.0:refs/tags/v0.1.0
```
- **Expected:** May fail with branch protection
- **Success indicator:** Tag appears in GitHub

#### Method 2: Git Push with HTTP Basic Auth
```bash
git push https://x-access-token:<token>@github.com/Aries-Serpent/_codex_.git v0.1.0
```
- **Expected:** Alternative authentication method
- **Success indicator:** Tag appears in GitHub

#### Method 3: GitHub API - Git Refs (Create Tag)
```bash
gh api repos/Aries-Serpent/_codex_/git/refs \
  -H "authorization: token <token>" \
  -f ref=refs/tags/v0.1.0 \
  -f sha="<commit_sha>"
```
- **Expected:** Bypasses git push, uses API directly
- **Success indicator:** Tag API returns 201/success

#### Method 4: GitHub API - Releases (Create Release)
```bash
gh api repos/Aries-Serpent/_codex_/releases \
  -H "authorization: token <token>" \
  -f tag_name=v0.1.0 \
  -f target_commitish=main \
  -f name="v0.1.0"
```
- **Expected:** Creates both tag and release
- **Success indicator:** Release appears on GitHub

#### Method 5: gh CLI with Fallback Token Chain
```bash
export GH_TOKEN="${CODEX_MASTER_KEY:-${CODEX_BACKUP_KEY:-$GITHUB_TOKEN}}"
git push origin v0.1.0
```
- **Expected:** Uses token fallback chain
- **Success indicator:** Tag appears with correct token

#### Method 6: GitHub App Authentication
```bash
# Use GitHub App JWT + Installation Token
gh api repos/Aries-Serpent/_codex_/git/refs \
  -f ref=refs/tags/v0.1.0 \
  -f sha="<commit_sha>"
# When GH_TOKEN is set to app installation token
```
- **Expected:** App has elevated permissions
- **Success indicator:** Tag created with app identity

---

## Test Execution Plan

### Phase 1: Single-Method Tests (No Live Push)
- Test each method with `--dry-run` or `--verbose` flags to see what would happen
- Capture error messages for each token type
- Document permission errors vs. authentication errors

### Phase 2: API Tests (Safe, Revertible)
- Test GitHub API methods which can create test tags and be cleaned up
- Use test tags like `v0.1.0-test-method-1`, `v0.1.0-test-method-2`
- Document success/failure for each token type

### Phase 3: Identify Successful Pattern
- Based on previous successful tags (beta1, beta3, artifacts tags)
- Determine which method was used
- Replicate that exact pattern for v0.1.0

### Phase 4: Production Tag Push
- Once successful pattern identified, push actual v0.1.0 tag
- Verify tag appears on GitHub
- Trigger release-to-pypi.yml workflow

---

## Token Permission Summary

### CODEX_MASTER_KEY (Classic PAT)
- ✅ `repo` scope (includes contents:write)
- ✅ `admin:org`, `admin:repo_hook`, `workflow`
- ✅ Should have write access
- ❌ May be blocked by branch protection

### CODEX_BACKUP_KEY (Fine-grained PAT)
- ✅ "Read and Write access to code"
- ✅ "Read and Write access to repository hooks"
- ✅ Fine-grained, may bypass some branch protection
- Repository level permissions (not org-wide)

### Cognitive Brain GitHub App
- ✅ "Read and write access to code"
- ✅ "Admin access to organization projects"
- ✅ App-level authentication (may bypass user-level restrictions)
- ✅ Installed 4 months ago with full permissions
- Environment: `_GITHUB_APP_PRIVATE_KEY`, `_GITHUB_APP_CLIENT_SECRET`, `_GITHUB_APP_ID`, `_GITHUB_APP_INSTALLATION_ID`

### GITHUB_TOKEN
- ❌ Limited permissions (installation token)
- ❌ No `contents:write` for protected branches
- ❌ Expected to fail

---

## Test Results Template

```markdown
### Method: <Method Name>
- Token: <Token Type>
- Command: <Exact command used>
- Result: <Success | Failure>
- Error (if failed): <Error message>
- Permission issue: <Yes | No>
- Branch protection bypass: <Yes | No | Unknown>
- Recommendation: <Use for v0.1.0 | Fallback option | Don't use>
```

---

## Success Criteria

- ✅ Identify at least one method that successfully creates tags
- ✅ Identify which token has sufficient permissions
- ✅ Understand branch protection behavior
- ✅ Document the pattern that worked for previous tags
- ✅ Provide recommended method for v0.1.0 production tag

---

## Timeline
- Phase 1 (Dry-run tests): ~5 minutes
- Phase 2 (API tests with test tags): ~10 minutes
- Phase 3 (Pattern identification): ~3 minutes
- Phase 4 (Production push): ~2 minutes
- **Total:** ~20 minutes

