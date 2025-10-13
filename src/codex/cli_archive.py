from __future__ import annotations

import json
import os
from pathlib import Path

import click

from codex.archive.api import (
    db_check as archive_db_check,
    insert_referent,
    recent_tombstones,
    restore,
    store,
    summarize as archive_summarize,
)
from codex.archive.consolidate import build_consolidation_plan
from codex.archive.detect import stat_file
from codex.archive.plan import build_plan
from codex.archive.shims import (
    write_csv_pointer,
    write_json_pointer,
    write_markdown_pointer,
    write_python_shim,
)
from codex.archive.stub import make_stub_text
from codex.archive.util import append_evidence, sha256_file, utcnow_iso


@click.group(help="Codex Archive (tombstone) CLI")
def app() -> None:
    """Entry point for archive operations."""


@app.command("store")
@click.argument("repo")
@click.argument("filepath", type=click.Path(path_type=Path, exists=True, dir_okay=False))
@click.option("--reason", "-r", default="dead", show_default=True)
@click.option("--by", "actor", default="codex", show_default=True)
@click.option("--commit", default="HEAD", show_default=True)
@click.option("--mime", default="text/plain", show_default=True)
@click.option("--lang", default="", show_default=True)
def cmd_store(
    repo: str,
    filepath: Path,
    reason: str,
    actor: str,
    commit: str,
    mime: str,
    lang: str,
) -> None:
    payload = store(
        repo=repo,
        path=str(filepath),
        by=actor,
        reason=reason,
        commit_sha=commit,
        bytes_in=filepath.read_bytes(),
        mime=mime,
        lang=lang or None,
    )
    click.echo(json.dumps(payload, indent=2))


@app.command("restore")
@click.argument("tombstone")
@click.option("--out", "out_path", type=click.Path(path_type=Path), default="-", show_default=True)
def cmd_restore(tombstone: str, out_path: Path) -> None:
    obj = restore(tombstone)
    if out_path.as_posix() == "-":
        click.echo(
            json.dumps(
                {
                    "path": obj["path"],
                    "bytes_len": len(obj["bytes"]),
                    "sha256": obj.get("sha256"),
                },
                indent=2,
            )
        )
    else:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(obj["bytes"])
        click.echo(out_path.as_posix())


@app.command("plan")
@click.option("--out", "out_file", type=click.Path(path_type=Path), default=Path("artifacts/archive_plan.json"), show_default=True)
@click.option("--sha", "analyze_sha", default="HEAD", show_default=True)
@click.option("--age", "age_days", default=180, show_default=True)
@click.option(
    "--root",
    type=click.Path(path_type=Path, exists=True, dir_okay=True, file_okay=False),
    default=Path("."),
    show_default=True,
)
@click.option(
    "--exclude",
    multiple=True,
    default=("**/.codex/**", "**/.git/**", "**/artifacts/**", "**/__pycache__/**"),
    show_default=True,
)
def cmd_plan(
    out_file: Path,
    analyze_sha: str,
    age_days: int,
    root: Path,
    exclude: tuple[str, ...],
) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    plan = build_plan(
        root,
        analyze_sha=analyze_sha,
        excludes=exclude,
        age_days_threshold=age_days,
    )
    out_file.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    append_evidence(
        {
            "action": "PLAN_GENERATED",
            "plan": out_file.as_posix(),
            "plan_sha256": sha256_file(out_file),
        }
    )
    click.echo(out_file.as_posix())


@app.command("apply-plan")
@click.argument(
    "plan_file",
    type=click.Path(path_type=Path, exists=True, dir_okay=False),
)
@click.option("--repo", default="_codex_", show_default=True)
@click.option("--by", "actor", default="codex", show_default=True)
@click.option("--write-stubs/--no-write-stubs", default=True, show_default=True)
def cmd_apply_plan(
    plan_file: Path,
    repo: str,
    actor: str,
    write_stubs: bool,
) -> None:
    data = json.loads(plan_file.read_text(encoding="utf-8"))
    results: list[dict[str, object]] = []
    for entry in data.get("entries", []):
        path = Path(entry["path"])
        if not path.exists():
            results.append(
                {
                    "path": entry["path"],
                    "skipped": True,
                    "reason": "missing",
                }
            )
            continue
        meta = stat_file(path)
        stored = store(
            repo=repo,
            path=str(path),
            by=actor,
            reason=entry.get("reason", "dead"),
            commit_sha=entry.get("commit_sha", "HEAD"),
            bytes_in=path.read_bytes(),
            mime=meta.mime,
            lang=meta.lang,
        )
        if write_stubs:
            stub = make_stub_text(
                path=str(path),
                actor=actor,
                reason=entry.get("reason", "dead"),
                tombstone=stored["tombstone"],
                sha256=stored["sha256"],
                commit=entry.get("commit_sha", "HEAD"),
            )
            path.write_text(stub, encoding="utf-8")
        append_evidence(
            {
                "action": "PLAN_APPLY",
                "path": entry["path"],
                "tombstone": stored["tombstone"],
                "reason": entry.get("reason", "dead"),
                "repo": repo,
            }
        )
        results.append(
            {
                "path": entry["path"],
                "tombstone": stored["tombstone"],
                "sha256": stored["sha256"],
            }
        )
    click.echo(json.dumps({"applied": results, "ts": utcnow_iso()}, indent=2))


