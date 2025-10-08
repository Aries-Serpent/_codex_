from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, Optional

try:  # pragma: no cover - optional dependency path
    import typer
except ModuleNotFoundError as exc:  # pragma: no cover - optional dependency path
    raise ImportError("typer is required for codex_ml.cli.detectors") from exc

if not hasattr(typer, "Typer"):  # pragma: no cover - optional dependency path
    raise ImportError("typer.Typer is required for codex_ml.cli.detectors")

from codex_ml.detectors import run_detectors
from codex_ml.detectors import unified_training
from codex_ml.detectors import core as det_core
from codex_ml.detectors.aggregate import aggregate, to_json_dict

app = typer.Typer(no_args_is_help=True, add_completion=False)


def _parse_weights(items: Iterable[str]) -> Dict[str, float]:
    out: Dict[str, float] = {}
    for it in items:
        name, _, val = it.partition("=")
        if not name or not val:
            raise typer.BadParameter(f"invalid weight '{it}', expected name=weight")
        try:
            out[name] = float(val)
        except ValueError as exc:
            raise typer.BadParameter(f"invalid weight '{it}', expected numeric weight") from exc
    return out


@app.command("run")
def run_cmd(
    manifest: Optional[Path] = typer.Option(
        None, "--manifest", "-m", help="Optional manifest JSON"
    ),
    out: Optional[Path] = typer.Option(None, "--out", "-o", help="Write scorecard JSON to file"),
    weight: Optional[list[str]] = typer.Option(None, "--weight", help="name=weight (can repeat)"),
) -> None:
    """Run selected detectors and print an aggregated scorecard as JSON."""

    detectors: list[det_core.Detector] = [unified_training.detect]
    manifest_data = None
    if manifest:
        manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
    results = run_detectors(detectors, manifest_data)
    weights = _parse_weights(weight or [])
    card = aggregate(results, weights=weights)
    js = json.dumps(to_json_dict(card), ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    if out:
        out.write_text(js + "\n", encoding="utf-8")
    typer.echo(js)


if __name__ == "__main__":  # pragma: no cover
    app()
