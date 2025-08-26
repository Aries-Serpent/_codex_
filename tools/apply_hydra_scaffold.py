#!/usr/bin/env python3
"""
Codex Orchestrator: Hydra Configs + CLI Entrypoint

Delivers:
- configs/config.yaml + configs/env/ubuntu.yaml
- codex_ml/cli/main.py with @hydra.main dispatcher
- README.md and deploy_codex_pipeline.py notes
- Validation and logs in .codex/

Policy: DO NOT ACTIVATE ANY GitHub Actions Online files.
All checks (pre-commit, validation, etc.) must run explicitly within the Codex environment.
"""

from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CODEX = REPO / ".codex"
CODEX.mkdir(parents=True, exist_ok=True)
CHANGE_LOG = CODEX / "change_log.md"
ERRORS = CODEX / "errors.ndjson"
RESULTS = CODEX / "results.md"


def ts() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def append(path: Path, text: str) -> None:
    if path.exists():
        path.write_text(path.read_text(encoding="utf-8") + text, encoding="utf-8")
    else:
        path.write_text(text, encoding="utf-8")


def log_change(title: str, file: Path, rationale: str, snippet: str = "") -> None:
    append(
        CHANGE_LOG,
        textwrap.dedent(
            f"""
            ## {ts()} — {file.relative_to(REPO)}
            - **Action:** {title}
            - **Rationale:** {rationale}
            ```text
            {snippet.strip()[:4000]}
            ```
            """
        ),
    )


def q5(step: str, err: str, ctx: str) -> None:
    record = {"ts": ts(), "step": step, "error": err, "context": ctx}
    append(ERRORS, json.dumps(record) + "\n")
    sys.stderr.write(
        textwrap.dedent(
            f"""
            Question for ChatGPT-5 {ts()}:
            While performing [{step}], encountered the following error:
            {err}
            Context: {ctx}
            What are the possible causes, and how can this be resolved while preserving intended functionality?
            """
        ).strip()
        + "\n",
    )


def write_file(
    path: Path, content: str, rationale: str, sentinel: str | None = None
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existed = path.exists()
    if existed and sentinel and sentinel in path.read_text(encoding="utf-8"):
        return
    path.write_text(content, encoding="utf-8")
    log_change("edit" if existed else "create", path, rationale, content)


# ----------------------------
# Phase 3: Best-Effort Construction
# ----------------------------

CONFIG_SENTINEL = "# BEGIN: HYDRA_ROOT_CONFIG"
ROOT_CONFIG = f"""{CONFIG_SENTINEL}
# Root Hydra configuration for codex_ml
defaults:
  - env: ubuntu

env:
  name: ubuntu

logging:
  level: INFO

train:
  epochs: 3
  lr: 3e-4
  batch_size: 8

tokenizer:
  name: gpt2

pipeline:
  steps: ["load_data", "tokenize", "train", "evaluate"]

dry_run: false
"""

ENV_SENTINEL = "# BEGIN: HYDRA_ENV_UBUNTU"
ENV_UBUNTU = f"""{ENV_SENTINEL}
# Ubuntu-specific overrides (paths, shells, CUDA toggles)
env:
  name: ubuntu
  shell: /bin/bash
  tmp_dir: /tmp/codex
"""

MAIN_SENTINEL = "# BEGIN: HYDRA_CLI_MAIN"
MAIN_PY = '''# BEGIN: HYDRA_CLI_MAIN
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
    _log("[hydra] composed config:\\n" + OmegaConf.to_yaml(cfg))
    _save_effective_cfg(cfg, HY_OUT / "config.yaml")
    rc = _dispatch_pipeline(cfg)
    sys.exit(rc)

if __name__ == "__main__":
    main()
'''

README_ADD = """
## Hydra Configuration & CLI

This project uses [Hydra](https://github.com/facebookresearch/hydra) for configuration.

### Run (dry)
```bash
python -m codex_ml.cli.main +dry_run=true
```

### Override examples
```bash
python -m codex_ml.cli.main train.epochs=2 tokenizer.name=gpt2 +dry_run=true
```

Effective composed config is saved to `.codex/hydra_last/config.yaml`.
"""

DEPLOY_NOTE = """
# NOTE: Hydra entrypoint
# Prefer: python -m codex_ml.cli.main +dry_run=true
# You can pass overrides, e.g. train.epochs=2 tokenizer.name=gpt2
"""


def apply() -> None:
    try:
        write_file(
            REPO / "configs" / "config.yaml",
            ROOT_CONFIG,
            "Hydra root config",
            CONFIG_SENTINEL,
        )
        write_file(
            REPO / "configs" / "env" / "ubuntu.yaml",
            ENV_UBUNTU,
            "Hydra ubuntu override",
            ENV_SENTINEL,
        )
        write_file(
            REPO / "src" / "codex_ml" / "cli" / "main.py",
            MAIN_PY,
            "Hydra CLI entrypoint",
            MAIN_SENTINEL,
        )
        readme = REPO / "README.md"
        if readme.exists():
            txt = readme.read_text(encoding="utf-8")
            if "## Hydra Configuration & CLI" not in txt:
                readme.write_text(txt.rstrip() + "\n\n" + README_ADD, encoding="utf-8")
                log_change("edit", readme, "Append Hydra docs", README_ADD)
        deploy_candidates = [
            REPO / "deploy_codex_pipeline.py",
            REPO / "scripts" / "deploy_codex_pipeline.py",
        ]
        for deploy in deploy_candidates:
            if deploy.exists():
                txt = deploy.read_text(encoding="utf-8")
                if "Hydra entrypoint" not in txt:
                    deploy.write_text(DEPLOY_NOTE + "\n" + txt, encoding="utf-8")
                    log_change("edit", deploy, "Add Hydra entrypoint note", DEPLOY_NOTE)
                    break
    except Exception as e:
        q5("3: Best-Effort Construction (write files)", str(e), f"path={REPO}")


def validate() -> None:
    append(RESULTS, f"\n# Hydra Validation {ts()}\n")
    cmds = [
        ["python", "-m", "codex_ml.cli.main", "+dry_run=true"],
        [
            "python",
            "-m",
            "codex_ml.cli.main",
            "train.epochs=2",
            "tokenizer.name=gpt2",
            "+dry_run=true",
        ],
    ]
    for cmd in cmds:
        append(RESULTS, f"\n## $ {' '.join(cmd)}\n```")
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO))
            append(RESULTS, p.stdout + p.stderr + f"\n(exit={p.returncode})\n")
        except Exception as e:
            q5("6: Finalization (validate hydra runs)", str(e), f"cmd={' '.join(cmd)}")
            append(RESULTS, f"ERROR: {e}\n")
        append(RESULTS, "```\n")


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()

    if args.apply:
        apply()
    if args.validate:
        validate()
    if not (args.apply or args.validate):
        print("Usage: --apply [--validate]")


if __name__ == "__main__":
    main()