@app.command("consolidate-plan")
@click.option("--out", "out_file", type=click.Path(path_type=Path), default=Path("artifacts/consolidation_plan.json"), show_default=True)
@click.option(
    "--root",
    type=click.Path(path_type=Path, exists=True, dir_okay=True, file_okay=False),
    default=Path("."),
    show_default=True,
)
@click.option(
    "--exclude",
    multiple=True,
    default=(
        "**/.codex/**",
        "**/.git/**",
        "**/artifacts/**",
        "**/__pycache__/**",
        "**/.venv/**",
    ),
    show_default=True,
)
@click.option("--jaccard-min", default=0.92, show_default=True)
@click.option("--hd-max", default=3, show_default=True)
def cmd_consolidate_plan(
    out_file: Path,
    root: Path,
    exclude: tuple[str, ...],
    jaccard_min: float,
    hd_max: int,
) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    plan = build_consolidation_plan(
        root,
        excludes=exclude,
        jaccard_min=jaccard_min,
        hd_max=hd_max,
    )
    out_file.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    append_evidence(
        {
            "action": "CONSOLIDATE_PLAN",
            "plan": out_file.as_posix(),
            "plan_sha256": sha256_file(out_file),
        }
    )
    click.echo(out_file.as_posix())


@app.command("consolidate-apply")
@click.argument(
    "plan_file",
    type=click.Path(path_type=Path, exists=True, dir_okay=False),
)
@click.option("--repo", default="_codex_", show_default=True)
@click.option("--by", "actor", default="codex", show_default=True)
@click.option("--write-shims/--no-write-shims", default=True, show_default=True)
def cmd_consolidate_apply(
    plan_file: Path,
    repo: str,
    actor: str,
    write_shims: bool,
) -> None:
    data = json.loads(plan_file.read_text(encoding="utf-8"))
    clusters = data.get("clusters", [])
    applied: list[dict[str, object]] = []
    for cluster in clusters:
        canonical_path = cluster.get("canonical", {}).get("path")
        if not canonical_path:
            continue
        canonical = Path(canonical_path)
        canonical_import: str | None = None
        if canonical.suffix == ".py" and "src" in canonical.parts:
            parts = list(canonical.parts)
            idx = parts.index("src")
            module_parts = Path(*parts[idx + 1 :]).with_suffix("")
            canonical_import = ".".join(module_parts.parts)
        for dup in cluster.get("duplicates", []):
            dup_path = Path(dup.get("path", ""))
            if not dup_path.exists():
                applied.append(
                    {
                        "path": dup_path.as_posix(),
                        "skipped": True,
                        "reason": "missing",
                    }
                )
                continue
            meta = stat_file(dup_path)
            stored = store(
                repo=repo,
                path=str(dup_path),
                by=actor,
                reason="duplicate",
                commit_sha="HEAD",
                bytes_in=dup_path.read_bytes(),
                mime=meta.mime,
                lang=meta.lang,
            )
            insert_referent(
                tombstone=stored["tombstone"],
                ref_type="canonical_path",
                ref_value=canonical_path,
            )
            append_evidence(
                {
                    "action": "CONSOLIDATE_APPLY",
                    "duplicate": dup_path.as_posix(),
                    "canonical": canonical_path,
                    "tombstone": stored["tombstone"],
                    "similarity": dup.get("similarity", {}),
                }
            )
            if write_shims:
                rel_path = os.path.relpath(canonical_path, start=str(dup_path.parent))
                if dup_path.suffix == ".py" and canonical_import:
                    write_python_shim(dup_path, canonical_import)
                elif dup_path.suffix in {".md", ".txt"}:
                    write_markdown_pointer(dup_path, rel_path)
                elif dup_path.suffix == ".json":
                    write_json_pointer(dup_path, rel_path)
                elif dup_path.suffix == ".csv":
                    write_csv_pointer(dup_path, rel_path)
                else:
                    stub = make_stub_text(
                        path=str(dup_path),
                        actor=actor,
                        reason="duplicate",
                        tombstone=stored["tombstone"],
                        sha256=stored["sha256"],
                        commit="HEAD",
                    )
                    dup_path.write_text(stub, encoding="utf-8")
            applied.append(
                {
                    "path": dup_path.as_posix(),
                    "tombstone": stored["tombstone"],
                    "canonical": canonical_path,
                }
            )
    click.echo(json.dumps({"applied": applied, "ts": utcnow_iso()}, indent=2))


@app.command("db-check")
def cmd_db_check() -> None:
    payload = archive_db_check()
    payload["ts"] = utcnow_iso()
    append_evidence({"action": "DB_CHECK", **payload})
    click.echo(json.dumps(payload, indent=2))


@app.command("summarize")
def cmd_summarize() -> None:
    payload = archive_summarize()
    payload["ts"] = utcnow_iso()
    append_evidence({"action": "SUMMARY", **payload})
    click.echo(json.dumps(payload, indent=2))


@app.command("verify-restore")
@click.option("--n", "sample", default=5, show_default=True)
def cmd_verify_restore(sample: int) -> None:
    rows = recent_tombstones(sample)
    verified: list[dict[str, object]] = []
    matches = 0
    for row in rows:
        tombstone = row["tombstone"]
        restored = restore(tombstone)
        sha_match = restored.get("sha256") == row.get("sha256")
        if sha_match:
            matches += 1
        verified.append(
            {
                "tombstone": tombstone,
                "path": row.get("path"),
                "sha256_match": sha_match,
            }
        )
    append_evidence(
        {
            "action": "VERIFY_RESTORE",
            "sample": sample,
            "matches": matches,
            "checked": len(verified),
        }
    )
    click.echo(json.dumps({"verified": verified, "ts": utcnow_iso()}, indent=2))
