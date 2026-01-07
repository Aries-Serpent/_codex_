# FORMAL_ARTIFACTS v0.3 — Interpretable Specs (CLI/metrics/policy)  
> Generated: 2025-10-09 | Author: mbaetiong  
Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5

Scope
- PEG CLI (admin+metrics), NDJSON JSON Schema (2020‑12), ReDoS‑safe regexes, token lifecycle (Mermaid), SMT‑LIB policy constraints, typing judgments (config), rewrites.

A. CLI Surface (PEG, v0.2)
- GNU‑style long options; `--k=v` ≡ `--k v`; last‑wins.
- Error codes: E_CLI_1 (missing required), E_ADMIN_1 (policy fail).
- Normalization: R1 duplicate → last, R2 `--k=v` → `--k v`, R3 path normalize, R4 booleans to typed plan, R5 lexicographic display.

B. NDJSON Metrics Schema (2020‑12, v0.3)
- epoch: integer or numeric string; else warn+reject.
- patternProperties for forward‑compatible keys.

C. ReDoS‑safe Regex (v0.2)
- Bounded quantifiers; anchors; avoid nested unbounded groups.

D. Token Lifecycle (Mermaid v2, v0.2)
- Offline → MintAppJWT → Installation Token → UseToken → Done (+ 401/403/429 branches).

E. Policy Constraints (SMT‑LIB 2, v0.1)
- admissible := online_allowlist ∧ host_allowlisted ∧ (action_readonly ∨ (action_admin ∧ admin_perms)).

F. Typing Fragments (v0.2)
- required_approvals ≥ 0 (Int), branch ≠ "" (Str). Last‑wins before typing.

G. Rewrites (v0.1)
- Termination measure: duplicates + `--k=v` count. Local confluence holds for R1/R2.

Prompts
- See docs/validation/Symbolic_Prompts_v0.3.md for A1–G1, X1–X2.

Acceptance (per artifact)
- Deterministic parse; disambiguated ops; decidable types; clear errors; stable NF.

*End of Spec*