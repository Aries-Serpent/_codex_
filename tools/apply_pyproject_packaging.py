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
 - Dedupe duplicate TOML keys ([project].dependencies and [project.optional-dependencies]) without clobbering content

Usage:
  python tools/apply_pyproject_packaging.py
"""
from __future__ import annotations

import ast
import re
import textwrap
from collections import OrderedDict
from pathlib import Path

from packaging.requirements import Requirement
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


CANONICAL_DEPENDENCIES = [
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

CANONICAL_OPTIONAL_DEPENDENCIES = OrderedDict(
    [
        ("analysis", ["libcst>=1.0", "parso>=0.10"]),
        ("configs", ["hydra-core>=1.3", "omegaconf>=2.3", "PyYAML>=6.0"]),
        ("logging", ["duckdb>=0.10", "jsonschema>=4.18", "pandas>=2.0"]),
        (
            "ml",
            [
                "datasets>=2.16",
                "peft>=0.10",
                "sentencepiece>=0.1.99",
                "torch>=2.1",
                "transformers>=4.30",
            ],
        ),
        ("monitoring", ["prometheus-client>=0.14", "psutil>=5.9", "pynvml>=11.5"]),
        ("ops", ["requests>=2.31"]),
        ("symbolic", ["sentencepiece>=0.1.99", "tokenizers>=0.14"]),
        ("tracking", ["mlflow>=2.9", "wandb>=0.15"]),
    ]
)

CANONICAL_DEPENDENCIES_BLOCK = (
    "dependencies = [\n"
    + "\n".join(
        f'  "{dep}"{"," if idx < len(CANONICAL_DEPENDENCIES) - 1 else ""}'
        for idx, dep in enumerate(CANONICAL_DEPENDENCIES)
    )
    + "\n]"
)

_optional_lines = ["[project.optional-dependencies]"]
for extra, values in CANONICAL_OPTIONAL_DEPENDENCIES.items():
    if not values:
        _optional_lines.append(f"{extra} = []")
        continue
    if len(values) == 1:
        _optional_lines.append(f'{extra} = ["{values[0]}"]')
        continue
    _optional_lines.append(f"{extra} = [")
    for idx, value in enumerate(values):
        comma = "," if idx < len(values) - 1 else ""
        _optional_lines.append(f'  "{value}"{comma}')
    _optional_lines.append("]")
CANONICAL_OPTIONAL_BLOCK = "\n".join(_optional_lines)
del _optional_lines

CANONICAL_HEADER = textwrap.dedent(
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

CANONICAL_FOOTER = textwrap.dedent(
    """
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

CANONICAL = (
    f"{CANONICAL_HEADER}\n{CANONICAL_DEPENDENCIES_BLOCK}\n\n"
    f"{CANONICAL_OPTIONAL_BLOCK}\n\n{CANONICAL_FOOTER}\n"
)


def _requirement_name(spec: str) -> str | None:
    try:
        return Requirement(spec).name.lower()
    except Exception:
        return None


def _merge_preserve_order(existing: list[str], required: list[str]) -> list[str]:
    seen_items: set[str] = set()
    seen_names: set[str] = set()
    merged: list[str] = []
    for item in existing:
        if item not in seen_items:
            merged.append(item)
            seen_items.add(item)
            name = _requirement_name(item)
            if name:
                seen_names.add(name)
    for item in required:
        if item in seen_items:
            continue
        name = _requirement_name(item)
        if name and name in seen_names:
            continue
        merged.append(item)
        seen_items.add(item)
        if name:
            seen_names.add(name)
    return merged


def _missing_canonical_dependencies(existing: list[str]) -> list[str]:
    seen_names = {_requirement_name(item) for item in existing if _requirement_name(item)}
    missing: list[str] = []
    for requirement in CANONICAL_DEPENDENCIES:
        name = _requirement_name(requirement)
        if name and name in seen_names:
            continue
        missing.append(requirement)
        if name:
            seen_names.add(name)
    return missing


def _format_array_assignment(name: str, values: list[str]) -> str:
    if not values:
        return f"{name} = []"
    if len(values) == 1:
        return f'{name} = ["{values[0]}"]'
    lines = [f"{name} = ["]
    for value in values:
        lines.append(f'  "{value}",')
    lines.append("]")
    return "\n".join(lines)


def _parse_array_body(body: str) -> list[str]:
    cleaned = body.strip()
    if not cleaned:
        return []
    try:
        parsed = ast.literal_eval(f"[{cleaned}]")
    except (SyntaxError, ValueError):
        items: list[str] = []
        for line in cleaned.splitlines():
            fragment = line.split("#", 1)[0].strip().rstrip(",")
            if fragment.startswith(("'", '"')) and fragment.endswith(("'", '"')):
                items.append(fragment[1:-1])
        return items
    return [str(item) for item in parsed]


def _find_matching_bracket(text: str, open_index: int) -> int:
    depth = 0
    in_string: str | None = None
    escape = False
    for idx in range(open_index, len(text)):
        char = text[idx]
        if in_string is not None:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == in_string:
                in_string = None
            continue
        if char in ('"', "'"):
            in_string = char
            continue
        if char == "[":
            depth += 1
            continue
        if char == "]":
            depth -= 1
            if depth == 0:
                return idx
    return -1


def _extract_dependencies(text: str) -> tuple[list[str], tuple[int, int] | None]:
    pattern = r"(?m)^dependencies\s*=\s*"
    match = re.search(pattern, text)
    if not match:
        return [], None
    open_index = text.find("[", match.end())
    if open_index == -1:
        return [], None
    close_index = _find_matching_bracket(text, open_index)
    if close_index == -1:
        return [], None
    body = text[open_index + 1 : close_index]
    span_start = match.start()
    span_end = close_index + 1
    return _parse_array_body(body), (span_start, span_end)


