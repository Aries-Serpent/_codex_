#!/usr/bin/env python3
"""
Idempotent pyproject.toml normalizer for Aries-Serpent/_codex_

Actions:
 - Set [project].name = "codex-ml"
 - Ensure console scripts: codex-train, codex-eval, codex-list-plugins (non-destructive; preserves others)
 - Enforce setuptools discovery across top-level and src/ (where=[".", "src"])
   with include filters for repo packages and excludes for tests/ and torch/ stubs
 - Keep build-backend: setuptools.build_meta

Usage:
  python tools/apply_pyproject_packaging.py
"""
from __future__ import annotations

import re
import textwrap
from pathlib import Path

from packaging.specifiers import SpecifierSet
from packaging.version import Version

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"


def _normalize_python_floor(prefix: str, spec: str, suffix: str, floor: str = "3.10") -> str:
    """Return a possibly-updated requires-python assignment."""

    normalized = _ensure_python_floor(spec, floor)
    if normalized == spec:
        return f"{prefix}{spec}{suffix}"
    return f"{prefix}{normalized}{suffix}"


def _ensure_python_floor(spec: str, floor: str) -> str:
    try:
        spec_set = SpecifierSet(spec)
    except Exception:
        return f">={floor}"

    floor_version = Version(floor)
    if not _allows_below_floor(spec_set, floor_version):
        return spec
    return f">={floor}"


def _allows_below_floor(spec_set: SpecifierSet, floor_version: Version) -> bool:
    # Check any major versions lower than the floor major.
    for major in range(floor_version.major):
        if spec_set.contains(Version(f"{major}.0")) or spec_set.contains(Version(f"{major}.999")):
            return True

    # Check minor releases below the floor within the same major version.
    for minor in range(floor_version.minor):
        if spec_set.contains(Version(f"{floor_version.major}.{minor}")) or spec_set.contains(
            Version(f"{floor_version.major}.{minor}.999")
        ):
            return True

    return False


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
requires-python = ">=3.10"
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
version = "0.1.0"

[project.scripts]
codex-train = "codex_ml.cli.entrypoints:train_main"
codex-eval = "codex_ml.cli.entrypoints:eval_main"
codex-list-plugins = "codex_ml.cli.list_plugins:main"

[tool.setuptools]

[tool.setuptools.package-dir]
"" = "src"
codex_addons = "codex_addons"
codex_digest = "codex_digest"
codex_utils = "codex_utils"
interfaces = "interfaces"
tokenization = "tokenization"
tools = "tools"
training = "training"

[tool.setuptools.packages.find]
where = [".", "src"]
include = [
  "codex_ml*",
  "codex*",
  "tokenization*",
  "training*",
  "codex_utils*",
  "interfaces*",
  "hhg_logistics*",
  "examples*",
  "tools*"
]
exclude = ["tests*", "torch*"]
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

    # Normalize minimum Python requirement (only bump floor, do not lower if already higher)
    text, _ = re.subn(
        r'(?m)^(requires-python\s*=\s*")(?P<spec>[^"]+)(")',
        lambda m: _normalize_python_floor(m.group(1), m.group("spec"), m.group(3)),
        text,
    )

    # Ensure [project.scripts] block exists and contains our canonical scripts without dropping existing ones
    if "[project.scripts]" not in text:
        text += "\n\n[project.scripts]\n"
    scripts = {
        "codex-train": "codex_ml.cli.entrypoints:train_main",
        "codex-eval": "codex_ml.cli.entrypoints:eval_main",
        "codex-list-plugins": "codex_ml.cli.list_plugins:main",
    }
    for key, val in scripts.items():
        pattern = rf'(?m)^{re.escape(key)}\s*=\s*"[^"]*"'
        if re.search(pattern, text):
            text = re.sub(pattern, f'{key} = "{val}"', text)
        else:
            text += f'{key} = "{val}"\n'

    # Ensure discovery across top-level and src/ package layouts
    if "[tool.setuptools]" not in text:
        text += "\n\n[tool.setuptools]\n"

    package_dir_block = textwrap.dedent(
        """
        [tool.setuptools.package-dir]
        "" = "src"
        codex_addons = "codex_addons"
        codex_digest = "codex_digest"
        codex_utils = "codex_utils"
        interfaces = "interfaces"
        tokenization = "tokenization"
        tools = "tools"
        training = "training"
        """
    ).strip()

    if "[tool.setuptools.package-dir]" in text:
        text, replaced = re.subn(
            r"(?ms)^\[tool\.setuptools\.package-dir\][\s\S]*?(?=^\[|\Z)",
            package_dir_block + "\n",
            text,
        )
        if replaced == 0:
            text = text.replace(
                "[tool.setuptools]",
                "[tool.setuptools]\n\n" + package_dir_block + "\n",
                1,
            )
    else:
        text = text.replace(
            "[tool.setuptools]",
            "[tool.setuptools]\n\n" + package_dir_block + "\n",
            1,
        )
    find_block = textwrap.dedent(
        """
[tool.setuptools.packages.find]
where = [".", "src"]
include = [
  "codex_ml*",
  "codex*",
  "tokenization*",
  "training*",
  "codex_utils*",
  "interfaces*",
  "hhg_logistics*",
  "examples*",
  "tools*"
]
exclude = ["tests*", "torch*"]
"""
    ).strip()
    if "[tool.setuptools.packages.find]" not in text:
        text += "\n" + find_block + "\n"
    else:
        text, _ = re.subn(
            r"(?ms)^\[tool\.setuptools\.packages\.find\][\s\S]*?(?=^\[|\Z)",
            find_block + "\n",
            text,
        )

    PYPROJECT.write_text(text, encoding="utf-8")
    print("Normalized pyproject.toml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
