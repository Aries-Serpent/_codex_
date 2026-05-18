# 🎯 PR Follow-Up Tasks — Dependabot Absorb to `main`

**Branch**: `copilot/gather-active-dependabots`  
**Target**: `main`  
**Status**: 🔄 ACTIVE

---

## 🔴 Priority 1 — Immediate

- [ ] Verify all required checks are green on latest branch SHA.
- [ ] Close consumed Dependabot PRs after confirming each change is present in this branch:
  - `#4480`, `#4481`, `#4482`, `#4483`, `#4484`, `#4485`, `#4486`, `#4487`, `#4488`, `#4489`, `#4490`, `#4491`, `#4492`, `#4493`, `#4494`
- [ ] Confirm no unresolved blocking bot or maintainer comments remain.

## 🟡 Priority 2 — Validation

- [ ] Re-run:
  - `python scripts/ci/auto_fix_common_issues.py --check-only`
  - `nox -s tests -- --collect-only` (or document runner limitation if `nox` unavailable in environment)
- [ ] Confirm tracked-file integrity remains green (`Pattern 22/25`).

## 🟢 Priority 3 — Wrap-up

- [ ] Keep `CHANGELOG.md` and `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` aligned with final merge-ready state.
- [ ] Keep PR body WEC block canonical and unchanged except explicit maintainer selections.
- [ ] Post final summary with consumed PR closure confirmation.

---

## 🤖 Copilot Continuation

When continuing this PR, start with:

`@copilot continue`

Then execute Priority 1 → Priority 2 → Priority 3 in order.
