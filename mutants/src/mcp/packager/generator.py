"""
Generator Module

This module provides functionality for generator.

Usage:
    from packager.generator import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from types import ModuleType
from typing import Any

from mcp.packager.config import PackageConfig

logger = logging.getLogger(__name__)

yaml: ModuleType | None
try:
    import yaml as _yaml_module

    yaml = _yaml_module
except (IOError, OSError):  # pragma: no cover - optional dependency
    yaml = None


def load_config(path: str) -> PackageConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    if yaml is None:
        raise RuntimeError("PyYAML is required to load MCP packager configs.")
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return PackageConfig(**data)


def generate_package(config: PackageConfig, output_dir: str | None = None) -> Path:
    output = Path(output_dir or config.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)

    _write_readme(output, config)
    _write_pyproject(output, config)
    _write_app(output, config)
    _write_manifest(output, config)

    if config.include_cli:
        _write_cli(output, config)
    if config.include_tests:
        _write_tests(output, config)
    if config.include_docs:
        _write_docs(output, config)
    if config.include_serverless:
        _write_serverless(output, config)

    return output


def _write_readme(output: Path, config: PackageConfig) -> None:
    content = f"""# {config.name}

{config.description}

## Quickstart

```bash
python -m {config.python_package}.{config.entrypoint.replace(".py", "")}
```
"""
    (output / "README.md").write_text(content, encoding="utf-8")


def _write_pyproject(output: Path, config: PackageConfig) -> None:
    deps = "\n".join(f'  "{dep}",' for dep in config.dependencies)
    content = f"""[project]
name = "{config.python_package}"
version = "0.1.0"
description = "{config.description}"
requires-python = ">=3.10"
dependencies = [
{deps}
]

[project.scripts]
{config.python_package} = "{config.python_package}.cli:main"
"""
    (output / "pyproject.toml").write_text(content, encoding="utf-8")


def _write_app(output: Path, config: PackageConfig) -> None:
    pkg_dir = output / config.python_package
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / "__init__.py").write_text("", encoding="utf-8")

    app_content = _template_app(config)
    (pkg_dir / config.entrypoint).write_text(app_content, encoding="utf-8")


def _write_cli(output: Path, config: PackageConfig) -> None:
    pkg_dir = output / config.python_package
    cli_content = """def main():
    print("MCP package CLI placeholder")
"""
    (pkg_dir / "cli.py").write_text(cli_content, encoding="utf-8")


def _write_tests(output: Path, config: PackageConfig) -> None:
    tests_dir = output / "tests"
    tests_dir.mkdir(exist_ok=True)
    test_content = f"""def test_placeholder():
    assert "{config.name}" != ""
"""
    (tests_dir / "test_placeholder.py").write_text(test_content, encoding="utf-8")


def _write_docs(output: Path, config: PackageConfig) -> None:
    docs_dir = output / "docs"
    docs_dir.mkdir(exist_ok=True)
    (docs_dir / "usage.md").write_text("Placeholder usage docs.", encoding="utf-8")


def _write_serverless(output: Path, config: PackageConfig) -> None:
    serverless_dir = output / "serverless"
    serverless_dir.mkdir(exist_ok=True)
    target = config.serverless_target or "aws_lambda"
    handler = """def handler(event, context):
    return {"statusCode": 200, "body": "ok"}
"""
    (serverless_dir / f"{target}.py").write_text(handler, encoding="utf-8")


def _write_manifest(output: Path, config: PackageConfig) -> None:
    manifest: dict[str, Any] = {
        "name": config.name,
        "template": config.template,
        "features": config.features,
        "env": config.env,
    }
    (output / "mcp_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def _template_app(config: PackageConfig) -> str:
    if config.template == "zendesk":
        return """def main():
    print("Zendesk MCP template")
"""
    if config.template == "web_crawler":
        return """def main():
    print("Web crawler MCP template")
"""
    return """def main():
    print("Base MCP template")
"""
