# [Playbook]: Component Improvements
Roles: [Audit Orchestrator], [Capability Cartographer] Energy: 5

| Component | How it's measured | Common root causes | Remediation checklist |
|-----------|-------------------|--------------------|-----------------------|
| Functionality | required vs found patterns | Patterns renamed or missing; detector too strict | Align required_patterns with code tokens; add minimal stubs; document anchors |
| Consistency | 1 - duplication_ratio | Duplicate stems across evidence files | Consolidate modules; introduce facades; delete dead copies |
| Tests | test/evidence ratio | No matching tests; test files named differently | Add unit tests named after capability token; colocate tests; use fixtures |
| Safeguards | keyword breadth | Missing integrity/repro flags | Add sha256/checksum on artifacts; seed RNG; set WANDB_MODE=offline |
| Documentation | doc token density | Docs use synonyms; missing anchors | Add explicit anchors with capability tokens; cross-link guides; update README |

Tips:
- Keep determinism: stable sort, avoid timestamped outputs in examples.
- Add "Why" in docs when introducing capability tokens to avoid noise.
