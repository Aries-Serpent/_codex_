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
import logging
logger = logging.getLogger(__name__)

import json
from pathlib import Path
from typing import Any

from src.mcp.packager.config import PackageConfig

try:
    import yaml
except Exception:  # pragma: no cover - optional dependency
    yaml = None
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


def x_load_config__mutmut_orig(path: str) -> PackageConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    if yaml is None:
        raise RuntimeError("PyYAML is required to load MCP packager configs.")
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return PackageConfig(**data)


def x_load_config__mutmut_1(path: str) -> PackageConfig:
    config_path = None
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    if yaml is None:
        raise RuntimeError("PyYAML is required to load MCP packager configs.")
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return PackageConfig(**data)


def x_load_config__mutmut_2(path: str) -> PackageConfig:
    config_path = Path(None)
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    if yaml is None:
        raise RuntimeError("PyYAML is required to load MCP packager configs.")
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return PackageConfig(**data)


def x_load_config__mutmut_3(path: str) -> PackageConfig:
    config_path = Path(path)
    if config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    if yaml is None:
        raise RuntimeError("PyYAML is required to load MCP packager configs.")
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return PackageConfig(**data)


def x_load_config__mutmut_4(path: str) -> PackageConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(None)
    if yaml is None:
        raise RuntimeError("PyYAML is required to load MCP packager configs.")
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return PackageConfig(**data)


def x_load_config__mutmut_5(path: str) -> PackageConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    if yaml is not None:
        raise RuntimeError("PyYAML is required to load MCP packager configs.")
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return PackageConfig(**data)


def x_load_config__mutmut_6(path: str) -> PackageConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    if yaml is None:
        raise RuntimeError(None)
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return PackageConfig(**data)


def x_load_config__mutmut_7(path: str) -> PackageConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    if yaml is None:
        raise RuntimeError("XXPyYAML is required to load MCP packager configs.XX")
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return PackageConfig(**data)


def x_load_config__mutmut_8(path: str) -> PackageConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    if yaml is None:
        raise RuntimeError("pyyaml is required to load mcp packager configs.")
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return PackageConfig(**data)


def x_load_config__mutmut_9(path: str) -> PackageConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    if yaml is None:
        raise RuntimeError("PYYAML IS REQUIRED TO LOAD MCP PACKAGER CONFIGS.")
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return PackageConfig(**data)


def x_load_config__mutmut_10(path: str) -> PackageConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    if yaml is None:
        raise RuntimeError("PyYAML is required to load MCP packager configs.")
    data = None
    return PackageConfig(**data)


def x_load_config__mutmut_11(path: str) -> PackageConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    if yaml is None:
        raise RuntimeError("PyYAML is required to load MCP packager configs.")
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) and {}
    return PackageConfig(**data)


def x_load_config__mutmut_12(path: str) -> PackageConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    if yaml is None:
        raise RuntimeError("PyYAML is required to load MCP packager configs.")
    data = yaml.safe_load(None) or {}
    return PackageConfig(**data)


def x_load_config__mutmut_13(path: str) -> PackageConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    if yaml is None:
        raise RuntimeError("PyYAML is required to load MCP packager configs.")
    data = yaml.safe_load(config_path.read_text(encoding=None)) or {}
    return PackageConfig(**data)


def x_load_config__mutmut_14(path: str) -> PackageConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    if yaml is None:
        raise RuntimeError("PyYAML is required to load MCP packager configs.")
    data = yaml.safe_load(config_path.read_text(encoding="XXutf-8XX")) or {}
    return PackageConfig(**data)


def x_load_config__mutmut_15(path: str) -> PackageConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    if yaml is None:
        raise RuntimeError("PyYAML is required to load MCP packager configs.")
    data = yaml.safe_load(config_path.read_text(encoding="UTF-8")) or {}
    return PackageConfig(**data)

x_load_config__mutmut_mutants : ClassVar[MutantDict] = {
'x_load_config__mutmut_1': x_load_config__mutmut_1, 
    'x_load_config__mutmut_2': x_load_config__mutmut_2, 
    'x_load_config__mutmut_3': x_load_config__mutmut_3, 
    'x_load_config__mutmut_4': x_load_config__mutmut_4, 
    'x_load_config__mutmut_5': x_load_config__mutmut_5, 
    'x_load_config__mutmut_6': x_load_config__mutmut_6, 
    'x_load_config__mutmut_7': x_load_config__mutmut_7, 
    'x_load_config__mutmut_8': x_load_config__mutmut_8, 
    'x_load_config__mutmut_9': x_load_config__mutmut_9, 
    'x_load_config__mutmut_10': x_load_config__mutmut_10, 
    'x_load_config__mutmut_11': x_load_config__mutmut_11, 
    'x_load_config__mutmut_12': x_load_config__mutmut_12, 
    'x_load_config__mutmut_13': x_load_config__mutmut_13, 
    'x_load_config__mutmut_14': x_load_config__mutmut_14, 
    'x_load_config__mutmut_15': x_load_config__mutmut_15
}

def load_config(*args, **kwargs):
    result = _mutmut_trampoline(x_load_config__mutmut_orig, x_load_config__mutmut_mutants, args, kwargs)
    return result 

load_config.__signature__ = _mutmut_signature(x_load_config__mutmut_orig)
x_load_config__mutmut_orig.__name__ = 'x_load_config'


def x_generate_package__mutmut_orig(config: PackageConfig, output_dir: str | None = None) -> Path:
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


def x_generate_package__mutmut_1(config: PackageConfig, output_dir: str | None = None) -> Path:
    output = None
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


def x_generate_package__mutmut_2(config: PackageConfig, output_dir: str | None = None) -> Path:
    output = Path(None).resolve()
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


def x_generate_package__mutmut_3(config: PackageConfig, output_dir: str | None = None) -> Path:
    output = Path(output_dir and config.output_dir).resolve()
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


def x_generate_package__mutmut_4(config: PackageConfig, output_dir: str | None = None) -> Path:
    output = Path(output_dir or config.output_dir).resolve()
    output.mkdir(parents=None, exist_ok=True)

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


def x_generate_package__mutmut_5(config: PackageConfig, output_dir: str | None = None) -> Path:
    output = Path(output_dir or config.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=None)

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


def x_generate_package__mutmut_6(config: PackageConfig, output_dir: str | None = None) -> Path:
    output = Path(output_dir or config.output_dir).resolve()
    output.mkdir(exist_ok=True)

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


def x_generate_package__mutmut_7(config: PackageConfig, output_dir: str | None = None) -> Path:
    output = Path(output_dir or config.output_dir).resolve()
    output.mkdir(parents=True, )

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


def x_generate_package__mutmut_8(config: PackageConfig, output_dir: str | None = None) -> Path:
    output = Path(output_dir or config.output_dir).resolve()
    output.mkdir(parents=False, exist_ok=True)

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


def x_generate_package__mutmut_9(config: PackageConfig, output_dir: str | None = None) -> Path:
    output = Path(output_dir or config.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=False)

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


def x_generate_package__mutmut_10(config: PackageConfig, output_dir: str | None = None) -> Path:
    output = Path(output_dir or config.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)

    _write_readme(None, config)
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


def x_generate_package__mutmut_11(config: PackageConfig, output_dir: str | None = None) -> Path:
    output = Path(output_dir or config.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)

    _write_readme(output, None)
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


def x_generate_package__mutmut_12(config: PackageConfig, output_dir: str | None = None) -> Path:
    output = Path(output_dir or config.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)

    _write_readme(config)
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


def x_generate_package__mutmut_13(config: PackageConfig, output_dir: str | None = None) -> Path:
    output = Path(output_dir or config.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)

    _write_readme(output, )
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


def x_generate_package__mutmut_14(config: PackageConfig, output_dir: str | None = None) -> Path:
    output = Path(output_dir or config.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)

    _write_readme(output, config)
    _write_pyproject(None, config)
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


def x_generate_package__mutmut_15(config: PackageConfig, output_dir: str | None = None) -> Path:
    output = Path(output_dir or config.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)

    _write_readme(output, config)
    _write_pyproject(output, None)
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


def x_generate_package__mutmut_16(config: PackageConfig, output_dir: str | None = None) -> Path:
    output = Path(output_dir or config.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)

    _write_readme(output, config)
    _write_pyproject(config)
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


def x_generate_package__mutmut_17(config: PackageConfig, output_dir: str | None = None) -> Path:
    output = Path(output_dir or config.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)

    _write_readme(output, config)
    _write_pyproject(output, )
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


def x_generate_package__mutmut_18(config: PackageConfig, output_dir: str | None = None) -> Path:
    output = Path(output_dir or config.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)

    _write_readme(output, config)
    _write_pyproject(output, config)
    _write_app(None, config)
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


def x_generate_package__mutmut_19(config: PackageConfig, output_dir: str | None = None) -> Path:
    output = Path(output_dir or config.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)

    _write_readme(output, config)
    _write_pyproject(output, config)
    _write_app(output, None)
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


def x_generate_package__mutmut_20(config: PackageConfig, output_dir: str | None = None) -> Path:
    output = Path(output_dir or config.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)

    _write_readme(output, config)
    _write_pyproject(output, config)
    _write_app(config)
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


def x_generate_package__mutmut_21(config: PackageConfig, output_dir: str | None = None) -> Path:
    output = Path(output_dir or config.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)

    _write_readme(output, config)
    _write_pyproject(output, config)
    _write_app(output, )
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


def x_generate_package__mutmut_22(config: PackageConfig, output_dir: str | None = None) -> Path:
    output = Path(output_dir or config.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)

    _write_readme(output, config)
    _write_pyproject(output, config)
    _write_app(output, config)
    _write_manifest(None, config)

    if config.include_cli:
        _write_cli(output, config)
    if config.include_tests:
        _write_tests(output, config)
    if config.include_docs:
        _write_docs(output, config)
    if config.include_serverless:
        _write_serverless(output, config)

    return output


def x_generate_package__mutmut_23(config: PackageConfig, output_dir: str | None = None) -> Path:
    output = Path(output_dir or config.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)

    _write_readme(output, config)
    _write_pyproject(output, config)
    _write_app(output, config)
    _write_manifest(output, None)

    if config.include_cli:
        _write_cli(output, config)
    if config.include_tests:
        _write_tests(output, config)
    if config.include_docs:
        _write_docs(output, config)
    if config.include_serverless:
        _write_serverless(output, config)

    return output


