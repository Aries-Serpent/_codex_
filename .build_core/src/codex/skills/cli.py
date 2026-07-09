"""Cognitive Brain Skills CLI.

Entry point: ``codex-skill`` (registered in pyproject.toml).

Sub-commands
------------
list        List registered skills with optional filters.
browse      Interactive dropdown to select and install a packaged skill.
run         Invoke a skill by id with a JSON payload.
compress    Package a skill directory into a .7z / .zip archive.
install     Extract and register a skill archive.
refresh-docs  Score, plan, and optionally apply AAIS-style doc refresh.
score       Compute AAIS score for a skill's documentation.
telemetry   Push telemetry events from a JSONL log.

Usage::

    codex-skill list
    codex-skill list --capability docs --risk-tier low
    codex-skill browse                         # interactive dropdown
    codex-skill browse --dist dist/            # pick from local archives
    codex-skill run doc.retriever.core --payload @input.json
    codex-skill compress doc.retriever.core --out dist/
    codex-skill install dist/doc-retriever-core-1.0.0.zip
    codex-skill refresh-docs --paths docs/agent --style aais --apply
    codex-skill score doc.retriever.core --emit aais_score.json
    codex-skill telemetry push --from logs/skill_events.jsonl --to file
"""

from __future__ import annotations

import json
import logging

# Fast-forward helper (optional — only wired when scripts/ci is reachable)
from pathlib import Path
from typing import Any, Optional

import typer

from .aais import AAISScorer
from .compression import compress_skill, install_skill
from .envelope import ExecutionEnvelope
from .registry import SkillRegistry, get_registry
from .telemetry import push_to_app, read_events, summarise_events

_FF_SCRIPT = Path(__file__).parents[3] / "scripts" / "ci" / "fast_forward_safe_files.py"

logger = logging.getLogger(__name__)

app = typer.Typer(
    name="codex-skill",
    help="Cognitive Brain Skills CLI — registry, routing, compression, telemetry.",
    add_completion=False,
)
telemetry_app = typer.Typer(help="Telemetry management sub-commands.")
app.add_typer(telemetry_app, name="telemetry")


def _ensure_registry() -> SkillRegistry:
    """Return the default registry after running discovery."""
    reg = get_registry()
    reg.discover()
    return reg


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------


