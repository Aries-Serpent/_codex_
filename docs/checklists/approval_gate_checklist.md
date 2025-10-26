# Approval Gate — Reviewer Checklist

Use this checklist to review an Intent Validation & Plan of Action before any execution.

## 1) Intent Validation
- [ ] Primary goal is explicitly stated.
- [ ] Scope boundaries and constraints are named.
- [ ] Success criteria are concrete and measurable.
- [ ] Out-of-scope items are called out.

## 2) Plan of Action (Phased)
- [ ] Phases are clearly named with objectives.
- [ ] Each phase has concrete tasks and a decision gate.
- [ ] Dependencies or effort estimates are present.
- [ ] Deliverables per phase are listed.

## 3) Discipline & Safety
- [ ] Risks & mitigations table provided (with severity).
- [ ] Rollback/fallback steps are described.
- [ ] No GitHub Actions are created/enabled (local-only checks).
- [ ] Commands are deterministic (e.g., `-q`) and copy-pastable.
- [ ] If `pytest` is present, `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` guard is used.

## 4) Structural Integrity
- [ ] Fenced code blocks are valid; single outer fence used for patches/diffs.
- [ ] No mixed fence types (backticks vs tildes) within a block.
- [ ] Response follows the requested reply format sections.

## 5) Tool Use & Freshness
- [ ] Appropriate tools selected (e.g., browsing for volatile topics).
- [ ] Absolute dates accompany any relative time phrasing.
- [ ] Citations are load-bearing and not dumps; domains are diverse.

## 6) Final Review
- [ ] Links to relevant docs/ADR included.
- [ ] Path locations exist or are being added in the PR.
- [ ] Minimal, reviewable change set with clear blast radius.

> Tip: Pair this checklist with `docs/ops/local_gates.md` and the sample in `samples/assistant_message_summary.sample.json`.