def x_generate_package__mutmut_24(config: PackageConfig, output_dir: str | None = None) -> Path:
    output = Path(output_dir or config.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)

    _write_readme(output, config)
    _write_pyproject(output, config)
    _write_app(output, config)
    _write_manifest(config)

    if config.include_cli:
        _write_cli(output, config)
    if config.include_tests:
        _write_tests(output, config)
    if config.include_docs:
        _write_docs(output, config)
    if config.include_serverless:
        _write_serverless(output, config)

    return output


def x_generate_package__mutmut_25(config: PackageConfig, output_dir: str | None = None) -> Path:
    output = Path(output_dir or config.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)

    _write_readme(output, config)
    _write_pyproject(output, config)
    _write_app(output, config)
    _write_manifest(output, )

    if config.include_cli:
        _write_cli(output, config)
    if config.include_tests:
        _write_tests(output, config)
    if config.include_docs:
        _write_docs(output, config)
    if config.include_serverless:
        _write_serverless(output, config)

    return output


def x_generate_package__mutmut_26(config: PackageConfig, output_dir: str | None = None) -> Path:
    output = Path(output_dir or config.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)

    _write_readme(output, config)
    _write_pyproject(output, config)
    _write_app(output, config)
    _write_manifest(output, config)

    if config.include_cli:
        _write_cli(None, config)
    if config.include_tests:
        _write_tests(output, config)
    if config.include_docs:
        _write_docs(output, config)
    if config.include_serverless:
        _write_serverless(output, config)

    return output


def x_generate_package__mutmut_27(config: PackageConfig, output_dir: str | None = None) -> Path:
    output = Path(output_dir or config.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)

    _write_readme(output, config)
    _write_pyproject(output, config)
    _write_app(output, config)
    _write_manifest(output, config)

    if config.include_cli:
        _write_cli(output, None)
    if config.include_tests:
        _write_tests(output, config)
    if config.include_docs:
        _write_docs(output, config)
    if config.include_serverless:
        _write_serverless(output, config)

    return output


def x_generate_package__mutmut_28(config: PackageConfig, output_dir: str | None = None) -> Path:
    output = Path(output_dir or config.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)

    _write_readme(output, config)
    _write_pyproject(output, config)
    _write_app(output, config)
    _write_manifest(output, config)

    if config.include_cli:
        _write_cli(config)
    if config.include_tests:
        _write_tests(output, config)
    if config.include_docs:
        _write_docs(output, config)
    if config.include_serverless:
        _write_serverless(output, config)

    return output


def x_generate_package__mutmut_29(config: PackageConfig, output_dir: str | None = None) -> Path:
    output = Path(output_dir or config.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)

    _write_readme(output, config)
    _write_pyproject(output, config)
    _write_app(output, config)
    _write_manifest(output, config)

    if config.include_cli:
        _write_cli(output, )
    if config.include_tests:
        _write_tests(output, config)
    if config.include_docs:
        _write_docs(output, config)
    if config.include_serverless:
        _write_serverless(output, config)

    return output


def x_generate_package__mutmut_30(config: PackageConfig, output_dir: str | None = None) -> Path:
    output = Path(output_dir or config.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)

    _write_readme(output, config)
    _write_pyproject(output, config)
    _write_app(output, config)
    _write_manifest(output, config)

    if config.include_cli:
        _write_cli(output, config)
    if config.include_tests:
        _write_tests(None, config)
    if config.include_docs:
        _write_docs(output, config)
    if config.include_serverless:
        _write_serverless(output, config)

    return output


def x_generate_package__mutmut_31(config: PackageConfig, output_dir: str | None = None) -> Path:
    output = Path(output_dir or config.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)

    _write_readme(output, config)
    _write_pyproject(output, config)
    _write_app(output, config)
    _write_manifest(output, config)

    if config.include_cli:
        _write_cli(output, config)
    if config.include_tests:
        _write_tests(output, None)
    if config.include_docs:
        _write_docs(output, config)
    if config.include_serverless:
        _write_serverless(output, config)

    return output


def x_generate_package__mutmut_32(config: PackageConfig, output_dir: str | None = None) -> Path:
    output = Path(output_dir or config.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)

    _write_readme(output, config)
    _write_pyproject(output, config)
    _write_app(output, config)
    _write_manifest(output, config)

    if config.include_cli:
        _write_cli(output, config)
    if config.include_tests:
        _write_tests(config)
    if config.include_docs:
        _write_docs(output, config)
    if config.include_serverless:
        _write_serverless(output, config)

    return output


def x_generate_package__mutmut_33(config: PackageConfig, output_dir: str | None = None) -> Path:
    output = Path(output_dir or config.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)

    _write_readme(output, config)
    _write_pyproject(output, config)
    _write_app(output, config)
    _write_manifest(output, config)

    if config.include_cli:
        _write_cli(output, config)
    if config.include_tests:
        _write_tests(output, )
    if config.include_docs:
        _write_docs(output, config)
    if config.include_serverless:
        _write_serverless(output, config)

    return output


def x_generate_package__mutmut_34(config: PackageConfig, output_dir: str | None = None) -> Path:
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
        _write_docs(None, config)
    if config.include_serverless:
        _write_serverless(output, config)

    return output


def x_generate_package__mutmut_35(config: PackageConfig, output_dir: str | None = None) -> Path:
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
        _write_docs(output, None)
    if config.include_serverless:
        _write_serverless(output, config)

    return output


def x_generate_package__mutmut_36(config: PackageConfig, output_dir: str | None = None) -> Path:
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
        _write_docs(config)
    if config.include_serverless:
        _write_serverless(output, config)

    return output


def x_generate_package__mutmut_37(config: PackageConfig, output_dir: str | None = None) -> Path:
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
        _write_docs(output, )
    if config.include_serverless:
        _write_serverless(output, config)

    return output


def x_generate_package__mutmut_38(config: PackageConfig, output_dir: str | None = None) -> Path:
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
        _write_serverless(None, config)

    return output


def x_generate_package__mutmut_39(config: PackageConfig, output_dir: str | None = None) -> Path:
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
        _write_serverless(output, None)

    return output


def x_generate_package__mutmut_40(config: PackageConfig, output_dir: str | None = None) -> Path:
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
        _write_serverless(config)

    return output


def x_generate_package__mutmut_41(config: PackageConfig, output_dir: str | None = None) -> Path:
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
        _write_serverless(output, )

    return output

x_generate_package__mutmut_mutants : ClassVar[MutantDict] = {
'x_generate_package__mutmut_1': x_generate_package__mutmut_1, 
    'x_generate_package__mutmut_2': x_generate_package__mutmut_2, 
    'x_generate_package__mutmut_3': x_generate_package__mutmut_3, 
    'x_generate_package__mutmut_4': x_generate_package__mutmut_4, 
    'x_generate_package__mutmut_5': x_generate_package__mutmut_5, 
    'x_generate_package__mutmut_6': x_generate_package__mutmut_6, 
    'x_generate_package__mutmut_7': x_generate_package__mutmut_7, 
    'x_generate_package__mutmut_8': x_generate_package__mutmut_8, 
    'x_generate_package__mutmut_9': x_generate_package__mutmut_9, 
    'x_generate_package__mutmut_10': x_generate_package__mutmut_10, 
    'x_generate_package__mutmut_11': x_generate_package__mutmut_11, 
    'x_generate_package__mutmut_12': x_generate_package__mutmut_12, 
    'x_generate_package__mutmut_13': x_generate_package__mutmut_13, 
    'x_generate_package__mutmut_14': x_generate_package__mutmut_14, 
    'x_generate_package__mutmut_15': x_generate_package__mutmut_15, 
    'x_generate_package__mutmut_16': x_generate_package__mutmut_16, 
    'x_generate_package__mutmut_17': x_generate_package__mutmut_17, 
    'x_generate_package__mutmut_18': x_generate_package__mutmut_18, 
    'x_generate_package__mutmut_19': x_generate_package__mutmut_19, 
    'x_generate_package__mutmut_20': x_generate_package__mutmut_20, 
    'x_generate_package__mutmut_21': x_generate_package__mutmut_21, 
    'x_generate_package__mutmut_22': x_generate_package__mutmut_22, 
    'x_generate_package__mutmut_23': x_generate_package__mutmut_23, 
    'x_generate_package__mutmut_24': x_generate_package__mutmut_24, 
    'x_generate_package__mutmut_25': x_generate_package__mutmut_25, 
    'x_generate_package__mutmut_26': x_generate_package__mutmut_26, 
    'x_generate_package__mutmut_27': x_generate_package__mutmut_27, 
    'x_generate_package__mutmut_28': x_generate_package__mutmut_28, 
    'x_generate_package__mutmut_29': x_generate_package__mutmut_29, 
    'x_generate_package__mutmut_30': x_generate_package__mutmut_30, 
    'x_generate_package__mutmut_31': x_generate_package__mutmut_31, 
    'x_generate_package__mutmut_32': x_generate_package__mutmut_32, 
    'x_generate_package__mutmut_33': x_generate_package__mutmut_33, 
    'x_generate_package__mutmut_34': x_generate_package__mutmut_34, 
    'x_generate_package__mutmut_35': x_generate_package__mutmut_35, 
    'x_generate_package__mutmut_36': x_generate_package__mutmut_36, 
    'x_generate_package__mutmut_37': x_generate_package__mutmut_37, 
    'x_generate_package__mutmut_38': x_generate_package__mutmut_38, 
    'x_generate_package__mutmut_39': x_generate_package__mutmut_39, 
    'x_generate_package__mutmut_40': x_generate_package__mutmut_40, 
    'x_generate_package__mutmut_41': x_generate_package__mutmut_41
}

def generate_package(*args, **kwargs):
    result = _mutmut_trampoline(x_generate_package__mutmut_orig, x_generate_package__mutmut_mutants, args, kwargs)
    return result 

generate_package.__signature__ = _mutmut_signature(x_generate_package__mutmut_orig)
x_generate_package__mutmut_orig.__name__ = 'x_generate_package'


def x__write_readme__mutmut_orig(output: Path, config: PackageConfig) -> None:
    content = f"""# {config.name}

{config.description}

## Quickstart

```bash
python -m {config.python_package}.{config.entrypoint.replace('.py','')}
```
"""
    (output / "README.md").write_text(content, encoding="utf-8")


def x__write_readme__mutmut_1(output: Path, config: PackageConfig) -> None:
    content = None
    (output / "README.md").write_text(content, encoding="utf-8")


