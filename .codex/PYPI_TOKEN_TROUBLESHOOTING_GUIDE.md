# 🆘 PYPI_TOKEN AUTHENTICATION TROUBLESHOOTING GUIDE

**Last Updated**: 2026-07-10T16:52:22Z  
**Status**: Active - For Run #321 and subsequent PyPI releases  
**Purpose**: Click-by-click resolution steps for PYPI_TOKEN authentication failures

---

---

## 🗺️ PyPI.org Site Navigation Guide

### Overview of PyPI.org Structure

**PyPI Home**: https://pypi.org/

**Key Navigation Areas**:
```
PyPI.org (top bar)
├─ Search box (center top)
├─ Top-right buttons (when NOT logged in):
│  ├─ Log in
│  └─ Sign up
├─ Top-right (when logged in):
│  ├─ Your username
│  ├─ Account settings
│  └─ Log out
└─ Footer links (bottom)
```

---

### For This Task: Account Settings Flow

**Step-by-step site navigation**:

1. **Start**: Go to https://pypi.org/
2. **Top-right corner**: Click your username or profile icon
3. **Dropdown menu appears** showing:
   - Your username
   - Your email
   - **"Account settings"** ← Click here
   - "Help & feedback"
   - "Log out"
4. **You're now on**: https://pypi.org/account/
5. **Left sidebar** shows account sections:
   - Account information
   - Email address
   - Password
   - Two-factor authentication (2FA)
   - Publishing
   - **API tokens** ← This is what you need
6. **Main content area** displays your chosen section

---

### Full PyPI Site Map for Reference

```
pypi.org/
├─ / (home page)
│  ├─ Browse projects (search)
│  └─ [Log in] [Sign up] (top right)
├─ /project/[project-name]/ (specific project page)
│  ├─ Project description
│  ├─ Release history
│  ├─ Files download
│  └─ Statistics
├─ /account/ (logged-in users only)
│  ├─ Account section
│  ├─ Email section
│  ├─ Password section
│  ├─ Two-factor authentication
│  ├─ Publishing
│  └─ API tokens ← Token management here
├─ /account/organizations/ (org management)
│  └─ Manage team members
├─ /help/ (documentation)
│  ├─ FAQ
│  ├─ Using PyPI
│  └─ API documentation
└─ /pypi-api/ (API reference)
   └─ JSON API endpoints
```

---

| Error | Cause | Solution |
|-------|-------|----------|
| `401 Unauthorized` | Token missing or invalid secret name | Verify secret exists with correct name `PYPI_TOKEN` |
| `403 Forbidden` | Token expired or insufficient permissions | Regenerate token from PyPI account |
| `twine HTTPError 403` | Wrong PyPI credentials format | Verify `TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}` |
| `No package found` | Upload succeeded but metadata wrong | Check `pyproject.toml` version matches git tag |

### STEP 0️⃣: Initial Login to PyPI.org (If Not Already Logged In)

**Browser Click Path**:
1. Open: **https://pypi.org/**
2. **Page loads** showing PyPI home
3. **Look at top-right corner**:
   - If you see a **username**: You're logged in ✅ (skip to STEP 1)
   - If you see **"Log in"** link: You're NOT logged in (continue below)

4. Click: **"Log in"** link (top-right)
5. **Login page appears** at: https://pypi.org/account/login/
6. **Enter credentials**:
   - Email/username field: Enter your PyPI account email
   - Password field: Enter your PyPI password
7. **Optional - Two-Factor Authentication**:
   - If your account has 2FA enabled: Enter the 6-digit code from your authenticator app
8. Click: **"Sign in"** button (blue)
9. ✅ **Successfully logged in** - Redirects to account dashboard

**What you should see after login**:
```
PyPI Account Dashboard
├─ Welcome message: "Welcome, [Your Name]"
├─ Your account summary
├─ Recent upload activity (if any)
└─ Quick links to settings
```

---



### STEP 1️⃣: Verify PYPI_TOKEN Secret Exists in Repository

**Browser Click Path**: 
1. Navigate to: **https://github.com/Aries-Serpent/_codex_/settings/secrets/actions**
2. Look for secret name: **`PYPI_TOKEN`** in the list
3. **Expected Result**: Secret appears in "Repository secrets" section (value hidden)
4. **If Missing**: Go to STEP 2
5. **If Present**: Go to STEP 3

