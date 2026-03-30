#!/usr/bin/env python3
"""Generate a per-module, per-function coverage map from one or more coverage.xml files.

Outputs:
    .codex/coverage/coverage_map.json  — machine-readable; used by agent context injection
    .codex/coverage/COVERAGE_GAPS.md   — human-readable index of uncovered functions

Usage:
    # Single XML (e.g. after running test-rag):
    python scripts/ci/generate_coverage_map.py coverage.xml

    # Merge multiple XML reports (from different suites):
    python scripts/ci/generate_coverage_map.py \\
        coverage-rag.xml coverage-core.xml coverage-sharded.xml \\
        --merge

    # Query a single module (agent helper):
    python scripts/ci/generate_coverage_map.py --query codex.rag.embeddings

    # PR delta mode (compare base map with head map):
    python scripts/ci/generate_coverage_map.py \\
        --pr-delta .codex/coverage/coverage_map.json /tmp/head_coverage_map.json

See .codex/plans/codebase_wide_coverage_plan.md for full architecture.
"""

from __future__ import annotations

import ast
import json
import sys
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / ".codex" / "coverage"
MAP_PATH = OUT_DIR / "coverage_map.json"
GAPS_MD_PATH = OUT_DIR / "COVERAGE_GAPS.md"

# Risk thresholds (line_rate)
RISK_LOW = 0.90
RISK_MEDIUM = 0.50
RISK_HIGH = 0.20


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class FunctionEntry:
    name: str
    start_line: int
    end_line: int
    is_covered: bool
    category: str = "function"  # "function" | "method" | "async_function" | "generator"
    risk: str = "unknown"  # "low" | "medium" | "high" | "critical"


@dataclass
class ModuleEntry:
    module: str
    file: str
    suite: str
    line_rate: float
    branch_rate: float
    uncovered_lines: list[int] = field(default_factory=list)
    covered_lines: list[int] = field(default_factory=list)
    uncovered_functions: list[dict[str, Any]] = field(default_factory=list)
    covered_functions: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# XML parsing
# ---------------------------------------------------------------------------


def _file_to_module(filename: str) -> str:
    """Convert a relative file path to a dotted module name.

    Examples:
        src/codex/rag/embeddings.py  →  codex.rag.embeddings
        src/codex/cli.py             →  codex.cli
    """
    p = Path(filename)
    # Strip leading src/ if present
    parts = list(p.with_suffix("").parts)
    if parts and parts[0] == "src":
        parts = parts[1:]
    return ".".join(parts)


def _line_rate(element: ET.Element) -> float:
    try:
        return float(element.attrib.get("line-rate", "0"))
    except (ValueError, TypeError):
        return 0.0


def _branch_rate(element: ET.Element) -> float:
    try:
        return float(element.attrib.get("branch-rate", "0"))
    except (ValueError, TypeError):
        return 0.0


def parse_coverage_xml(
    xml_path: Path,
    suite_name: str = "unknown",
) -> dict[str, ModuleEntry]:
    """Parse a coverage.xml file and return a dict of module_name → ModuleEntry."""
    entries: dict[str, ModuleEntry] = {}

    try:
        tree = ET.parse(xml_path)
    except ET.ParseError as exc:
        print(f"[warn] Could not parse {xml_path}: {exc}", file=sys.stderr)
        return entries

    root = tree.getroot()

    for pkg in root.iter("package"):
        for cls in pkg.iter("class"):
            filename = cls.attrib.get("filename", "")
            if not filename:
                continue

            # Resolve to repo-relative path
            if not Path(filename).is_absolute():
                file_path = REPO_ROOT / filename
            else:
                file_path = Path(filename)
            rel_path = filename

            module = _file_to_module(rel_path)
            lr = _line_rate(cls)
            br = _branch_rate(cls)

            covered_lines: list[int] = []
            uncovered_lines: list[int] = []
            for line_el in cls.iter("line"):
                try:
                    lineno = int(line_el.attrib["number"])
                    hits = int(line_el.attrib.get("hits", "0"))
                except (KeyError, ValueError):
                    continue
                if hits > 0:
                    covered_lines.append(lineno)
                else:
                    uncovered_lines.append(lineno)

            # Build function coverage from AST if source is available
            uncovered_fns, covered_fns = _annotate_functions(
                file_path, uncovered_lines, covered_lines
            )

            if module in entries:
                # Merge: union of covered lines, prefer higher line_rate
                existing = entries[module]
                existing.covered_lines = sorted(
                    set(existing.covered_lines) | set(covered_lines)
                )
                existing.uncovered_lines = sorted(
                    set(existing.uncovered_lines) - set(covered_lines)
                )
                if lr > existing.line_rate:
                    existing.line_rate = lr
                    existing.branch_rate = br
            else:
                entries[module] = ModuleEntry(
                    module=module,
                    file=rel_path,
                    suite=suite_name,
                    line_rate=lr,
                    branch_rate=br,
                    covered_lines=sorted(covered_lines),
                    uncovered_lines=sorted(uncovered_lines),
                    uncovered_functions=[asdict(f) for f in uncovered_fns],
                    covered_functions=[f.name for f in covered_fns],
                )

    return entries


