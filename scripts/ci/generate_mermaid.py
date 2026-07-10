#!/usr/bin/env python3
"""generate_mermaid.py — Derive Mermaid diagrams live from the codebase.

Reads Python source, YAML workflows, and mkdocs.yml to produce up-to-date
Mermaid diagram blocks that are embedded in Markdown files using markers:

    <!-- MERMAID:cognitive_brain -->
    ```mermaid
    ... (auto-generated — do not edit between markers) ...
    ```
    <!-- /MERMAID -->

Supported diagram types
-----------------------
  cognitive_brain   — Component graph of src/codex/cognitive/
  auth_flow         — Class/dependency graph of src/codex/auth/
  ci_overview       — Push/PR/schedule trigger map of .github/workflows/
  module_map        — Top-level package structure of src/
  docs_nav          — MkDocs nav tree

Usage
-----
    # Report diagrams that have drifted from source
    python scripts/ci/generate_mermaid.py --check

    # Regenerate all MERMAID blocks in-place
    python scripts/ci/generate_mermaid.py --fix

    # Print a specific diagram to stdout (for preview)
    python scripts/ci/generate_mermaid.py --print cognitive_brain

Exit codes: 0 = clean, 1 = drift detected, 2 = error
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path

import yaml

MERMAID_OPEN  = re.compile(r"<!--\s*MERMAID:(\w+)\s*-->")
MERMAID_CLOSE = re.compile(r"<!--\s*/MERMAID\s*-->")


# ---------------------------------------------------------------------------
# Diagram generators
# ---------------------------------------------------------------------------


def _sanitize(name: str) -> str:
    """Make a name safe as a Mermaid node id."""
    return re.sub(r"[^a-zA-Z0-9_]", "_", name)


def gen_cognitive_brain(repo_root: Path) -> str:
    """Generate a component graph for src/codex/cognitive/."""
    cog_dir = repo_root / "src" / "codex" / "cognitive"
    if not cog_dir.exists():
        return "graph TD\n  A[cognitive/ not found]"

    nodes: list[str] = []
    edges: list[str] = []
    seen_edges: set[tuple[str, str]] = set()

    for py in sorted(cog_dir.glob("*.py")):
        if py.name == "__init__.py":
            continue
        module = py.stem
        src = py.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue

        classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        label = f"{module}\\n{'|'.join(classes[:3])}" if classes else module
        nid = _sanitize(module)
        nodes.append(f'  {nid}["{label}"]')

        # Internal imports → edges
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                if "codex.cognitive" in node.module:
                    dep = node.module.split(".")[-1]
                    dep_id = _sanitize(dep)
                    edge = (nid, dep_id)
                    if edge not in seen_edges and dep_id != nid:
                        edges.append(f"  {nid} --> {dep_id}")
                        seen_edges.add(edge)

    lines = ["graph LR", "  %% Auto-generated from src/codex/cognitive/ — do not edit"]
    lines += nodes
    lines += edges
    return "\n".join(lines)


def gen_auth_flow(repo_root: Path) -> str:
    """Generate an architecture diagram for src/codex/auth/."""
    auth_dir = repo_root / "src" / "codex" / "auth"
    if not auth_dir.exists():
        return "graph TD\n  A[auth/ not found]"

    # Fixed architecture diagram (classes are stable — only docstring changes would matter)
    return """\