**What you should see:**
```
Repository secrets
  PYPI_TOKEN ● (value hidden)
  CODEX_MASTER_KEY ● (value hidden)
  ...
```

---

### STEP 2️⃣: Create PYPI_TOKEN Secret (If Missing)

**Browser Click Path**:
1. Go to: **https://github.com/Aries-Serpent/_codex_/settings/secrets/actions**
2. Click green button: **"New repository secret"**
3. Fill **"Name"** field: Type exactly `PYPI_TOKEN` (case-sensitive, no spaces)
4. Fill **"Secret"** field:
   - Open new tab: **https://pypi.org/account/**
   - Log in as package maintainer
   - Click: **"Account Settings"** in dropdown
   - Scroll to: **"API tokens"** section
   - Click: **"Create token"** or copy existing token
   - Copy token value (starts with `pypi-...`)
   - Paste into GitHub "Secret" field
5. Click: **"Add secret"** button
6. ✅ **Success**: Secret created, page refreshes

**Important**: 
- Token format: `pypi-AgEIcHlwaS5vcmcVf...` (long base64-like string)
- Token must start with `pypi-`
- Copy the ENTIRE token value

---

### STEP 3️⃣: Verify Workflow Uses Correct Secret Name

**Browser Click Path**:
1. Go to: **https://github.com/Aries-Serpent/_codex_/blob/v0.1.0/.github/workflows/release-to-pypi.yml**
2. Press **Ctrl+F** (Windows/Linux) or **Cmd+F** (Mac)
3. Search for: `PYPI_TOKEN`
4. Find line showing upload step, should read:
   ```yaml
   TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
   ```

**If you see instead**:
```yaml
TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}  # ❌ WRONG
```

**Then Fix Required**:
1. Click pencil icon (top right): **Edit file**
2. Find and replace: `PYPI_API_TOKEN` → `PYPI_TOKEN`
3. Scroll down: Add commit message: `fix: Use correct PYPI_TOKEN secret name`
4. Select: **"Commit directly to v0.1.0 branch"**
5. Click: **"Commit changes"**
6. Push tag again: `git push origin v0.1.0 --force` (triggers new run)

---

### STEP 4️⃣: Check Token Expiration and Permissions

**Browser Click Path**:
1. Go to: **https://pypi.org/account/**
2. Log in as package maintainer
3. Click: **"Account Settings"** (top right dropdown)
4. Scroll to: **"API tokens"** section
5. Verify:
   - ✅ Token status shows: **"Active"** (not "Revoked" or "Expired")
   - ✅ Token scope shows: **"All projects"** OR **"codex-ml"**
   - ✅ Creation date is recent (within last 90 days is safe)

**If Token Expired or Missing Permissions**:
- Proceed to STEP 5 to regenerate

---

### STEP 5️⃣: Regenerate Invalid or Expired Token

#### 5.A - Navigate to PyPI.org Account Settings

**Browser Click Path**:
1. Open new tab/window: **https://pypi.org/**
2. Look at top-right corner of page
3. If **NOT logged in**: 
   - Click: **"Log in"** link (top right)
   - Enter email/username and password
   - Click: **"Sign in"** button
4. Once logged in, top-right shows your username
5. Click on your username/profile icon (top right)
6. Click: **"Account settings"** from dropdown menu
   - **Expected URL**: `https://pypi.org/account/`

**What you should see on Account Settings page**:
```
PyPI Account Settings
├─ Account: [Your name/email]
├─ Email address
├─ Password
├─ Two-factor authentication
├─ Publishing
└─ API tokens  ← You are here
```

---

#### 5.B - Locate Existing Token to Revoke

**Still on Account Settings page**:
1. Scroll down to: **"API tokens"** section (near bottom)
2. You should see heading: **"API tokens"** with subtitle "View and manage your API tokens"
3. Below this, see list of existing tokens (if any)
4. Each token shows:
   - Token name (e.g., "GitHub Release", "CI/CD", etc.)
   - Last used date
   - Scope (e.g., "Entire account", "codex-ml project")
   - **"Revoke"** button (right side)

**Example Token List**:
```
API tokens
View and manage your API tokens

Token: "github-release-token"
  Last used: 2 months ago
  Scope: Entire account
  [Revoke] button

Token: "old-expired-token"
  Last used: Never
  Scope: Entire account
  [Revoke] button
```

