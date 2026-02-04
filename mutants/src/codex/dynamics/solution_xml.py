"""
Solution Xml Module

This module provides functionality for solution xml.

Usage:
    from dynamics.solution_xml import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)
"""Emit unmanaged Dynamics 365 Solution XML from config-as-data."""


import json
from pathlib import Path

try:
    from defusedxml.ElementTree import tostring
    # Note: defusedxml.ElementTree doesn't re-export Element/SubElement
    # We use xml.etree for construction (safe) and defusedxml for serialization (extra safety)
    from xml.etree.ElementTree import Element, SubElement
except ImportError as exc:
    logger.debug(f"ImportError: {exc}")
    raise ImportError(
        "defusedxml is required for safe XML handling in solution_xml; install it via pip"
    ) from exc

from pydantic import AliasChoices, BaseModel, Field

from codex.evidence import utc_now

__all__ = [
    "LocalizedName",
    "Publisher",
    "RootComponent",
    "SolutionManifestConfig",
    "build_solution_tree",
    "emit_solution_xml",
    "load_solution_manifest",
]
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


class LocalizedName(BaseModel):
    """Localized solution label."""

    description: str = Field(validation_alias=AliasChoices("description", "Description"))
    languagecode: int = Field(validation_alias=AliasChoices("languagecode", "LanguageCode"))

    model_config = {
        "populate_by_name": True,
        "extra": "ignore",
    }


class Publisher(BaseModel):
    """Minimal publisher definition for unmanaged solutions."""

    prefix: str = Field(validation_alias=AliasChoices("prefix", "Prefix"))
    unique_name: str = Field(validation_alias=AliasChoices("unique_name", "UniqueName"))
    friendly_name: str | None = Field(
        default=None,
        validation_alias=AliasChoices("friendly_name", "FriendlyName"),
    )

    model_config = {
        "populate_by_name": True,
        "extra": "ignore",
    }


class RootComponent(BaseModel):
    """Define a root component entry for the solution manifest."""

    type: int = Field(validation_alias=AliasChoices("type", "Type"))
    schema_name: str = Field(
        validation_alias=AliasChoices("schema_name", "schemaName", "SchemaName")
    )
    behavior: int | None = Field(
        default=None,
        validation_alias=AliasChoices("behavior", "Behavior"),
    )
    include_subcomponents: int | None = Field(
        default=None,
        validation_alias=AliasChoices("include_subcomponents", "IncludeSubcomponents"),
    )
    component_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("component_id", "Id", "id"),
    )

    model_config = {
        "populate_by_name": True,
        "extra": "ignore",
    }


class SolutionManifestConfig(BaseModel):
    """Pydantic model backing the solution manifest config-as-data."""

    unique_name: str = Field(
        default="CodexCRM", validation_alias=AliasChoices("unique_name", "UniqueName")
    )
    version: str = Field(default="1.0.0.0", validation_alias=AliasChoices("version", "Version"))
    friendly_name: str | None = Field(
        default=None, validation_alias=AliasChoices("friendly_name", "FriendlyName")
    )
    description: str | None = Field(
        default=None, validation_alias=AliasChoices("description", "Description")
    )
    managed: bool | None = Field(default=None, validation_alias=AliasChoices("managed", "Managed"))
    publisher: Publisher | None = Field(default=None)
    localized_names: list[LocalizedName] = Field(default_factory=list)
    root_components: list[RootComponent] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)

    model_config = {
        "populate_by_name": True,
        "extra": "ignore",
    }

    def xǁSolutionManifestConfigǁwith_overrides__mutmut_orig(
        self, *, name: str | None = None, version: str | None = None
    ) -> SolutionManifestConfig:
        data = self.model_dump()
        if name is not None:
            data["unique_name"] = name
        if version is not None:
            data["version"] = version
        return SolutionManifestConfig.model_validate(data)

    def xǁSolutionManifestConfigǁwith_overrides__mutmut_1(
        self, *, name: str | None = None, version: str | None = None
    ) -> SolutionManifestConfig:
        data = None
        if name is not None:
            data["unique_name"] = name
        if version is not None:
            data["version"] = version
        return SolutionManifestConfig.model_validate(data)

    def xǁSolutionManifestConfigǁwith_overrides__mutmut_2(
        self, *, name: str | None = None, version: str | None = None
    ) -> SolutionManifestConfig:
        data = self.model_dump()
        if name is None:
            data["unique_name"] = name
        if version is not None:
            data["version"] = version
        return SolutionManifestConfig.model_validate(data)

    def xǁSolutionManifestConfigǁwith_overrides__mutmut_3(
        self, *, name: str | None = None, version: str | None = None
    ) -> SolutionManifestConfig:
        data = self.model_dump()
        if name is not None:
            data["unique_name"] = None
        if version is not None:
            data["version"] = version
        return SolutionManifestConfig.model_validate(data)

    def xǁSolutionManifestConfigǁwith_overrides__mutmut_4(
        self, *, name: str | None = None, version: str | None = None
    ) -> SolutionManifestConfig:
        data = self.model_dump()
        if name is not None:
            data["XXunique_nameXX"] = name
        if version is not None:
            data["version"] = version
        return SolutionManifestConfig.model_validate(data)

    def xǁSolutionManifestConfigǁwith_overrides__mutmut_5(
        self, *, name: str | None = None, version: str | None = None
    ) -> SolutionManifestConfig:
        data = self.model_dump()
        if name is not None:
            data["UNIQUE_NAME"] = name
        if version is not None:
            data["version"] = version
        return SolutionManifestConfig.model_validate(data)

    def xǁSolutionManifestConfigǁwith_overrides__mutmut_6(
        self, *, name: str | None = None, version: str | None = None
    ) -> SolutionManifestConfig:
        data = self.model_dump()
        if name is not None:
            data["unique_name"] = name
        if version is None:
            data["version"] = version
        return SolutionManifestConfig.model_validate(data)

    def xǁSolutionManifestConfigǁwith_overrides__mutmut_7(
        self, *, name: str | None = None, version: str | None = None
    ) -> SolutionManifestConfig:
        data = self.model_dump()
        if name is not None:
            data["unique_name"] = name
        if version is not None:
            data["version"] = None
        return SolutionManifestConfig.model_validate(data)

    def xǁSolutionManifestConfigǁwith_overrides__mutmut_8(
        self, *, name: str | None = None, version: str | None = None
    ) -> SolutionManifestConfig:
        data = self.model_dump()
        if name is not None:
            data["unique_name"] = name
        if version is not None:
            data["XXversionXX"] = version
        return SolutionManifestConfig.model_validate(data)

    def xǁSolutionManifestConfigǁwith_overrides__mutmut_9(
        self, *, name: str | None = None, version: str | None = None
    ) -> SolutionManifestConfig:
        data = self.model_dump()
        if name is not None:
            data["unique_name"] = name
        if version is not None:
            data["VERSION"] = version
        return SolutionManifestConfig.model_validate(data)

    def xǁSolutionManifestConfigǁwith_overrides__mutmut_10(
        self, *, name: str | None = None, version: str | None = None
    ) -> SolutionManifestConfig:
        data = self.model_dump()
        if name is not None:
            data["unique_name"] = name
        if version is not None:
            data["version"] = version
        return SolutionManifestConfig.model_validate(None)
    
    xǁSolutionManifestConfigǁwith_overrides__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSolutionManifestConfigǁwith_overrides__mutmut_1': xǁSolutionManifestConfigǁwith_overrides__mutmut_1, 
        'xǁSolutionManifestConfigǁwith_overrides__mutmut_2': xǁSolutionManifestConfigǁwith_overrides__mutmut_2, 
        'xǁSolutionManifestConfigǁwith_overrides__mutmut_3': xǁSolutionManifestConfigǁwith_overrides__mutmut_3, 
        'xǁSolutionManifestConfigǁwith_overrides__mutmut_4': xǁSolutionManifestConfigǁwith_overrides__mutmut_4, 
        'xǁSolutionManifestConfigǁwith_overrides__mutmut_5': xǁSolutionManifestConfigǁwith_overrides__mutmut_5, 
        'xǁSolutionManifestConfigǁwith_overrides__mutmut_6': xǁSolutionManifestConfigǁwith_overrides__mutmut_6, 
        'xǁSolutionManifestConfigǁwith_overrides__mutmut_7': xǁSolutionManifestConfigǁwith_overrides__mutmut_7, 
        'xǁSolutionManifestConfigǁwith_overrides__mutmut_8': xǁSolutionManifestConfigǁwith_overrides__mutmut_8, 
        'xǁSolutionManifestConfigǁwith_overrides__mutmut_9': xǁSolutionManifestConfigǁwith_overrides__mutmut_9, 
        'xǁSolutionManifestConfigǁwith_overrides__mutmut_10': xǁSolutionManifestConfigǁwith_overrides__mutmut_10
    }
    
    def with_overrides(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSolutionManifestConfigǁwith_overrides__mutmut_orig"), object.__getattribute__(self, "xǁSolutionManifestConfigǁwith_overrides__mutmut_mutants"), args, kwargs, self)
        return result 
    
    with_overrides.__signature__ = _mutmut_signature(xǁSolutionManifestConfigǁwith_overrides__mutmut_orig)
    xǁSolutionManifestConfigǁwith_overrides__mutmut_orig.__name__ = 'xǁSolutionManifestConfigǁwith_overrides'


def x__resolve_config_dir__mutmut_orig(config_dir: Path) -> Path:
    if config_dir.exists():
        return config_dir
    if config_dir.is_absolute():
        return config_dir
    repo_root = Path(__file__).resolve().parents[3]
    return repo_root / config_dir


def x__resolve_config_dir__mutmut_1(config_dir: Path) -> Path:
    if config_dir.exists():
        return config_dir
    if config_dir.is_absolute():
        return config_dir
    repo_root = None
    return repo_root / config_dir


def x__resolve_config_dir__mutmut_2(config_dir: Path) -> Path:
    if config_dir.exists():
        return config_dir
    if config_dir.is_absolute():
        return config_dir
    repo_root = Path(None).resolve().parents[3]
    return repo_root / config_dir


def x__resolve_config_dir__mutmut_3(config_dir: Path) -> Path:
    if config_dir.exists():
        return config_dir
    if config_dir.is_absolute():
        return config_dir
    repo_root = Path(__file__).resolve().parents[4]
    return repo_root / config_dir


def x__resolve_config_dir__mutmut_4(config_dir: Path) -> Path:
    if config_dir.exists():
        return config_dir
    if config_dir.is_absolute():
        return config_dir
    repo_root = Path(__file__).resolve().parents[3]
    return repo_root * config_dir

x__resolve_config_dir__mutmut_mutants : ClassVar[MutantDict] = {
'x__resolve_config_dir__mutmut_1': x__resolve_config_dir__mutmut_1, 
    'x__resolve_config_dir__mutmut_2': x__resolve_config_dir__mutmut_2, 
    'x__resolve_config_dir__mutmut_3': x__resolve_config_dir__mutmut_3, 
    'x__resolve_config_dir__mutmut_4': x__resolve_config_dir__mutmut_4
}

def _resolve_config_dir(*args, **kwargs):
    result = _mutmut_trampoline(x__resolve_config_dir__mutmut_orig, x__resolve_config_dir__mutmut_mutants, args, kwargs)
    return result 

_resolve_config_dir.__signature__ = _mutmut_signature(x__resolve_config_dir__mutmut_orig)
x__resolve_config_dir__mutmut_orig.__name__ = 'x__resolve_config_dir'


def x_load_solution_manifest__mutmut_orig(config_dir: Path | None = None) -> SolutionManifestConfig:
    """Load the solution manifest definition from ``configs/deployment/d365``."""

    base = _resolve_config_dir(config_dir or Path("configs/deployment/d365"))
    config_path = base / "solution_manifest.json"
    if not config_path.exists():
        return SolutionManifestConfig()
    data = json.loads(config_path.read_text(encoding="utf-8"))
    return SolutionManifestConfig.model_validate(data)


def x_load_solution_manifest__mutmut_1(config_dir: Path | None = None) -> SolutionManifestConfig:
    """Load the solution manifest definition from ``configs/deployment/d365``."""

    base = None
    config_path = base / "solution_manifest.json"
    if not config_path.exists():
        return SolutionManifestConfig()
    data = json.loads(config_path.read_text(encoding="utf-8"))
    return SolutionManifestConfig.model_validate(data)


def x_load_solution_manifest__mutmut_2(config_dir: Path | None = None) -> SolutionManifestConfig:
    """Load the solution manifest definition from ``configs/deployment/d365``."""

    base = _resolve_config_dir(None)
    config_path = base / "solution_manifest.json"
    if not config_path.exists():
        return SolutionManifestConfig()
    data = json.loads(config_path.read_text(encoding="utf-8"))
    return SolutionManifestConfig.model_validate(data)


def x_load_solution_manifest__mutmut_3(config_dir: Path | None = None) -> SolutionManifestConfig:
    """Load the solution manifest definition from ``configs/deployment/d365``."""

    base = _resolve_config_dir(config_dir and Path("configs/deployment/d365"))
    config_path = base / "solution_manifest.json"
    if not config_path.exists():
        return SolutionManifestConfig()
    data = json.loads(config_path.read_text(encoding="utf-8"))
    return SolutionManifestConfig.model_validate(data)


def x_load_solution_manifest__mutmut_4(config_dir: Path | None = None) -> SolutionManifestConfig:
    """Load the solution manifest definition from ``configs/deployment/d365``."""

    base = _resolve_config_dir(config_dir or Path(None))
    config_path = base / "solution_manifest.json"
    if not config_path.exists():
        return SolutionManifestConfig()
    data = json.loads(config_path.read_text(encoding="utf-8"))
    return SolutionManifestConfig.model_validate(data)


def x_load_solution_manifest__mutmut_5(config_dir: Path | None = None) -> SolutionManifestConfig:
    """Load the solution manifest definition from ``configs/deployment/d365``."""

    base = _resolve_config_dir(config_dir or Path("XXconfigs/deployment/d365XX"))
    config_path = base / "solution_manifest.json"
    if not config_path.exists():
        return SolutionManifestConfig()
    data = json.loads(config_path.read_text(encoding="utf-8"))
    return SolutionManifestConfig.model_validate(data)


def x_load_solution_manifest__mutmut_6(config_dir: Path | None = None) -> SolutionManifestConfig:
    """Load the solution manifest definition from ``configs/deployment/d365``."""

    base = _resolve_config_dir(config_dir or Path("CONFIGS/DEPLOYMENT/D365"))
    config_path = base / "solution_manifest.json"
    if not config_path.exists():
        return SolutionManifestConfig()
    data = json.loads(config_path.read_text(encoding="utf-8"))
    return SolutionManifestConfig.model_validate(data)


def x_load_solution_manifest__mutmut_7(config_dir: Path | None = None) -> SolutionManifestConfig:
    """Load the solution manifest definition from ``configs/deployment/d365``."""

    base = _resolve_config_dir(config_dir or Path("configs/deployment/d365"))
    config_path = None
    if not config_path.exists():
        return SolutionManifestConfig()
    data = json.loads(config_path.read_text(encoding="utf-8"))
    return SolutionManifestConfig.model_validate(data)


def x_load_solution_manifest__mutmut_8(config_dir: Path | None = None) -> SolutionManifestConfig:
    """Load the solution manifest definition from ``configs/deployment/d365``."""

    base = _resolve_config_dir(config_dir or Path("configs/deployment/d365"))
    config_path = base * "solution_manifest.json"
    if not config_path.exists():
        return SolutionManifestConfig()
    data = json.loads(config_path.read_text(encoding="utf-8"))
    return SolutionManifestConfig.model_validate(data)


def x_load_solution_manifest__mutmut_9(config_dir: Path | None = None) -> SolutionManifestConfig:
    """Load the solution manifest definition from ``configs/deployment/d365``."""

    base = _resolve_config_dir(config_dir or Path("configs/deployment/d365"))
    config_path = base / "XXsolution_manifest.jsonXX"
    if not config_path.exists():
        return SolutionManifestConfig()
    data = json.loads(config_path.read_text(encoding="utf-8"))
    return SolutionManifestConfig.model_validate(data)


def x_load_solution_manifest__mutmut_10(config_dir: Path | None = None) -> SolutionManifestConfig:
    """Load the solution manifest definition from ``configs/deployment/d365``."""

    base = _resolve_config_dir(config_dir or Path("configs/deployment/d365"))
    config_path = base / "SOLUTION_MANIFEST.JSON"
    if not config_path.exists():
        return SolutionManifestConfig()
    data = json.loads(config_path.read_text(encoding="utf-8"))
    return SolutionManifestConfig.model_validate(data)


def x_load_solution_manifest__mutmut_11(config_dir: Path | None = None) -> SolutionManifestConfig:
    """Load the solution manifest definition from ``configs/deployment/d365``."""

    base = _resolve_config_dir(config_dir or Path("configs/deployment/d365"))
    config_path = base / "solution_manifest.json"
    if config_path.exists():
        return SolutionManifestConfig()
    data = json.loads(config_path.read_text(encoding="utf-8"))
    return SolutionManifestConfig.model_validate(data)


def x_load_solution_manifest__mutmut_12(config_dir: Path | None = None) -> SolutionManifestConfig:
    """Load the solution manifest definition from ``configs/deployment/d365``."""

    base = _resolve_config_dir(config_dir or Path("configs/deployment/d365"))
    config_path = base / "solution_manifest.json"
    if not config_path.exists():
        return SolutionManifestConfig()
    data = None
    return SolutionManifestConfig.model_validate(data)


def x_load_solution_manifest__mutmut_13(config_dir: Path | None = None) -> SolutionManifestConfig:
    """Load the solution manifest definition from ``configs/deployment/d365``."""

    base = _resolve_config_dir(config_dir or Path("configs/deployment/d365"))
    config_path = base / "solution_manifest.json"
    if not config_path.exists():
        return SolutionManifestConfig()
    data = json.loads(None)
    return SolutionManifestConfig.model_validate(data)


def x_load_solution_manifest__mutmut_14(config_dir: Path | None = None) -> SolutionManifestConfig:
    """Load the solution manifest definition from ``configs/deployment/d365``."""

    base = _resolve_config_dir(config_dir or Path("configs/deployment/d365"))
    config_path = base / "solution_manifest.json"
    if not config_path.exists():
        return SolutionManifestConfig()
    data = json.loads(config_path.read_text(encoding=None))
    return SolutionManifestConfig.model_validate(data)


def x_load_solution_manifest__mutmut_15(config_dir: Path | None = None) -> SolutionManifestConfig:
    """Load the solution manifest definition from ``configs/deployment/d365``."""

    base = _resolve_config_dir(config_dir or Path("configs/deployment/d365"))
    config_path = base / "solution_manifest.json"
    if not config_path.exists():
        return SolutionManifestConfig()
    data = json.loads(config_path.read_text(encoding="XXutf-8XX"))
    return SolutionManifestConfig.model_validate(data)


def x_load_solution_manifest__mutmut_16(config_dir: Path | None = None) -> SolutionManifestConfig:
    """Load the solution manifest definition from ``configs/deployment/d365``."""

    base = _resolve_config_dir(config_dir or Path("configs/deployment/d365"))
    config_path = base / "solution_manifest.json"
    if not config_path.exists():
        return SolutionManifestConfig()
    data = json.loads(config_path.read_text(encoding="UTF-8"))
    return SolutionManifestConfig.model_validate(data)


def x_load_solution_manifest__mutmut_17(config_dir: Path | None = None) -> SolutionManifestConfig:
    """Load the solution manifest definition from ``configs/deployment/d365``."""

    base = _resolve_config_dir(config_dir or Path("configs/deployment/d365"))
    config_path = base / "solution_manifest.json"
    if not config_path.exists():
        return SolutionManifestConfig()
    data = json.loads(config_path.read_text(encoding="utf-8"))
    return SolutionManifestConfig.model_validate(None)

x_load_solution_manifest__mutmut_mutants : ClassVar[MutantDict] = {
'x_load_solution_manifest__mutmut_1': x_load_solution_manifest__mutmut_1, 
    'x_load_solution_manifest__mutmut_2': x_load_solution_manifest__mutmut_2, 
    'x_load_solution_manifest__mutmut_3': x_load_solution_manifest__mutmut_3, 
    'x_load_solution_manifest__mutmut_4': x_load_solution_manifest__mutmut_4, 
    'x_load_solution_manifest__mutmut_5': x_load_solution_manifest__mutmut_5, 
    'x_load_solution_manifest__mutmut_6': x_load_solution_manifest__mutmut_6, 
    'x_load_solution_manifest__mutmut_7': x_load_solution_manifest__mutmut_7, 
    'x_load_solution_manifest__mutmut_8': x_load_solution_manifest__mutmut_8, 
    'x_load_solution_manifest__mutmut_9': x_load_solution_manifest__mutmut_9, 
    'x_load_solution_manifest__mutmut_10': x_load_solution_manifest__mutmut_10, 
    'x_load_solution_manifest__mutmut_11': x_load_solution_manifest__mutmut_11, 
    'x_load_solution_manifest__mutmut_12': x_load_solution_manifest__mutmut_12, 
    'x_load_solution_manifest__mutmut_13': x_load_solution_manifest__mutmut_13, 
    'x_load_solution_manifest__mutmut_14': x_load_solution_manifest__mutmut_14, 
    'x_load_solution_manifest__mutmut_15': x_load_solution_manifest__mutmut_15, 
    'x_load_solution_manifest__mutmut_16': x_load_solution_manifest__mutmut_16, 
    'x_load_solution_manifest__mutmut_17': x_load_solution_manifest__mutmut_17
}

def load_solution_manifest(*args, **kwargs):
    result = _mutmut_trampoline(x_load_solution_manifest__mutmut_orig, x_load_solution_manifest__mutmut_mutants, args, kwargs)
    return result 

load_solution_manifest.__signature__ = _mutmut_signature(x_load_solution_manifest__mutmut_orig)
x_load_solution_manifest__mutmut_orig.__name__ = 'x_load_solution_manifest'


def x_build_solution_tree__mutmut_orig(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_1(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = None
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_2(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element(None)
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_3(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("XXImportExportXmlXX")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_4(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("importexportxml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_5(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("IMPORTEXPORTXML")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_6(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = None

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_7(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(None, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_8(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, None)

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_9(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement("SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_10(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, )

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_11(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "XXSolutionManifestXX")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_12(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "solutionmanifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_13(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SOLUTIONMANIFEST")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_14(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = None
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_15(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(None, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_16(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, None).text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_17(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement("UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_18(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, ).text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_19(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "XXUniqueNameXX").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_20(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "uniquename").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_21(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UNIQUENAME").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_22(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = None
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_23(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(None, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_24(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, None).text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_25(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement("Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_26(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, ).text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_27(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "XXVersionXX").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_28(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_29(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "VERSION").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_30(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = None

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_31(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(None, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_32(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, None).text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_33(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement("Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_34(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, ).text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_35(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "XXManagedXX").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_36(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_37(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "MANAGED").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_38(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "XX1XX" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_39(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "XX0XX"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_40(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = None
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_41(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(None, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_42(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, None).text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_43(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement("FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_44(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, ).text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_45(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "XXFriendlyNameXX").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_46(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "friendlyname").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_47(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FRIENDLYNAME").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_48(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = None

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_49(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(None, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_50(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, None).text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_51(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement("Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_52(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, ).text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_53(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "XXDescriptionXX").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_54(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_55(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "DESCRIPTION").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_56(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = None
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_57(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(None, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_58(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, None)
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_59(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement("Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_60(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, )
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_61(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "XXPublisherXX")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_62(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_63(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "PUBLISHER")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_64(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = None
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_65(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(None, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_66(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, None).text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_67(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement("UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_68(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, ).text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_69(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "XXUniqueNameXX").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_70(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "uniquename").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_71(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UNIQUENAME").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_72(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = None
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_73(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(None, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_74(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, None).text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_75(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement("FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_76(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, ).text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_77(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "XXFriendlyNameXX").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_78(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "friendlyname").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_79(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FRIENDLYNAME").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_80(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name and ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_81(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or "XXXX"
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_82(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = None

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_83(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(None, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_84(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, None).text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_85(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement("Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_86(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, ).text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_87(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "XXPrefixXX").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_88(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_89(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "PREFIX").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_90(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = None
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_91(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(None, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_92(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, None)
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_93(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement("LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_94(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, )
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_95(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "XXLocalizedNamesXX")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_96(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "localizednames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_97(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LOCALIZEDNAMES")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_98(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = None
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_99(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(None, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_100(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, None)
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_101(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement("LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_102(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, )
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_103(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "XXLocalizedNameXX")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_104(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "localizedname")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_105(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LOCALIZEDNAME")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_106(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set(None, entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_107(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", None)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_108(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set(entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_109(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", )
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_110(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("XXdescriptionXX", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_111(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("DESCRIPTION", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_112(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set(None, str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_113(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", None)

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_114(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set(str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_115(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", )

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_116(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("XXlanguagecodeXX", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_117(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("LANGUAGECODE", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_118(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(None))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_119(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = None

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_120(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(None, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_121(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, None).text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_122(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement("GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_123(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, ).text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_124(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "XXGeneratedOnXX").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_125(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "generatedon").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_126(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GENERATEDON").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_127(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = None
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_128(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(None, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_129(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, None)
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_130(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement("RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_131(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, )
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_132(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "XXRootComponentsXX")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_133(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "rootcomponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_134(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "ROOTCOMPONENTS")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_135(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = None
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_136(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(None, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_137(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, None)
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_138(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement("RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_139(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, )
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_140(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "XXRootComponentXX")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_141(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "rootcomponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_142(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "ROOTCOMPONENT")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_143(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set(None, str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_144(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", None)
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_145(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set(str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_146(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", )
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_147(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("XXtypeXX", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_148(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("TYPE", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_149(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(None))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_150(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set(None, component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_151(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", None)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_152(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set(component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_153(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", )
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_154(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("XXschemaNameXX", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_155(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaname", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_156(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("SCHEMANAME", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_157(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_158(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set(None, str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_159(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", None)
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_160(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set(str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_161(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", )
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_162(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("XXbehaviorXX", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_163(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("BEHAVIOR", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_164(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(None))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_165(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_166(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set(None, str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_167(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", None)
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_168(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set(str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_169(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", )
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_170(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("XXincludeSubcomponentsXX", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_171(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includesubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_172(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("INCLUDESUBCOMPONENTS", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_173(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(None))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_174(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set(None, component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_175(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", None)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_176(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set(component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_177(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", )

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_178(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("XXidXX", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_179(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("ID", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_180(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = None
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_181(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(None, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_182(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, None)
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_183(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement("Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_184(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, )
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_185(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "XXDependenciesXX")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_186(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_187(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "DEPENDENCIES")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_188(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = None
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_189(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(None, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_190(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, None)
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_191(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement("Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_192(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, )
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_193(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "XXDependencyXX")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_194(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_195(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "DEPENDENCY")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_196(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = None

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_197(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = None
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_198(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(None, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_199(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, None).text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_200(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement("SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_201(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, ).text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_202(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "XXSourceSolutionTypeXX").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_203(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "sourcesolutiontype").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_204(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SOURCESOLUTIONTYPE").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_205(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "XX0XX"
    SubElement(manifest, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_206(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SolutionPackageVersion").text = None

    return root


def x_build_solution_tree__mutmut_207(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(None, "SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_208(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, None).text = config.version

    return root


def x_build_solution_tree__mutmut_209(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement("SolutionPackageVersion").text = config.version

    return root


def x_build_solution_tree__mutmut_210(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, ).text = config.version

    return root


def x_build_solution_tree__mutmut_211(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "XXSolutionPackageVersionXX").text = config.version

    return root


def x_build_solution_tree__mutmut_212(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "solutionpackageversion").text = config.version

    return root


def x_build_solution_tree__mutmut_213(config: SolutionManifestConfig) -> Element:
    """Construct the XML tree for ``config`` without serializing it."""

    root = Element("ImportExportXml")
    manifest = SubElement(root, "SolutionManifest")

    SubElement(manifest, "UniqueName").text = config.unique_name
    SubElement(manifest, "Version").text = config.version
    SubElement(manifest, "Managed").text = "1" if config.managed else "0"

    if config.friendly_name:
        SubElement(manifest, "FriendlyName").text = config.friendly_name
    if config.description:
        SubElement(manifest, "Description").text = config.description

    if config.publisher:
        publisher = SubElement(manifest, "Publisher")
        SubElement(publisher, "UniqueName").text = config.publisher.unique_name
        SubElement(publisher, "FriendlyName").text = config.publisher.friendly_name or ""
        SubElement(publisher, "Prefix").text = config.publisher.prefix

    if config.localized_names:
        localized_names = SubElement(manifest, "LocalizedNames")
        for entry in config.localized_names:
            localized_name = SubElement(localized_names, "LocalizedName")
            localized_name.set("description", entry.description)
            localized_name.set("languagecode", str(entry.languagecode))

    SubElement(manifest, "GeneratedOn").text = utc_now()

    root_components = SubElement(manifest, "RootComponents")
    for component in config.root_components:
        node = SubElement(root_components, "RootComponent")
        node.set("type", str(component.type))
        node.set("schemaName", component.schema_name)
        if component.behavior is not None:
            node.set("behavior", str(component.behavior))
        if component.include_subcomponents is not None:
            node.set("includeSubcomponents", str(component.include_subcomponents))
        if component.component_id:
            node.set("id", component.component_id)

    dependencies = SubElement(manifest, "Dependencies")
    for dep in config.dependencies:
        dep_node = SubElement(dependencies, "Dependency")
        dep_node.text = dep

    SubElement(manifest, "SourceSolutionType").text = "0"
    SubElement(manifest, "SOLUTIONPACKAGEVERSION").text = config.version

    return root

x_build_solution_tree__mutmut_mutants : ClassVar[MutantDict] = {
'x_build_solution_tree__mutmut_1': x_build_solution_tree__mutmut_1, 
    'x_build_solution_tree__mutmut_2': x_build_solution_tree__mutmut_2, 
    'x_build_solution_tree__mutmut_3': x_build_solution_tree__mutmut_3, 
    'x_build_solution_tree__mutmut_4': x_build_solution_tree__mutmut_4, 
    'x_build_solution_tree__mutmut_5': x_build_solution_tree__mutmut_5, 
    'x_build_solution_tree__mutmut_6': x_build_solution_tree__mutmut_6, 
    'x_build_solution_tree__mutmut_7': x_build_solution_tree__mutmut_7, 
    'x_build_solution_tree__mutmut_8': x_build_solution_tree__mutmut_8, 
    'x_build_solution_tree__mutmut_9': x_build_solution_tree__mutmut_9, 
    'x_build_solution_tree__mutmut_10': x_build_solution_tree__mutmut_10, 
    'x_build_solution_tree__mutmut_11': x_build_solution_tree__mutmut_11, 
    'x_build_solution_tree__mutmut_12': x_build_solution_tree__mutmut_12, 
    'x_build_solution_tree__mutmut_13': x_build_solution_tree__mutmut_13, 
    'x_build_solution_tree__mutmut_14': x_build_solution_tree__mutmut_14, 
    'x_build_solution_tree__mutmut_15': x_build_solution_tree__mutmut_15, 
    'x_build_solution_tree__mutmut_16': x_build_solution_tree__mutmut_16, 
    'x_build_solution_tree__mutmut_17': x_build_solution_tree__mutmut_17, 
    'x_build_solution_tree__mutmut_18': x_build_solution_tree__mutmut_18, 
    'x_build_solution_tree__mutmut_19': x_build_solution_tree__mutmut_19, 
    'x_build_solution_tree__mutmut_20': x_build_solution_tree__mutmut_20, 
    'x_build_solution_tree__mutmut_21': x_build_solution_tree__mutmut_21, 
    'x_build_solution_tree__mutmut_22': x_build_solution_tree__mutmut_22, 
    'x_build_solution_tree__mutmut_23': x_build_solution_tree__mutmut_23, 
    'x_build_solution_tree__mutmut_24': x_build_solution_tree__mutmut_24, 
    'x_build_solution_tree__mutmut_25': x_build_solution_tree__mutmut_25, 
    'x_build_solution_tree__mutmut_26': x_build_solution_tree__mutmut_26, 
    'x_build_solution_tree__mutmut_27': x_build_solution_tree__mutmut_27, 
    'x_build_solution_tree__mutmut_28': x_build_solution_tree__mutmut_28, 
    'x_build_solution_tree__mutmut_29': x_build_solution_tree__mutmut_29, 
    'x_build_solution_tree__mutmut_30': x_build_solution_tree__mutmut_30, 
    'x_build_solution_tree__mutmut_31': x_build_solution_tree__mutmut_31, 
    'x_build_solution_tree__mutmut_32': x_build_solution_tree__mutmut_32, 
    'x_build_solution_tree__mutmut_33': x_build_solution_tree__mutmut_33, 
    'x_build_solution_tree__mutmut_34': x_build_solution_tree__mutmut_34, 
    'x_build_solution_tree__mutmut_35': x_build_solution_tree__mutmut_35, 
    'x_build_solution_tree__mutmut_36': x_build_solution_tree__mutmut_36, 
    'x_build_solution_tree__mutmut_37': x_build_solution_tree__mutmut_37, 
    'x_build_solution_tree__mutmut_38': x_build_solution_tree__mutmut_38, 
    'x_build_solution_tree__mutmut_39': x_build_solution_tree__mutmut_39, 
    'x_build_solution_tree__mutmut_40': x_build_solution_tree__mutmut_40, 
    'x_build_solution_tree__mutmut_41': x_build_solution_tree__mutmut_41, 
    'x_build_solution_tree__mutmut_42': x_build_solution_tree__mutmut_42, 
    'x_build_solution_tree__mutmut_43': x_build_solution_tree__mutmut_43, 
    'x_build_solution_tree__mutmut_44': x_build_solution_tree__mutmut_44, 
    'x_build_solution_tree__mutmut_45': x_build_solution_tree__mutmut_45, 
    'x_build_solution_tree__mutmut_46': x_build_solution_tree__mutmut_46, 
    'x_build_solution_tree__mutmut_47': x_build_solution_tree__mutmut_47, 
    'x_build_solution_tree__mutmut_48': x_build_solution_tree__mutmut_48, 
    'x_build_solution_tree__mutmut_49': x_build_solution_tree__mutmut_49, 
    'x_build_solution_tree__mutmut_50': x_build_solution_tree__mutmut_50, 
    'x_build_solution_tree__mutmut_51': x_build_solution_tree__mutmut_51, 
    'x_build_solution_tree__mutmut_52': x_build_solution_tree__mutmut_52, 
    'x_build_solution_tree__mutmut_53': x_build_solution_tree__mutmut_53, 
    'x_build_solution_tree__mutmut_54': x_build_solution_tree__mutmut_54, 
    'x_build_solution_tree__mutmut_55': x_build_solution_tree__mutmut_55, 
    'x_build_solution_tree__mutmut_56': x_build_solution_tree__mutmut_56, 
    'x_build_solution_tree__mutmut_57': x_build_solution_tree__mutmut_57, 
    'x_build_solution_tree__mutmut_58': x_build_solution_tree__mutmut_58, 
    'x_build_solution_tree__mutmut_59': x_build_solution_tree__mutmut_59, 
    'x_build_solution_tree__mutmut_60': x_build_solution_tree__mutmut_60, 
    'x_build_solution_tree__mutmut_61': x_build_solution_tree__mutmut_61, 
    'x_build_solution_tree__mutmut_62': x_build_solution_tree__mutmut_62, 
    'x_build_solution_tree__mutmut_63': x_build_solution_tree__mutmut_63, 
    'x_build_solution_tree__mutmut_64': x_build_solution_tree__mutmut_64, 
    'x_build_solution_tree__mutmut_65': x_build_solution_tree__mutmut_65, 
    'x_build_solution_tree__mutmut_66': x_build_solution_tree__mutmut_66, 
    'x_build_solution_tree__mutmut_67': x_build_solution_tree__mutmut_67, 
    'x_build_solution_tree__mutmut_68': x_build_solution_tree__mutmut_68, 
    'x_build_solution_tree__mutmut_69': x_build_solution_tree__mutmut_69, 
    'x_build_solution_tree__mutmut_70': x_build_solution_tree__mutmut_70, 
    'x_build_solution_tree__mutmut_71': x_build_solution_tree__mutmut_71, 
    'x_build_solution_tree__mutmut_72': x_build_solution_tree__mutmut_72, 
    'x_build_solution_tree__mutmut_73': x_build_solution_tree__mutmut_73, 
    'x_build_solution_tree__mutmut_74': x_build_solution_tree__mutmut_74, 
    'x_build_solution_tree__mutmut_75': x_build_solution_tree__mutmut_75, 
    'x_build_solution_tree__mutmut_76': x_build_solution_tree__mutmut_76, 
    'x_build_solution_tree__mutmut_77': x_build_solution_tree__mutmut_77, 
    'x_build_solution_tree__mutmut_78': x_build_solution_tree__mutmut_78, 
    'x_build_solution_tree__mutmut_79': x_build_solution_tree__mutmut_79, 
    'x_build_solution_tree__mutmut_80': x_build_solution_tree__mutmut_80, 
    'x_build_solution_tree__mutmut_81': x_build_solution_tree__mutmut_81, 
    'x_build_solution_tree__mutmut_82': x_build_solution_tree__mutmut_82, 
    'x_build_solution_tree__mutmut_83': x_build_solution_tree__mutmut_83, 
    'x_build_solution_tree__mutmut_84': x_build_solution_tree__mutmut_84, 
    'x_build_solution_tree__mutmut_85': x_build_solution_tree__mutmut_85, 
    'x_build_solution_tree__mutmut_86': x_build_solution_tree__mutmut_86, 
    'x_build_solution_tree__mutmut_87': x_build_solution_tree__mutmut_87, 
    'x_build_solution_tree__mutmut_88': x_build_solution_tree__mutmut_88, 
    'x_build_solution_tree__mutmut_89': x_build_solution_tree__mutmut_89, 
    'x_build_solution_tree__mutmut_90': x_build_solution_tree__mutmut_90, 
    'x_build_solution_tree__mutmut_91': x_build_solution_tree__mutmut_91, 
    'x_build_solution_tree__mutmut_92': x_build_solution_tree__mutmut_92, 
    'x_build_solution_tree__mutmut_93': x_build_solution_tree__mutmut_93, 
    'x_build_solution_tree__mutmut_94': x_build_solution_tree__mutmut_94, 
    'x_build_solution_tree__mutmut_95': x_build_solution_tree__mutmut_95, 
    'x_build_solution_tree__mutmut_96': x_build_solution_tree__mutmut_96, 
    'x_build_solution_tree__mutmut_97': x_build_solution_tree__mutmut_97, 
    'x_build_solution_tree__mutmut_98': x_build_solution_tree__mutmut_98, 
    'x_build_solution_tree__mutmut_99': x_build_solution_tree__mutmut_99, 
    'x_build_solution_tree__mutmut_100': x_build_solution_tree__mutmut_100, 
    'x_build_solution_tree__mutmut_101': x_build_solution_tree__mutmut_101, 
    'x_build_solution_tree__mutmut_102': x_build_solution_tree__mutmut_102, 
    'x_build_solution_tree__mutmut_103': x_build_solution_tree__mutmut_103, 
    'x_build_solution_tree__mutmut_104': x_build_solution_tree__mutmut_104, 
    'x_build_solution_tree__mutmut_105': x_build_solution_tree__mutmut_105, 
    'x_build_solution_tree__mutmut_106': x_build_solution_tree__mutmut_106, 
    'x_build_solution_tree__mutmut_107': x_build_solution_tree__mutmut_107, 
    'x_build_solution_tree__mutmut_108': x_build_solution_tree__mutmut_108, 
    'x_build_solution_tree__mutmut_109': x_build_solution_tree__mutmut_109, 
    'x_build_solution_tree__mutmut_110': x_build_solution_tree__mutmut_110, 
    'x_build_solution_tree__mutmut_111': x_build_solution_tree__mutmut_111, 
    'x_build_solution_tree__mutmut_112': x_build_solution_tree__mutmut_112, 
    'x_build_solution_tree__mutmut_113': x_build_solution_tree__mutmut_113, 
    'x_build_solution_tree__mutmut_114': x_build_solution_tree__mutmut_114, 
    'x_build_solution_tree__mutmut_115': x_build_solution_tree__mutmut_115, 
    'x_build_solution_tree__mutmut_116': x_build_solution_tree__mutmut_116, 
    'x_build_solution_tree__mutmut_117': x_build_solution_tree__mutmut_117, 
    'x_build_solution_tree__mutmut_118': x_build_solution_tree__mutmut_118, 
    'x_build_solution_tree__mutmut_119': x_build_solution_tree__mutmut_119, 
    'x_build_solution_tree__mutmut_120': x_build_solution_tree__mutmut_120, 
    'x_build_solution_tree__mutmut_121': x_build_solution_tree__mutmut_121, 
    'x_build_solution_tree__mutmut_122': x_build_solution_tree__mutmut_122, 
    'x_build_solution_tree__mutmut_123': x_build_solution_tree__mutmut_123, 
    'x_build_solution_tree__mutmut_124': x_build_solution_tree__mutmut_124, 
    'x_build_solution_tree__mutmut_125': x_build_solution_tree__mutmut_125, 
    'x_build_solution_tree__mutmut_126': x_build_solution_tree__mutmut_126, 
    'x_build_solution_tree__mutmut_127': x_build_solution_tree__mutmut_127, 
    'x_build_solution_tree__mutmut_128': x_build_solution_tree__mutmut_128, 
    'x_build_solution_tree__mutmut_129': x_build_solution_tree__mutmut_129, 
    'x_build_solution_tree__mutmut_130': x_build_solution_tree__mutmut_130, 
    'x_build_solution_tree__mutmut_131': x_build_solution_tree__mutmut_131, 
    'x_build_solution_tree__mutmut_132': x_build_solution_tree__mutmut_132, 
    'x_build_solution_tree__mutmut_133': x_build_solution_tree__mutmut_133, 
    'x_build_solution_tree__mutmut_134': x_build_solution_tree__mutmut_134, 
    'x_build_solution_tree__mutmut_135': x_build_solution_tree__mutmut_135, 
    'x_build_solution_tree__mutmut_136': x_build_solution_tree__mutmut_136, 
    'x_build_solution_tree__mutmut_137': x_build_solution_tree__mutmut_137, 
    'x_build_solution_tree__mutmut_138': x_build_solution_tree__mutmut_138, 
    'x_build_solution_tree__mutmut_139': x_build_solution_tree__mutmut_139, 
    'x_build_solution_tree__mutmut_140': x_build_solution_tree__mutmut_140, 
    'x_build_solution_tree__mutmut_141': x_build_solution_tree__mutmut_141, 
    'x_build_solution_tree__mutmut_142': x_build_solution_tree__mutmut_142, 
    'x_build_solution_tree__mutmut_143': x_build_solution_tree__mutmut_143, 
    'x_build_solution_tree__mutmut_144': x_build_solution_tree__mutmut_144, 
    'x_build_solution_tree__mutmut_145': x_build_solution_tree__mutmut_145, 
    'x_build_solution_tree__mutmut_146': x_build_solution_tree__mutmut_146, 
    'x_build_solution_tree__mutmut_147': x_build_solution_tree__mutmut_147, 
    'x_build_solution_tree__mutmut_148': x_build_solution_tree__mutmut_148, 
    'x_build_solution_tree__mutmut_149': x_build_solution_tree__mutmut_149, 
    'x_build_solution_tree__mutmut_150': x_build_solution_tree__mutmut_150, 
    'x_build_solution_tree__mutmut_151': x_build_solution_tree__mutmut_151, 
    'x_build_solution_tree__mutmut_152': x_build_solution_tree__mutmut_152, 
    'x_build_solution_tree__mutmut_153': x_build_solution_tree__mutmut_153, 
    'x_build_solution_tree__mutmut_154': x_build_solution_tree__mutmut_154, 
    'x_build_solution_tree__mutmut_155': x_build_solution_tree__mutmut_155, 
    'x_build_solution_tree__mutmut_156': x_build_solution_tree__mutmut_156, 
    'x_build_solution_tree__mutmut_157': x_build_solution_tree__mutmut_157, 
    'x_build_solution_tree__mutmut_158': x_build_solution_tree__mutmut_158, 
    'x_build_solution_tree__mutmut_159': x_build_solution_tree__mutmut_159, 
    'x_build_solution_tree__mutmut_160': x_build_solution_tree__mutmut_160, 
    'x_build_solution_tree__mutmut_161': x_build_solution_tree__mutmut_161, 
    'x_build_solution_tree__mutmut_162': x_build_solution_tree__mutmut_162, 
    'x_build_solution_tree__mutmut_163': x_build_solution_tree__mutmut_163, 
    'x_build_solution_tree__mutmut_164': x_build_solution_tree__mutmut_164, 
    'x_build_solution_tree__mutmut_165': x_build_solution_tree__mutmut_165, 
    'x_build_solution_tree__mutmut_166': x_build_solution_tree__mutmut_166, 
    'x_build_solution_tree__mutmut_167': x_build_solution_tree__mutmut_167, 
    'x_build_solution_tree__mutmut_168': x_build_solution_tree__mutmut_168, 
    'x_build_solution_tree__mutmut_169': x_build_solution_tree__mutmut_169, 
    'x_build_solution_tree__mutmut_170': x_build_solution_tree__mutmut_170, 
    'x_build_solution_tree__mutmut_171': x_build_solution_tree__mutmut_171, 
    'x_build_solution_tree__mutmut_172': x_build_solution_tree__mutmut_172, 
    'x_build_solution_tree__mutmut_173': x_build_solution_tree__mutmut_173, 
    'x_build_solution_tree__mutmut_174': x_build_solution_tree__mutmut_174, 
    'x_build_solution_tree__mutmut_175': x_build_solution_tree__mutmut_175, 
    'x_build_solution_tree__mutmut_176': x_build_solution_tree__mutmut_176, 
    'x_build_solution_tree__mutmut_177': x_build_solution_tree__mutmut_177, 
    'x_build_solution_tree__mutmut_178': x_build_solution_tree__mutmut_178, 
    'x_build_solution_tree__mutmut_179': x_build_solution_tree__mutmut_179, 
    'x_build_solution_tree__mutmut_180': x_build_solution_tree__mutmut_180, 
    'x_build_solution_tree__mutmut_181': x_build_solution_tree__mutmut_181, 
    'x_build_solution_tree__mutmut_182': x_build_solution_tree__mutmut_182, 
    'x_build_solution_tree__mutmut_183': x_build_solution_tree__mutmut_183, 
    'x_build_solution_tree__mutmut_184': x_build_solution_tree__mutmut_184, 
    'x_build_solution_tree__mutmut_185': x_build_solution_tree__mutmut_185, 
    'x_build_solution_tree__mutmut_186': x_build_solution_tree__mutmut_186, 
    'x_build_solution_tree__mutmut_187': x_build_solution_tree__mutmut_187, 
    'x_build_solution_tree__mutmut_188': x_build_solution_tree__mutmut_188, 
    'x_build_solution_tree__mutmut_189': x_build_solution_tree__mutmut_189, 
    'x_build_solution_tree__mutmut_190': x_build_solution_tree__mutmut_190, 
    'x_build_solution_tree__mutmut_191': x_build_solution_tree__mutmut_191, 
    'x_build_solution_tree__mutmut_192': x_build_solution_tree__mutmut_192, 
    'x_build_solution_tree__mutmut_193': x_build_solution_tree__mutmut_193, 
    'x_build_solution_tree__mutmut_194': x_build_solution_tree__mutmut_194, 
    'x_build_solution_tree__mutmut_195': x_build_solution_tree__mutmut_195, 
    'x_build_solution_tree__mutmut_196': x_build_solution_tree__mutmut_196, 
    'x_build_solution_tree__mutmut_197': x_build_solution_tree__mutmut_197, 
    'x_build_solution_tree__mutmut_198': x_build_solution_tree__mutmut_198, 
    'x_build_solution_tree__mutmut_199': x_build_solution_tree__mutmut_199, 
    'x_build_solution_tree__mutmut_200': x_build_solution_tree__mutmut_200, 
    'x_build_solution_tree__mutmut_201': x_build_solution_tree__mutmut_201, 
    'x_build_solution_tree__mutmut_202': x_build_solution_tree__mutmut_202, 
    'x_build_solution_tree__mutmut_203': x_build_solution_tree__mutmut_203, 
    'x_build_solution_tree__mutmut_204': x_build_solution_tree__mutmut_204, 
    'x_build_solution_tree__mutmut_205': x_build_solution_tree__mutmut_205, 
    'x_build_solution_tree__mutmut_206': x_build_solution_tree__mutmut_206, 
    'x_build_solution_tree__mutmut_207': x_build_solution_tree__mutmut_207, 
    'x_build_solution_tree__mutmut_208': x_build_solution_tree__mutmut_208, 
    'x_build_solution_tree__mutmut_209': x_build_solution_tree__mutmut_209, 
    'x_build_solution_tree__mutmut_210': x_build_solution_tree__mutmut_210, 
    'x_build_solution_tree__mutmut_211': x_build_solution_tree__mutmut_211, 
    'x_build_solution_tree__mutmut_212': x_build_solution_tree__mutmut_212, 
    'x_build_solution_tree__mutmut_213': x_build_solution_tree__mutmut_213
}

def build_solution_tree(*args, **kwargs):
    result = _mutmut_trampoline(x_build_solution_tree__mutmut_orig, x_build_solution_tree__mutmut_mutants, args, kwargs)
    return result 

build_solution_tree.__signature__ = _mutmut_signature(x_build_solution_tree__mutmut_orig)
x_build_solution_tree__mutmut_orig.__name__ = 'x_build_solution_tree'


def x_emit_solution_xml__mutmut_orig(config: SolutionManifestConfig) -> str:
    """Serialize ``config`` to the Dynamics unmanaged solution XML string."""

    tree = build_solution_tree(config)
    return tostring(tree, encoding="utf-8", xml_declaration=True).decode("utf-8")


def x_emit_solution_xml__mutmut_1(config: SolutionManifestConfig) -> str:
    """Serialize ``config`` to the Dynamics unmanaged solution XML string."""

    tree = None
    return tostring(tree, encoding="utf-8", xml_declaration=True).decode("utf-8")


def x_emit_solution_xml__mutmut_2(config: SolutionManifestConfig) -> str:
    """Serialize ``config`` to the Dynamics unmanaged solution XML string."""

    tree = build_solution_tree(None)
    return tostring(tree, encoding="utf-8", xml_declaration=True).decode("utf-8")


def x_emit_solution_xml__mutmut_3(config: SolutionManifestConfig) -> str:
    """Serialize ``config`` to the Dynamics unmanaged solution XML string."""

    tree = build_solution_tree(config)
    return tostring(tree, encoding="utf-8", xml_declaration=True).decode(None)


def x_emit_solution_xml__mutmut_4(config: SolutionManifestConfig) -> str:
    """Serialize ``config`` to the Dynamics unmanaged solution XML string."""

    tree = build_solution_tree(config)
    return tostring(None, encoding="utf-8", xml_declaration=True).decode("utf-8")


def x_emit_solution_xml__mutmut_5(config: SolutionManifestConfig) -> str:
    """Serialize ``config`` to the Dynamics unmanaged solution XML string."""

    tree = build_solution_tree(config)
    return tostring(tree, encoding=None, xml_declaration=True).decode("utf-8")


def x_emit_solution_xml__mutmut_6(config: SolutionManifestConfig) -> str:
    """Serialize ``config`` to the Dynamics unmanaged solution XML string."""

    tree = build_solution_tree(config)
    return tostring(tree, encoding="utf-8", xml_declaration=None).decode("utf-8")


def x_emit_solution_xml__mutmut_7(config: SolutionManifestConfig) -> str:
    """Serialize ``config`` to the Dynamics unmanaged solution XML string."""

    tree = build_solution_tree(config)
    return tostring(encoding="utf-8", xml_declaration=True).decode("utf-8")


def x_emit_solution_xml__mutmut_8(config: SolutionManifestConfig) -> str:
    """Serialize ``config`` to the Dynamics unmanaged solution XML string."""

    tree = build_solution_tree(config)
    return tostring(tree, xml_declaration=True).decode("utf-8")


def x_emit_solution_xml__mutmut_9(config: SolutionManifestConfig) -> str:
    """Serialize ``config`` to the Dynamics unmanaged solution XML string."""

    tree = build_solution_tree(config)
    return tostring(tree, encoding="utf-8", ).decode("utf-8")


def x_emit_solution_xml__mutmut_10(config: SolutionManifestConfig) -> str:
    """Serialize ``config`` to the Dynamics unmanaged solution XML string."""

    tree = build_solution_tree(config)
    return tostring(tree, encoding="XXutf-8XX", xml_declaration=True).decode("utf-8")


def x_emit_solution_xml__mutmut_11(config: SolutionManifestConfig) -> str:
    """Serialize ``config`` to the Dynamics unmanaged solution XML string."""

    tree = build_solution_tree(config)
    return tostring(tree, encoding="UTF-8", xml_declaration=True).decode("utf-8")


def x_emit_solution_xml__mutmut_12(config: SolutionManifestConfig) -> str:
    """Serialize ``config`` to the Dynamics unmanaged solution XML string."""

    tree = build_solution_tree(config)
    return tostring(tree, encoding="utf-8", xml_declaration=False).decode("utf-8")


def x_emit_solution_xml__mutmut_13(config: SolutionManifestConfig) -> str:
    """Serialize ``config`` to the Dynamics unmanaged solution XML string."""

    tree = build_solution_tree(config)
    return tostring(tree, encoding="utf-8", xml_declaration=True).decode("XXutf-8XX")


def x_emit_solution_xml__mutmut_14(config: SolutionManifestConfig) -> str:
    """Serialize ``config`` to the Dynamics unmanaged solution XML string."""

    tree = build_solution_tree(config)
    return tostring(tree, encoding="utf-8", xml_declaration=True).decode("UTF-8")

x_emit_solution_xml__mutmut_mutants : ClassVar[MutantDict] = {
'x_emit_solution_xml__mutmut_1': x_emit_solution_xml__mutmut_1, 
    'x_emit_solution_xml__mutmut_2': x_emit_solution_xml__mutmut_2, 
    'x_emit_solution_xml__mutmut_3': x_emit_solution_xml__mutmut_3, 
    'x_emit_solution_xml__mutmut_4': x_emit_solution_xml__mutmut_4, 
    'x_emit_solution_xml__mutmut_5': x_emit_solution_xml__mutmut_5, 
    'x_emit_solution_xml__mutmut_6': x_emit_solution_xml__mutmut_6, 
    'x_emit_solution_xml__mutmut_7': x_emit_solution_xml__mutmut_7, 
    'x_emit_solution_xml__mutmut_8': x_emit_solution_xml__mutmut_8, 
    'x_emit_solution_xml__mutmut_9': x_emit_solution_xml__mutmut_9, 
    'x_emit_solution_xml__mutmut_10': x_emit_solution_xml__mutmut_10, 
    'x_emit_solution_xml__mutmut_11': x_emit_solution_xml__mutmut_11, 
    'x_emit_solution_xml__mutmut_12': x_emit_solution_xml__mutmut_12, 
    'x_emit_solution_xml__mutmut_13': x_emit_solution_xml__mutmut_13, 
    'x_emit_solution_xml__mutmut_14': x_emit_solution_xml__mutmut_14
}

def emit_solution_xml(*args, **kwargs):
    result = _mutmut_trampoline(x_emit_solution_xml__mutmut_orig, x_emit_solution_xml__mutmut_mutants, args, kwargs)
    return result 

emit_solution_xml.__signature__ = _mutmut_signature(x_emit_solution_xml__mutmut_orig)
x_emit_solution_xml__mutmut_orig.__name__ = 'x_emit_solution_xml'