# ---------------------------------------------------------------------------
# AST-based function annotation
# ---------------------------------------------------------------------------


def _function_risk(line_rate: float) -> str:
    if line_rate >= RISK_LOW:
        return "low"
    if line_rate >= RISK_MEDIUM:
        return "medium"
    if line_rate >= RISK_HIGH:
        return "high"
    return "critical"


def _annotate_functions(
    file_path: Path,
    uncovered_lines: list[int],
    covered_lines: list[int],
) -> tuple[list[FunctionEntry], list[FunctionEntry]]:
    """Use AST to map uncovered/covered lines to function definitions."""
    covered_set = set(covered_lines)

    try:
        raw = file_path.read_bytes()
        try:
            source = raw.decode("utf-8")
        except UnicodeDecodeError:
            # Source file contains non-UTF-8 bytes; replace invalid sequences so
            # AST parsing can still proceed, but log the issue for visibility.
            source = raw.decode("utf-8", errors="replace")
            print(
                f"[warn] {file_path}: non-UTF-8 bytes replaced during AST parse",
                file=sys.stderr,
            )
        tree = ast.parse(source, filename=str(file_path))
    except (OSError, SyntaxError):
        return [], []

    functions: list[FunctionEntry] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        start = node.lineno
        end = getattr(node, "end_lineno", start)
        fn_lines = set(range(start, end + 1))

        covered_in_fn = fn_lines & covered_set

        if not fn_lines:
            continue

        fn_covered = len(covered_in_fn) / len(fn_lines) if fn_lines else 0
        category = (
            "async_function"
            if isinstance(node, ast.AsyncFunctionDef)
            else "function"
        )
        is_covered = fn_covered >= 0.50  # >50 % of function body is executed

        functions.append(
            FunctionEntry(
                name=node.name,
                start_line=start,
                end_line=end,
                is_covered=is_covered,
                category=category,
                risk=_function_risk(fn_covered),
            )
        )

    covered_fns = [f for f in functions if f.is_covered]
    uncovered_fns = [f for f in functions if not f.is_covered]
    return uncovered_fns, covered_fns


# ---------------------------------------------------------------------------
# Map generation
# ---------------------------------------------------------------------------


def build_coverage_map(
    xml_paths: list[Path],
    suite_names: Optional[list[str]] = None,
    git_sha: str = "",
) -> dict[str, Any]:
    """Merge one or more coverage.xml reports into a unified coverage map dict."""
    if suite_names is None:
        suite_names = [p.stem for p in xml_paths]

    all_modules: dict[str, ModuleEntry] = {}
    for xml_path, suite in zip(xml_paths, suite_names):
        parsed = parse_coverage_xml(xml_path, suite_name=suite)
        for module, entry in parsed.items():
            if module in all_modules:
                # Merge: take the higher line_rate
                existing = all_modules[module]
                if entry.line_rate > existing.line_rate:
                    all_modules[module] = entry
            else:
                all_modules[module] = entry

    # Compute aggregates
    rates = [e.line_rate for e in all_modules.values()]
    overall = sum(rates) / len(rates) if rates else 0.0

    zero_cov = [m for m, e in all_modules.items() if e.line_rate == 0.0]
    low_cov = [m for m, e in all_modules.items() if 0.0 < e.line_rate < RISK_MEDIUM]
    total_uncov_fns = sum(len(e.uncovered_functions) for e in all_modules.values())
    high_risk_fns = sum(
        1
        for e in all_modules.values()
        for f in e.uncovered_functions
        if f.get("risk") in ("high", "critical")
    )

    return {
        "_meta": {
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "git_sha": git_sha or _current_sha(),
            "source_suites": suite_names,
            "total_modules": len(all_modules),
            "overall_line_rate": round(overall, 4),
        },
        "modules": {m: asdict(e) for m, e in all_modules.items()},
        "gaps_summary": {
            "modules_zero_coverage": zero_cov,
            "modules_below_50pct": low_cov,
            "total_uncovered_functions": total_uncov_fns,
            "high_risk_functions": high_risk_fns,
        },
    }