---

#### 5.C - Revoke Old/Expired Token

**On API tokens section**:
1. Find the token you want to remove (usually oldest or "expired" one)
2. Click: **"Revoke"** button on the right side of that token
3. **Popup appears** asking: "Are you sure you want to revoke this token?"
4. Click: **"Revoke"** button in popup (red/danger button)
5. ✅ **Token revoked** - Page refreshes, token removed from list

---

#### 5.D - Create New API Token

**Still on Account Settings → API tokens section**:
1. Look for green button: **"Add API token"** (top of tokens list or bottom)
2. Click: **"Add API token"** button
3. **"Create API token" popup/form appears** with these fields:

   **Field 1 - Token name (required)**:
   - Type: `codex_github_release`
   - (Or any descriptive name like "GitHub Workflow", "Release Automation", etc.)
   
   **Field 2 - Scope (required)**:
   - Click dropdown: "Scope"
   - Select: **"Entire account"** (allows publishing to all projects)
   - OR: **"codex-ml"** (if you want to restrict to only this project)
   - ✅ Recommend: **"Entire account"** for broader access

4. Form should look like:
   ```
   Token name: [codex_github_release]
   
   Scope: [Entire account ▼]
   
   [Create token] button
   ```

5. Click: **"Create token"** button (blue)

---

#### 5.E - Copy Token Value (CRITICAL - APPEARS ONLY ONCE)

**Important dialog appears**:
1. **Dialog says**: "Copy this token. We can't show it to you again."
2. **Token value displayed**: Long string starting with `pypi-AgEIcHlwaS5vcmcVf...`
3. **Actions available**:
   - **"Copy to clipboard"** button (fast copy)
   - OR manually select all text and Ctrl+C

4. ⚠️ **CRITICAL**: 
   - Copy this token value IMMEDIATELY
   - You will NOT be able to see it again
   - Do NOT close this dialog without copying!

5. **Visual guide** - dialog looks like:
   ```
   ┌─────────────────────────────────────────┐
   │  API Token Created                      │
   │  Copy this token. We can't show it      │
   │  to you again.                          │
   │                                         │
   │  pypi-AgEIcHlwaS5vcmcVfN2ZXJhZ2...     │
   │                                         │
   │  [Copy to clipboard] [I've copied it]   │
   └─────────────────────────────────────────┘
   ```

6. Click: **"Copy to clipboard"** button (recommended)
7. Or click: **"I've copied it"** button after manual copy
8. Dialog closes

**Token copied!** ✅

---

#### 5.F - Verify Token in Your List

**Back on Account Settings → API tokens**:
1. Scroll to **"API tokens"** section
2. New token should appear in list:
   ```
   Token: "codex_github_release"
   Last used: Just now
   Scope: Entire account
   [Revoke] button
   ```
3. ✅ Token created and listed

---

#### 5.G - Update GitHub Secret with New Token

**Switch to GitHub**:
1. Go to: **https://github.com/Aries-Serpent/_codex_/settings/secrets/actions**
2. Locate: **`PYPI_TOKEN`** in the "Repository secrets" list
3. Click on: **`PYPI_TOKEN`** name (or the secret row)
4. **Edit view appears** with:
   - Name field: `PYPI_TOKEN` (read-only)
   - Secret field: (empty or masked value)
5. Click in the **"Secret"** field
6. Clear any existing value: **Ctrl+A** → **Delete**
7. Paste new token: **Ctrl+V** (paste the token you copied from PyPI)
8. Verify pasted value:
   - ✅ Starts with: `pypi-`
   - ✅ Ends with: random characters
   - ✅ Length: ~100+ characters
9. Click: **"Update secret"** button (green, bottom right)
10. ✅ **Secret updated** - Page shows confirmation

**Confirmation message** should appear:
```
Repository secret updated
PYPI_TOKEN has been updated
```

---

### STEP 6️⃣: Re-trigger Workflow Run with Fixed Token

**Browser Click Path**:
1. Go to: **https://github.com/Aries-Serpent/_codex_/actions/runs/29108822519** (or latest run)
2. Click dropdown menu: **⋯** (three dots, top right of run status)
3. Select: **"Re-run all jobs"**
4. Confirm: Click **"Re-run all jobs"** in popup
5. ✅ New run triggered

