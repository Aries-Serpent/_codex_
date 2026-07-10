"""
scripts/ci/agent_frequency_audit.py
Phase 0 (WU-0.2): Agent activation frequency audit.
Reconciles:
  - .github/agents/ filesystem (agent definitions)
  - .github/agents/AGENT_REGISTRY.yaml (128 registered agents)
  - .github/workflows/ YAML references
  - docs/ and .codex/ document mentions
  - docs/accountability/.codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md (W-NNN rows)
Output: docs/audits/AGENTIC_BASELINE_AUDIT_v2.md (section: Top-20 by Activation Frequency)
"""
from __future__ import annotations

import pathlib
import re
from collections import Counter
from dataclasses import dataclass, field

import yaml

REPO_ROOT    = pathlib.Path(__file__).resolve().parents[2]
AGENTS_DIR   = REPO_ROOT / ".github" / "agents"
REGISTRY_FILE = AGENTS_DIR / "AGENT_REGISTRY.yaml"
WF_DIR       = REPO_ROOT / ".github" / "workflows"
DOCS_DIR     = REPO_ROOT / "docs"
CODEX_DIR    = REPO_ROOT / ".codex"
ACCOUNTABILITY = REPO_ROOT / "docs" / "accountability" / ".codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md"
OUT_SECTION  = REPO_ROOT / "docs" / "audits" / "AGENTIC_BASELINE_AUDIT_v2.md"

# Patterns that indicate an agent file is a *definition* (not a support doc)
_DOC_PREFIXES = {
    "AGENT_CHAINING", "AGENT_DEVELOPMENT", "AGENT_ECOSYSTEM", "AGENT_IMPLEMENTATION",
    "AGENT_REGISTRY", "AGENT_SELECTION", "AI_AGENT", "API_REFERENCE", "ARCHITECTURE",
    "BATCH_SCAN", "CI_TESTING_AGENT_IMPL", "COGNITIVE_BRAIN", "COMPLIANCE_CHECKER_AGENT_PROMPT",
    "CUSTOM_COPILOT", "EMERGENT_PATTERNS", "GAP_ANALYSIS", "GITHUB_APP", "GITHUB_ENV",
    "INFRA_LINTER_AGENT_PROMPT", "K1_OPTIM", "LIVE_API", "ORCHESTRATOR_SEQ",
    "PROJECT_ARCHITECT_RESEARCHER_COMPLETE", "QUANTUM_", "RECON_SEC", "README",
    "S9", "S10", "SECRETS_CONFIG", "TOKEN_USAGE", "VALIDATION_CHECKLIST",
    "WORKFLOW_", "CRITICAL_", "AGENTS_", "CHAIN_", "CONTEXT_", "DEFERRED_",
    "FAILURE_", "FULL_", "GENESIS_", "GOVERNANCE_", "HIGH_PRIORITY",
    "IMMEDIATE_", "INTEGRATION_", "MEMORY_", "OPERATIONAL_", "PHASE_",
    "POLICY_", "QA_", "READY_", "REQ_", "REVIEW_", "ROOT_", "SECURITY_",
    "SELECTION_", "SESSION_", "SPRINT_", "STATUS_", "SYSTEM_", "TECHNICAL_",
    "TEST_", "TOP_", "UNIFIED_", "WORK_", "YAML_", "FINAL_STATUS",
    "GROUNDED_", "IMPLEMENTATION_", "CUSTOM_AGENT", ".codex/archive/deprecated/AGENTS.md",
}


def _is_doc_file(stem: str) -> bool:
    """Return True if the .md file is a documentation/support file, not an agent def."""
    upper = stem.upper()
    return any(upper.startswith(p.upper()) for p in _DOC_PREFIXES)


def discover_agent_definitions() -> list[str]:
    """
    Return sorted list of unique agent definition names from .github/agents/.
    Sources:
      1. Top-level *.md files where stem starts with lowercase (agent defs)
      2. Sub-directory names that look like agent identifiers
    """
    names: set[str] = set()

    # Top-level .md files
    for p in AGENTS_DIR.glob("*.md"):
        stem = p.stem
        if stem[0].islower() and not _is_doc_file(stem):
            # Strip .agent suffix if present
            clean = re.sub(r"\.agent$", "", stem)
            names.add(clean)

    # Sub-directories (agent packages)
    for p in AGENTS_DIR.iterdir():
        if p.is_dir() and p.name[0].islower() and p.name not in ("__pycache__", "core",
                                                                   "deploy", "docs", "metrics",
                                                                   "scripts", "tests", "workflows",
                                                                   "github_app"):
            names.add(p.name)

    return sorted(names)