def _current_sha() -> str:
    try:
        import subprocess

        return (
            subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=REPO_ROOT,
                text=True,
                stderr=subprocess.DEVNULL,
            )
            .strip()
        )
    except Exception:
        return "unknown"


# ---------------------------------------------------------------------------
# Markdown gap report
# ---------------------------------------------------------------------------


def build_gaps_md(coverage_map: dict[str, Any]) -> str:
    meta = coverage_map.get("_meta", {})
    modules = coverage_map.get("modules", {})
    gaps = coverage_map.get("gaps_summary", {})
    lines = [
        "# Coverage Gaps Index — codex repository",
        f"> **Generated:** {meta.get('generated_at', 'unknown')}  "
        f"| **SHA:** `{meta.get('git_sha', '?')}`  "
        f"| **Overall:** {meta.get('overall_line_rate', 0) * 100:.1f}%",
        f"> **Suites:** {', '.join(meta.get('source_suites', []))}",
        "",
        "<!-- AUTO-GENERATED — do not edit manually; see generate_coverage_map.py -->",
        "",
        "## Quick Summary",
        "",
        "| Stat | Value |",
        "|------|-------|",
        f"| Total modules measured | {meta.get('total_modules', 0)} |",
        f"| Overall line rate | {meta.get('overall_line_rate', 0) * 100:.1f}% |",
        f"| Modules with 0% coverage | {len(gaps.get('modules_zero_coverage', []))} |",
        f"| Modules below 50% | {len(gaps.get('modules_below_50pct', []))} |",
        f"| Total uncovered functions | {gaps.get('total_uncovered_functions', 0)} |",
        f"| High-risk uncovered functions | {gaps.get('high_risk_functions', 0)} |",
        "",
    ]

    # Zero coverage
    zero = gaps.get("modules_zero_coverage", [])
    if zero:
        lines += [
            "## 🔴 Zero-Coverage Modules",
            "",
            "| Module | File | Lines |",
            "|--------|------|-------|",
        ]
        for m in sorted(zero):
            e = modules.get(m, {})
            total = len(e.get("covered_lines", [])) + len(e.get("uncovered_lines", []))
            lines.append(f"| `{m}` | `{e.get('file', '?')}` | {total} |")
        lines.append("")

    # Low coverage (<50%)
    low = sorted(
        (m for m, e in modules.items() if 0 < e.get("line_rate", 0) < RISK_MEDIUM),
        key=lambda m: modules[m].get("line_rate", 0),
    )
    if low:
        lines += [
            "## 🟠 Low-Coverage Modules (< 50%)",
            "",
            "| Module | Coverage | Uncovered Functions |",
            "|--------|----------|---------------------|",
        ]
        for m in low:
            e = modules[m]
            lr = e.get("line_rate", 0) * 100
            fns = ", ".join(
                f.get("name", "?") for f in e.get("uncovered_functions", [])
            )
            if len(fns) > 80:
                fns = fns[:77] + "..."
            lines.append(f"| `{m}` | {lr:.1f}% | {fns or '—'} |")
        lines.append("")

    # Medium coverage (50–90%)
    med = sorted(
        (m for m, e in modules.items() if RISK_MEDIUM <= e.get("line_rate", 0) < RISK_LOW),
        key=lambda m: modules[m].get("line_rate", 0),
    )
    if med:
        lines += [
            "## 🟡 Partially-Covered Modules (50–90%)",
            "",
            "| Module | Coverage | Uncovered Functions |",
            "|--------|----------|---------------------|",
        ]
        for m in med:
            e = modules[m]
            lr = e.get("line_rate", 0) * 100
            uncov_fn_names = [f.get("name", "?") for f in e.get("uncovered_functions", [])]
            fns = ", ".join(uncov_fn_names[:5])
            if len(uncov_fn_names) > 5:
                fns += f" (+{len(uncov_fn_names) - 5} more)"
            lines.append(f"| `{m}` | {lr:.1f}% | {fns or '—'} |")
        lines.append("")

    # Uncovered function detail (high/critical risk only to keep it manageable)
    high_risk = [
        (m, f)
        for m, e in modules.items()
        for f in e.get("uncovered_functions", [])
        if f.get("risk") in ("high", "critical")
    ]
    if high_risk:
        lines += [
            "## ⚠️ High-Risk Uncovered Functions",
            "",
            "> These functions have < 20% line coverage. Modifying them without",
            "> adding tests first risks introducing undetected regressions.",
            "",
            "| Module | Function | Lines | Risk |",
            "|--------|----------|-------|------|",
        ]
        for m, f in sorted(high_risk, key=lambda x: x[0]):
            lines.append(
                f"| `{m}` | `{f.get('name', '?')}` | "
                f"{f.get('start_line', '?')}–{f.get('end_line', '?')} | "
                f"{f.get('risk', '?').upper()} |"
            )
        lines.append("")

    lines += [
        "---",
        "",
        "_Generated by `scripts/ci/generate_coverage_map.py`._",
        "_See `.codex/plans/codebase_wide_coverage_plan.md` for the full architecture._",
    ]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Query mode
