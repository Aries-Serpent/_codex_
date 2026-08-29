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


import json  # noqa: E402
from html import escape as html_escape  # noqa: E402
from pathlib import Path  # noqa: E402

try:
    from defusedxml.ElementTree import fromstring as safe_xml_fromstring
except ImportError as exc:
    error_type = type(exc).__name__
    logger.debug("ImportError: <ERROR_TYPE>")
    raise ImportError(
        "defusedxml is required for safe XML handling in solution_xml; install it via pip"
    ) from exc

from pydantic import AliasChoices, BaseModel, Field  # noqa: E402

from codex.evidence import utc_now  # noqa: E402

__all__ = [
    "LocalizedName",
    "Publisher",
    "RootComponent",
    "SolutionManifestConfig",
    "build_solution_tree",
    "emit_solution_xml",
    "load_solution_manifest",
]


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

    def with_overrides(
        self, *, name: str | None = None, version: str | None = None
    ) -> SolutionManifestConfig:
        data = self.model_dump()
        if name is not None:
            data["unique_name"] = name
        if version is not None:
            data["version"] = version
        return SolutionManifestConfig.model_validate(data)


def _resolve_config_dir(config_dir: Path) -> Path:
    if config_dir.exists():
        return config_dir
    if config_dir.is_absolute():
        return config_dir
    repo_root = Path(__file__).resolve().parents[3]
    return repo_root / config_dir


def load_solution_manifest(config_dir: Path | None = None) -> SolutionManifestConfig:
    """Load the solution manifest definition from ``configs/deployment/d365``."""

    base = _resolve_config_dir(config_dir or Path("configs/deployment/d365"))
    config_path = base / "solution_manifest.json"
    if not config_path.exists():
        return SolutionManifestConfig()
    data = json.loads(config_path.read_text(encoding="utf-8"))
    return SolutionManifestConfig.model_validate(data)


def _xml_text(value: str) -> str:
    return html_escape(value, quote=True)


def _xml_attrs(**attrs: str | None) -> str:
    parts = [f' {key}="{_xml_text(value)}"' for key, value in attrs.items() if value is not None]
    return "".join(parts)


def _xml_node(
    tag: str,
    value: str | None = None,
    *,
    attrs: dict[str, str | None] | None = None,
) -> str:
    attr_text = _xml_attrs(**(attrs or {}))
    if value is None:
        return f"<{tag}{attr_text}/>"
    return f"<{tag}{attr_text}>{_xml_text(value)}</{tag}>"


def build_solution_tree(config: SolutionManifestConfig) -> str:
    """Construct the XML string for ``config`` without reparsing it."""

    manifest_nodes = [
        _xml_node("UniqueName", config.unique_name),
        _xml_node("Version", config.version),
        _xml_node("Managed", "1" if config.managed else "0"),
    ]

    if config.friendly_name:
        manifest_nodes.append(_xml_node("FriendlyName", config.friendly_name))
    if config.description:
        manifest_nodes.append(_xml_node("Description", config.description))

    if config.publisher:
        manifest_nodes.append(
            "".join(
                [
                    "<Publisher>",
                    _xml_node("UniqueName", config.publisher.unique_name),
                    _xml_node("FriendlyName", config.publisher.friendly_name or ""),
                    _xml_node("Prefix", config.publisher.prefix),
                    "</Publisher>",
                ]
            )
        )

    if config.localized_names:
        localized = "".join(
            _xml_node(
                "LocalizedName",
                attrs={
                    "description": entry.description,
                    "languagecode": str(entry.languagecode),
                },
            )
            for entry in config.localized_names
        )
        manifest_nodes.append(f"<LocalizedNames>{localized}</LocalizedNames>")

    manifest_nodes.append(_xml_node("GeneratedOn", utc_now()))

    root_components = "".join(
        _xml_node(
            "RootComponent",
            attrs={
                "type": str(component.type),
                "schemaName": component.schema_name,
                "behavior": str(component.behavior) if component.behavior is not None else None,
                "includeSubcomponents": (
                    str(component.include_subcomponents)
                    if component.include_subcomponents is not None
                    else None
                ),
                "id": component.component_id,
            },
        )
        for component in config.root_components
    )
    manifest_nodes.append(f"<RootComponents>{root_components}</RootComponents>")

    dependencies = "".join(_xml_node("Dependency", dep) for dep in config.dependencies)
    manifest_nodes.append(f"<Dependencies>{dependencies}</Dependencies>")
    manifest_nodes.append(_xml_node("SourceSolutionType", "0"))
    manifest_nodes.append(_xml_node("SolutionPackageVersion", config.version))

    return (
        f"<ImportExportXml>"
        f"<SolutionManifest>{''.join(manifest_nodes)}</SolutionManifest>"
        f"</ImportExportXml>"
    )


def emit_solution_xml(config: SolutionManifestConfig) -> str:
    """Serialize ``config`` to the Dynamics unmanaged solution XML string.

    Security Guarantees:
    - Uses defusedxml.ElementTree for XXE attack prevention
    - Validates against DOCTYPE declarations
    - Prevents XML entity expansion attacks
    - No external entity resolution
    """

    xml = f'<?xml version="1.0" encoding="utf-8"?>{build_solution_tree(config)}'

    # XXE Protection: Check for DOCTYPE declarations which could be attack vectors
    if "<!DOCTYPE" in xml.upper():
        raise ValueError("DOCTYPE declarations are not permitted in solution XML")

    # XXE Protection: Validate with defusedxml parser (prevents XXE, billion laughs, etc.)
    try:
        safe_xml_fromstring(xml)
    except (ValueError, TypeError) as exc:
        type(exc).__name__
        logger.error("XML validation failed: <ERROR_TYPE>")
        raise ValueError(f"Generated XML failed validation: {exc}") from exc

    return xml