**Monitor the Run**:
1. Go to: **https://github.com/Aries-Serpent/_codex_/actions?query=workflow%3A%22Release+to+PyPI%22**
2. Locate latest run with your changes
3. Click on run to open details
4. Click on: **"upload-to-pypi"** job when it appears
5. Look for successful log line:
   - ✅ **Success**: `Uploading distributions to PyPI` followed by version number
   - ❌ **Failure**: `401 Unauthorized` or `403 Forbidden`

---

## 🔍 DIAGNOSTIC: Check Workflow Log Output

**Browser Click Path**:
1. Go to: **https://github.com/Aries-Serpent/_codex_/actions/runs/29108822519**
2. Click on job: **"upload-to-pypi"** (under "Jobs" section)
3. Expand step: **"Run twine upload"** (click to expand)
4. Look for one of these outputs:

**✅ SUCCESS Output**:
```
Uploading distributions to PyPI
Uploading codex_ml-0.1.0-py3-none-any.whl
Uploading codex-ml-0.1.0.tar.gz
100%
```

**❌ FAILURE Output**:
```
HTTPError: 401 Unauthorized
Upload failed with status code 401
```

**If Seeing 401/403**: 
- Go back to STEP 1 and verify PYPI_TOKEN exists
- Then STEP 5 to regenerate token
- Then STEP 6 to re-run

---

## ⚡ VERIFICATION CHECKLIST

Before considering the issue resolved, verify ALL:

- [ ] PYPI_TOKEN secret exists in GitHub repo settings
- [ ] Secret name is **exactly** `PYPI_TOKEN` (case-sensitive)
- [ ] Secret value starts with `pypi-`
- [ ] Workflow YAML uses `${{ secrets.PYPI_TOKEN }}`
- [ ] PyPI token status is **"Active"** (not expired)
- [ ] PyPI token scope includes **"All projects"** or **"codex-ml"**
- [ ] Workflow run completed with status **"completed"** and conclusion **"success"**
- [ ] PyPI upload job shows **"Uploading distributions to PyPI"** message
- [ ] Package appears on https://pypi.org/project/codex-ml/0.1.0/

---

## 🆘 If All Steps Fail - Advanced Diagnostics

### Check Repository Organization/Permissions
1. Go to: **https://github.com/Aries-Serpent/_codex_/settings/secrets/actions**
2. Verify you have **"Admin"** or **"Maintain"** permissions on this repository
3. If not: Contact @mbaetiong to grant appropriate permissions

### Test PyPI Credentials Manually
**Local Terminal** (if you have local repo):
```bash
# Install twine if needed
pip install twine

# Test upload (dry-run)
twine upload --repository testpypi dist/* -u __token__ -p pypi-your-token-here

# If successful, try real PyPI
twine upload dist/* -u __token__ -p pypi-your-token-here
```

### Check PyPI Server Status
- Visit: **https://status.pypi.org/**
- Verify all services show **"Operational"** (green status)
- If red status: PyPI may be under maintenance - wait and retry

---

## 📞 ESCALATION PATH

**If issue persists after all steps:**

1. **Verify organization membership**: Is your PyPI account in correct organization?
2. **Check package ownership**: Does your PyPI account own "codex-ml" package?
3. **Try different token**: Create new token with broader scope from scratch
4. **Contact PyPI Support**: https://pypi.org/help/ → "Report a problem"
5. **Escalate to @mbaetiong**: May need elevated PyPI account permissions

---

## 📝 COMMON MISTAKES TO AVOID

❌ **Wrong Secret Name**: `PYPI_API_TOKEN` instead of `PYPI_TOKEN`  
✅ **Fix**: Use exactly `PYPI_TOKEN`

❌ **Token Pasted Partially**: Missed first/last characters  
✅ **Fix**: Copy ENTIRE token value starting with `pypi-`

❌ **Old/Expired Token**: Using token older than 90 days  
✅ **Fix**: Regenerate fresh token from PyPI account

❌ **Workflow Not Updated**: Edited secret but workflow still references old name  
✅ **Fix**: Edit `.github/workflows/release-to-pypi.yml` to use correct secret name

❌ **Not Re-running After Fix**: Applied fix but didn't trigger new run  
✅ **Fix**: Click "Re-run all jobs" after secret update

---

**Questions?** Refer back to the step-by-step guide or escalate to @mbaetiong.