# ---------------------------------------------------------------------------


def query_module(module_name: str) -> int:
    """Print coverage info for a single module from the stored map. Returns exit code."""
    if not MAP_PATH.exists():
        print(
            f"[error] Coverage map not found: {MAP_PATH}\n"
            "Run `python scripts/ci/generate_coverage_map.py <coverage.xml>` first.",
            file=sys.stderr,
        )
        return 1

    data = json.loads(MAP_PATH.read_text())
    modules = data.get("modules", {})

    # Try exact match, then prefix match
    entry = modules.get(module_name)
    if entry is None:
        matches = [k for k in modules if module_name in k]
        if not matches:
            print(f"[error] Module '{module_name}' not found in coverage map.", file=sys.stderr)
            return 1
        if len(matches) == 1:
            entry = modules[matches[0]]
            module_name = matches[0]
        else:
            print(f"Ambiguous query '{module_name}'. Matches:", file=sys.stderr)
            for m in matches:
                print(f"  {m}", file=sys.stderr)
            return 1

    lr = entry.get("line_rate", 0) * 100
    br = entry.get("branch_rate", 0) * 100
    uncov = entry.get("uncovered_functions", [])
    cov = entry.get("covered_functions", [])

    risk = _function_risk(entry.get("line_rate", 0))
    risk_icon = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}.get(
        risk, "❓"
    )

    print(f"\n{'─' * 60}")
    print(f"  {risk_icon}  {module_name}")
    print(f"{'─' * 60}")
    print(f"  File:           {entry.get('file', '?')}")
    print(f"  Suite:          {entry.get('suite', '?')}")
    print(f"  Line coverage:  {lr:.1f}%  |  Branch coverage: {br:.1f}%")
    print(f"  Covered fns:    {len(cov)}  |  Uncovered fns: {len(uncov)}")

    if uncov:
        print("\n  ⚠ Uncovered functions:")
        for f in sorted(uncov, key=lambda x: x.get("start_line", 0)):
            print(
                f"    • {f['name']}  "
                f"(lines {f.get('start_line', '?')}–{f.get('end_line', '?')})  "
                f"[{f.get('category', 'fn')}]  risk={f.get('risk', '?').upper()}"
            )
    if cov:
        print(f"\n  ✅ Covered functions: {', '.join(cov[:10])}", end="")
        if len(cov) > 10:
            print(f" (+{len(cov) - 10} more)")
        else:
            print()
    print()
    return 0


# ---------------------------------------------------------------------------
# PR delta mode
# ---------------------------------------------------------------------------