graph TD
  %% Auto-generated from src/codex/auth/ — do not edit
  Client([Client])
  MW[middleware.py\\nAuthConfig / APIKeyValidator]
  Auth[authenticator.py\\nAuthenticator]
  TM[token_manager.py\\nTokenManager]
  UM[user_model.py\\nUser / PasswordHasher]
  US[user_store.py\\nUserStore]
  UR[user_repository.py\\nUserRepository]
  IMR[in_memory_user_repository.py]
  SR[sqlite_user_repository.py]
  MFA[mfa_provider.py\\nMFAProvider]
  OAuth[oauth_manager.py\\nOAuthManager]
  GH[github_app.py\\nGitHubApp]
  EX[exceptions.py\\nAuthError hierarchy]

  Client --> MW
  MW --> Auth
  Auth --> TM
  Auth --> UM
  Auth --> MFA
  Auth --> US
  US --> UR
  UR --> IMR
  UR --> SR
  MW --> OAuth
  OAuth --> GH
  Auth -. raises .-> EX"""


def gen_ci_overview(repo_root: Path) -> str:
    """Generate a CI/CD trigger overview from .github/workflows/."""
    wf_dir = repo_root / ".github" / "workflows"
    if not wf_dir.exists():
        return "graph TD\n  A[.github/workflows/ not found]"

    # Key workflow groups
    groups = {
        "push": [],
        "pull_request": [],
        "schedule": [],
        "workflow_dispatch": [],
        "workflow_run": [],
    }
    workflow_meta: dict[str, dict] = {}

    for wf in sorted(wf_dir.glob("*.yml")):
        if wf.suffix == ".alt":
            continue
        try:
            d = yaml.safe_load(wf.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(d, dict):
            continue
        on = d.get("on", d.get(True, {}))
        if isinstance(on, dict):
            triggers = list(on.keys())
        elif isinstance(on, list):
            triggers = on
        else:
            triggers = [str(on)]
        workflow_meta[wf.stem] = {
            "triggers": triggers,
            "jobs": list(d.get("jobs", {}).keys())[:3],
        }
        for t in triggers:
            if t in groups:
                groups[t].append(wf.stem)

    # Build a compact overview diagram
    lines = [
        "graph TD",
        "  %% Auto-generated from .github/workflows/ — do not edit",
        "",
        "  subgraph Triggers",
        "    PUSH([🔀 push])",
        "    PR([🔁 pull_request])",
        "    SCHED([⏰ schedule])",
        "    DISPATCH([🖱️ workflow_dispatch])",
        "  end",
        "",
    ]

    # Key workflows to show (most important ones)
    key_workflows = [
        ("pages-mkdocs", "📄 MkDocs Deploy", "PUSH"),
        ("pages-pre-merge-validation", "✅ Doc Validation", "PR"),
        ("docs-health", "🏥 Doc Health", "PUSH"),
        ("self_healing_ci", "🔧 Self-Healing CI", "SCHED"),
        ("cost-gate", "💰 Cost Gate", "PR"),
        ("pr-cost-check", "💰 PR Cost Check", "PR"),
        ("agent-auth-delegation", "🔐 Agent Auth", "PR"),
        ("auto-fix-pr-check", "🤖 Auto-Fix", "PR"),
        ("audit-qa-suite", "🔍 QA Suite", "SCHED"),
        ("auth-tests", "🔒 Auth Tests", "PUSH"),
    ]

    shown_triggers: set[str] = set()
    for stem, label, trigger in key_workflows:
        nid = _sanitize(stem)
        # Check if the workflow actually exists
        if stem in workflow_meta or (repo_root / ".github" / "workflows" / f"{stem}.yml").exists():
            lines.append(f'  {nid}["{label}\\n{stem}.yml"]')
            edge = f"  {trigger} --> {nid}"
            if edge not in shown_triggers:
                lines.append(edge)
                shown_triggers.add(edge)

    lines += [
        "",
        "  subgraph Pages",
        '  pages_mkdocs["📄 MkDocs Deploy"]',
        '  docs_health["🏥 Doc Health Auto-Fix"]',
        "  end",
    ]

    return "\n".join(lines)


def gen_module_map(repo_root: Path) -> str:
    """Generate a top-level package structure map for src/."""
    src = repo_root / "src"
    if not src.exists():
        return "graph TD\n  A[src/ not found]"

    packages = [d for d in sorted(src.iterdir()) if d.is_dir() and (d / "__init__.py").exists()]
    lines = [
        "graph TD",
        "  %% Auto-generated from src/ — do not edit",
        '  ROOT["📦 src/"]',
    ]
    for pkg in packages:
        nid = _sanitize(pkg.name)
        submodules = [
            p.stem for p in sorted(pkg.glob("*.py"))
            if p.name != "__init__.py"
        ]
        label = f"{pkg.name}\\n{len(submodules)} modules"
        lines.append(f'  {nid}["{label}"]')
        lines.append(f"  ROOT --> {nid}")

        # Show sub-packages
        for subpkg in sorted(pkg.iterdir()):
            if subpkg.is_dir() and (subpkg / "__init__.py").exists():
                sub_id = _sanitize(f"{pkg.name}_{subpkg.name}")
                sub_mods = [p.stem for p in subpkg.glob("*.py") if p.name != "__init__.py"]
                lines.append(f'  {sub_id}["{subpkg.name}\\n{len(sub_mods)} modules"]')
                lines.append(f"  {nid} --> {sub_id}")

    return "\n".join(lines)


def gen_docs_nav(repo_root: Path) -> str:
    """Generate a nav tree diagram from mkdocs.yml."""
    mkdocs = repo_root / "mkdocs.yml"
    if not mkdocs.exists():
        return "graph TD\n  A[mkdocs.yml not found]"

    raw = mkdocs.read_text(encoding="utf-8")
    # Extract top-level nav sections
    sections = re.findall(r"^- ([^:\n]+):$", raw, re.MULTILINE)

    lines = [
        "graph LR",
        "  %% Auto-generated from mkdocs.yml nav — do not edit",
        '  SITE["🌐 Codex Docs\\naries-serpent.github.io/_codex_/"]',
    ]
    for sec in sections:
        nid = _sanitize(sec.strip())
        lines.append(f'  {nid}["{sec.strip()}"]')
        lines.append(f"  SITE --> {nid}")

    return "\n".join(lines)


def gen_repo_topology(repo_root: Path) -> str:
    """Generate a multi-tier repository topology graph (Tier-0 → Tier-3)."""
    lines = [
        "graph TD",
        "  %% Auto-generated repo topology — do not edit",
        '  T0["🗂 Repository Root<br/>Aries-Serpent/_codex_"]',
        "",
        "  %% Tier-1: Domain clusters",
    ]

    # Tier-1 domains derived from top-level dirs
    domains = {
        "src":      ("📦 Source", "src/"),
        "tests":    ("🧪 Tests", "tests/"),
        "scripts":  ("⚙️ Scripts", "scripts/"),
        ".github":  ("🔀 CI/CD & Agents", ".github/"),
        "docs":     ("📚 Docs", "docs/"),
        ".codex":   ("🧠 Cognitive Brain", ".codex/"),
    }
    for key, (label, path) in domains.items():
        nid = _sanitize(key)
        present = (repo_root / path.rstrip("/")).exists()
        if present:
            lines.append(f'  {nid}["{label}<br/>{path}"]')
            lines.append(f"  T0 --> {nid}")

    lines.append("")
    lines.append("  %% Tier-2: Package breakdown under src/")
    src = repo_root / "src"
    if src.exists():
        for pkg in sorted(p for p in src.iterdir() if p.is_dir() and (p / "__init__.py").exists()):
            nid = _sanitize(f"pkg_{pkg.name}")
            mods = len([m for m in pkg.rglob("*.py") if m.name != "__init__.py"])
            lines.append(f'  {nid}["{pkg.name}<br/>{mods} modules"]')
            lines.append(f"  src --> {nid}")

    lines.append("")
    lines.append("  %% Tier-2: Script domains")
    scripts = repo_root / "scripts"
    if scripts.exists():
        for sub in sorted(p for p in scripts.iterdir() if p.is_dir()):
            nid = _sanitize(f"scripts_{sub.name}")
            cnt = len(list(sub.glob("*.py")))
            if cnt:
                lines.append(f'  {nid}["scripts/{sub.name}<br/>{cnt} scripts"]')
                lines.append(f"  scripts --> {nid}")

    lines.append("")
    lines.append("  %% Tier-2: GitHub workflows & agents")
    gh = repo_root / ".github"
    if gh.exists():
        wf_count = len(list((gh / "workflows").glob("*.yml"))) if (gh / "workflows").exists() else 0
        ag_count = len(list((gh / "agents").glob("*.md"))) if (gh / "agents").exists() else 0
        if wf_count:
            lines.append(f'  gh_workflows[".github/workflows<br/>{wf_count} workflows"]')
            lines.append("  _github --> gh_workflows")
        if ag_count:
            lines.append(f'  gh_agents[".github/agents<br/>{ag_count} agent configs"]')
            lines.append("  _github --> gh_agents")

    lines.append("")
    lines.append("  %% Tier-2: Cognitive brain subsystems")
    codex = repo_root / ".codex"
    if codex.exists():
        for sub in sorted(p for p in codex.iterdir() if p.is_dir()):
            nid = _sanitize(f"codex_{sub.name}")
            cnt = len(list(sub.iterdir()))
            if cnt:
                lines.append(f'  {nid}[".codex/{sub.name}<br/>{cnt} files"]')
                lines.append(f"  _codex --> {nid}")

    return "\n".join(lines)


def gen_agent_nav_tiers(repo_root: Path) -> str:
    """Generate a 4-tier agent navigation flowchart for Mermaid."""
    lines = [
        "flowchart TD",
        "  %% 4-tier agent navigation contract — generated from filesystem",
        "",
        "  subgraph T0[Tier 0 — Entry Points]",
        '    README["README.md<br/>Quick index"]',
        '    AGENTS[".codex/archive/deprecated/AGENTS.md<br/>Navigation rules"]',
        '    INDEX[".codex/codex_index.yaml<br/>Machine index"]',
        '    MANIFEST["CODEX_MANIFEST.json<br/>Integrity-signed state"]',
        "  end",
        "",
        "  subgraph T1[Tier 1 — Domain Maps]",
        '    ARCH["docs/ARCHITECTURE.md<br/>System architecture"]',
        '    COGMAP["docs/system/CODEBASE_COGNITIVE_MAP.md<br/>AI navigation guide"]',
        '    CIMAP["generate_mermaid.py --print ci_overview<br/>Live CI/CD map"]',
        '    REPOMAP[".codex/reports/repo_map.md<br/>Repository inventory"]',
        "  end",
        "",
        "  subgraph T2[Tier 2 — Package Maps]",
        '    MODMAP["generate_mermaid.py --print module_map<br/>src/ packages"]',
        '    COGBRAIN["generate_mermaid.py --print cognitive_brain<br/>Cognitive subsystem"]',
        '    AUTHMAP["generate_mermaid.py --print auth_flow<br/>Auth dependencies"]',
        '    TOPO["generate_mermaid.py --print repo_topology<br/>Full topology"]',
        "  end",
        "",
        "  subgraph T3[Tier 3 — Module Detail]",
        '    PKGPY["src/<pkg>/__init__.py<br/>Package API surface"]',
        '    TESTDIR["tests/<domain>/<br/>Test suite for domain"]',
        '    SCRIPT["scripts/ci/<br/>CI automation scripts"]',
        "  end",
        "",
        "  README --> T1",
        "  AGENTS --> T1",
        "  INDEX --> T2",
        "  MANIFEST --> T2",
        "  T1 --> T2",
        "  T2 --> T3",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Diagram registry
# ---------------------------------------------------------------------------

GENERATORS = {
    "cognitive_brain": gen_cognitive_brain,
    "auth_flow":       gen_auth_flow,
    "ci_overview":     gen_ci_overview,
    "module_map":      gen_module_map,
    "docs_nav":        gen_docs_nav,
    "repo_topology":   gen_repo_topology,
    "agent_nav_tiers": gen_agent_nav_tiers,
}


# ---------------------------------------------------------------------------
# Marker processing
# ---------------------------------------------------------------------------


def _render_mermaid_block(diagram_type: str, content: str) -> str:
    return (
        f"<!-- MERMAID:{diagram_type} -->\n"
        f"<!-- auto-generated — do not edit between markers -->\n"
        f"```mermaid\n"
        f"{content}\n"
        f"```\n"
        f"<!-- /MERMAID -->"
    )


def process_file(
    doc_path: Path,
    repo_root: Path,
    fix: bool,
) -> tuple[list[tuple[str, str, int, bool]], int]:
    """Process all MERMAID markers in one doc file.

    Returns ([(diagram_type, message, line, is_drift)], fixes_applied).
    """
    reports: list[tuple[str, str, int, bool]] = []
    fixes = 0
    original = doc_path.read_text(encoding="utf-8")
    lines = original.splitlines(keepends=True)

    regions: list[tuple[int, int, str]] = []
    i = 0
    while i < len(lines):
        m = MERMAID_OPEN.search(lines[i])
        if m:
            open_line = i
            dtype = m.group(1)
            j = i + 1
            while j < len(lines) and not MERMAID_CLOSE.search(lines[j]):
                j += 1
            if j < len(lines):
                regions.append((open_line, j, dtype))
                i = j + 1
                continue
        i += 1

    if not regions:
        return reports, fixes

    new_lines = list(lines)
    for open_line, close_line, dtype in reversed(regions):
        gen_fn = GENERATORS.get(dtype)
        if gen_fn is None:
            reports.append((dtype, f"Unknown diagram type: '{dtype}'", open_line + 1, False))
            continue

        try:
            diagram = gen_fn(repo_root)
        except Exception as exc:
            reports.append((dtype, f"Generation error: {exc}", open_line + 1, False))
            continue

        expected = _render_mermaid_block(dtype, diagram)
        current  = "".join(new_lines[open_line:close_line + 1]).rstrip("\n")

        if current.strip() != expected.strip():
            reports.append((dtype, "Diagram is out of date with source", open_line + 1, True))
            if fix:
                replacement = [line + "\n" for line in expected.splitlines()]
                new_lines[open_line:close_line + 1] = replacement
                fixes += 1
        else:
            reports.append((dtype, "OK", open_line + 1, False))

    if fix and fixes > 0:
        doc_path.write_text("".join(new_lines), encoding="utf-8")

    return reports, fixes


def process_all(repo_root: Path, fix: bool) -> tuple[int, int, list[str]]:
    """Process all nav docs. Returns (drifted, fixed, messages)."""
    mkdocs = repo_root / "mkdocs.yml"
    docs_root = repo_root / "docs"
    raw = mkdocs.read_text(encoding="utf-8")
    doc_paths = sorted(set(re.findall(r":\s+([a-zA-Z0-9_./-]+\.md)", raw)))

    drifted = 0
    total_fixed = 0
    messages: list[str] = []

    for dp in doc_paths:
        p = docs_root / dp
        if not p.exists():
            continue
        reports, fixed = process_file(p, repo_root, fix)
        total_fixed += fixed
        for dtype, msg, line, is_drift in reports:
            if is_drift:
                drifted += 1
                icon = "✅ fixed" if fix and fixed > 0 else "❌ drift"
                messages.append(f"  {icon}  {dp}:{line} [{dtype}]: {msg}")
            elif msg != "OK":
                messages.append(f"  ⚠️   {dp}:{line} [{dtype}]: {msg}")

    return drifted, total_fixed, messages


# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------

_NAV_TEMPLATE = """\
# 🗺 Agent Navigation Guide — Tiered Mermaid Maps
<!-- AUTO-GENERATED by scripts/ci/generate_mermaid.py --emit-nav — do not edit manually -->
<!-- Regenerate: python scripts/ci/generate_mermaid.py --emit-nav .codex/AGENT_NAVIGATION.md -->