def x__write_readme__mutmut_2(output: Path, config: PackageConfig) -> None:
    content = f"""# {config.name}

{config.description}

## Quickstart

```bash
python -m {config.python_package}.{config.entrypoint.replace(None,'')}
```
"""
    (output / "README.md").write_text(content, encoding="utf-8")


def x__write_readme__mutmut_3(output: Path, config: PackageConfig) -> None:
    content = f"""# {config.name}

{config.description}

## Quickstart

```bash
python -m {config.python_package}.{config.entrypoint.replace('.py',None)}
```
"""
    (output / "README.md").write_text(content, encoding="utf-8")


def x__write_readme__mutmut_4(output: Path, config: PackageConfig) -> None:
    content = f"""# {config.name}

{config.description}

## Quickstart

```bash
python -m {config.python_package}.{config.entrypoint.replace('')}
```
"""
    (output / "README.md").write_text(content, encoding="utf-8")


def x__write_readme__mutmut_5(output: Path, config: PackageConfig) -> None:
    content = f"""# {config.name}

{config.description}

## Quickstart

```bash
python -m {config.python_package}.{config.entrypoint.replace('.py',)}
```
"""
    (output / "README.md").write_text(content, encoding="utf-8")


def x__write_readme__mutmut_6(output: Path, config: PackageConfig) -> None:
    content = f"""# {config.name}

{config.description}

## Quickstart

```bash
python -m {config.python_package}.{config.entrypoint.replace('XX.pyXX','')}
```
"""
    (output / "README.md").write_text(content, encoding="utf-8")


def x__write_readme__mutmut_7(output: Path, config: PackageConfig) -> None:
    content = f"""# {config.name}

{config.description}

## Quickstart

```bash
python -m {config.python_package}.{config.entrypoint.replace('.PY','')}
```
"""
    (output / "README.md").write_text(content, encoding="utf-8")


def x__write_readme__mutmut_8(output: Path, config: PackageConfig) -> None:
    content = f"""# {config.name}

{config.description}

## Quickstart

```bash
python -m {config.python_package}.{config.entrypoint.replace('.py','XXXX')}
```
"""
    (output / "README.md").write_text(content, encoding="utf-8")


def x__write_readme__mutmut_9(output: Path, config: PackageConfig) -> None:
    content = f"""# {config.name}

{config.description}

## Quickstart

```bash
python -m {config.python_package}.{config.entrypoint.replace('.py','')}
```
"""
    (output / "README.md").write_text(None, encoding="utf-8")


def x__write_readme__mutmut_10(output: Path, config: PackageConfig) -> None:
    content = f"""# {config.name}

{config.description}

## Quickstart

```bash
python -m {config.python_package}.{config.entrypoint.replace('.py','')}
```
"""
    (output / "README.md").write_text(content, encoding=None)


def x__write_readme__mutmut_11(output: Path, config: PackageConfig) -> None:
    content = f"""# {config.name}

{config.description}

## Quickstart

```bash
python -m {config.python_package}.{config.entrypoint.replace('.py','')}
```
"""
    (output / "README.md").write_text(encoding="utf-8")


def x__write_readme__mutmut_12(output: Path, config: PackageConfig) -> None:
    content = f"""# {config.name}

{config.description}

## Quickstart

```bash
python -m {config.python_package}.{config.entrypoint.replace('.py','')}
```
"""
    (output / "README.md").write_text(content, )


def x__write_readme__mutmut_13(output: Path, config: PackageConfig) -> None:
    content = f"""# {config.name}

{config.description}

## Quickstart

```bash
python -m {config.python_package}.{config.entrypoint.replace('.py','')}
```
"""
    (output * "README.md").write_text(content, encoding="utf-8")


def x__write_readme__mutmut_14(output: Path, config: PackageConfig) -> None:
    content = f"""# {config.name}

{config.description}

## Quickstart

```bash
python -m {config.python_package}.{config.entrypoint.replace('.py','')}
```
"""
    (output / "XXREADME.mdXX").write_text(content, encoding="utf-8")


def x__write_readme__mutmut_15(output: Path, config: PackageConfig) -> None:
    content = f"""# {config.name}

{config.description}

## Quickstart

```bash
python -m {config.python_package}.{config.entrypoint.replace('.py','')}
```
"""
    (output / "readme.md").write_text(content, encoding="utf-8")


def x__write_readme__mutmut_16(output: Path, config: PackageConfig) -> None:
    content = f"""# {config.name}

{config.description}

## Quickstart

```bash
python -m {config.python_package}.{config.entrypoint.replace('.py','')}
```
"""
    (output / "README.MD").write_text(content, encoding="utf-8")


def x__write_readme__mutmut_17(output: Path, config: PackageConfig) -> None:
    content = f"""# {config.name}

{config.description}

## Quickstart

```bash
python -m {config.python_package}.{config.entrypoint.replace('.py','')}
```
"""
    (output / "README.md").write_text(content, encoding="XXutf-8XX")


def x__write_readme__mutmut_18(output: Path, config: PackageConfig) -> None:
    content = f"""# {config.name}

{config.description}

## Quickstart

```bash
python -m {config.python_package}.{config.entrypoint.replace('.py','')}
```
"""
    (output / "README.md").write_text(content, encoding="UTF-8")

x__write_readme__mutmut_mutants : ClassVar[MutantDict] = {
'x__write_readme__mutmut_1': x__write_readme__mutmut_1, 
    'x__write_readme__mutmut_2': x__write_readme__mutmut_2, 
    'x__write_readme__mutmut_3': x__write_readme__mutmut_3, 
    'x__write_readme__mutmut_4': x__write_readme__mutmut_4, 
    'x__write_readme__mutmut_5': x__write_readme__mutmut_5, 
    'x__write_readme__mutmut_6': x__write_readme__mutmut_6, 
    'x__write_readme__mutmut_7': x__write_readme__mutmut_7, 
    'x__write_readme__mutmut_8': x__write_readme__mutmut_8, 
    'x__write_readme__mutmut_9': x__write_readme__mutmut_9, 
    'x__write_readme__mutmut_10': x__write_readme__mutmut_10, 
    'x__write_readme__mutmut_11': x__write_readme__mutmut_11, 
    'x__write_readme__mutmut_12': x__write_readme__mutmut_12, 
    'x__write_readme__mutmut_13': x__write_readme__mutmut_13, 
    'x__write_readme__mutmut_14': x__write_readme__mutmut_14, 
    'x__write_readme__mutmut_15': x__write_readme__mutmut_15, 
    'x__write_readme__mutmut_16': x__write_readme__mutmut_16, 
    'x__write_readme__mutmut_17': x__write_readme__mutmut_17, 
    'x__write_readme__mutmut_18': x__write_readme__mutmut_18
}

def _write_readme(*args, **kwargs):
    result = _mutmut_trampoline(x__write_readme__mutmut_orig, x__write_readme__mutmut_mutants, args, kwargs)
    return result 

_write_readme.__signature__ = _mutmut_signature(x__write_readme__mutmut_orig)
x__write_readme__mutmut_orig.__name__ = 'x__write_readme'


def x__write_pyproject__mutmut_orig(output: Path, config: PackageConfig) -> None:
    deps = "\n".join(f"  \"{dep}\"," for dep in config.dependencies)
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


def x__write_pyproject__mutmut_1(output: Path, config: PackageConfig) -> None:
    deps = None
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


def x__write_pyproject__mutmut_2(output: Path, config: PackageConfig) -> None:
    deps = "\n".join(None)
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


def x__write_pyproject__mutmut_3(output: Path, config: PackageConfig) -> None:
    deps = "XX\nXX".join(f"  \"{dep}\"," for dep in config.dependencies)
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


def x__write_pyproject__mutmut_4(output: Path, config: PackageConfig) -> None:
    deps = "\n".join(f"  \"{dep}\"," for dep in config.dependencies)
    content = None
    (output / "pyproject.toml").write_text(content, encoding="utf-8")


def x__write_pyproject__mutmut_5(output: Path, config: PackageConfig) -> None:
    deps = "\n".join(f"  \"{dep}\"," for dep in config.dependencies)
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
    (output / "pyproject.toml").write_text(None, encoding="utf-8")


def x__write_pyproject__mutmut_6(output: Path, config: PackageConfig) -> None:
    deps = "\n".join(f"  \"{dep}\"," for dep in config.dependencies)
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
    (output / "pyproject.toml").write_text(content, encoding=None)


def x__write_pyproject__mutmut_7(output: Path, config: PackageConfig) -> None:
    deps = "\n".join(f"  \"{dep}\"," for dep in config.dependencies)
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
    (output / "pyproject.toml").write_text(encoding="utf-8")


def x__write_pyproject__mutmut_8(output: Path, config: PackageConfig) -> None:
    deps = "\n".join(f"  \"{dep}\"," for dep in config.dependencies)
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
    (output / "pyproject.toml").write_text(content, )


def x__write_pyproject__mutmut_9(output: Path, config: PackageConfig) -> None:
    deps = "\n".join(f"  \"{dep}\"," for dep in config.dependencies)
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
    (output * "pyproject.toml").write_text(content, encoding="utf-8")


def x__write_pyproject__mutmut_10(output: Path, config: PackageConfig) -> None:
    deps = "\n".join(f"  \"{dep}\"," for dep in config.dependencies)
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
    (output / "XXpyproject.tomlXX").write_text(content, encoding="utf-8")


def x__write_pyproject__mutmut_11(output: Path, config: PackageConfig) -> None:
    deps = "\n".join(f"  \"{dep}\"," for dep in config.dependencies)
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
    (output / "PYPROJECT.TOML").write_text(content, encoding="utf-8")


def x__write_pyproject__mutmut_12(output: Path, config: PackageConfig) -> None:
    deps = "\n".join(f"  \"{dep}\"," for dep in config.dependencies)
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
    (output / "pyproject.toml").write_text(content, encoding="XXutf-8XX")


def x__write_pyproject__mutmut_13(output: Path, config: PackageConfig) -> None:
    deps = "\n".join(f"  \"{dep}\"," for dep in config.dependencies)
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
    (output / "pyproject.toml").write_text(content, encoding="UTF-8")