@app.command("list")
def cmd_list(
    capability: Optional[str] = typer.Option(
        None, "--capability", "-c", help="Filter by capability tag"
    ),
    risk_tier: Optional[str] = typer.Option(
        None, "--risk-tier", "-r", help="Filter by risk tier (low|medium|high)"
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
) -> None:
    """List registered skills with optional filters."""
    reg = _ensure_registry()
    skills = reg.list(capability_tag=capability, risk_tier=risk_tier)

    if not skills:
        typer.echo("No skills found.")
        return

    if json_output:
        output = [
            {
                "id": s.skill_id,
                "version": s.version,
                "name": s.manifest.name,
                "tags": s.manifest.capability_tags,
                "risk_tier": s.manifest.policy.risk_tier,
                "aais_score": s.manifest.doc.aais_score if s.manifest.doc else None,
            }
            for s in skills
        ]
        typer.echo(json.dumps(output, indent=2))
        return

    typer.echo(f"{'ID':<35} {'VERSION':<10} {'RISK':<8} {'TAGS'}")
    typer.echo("-" * 80)
    for s in skills:
        tags_str = ", ".join(s.manifest.capability_tags[:4])
        typer.echo(f"{s.skill_id:<35} {s.version:<10} {s.manifest.policy.risk_tier:<8} {tags_str}")


# ---------------------------------------------------------------------------
# browse  (interactive dropdown)
# ---------------------------------------------------------------------------


@app.command("browse")
def cmd_browse(
    dist_dir: Optional[str] = typer.Option(
        None,
        "--dist",
        "-d",
        help="Directory of pre-built .7z/.zip archives to choose from",
    ),
    capability: Optional[str] = typer.Option(
        None, "--capability", "-c", help="Filter by capability tag"
    ),
    risk_tier: Optional[str] = typer.Option(
        None, "--risk-tier", "-r", help="Filter by risk tier (low|medium|high)"
    ),
    install_after: bool = typer.Option(
        True, "--install/--no-install", help="Install the selected skill archive"
    ),
    out_dir: str = typer.Option(
        "dist", "--out", "-o", help="Output dir when compressing before install"
    ),
) -> None:
    """Interactive dropdown to browse and install packaged skills.

    Two modes:

    1. **Registry mode** (default) — lists all discovered skills from the
       registry.  Select one by number; the CLI compresses it to ``--out``
       and (optionally) installs it back.

    2. **Archive mode** (``--dist <dir>``) — lists ``.7z``/``.zip`` archives
       in *dist_dir*.  Select one; the CLI installs it directly.
    """
    # ── Archive mode: list .7z / .zip files ─────────────────────────────────
    if dist_dir is not None:
        dist_path = Path(dist_dir)
        if not dist_path.is_dir():
            typer.echo(f"Directory not found: {dist_path}", err=True)
            raise typer.Exit(1)

        archives = sorted(
            p for p in dist_path.iterdir() if p.suffix in {".7z", ".zip"} and p.is_file()
        )
        if not archives:
            typer.echo(f"No .7z or .zip archives found in '{dist_path}'.")
            raise typer.Exit(0)

        typer.echo(_BROWSE_HEADER)
        typer.echo(f"{'#':<4} {'ARCHIVE':<55} {'SIZE':>10}")
        typer.echo("-" * 72)
        for idx, arc in enumerate(archives, start=1):
            size_kb = arc.stat().st_size // 1024
            typer.echo(f"{idx:<4} {arc.name:<55} {size_kb:>8} KB")

        selection = _prompt_selection(len(archives))
        if selection is None:
            typer.echo("Cancelled.")
            raise typer.Exit(0)

        chosen = archives[selection - 1]
        typer.echo(f"\n→ Selected: {chosen.name}")

        if install_after:
            try:
                dest = install_skill(chosen)
                typer.echo(f"✅ Installed to: {dest}")
                reg = _ensure_registry()
                reg.discover(dest.parent)
                typer.echo(f"   Registry now has {len(reg)} skill(s).")
            except (FileNotFoundError, RuntimeError, ValueError) as exc:
                typer.echo(f"Install failed: {exc}", err=True)
                raise typer.Exit(1)
        return

    # ── Registry mode: list discovered skills ───────────────────────────────
    reg = _ensure_registry()
    skills = reg.list(capability_tag=capability, risk_tier=risk_tier)

    if not skills:
        typer.echo("No skills found in registry.")
        raise typer.Exit(0)

    typer.echo(_BROWSE_HEADER)
    typer.echo(f"{'#':<4} {'ID':<38} {'VER':<8} {'RISK':<8} {'AAIS':>6}  TAGS")
    typer.echo("-" * 90)
    for idx, s in enumerate(skills, start=1):
        aais = s.manifest.doc.aais_score if s.manifest.doc else None
        aais_str = f"{aais:.2f}" if aais is not None else "  —  "
        tags_str = ", ".join(s.manifest.capability_tags[:3])
        typer.echo(
            f"{idx:<4} {s.skill_id:<38} {s.version:<8} "
            f"{s.manifest.policy.risk_tier:<8} {aais_str:>6}  {tags_str}"
        )

    selection = _prompt_selection(len(skills))
    if selection is None:
        typer.echo("Cancelled.")
        raise typer.Exit(0)

    chosen_skill = skills[selection - 1]
    typer.echo(f"\n→ Selected: {chosen_skill.skill_id} v{chosen_skill.version}")

    if install_after:
        # Compress to out_dir, then install
        try:
            out_path = Path(out_dir)
            out_path.mkdir(parents=True, exist_ok=True)
            metrics = compress_skill(
                chosen_skill.skill_id,
                out_dir=out_path,
                format="7z",
                level="max",
            )
            typer.echo(
                f"📦 Compressed → {metrics.archive_path}  "
                f"({metrics.size_before} → {metrics.size_after} bytes)"
            )
            dest = install_skill(Path(metrics.archive_path))
            typer.echo(f"✅ Installed to: {dest}")
            reg.discover(dest.parent)
            typer.echo(f"   Registry now has {len(reg)} skill(s).")
        except (FileNotFoundError, RuntimeError, ValueError) as exc:
            typer.echo(f"Package/install failed: {exc}", err=True)
            raise typer.Exit(1)


# Browse helper constants / functions

_BROWSE_HEADER = (
    "\n╔══════════════════════════════════════════════════════════════════════╗\n"
    "║           Cognitive Brain Skills — Available Packages                ║\n"
    "╚══════════════════════════════════════════════════════════════════════╝\n"
)


def _prompt_selection(max_idx: int) -> Optional[int]:
    """Prompt the user for a number in [1, max_idx]; return None on cancel."""
    while True:
        raw = typer.prompt(
            f"\nEnter number [1-{max_idx}] or 'q' to quit",
            default="q",
        )
        if str(raw).strip().lower() in {"q", "quit", "exit", ""}:
            return None
        try:
            val = int(str(raw).strip())
            if 1 <= val <= max_idx:
                return val
            typer.echo(f"  Please enter a number between 1 and {max_idx}.")
        except ValueError:
            typer.echo("  Invalid input — enter a number or 'q' to quit.")


# ---------------------------------------------------------------------------
# run
# ---------------------------------------------------------------------------


@app.command("run")
def cmd_run(
    skill_id: str = typer.Argument(..., help="Dotted skill identifier"),
    payload: str = typer.Option("{}", "--payload", "-p", help="JSON payload or @filepath"),
    timeout_ms: Optional[int] = typer.Option(None, "--timeout-ms", help="Override timeout in ms"),
    max_retries: int = typer.Option(0, "--max-retries", help="Override max retries"),
    caller: str = typer.Option("*", "--caller", help="Caller ID for allowlist check"),
    version: Optional[str] = typer.Option(None, "--version", "-v", help="Specific skill version"),
) -> None:
    """Invoke a skill by id with a JSON payload."""
    # Resolve payload
    if payload.startswith("@"):
        path = Path(payload[1:])
        if not path.exists():
            typer.echo(f"Payload file not found: {path}", err=True)
            raise typer.Exit(1)
        payload_data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    else:
        try:
            payload_data = json.loads(payload)
        except json.JSONDecodeError as exc:
            typer.echo(f"Invalid JSON payload: {exc}", err=True)
            raise typer.Exit(1)

    reg = _ensure_registry()
    envelope = ExecutionEnvelope(reg)

    result = envelope.run(
        skill_id,
        payload_data,
        caller_id=caller,
        version=version,
        timeout_ms=timeout_ms,
        max_retries=max_retries,
    )

    typer.echo(json.dumps(result.model_dump(), indent=2))

    if result.status == "error":
        raise typer.Exit(1)


# ---------------------------------------------------------------------------
# compress
# ---------------------------------------------------------------------------


@app.command("compress")
def cmd_compress(
    skill_id: str = typer.Option(..., "--skill", "-s", help="Skill id to compress"),
    fmt: str = typer.Option("7z", "--format", "-f", help="Archive format: 7z or zip"),
    level: str = typer.Option("max", "--level", "-l", help="Compression level: max or fast"),
    record_metrics: bool = typer.Option(True, "--record-metrics/--no-record-metrics"),
    out: str = typer.Option("dist", "--out", "-o", help="Output directory"),
) -> None:
    """Package a skill directory into a distributable archive."""
    try:
        result = compress_skill(
            skill_id,
            out_dir=Path(out),
            format=fmt,
            level=level,
            record_metrics=record_metrics,
        )
        typer.echo(
            f"Compressed '{skill_id}' → {result.archive_path} "
            f"({result.size_before} → {result.size_after} bytes, "
            f"ratio={result.compression_ratio:.2f})"
        )
    except FileNotFoundError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1)


