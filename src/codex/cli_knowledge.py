"""
Cli Knowledge Module

This module provides functionality for cli knowledge.

Usage:
    from codex.cli_knowledge import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import json
from pathlib import Path

import typer
from codex.knowledge.build import archive_and_manifest, build_kb
from codex.release.api import pack_release, verify_bundle

DEFAULT_ROOT = Path("docs")
DEFAULT_KB_OUT = Path("artifacts/kb.ndjsonl")
DEFAULT_MANIFEST = Path("artifacts/knowledge.release.manifest.json")
DEFAULT_STAGING = Path("work/knowledge_staging")
DEFAULT_BUNDLE = Path("dist/codex-knowledge.tar.gz")

ROOT_OPTION = typer.Option(DEFAULT_ROOT, "--root")
OUT_OPTION = typer.Option(DEFAULT_KB_OUT, "--out")
ALLOW_GPL_OPTION = typer.Option(False, "--allow-gpl/--no-allow-gpl")
MAX_TOKENS_OPTION = typer.Option(2048, "--max-tokens")
DEDUP_OPTION = typer.Option(True, "--dedup/--no-dedup")
KB_ARGUMENT = typer.Argument(DEFAULT_KB_OUT, exists=True)
INSTRUCTIONS_OPTION = typer.Option(None, "--instructions")
EVAL_OPTION = typer.Option(None, "--eval")
ACTOR_OPTION = typer.Option("codex", "--by")
MANIFEST_ARGUMENT = typer.Argument(DEFAULT_MANIFEST, exists=True)
STAGING_OPTION = typer.Option(DEFAULT_STAGING, "--staging")
BUNDLE_OPTION = typer.Option(DEFAULT_BUNDLE, "--out")

app = typer.Typer(help="Codex Knowledge (ingest → normalize → chunk → build)")


@app.command("build-kb")
def build_kb_cmd(
    root: Path = ROOT_OPTION,
    out: Path = OUT_OPTION,
    allow_gpl: bool = ALLOW_GPL_OPTION,
    max_tokens: int = MAX_TOKENS_OPTION,
    dedup: bool = DEDUP_OPTION,
) -> None:
    res = build_kb(
        root,
        out,
        allow_gpl=allow_gpl,
        max_tokens_per_rec=max_tokens,
        dedup=dedup,
    )
    typer.echo(json.dumps(res, indent=2))


@app.command("archive-and-manifest")
def archive_and_manifest_cmd(
    kb: Path = KB_ARGUMENT,
    instructions: Path | None = INSTRUCTIONS_OPTION,
    evl: Path | None = EVAL_OPTION,
    by: str = ACTOR_OPTION,
) -> None:
    res = archive_and_manifest(kb, instructions, evl, actor=by)
    typer.echo(json.dumps(res, indent=2))


@app.command("pack-release")
def pack_release_cmd(
    manifest: Path = MANIFEST_ARGUMENT,
    staging: Path = STAGING_OPTION,
    out_bundle: Path = BUNDLE_OPTION,
) -> None:
    bundle, locked = pack_release(manifest, staging, out_bundle)
    v = verify_bundle(bundle)
    typer.echo(
        json.dumps(
            {
                "bundle": bundle.as_posix(),
                "sha256_manifest": locked["checks"]["sha256_manifest"],
                "verified": v["ok"],
            },
            indent=2,
        )
    )