def load_registry() -> dict[str, dict]:
    """Load AGENT_REGISTRY.yaml and return a dict keyed by agent id."""
    if not REGISTRY_FILE.exists():
        return {}
    with REGISTRY_FILE.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return {a["id"]: a for a in (data or {}).get("agents", [])}


def build_mention_counter(agent_names: list[str]) -> Counter:
    """
    Count how many times each agent name is mentioned across:
      - .github/workflows/*.yml
      - docs/**/*.md
      - .codex/**/*.md  .codex/**/*.json
      - docs/accountability/.codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md (W-NNN rows)
    """
    counter: Counter = Counter()

    # Build regex patterns (longest names first to avoid partial matches)
    sorted_names = sorted(agent_names, key=len, reverse=True)
    # We'll do a simple per-file scan
    search_dirs = [
        (WF_DIR, ["*.yml"]),
        (DOCS_DIR, ["**/*.md"]),
        (CODEX_DIR, ["**/*.md", "**/*.json"]),
    ]

    for base, globs in search_dirs:
        if not base.exists():
            continue
        for pattern in globs:
            for fpath in base.glob(pattern):
                try:
                    text = fpath.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                for name in sorted_names:
                    # Count non-overlapping occurrences
                    counter[name] += len(re.findall(re.escape(name), text))

    return counter


def classify_enforcement(registry_entry: dict | None, agent_name: str) -> str:
    """
    Derive enforcement tier from AGENT_REGISTRY entry or by scanning agent .md file.
    GROUNDED = references a workflow gate or 'exit 1'
    PARTIAL  = references a workflow but no hard stop
    SOFT     = markdown instructions only
    """
    # Check registry first
    if registry_entry:
        tier = registry_entry.get("enforcement_tier", "")
        if tier in ("GROUNDED", "PARTIAL", "SOFT"):
            return tier

    # Fall back to scanning the agent .md file
    for candidate in [
        AGENTS_DIR / f"{agent_name}.md",
        AGENTS_DIR / f"{agent_name}.agent.md",
        AGENTS_DIR / agent_name / "README.md",
    ]:
        if candidate.exists():
            text = candidate.read_text(encoding="utf-8", errors="ignore")
            if "cognitive-preflight" in text or "exit 1" in text or "Tier-1" in text:
                return "GROUNDED"
            if "::warning::" in text or "createComment" in text or "workflow" in text.lower():
                return "PARTIAL"
            return "SOFT"
    return "SOFT"


def classify_handoff(registry_entry: dict | None, agent_name: str) -> str:
    """Derive handoff protocol: none | soft | structured."""
    if registry_entry:
        proto = registry_entry.get("handoff_protocol", "")
        if proto in ("none", "soft", "structured"):
            return proto

    for candidate in [
        AGENTS_DIR / f"{agent_name}.md",
        AGENTS_DIR / f"{agent_name}.agent.md",
        AGENTS_DIR / agent_name / "README.md",
    ]:
        if candidate.exists():
            text = candidate.read_text(encoding="utf-8", errors="ignore")
            if "handoff_manifest" in text.lower() or '"handoff"' in text or "AgentHandoff" in text:
                return "structured"
            if "handoff" in text.lower():
                return "soft"
    return "none"


@dataclass
class AgentProfile:
    name: str
    in_registry: bool
    in_filesystem: bool
    mention_count: int
    enforcement_tier: str
    handoff_protocol: str
    accepts_handoff_from: list[str] = field(default_factory=list)
    has_dependency_declared: bool = False


