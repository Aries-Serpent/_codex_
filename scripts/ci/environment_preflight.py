#!/usr/bin/env python3
"""Classify the required Copilot environment before heavy ML/RAG work runs.

The local sandbox is intentionally a staging layer for quick diagnosis and patch
assembly. When the task touches ML/RAG code or dependency names, the repo should
prefer the GitHub-hosted ``ml-heavy`` Copilot environment instead of trying to
reproduce the full CI matrix in a stripped sandbox.

The script writes a repo-owned configuration file in ``.codex/agent_environment_config.yaml``
so future sessions can reuse the same decision without a human re-selecting the
workflow input each time.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
from pathlib import Path
from typing import Sequence

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback
    import tomli as tomllib  # type: ignore


ML_RAG_KEYWORDS = (
    "ml",
    "rag",
    "retrieval",
    "retriever",
    "vector",
    "embedding",
    "embeddings",
    "faiss",
    "transformers",
    "torch",
    "tensorflow",
    "sentence-transformers",
    "sentence_transformers",
    "datasets",
    "numpy",
    "pytorch",
    "ml-heavy",
    "test-ml-components",
    "test-rag",
    "checkpoint",
)

SECURITY_KEYWORDS = ("security", "codeql", "scan", "semgrep", "sast", "dependency-vulnerability")
DOCS_KEYWORDS = ("docs", "documentation", "mkdocs", "readme")


def _normalize(value: str | None) -> str:
    return (value or "").strip().lower()


def _coalesce(values: Sequence[str | None]) -> list[str]:
    cleaned: list[str] = []
    for value in values:
        entry = str(value or "").strip()
        if entry:
            cleaned.append(entry)
    return cleaned


def _load_runtime_dependencies(repo_root: Path) -> list[str]:
    pyproject = repo_root / "pyproject.toml"
    if not pyproject.exists():
        return []
    try:
        with pyproject.open("rb") as handle:
            data = tomllib.load(handle)
    except Exception:
        return []

    optionals = data.get("project", {}).get("optional-dependencies", {})
    runtime = optionals.get("runtime", [])
    return [str(dep).strip() for dep in runtime if str(dep).strip()]


def _contains_keyword(haystack: str, keyword: str) -> bool:
    if not keyword:
        return False
    normalized_haystack = re.sub(r"[^a-z0-9]+", " ", (haystack or "").lower()).strip()
    normalized_keyword = re.sub(r"[^a-z0-9]+", " ", keyword.lower()).strip()
    if not normalized_keyword:
        return False

    tokens = normalized_haystack.split()
    keyword_tokens = normalized_keyword.split()
    if len(keyword_tokens) == 1:
        return keyword_tokens[0] in tokens

    keyword_phrase = " ".join(keyword_tokens)
    return keyword_phrase in normalized_haystack or keyword_phrase.replace(" ", "-") in (haystack or "").lower() or keyword_phrase.replace(" ", "_") in (haystack or "").lower()


def _detect_environment_type(task_inputs: Sequence[str | None]) -> tuple[str, str]:
    haystack = " ".join(_coalesce(task_inputs)).lower()
    for keywords in (ML_RAG_KEYWORDS, SECURITY_KEYWORDS, DOCS_KEYWORDS):
        for keyword in keywords:
            if _contains_keyword(haystack, keyword):
                if keywords is ML_RAG_KEYWORDS:
                    return "ml-heavy", f"Detected ML/RAG signal: '{keyword}'"
                if keywords is SECURITY_KEYWORDS:
                    return "security-scan", f"Detected security signal: '{keyword}'"
                if keywords is DOCS_KEYWORDS:
                    return "documentation", f"Detected docs signal: '{keyword}'"
    return "standard", "No ML/RAG/security/docs signal detected; defaulting to standard environment."


def _is_stubbed_dependency(module_name: str, spec: object | None) -> bool:
    if spec is None:
        return True
    loader = getattr(spec, "loader", None)
    if loader is not None:
        return False
    if getattr(spec, "origin", None) in {"built-in", "frozen"}:
        return False
    if getattr(sys.modules.get(module_name), "__codex_stub__", False):
        return True
    # sitecustomize installs empty placeholder modules with a ModuleSpec whose
    # loader is intentionally unset. Those should not count as actually installed.
    return True


def _detect_missing_runtime_dependencies(required_deps: Sequence[str]) -> list[str]:
    missing: list[str] = []
    for dep in required_deps:
        match = re.match(r"^\s*([A-Za-z0-9_.-]+)", dep)
        name = match.group(1).strip() if match else ""
        if not name:
            continue
        # Normalize names such as "sentence-transformers" and "faiss-cpu".
        normalized = name.lower().replace("_", "-")
        module_name = normalized.replace("-cpu", "")
        module_name = module_name.replace("-", "_")
        if module_name in {"pyyaml", "yaml"}:
            module_name = "yaml"
        spec = importlib.util.find_spec(module_name)
        if spec is None or _is_stubbed_dependency(module_name, spec):
            missing.append(dep)
    return missing


def _write_github_output(environment_type: str, reason: str, lfs_mode: str, config_path: Path) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    with open(output_path, "a", encoding="utf-8") as handle:
        handle.write(f"environment_type={environment_type}\n")
        handle.write(f"lfs_mode={lfs_mode}\n")
        handle.write(f"config_path={config_path}\n")
        handle.write(f"reason={reason}\n")


def _build_config(environment_type: str, reason: str, repo_root: Path) -> dict:
    ml_runtime = _load_runtime_dependencies(repo_root)
    if environment_type == "ml-heavy":
        default_lfs_mode = "targeted"
        default_lfs_include = ["data/models/*", "artifacts/*"]
    else:
        default_lfs_mode = "none"
        default_lfs_include = []

    config = {
        "environment_type": environment_type,
        "reason": reason,
        "lfs_mode": default_lfs_mode,
        "lfs_include_paths": default_lfs_include,
        "local_sandbox_policy": {
            "sandbox_is_staging_only": True,
            "prefer_prepared_primary_environment": environment_type == "ml-heavy",
            "transfer_via_repo_bundle": True,
        },
        "runtime": {
            "python": "3.12",
            "runner_profile": "ubuntu-8-core" if environment_type == "ml-heavy" else "ubuntu-latest-m",
            "required_dependencies": ml_runtime,
            "missing_dependencies": _detect_missing_runtime_dependencies(ml_runtime),
        },
        "notes": [
            "The local sandbox is for diagnosis and patch prep, not full ML/RAG matrix validation.",
            "For ml-heavy tasks, prefer the GitHub-hosted prepared environment before full suite runs.",
        ],
    }
    return config


def _render_yaml(data: dict, indent: int = 0) -> str:
    def _format_scalar(value: object) -> str:
        if isinstance(value, bool):
            return "true" if value else "false"
        if value is None:
            return "null"
        if isinstance(value, (int, float)):
            return str(value)

        scalar = str(value)
        needs_quotes = (
            scalar == ""
            or scalar.strip() != scalar
            or ":" in scalar
            or "#" in scalar
            or scalar.lower() in {"true", "false", "null", "~", "yes", "no", "on", "off"}
            or scalar[0] in {"-", "?", "!", "&", "*", "{", "}", "[", "]", ",", "|", ">", "@", "`", "%", "'", '"'}
        )
        if needs_quotes:
            return json.dumps(scalar)
        return scalar

    prefix = " " * indent
    lines: list[str] = []
    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"{prefix}{key}:")
            lines.append(_render_yaml(value, indent + 2))
        elif isinstance(value, list):
            if not value:
                lines.append(f"{prefix}{key}: []")
            else:
                lines.append(f"{prefix}{key}:")
                for item in value:
                    if isinstance(item, str):
                        lines.append(f"{prefix}  - {_format_scalar(item)}")
                    elif isinstance(item, dict):
                        lines.append(f"{prefix}  -")
                        lines.append(_render_yaml(item, indent + 4).rstrip())
        else:
            lines.append(f"{prefix}{key}: {_format_scalar(value)}")
    return "\n".join(lines) + "\n"


def _write_config(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = _render_yaml(data)
    path.write_text(rendered, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root to scan")
    parser.add_argument("--task-context", nargs="*", default=[], help="Task text, PR title, CI failure summary, or file paths")
    parser.add_argument("--head-ref", default="", help="Branch or ref name to inspect when auto-detecting the environment")
    parser.add_argument("--ci-job", default="", help="CI job or workflow name to inspect when auto-detecting the environment")
    parser.add_argument("--output", type=Path, default=None, help="Override output path for the YAML config")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    task_context = _coalesce(args.task_context)
    if args.head_ref:
        task_context.append(args.head_ref)
    if args.ci_job:
        task_context.append(args.ci_job)

    environment_type, reason = _detect_environment_type(task_context)
    config = _build_config(environment_type, reason, repo_root)
    output = args.output or (repo_root / ".codex" / "agent_environment_config.yaml")
    output_path = output.resolve(strict=False)
    try:
        output_path.relative_to(repo_root)
    except ValueError as exc:
        raise ValueError(f"--output path must stay inside repo root: {output}") from exc

    _write_config(output_path, config)
    _write_github_output(environment_type, reason, config["lfs_mode"], output_path)

    print(f"environment_type={environment_type}")
    print(f"lfs_mode={config['lfs_mode']}")
    print(f"reason={reason}")
    print(f"config_path={output_path}")
    print(f"local_sandbox_policy={config['local_sandbox_policy']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