# ---------------------------------------------------------------------------
# install
# ---------------------------------------------------------------------------


@app.command("install")
def cmd_install(
    archive: str = typer.Argument(..., help="Path to .7z or .zip skill archive"),
) -> None:
    """Extract and register a skill archive."""
    try:
        dest = install_skill(Path(archive))
        typer.echo(f"Installed to: {dest}")
        # Re-discover so the newly installed skill is registered
        reg = _ensure_registry()
        reg.discover(dest.parent)
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        typer.echo(f"Install failed: {exc}", err=True)
        raise typer.Exit(1)


# ---------------------------------------------------------------------------
# refresh-docs
# ---------------------------------------------------------------------------


@app.command("refresh-docs")
def cmd_refresh_docs(
    paths: list[str] = typer.Option(..., "--paths", "-p", help="Doc paths to refresh"),
    style: str = typer.Option("aais", "--style", help="Scoring style (currently: aais)"),
    prune_stale: bool = typer.Option(
        False, "--prune-stale", help="Remove docs scoring below threshold"
    ),
    emit_plan: Optional[str] = typer.Option(None, "--emit-plan", help="Write refresh plan to file"),
    apply: bool = typer.Option(False, "--apply", help="Apply the refresh plan"),
) -> None:
    """Score, plan, and optionally apply AAIS-style doc refresh."""
    reg = _ensure_registry()
    skill = reg.resolve("doc.refresh.agent")
    if skill is None:
        typer.echo("doc.refresh.agent skill not registered; run discovery first.", err=True)
        raise typer.Exit(1)

    envelope = ExecutionEnvelope(reg)
    result = envelope.run(
        "doc.refresh.agent",
        payload={
            "paths": paths,
            "style": style,
            "prune_stale": prune_stale,
            "actions": ["score", "plan"] + (["apply"] if apply else []),
        },
    )

    if result.status == "error":
        typer.echo(f"Refresh failed: {result.error}", err=True)
        raise typer.Exit(1)

    if emit_plan:
        Path(emit_plan).write_text(json.dumps(result.data, indent=2), encoding="utf-8")
        typer.echo(f"Plan written to: {emit_plan}")
    else:
        typer.echo(json.dumps(result.data, indent=2))


