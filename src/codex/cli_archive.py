from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Any

from codex.archive.api import restore, store

if TYPE_CHECKING:  # pragma: no cover - typing only
    Option = Any
    Typer = Any

    def echo(value: str) -> None: ...

else:
    from typer import Option, Typer, echo

app = Typer(help="Codex Archive (tombstone) CLI")

DEFAULT_STDOUT_PATH = Path("-")


@app.command("store")
def cmd_store(
    repo: str,
    filepath: Path,
    reason: Annotated[str, Option("--reason", "-r")] = "dead",
    by: Annotated[str, Option("--by")] = "codex",
    commit: Annotated[str, Option("--commit")] = "HEAD",
    mime: Annotated[str, Option("--mime")] = "text/plain",
    lang: Annotated[str, Option("--lang")] = "",
) -> None:
    b = filepath.read_bytes()
    out = store(
        repo=repo,
        path=str(filepath),
        by=by,
        reason=reason,
        commit_sha=commit,
        bytes_in=b,
        mime=mime,
        lang=lang or None,
    )
    echo(json.dumps(out, indent=2))


@app.command("restore")
def cmd_restore(
    tombstone: str,
    out_path: Annotated[Path, Option("--out")] = DEFAULT_STDOUT_PATH,
) -> None:
    obj = restore(tombstone)
    if out_path.as_posix() == "-":
        echo(json.dumps({"path": obj["path"], "bytes_len": len(obj["bytes"])}, indent=2))
    else:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(obj["bytes"])
        echo(out_path.as_posix())