def pr_delta(base_map_path: Path, head_map_path: Path) -> int:
    """Compare base and head coverage maps; print functions newly uncovered in head."""
    if not base_map_path.exists():
        print(f"[error] Base map not found: {base_map_path}", file=sys.stderr)
        return 1
    if not head_map_path.exists():
        print(f"[error] Head map not found: {head_map_path}", file=sys.stderr)
        return 1

    base = json.loads(base_map_path.read_text()).get("modules", {})
    head = json.loads(head_map_path.read_text()).get("modules", {})

    regressions: list[tuple[str, str, float, float]] = []
    for module, head_entry in head.items():
        base_entry = base.get(module, {})
        base_lr = base_entry.get("line_rate", head_entry.get("line_rate", 0))
        head_lr = head_entry.get("line_rate", 0)
        delta = head_lr - base_lr
        if delta < -0.02:  # more than 2% regression
            regressions.append((module, head_entry.get("file", "?"), base_lr, head_lr))

    if regressions:
        print("\n⚠️  Coverage regressions detected in PR:\n")
        for module, f, base_lr, head_lr in sorted(regressions, key=lambda x: x[2] - x[3]):
            print(
                f"  🔴 {module}  ({f})\n"
                f"     base={base_lr * 100:.1f}%  →  head={head_lr * 100:.1f}%  "
                f"(Δ {(head_lr - base_lr) * 100:+.1f}%)"
            )
        print()
        return 1

    print("✅ No coverage regressions detected.")
    return 0


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate or query the codebase-wide coverage map.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "xml_files",
        nargs="*",
        help="coverage.xml file(s) to parse",
    )
    parser.add_argument(
        "--merge",
        action="store_true",
        help="Merge multiple XML reports (union of covered lines)",
    )
    parser.add_argument(
        "--query",
        metavar="MODULE",
        help="Query coverage for a single module (reads stored map)",
    )
    parser.add_argument(
        "--pr-delta",
        nargs=2,
        metavar=("BASE_MAP", "HEAD_MAP"),
        help="Compare two coverage maps and show regressions",
    )
    parser.add_argument(
        "--out-dir",
        default=str(OUT_DIR),
        help=f"Output directory for map JSON and gaps MD (default: {OUT_DIR})",
    )
    parser.add_argument(
        "--git-sha",
        default="",
        help="Override git SHA embedded in the map metadata",
    )
    parser.add_argument(
        "--suite",
        action="append",
        dest="suites",
        metavar="NAME",
        help="Suite name(s) for each XML file (repeat for each file)",
    )

    args = parser.parse_args(argv)

    # --query mode
    if args.query:
        return query_module(args.query)

    # --pr-delta mode
    if args.pr_delta:
        return pr_delta(Path(args.pr_delta[0]), Path(args.pr_delta[1]))

    # Build mode
    if not args.xml_files:
        parser.error("Provide at least one coverage.xml file, or --query / --pr-delta")

    xml_paths = [Path(p) for p in args.xml_files]
    missing = [p for p in xml_paths if not p.exists()]
    if missing:
        print(
            f"[error] File(s) not found: {', '.join(str(p) for p in missing)}",
            file=sys.stderr,
        )
        return 1

    suite_names = args.suites or [p.stem for p in xml_paths]
    if len(suite_names) < len(xml_paths):
        # Pad with stem names
        suite_names += [p.stem for p in xml_paths[len(suite_names) :]]

    print(f"[info] Parsing {len(xml_paths)} coverage file(s)…")
    coverage_map = build_coverage_map(xml_paths, suite_names, git_sha=args.git_sha)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    map_out = out_dir / "coverage_map.json"
    map_out.write_text(json.dumps(coverage_map, indent=2))
    print(f"[info] Coverage map written to {map_out}")

    gaps_out = out_dir / "COVERAGE_GAPS.md"
    gaps_out.write_text(build_gaps_md(coverage_map))
    print(f"[info] Gaps index written to {gaps_out}")

    meta = coverage_map["_meta"]
    gaps = coverage_map["gaps_summary"]
    print(
        f"\n📊 Summary: {meta['total_modules']} modules | "
        f"overall {meta['overall_line_rate'] * 100:.1f}% | "
        f"{len(gaps['modules_zero_coverage'])} zero-coverage | "
        f"{gaps['total_uncovered_functions']} uncovered functions "
        f"({gaps['high_risk_functions']} high-risk)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
