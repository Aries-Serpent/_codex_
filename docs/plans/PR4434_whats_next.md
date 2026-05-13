# PR #4434 — What's Next

> **PR:** [#4434](https://github.com/Aries-Serpent/_codex_/pull/4434)  
> **Session:** S982 | **Date:** 2026-05-13 | **Branch:** `copilot/verify-codeql-alerts-and-sweep`  
> **Current head:** `HEAD` (S982 in progress)

---

## ✅ Completed (S981)

| Area | Status |
|------|--------|
| PDA metadata correction | ✅ S979 entry fixed from PR #4432 to PR #4434 |
| Session context truncation | ✅ full commit summary restored |
| Follow-up prompt contradiction | ✅ `Files Modified` list populated |
| Branch divergence | ✅ merged `main` commit `2696aa53` cleanly |

## ✅ Completed (S979–S980)

| Area | Status |
|------|--------|
| CodeQL verification on `main` | ✅ run `25774686922` passed after PR #4427 merge |
| `scripts/fix_broken_doc_links.py` shell-injection fix | ✅ `os.popen` → timezone-aware `datetime` |
| Pattern 25 recovery | ✅ `CHANGELOG.md` + accountability report updated |
| Follow-up prompt / sync-tracked recovery | ✅ `sync_tracked_files --fix` clean |

---

## 🟡 Current Session Focus (S982)

| Area | Goal |
|------|------|
| Living files | Create missing `docs/plans/PR4434_whats_next.md` and `docs/sessions/PR4434_session_diagram.md` so `verify_living_files.py --strict` passes |
| MFA security | Assess `src/codex/auth/mfa_provider.py` weak-crypto usage and harden TOTP defaults without breaking RFC 6238 compatibility |
| Traceability | Keep Pattern 25 / Pattern 30 green while continuing the CodeQL sweep |

---

## 📋 Next Priority 1

1. **Finish MFA hardening** — replace direct weak-hash usage in TOTP generation with validated algorithm selection and move new secret default to `SHA256`.
2. **Validate MFA flows** — run targeted tests for `tests/auth/test_mfa_provider.py`, `tests/auth/test_authenticator.py`, and `tests/api/test_auth_mfa_expiry.py`.
3. **Re-run living-file enforcement** — `python scripts/ci/verify_living_files.py --pr-number 4434 --strict`.

## 📋 Next Priority 2

4. **Refresh follow-up artifacts** — update `PR-4434-followup.md`, `CHANGELOG.md`, accountability report, and PDA entry with S982 outcomes.
5. **Run tracked-file hygiene** — `python scripts/ci/sync_tracked_files.py --fix`.
6. **Continue CodeQL sweep** — next likely buckets remain `py/weak-cryptographic-algorithm` and `py/undefined-export`.

## 📋 Next Priority 3

7. **Confirm PR checks are fully green** after the next push and review any new bot comments.
8. **Confirm CodeQL status on the PR** after the weak-crypto remediation lands.
