"""Capture light-weight provenance information for training runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

__all__ = ["snapshot_hydra_config"]


def snapshot_hydra_config(config: Mapping[str, object], output_dir: Path | str) -> Path:
    target = Path(output_dir) / "hydra_config.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(dict(config), indent=2, sort_keys=True), encoding="utf-8")
    return target
