#!/usr/bin/env python3
"""Validate GitHub Actions workflow YAML and repo drift contracts.

This keeps the workflow surface aligned with the repository's canonical nox
registry and prevents stale GitHub Actions drift such as:

  - unquoted YAML trigger keys like ``on:``
  - workflow commands invoking nox sessions that do not exist
  - duplicate CodeQL categories within a single workflow file
  - stale hard-coded issue assignee names like ``security-team``

Usage::

    python scripts/ci/check_workflow_yaml.py .github/workflows/ci.yml ...
    python scripts/ci/check_workflow_yaml.py .github/workflows
    pre-commit run check-github-workflows --all-files
"""

from __future__ import annotations

import ast
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is not installed.  Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parents[2]
NOXFILE_PATH = REPO_ROOT / "noxfile.py"
GITHUB_ACTIONS_SCHEMA = "https://json.schemastore.org/github-workflow.json"


def _check_jsonschema_available() -> bool:
    try:
        import check_jsonschema  # noqa: F401  # type: ignore[import]
        return True
    except ImportError:
        return False


def _discover_workflow_paths(paths: list[str]) -> list[str]:
    """Expand directories to workflow files and deduplicate results."""
    discovered: list[str] = []
    for raw in paths:
        candidate = Path(raw)
        if candidate.is_dir():
            for suffix in (".yml", ".yaml"):
                discovered.extend(str(path) for path in sorted(candidate.glob(f"*{suffix}")))
        elif candidate.exists():
            discovered.append(str(candidate))
    return sorted(set(discovered))


def _extract_python_versions(tree: ast.AST) -> list[str]:
    versions: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "PY_VERSIONS":
                    versions = _literal_string_list(node.value)
                    if versions:
                        return versions
    return versions or ["3.12", "3.11", "3.10"]


def _literal_string_list(node: ast.AST | None) -> list[str]:
    if node is None:
        return []
    if isinstance(node, (ast.List, ast.Tuple)):
        values: list[str] = []
        for element in node.elts:
            if isinstance(element, ast.Constant) and isinstance(element.value, str):
                values.append(element.value)
        return values
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    return []


def _nox_registry() -> set[str]:
    """Return the repo's canonical nox session names from the active nox files."""
    candidates = [NOXFILE_PATH]
    nested = REPO_ROOT / "configs" / "development" / "noxfile.py"
    if nested.exists():
        candidates.append(nested)

    registry: set[str] = set()
    for path in candidates:
        if not path.exists():
            continue

        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        versions = _extract_python_versions(tree)

        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for decorator in node.decorator_list:
                if not isinstance(decorator, ast.Call):
                    continue
                func = decorator.func
                if not (isinstance(func, ast.Attribute) and func.attr == "session"):
                    continue
                if not (isinstance(func.value, ast.Name) and func.value.id == "nox"):
                    continue

                name = None
                python_value = None
                for keyword in decorator.keywords:
                    if keyword.arg == "name" and isinstance(keyword.value, ast.Constant):
                        if isinstance(keyword.value.value, str):
                            name = keyword.value.value
                    if keyword.arg == "python":
                        python_value = keyword.value

                base_name = name or node.name
                registry.add(base_name)

                if python_value is None:
                    continue

                if isinstance(python_value, ast.Name) and python_value.id == "DEFAULT_PYTHON":
                    continue
                if isinstance(python_value, ast.Name) and python_value.id == "PY_VERSIONS":
                    for version in versions:
                        registry.add(f"{base_name}-{version}")
                    continue
                if isinstance(python_value, (ast.List, ast.Tuple)):
                    strings = _literal_string_list(python_value)
                    if strings:
                        for version in strings:
                            registry.add(f"{base_name}-{version}")
                        continue
                if isinstance(python_value, ast.Call):
                    if isinstance(python_value.func, ast.Name) and python_value.func.id == "list":
                        if python_value.args and isinstance(python_value.args[0], ast.Name):
                            if python_value.args[0].id == "PY_VERSIONS":
                                for version in versions:
                                    registry.add(f"{base_name}-{version}")
                                continue

    return registry


def validate_syntax(paths: list[str]) -> list[str]:
    """Return a list of error strings for files with invalid YAML."""
    errors: list[str] = []
    for path in paths:
        try:
            with open(path, encoding="utf-8") as fh:
                yaml.safe_load(fh)
        except yaml.YAMLError as exc:
            errors.append(f"{path}: YAML syntax error — {exc}")
        except OSError as exc:
            errors.append(f"{path}: cannot open file — {exc}")
    return errors