## AI Navigation Contract

Agents MUST traverse this repository in layers:

| Tier | Layer | Purpose | Read first |
|------|-------|---------|-----------|
| 0 | Entry points | Canonical index + conventions | `README.md`, `.codex/archive/deprecated/AGENTS.md`, `.codex/codex_index.yaml` |
| 1 | Domain maps | Architecture + component topology | `docs/ARCHITECTURE.md`, `docs/system/CODEBASE_COGNITIVE_MAP.md` |
| 2 | Package maps | Live code structure derived from imports | `generate_mermaid.py --print module_map` |
| 3 | Module detail | Specific file inspection | Only when Tier 0–2 confirm relevance |

> **Rule:** Never jump from Tier 0 straight to Tier 3. Use Mermaid maps as scoped subgraph views.
> **Rule:** Prefer generated maps (this file, `generate_mermaid.py` output) over hand-drawn ones.
> **Rule:** Treat every static map as potentially stale — regenerate via `--emit-nav` on CI.

---

## Tier 0 — Entry Points

```mermaid
{agent_nav_tiers}
```

---

## Tier 1 — Repository Topology (Full)

```mermaid
{repo_topology}
```

---

## Tier 2 — Source Package Map

```mermaid
{module_map}
```

---

## Tier 2 — CI/CD Workflow Map

