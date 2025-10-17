#!/usr/bin/env python3
"""
Idempotent pyproject.toml normalizer for Aries-Serpent/_codex_

Actions:
 - Set [project].name = "codex-ml"
 - Ensure console scripts: codex-train, codex-eval, codex-list-plugins
 - Enforce setuptools src/ layout discovery include ["codex_ml*"]
 - Keep build-backend: setuptools.build_meta

Usage:
  python tools/apply_pyproject_packaging.py
"""
from __future__ import annotations

import re
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"

CANONICAL = (
    textwrap.dedent(
        """
[build-system]
requires = ["setuptools>=67", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "codex-ml"
description = "Codex ML training, evaluation, and plugin framework"
readme = "README.md"
requires-python = ">=3.9"
license = { file = "LICENSE" }
authors = [
  { name = "Aries Serpent" }
]
keywords = ["ml", "training", "evaluation", "plugins", "hydra", "cli"]
classifiers = [
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3 :: Only",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent",
]
version = "0.0.0"
dependencies = [
  "datasets>=2.16",
  "duckdb>=0.10",
  "hydra-core>=1.3",
  "numpy>=1.24",
  "omegaconf>=2.3",
  "pandas>=2.0",
  "peft>=0.10",
  "PyYAML>=6.0",
  "pydantic>=2.11",
  "pydantic-settings>=2.2",
  "sentencepiece>=0.1.99",
  "torch>=2.1",
  "transformers>=4.30",
  "typer>=0.12",
]

[project.optional-dependencies]
analysis = ["libcst>=1.0", "parso>=0.10"]
configs = ["hydra-core>=1.3", "omegaconf>=2.3", "PyYAML>=6.0"]
logging = ["duckdb>=0.10", "jsonschema>=4.18", "pandas>=2.0"]
ml = [
  "datasets>=2.16",
  "peft>=0.10",
  "sentencepiece>=0.1.99",
  "torch>=2.1",
  "transformers>=4.30",
]
monitoring = ["prometheus-client>=0.14", "psutil>=5.9", "pynvml>=11.5"]
ops = ["requests>=2.31"]
symbolic = ["sentencepiece>=0.1.99", "tokenizers>=0.14"]
tracking = ["mlflow>=2.9", "wandb>=0.15"]

[project.scripts]
codex-train = "codex_ml.cli.entrypoints:train_main"
codex-eval = "codex_ml.cli.entrypoints:eval_main"
codex-list-plugins = "codex_ml.cli.list_plugins:main"

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]
include = ["codex_ml*"]
exclude = []
"""
    ).strip()
    + "\n"
)


def main():
    # If file is missing or too divergent, write canonical content
    if not PYPROJECT.exists():
        PYPROJECT.write_text(CANONICAL, encoding="utf-8")
        print("Wrote canonical pyproject.toml")
        return 0

    text = PYPROJECT.read_text(encoding="utf-8")

    # Ensure name is codex-ml (hyphen)
    text, _ = re.subn(r'(?m)^(name\s*=\s*")[^"]+(")', r"\1codex-ml\2", text)
    # Build backend correctness
    if "build-backend" not in text:
        text = text.replace(
            "[build-system]",
            '[build-system]\nrequires = ["setuptools>=67", "wheel"]\nbuild-backend = "setuptools.build_meta"',
        )
    else:
        text, _ = re.subn(
            r'(?m)^(build-backend\s*=\s*")[^"]+(")', r"\1setuptools.build_meta\2", text
        )

    # Ensure dependency list is present and matches canonical order
    dependencies_block = (
        "dependencies = [\n"
        '  "datasets>=2.16",\n'
        '  "duckdb>=0.10",\n'
        '  "hydra-core>=1.3",\n'
        '  "numpy>=1.24",\n'
        '  "omegaconf>=2.3",\n'
        '  "pandas>=2.0",\n'
        '  "peft>=0.10",\n'
        '  "PyYAML>=6.0",\n'
        '  "pydantic>=2.11",\n'
        '  "pydantic-settings>=2.2",\n'
        '  "sentencepiece>=0.1.99",\n'
        '  "torch>=2.1",\n'
        '  "transformers>=4.30",\n'
        '  "typer>=0.12",\n'
        "]\n"
    )
    if "dependencies =" in text:
        text, _ = re.subn(r"(?ms)^dependencies\s*=\s*\[[^\]]*\]", dependencies_block.rstrip(), text)
    else:
        text = text.replace('version = "0.0.0"\n', f'version = "0.0.0"\n{dependencies_block}\n')

    optional_block = (
        "[project.optional-dependencies]\n"
        'analysis = ["libcst>=1.0", "parso>=0.10"]\n'
        'configs = ["hydra-core>=1.3", "omegaconf>=2.3", "PyYAML>=6.0"]\n'
        'logging = ["duckdb>=0.10", "jsonschema>=4.18", "pandas>=2.0"]\n'
        "ml = [\n"
        '  "datasets>=2.16",\n'
        '  "peft>=0.10",\n'
        '  "sentencepiece>=0.1.99",\n'
        '  "torch>=2.1",\n'
        '  "transformers>=4.30",\n'
        "]\n"
        'monitoring = ["prometheus-client>=0.14", "psutil>=5.9", "pynvml>=11.5"]\n'
        'ops = ["requests>=2.31"]\n'
        'symbolic = ["sentencepiece>=0.1.99", "tokenizers>=0.14"]\n'
        'tracking = ["mlflow>=2.9", "wandb>=0.15"]\n'
    )
    if "[project.optional-dependencies]" in text:
        text, _ = re.subn(
            r"(?ms)^\[project\.optional-dependencies\][\s\S]*?(?=^\[project\.|^\[tool\.|\Z)",
            optional_block,
            text,
        )
    else:
        text = text.replace("[project.scripts]\n", optional_block + "\n[project.scripts]\n")

    # Ensure [project.scripts] block exists and contains our scripts
    if "[project.scripts]" not in text:
        text += "\n\n[project.scripts]\n"
    # Insert/normalize scripts
    scripts = {
        "codex-train": "codex_ml.cli.entrypoints:train_main",
        "codex-eval": "codex_ml.cli.entrypoints:eval_main",
        "codex-list-plugins": "codex_ml.cli.list_plugins:main",
    }
    for key, val in scripts.items():
        pattern = rf'(?m)^{re.escape(key)}\s*=\s*".*"$'
        if re.search(pattern, text):
            text = re.sub(pattern, f'{key} = "{val}"', text)
        else:
            text += f'{key} = "{val}"\n'

    # Ensure src/ layout discovery
    if "[tool.setuptools]" not in text:
        text += '\n[tool.setuptools]\npackage-dir = {"" = "src"}\n'
    if "[tool.setuptools.packages.find]" not in text:
        text += '\n[tool.setuptools.packages.find]\nwhere = ["src"]\ninclude = ["codex_ml*"]\nexclude = []\n'
    else:
        text, _ = re.subn(
            r"(?ms)^\[tool\.setuptools\.packages\.find\][\s\S]*?(?=^\[|\Z)",
            '[tool.setuptools.packages.find]\nwhere = ["src"]\ninclude = ["codex_ml*"]\nexclude = []\n',
            text,
        )

    PYPROJECT.write_text(text, encoding="utf-8")
    print("Normalized pyproject.toml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
