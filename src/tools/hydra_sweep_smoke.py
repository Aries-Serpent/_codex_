"""Compose Hydra configs for a minimal sweep and emit JSON artefacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

try:  # pragma: no cover - hydra optional
    from hydra import compose, initialize
    from omegaconf import OmegaConf
except Exception as exc:  # pragma: no cover - degrade gracefully
    raise RuntimeError("hydra-core and omegaconf are required for sweep smoke tests") from exc


def _load_definition(path: Path) -> dict[str, object]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in sweep config: {path}")
    return data


def run(config: Path) -> list[dict[str, object]]:
    definition = _load_definition(config)
    base = definition.get("base") or {}
    sweep = definition.get("sweep") or {}
    if not isinstance(base, dict) or not isinstance(sweep, dict):
        raise ValueError("'base' and 'sweep' sections must be mappings")

    config_name = base.get("config_name")
    if not isinstance(config_name, str):
        raise ValueError("base.config_name must be a string")
    base_overrides = list(base.get("overrides", []))
    sweep_overrides = list(sweep.get("overrides", []))

    artifacts = Path("artifacts/sweeps_smoke")
    artifacts.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, object]] = []

    with initialize(version_base="1.3", config_path="configs"):
        for idx, override in enumerate(sweep_overrides, start=1):
            overrides = base_overrides + [override]
            cfg = compose(config_name=config_name, overrides=overrides)
            payload = OmegaConf.to_container(cfg, resolve=True)
            out_path = artifacts / f"config_{idx}.json"
            out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            results.append({"index": idx, "overrides": overrides, "path": str(out_path)})

    summary_path = artifacts / "summary.json"
    summary_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compose a minimal Hydra sweep")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/sweeps/minimal.yaml"),
        help="Sweep definition YAML",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run(args.config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
