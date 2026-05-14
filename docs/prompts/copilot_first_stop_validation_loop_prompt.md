# Copilot Prompt — First-Stop Validation Loop for CI Rescue

Use this prompt when CI or local validation exposes unrelated issues during a PR session and you need a repeatable stabilization loop.

```text
@copilot Continue the deterministic first-stop validation loop for this PR.

Operating contract:
1. Review actionable maintainer/bot comments first.
2. Use GitHub MCP to inspect the latest failing workflow runs and logs before changing files.
3. Run local validation in this order:
   - python3 -m ruff check
   - python3 -m pytest -x
4. Treat the first unrelated failure surfaced by pytest -x as actionable in this session.
5. Classify the blocker (code, test, docs/metrics, CI-policy, config, logging state, etc.).
6. Prefer existing repository utilities/fixers before manual edits.
7. Apply the smallest fix that restores the broken contract.
8. Run targeted regressions for the touched area immediately.
9. Update living docs for the PR (`PR####_whats_next.md` and `PR####_session_diagram.mmd`) with:
   - latest blocker
   - fix applied
   - current validation status
   - next immediate actions
10. Update `CHANGELOG.md` and `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` in the same rescue cycle.
11. Re-run:
    - python3 -m pytest -x
    and continue the loop until:
    - the suite passes, or
    - only clearly external/infrastructure-only blockers remain.
12. Before final commit, clean transient runtime artifacts so the PR stays scoped.
13. Leave ~5 minutes for wrap-up:
    - final required checks
    - comment replies with fixing commit hash
    - progress/reporting updates

Non-deferral rules:
- Do not dismiss unrelated deterministic failures as out of scope.
- Do not hand-wave CI issues without checking logs.
- Do not broaden fixes unnecessarily; use surgical repairs plus regression coverage.

Output expectations for each loop:
- blocker found
- root cause
- minimal fix
- targeted validation result
- next full-suite rerun status
```

## Suggested session checklist

- [ ] Triage CI logs with GitHub MCP
- [ ] Run `ruff`
- [ ] Run `pytest -x`
- [ ] Fix first deterministic blocker
- [ ] Run targeted regression tests
- [ ] Update living docs + changelog + accountability
- [ ] Continue `pytest -x` loop
- [ ] Clean transient artifacts
- [ ] Run final gates
- [ ] Reply to blocking comments