x__write_pyproject__mutmut_mutants : ClassVar[MutantDict] = {
'x__write_pyproject__mutmut_1': x__write_pyproject__mutmut_1, 
    'x__write_pyproject__mutmut_2': x__write_pyproject__mutmut_2, 
    'x__write_pyproject__mutmut_3': x__write_pyproject__mutmut_3, 
    'x__write_pyproject__mutmut_4': x__write_pyproject__mutmut_4, 
    'x__write_pyproject__mutmut_5': x__write_pyproject__mutmut_5, 
    'x__write_pyproject__mutmut_6': x__write_pyproject__mutmut_6, 
    'x__write_pyproject__mutmut_7': x__write_pyproject__mutmut_7, 
    'x__write_pyproject__mutmut_8': x__write_pyproject__mutmut_8, 
    'x__write_pyproject__mutmut_9': x__write_pyproject__mutmut_9, 
    'x__write_pyproject__mutmut_10': x__write_pyproject__mutmut_10, 
    'x__write_pyproject__mutmut_11': x__write_pyproject__mutmut_11, 
    'x__write_pyproject__mutmut_12': x__write_pyproject__mutmut_12, 
    'x__write_pyproject__mutmut_13': x__write_pyproject__mutmut_13
}

def _write_pyproject(*args, **kwargs):
    result = _mutmut_trampoline(x__write_pyproject__mutmut_orig, x__write_pyproject__mutmut_mutants, args, kwargs)
    return result 

_write_pyproject.__signature__ = _mutmut_signature(x__write_pyproject__mutmut_orig)
x__write_pyproject__mutmut_orig.__name__ = 'x__write_pyproject'


def x__write_app__mutmut_orig(output: Path, config: PackageConfig) -> None:
    pkg_dir = output / config.python_package
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / "__init__.py").write_text("", encoding="utf-8")

    app_content = _template_app(config)
    (pkg_dir / config.entrypoint).write_text(app_content, encoding="utf-8")


def x__write_app__mutmut_1(output: Path, config: PackageConfig) -> None:
    pkg_dir = None
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / "__init__.py").write_text("", encoding="utf-8")

    app_content = _template_app(config)
    (pkg_dir / config.entrypoint).write_text(app_content, encoding="utf-8")


def x__write_app__mutmut_2(output: Path, config: PackageConfig) -> None:
    pkg_dir = output * config.python_package
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / "__init__.py").write_text("", encoding="utf-8")

    app_content = _template_app(config)
    (pkg_dir / config.entrypoint).write_text(app_content, encoding="utf-8")


def x__write_app__mutmut_3(output: Path, config: PackageConfig) -> None:
    pkg_dir = output / config.python_package
    pkg_dir.mkdir(parents=None, exist_ok=True)
    (pkg_dir / "__init__.py").write_text("", encoding="utf-8")

    app_content = _template_app(config)
    (pkg_dir / config.entrypoint).write_text(app_content, encoding="utf-8")


def x__write_app__mutmut_4(output: Path, config: PackageConfig) -> None:
    pkg_dir = output / config.python_package
    pkg_dir.mkdir(parents=True, exist_ok=None)
    (pkg_dir / "__init__.py").write_text("", encoding="utf-8")

    app_content = _template_app(config)
    (pkg_dir / config.entrypoint).write_text(app_content, encoding="utf-8")


def x__write_app__mutmut_5(output: Path, config: PackageConfig) -> None:
    pkg_dir = output / config.python_package
    pkg_dir.mkdir(exist_ok=True)
    (pkg_dir / "__init__.py").write_text("", encoding="utf-8")

    app_content = _template_app(config)
    (pkg_dir / config.entrypoint).write_text(app_content, encoding="utf-8")


def x__write_app__mutmut_6(output: Path, config: PackageConfig) -> None:
    pkg_dir = output / config.python_package
    pkg_dir.mkdir(parents=True, )
    (pkg_dir / "__init__.py").write_text("", encoding="utf-8")

    app_content = _template_app(config)
    (pkg_dir / config.entrypoint).write_text(app_content, encoding="utf-8")


def x__write_app__mutmut_7(output: Path, config: PackageConfig) -> None:
    pkg_dir = output / config.python_package
    pkg_dir.mkdir(parents=False, exist_ok=True)
    (pkg_dir / "__init__.py").write_text("", encoding="utf-8")

    app_content = _template_app(config)
    (pkg_dir / config.entrypoint).write_text(app_content, encoding="utf-8")


def x__write_app__mutmut_8(output: Path, config: PackageConfig) -> None:
    pkg_dir = output / config.python_package
    pkg_dir.mkdir(parents=True, exist_ok=False)
    (pkg_dir / "__init__.py").write_text("", encoding="utf-8")

    app_content = _template_app(config)
    (pkg_dir / config.entrypoint).write_text(app_content, encoding="utf-8")


def x__write_app__mutmut_9(output: Path, config: PackageConfig) -> None:
    pkg_dir = output / config.python_package
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / "__init__.py").write_text(None, encoding="utf-8")

    app_content = _template_app(config)
    (pkg_dir / config.entrypoint).write_text(app_content, encoding="utf-8")


def x__write_app__mutmut_10(output: Path, config: PackageConfig) -> None:
    pkg_dir = output / config.python_package
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / "__init__.py").write_text("", encoding=None)

    app_content = _template_app(config)
    (pkg_dir / config.entrypoint).write_text(app_content, encoding="utf-8")


def x__write_app__mutmut_11(output: Path, config: PackageConfig) -> None:
    pkg_dir = output / config.python_package
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / "__init__.py").write_text(encoding="utf-8")

    app_content = _template_app(config)
    (pkg_dir / config.entrypoint).write_text(app_content, encoding="utf-8")


def x__write_app__mutmut_12(output: Path, config: PackageConfig) -> None:
    pkg_dir = output / config.python_package
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / "__init__.py").write_text("", )

    app_content = _template_app(config)
    (pkg_dir / config.entrypoint).write_text(app_content, encoding="utf-8")


def x__write_app__mutmut_13(output: Path, config: PackageConfig) -> None:
    pkg_dir = output / config.python_package
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir * "__init__.py").write_text("", encoding="utf-8")

    app_content = _template_app(config)
    (pkg_dir / config.entrypoint).write_text(app_content, encoding="utf-8")


def x__write_app__mutmut_14(output: Path, config: PackageConfig) -> None:
    pkg_dir = output / config.python_package
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / "XX__init__.pyXX").write_text("", encoding="utf-8")

    app_content = _template_app(config)
    (pkg_dir / config.entrypoint).write_text(app_content, encoding="utf-8")


def x__write_app__mutmut_15(output: Path, config: PackageConfig) -> None:
    pkg_dir = output / config.python_package
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / "__INIT__.PY").write_text("", encoding="utf-8")

    app_content = _template_app(config)
    (pkg_dir / config.entrypoint).write_text(app_content, encoding="utf-8")


def x__write_app__mutmut_16(output: Path, config: PackageConfig) -> None:
    pkg_dir = output / config.python_package
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / "__init__.py").write_text("XXXX", encoding="utf-8")

    app_content = _template_app(config)
    (pkg_dir / config.entrypoint).write_text(app_content, encoding="utf-8")


def x__write_app__mutmut_17(output: Path, config: PackageConfig) -> None:
    pkg_dir = output / config.python_package
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / "__init__.py").write_text("", encoding="XXutf-8XX")

    app_content = _template_app(config)
    (pkg_dir / config.entrypoint).write_text(app_content, encoding="utf-8")


def x__write_app__mutmut_18(output: Path, config: PackageConfig) -> None:
    pkg_dir = output / config.python_package
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / "__init__.py").write_text("", encoding="UTF-8")

    app_content = _template_app(config)
    (pkg_dir / config.entrypoint).write_text(app_content, encoding="utf-8")


def x__write_app__mutmut_19(output: Path, config: PackageConfig) -> None:
    pkg_dir = output / config.python_package
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / "__init__.py").write_text("", encoding="utf-8")

    app_content = None
    (pkg_dir / config.entrypoint).write_text(app_content, encoding="utf-8")


def x__write_app__mutmut_20(output: Path, config: PackageConfig) -> None:
    pkg_dir = output / config.python_package
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / "__init__.py").write_text("", encoding="utf-8")

    app_content = _template_app(None)
    (pkg_dir / config.entrypoint).write_text(app_content, encoding="utf-8")


def x__write_app__mutmut_21(output: Path, config: PackageConfig) -> None:
    pkg_dir = output / config.python_package
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / "__init__.py").write_text("", encoding="utf-8")

    app_content = _template_app(config)
    (pkg_dir / config.entrypoint).write_text(None, encoding="utf-8")


def x__write_app__mutmut_22(output: Path, config: PackageConfig) -> None:
    pkg_dir = output / config.python_package
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / "__init__.py").write_text("", encoding="utf-8")

    app_content = _template_app(config)
    (pkg_dir / config.entrypoint).write_text(app_content, encoding=None)


def x__write_app__mutmut_23(output: Path, config: PackageConfig) -> None:
    pkg_dir = output / config.python_package
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / "__init__.py").write_text("", encoding="utf-8")

    app_content = _template_app(config)
    (pkg_dir / config.entrypoint).write_text(encoding="utf-8")


def x__write_app__mutmut_24(output: Path, config: PackageConfig) -> None:
    pkg_dir = output / config.python_package
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / "__init__.py").write_text("", encoding="utf-8")

    app_content = _template_app(config)
    (pkg_dir / config.entrypoint).write_text(app_content, )


def x__write_app__mutmut_25(output: Path, config: PackageConfig) -> None:
    pkg_dir = output / config.python_package
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / "__init__.py").write_text("", encoding="utf-8")

    app_content = _template_app(config)
    (pkg_dir * config.entrypoint).write_text(app_content, encoding="utf-8")


def x__write_app__mutmut_26(output: Path, config: PackageConfig) -> None:
    pkg_dir = output / config.python_package
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / "__init__.py").write_text("", encoding="utf-8")

    app_content = _template_app(config)
    (pkg_dir / config.entrypoint).write_text(app_content, encoding="XXutf-8XX")


def x__write_app__mutmut_27(output: Path, config: PackageConfig) -> None:
    pkg_dir = output / config.python_package
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / "__init__.py").write_text("", encoding="utf-8")

    app_content = _template_app(config)
    (pkg_dir / config.entrypoint).write_text(app_content, encoding="UTF-8")

