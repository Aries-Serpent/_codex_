# PR #4434 — What's Next

> **PR:** [#4434](https://github.com/Aries-Serpent/_codex_/pull/4434)  
> **Session:** S987-S989 | **Date:** 2026-05-13 | **Branch:** `copilot/verify-codeql-alerts-and-sweep`  
> **Current head:** `HEAD` (S989 — workflow guide + Pattern 25/30 wrap)

---

## ✅ Completed (S987–S989)

| Area | Status |
|------|--------|
| 20 CodeQL quick-win fixes | ✅ 6 ineffectual-stmt + 14 unused-global/import |
| `scripts/ci/_gh_api.py` — rate-limit cache layer | ✅ TTL disk cache + retry/backoff |
| `scripts/ci/fetch_security_snapshot.py` — unified fetcher | ✅ all types + autofix + context |
| `fetch_codeql_alerts.py` dedup cleanup | ✅ delegates to `_gh_api.py` |
| `codeql-alert-fetcher.yml` — multi-stage pipeline | ✅ dropdown, cache, autofix, prompt |
| `wec_enforcer.py` — explicit pipeline input on dispatch | ✅ `_WORKFLOW_DEFAULT_INPUTS` |
| PR template WEC checkbox | ✅ `codeql-alert-fetcher.yml` added |
| `copilot-iterative-self-healing.yml` trigger | ✅ fetcher registered |
| `docs/reference/SECURITY_API_REFERENCE.md` | ✅ agent-readable API catalog |
| `docs/reference/CODEQL_FETCHER_WORKFLOW_GUIDE.md` | ✅ 7 Mermaid diagrams |

## ✅ Completed (S982–S986)

| Area | Status |
|------|--------|
| PR4434 living docs created | ✅ verify_living_files --strict passes |
| MFA SHA1→SHA256 hardening | ✅ new secrets default to HMAC-SHA256 |
| CodeQL top alert (peft_utils uninitialized var) | ✅ fixed |
| ujson Dependabot advisory #256 | ✅ uv.lock upgraded to 5.12.1 |
| Pattern 25/30 maintained | ✅ all sessions |

---

## 🔲 Remaining / Next Session

| Priority | Area | Notes |
|----------|------|-------|
| P1 | Run `codeql-alert-fetcher.yml` full pipeline | Verify WEC checkbox fires and artifact uploads correctly |
| P1 | Review Copilot Autofix suggestions in Security tab | Check which alerts got AI fixes after first autofix run |
| P2 | Next batch of CodeQL alerts from `alerts_fixable.md` | Continue systematic reduction |
| P2 | Dependabot alerts — remaining high/critical | Check `dependabot/alerts_critical.json` in latest snapshot |
| P3 | Create `fetch_security_snapshot.py` — `--types autofix` | Script already scaffolded; validate with real token |
| P3 | Add `template_lint.yml` to `session_wrapup_autofix.py` | Minor discrepancy between template and `_WEC_ITEMS` |

---

## CodeQL Alert Baseline (as of S985)

| Metric | Count |
|--------|-------|
| Total open on `main` | 119 |
| Fixed this PR branch | 20+ |
| Remaining fixable (estimate) | ~90 |



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
