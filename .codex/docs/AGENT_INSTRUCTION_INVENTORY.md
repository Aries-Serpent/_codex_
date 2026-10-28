# Agent instruction coverage — 2026-10-22

This is a compact inventory, not a grant of authority or proof of hosted profile
activation. Raw source snapshots and hashes remain in session artifacts rather
than repository documentation.

## Current instruction groups

| Group | Sources and scope |
| --- | --- |
| Canonical behavior | `.codex/CODEBASE_AGENCY_POLICY.md` |
| Repository Copilot guidance | `.github/copilot-instructions.md` |
| Path instructions | `.github/instructions/python.instructions.md` and `workflows.instructions.md` |
| Directory instructions | `.github/AGENTS.md`, `.github/agents/docs/AGENTS.md`, `.github/copilot-evolution/AGENTS.md`, `docs/guides/AGENTS.md`, `prompts/AGENTS.md`, `scripts/AGENTS.md`, `src/mcp/AGENTS.md` |
| Planning/coaching duplicates | `.github/agents/COPILOT_HARDENED_PLANNING_PROTOCOL.md`, `policy-coach-agent.md`, `.codex/docs/COPILOT_AGENT_PROMPT_GUIDE.md` |
| Optional startup diagnostics | `.github/copilot-prompts/active/SESSION-DIAGNOSTIC-PROTOCOL.md` |
| Workflow preparation standards | `.github/WORKFLOW_GOVERNANCE.md`; actual validation/review remains separate |
| Healing execution | `.codex/SELF_HEALING_POLICY_TIERS.md` and existing executor contracts; preparation does not change approvers |
| Historical instructions | Two archived `AGENTS.md` files; not current “main” instructions |

No repository-root/checked ancestor `AGENTS.md` or `AGENTS.override.md` was found.
The nine `AGENTS.md` files comprise seven current directory scopes and two
archived-tree scopes. Six `.github/prompts/*.prompt.md` files were inventoried
as selected task prompts, not automatic repository-wide instructions.

## Agent-profile coverage and validation

- All **661 files** under `.github/agents/` were enumerated, hashed and scanned
  programmatically, including **335 Markdown** and **53 archived-tree files**.
  This is not full manual review of every profile.
- There are **168 root Markdown files**: **126** with frontmatter delimiters
  and **42** without. Frontmatter-bearing documents include templates/guides;
  candidates are not confirmed active/selectable profiles.
- With the existing dependency-complete Python environment, **125 of 126**
  Markdown candidates pass the local frontmatter schema. The only failure is
  `.TEMPLATE_COGNITIVE_AGENT.md`, whose placeholder name/description are lists.
- Local filename discovery finds **118 definitions**: **99 Markdown** (all
  schema-valid) and **19 YAML** (7 valid, 12 with 86 schema-contract errors).
- The registry parses **120 entries** (101 locally marked active, 19 archived).
  All entry schemas pass; its header still claims 119/100/19.
- Combined local validation has **224 passing / 15 failing records**: twelve
  YAML definitions, stale registry summary, and two plain-name reference
  failures. The consolidated governance/security Markdown profiles pass
  frontmatter validation but fail the validator's narrower filename heuristic.
- No profile activation/deletion, catalog rewrite, tool-filter widening or model
  change was part of this remediation. Local registry status and body
  deprecation notices are not platform invocation controls.

## Manual versus automated inspection

The main Copilot instructions, short scoped instructions, and deep-research
profile received full manual reads. Long policies and selected profiles received
targeted manual review plus the exhaustive programmatic scan. The rewritten
canonical/planning/coaching/diagnostic guidance was reviewed as replacement
provisions, not a permissive banner over old universal mandates.

The evolution guide, archived mutant instruction and six selected task prompts
were not all fully manually reviewed. No mapping from inventoried repository
files/revisions or registry entries to hosted prompt loading was verified.
Successful invocations of Policy Coach Agent and GitHub Guru Agent in this
session demonstrate custom-agent capability, but do not establish that their
prompts came from these files or this registry. Organization instruction
inheritance and inaccessible GitHub settings also remain unverified.

## Executable checks and preserved boundaries

Handoff wording is advisory in `check_deferral_language.py`, its existing workflow
callers and commit-msg hook. Security exception owner/reason and matrix
classification still fail when evidence is missing. Wrapup accepts explicitly
declared direct work, does not invent agent IDs, and exempts local/no-PR
preparation from PR bookkeeping.

Focused regressions cover these boundaries, current-source links, unsupported
authority claims and unchanged healing approver definitions. They do not prove
live CI, GitHub permissions, runtime tool availability or successful deployment.
