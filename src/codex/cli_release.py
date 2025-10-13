from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from codex.release.api import pack_release, unpack_bundle, verify_bundle

DEFAULT_MANIFEST = Path("release.manifest.json")
DEFAULT_STAGING = Path("work/release_staging")
DEFAULT_BUNDLE = Path("dist/codex-release.tar.gz")
DEFAULT_DEST = Path("/opt/codex/app")

app = typer.Typer(help="Codex Release (offline pack/verify/unpack)")


@app.command("init-manifest")
def cmd_init_manifest(
    out: Annotated[Path, typer.Argument()] = DEFAULT_MANIFEST,
) -> None:
    out.write_text(
        json.dumps(
            {
                "release_id": "codex-YYYY.MM.DD-r01",
                "version": "vYYYY.MM.DD",
                "created_at": "YYYY-MM-DDTHH:MM:SSZ",
                "actor": "marc",
                "target": {"platforms": ["linux/amd64"], "apps": []},
                "components": [
                    {
                        "tombstone": "<uuid>",
                        "dest_path": "bin/codex-cli",
                        "mode": "0755",
                        "type": "file",
                    },
                ],
                "symlinks": [],
                "post_unpack_commands": [],
                "checks": {"sha256_manifest": "<filled at pack time>"},
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    typer.echo(out.as_posix())


@app.command("pack")
def cmd_pack(
    manifest: Annotated[Path, typer.Argument(exists=True)] = DEFAULT_MANIFEST,
    staging: Annotated[Path, typer.Option("--staging")] = DEFAULT_STAGING,
    out_bundle: Annotated[Path, typer.Option("--out")] = DEFAULT_BUNDLE,
) -> None:
    bundle, locked = pack_release(manifest, staging, out_bundle)
    typer.echo(
        json.dumps(
            {
                "bundle": bundle.as_posix(),
                "locked": {"sha256_manifest": locked["checks"]["sha256_manifest"]},
            },
            indent=2,
        )
    )


@app.command("verify")
def cmd_verify(
    bundle: Annotated[Path, typer.Argument(exists=True)] = DEFAULT_BUNDLE,
) -> None:
    res = verify_bundle(bundle)
    typer.echo(json.dumps(res, indent=2))


@app.command("unpack")
def cmd_unpack(
    bundle: Annotated[Path, typer.Argument(exists=True)] = DEFAULT_BUNDLE,
    dest: Annotated[Path, typer.Option("--dest")] = DEFAULT_DEST,
    allow_scripts: Annotated[bool, typer.Option("--allow-scripts/--no-allow-scripts")] = False,
) -> None:
    d = unpack_bundle(bundle, dest, allow_scripts=allow_scripts)
    typer.echo(json.dumps({"dest": d.as_posix()}, indent=2))