def _parse_optional_block(block: str) -> OrderedDict[str, list[str]]:
    extras: OrderedDict[str, list[str]] = OrderedDict()
    lines = block.splitlines()
    i = 0
    while i < len(lines):
        raw_line = lines[i]
        line = raw_line.strip()
        if not line or line.startswith("#"):
            i += 1
            continue
        if "=" not in line:
            i += 1
            continue
        name, rest = line.split("=", 1)
        key = name.strip()
        rhs = rest.strip()
        if not rhs.startswith("["):
            i += 1
            continue
        values_lines = [rhs]
        while not values_lines[-1].strip().endswith("]") and i + 1 < len(lines):
            i += 1
            values_lines.append(lines[i].strip())
        values_block = "\n".join(values_lines).strip()
        if values_block.startswith("[") and values_block.endswith("]"):
            array_body = values_block[1:-1]
            extras[key] = _parse_array_body(array_body)
        else:
            extras[key] = []
        i += 1
    return extras


def _extract_optional_dependencies(
    text: str,
) -> tuple[OrderedDict[str, list[str]], tuple[int, int] | None]:
    pattern = r"(?ms)^\[project\.optional-dependencies\]\s*(.*?)(?=^\[project\.|^\[tool\.|\Z)"
    match = re.search(pattern, text)
    if not match:
        return OrderedDict(), None
    return _parse_optional_block(match.group(1)), (match.start(), match.end())


def _format_optional_block(extras: OrderedDict[str, list[str]]) -> str:
    lines = ["[project.optional-dependencies]"]
    for key, values in extras.items():
        if not values:
            lines.append(f"{key} = []")
            continue
        if len(values) == 1:
            lines.append(f'{key} = ["{values[0]}"]')
            continue
        lines.append(f"{key} = [")
        for value in values:
            lines.append(f'  "{value}",')
        lines.append("]")
    return "\n".join(lines)


def _merge_optional_dependencies(
    existing: OrderedDict[str, list[str]]
) -> tuple[OrderedDict[str, list[str]], bool]:
    merged: OrderedDict[str, list[str]] = OrderedDict()
    changed = False
    for key, values in existing.items():
        required = CANONICAL_OPTIONAL_DEPENDENCIES.get(key, [])
        merged_values = _merge_preserve_order(values, required)
        if merged_values != values:
            changed = True
        merged[key] = merged_values
    for key, required in CANONICAL_OPTIONAL_DEPENDENCIES.items():
        if key not in merged:
            merged[key] = required[:]
            changed = True
    return merged, changed


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

    # Helper: keep first block occurrence, remove subsequent
    def _keep_first(pattern: str, s: str) -> str:
        rx = re.compile(pattern, re.M | re.S)
        matches = list(rx.finditer(s))
        if len(matches) <= 1:
            return s
        first_end = matches[0].end()
        return s[:first_end] + rx.sub("", s[first_end:])

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

    # Dependencies: rewrite the first block to the canonical set and drop duplicates.
    # Only add a canonical block if dependencies are entirely missing.
    dep_pattern = r"(?ms)^dependencies\s*=\s*\[[\s\S]*?\]"
    if re.search(dep_pattern, text):
        text, _ = re.subn(dep_pattern, CANONICAL_DEPENDENCIES_BLOCK, text, count=1)
        text = _keep_first(dep_pattern, text)
    else:
        dependencies_block = _format_array_assignment("dependencies", CANONICAL_DEPENDENCIES)
        insertion = 'version = "0.0.0"\n'
        replacement = f"{insertion}{dependencies_block}\n"
        if insertion in text:
            text = text.replace(insertion, replacement, 1)
        else:
            text = text.rstrip() + "\n\n" + dependencies_block

    optional_deps, optional_span = _extract_optional_dependencies(text)
    merged_optional, optional_changed = _merge_optional_dependencies(optional_deps)
    optional_block = None
    if optional_span:
        start, end = optional_span
        if optional_changed:
            optional_block = _format_optional_block(merged_optional)
            text = text[:start] + optional_block + text[end:]
        else:
            optional_block = text[start:end]
    else:
        optional_block = _format_optional_block(merged_optional)
        marker = "[project.scripts]"
        insertion_text = optional_block + "\n\n"
        idx = text.find(marker)
        if idx == -1:
            text = text.rstrip() + "\n\n" + optional_block + "\n"
        else:
            text = text[:idx] + insertion_text + text[idx:]

    # Deduplicate optional dependencies blocks if multiple remain
    if optional_block is not None:
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

    package_dir_block = "\n".join(
        [
            "[tool.setuptools.package-dir]",
            '"" = "src"',
            'codex_addons = "codex_addons"',
            'codex_digest = "codex_digest"',
            'codex_utils = "codex_utils"',
            'interfaces = "interfaces"',
            'tokenization = "tokenization"',
            'tools = "tools"',
            'training = "training"',
        ]
    )

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
    find_block = "\n".join(
        [
            "[tool.setuptools.packages.find]",
            'where = [".", "src"]',
            "include = [",
            '  "codex_ml*",',
            '  "codex*",',
            '  "tokenization*",',
            '  "training*",',
            '  "codex_utils*",',
            '  "interfaces*",',
            '  "hhg_logistics*",',
            '  "examples*",',
            '  "tools*"',
            "]",
            'exclude = ["tests*", "torch*"]',
        ]
    )
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