# ---------------------------------------------------------------------------
# score
# ---------------------------------------------------------------------------


@app.command("score")
def cmd_score(
    skill_id: str = typer.Option(..., "--skill", "-s", help="Skill id to score"),
    emit: Optional[str] = typer.Option(None, "--emit", "-e", help="Write score JSON to file"),
) -> None:
    """Compute AAIS score for a skill's documentation."""
    reg = _ensure_registry()
    skill = reg.resolve(skill_id)
    if skill is None:
        typer.echo(f"Skill '{skill_id}' not found.", err=True)
        raise typer.Exit(1)

    scorer = AAISScorer()

    # Score the manifest description + doc metadata as representative text
    content = "\n\n".join(
        filter(
            None,
            [
                skill.manifest.name,
                skill.manifest.description,
                " ".join(skill.manifest.capability_tags),
                skill.source_path,
            ],
        )
    )
    aais_result = scorer.score(content)

    score_data = {
        "skill_id": skill_id,
        "version": skill.version,
        "aais_score": aais_result.total,
        "dimensions": {
            "concision": aais_result.concision,
            "acronym_discipline": aais_result.acronym_discipline,
            "structure": aais_result.structure,
            "clarity": aais_result.clarity,
            "citation_lineage": aais_result.citation_lineage,
        },
    }

    if emit:
        Path(emit).write_text(json.dumps(score_data, indent=2), encoding="utf-8")
        typer.echo(f"Score written to: {emit}")
    else:
        typer.echo(json.dumps(score_data, indent=2))


# ---------------------------------------------------------------------------
# telemetry push
# ---------------------------------------------------------------------------


@telemetry_app.command("push")
def cmd_telemetry_push(
    from_path: str = typer.Option("logs/skill_events.jsonl", "--from", help="Source JSONL file"),
    to: str = typer.Option("file", "--to", help="Destination: file|app|discussions"),
    summary: bool = typer.Option(False, "--summary", help="Print summary table"),
    app_endpoint: str = typer.Option(
        "",
        "--app-endpoint",
        help="App ingest URL (required when --to=app)",
        envvar="CODEX_SKILL_APP_ENDPOINT",
    ),
) -> None:
    """Push telemetry events from a JSONL log to a destination."""
    events = read_events(Path(from_path))
    if not events:
        typer.echo("No events found in log.")
        return

    if summary:
        s = summarise_events(events)
        typer.echo(
            f"Total: {s['total']}  OK: {s['ok']}  Error: {s['error']}\n"
            f"Skills: {', '.join(s['skills'])}\n"
            f"Avg latency: {s['avg_latency_ms']}ms  "
            f"Avg AAIS: {s['avg_aais_score']}"
        )

    if to == "app":
        if not app_endpoint:
            typer.echo("--app-endpoint is required when --to=app", err=True)
            raise typer.Exit(1)
        push_to_app(events, app_endpoint)
    elif to == "discussions":
        typer.echo("Discussions push not implemented; use GitHub API directly.")
    else:
        typer.echo(f"Events read: {len(events)} records from '{from_path}'")


# ---------------------------------------------------------------------------
# ff  (fast-forward safe files to main)
# ---------------------------------------------------------------------------