x__write_app__mutmut_mutants : ClassVar[MutantDict] = {
'x__write_app__mutmut_1': x__write_app__mutmut_1, 
    'x__write_app__mutmut_2': x__write_app__mutmut_2, 
    'x__write_app__mutmut_3': x__write_app__mutmut_3, 
    'x__write_app__mutmut_4': x__write_app__mutmut_4, 
    'x__write_app__mutmut_5': x__write_app__mutmut_5, 
    'x__write_app__mutmut_6': x__write_app__mutmut_6, 
    'x__write_app__mutmut_7': x__write_app__mutmut_7, 
    'x__write_app__mutmut_8': x__write_app__mutmut_8, 
    'x__write_app__mutmut_9': x__write_app__mutmut_9, 
    'x__write_app__mutmut_10': x__write_app__mutmut_10, 
    'x__write_app__mutmut_11': x__write_app__mutmut_11, 
    'x__write_app__mutmut_12': x__write_app__mutmut_12, 
    'x__write_app__mutmut_13': x__write_app__mutmut_13, 
    'x__write_app__mutmut_14': x__write_app__mutmut_14, 
    'x__write_app__mutmut_15': x__write_app__mutmut_15, 
    'x__write_app__mutmut_16': x__write_app__mutmut_16, 
    'x__write_app__mutmut_17': x__write_app__mutmut_17, 
    'x__write_app__mutmut_18': x__write_app__mutmut_18, 
    'x__write_app__mutmut_19': x__write_app__mutmut_19, 
    'x__write_app__mutmut_20': x__write_app__mutmut_20, 
    'x__write_app__mutmut_21': x__write_app__mutmut_21, 
    'x__write_app__mutmut_22': x__write_app__mutmut_22, 
    'x__write_app__mutmut_23': x__write_app__mutmut_23, 
    'x__write_app__mutmut_24': x__write_app__mutmut_24, 
    'x__write_app__mutmut_25': x__write_app__mutmut_25, 
    'x__write_app__mutmut_26': x__write_app__mutmut_26, 
    'x__write_app__mutmut_27': x__write_app__mutmut_27
}

def _write_app(*args, **kwargs):
    result = _mutmut_trampoline(x__write_app__mutmut_orig, x__write_app__mutmut_mutants, args, kwargs)
    return result 

_write_app.__signature__ = _mutmut_signature(x__write_app__mutmut_orig)
x__write_app__mutmut_orig.__name__ = 'x__write_app'


def x__write_cli__mutmut_orig(output: Path, config: PackageConfig) -> None:
    pkg_dir = output / config.python_package
    cli_content = """def main():
    print("MCP package CLI placeholder")
"""
    (pkg_dir / "cli.py").write_text(cli_content, encoding="utf-8")


def x__write_cli__mutmut_1(output: Path, config: PackageConfig) -> None:
    pkg_dir = None
    cli_content = """def main():
    print("MCP package CLI placeholder")
"""
    (pkg_dir / "cli.py").write_text(cli_content, encoding="utf-8")


def x__write_cli__mutmut_2(output: Path, config: PackageConfig) -> None:
    pkg_dir = output * config.python_package
    cli_content = """def main():
    print("MCP package CLI placeholder")
"""
    (pkg_dir / "cli.py").write_text(cli_content, encoding="utf-8")


def x__write_cli__mutmut_3(output: Path, config: PackageConfig) -> None:
    pkg_dir = output / config.python_package
    cli_content = None
    (pkg_dir / "cli.py").write_text(cli_content, encoding="utf-8")


def x__write_cli__mutmut_4(output: Path, config: PackageConfig) -> None:
    pkg_dir = output / config.python_package
    cli_content = """def main():
    print("MCP package CLI placeholder")
"""
    (pkg_dir / "cli.py").write_text(None, encoding="utf-8")


def x__write_cli__mutmut_5(output: Path, config: PackageConfig) -> None:
    pkg_dir = output / config.python_package
    cli_content = """def main():
    print("MCP package CLI placeholder")
"""
    (pkg_dir / "cli.py").write_text(cli_content, encoding=None)


def x__write_cli__mutmut_6(output: Path, config: PackageConfig) -> None:
    pkg_dir = output / config.python_package
    cli_content = """def main():
    print("MCP package CLI placeholder")
"""
    (pkg_dir / "cli.py").write_text(encoding="utf-8")


def x__write_cli__mutmut_7(output: Path, config: PackageConfig) -> None:
    pkg_dir = output / config.python_package
    cli_content = """def main():
    print("MCP package CLI placeholder")
"""
    (pkg_dir / "cli.py").write_text(cli_content, )


def x__write_cli__mutmut_8(output: Path, config: PackageConfig) -> None:
    pkg_dir = output / config.python_package
    cli_content = """def main():
    print("MCP package CLI placeholder")
"""
    (pkg_dir * "cli.py").write_text(cli_content, encoding="utf-8")


def x__write_cli__mutmut_9(output: Path, config: PackageConfig) -> None:
    pkg_dir = output / config.python_package
    cli_content = """def main():
    print("MCP package CLI placeholder")
"""
    (pkg_dir / "XXcli.pyXX").write_text(cli_content, encoding="utf-8")


def x__write_cli__mutmut_10(output: Path, config: PackageConfig) -> None:
    pkg_dir = output / config.python_package
    cli_content = """def main():
    print("MCP package CLI placeholder")
"""
    (pkg_dir / "CLI.PY").write_text(cli_content, encoding="utf-8")


def x__write_cli__mutmut_11(output: Path, config: PackageConfig) -> None:
    pkg_dir = output / config.python_package
    cli_content = """def main():
    print("MCP package CLI placeholder")
"""
    (pkg_dir / "cli.py").write_text(cli_content, encoding="XXutf-8XX")


def x__write_cli__mutmut_12(output: Path, config: PackageConfig) -> None:
    pkg_dir = output / config.python_package
    cli_content = """def main():
    print("MCP package CLI placeholder")
"""
    (pkg_dir / "cli.py").write_text(cli_content, encoding="UTF-8")

x__write_cli__mutmut_mutants : ClassVar[MutantDict] = {
'x__write_cli__mutmut_1': x__write_cli__mutmut_1, 
    'x__write_cli__mutmut_2': x__write_cli__mutmut_2, 
    'x__write_cli__mutmut_3': x__write_cli__mutmut_3, 
    'x__write_cli__mutmut_4': x__write_cli__mutmut_4, 
    'x__write_cli__mutmut_5': x__write_cli__mutmut_5, 
    'x__write_cli__mutmut_6': x__write_cli__mutmut_6, 
    'x__write_cli__mutmut_7': x__write_cli__mutmut_7, 
    'x__write_cli__mutmut_8': x__write_cli__mutmut_8, 
    'x__write_cli__mutmut_9': x__write_cli__mutmut_9, 
    'x__write_cli__mutmut_10': x__write_cli__mutmut_10, 
    'x__write_cli__mutmut_11': x__write_cli__mutmut_11, 
    'x__write_cli__mutmut_12': x__write_cli__mutmut_12
}

def _write_cli(*args, **kwargs):
    result = _mutmut_trampoline(x__write_cli__mutmut_orig, x__write_cli__mutmut_mutants, args, kwargs)
    return result 

_write_cli.__signature__ = _mutmut_signature(x__write_cli__mutmut_orig)
x__write_cli__mutmut_orig.__name__ = 'x__write_cli'


def x__write_tests__mutmut_orig(output: Path, config: PackageConfig) -> None:
    tests_dir = output / "tests"
    tests_dir.mkdir(exist_ok=True)
    test_content = f"""def test_placeholder():
    assert "{config.name}" != ""
"""
    (tests_dir / "test_placeholder.py").write_text(test_content, encoding="utf-8")


def x__write_tests__mutmut_1(output: Path, config: PackageConfig) -> None:
    tests_dir = None
    tests_dir.mkdir(exist_ok=True)
    test_content = f"""def test_placeholder():
    assert "{config.name}" != ""
"""
    (tests_dir / "test_placeholder.py").write_text(test_content, encoding="utf-8")


def x__write_tests__mutmut_2(output: Path, config: PackageConfig) -> None:
    tests_dir = output * "tests"
    tests_dir.mkdir(exist_ok=True)
    test_content = f"""def test_placeholder():
    assert "{config.name}" != ""
"""
    (tests_dir / "test_placeholder.py").write_text(test_content, encoding="utf-8")


def x__write_tests__mutmut_3(output: Path, config: PackageConfig) -> None:
    tests_dir = output / "XXtestsXX"
    tests_dir.mkdir(exist_ok=True)
    test_content = f"""def test_placeholder():
    assert "{config.name}" != ""
"""
    (tests_dir / "test_placeholder.py").write_text(test_content, encoding="utf-8")


def x__write_tests__mutmut_4(output: Path, config: PackageConfig) -> None:
    tests_dir = output / "TESTS"
    tests_dir.mkdir(exist_ok=True)
    test_content = f"""def test_placeholder():
    assert "{config.name}" != ""
"""
    (tests_dir / "test_placeholder.py").write_text(test_content, encoding="utf-8")


def x__write_tests__mutmut_5(output: Path, config: PackageConfig) -> None:
    tests_dir = output / "tests"
    tests_dir.mkdir(exist_ok=None)
    test_content = f"""def test_placeholder():
    assert "{config.name}" != ""
"""
    (tests_dir / "test_placeholder.py").write_text(test_content, encoding="utf-8")


def x__write_tests__mutmut_6(output: Path, config: PackageConfig) -> None:
    tests_dir = output / "tests"
    tests_dir.mkdir(exist_ok=False)
    test_content = f"""def test_placeholder():
    assert "{config.name}" != ""
"""
    (tests_dir / "test_placeholder.py").write_text(test_content, encoding="utf-8")


def x__write_tests__mutmut_7(output: Path, config: PackageConfig) -> None:
    tests_dir = output / "tests"
    tests_dir.mkdir(exist_ok=True)
    test_content = None
    (tests_dir / "test_placeholder.py").write_text(test_content, encoding="utf-8")


def x__write_tests__mutmut_8(output: Path, config: PackageConfig) -> None:
    tests_dir = output / "tests"
    tests_dir.mkdir(exist_ok=True)
    test_content = f"""def test_placeholder():
    assert "{config.name}" != ""
"""
    (tests_dir / "test_placeholder.py").write_text(None, encoding="utf-8")


def x__write_tests__mutmut_9(output: Path, config: PackageConfig) -> None:
    tests_dir = output / "tests"
    tests_dir.mkdir(exist_ok=True)
    test_content = f"""def test_placeholder():
    assert "{config.name}" != ""
"""
    (tests_dir / "test_placeholder.py").write_text(test_content, encoding=None)


def x__write_tests__mutmut_10(output: Path, config: PackageConfig) -> None:
    tests_dir = output / "tests"
    tests_dir.mkdir(exist_ok=True)
    test_content = f"""def test_placeholder():
    assert "{config.name}" != ""
"""
    (tests_dir / "test_placeholder.py").write_text(encoding="utf-8")