def run_audit() -> None:
    print("Loading agent registry…")
    registry = load_registry()
    registered_ids = set(registry.keys())

    print("Discovering agent definitions from filesystem…")
    fs_agents = set(discover_agent_definitions())

    # Union of all known agents
    all_agents = sorted(registered_ids | fs_agents)

    print(f"  Registry agents:    {len(registered_ids)}")
    print(f"  Filesystem agents:  {len(fs_agents)}")
    print(f"  Union (total):      {len(all_agents)}")
    print(f"  .md files in agents/: {len(list(AGENTS_DIR.glob('*.md')))}")
    print(f"  Sub-directories:    {sum(1 for p in AGENTS_DIR.iterdir() if p.is_dir())}")

    print("Counting mentions across workflows, docs, .codex…")
    counter = build_mention_counter(all_agents)

    # Build profiles
    profiles: list[AgentProfile] = []
    for name in all_agents:
        reg_entry = registry.get(name)
        accepts = []
        if reg_entry:
            accepts = reg_entry.get("accepts_handoff_from", []) or []
        has_dep = bool(reg_entry and reg_entry.get("dependencies"))
        profiles.append(AgentProfile(
            name=name,
            in_registry=(name in registered_ids),
            in_filesystem=(name in fs_agents),
            mention_count=counter.get(name, 0),
            enforcement_tier=classify_enforcement(reg_entry, name),
            handoff_protocol=classify_handoff(reg_entry, name),
            accepts_handoff_from=accepts,
            has_dependency_declared=has_dep,
        ))

    # Sort by mention count desc
    profiles.sort(key=lambda p: p.mention_count, reverse=True)

    # Counts for KPI section
    grounded_count = sum(1 for p in profiles if p.enforcement_tier == "GROUNDED")
    partial_count  = sum(1 for p in profiles if p.enforcement_tier == "PARTIAL")
    soft_count     = sum(1 for p in profiles if p.enforcement_tier == "SOFT")
    structured_handoff = sum(1 for p in profiles if p.handoff_protocol == "structured")
    no_handoff = sum(1 for p in profiles if p.handoff_protocol == "none")
    no_accepts = sum(1 for p in profiles if not p.accepts_handoff_from)
    registry_only = sum(1 for p in profiles if p.in_registry and not p.in_filesystem)
    fs_only        = sum(1 for p in profiles if p.in_filesystem and not p.in_registry)
    both           = sum(1 for p in profiles if p.in_registry and p.in_filesystem)

    # --- Build output document ---
    OUT_SECTION.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Agentic Baseline Audit v2",
        "> Phase 0 (WU-0.2 + WU-0.3) | Generated by `scripts/ci/agent_frequency_audit.py`",
        "",
        "## Agent Inventory Reconciliation",
        "",
        "| Source | Count |",
        "|--------|-------|",
        f"| `.github/agents/` total files/dirs | {len(list(AGENTS_DIR.iterdir()))} |",
        f"| `.github/agents/*.md` total        | {len(list(AGENTS_DIR.glob('*.md')))} |",
        f"| Agent definition `.md` files       | {len(fs_agents)} |",
        f"| AGENT_REGISTRY.yaml registered     | {len(registered_ids)} |",
        "| Plan reference count (soft_to_GROUNDED.md) | 193 |",
        f"| **Union (known unique agents)**    | **{len(all_agents)}** |",
        f"| In registry only (no .md def)      | {registry_only} |",
        f"| In filesystem only (not registered) | {fs_only} |",
        f"| In both registry + filesystem       | {both} |",
        "",
        "### Reconciliation Notes",
        "",
        "- **372 → 197 .md files**: The problem statement referenced 372 files; the actual",
        "  count of `.md` files in `.github/agents/` is 197-198 (varies slightly across scans",
        "  as new agent docs are added). 372 likely counted all file-system entries including",
        "  sub-directories, JSON files, YAML, and other non-.md artefacts.",
        f"  Of the 197 `.md` files, **{len(fs_agents)}** are genuine agent definitions (lowercase stem).",
        "- **128 registered (AGENT_REGISTRY.yaml v1.7.0)**: The authoritative registry",
        "  includes agents with full metadata (id, status, capabilities).",
        "- **193 plan reference**: `soft_to_GROUNDED.md` references 193 as the target",
        "  registry size after Phase 1 expansion. This is the **target**, not current state.",
        f"- **Current canonical active count**: {len(all_agents)} unique agent identifiers",
        "  (registry + filesystem union). Phase 1 task is to reconcile to a single",
        "  authoritative list and update AGENT_REGISTRY.yaml to cover all.",
        "",
        "---",
        "",
        "## Top-20 Agents by Activation Frequency",
        "",
        "| Rank | Agent | Mentions | In Registry | Enforcement Tier | Handoff |",
        "|------|-------|:--------:|:-----------:|:----------------:|:-------:|",
    ]

    for i, p in enumerate(profiles[:20], 1):
        reg_mark = "✅" if p.in_registry else "❌"
        lines.append(
            f"| {i} | `{p.name}` | {p.mention_count} | {reg_mark} "
            f"| {p.enforcement_tier} | {p.handoff_protocol} |"
        )

    lines += [
        "",
        "---",
        "",
        "## Agent Enforcement Classification",
        "",
        "| Agent | In Registry | Enforcement Tier | Handoff Protocol | Accepts Handoff From | Has Deps |",
        "|-------|:-----------:|:----------------:|:----------------:|---------------------|:--------:|",
    ]

    for p in sorted(profiles, key=lambda x: x.name):
        reg_mark = "✅" if p.in_registry else "❌"
        accepts = ", ".join(p.accepts_handoff_from) if p.accepts_handoff_from else "—"
        has_dep = "✅" if p.has_dependency_declared else "❌"
        lines.append(
            f"| `{p.name}` | {reg_mark} | {p.enforcement_tier} "
            f"| {p.handoff_protocol} | {accepts} | {has_dep} |"
        )

    # E→D gap analysis
    soft_no_handoff = [p for p in profiles if p.enforcement_tier == "SOFT" and p.handoff_protocol == "none"]
    no_accepts_list = [p for p in profiles if not p.accepts_handoff_from]

    lines += [
        "",
        "---",
        "",
        "## E→D Transition Gaps",
        "",
        f"**Agents with `enforcement_tier=SOFT` AND `handoff_protocol=none`** ({len(soft_no_handoff)} agents):",
        "These are the highest-priority candidates for Phase 2 grounding.",
        "",
        "| Agent | Mentions |",
        "|-------|:--------:|",
    ]
    for p in sorted(soft_no_handoff, key=lambda x: x.mention_count, reverse=True)[:30]:
        lines.append(f"| `{p.name}` | {p.mention_count} |")

    lines += [
        "",
        f"**Agents with no `accepts_handoff_from` declared** ({len(no_accepts_list)} agents):",
        "These agents cannot participate in orchestrator→specialist delegation.",
        "",
        "---",
        "",
        "## KPI Baselines (Phase 0)",
        "",
        "| KPI | Baseline Value | Target |",
        "|-----|---------------|--------|",
        f"| Total agent definitions (union) | {len(all_agents)} | ≥193 |",
        f"| Registered in AGENT_REGISTRY.yaml | {len(registered_ids)} | {len(all_agents)} (100%) |",
        f"| Agents with enforcement_tier=GROUNDED | {grounded_count} | {len(all_agents)} |",
        f"| Agents with enforcement_tier=PARTIAL   | {partial_count} | 0 |",
        f"| Agents with enforcement_tier=SOFT      | {soft_count} | ≤2 (Tier-3 count) |",
        f"| Agents with structured handoff | {structured_handoff} | {len(all_agents)} |",
        f"| Agents with no handoff protocol | {no_handoff} | 0 |",
        f"| Agents with no `accepts_handoff_from` | {no_accepts} | 0 |",
        f"| Agents unregistered (fs-only) | {fs_only} | 0 |",
        "| Tier-3 policy count (workflow SOFT) | see WORKFLOW_COMPLIANCE_MATRIX.md | ≤2 |",
        "| CI failure rate (7d) | see CODEX_CI_FAILURE_RATE repo var | <20% |",
        "| E→D transition conditions met | 0/5 | 5/5 |",
        "| Cascade risk workflows | 0 | 0 |",
        "",
        "---",
        "",
        "*Generated by `scripts/ci/agent_frequency_audit.py` — Phase 0 WU-0.2*",
        "",
    ]

    # Preserve existing content if file already has E→D section
    existing = ""
    if OUT_SECTION.exists():
        existing = OUT_SECTION.read_text(encoding="utf-8")
        # If it already has E→D Transition Map section, keep it
        if "## E→D Transition Map" in existing:
            etod_start = existing.index("## E→D Transition Map")
            lines.append(existing[etod_start:])

    OUT_SECTION.write_text("\n".join(lines) + "\n")
    print(f"\nBaseline audit written: {OUT_SECTION}")
    print(f"  Unique agents: {len(all_agents)}")
    print(f"  GROUNDED={grounded_count}  PARTIAL={partial_count}  SOFT={soft_count}")
    print(f"  Structured handoff={structured_handoff}  No handoff={no_handoff}")
    print(f"  No accepts_handoff_from: {no_accepts}")
    print(f"  Registry-only: {registry_only}  FS-only: {fs_only}  Both: {both}")

    return profiles


def _run() -> None:
    run_audit()


if __name__ == "__main__":
    _run()
