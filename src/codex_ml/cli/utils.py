"""Shared CLI utilities for _codex_ minimal workflows."""

from __future__ import annotations

import datetime as _dt
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

from codex_ml.utils import reproducibility as _repro  # type: ignore[attr-defined]


@dataclass
class RunContext:
    """Lightweight run context information for CLIs."""

    run_id: str
    run_dir: str
    seed: int
    created_at: str
    config_path: str
    mode: str  # "train" or "eval"


def load_yaml_config(path: Path) -> dict[str, Any]:
    """Load a YAML configuration file, returning an empty dict if missing."""

    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Config at {path} must be a mapping")
    return data


def create_run_dir(base_dir: Path, mode: str, seed: int) -> RunContext:
    """Create a timestamped run directory and return a RunContext."""

    base_dir = base_dir.expanduser().resolve()
    now = _dt.datetime.now(_dt.UTC).replace(microsecond=0).isoformat().replace(":", "-")
    run_id = f"{now}_seed{seed}"
    run_dir = base_dir / mode / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    _repro.set_global_seed(seed)
    return RunContext(
        run_id=run_id,
        run_dir=str(run_dir),
        seed=seed,
        created_at=now,
        config_path="",
        mode=mode,
    )


def write_run_manifest(ctx: RunContext, config: dict[str, Any]) -> None:
    """Write a small run manifest file into the run directory."""

    run_dir = Path(ctx.run_dir)
    manifest = {
        "context": asdict(ctx),
        "config": config,
    }
    out = run_dir / "run_manifest.yaml"
    out.write_text(yaml.safe_dump(manifest), encoding="utf-8")

    # Append an index entry for quick inspection
    index = run_dir.parent.parent / "runs_index.txt"
    line = f"{ctx.mode}\t{ctx.run_id}\t{ctx.run_dir}\n"
    with index.open("a", encoding="utf-8") as f:
        f.write(line)
