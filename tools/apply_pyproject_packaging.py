#!/usr/bin/env python3
"""
Idempotent pyproject.toml normalizer for Aries-Serpent/_codex_

Actions:
 - Set [project].name = "codex-ml"
 - Ensure console scripts: codex-train, codex-eval, codex-list-plugins (non-destructive; preserves others)
 - Enforce setuptools discovery across top-level and src/ (where=[".", "src"])
   with include filters for repo packages and excludes for tests/ and torch/ stubs
 - Keep build-backend: setuptools.build_meta
 - Enforce SPDX license ("MIT") and inject [project.license-files] to silence Setuptools deprecations

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
license = "MIT"
authors = [
  { name = "Aries Serpent" }
]
keywords = ["ml", "training", "evaluation", "plugins", "hydra", "cli"]
classifiers = [
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3 :: Only",
  "Operating System :: OS Independent",
]
version = "0.0.0"

[project.license-files]
paths = [
  "LICENSE",
  "LICENSES/*"
]
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

    # SPDX license enforcement (string form) and canonical license-files table
    text, _ = re.subn(
        r'(?m)^\s*license\s*=\s*\{\s*file\s*=\s*"?LICENSE"?\s*\}\s*$',
        'license = "MIT"',
        text,
    )
    text, _ = re.subn(
        r'(?m)^\s*license\s*=\s*"(?!MIT)[^"]*"\s*$',
        'license = "MIT"',
        text,
    )

    canonical_license_block = (
        "[project.license-files]\n"
        'paths = [\n'
        '  "LICENSE",\n'
        '  "LICENSES/*"\n'
        "]\n"
    )
    license_pattern = r"(?ms)^\[project\.license-files\][\s\S]*?(?=^dependencies\s*=|^\[project\.[a-zA-Z-]+|^\[tool\.|^\Z)"
    text, license_replacements = re.subn(license_pattern, canonical_license_block, text)
    if license_replacements == 0:
        inserted = False
        text, dep_insertions = re.subn(
            r"(?ms)^(dependencies\s*=\s*\[[\s\S]*?\]\s*)",
            canonical_license_block + r"\1",
            text,
            count=1,
        )
        if dep_insertions > 0:
            inserted = True
        if not inserted:
            text, version_insertions = re.subn(
                r'(?m)^(version\s*=\s*".*"\s*)$',
                r"\1\n" + canonical_license_block.rstrip("\n"),
                text,
                count=1,
            )
            if version_insertions > 0:
                inserted = True
        if not inserted:
            text += "\n" + canonical_license_block

    # Ensure blank line between version and license-files block for readability
    text, _ = re.subn(
        r'(?m)^(version\s*=\s*".*")\n(?=\[project\.license-files\])',
        r"\1\n\n",
        text,
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

    # Deduplicate optional dependencies blocks if multiple remain
    double_optional = optional_block + optional_block
    double_optional_nl = optional_block + "\n" + optional_block
    while double_optional in text or double_optional_nl in text:
        if double_optional in text:
            text = text.replace(double_optional, optional_block, 1)
        if double_optional_nl in text:
            text = text.replace(double_optional_nl, optional_block, 1)

    # Ensure [project.scripts] block exists and contains our scripts
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
