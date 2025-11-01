# [Change Map]: Files Affected, Purpose, and Research References
Roles: [Audit Orchestrator], [Capability Cartographer] Energy: 5

| File | Action | Purpose | Key Changes | Gaps Addressed | CI/Policy Impact | Determinism Notes | References (/deepresearch style) |
|------|--------|---------|-------------|----------------|------------------|-------------------|----------------------------------|
| .copilot-space/workflow.yaml | UPDATE | Policy-as-code hub | Add options.fail_on_low_maturity, options.fail_on_missing_detector; document thresholds | Low-threshold hard gate; missing-detector gate | Runner reads flags; CI calls `validate` | YAML parse stable; no runtime side effects | GitHub Actions config patterns; YAML policy docs |
| scripts/space_traversal/audit_runner.py | UPDATE | Orchestrate S1–S7 and gates | Propagate required_patterns to scored; compute missing_patterns; write component_gaps.json; extend gaps.json; add `validate` command; include missing_detectors in manifest; pass thresholds to template | Required/missing patterns visibility; component gaps; missing-detector; low-threshold gate | Enables CI hard-fail via exit codes | Sorted traversal; pure local reads; stable hashing | “Policy as code” validators; SLSA-style manifest hashing |
| scripts/space_traversal/validators.py | NEW | Centralize checks | check_low_threshold(), check_missing_detectors(), emit_summary() | Encapsulate policy gates and PR summary text | Called by audit_runner validate | Pure functions on JSON; deterministic text | Lint-like patterns (flake8/mypy); exit code semantics |
| templates/audit/capability_matrix.md.j2 | UPDATE | Human-readable matrix | Show missing_patterns; annotate zero components with “(ZERO)”; correct threshold in Summary using cfg thresholds | Visibility & emphasis for reviewers | N/A | Deterministic text markers only | Jinja2 deterministic rendering; template hashing |
| .github/workflows/capability-audit.yml | NEW | CI automation & gates | Setup, run, diff, validate; baseline download/upload; 90-day retention; PR summary via GITHUB_STEP_SUMMARY | CI wiring of gates and artifacts | Enforces org policy | Pinned actions; no network extras | Official actions/upload-artifact; step summary docs |
| docs/remediation/README.md | NEW | Playbook entrypoint | Links to components/detectors/policy | Operationalize remediation | Guides reviewers and engineers | N/A | Engineering playbooks structure |
| docs/remediation/components.md | NEW | Component-level fixes | How to improve functionality, consistency, tests, safeguards, docs | Actionable next steps | N/A | N/A | Testing best practices; reproducibility checklists |
| docs/remediation/detectors.md | NEW | Detector lifecycle | Contract, unit test patterns, overrides | Reduce detector drift | N/A | N/A | Plugin contracts; dynamic loading patterns |
| docs/remediation/policy.md | NEW | Gate policy guide | How to tune thresholds, deltas, and failure modes | Policy transparency | N/A | N/A | Governance playbooks |
| docs/validation/Gaps_Coverage_Checklist_And_Scripts.md | NEW | Verification suite | Ready-to-run scripts for completeness/primary-deficit/zeros/missing patterns/missing detector | Repeatable assurance pre-merge | Optional local pre-check | Deterministic scripts | QA checklist patterns |
| .github/docs/Copilot_Audit_InstructionEnhancement.md | NEW | Copilot grounding | Instruction tips to bias Copilot to audit artifacts and remediation docs | Better dev assist | N/A | N/A | Prompt engineering groundings |
| space.mk | UPDATE | Dev ergonomics | Add space-validate target (calls runner validate) | Local parity with CI gates | Make-based local checks | Stable phony targets | Makefile CI parity patterns |

Abbreviated references:
- Jinja2 deterministic rendering: https://jinja.palletsprojects.com/
- GitHub Actions artifact retention: https://docs.github.com/actions/using-workflows/storing-workflow-data-as-artifacts
- GitHub Step Summary: https://docs.github.com/actions/using-workflows/workflow-commands-for-github-actions#adding-a-job-summary
- SLSA/Provenance concepts (manifest hashing): https://slsa.dev/spec
- Lint-like exit codes: flake8/mypy design conventions