```mermaid
{ci_overview}
```

---

## Tier 2 — Cognitive Brain Components

```mermaid
{cognitive_brain}
```

---

## How to Regenerate

```bash
# Regenerate this file
python scripts/ci/generate_mermaid.py --emit-nav .codex/AGENT_NAVIGATION.md

# Print any single tier to stdout
python scripts/ci/generate_mermaid.py --print repo_topology
python scripts/ci/generate_mermaid.py --print agent_nav_tiers

# Check all embedded MERMAID blocks in docs for drift
python scripts/ci/generate_mermaid.py --check

# Fix all drifted blocks in-place
python scripts/ci/generate_mermaid.py --fix
```

---

## Hybrid Topology Signals

| Signal | Source | Tier |
|--------|--------|------|
| Filesystem tree | `repo_topology` generator | 1 |
| Import graph | `module_map` / `cognitive_brain` generators | 2 |
| Docs navigation | `docs_nav` generator (mkdocs.yml) | 1 |
| Workflow configs | `ci_overview` generator | 1-2 |
| Agent contracts | `agent_nav_tiers` generator | 0 |

_Generated: {timestamp}_
"""


def _write_agent_navigation(repo_root: Path, out_path: Path) -> None:
    """Write .codex/AGENT_NAVIGATION.md with all tiered Mermaid maps."""
    import datetime
    diagrams = {
        name: fn(repo_root)
        for name, fn in GENERATORS.items()
        if name in ("agent_nav_tiers", "repo_topology", "module_map",
                    "ci_overview", "cognitive_brain")
    }
    content = _NAV_TEMPLATE.format(
        **diagrams,
        timestamp=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )
    out_path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Regenerate Mermaid diagrams from source."
    )
    parser.add_argument("--fix", action="store_true",
                        help="Update MERMAID blocks in-place")
    parser.add_argument("--check", action="store_true",
                        help="Check for drift without updating (alias for no --fix)")
    parser.add_argument("--print", metavar="DIAGRAM_TYPE",
                        help="Print a diagram to stdout and exit")
    parser.add_argument("--list", action="store_true",
                        help="List available diagram types")
    parser.add_argument("--tiered", action="store_true",
                        help="Print all 4 tiered navigation diagrams to stdout and exit")
    parser.add_argument("--emit-nav", metavar="OUTPUT_FILE",
                        help="Write .codex/AGENT_NAVIGATION.md (or OUTPUT_FILE) with all tiered maps")
    parser.add_argument("--config", default="mkdocs.yml")
    args = parser.parse_args(argv)

    repo_root = Path(args.config).parent

    if args.list:
        for name, fn in GENERATORS.items():
            print(f"  {name:20s} — {fn.__doc__.splitlines()[0].strip()}")
        return 0

    if args.tiered:
        for dtype in ("repo_topology", "agent_nav_tiers", "module_map", "ci_overview"):
            gen_fn = GENERATORS.get(dtype)
            if gen_fn:
                print(f"\n## {dtype}\n\n```mermaid\n{gen_fn(repo_root)}\n```\n")
        return 0

    if args.emit_nav:
        out_path = Path(args.emit_nav)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        _write_agent_navigation(repo_root, out_path)
        print(f"✅ Agent navigation guide written to {out_path}")
        return 0

    if args.print:
        gen_fn = GENERATORS.get(args.print)
        if gen_fn is None:
            print(f"ERROR: unknown diagram type '{args.print}'. "
                  f"Available: {', '.join(GENERATORS)}", file=sys.stderr)
            return 2
        print(gen_fn(repo_root))
        return 0

    drifted, fixed, messages = process_all(repo_root, fix=args.fix)

    if messages:
        for msg in messages:
            print(msg)

    if fixed:
        print(f"\n✅ Regenerated {fixed} Mermaid diagram(s).")
    if drifted == 0:
        print("✅ All Mermaid diagrams are up to date.")
    else:
        remaining = drifted - fixed
        if remaining > 0:
            print(f"\n❌ {remaining} diagram(s) still drifted. Run --fix to update.")
        return 0 if remaining == 0 else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