def x__write_tests__mutmut_11(output: Path, config: PackageConfig) -> None:
    tests_dir = output / "tests"
    tests_dir.mkdir(exist_ok=True)
    test_content = f"""def test_placeholder():
    assert "{config.name}" != ""
"""
    (tests_dir / "test_placeholder.py").write_text(test_content, )


def x__write_tests__mutmut_12(output: Path, config: PackageConfig) -> None:
    tests_dir = output / "tests"
    tests_dir.mkdir(exist_ok=True)
    test_content = f"""def test_placeholder():
    assert "{config.name}" != ""
"""
    (tests_dir * "test_placeholder.py").write_text(test_content, encoding="utf-8")


def x__write_tests__mutmut_13(output: Path, config: PackageConfig) -> None:
    tests_dir = output / "tests"
    tests_dir.mkdir(exist_ok=True)
    test_content = f"""def test_placeholder():
    assert "{config.name}" != ""
"""
    (tests_dir / "XXtest_placeholder.pyXX").write_text(test_content, encoding="utf-8")


def x__write_tests__mutmut_14(output: Path, config: PackageConfig) -> None:
    tests_dir = output / "tests"
    tests_dir.mkdir(exist_ok=True)
    test_content = f"""def test_placeholder():
    assert "{config.name}" != ""
"""
    (tests_dir / "TEST_PLACEHOLDER.PY").write_text(test_content, encoding="utf-8")


def x__write_tests__mutmut_15(output: Path, config: PackageConfig) -> None:
    tests_dir = output / "tests"
    tests_dir.mkdir(exist_ok=True)
    test_content = f"""def test_placeholder():
    assert "{config.name}" != ""
"""
    (tests_dir / "test_placeholder.py").write_text(test_content, encoding="XXutf-8XX")


def x__write_tests__mutmut_16(output: Path, config: PackageConfig) -> None:
    tests_dir = output / "tests"
    tests_dir.mkdir(exist_ok=True)
    test_content = f"""def test_placeholder():
    assert "{config.name}" != ""
"""
    (tests_dir / "test_placeholder.py").write_text(test_content, encoding="UTF-8")

x__write_tests__mutmut_mutants : ClassVar[MutantDict] = {
'x__write_tests__mutmut_1': x__write_tests__mutmut_1, 
    'x__write_tests__mutmut_2': x__write_tests__mutmut_2, 
    'x__write_tests__mutmut_3': x__write_tests__mutmut_3, 
    'x__write_tests__mutmut_4': x__write_tests__mutmut_4, 
    'x__write_tests__mutmut_5': x__write_tests__mutmut_5, 
    'x__write_tests__mutmut_6': x__write_tests__mutmut_6, 
    'x__write_tests__mutmut_7': x__write_tests__mutmut_7, 
    'x__write_tests__mutmut_8': x__write_tests__mutmut_8, 
    'x__write_tests__mutmut_9': x__write_tests__mutmut_9, 
    'x__write_tests__mutmut_10': x__write_tests__mutmut_10, 
    'x__write_tests__mutmut_11': x__write_tests__mutmut_11, 
    'x__write_tests__mutmut_12': x__write_tests__mutmut_12, 
    'x__write_tests__mutmut_13': x__write_tests__mutmut_13, 
    'x__write_tests__mutmut_14': x__write_tests__mutmut_14, 
    'x__write_tests__mutmut_15': x__write_tests__mutmut_15, 
    'x__write_tests__mutmut_16': x__write_tests__mutmut_16
}

def _write_tests(*args, **kwargs):
    result = _mutmut_trampoline(x__write_tests__mutmut_orig, x__write_tests__mutmut_mutants, args, kwargs)
    return result 

_write_tests.__signature__ = _mutmut_signature(x__write_tests__mutmut_orig)
x__write_tests__mutmut_orig.__name__ = 'x__write_tests'


def x__write_docs__mutmut_orig(output: Path, config: PackageConfig) -> None:
    docs_dir = output / "docs"
    docs_dir.mkdir(exist_ok=True)
    (docs_dir / "usage.md").write_text("Placeholder usage docs.", encoding="utf-8")


def x__write_docs__mutmut_1(output: Path, config: PackageConfig) -> None:
    docs_dir = None
    docs_dir.mkdir(exist_ok=True)
    (docs_dir / "usage.md").write_text("Placeholder usage docs.", encoding="utf-8")


def x__write_docs__mutmut_2(output: Path, config: PackageConfig) -> None:
    docs_dir = output * "docs"
    docs_dir.mkdir(exist_ok=True)
    (docs_dir / "usage.md").write_text("Placeholder usage docs.", encoding="utf-8")


def x__write_docs__mutmut_3(output: Path, config: PackageConfig) -> None:
    docs_dir = output / "XXdocsXX"
    docs_dir.mkdir(exist_ok=True)
    (docs_dir / "usage.md").write_text("Placeholder usage docs.", encoding="utf-8")


def x__write_docs__mutmut_4(output: Path, config: PackageConfig) -> None:
    docs_dir = output / "DOCS"
    docs_dir.mkdir(exist_ok=True)
    (docs_dir / "usage.md").write_text("Placeholder usage docs.", encoding="utf-8")


def x__write_docs__mutmut_5(output: Path, config: PackageConfig) -> None:
    docs_dir = output / "docs"
    docs_dir.mkdir(exist_ok=None)
    (docs_dir / "usage.md").write_text("Placeholder usage docs.", encoding="utf-8")


def x__write_docs__mutmut_6(output: Path, config: PackageConfig) -> None:
    docs_dir = output / "docs"
    docs_dir.mkdir(exist_ok=False)
    (docs_dir / "usage.md").write_text("Placeholder usage docs.", encoding="utf-8")


def x__write_docs__mutmut_7(output: Path, config: PackageConfig) -> None:
    docs_dir = output / "docs"
    docs_dir.mkdir(exist_ok=True)
    (docs_dir / "usage.md").write_text(None, encoding="utf-8")


def x__write_docs__mutmut_8(output: Path, config: PackageConfig) -> None:
    docs_dir = output / "docs"
    docs_dir.mkdir(exist_ok=True)
    (docs_dir / "usage.md").write_text("Placeholder usage docs.", encoding=None)


def x__write_docs__mutmut_9(output: Path, config: PackageConfig) -> None:
    docs_dir = output / "docs"
    docs_dir.mkdir(exist_ok=True)
    (docs_dir / "usage.md").write_text(encoding="utf-8")


def x__write_docs__mutmut_10(output: Path, config: PackageConfig) -> None:
    docs_dir = output / "docs"
    docs_dir.mkdir(exist_ok=True)
    (docs_dir / "usage.md").write_text("Placeholder usage docs.", )


def x__write_docs__mutmut_11(output: Path, config: PackageConfig) -> None:
    docs_dir = output / "docs"
    docs_dir.mkdir(exist_ok=True)
    (docs_dir * "usage.md").write_text("Placeholder usage docs.", encoding="utf-8")


def x__write_docs__mutmut_12(output: Path, config: PackageConfig) -> None:
    docs_dir = output / "docs"
    docs_dir.mkdir(exist_ok=True)
    (docs_dir / "XXusage.mdXX").write_text("Placeholder usage docs.", encoding="utf-8")


def x__write_docs__mutmut_13(output: Path, config: PackageConfig) -> None:
    docs_dir = output / "docs"
    docs_dir.mkdir(exist_ok=True)
    (docs_dir / "USAGE.MD").write_text("Placeholder usage docs.", encoding="utf-8")


def x__write_docs__mutmut_14(output: Path, config: PackageConfig) -> None:
    docs_dir = output / "docs"
    docs_dir.mkdir(exist_ok=True)
    (docs_dir / "usage.md").write_text("XXPlaceholder usage docs.XX", encoding="utf-8")


def x__write_docs__mutmut_15(output: Path, config: PackageConfig) -> None:
    docs_dir = output / "docs"
    docs_dir.mkdir(exist_ok=True)
    (docs_dir / "usage.md").write_text("placeholder usage docs.", encoding="utf-8")


def x__write_docs__mutmut_16(output: Path, config: PackageConfig) -> None:
    docs_dir = output / "docs"
    docs_dir.mkdir(exist_ok=True)
    (docs_dir / "usage.md").write_text("PLACEHOLDER USAGE DOCS.", encoding="utf-8")


def x__write_docs__mutmut_17(output: Path, config: PackageConfig) -> None:
    docs_dir = output / "docs"
    docs_dir.mkdir(exist_ok=True)
    (docs_dir / "usage.md").write_text("Placeholder usage docs.", encoding="XXutf-8XX")


def x__write_docs__mutmut_18(output: Path, config: PackageConfig) -> None:
    docs_dir = output / "docs"
    docs_dir.mkdir(exist_ok=True)
    (docs_dir / "usage.md").write_text("Placeholder usage docs.", encoding="UTF-8")

x__write_docs__mutmut_mutants : ClassVar[MutantDict] = {
'x__write_docs__mutmut_1': x__write_docs__mutmut_1, 
    'x__write_docs__mutmut_2': x__write_docs__mutmut_2, 
    'x__write_docs__mutmut_3': x__write_docs__mutmut_3, 
    'x__write_docs__mutmut_4': x__write_docs__mutmut_4, 
    'x__write_docs__mutmut_5': x__write_docs__mutmut_5, 
    'x__write_docs__mutmut_6': x__write_docs__mutmut_6, 
    'x__write_docs__mutmut_7': x__write_docs__mutmut_7, 
    'x__write_docs__mutmut_8': x__write_docs__mutmut_8, 
    'x__write_docs__mutmut_9': x__write_docs__mutmut_9, 
    'x__write_docs__mutmut_10': x__write_docs__mutmut_10, 
    'x__write_docs__mutmut_11': x__write_docs__mutmut_11, 
    'x__write_docs__mutmut_12': x__write_docs__mutmut_12, 
    'x__write_docs__mutmut_13': x__write_docs__mutmut_13, 
    'x__write_docs__mutmut_14': x__write_docs__mutmut_14, 
    'x__write_docs__mutmut_15': x__write_docs__mutmut_15, 
    'x__write_docs__mutmut_16': x__write_docs__mutmut_16, 
    'x__write_docs__mutmut_17': x__write_docs__mutmut_17, 
    'x__write_docs__mutmut_18': x__write_docs__mutmut_18
}

def _write_docs(*args, **kwargs):
    result = _mutmut_trampoline(x__write_docs__mutmut_orig, x__write_docs__mutmut_mutants, args, kwargs)
    return result 

