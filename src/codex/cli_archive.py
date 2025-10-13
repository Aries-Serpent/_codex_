from __future__ import annotations

import json
from pathlib import Path

import typer
from codex.archive.api import restore, store
from codex.archive.plan import build_plan
from codex.archive.stub import make_stub_text
from codex.archive.util import utcnow_iso

DEFAULT_PLAN_EXCLUDES = [
    "**/.codex/**",
    "**/artifacts/**",
    "**/.venv/**",
    "**/__pycache__/**",
]

PLAN_OUT_OPTION = typer.Option(Path("artifacts/archive_plan.json"), "--out")
PLAN_SHA_OPTION = typer.Option("HEAD", "--sha")
PLAN_AGE_OPTION = typer.Option(180, "--age", help="Age threshold in days")
PLAN_ROOT_OPTION = typer.Option(Path("."), "--root", dir_okay=True, file_okay=False, exists=True)
PLAN_EXCLUDE_OPTION = typer.Option(DEFAULT_PLAN_EXCLUDES, "--exclude")
PLAN_FILE_ARGUMENT = typer.Argument(Path("artifacts/archive_plan.json"), exists=True)
RESTORE_OUT_OPTION = typer.Option(Path("-"), "--out")

app = typer.Typer(help="Codex Archive (tombstone) CLI")


@app.command("plan")
def cmd_plan(
    out_file: Path = PLAN_OUT_OPTION,
    analyze_sha: str = PLAN_SHA_OPTION,
    age_days: int = PLAN_AGE_OPTION,
    root: Path = PLAN_ROOT_OPTION,
    exclude: list[str] = PLAN_EXCLUDE_OPTION,
) -> None:
    """Build an archive plan JSON by scanning the working tree."""
    out_file.parent.mkdir(parents=True, exist_ok=True)
    plan = build_plan(root, analyze_sha=analyze_sha, excludes=exclude, age_days_threshold=age_days)
    out_file.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    typer.echo(out_file.as_posix())


@app.command("apply-plan")
def cmd_apply_plan(
    plan_file: Path = PLAN_FILE_ARGUMENT,
    repo: str = typer.Option("_codex_", "--repo"),
    actor: str = typer.Option("codex", "--by"),
    write_stubs: bool = typer.Option(True, "--write-stubs/--no-write-stubs"),
) -> None:
    """Apply a plan: archive bytes then optionally write tombstone stubs."""
    data = json.loads(plan_file.read_text(encoding="utf-8"))
    entries = data.get("entries", [])
    results = []
    for entry in entries:
        path = Path(entry["path"])
        if not path.exists():
            results.append({"path": entry["path"], "skipped": True, "reason": "missing"})
            continue
        payload = path.read_bytes()
        out = store(
            repo=repo,
            path=str(path),
            by=actor,
            reason=entry.get("reason", "dead"),
            commit_sha=entry.get("commit_sha", "HEAD"),
            bytes_in=payload,
            mime=entry.get("mime", "application/octet-stream"),
            lang=entry.get("lang", "binary"),
        )
        if write_stubs:
            stub = make_stub_text(
                str(path),
                actor=actor,
                reason=entry.get("reason", "dead"),
                tombstone=out["tombstone"],
                sha256=out["sha256"],
                commit=entry.get("commit_sha", "HEAD"),
            )
            path.write_text(stub, encoding="utf-8")
        results.append(
            {"path": entry["path"], "tombstone": out["tombstone"], "sha256": out["sha256"]}
        )
    typer.echo(json.dumps({"applied": results, "ts": utcnow_iso()}, indent=2))


@app.command("store")
def cmd_store(
    repo: str,
    filepath: Path,
    reason: str = typer.Option("dead", "--reason", "-r"),
    by: str = typer.Option("codex", "--by"),
    commit: str = typer.Option("HEAD", "--commit"),
    mime: str = typer.Option("", "--mime", help="Auto-detect if empty"),
    lang: str = typer.Option("", "--lang", help="Auto-detect if empty"),
    write_stub: bool = typer.Option(
        False, "--write-stub/--no-write-stub", help="Write tombstone stub inline"
    ),
) -> None:
    payload = filepath.read_bytes()
    if not mime or not lang:
        from codex.archive.detect import detect_mime_lang

        detected_mime, detected_lang = detect_mime_lang(filepath)
        mime = mime or detected_mime
        lang = lang or detected_lang
    out = store(
        repo=repo,
        path=str(filepath),
        by=by,
        reason=reason,
        commit_sha=commit,
        bytes_in=payload,
        mime=mime or "application/octet-stream",
        lang=lang or "binary",
    )
    if write_stub:
        stub = make_stub_text(
            str(filepath),
            actor=by,
            reason=reason,
            tombstone=out["tombstone"],
            sha256=out["sha256"],
            commit=commit,
        )
        filepath.write_text(stub, encoding="utf-8")
    typer.echo(json.dumps(out, indent=2))


@app.command("restore")
def cmd_restore(
    tombstone: str,
    out_path: Path = RESTORE_OUT_OPTION,
) -> None:
    obj = restore(tombstone)
    if out_path.as_posix() == "-":
        typer.echo(json.dumps({"path": obj["path"], "bytes_len": len(obj["bytes"])}, indent=2))
    else:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(obj["bytes"])
        typer.echo(out_path.as_posix())