def validate_workflow_contract(paths: list[str]) -> list[str]:
    """Reject stale workflow drift against the repo's canonical contracts."""
    errors: list[str] = []
    registry = _nox_registry()

    for path in paths:
        try:
            text = Path(path).read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"{path}: cannot read file — {exc}")
            continue

        if re.search(r"(?m)^on\s*:", text) and not re.search(r"(?m)^['\"]on['\"]\s*:", text):
            errors.append(
                f"{path}: unquoted GitHub Actions trigger key 'on' detected; quote it as 'on' to avoid YAML 1.1 bool parsing."
            )

        stale_trigger_names = [
            "push",
            "pull_request",
            "pull_request_target",
            "workflow_dispatch",
            "workflow_call",
            "schedule",
        ]
        for trigger in stale_trigger_names:
            if re.search(rf"(?m)^\s*{trigger}\s*:\s*null\s*$", text):
                errors.append(
                    f"{path}: stale trigger key '{trigger}: null' detected; define it as '{trigger}: {{}}' or with explicit inputs."
                )

        for session in sorted(set(re.findall(r"nox\s+-s\s+([A-Za-z0-9_.-]+)", text))):
            if session not in registry:
                errors.append(
                    f"{path}: nox session '{session}' is not registered in {NOXFILE_PATH.name}."
                )

        codeql_config_paths = re.findall(r"(?m)^\s*config-file\s*:\s*(.+?)\s*$", text)
        if codeql_config_paths:
            canonical = ".github/codeql/codeql-config.yml"
            for raw_path in codeql_config_paths:
                normalized = raw_path.strip().strip("\"'")
                if normalized not in {canonical, f"./{canonical}"}:
                    errors.append(
                        f"{path}: CodeQL config drift detected: '{normalized}' does not match the repo-standard '{canonical}'."
                    )
                elif not (REPO_ROOT / canonical).exists():
                    errors.append(
                        f"{path}: CodeQL config file '{canonical}' is missing from the repository root."
                    )

        category_counts: dict[str, int] = {}
        for category in re.findall(r"(?m)^\s*category\s*:\s*(.+?)\s*$", text):
            cleaned = category.strip().strip("\"'")
            if cleaned:
                category_counts[cleaned] = category_counts.get(cleaned, 0) + 1
        for category, count in sorted(category_counts.items()):
            if count > 1:
                errors.append(
                    f"{path}: duplicate CodeQL category '{category}' detected; use a unique category per run/attempt."
                )

        if re.search(r"assignees\s*:\s*\[|assignees\s*:\s*\n", text, re.IGNORECASE):
            if re.search(r"security-team|@security-team|security-team\b", text, re.IGNORECASE):
                errors.append(
                    f"{path}: stale assignee reference 'security-team' detected; use a valid repository username instead."
                )

    return errors


def validate_schema(paths: list[str]) -> list[str]:
    """Validate *paths* against the GitHub Actions JSON Schema."""
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "check_jsonschema",
            "--schemafile",
            GITHUB_ACTIONS_SCHEMA,
            *paths,
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return [result.stdout.strip() or result.stderr.strip()]
    return []


def main() -> None:
    raw_paths = sys.argv[1:]
    if not raw_paths:
        print("check-workflow-yaml: no workflow files to check.")
        sys.exit(0)

    paths = _discover_workflow_paths(raw_paths)
    if not paths:
        print("check-workflow-yaml: no workflow YAML files found.")
        sys.exit(0)

    syntax_errors = validate_syntax(paths)
    if syntax_errors:
        for err in syntax_errors:
            print(f"  ❌ {err}", file=sys.stderr)
        sys.exit(1)

    contract_errors = validate_workflow_contract(paths)
    if contract_errors:
        for err in contract_errors:
            print(f"  ❌ {err}", file=sys.stderr)
        sys.exit(1)

    if _check_jsonschema_available():
        schema_errors = validate_schema(paths)
        if schema_errors:
            for err in schema_errors:
                print(f"  ❌ {err}", file=sys.stderr)
            sys.exit(1)
        print(f"  ✅ {len(paths)} workflow file(s) passed YAML syntax, repo contract, and schema validation.")
    else:
        print(
            f"  ✔  {len(paths)} workflow file(s) passed YAML syntax and repo contract validation.  "
            "Install check-jsonschema for full schema validation: pip install check-jsonschema"
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