_write_docs.__signature__ = _mutmut_signature(x__write_docs__mutmut_orig)
x__write_docs__mutmut_orig.__name__ = 'x__write_docs'


def x__write_serverless__mutmut_orig(output: Path, config: PackageConfig) -> None:
    serverless_dir = output / "serverless"
    serverless_dir.mkdir(exist_ok=True)
    target = config.serverless_target or "aws_lambda"
    handler = """def handler(event, context):
    return {"statusCode": 200, "body": "ok"}
"""
    (serverless_dir / f"{target}.py").write_text(handler, encoding="utf-8")


def x__write_serverless__mutmut_1(output: Path, config: PackageConfig) -> None:
    serverless_dir = None
    serverless_dir.mkdir(exist_ok=True)
    target = config.serverless_target or "aws_lambda"
    handler = """def handler(event, context):
    return {"statusCode": 200, "body": "ok"}
"""
    (serverless_dir / f"{target}.py").write_text(handler, encoding="utf-8")


def x__write_serverless__mutmut_2(output: Path, config: PackageConfig) -> None:
    serverless_dir = output * "serverless"
    serverless_dir.mkdir(exist_ok=True)
    target = config.serverless_target or "aws_lambda"
    handler = """def handler(event, context):
    return {"statusCode": 200, "body": "ok"}
"""
    (serverless_dir / f"{target}.py").write_text(handler, encoding="utf-8")


def x__write_serverless__mutmut_3(output: Path, config: PackageConfig) -> None:
    serverless_dir = output / "XXserverlessXX"
    serverless_dir.mkdir(exist_ok=True)
    target = config.serverless_target or "aws_lambda"
    handler = """def handler(event, context):
    return {"statusCode": 200, "body": "ok"}
"""
    (serverless_dir / f"{target}.py").write_text(handler, encoding="utf-8")


def x__write_serverless__mutmut_4(output: Path, config: PackageConfig) -> None:
    serverless_dir = output / "SERVERLESS"
    serverless_dir.mkdir(exist_ok=True)
    target = config.serverless_target or "aws_lambda"
    handler = """def handler(event, context):
    return {"statusCode": 200, "body": "ok"}
"""
    (serverless_dir / f"{target}.py").write_text(handler, encoding="utf-8")


def x__write_serverless__mutmut_5(output: Path, config: PackageConfig) -> None:
    serverless_dir = output / "serverless"
    serverless_dir.mkdir(exist_ok=None)
    target = config.serverless_target or "aws_lambda"
    handler = """def handler(event, context):
    return {"statusCode": 200, "body": "ok"}
"""
    (serverless_dir / f"{target}.py").write_text(handler, encoding="utf-8")


def x__write_serverless__mutmut_6(output: Path, config: PackageConfig) -> None:
    serverless_dir = output / "serverless"
    serverless_dir.mkdir(exist_ok=False)
    target = config.serverless_target or "aws_lambda"
    handler = """def handler(event, context):
    return {"statusCode": 200, "body": "ok"}
"""
    (serverless_dir / f"{target}.py").write_text(handler, encoding="utf-8")


def x__write_serverless__mutmut_7(output: Path, config: PackageConfig) -> None:
    serverless_dir = output / "serverless"
    serverless_dir.mkdir(exist_ok=True)
    target = None
    handler = """def handler(event, context):
    return {"statusCode": 200, "body": "ok"}
"""
    (serverless_dir / f"{target}.py").write_text(handler, encoding="utf-8")


def x__write_serverless__mutmut_8(output: Path, config: PackageConfig) -> None:
    serverless_dir = output / "serverless"
    serverless_dir.mkdir(exist_ok=True)
    target = config.serverless_target and "aws_lambda"
    handler = """def handler(event, context):
    return {"statusCode": 200, "body": "ok"}
"""
    (serverless_dir / f"{target}.py").write_text(handler, encoding="utf-8")


def x__write_serverless__mutmut_9(output: Path, config: PackageConfig) -> None:
    serverless_dir = output / "serverless"
    serverless_dir.mkdir(exist_ok=True)
    target = config.serverless_target or "XXaws_lambdaXX"
    handler = """def handler(event, context):
    return {"statusCode": 200, "body": "ok"}
"""
    (serverless_dir / f"{target}.py").write_text(handler, encoding="utf-8")


def x__write_serverless__mutmut_10(output: Path, config: PackageConfig) -> None:
    serverless_dir = output / "serverless"
    serverless_dir.mkdir(exist_ok=True)
    target = config.serverless_target or "AWS_LAMBDA"
    handler = """def handler(event, context):
    return {"statusCode": 200, "body": "ok"}
"""
    (serverless_dir / f"{target}.py").write_text(handler, encoding="utf-8")


def x__write_serverless__mutmut_11(output: Path, config: PackageConfig) -> None:
    serverless_dir = output / "serverless"
    serverless_dir.mkdir(exist_ok=True)
    target = config.serverless_target or "aws_lambda"
    handler = None
    (serverless_dir / f"{target}.py").write_text(handler, encoding="utf-8")


def x__write_serverless__mutmut_12(output: Path, config: PackageConfig) -> None:
    serverless_dir = output / "serverless"
    serverless_dir.mkdir(exist_ok=True)
    target = config.serverless_target or "aws_lambda"
    handler = """def handler(event, context):
    return {"statusCode": 200, "body": "ok"}
"""
    (serverless_dir / f"{target}.py").write_text(None, encoding="utf-8")


def x__write_serverless__mutmut_13(output: Path, config: PackageConfig) -> None:
    serverless_dir = output / "serverless"
    serverless_dir.mkdir(exist_ok=True)
    target = config.serverless_target or "aws_lambda"
    handler = """def handler(event, context):
    return {"statusCode": 200, "body": "ok"}
"""
    (serverless_dir / f"{target}.py").write_text(handler, encoding=None)


def x__write_serverless__mutmut_14(output: Path, config: PackageConfig) -> None:
    serverless_dir = output / "serverless"
    serverless_dir.mkdir(exist_ok=True)
    target = config.serverless_target or "aws_lambda"
    handler = """def handler(event, context):
    return {"statusCode": 200, "body": "ok"}
"""
    (serverless_dir / f"{target}.py").write_text(encoding="utf-8")


def x__write_serverless__mutmut_15(output: Path, config: PackageConfig) -> None:
    serverless_dir = output / "serverless"
    serverless_dir.mkdir(exist_ok=True)
    target = config.serverless_target or "aws_lambda"
    handler = """def handler(event, context):
    return {"statusCode": 200, "body": "ok"}
"""
    (serverless_dir / f"{target}.py").write_text(handler, )


def x__write_serverless__mutmut_16(output: Path, config: PackageConfig) -> None:
    serverless_dir = output / "serverless"
    serverless_dir.mkdir(exist_ok=True)
    target = config.serverless_target or "aws_lambda"
    handler = """def handler(event, context):
    return {"statusCode": 200, "body": "ok"}
"""
    (serverless_dir * f"{target}.py").write_text(handler, encoding="utf-8")


def x__write_serverless__mutmut_17(output: Path, config: PackageConfig) -> None:
    serverless_dir = output / "serverless"
    serverless_dir.mkdir(exist_ok=True)
    target = config.serverless_target or "aws_lambda"
    handler = """def handler(event, context):
    return {"statusCode": 200, "body": "ok"}
"""
    (serverless_dir / f"{target}.py").write_text(handler, encoding="XXutf-8XX")


def x__write_serverless__mutmut_18(output: Path, config: PackageConfig) -> None:
    serverless_dir = output / "serverless"
    serverless_dir.mkdir(exist_ok=True)
    target = config.serverless_target or "aws_lambda"
    handler = """def handler(event, context):
    return {"statusCode": 200, "body": "ok"}
"""
    (serverless_dir / f"{target}.py").write_text(handler, encoding="UTF-8")

x__write_serverless__mutmut_mutants : ClassVar[MutantDict] = {
'x__write_serverless__mutmut_1': x__write_serverless__mutmut_1, 
    'x__write_serverless__mutmut_2': x__write_serverless__mutmut_2, 
    'x__write_serverless__mutmut_3': x__write_serverless__mutmut_3, 
    'x__write_serverless__mutmut_4': x__write_serverless__mutmut_4, 
    'x__write_serverless__mutmut_5': x__write_serverless__mutmut_5, 
    'x__write_serverless__mutmut_6': x__write_serverless__mutmut_6, 
    'x__write_serverless__mutmut_7': x__write_serverless__mutmut_7, 
    'x__write_serverless__mutmut_8': x__write_serverless__mutmut_8, 
    'x__write_serverless__mutmut_9': x__write_serverless__mutmut_9, 
    'x__write_serverless__mutmut_10': x__write_serverless__mutmut_10, 
    'x__write_serverless__mutmut_11': x__write_serverless__mutmut_11, 
    'x__write_serverless__mutmut_12': x__write_serverless__mutmut_12, 
    'x__write_serverless__mutmut_13': x__write_serverless__mutmut_13, 
    'x__write_serverless__mutmut_14': x__write_serverless__mutmut_14, 
    'x__write_serverless__mutmut_15': x__write_serverless__mutmut_15, 
    'x__write_serverless__mutmut_16': x__write_serverless__mutmut_16, 
    'x__write_serverless__mutmut_17': x__write_serverless__mutmut_17, 
    'x__write_serverless__mutmut_18': x__write_serverless__mutmut_18
}

def _write_serverless(*args, **kwargs):
    result = _mutmut_trampoline(x__write_serverless__mutmut_orig, x__write_serverless__mutmut_mutants, args, kwargs)
    return result 

_write_serverless.__signature__ = _mutmut_signature(x__write_serverless__mutmut_orig)
x__write_serverless__mutmut_orig.__name__ = 'x__write_serverless'