@app.command("ff")
def cmd_ff(
    pr: int = typer.Option(..., "--pr", "-p", help="PR number to promote safe files FROM"),
    target: str = typer.Option("main", "--target", "-t", help="Branch to promote INTO"),
    files: Optional[str] = typer.Option(
        None,
        "--files",
        "-f",
        help="Comma-separated file paths (blank = use full allowlist)",
    ),
    merge_mode: str = typer.Option(
        "create-pr",
        "--merge-mode",
        "-m",
        help="create-pr (default, safe) | direct-push (admin only)",
    ),
    dry_run: bool = typer.Option(True, "--dry-run/--no-dry-run", help="Preview only (default: ON)"),
    repo: str = typer.Option(
        "",
        "--repo",
        "-r",
        envvar="GITHUB_REPOSITORY",
        help="owner/repo  (default: $GITHUB_REPOSITORY)",
    ),
    token: str = typer.Option(
        "",
        "--token",
        envvar="GITHUB_TOKEN",
        help="GitHub PAT  (default: $GITHUB_TOKEN)",
    ),
    emit: Optional[str] = typer.Option(None, "--emit", "-e", help="Write JSON result to file"),
) -> None:
    """Fast-forward pre-approved safe files from a PR directly to main.

    Files that ONLY take effect from the default branch (workflow schedules,
    ``workflow_run`` triggers, ``workflow_dispatch`` UI buttons) can be promoted
    immediately without waiting for the full PR merge cycle.

    The allowlist lives in ``.codex/fast_forward_allowlist.yaml``.

    Examples::

        # Preview what would be promoted from PR #3856
        codex-skill ff --pr 3856 --dry-run

        # Promote only specific files (creates a new PR against main)
        codex-skill ff --pr 3856 --no-dry-run \\
            --files .github/workflows/proactive-ci-monitor.yml

        # Direct-push to main (admin token required)
        codex-skill ff --pr 3856 --no-dry-run --merge-mode direct-push
    """
    if not _FF_SCRIPT.exists():
        typer.echo(
            "fast_forward_safe_files.py not found at expected path. Run from the repository root.",
            err=True,
        )
        raise typer.Exit(1)

    # Lazy-import to keep startup fast when FF is not needed
    import importlib.util

    spec = importlib.util.spec_from_file_location("fast_forward_safe_files", _FF_SCRIPT)
    ff_mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(ff_mod)  # type: ignore[union-attr]

    if not repo:
        typer.echo("--repo is required (or set GITHUB_REPOSITORY)", err=True)
        raise typer.Exit(1)
    if not token:
        typer.echo("--token is required (or set GITHUB_TOKEN)", err=True)
        raise typer.Exit(1)

    force_files = [f.strip() for f in files.split(",")] if files else None

    plan = ff_mod.build_plan(repo, token, pr, target, merge_mode, force_files)

    # Always show the plan
    typer.echo(f"\n{'─' * 60}")
    typer.echo(f"  Fast-Forward Plan — PR #{pr}  ({plan.pr_branch}@{plan.source_sha[:8]})")
    typer.echo(f"  Target: {target}   Mode: {merge_mode}   Dry-run: {dry_run}")
    typer.echo(f"{'─' * 60}")
    typer.echo(f"  ✅ Allowed  ({len(plan.allowed):>3}): " + (", ".join(plan.allowed[:5]) or "—"))
    if len(plan.allowed) > 5:
        typer.echo(f"               … and {len(plan.allowed) - 5} more")
    typer.echo(
        f"  ⏭️  Excluded ({len(plan.excluded):>3}): " + (", ".join(plan.excluded[:3]) or "—")
    )
    typer.echo(f"  🚫 Denied   ({len(plan.denied):>3}): " + (", ".join(plan.denied) or "—"))
    typer.echo(f"{'─' * 60}\n")

    if dry_run:
        typer.echo("🔕 DRY-RUN: no changes made. Pass --no-dry-run to apply.")
        result = {
            "status": "dry-run",
            "would_promote": plan.allowed,
            "would_exclude": plan.excluded,
            "would_deny": plan.denied,
        }
    else:
        if not plan.allowed:
            typer.echo("Nothing to promote after allowlist filtering.")
            raise typer.Exit(0)

        if plan.denied:
            typer.echo(f"⚠️  {len(plan.denied)} file(s) are deny-listed and will NOT be promoted.")

        confirm = typer.confirm(
            f"Promote {len(plan.allowed)} file(s) to '{target}' via {merge_mode}?",
            default=False,
        )
        if not confirm:
            typer.echo("Cancelled.")
            raise typer.Exit(0)

        result = ff_mod.execute_plan(repo, token, plan)
        status = result.get("status", "unknown")
        if status == "pr-created":
            typer.echo(
                f"✅ Fast-forward PR created: "
                f"#{result['fast_forward_pr']}  {result['fast_forward_pr_url']}"
            )
        elif status == "direct-pushed":
            typer.echo(
                f"🚀 Direct-pushed to {result['target_branch']}  "
                f"(new SHA: {result.get('new_sha', '?')[:8]})"
            )
        else:
            typer.echo(f"Status: {status}")

    if emit:
        Path(emit).write_text(json.dumps(result, indent=2), encoding="utf-8")
        typer.echo(f"Result written to: {emit}")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def main() -> None:
    app()


if __name__ == "__main__":
    main()
