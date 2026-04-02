"""Cognitive Brain Skills CLI.

Entry point: ``codex-skill`` (registered in pyproject.toml).

Sub-commands
------------
list        List registered skills with optional filters.
run         Invoke a skill by id with a JSON payload.
compress    Package a skill directory into a .7z / .zip archive.
install     Extract and register a skill archive.
refresh-docs  Score, plan, and optionally apply AAIS-style doc refresh.
score       Compute AAIS score for a skill's documentation.
telemetry   Push telemetry events from a JSONL log.

Usage::

    codex-skill list
    codex-skill list --capability docs --risk-tier low
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
import sys
from pathlib import Path
from typing import Optional

import typer

from .aais import AAISScorer
from .compression import compress_skill, install_skill
from .envelope import ExecutionEnvelope
from .registry import SkillRegistry, get_registry
from .routing import StratifiedRouter
from .telemetry import push_to_app, read_events, summarise_events

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
    capability: Optional[str] = typer.Option(None, "--capability", "-c", help="Filter by capability tag"),
    risk_tier: Optional[str] = typer.Option(None, "--risk-tier", "-r", help="Filter by risk tier (low|medium|high)"),
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
        payload_data: dict = json.loads(path.read_text(encoding="utf-8"))
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
    prune_stale: bool = typer.Option(False, "--prune-stale", help="Remove docs scoring below threshold"),
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
    content = "\n\n".join(filter(None, [
        skill.manifest.name,
        skill.manifest.description,
        " ".join(skill.manifest.capability_tags),
        skill.source_path,
    ]))
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
# Main entry point
# ---------------------------------------------------------------------------

def main() -> None:
    app()


if __name__ == "__main__":
    main()
