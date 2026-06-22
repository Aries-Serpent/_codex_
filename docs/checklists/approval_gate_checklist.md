# Intent Validation Approval Gate Checklist

**Last Updated:** 2026-06-22

Use this checklist to review an Intent Validation & Plan of Action before any execution work begins.

## 1) Scope & Objectives
- [ ] Problem framing is explicit, including in-scope and out-of-scope items.
- [ ] Success metrics and definitions of done are documented.
- [ ] Stakeholders and approvers are named.

## 2) Evidence & References
- [ ] Rubric and documentation links are present (rubric overview, ops doc, examples, negative sample, tests).
- [ ] Prior incidents, DRIs, and decision records are cited.
- [ ] External dependencies or upstream blockers are listed.

## 3) Risk Assessment
- [ ] Critical failure modes enumerated with mitigations.
- [ ] Data handling / privacy concerns addressed.
- [ ] Rollback or fallback plan documented.

## 4) Plan of Action
- [ ] Milestones, owners, and timelines outlined.
- [ ] Tooling / automation requirements captured.
- [ ] Response follows the requested reply format sections.

## 5) Tool Use & Freshness
- [ ] **Selection Guard** was run (if multiple assistant candidates exist) and the chosen one satisfies required signals.
- [ ] **Required docs surface present** in the diff: rubric overview, ops doc, checklist/example, negative sample, and presence-check tests.
- [ ] Optional signals present when applicable: ADRs for gate + evaluator, PR template updates.
- [ ] Appropriate tools selected (e.g., browsing for volatile topics).
- [ ] Absolute dates accompany any relative time phrasing.
- [ ] Citations are load-bearing and not dumps; domains are diverse.