def x__write_manifest__mutmut_orig(output: Path, config: PackageConfig) -> None:
    manifest: dict[str, Any] = {
        "name": config.name,
        "template": config.template,
        "features": config.features,
        "env": config.env,
    }
    (output / "mcp_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def x__write_manifest__mutmut_1(output: Path, config: PackageConfig) -> None:
    manifest: dict[str, Any] = None
    (output / "mcp_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def x__write_manifest__mutmut_2(output: Path, config: PackageConfig) -> None:
    manifest: dict[str, Any] = {
        "XXnameXX": config.name,
        "template": config.template,
        "features": config.features,
        "env": config.env,
    }
    (output / "mcp_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def x__write_manifest__mutmut_3(output: Path, config: PackageConfig) -> None:
    manifest: dict[str, Any] = {
        "NAME": config.name,
        "template": config.template,
        "features": config.features,
        "env": config.env,
    }
    (output / "mcp_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def x__write_manifest__mutmut_4(output: Path, config: PackageConfig) -> None:
    manifest: dict[str, Any] = {
        "name": config.name,
        "XXtemplateXX": config.template,
        "features": config.features,
        "env": config.env,
    }
    (output / "mcp_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def x__write_manifest__mutmut_5(output: Path, config: PackageConfig) -> None:
    manifest: dict[str, Any] = {
        "name": config.name,
        "TEMPLATE": config.template,
        "features": config.features,
        "env": config.env,
    }
    (output / "mcp_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def x__write_manifest__mutmut_6(output: Path, config: PackageConfig) -> None:
    manifest: dict[str, Any] = {
        "name": config.name,
        "template": config.template,
        "XXfeaturesXX": config.features,
        "env": config.env,
    }
    (output / "mcp_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def x__write_manifest__mutmut_7(output: Path, config: PackageConfig) -> None:
    manifest: dict[str, Any] = {
        "name": config.name,
        "template": config.template,
        "FEATURES": config.features,
        "env": config.env,
    }
    (output / "mcp_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def x__write_manifest__mutmut_8(output: Path, config: PackageConfig) -> None:
    manifest: dict[str, Any] = {
        "name": config.name,
        "template": config.template,
        "features": config.features,
        "XXenvXX": config.env,
    }
    (output / "mcp_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def x__write_manifest__mutmut_9(output: Path, config: PackageConfig) -> None:
    manifest: dict[str, Any] = {
        "name": config.name,
        "template": config.template,
        "features": config.features,
        "ENV": config.env,
    }
    (output / "mcp_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def x__write_manifest__mutmut_10(output: Path, config: PackageConfig) -> None:
    manifest: dict[str, Any] = {
        "name": config.name,
        "template": config.template,
        "features": config.features,
        "env": config.env,
    }
    (output / "mcp_manifest.json").write_text(None, encoding="utf-8")


def x__write_manifest__mutmut_11(output: Path, config: PackageConfig) -> None:
    manifest: dict[str, Any] = {
        "name": config.name,
        "template": config.template,
        "features": config.features,
        "env": config.env,
    }
    (output / "mcp_manifest.json").write_text(json.dumps(manifest, indent=2), encoding=None)


def x__write_manifest__mutmut_12(output: Path, config: PackageConfig) -> None:
    manifest: dict[str, Any] = {
        "name": config.name,
        "template": config.template,
        "features": config.features,
        "env": config.env,
    }
    (output / "mcp_manifest.json").write_text(encoding="utf-8")


def x__write_manifest__mutmut_13(output: Path, config: PackageConfig) -> None:
    manifest: dict[str, Any] = {
        "name": config.name,
        "template": config.template,
        "features": config.features,
        "env": config.env,
    }
    (output / "mcp_manifest.json").write_text(json.dumps(manifest, indent=2), )


def x__write_manifest__mutmut_14(output: Path, config: PackageConfig) -> None:
    manifest: dict[str, Any] = {
        "name": config.name,
        "template": config.template,
        "features": config.features,
        "env": config.env,
    }
    (output * "mcp_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def x__write_manifest__mutmut_15(output: Path, config: PackageConfig) -> None:
    manifest: dict[str, Any] = {
        "name": config.name,
        "template": config.template,
        "features": config.features,
        "env": config.env,
    }
    (output / "XXmcp_manifest.jsonXX").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def x__write_manifest__mutmut_16(output: Path, config: PackageConfig) -> None:
    manifest: dict[str, Any] = {
        "name": config.name,
        "template": config.template,
        "features": config.features,
        "env": config.env,
    }
    (output / "MCP_MANIFEST.JSON").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def x__write_manifest__mutmut_17(output: Path, config: PackageConfig) -> None:
    manifest: dict[str, Any] = {
        "name": config.name,
        "template": config.template,
        "features": config.features,
        "env": config.env,
    }
    (output / "mcp_manifest.json").write_text(json.dumps(None, indent=2), encoding="utf-8")


def x__write_manifest__mutmut_18(output: Path, config: PackageConfig) -> None:
    manifest: dict[str, Any] = {
        "name": config.name,
        "template": config.template,
        "features": config.features,
        "env": config.env,
    }
    (output / "mcp_manifest.json").write_text(json.dumps(manifest, indent=None), encoding="utf-8")


def x__write_manifest__mutmut_19(output: Path, config: PackageConfig) -> None:
    manifest: dict[str, Any] = {
        "name": config.name,
        "template": config.template,
        "features": config.features,
        "env": config.env,
    }
    (output / "mcp_manifest.json").write_text(json.dumps(indent=2), encoding="utf-8")


def x__write_manifest__mutmut_20(output: Path, config: PackageConfig) -> None:
    manifest: dict[str, Any] = {
        "name": config.name,
        "template": config.template,
        "features": config.features,
        "env": config.env,
    }
    (output / "mcp_manifest.json").write_text(json.dumps(manifest, ), encoding="utf-8")


def x__write_manifest__mutmut_21(output: Path, config: PackageConfig) -> None:
    manifest: dict[str, Any] = {
        "name": config.name,
        "template": config.template,
        "features": config.features,
        "env": config.env,
    }
    (output / "mcp_manifest.json").write_text(json.dumps(manifest, indent=3), encoding="utf-8")


def x__write_manifest__mutmut_22(output: Path, config: PackageConfig) -> None:
    manifest: dict[str, Any] = {
        "name": config.name,
        "template": config.template,
        "features": config.features,
        "env": config.env,
    }
    (output / "mcp_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="XXutf-8XX")


def x__write_manifest__mutmut_23(output: Path, config: PackageConfig) -> None:
    manifest: dict[str, Any] = {
        "name": config.name,
        "template": config.template,
        "features": config.features,
        "env": config.env,
    }
    (output / "mcp_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="UTF-8")

x__write_manifest__mutmut_mutants : ClassVar[MutantDict] = {
'x__write_manifest__mutmut_1': x__write_manifest__mutmut_1, 
    'x__write_manifest__mutmut_2': x__write_manifest__mutmut_2, 
    'x__write_manifest__mutmut_3': x__write_manifest__mutmut_3, 
    'x__write_manifest__mutmut_4': x__write_manifest__mutmut_4, 
    'x__write_manifest__mutmut_5': x__write_manifest__mutmut_5, 
    'x__write_manifest__mutmut_6': x__write_manifest__mutmut_6, 
    'x__write_manifest__mutmut_7': x__write_manifest__mutmut_7, 
    'x__write_manifest__mutmut_8': x__write_manifest__mutmut_8, 
    'x__write_manifest__mutmut_9': x__write_manifest__mutmut_9, 
    'x__write_manifest__mutmut_10': x__write_manifest__mutmut_10, 
    'x__write_manifest__mutmut_11': x__write_manifest__mutmut_11, 
    'x__write_manifest__mutmut_12': x__write_manifest__mutmut_12, 
    'x__write_manifest__mutmut_13': x__write_manifest__mutmut_13, 
    'x__write_manifest__mutmut_14': x__write_manifest__mutmut_14, 
    'x__write_manifest__mutmut_15': x__write_manifest__mutmut_15, 
    'x__write_manifest__mutmut_16': x__write_manifest__mutmut_16, 
    'x__write_manifest__mutmut_17': x__write_manifest__mutmut_17, 
    'x__write_manifest__mutmut_18': x__write_manifest__mutmut_18, 
    'x__write_manifest__mutmut_19': x__write_manifest__mutmut_19, 
    'x__write_manifest__mutmut_20': x__write_manifest__mutmut_20, 
    'x__write_manifest__mutmut_21': x__write_manifest__mutmut_21, 
    'x__write_manifest__mutmut_22': x__write_manifest__mutmut_22, 
    'x__write_manifest__mutmut_23': x__write_manifest__mutmut_23
}

def _write_manifest(*args, **kwargs):
    result = _mutmut_trampoline(x__write_manifest__mutmut_orig, x__write_manifest__mutmut_mutants, args, kwargs)
    return result 

_write_manifest.__signature__ = _mutmut_signature(x__write_manifest__mutmut_orig)
x__write_manifest__mutmut_orig.__name__ = 'x__write_manifest'


def x__template_app__mutmut_orig(config: PackageConfig) -> str:
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


def x__template_app__mutmut_1(config: PackageConfig) -> str:
    if config.template != "zendesk":
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


def x__template_app__mutmut_2(config: PackageConfig) -> str:
    if config.template == "XXzendeskXX":
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


def x__template_app__mutmut_3(config: PackageConfig) -> str:
    if config.template == "ZENDESK":
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


def x__template_app__mutmut_4(config: PackageConfig) -> str:
    if config.template == "zendesk":
        return """def main():
    print("Zendesk MCP template")
"""
    if config.template != "web_crawler":
        return """def main():
    print("Web crawler MCP template")
"""
    return """def main():
    print("Base MCP template")
"""


def x__template_app__mutmut_5(config: PackageConfig) -> str:
    if config.template == "zendesk":
        return """def main():
    print("Zendesk MCP template")
"""
    if config.template == "XXweb_crawlerXX":
        return """def main():
    print("Web crawler MCP template")
"""
    return """def main():
    print("Base MCP template")
"""


def x__template_app__mutmut_6(config: PackageConfig) -> str:
    if config.template == "zendesk":
        return """def main():
    print("Zendesk MCP template")
"""
    if config.template == "WEB_CRAWLER":
        return """def main():
    print("Web crawler MCP template")
"""
    return """def main():
    print("Base MCP template")
"""

x__template_app__mutmut_mutants : ClassVar[MutantDict] = {
'x__template_app__mutmut_1': x__template_app__mutmut_1, 
    'x__template_app__mutmut_2': x__template_app__mutmut_2, 
    'x__template_app__mutmut_3': x__template_app__mutmut_3, 
    'x__template_app__mutmut_4': x__template_app__mutmut_4, 
    'x__template_app__mutmut_5': x__template_app__mutmut_5, 
    'x__template_app__mutmut_6': x__template_app__mutmut_6
}

def _template_app(*args, **kwargs):
    result = _mutmut_trampoline(x__template_app__mutmut_orig, x__template_app__mutmut_mutants, args, kwargs)
    return result 

_template_app.__signature__ = _mutmut_signature(x__template_app__mutmut_orig)
x__template_app__mutmut_orig.__name__ = 'x__template_app'
