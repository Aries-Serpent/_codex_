"""Emit unmanaged Dynamics 365 Solution XML from config-as-data."""

from __future__ import annotations

import json
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring

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
    """Load the solution manifest definition from ``config/d365``."""

    base = _resolve_config_dir(config_dir or Path("config/d365"))
    config_path = base / "solution_manifest.json"
    if not config_path.exists():
        return SolutionManifestConfig()
    data = json.loads(config_path.read_text(encoding="utf-8"))
    return SolutionManifestConfig.model_validate(data)


def build_solution_tree(config: SolutionManifestConfig) -> Element:
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


def emit_solution_xml(config: SolutionManifestConfig) -> str:
    """Serialize ``config`` to the Dynamics unmanaged solution XML string."""

    tree = build_solution_tree(config)
    return tostring(tree, encoding="utf-8", xml_declaration=True).decode("utf-8")
