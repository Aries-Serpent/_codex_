from __future__ import annotations

import json
import shutil
from pathlib import Path

import typer
from tokenizers import Tokenizer

app = typer.Typer(help="Tokenizer utilities")


def _load(path: Path) -> Tokenizer:
    return Tokenizer.from_file(str(path / "tokenizer.json"))


@app.command()
def inspect(path: Path) -> None:
    tk = _load(path)
    manifest_path = path / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    tokenizer_config = json.loads((path / "tokenizer.json").read_text())
    added_tokens = tokenizer_config.get("added_tokens", [])
    special_tokens = [item.get("content") for item in added_tokens if item.get("special")]
    typer.echo(f"vocab_size: {tk.get_vocab_size()}")
    typer.echo(f"special_tokens: {special_tokens}")
    cfg = manifest.get("config", {})
    pad = cfg.get("padding")
    trunc = cfg.get("truncation")
    max_len = cfg.get("max_length")
    typer.echo(f"padding: {pad} truncation: {trunc} max_length: {max_len}")


@app.command()
def encode(
    tokenizer_path: Path,
    text: str,
    from_file: bool = typer.Option(False, "--from-file", help="Treat TEXT as path"),
    show_ids: bool = typer.Option(True, help="Show token ids"),
    show_tokens: bool = typer.Option(False, help="Show decoded tokens"),
) -> None:
    tk = _load(tokenizer_path)
    if from_file:
        text = Path(text).read_text()
    enc = tk.encode(text)
    if show_ids:
        typer.echo("ids: " + " ".join(str(i) for i in enc.ids))
    if show_tokens:
        typer.echo("tokens: " + " ".join(enc.tokens))


@app.command()
def export(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for name in ("tokenizer.json", "manifest.json", "spm.model", "spm.vocab"):
        p = src / name
        if p.exists():
            shutil.copy2(p, dst / name)
    manifest_path = src / "manifest.json"
    readme = dst / "README.md"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        readme.write_text(
            "# Tokenizer Export\n\n````json\n" + json.dumps(manifest, indent=2) + "\n````\n"
        )
    else:
        readme.write_text("# Tokenizer Export\n")


if __name__ == "__main__":
    app()
