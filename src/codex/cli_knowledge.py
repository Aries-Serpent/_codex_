from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from codex.knowledge.build import archive_and_manifest, build_kb
from codex.release.api import pack_release, verify_bundle

DEFAULT_ROOT = Path("docs")
DEFAULT_KB_OUT = Path("artifacts/kb.ndjsonl")
DEFAULT_MANIFEST = Path("artifacts/knowledge.release.manifest.json")
DEFAULT_STAGING = Path("work/knowledge_staging")
DEFAULT_BUNDLE = Path("dist/codex-knowledge.tar.gz")

ROOT_OPTION = typer.Option(
    DEFAULT_ROOT,
    "--root",
    help="Docs root to scan (.md/.txt/.html/.pdf)",
)
OUT_OPTION = typer.Option(DEFAULT_KB_OUT, "--out")
ALLOW_GPL_OPTION = typer.Option(False, "--allow-gpl/--no-allow-gpl")
MAX_TOKENS_OPTION = typer.Option(2048, "--max-tokens")
KB_ARGUMENT = typer.Argument(DEFAULT_KB_OUT, exists=True)
INSTRUCTIONS_OPTION = typer.Option(
    None,
    "--instructions",
    help="Optional NDJSONL of instruction tasks",
)
EVAL_OPTION = typer.Option(None, "--eval", help="Optional NDJSONL of eval tasks")
ACTOR_OPTION = typer.Option("codex", "--by")
MANIFEST_ARGUMENT = typer.Argument(DEFAULT_MANIFEST, exists=True)
STAGING_OPTION = typer.Option(DEFAULT_STAGING, "--staging")
BUNDLE_OPTION = typer.Option(DEFAULT_BUNDLE, "--out")

app = typer.Typer(help="Codex Knowledge (ingest → normalize → chunk → build)")


@app.command("build-kb")
def cmd_build_kb(
    root: Annotated[Path, ROOT_OPTION] = DEFAULT_ROOT,
    out: Annotated[Path, OUT_OPTION] = DEFAULT_KB_OUT,
    allow_gpl: Annotated[bool, ALLOW_GPL_OPTION] = False,
    max_tokens: Annotated[int, MAX_TOKENS_OPTION] = 2048,
) -> None:
    result = build_kb(root, out, allow_gpl=allow_gpl, max_tokens_per_rec=max_tokens)
    typer.echo(json.dumps(result, indent=2))


@app.command("archive-and-manifest")
def cmd_archive_and_manifest(
    kb: Annotated[Path, KB_ARGUMENT] = DEFAULT_KB_OUT,
    instructions: Annotated[Path | None, INSTRUCTIONS_OPTION] = None,
    evl: Annotated[Path | None, EVAL_OPTION] = None,
    actor: Annotated[str, ACTOR_OPTION] = "codex",
) -> None:
    result = archive_and_manifest(kb, instructions, evl, actor=actor)
    typer.echo(json.dumps(result, indent=2))


@app.command("pack-release")
def cmd_pack_release(
    manifest: Annotated[Path, MANIFEST_ARGUMENT] = DEFAULT_MANIFEST,
    staging: Annotated[Path, STAGING_OPTION] = DEFAULT_STAGING,
    out_bundle: Annotated[Path, BUNDLE_OPTION] = DEFAULT_BUNDLE,
) -> None:
    bundle, locked = pack_release(manifest, staging, out_bundle)
    verify = verify_bundle(bundle)
    payload = {
        "bundle": bundle.as_posix(),
        "sha256_manifest": locked["checks"]["sha256_manifest"],
        "verified": verify["ok"],
    }
    typer.echo(json.dumps(payload, indent=2))
