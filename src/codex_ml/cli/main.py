# BEGIN: HYDRA_CLI_MAIN
"""Hydra CLI entrypoint for codex_ml.
Supports overrides, e.g.:
  python -m codex_ml.cli.main +dry_run=true train.epochs=2 tokenizer.name=gpt2
"""
from __future__ import annotations
import sys
from pathlib import Path
import hydra
from omegaconf import DictConfig, OmegaConf

REPO = Path(__file__).resolve().parents[3]
CODEX = REPO / ".codex"
(HY_OUT := CODEX / "hydra_last").mkdir(parents=True, exist_ok=True)

def _log(msg: str) -> None:
    print(msg, flush=True)

def _save_effective_cfg(cfg: DictConfig, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(OmegaConf.to_yaml(cfg))

def _dispatch_pipeline(cfg: DictConfig) -> int:
    for step in list(cfg.pipeline.steps):
        _log(f"[pipeline] step={step} dry_run={cfg.dry_run}")
        if cfg.dry_run:
            continue
        # TODO: Implement real step handlers; here we simulate success
    return 0

@hydra.main(version_base="1.3", config_path="../../../configs", config_name="config")
def main(cfg: DictConfig) -> None:
    _log("[hydra] composed config:\n" + OmegaConf.to_yaml(cfg))
    _save_effective_cfg(cfg, HY_OUT / "config.yaml")
    rc = _dispatch_pipeline(cfg)
    sys.exit(rc)

if __name__ == "__main__":
    main()
