"""
Manifest Parser - Parse and validate ingestion manifests.

Handles YAML manifest files that define ingestion configuration,
sample inputs, golden outputs, and execution constraints.

Author: mbaetiong
Generated: 2025-12-17

Safeguards:
- Schema validation
- Input sanitization
- Bounds checking on constraints
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, Optional

logger = logging.getLogger(__name__)

# Try to import YAML parser
try:
    import yaml

    YAML_AVAILABLE = True
except ImportError as e:
    error_type = type(e).__name__
    logger.debug("ImportError: <ERROR_TYPE>")
    logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
    YAML_AVAILABLE = False


@dataclass
class SourceConfig:
    """Source configuration in manifest."""

    type: Literal["file", "zip", "git-url"]
    path: str
    ref: Optional[str] = None


@dataclass
class SampleInput:
    """Sample input definition."""

    path: str
    description: Optional[str] = None


@dataclass
class GoldenOutput:
    """Golden output for verification."""

    input_ref: str
    expected_output: str
    comparison_mode: Literal["exact", "fuzzy", "regex", "semantic"] = "exact"


@dataclass
class Constraints:
    """Execution constraints."""

    max_runtime_seconds: int = 60
    max_memory_mb: int = 512
    allowed_network: bool = False
    allowed_file_write: bool = False
    forbidden_patterns: list[str] = field(default_factory=list)


@dataclass
class Metadata:
    """Manifest metadata."""

    owner: Optional[str] = None
    privacy: Literal["public", "private"] = "private"
    allow_external_llm: bool = False
    tags: list[str] = field(default_factory=list)


@dataclass
class IngestManifest:
    """Parsed ingestion manifest.

    Represents a complete ingestion manifest with source configuration,
    sample inputs, golden outputs, constraints, and metadata.

    Attributes:
        version: Manifest schema version
        source: Source configuration
        entry_point: Optional entry point specification
        sample_inputs: list of sample input files
        golden_outputs: list of expected outputs for verification
        constraints: Execution constraints
        metadata: Additional metadata
    """

    version: str
    source: SourceConfig
    entry_point: Optional[str] = None
    sample_inputs: list[SampleInput] = field(default_factory=list)
    golden_outputs: list[GoldenOutput] = field(default_factory=list)
    constraints: Constraints = field(default_factory=Constraints)
    metadata: Metadata = field(default_factory=Metadata)

    def to_dict(self) -> dict[str, Any]:
        """Convert manifest to dictionary."""
        return {
            "version": self.version,
            "source": {
                "type": self.source.type,
                "path": self.source.path,
                "ref": self.source.ref,
            },
            "entry_point": self.entry_point,
            "sample_inputs": [
                {"path": s.path, "description": s.description} for s in self.sample_inputs
            ],
            "golden_outputs": [
                {
                    "input_ref": g.input_ref,
                    "expected_output": g.expected_output,
                    "comparison_mode": g.comparison_mode,
                }
                for g in self.golden_outputs
            ],
            "constraints": {
                "max_runtime_seconds": self.constraints.max_runtime_seconds,
                "max_memory_mb": self.constraints.max_memory_mb,
                "allowed_network": self.constraints.allowed_network,
                "allowed_file_write": self.constraints.allowed_file_write,
                "forbidden_patterns": self.constraints.forbidden_patterns,
            },
            "metadata": {
                "owner": self.metadata.owner,
                "privacy": self.metadata.privacy,
                "allow_external_llm": self.metadata.allow_external_llm,
                "tags": self.metadata.tags,
            },
        }


def _validate_version(version: str) -> None:
    """Validate manifest version.

    Safeguard: Version format validation.
    """
    import re

    if not re.match(r"^\d+\.\d+$", version):
        raise ValueError(f"Invalid version format: {version}")


def _validate_constraints(constraints: dict[str, Any]) -> Constraints:
    """Validate and parse constraints.

    Safeguard: Bounds checking on constraint values.
    """
    max_runtime = constraints.get("max_runtime_seconds", 60)
    max_memory = constraints.get("max_memory_mb", 512)

    # Bounds checking
    if max_runtime <= 0 or max_runtime > 3600:
        raise ValueError(f"max_runtime_seconds must be 1-3600: {max_runtime}")
    if max_memory <= 0 or max_memory > 8192:
        raise ValueError(f"max_memory_mb must be 1-8192: {max_memory}")

    return Constraints(
        max_runtime_seconds=max_runtime,
        max_memory_mb=max_memory,
        allowed_network=bool(constraints.get("allowed_network", False)),
        allowed_file_write=bool(constraints.get("allowed_file_write", False)),
        forbidden_patterns=list(constraints.get("forbidden_patterns", [])),
    )


def parse_manifest(path: Path) -> IngestManifest:
    """Parse and validate an ingestion manifest file.

    Args:
        path: Path to YAML manifest file

    Returns:
        Parsed IngestManifest object

    Raises:
        FileNotFoundError: If manifest file doesn't exist
        ValueError: If manifest is invalid
        ImportError: If PyYAML is not installed

    Example:
        >>> manifest = parse_manifest(Path("manifest.yaml"))
        >>> logger.info(f"Source: {manifest.source.path}")
    """
    if not YAML_AVAILABLE:
        raise ImportError("PyYAML is required for manifest parsing")

    if not path.exists():
        raise FileNotFoundError(f"Manifest not found: {path}")

    # Read and parse YAML
    content = path.read_text(encoding="utf-8")
    data = yaml.safe_load(content)

    if not isinstance(data, dict):
        raise ValueError("Manifest must be a YAML mapping")

    # Validate required fields
    if "version" not in data:
        raise ValueError("Manifest missing required field: version")
    if "source" not in data:
        raise ValueError("Manifest missing required field: source")

    _validate_version(data["version"])

    # Parse source
    source_data = data["source"]
    if not isinstance(source_data, dict):
        raise ValueError("source must be a mapping")
    if "type" not in source_data or "path" not in source_data:
        raise ValueError("source must have type and path")

    source = SourceConfig(
        type=source_data["type"],
        path=source_data["path"],
        ref=source_data.get("ref"),
    )

    # Parse sample inputs
    sample_inputs = []
    for item in data.get("sample_inputs", []):
        if isinstance(item, dict):
            sample_inputs.append(
                SampleInput(
                    path=item["path"],
                    description=item.get("description"),
                )
            )
        elif isinstance(item, str):
            sample_inputs.append(SampleInput(path=item))

    # Parse golden outputs
    golden_outputs = []
    for item in data.get("golden_outputs", []):
        if isinstance(item, dict):
            golden_outputs.append(
                GoldenOutput(
                    input_ref=item["input_ref"],
                    expected_output=item["expected_output"],
                    comparison_mode=item.get("comparison_mode", "exact"),
                )
            )

    # Parse constraints
    constraints = _validate_constraints(data.get("constraints", {}))

    # Parse metadata
    meta_data = data.get("metadata", {})
    metadata = Metadata(
        owner=meta_data.get("owner"),
        privacy=meta_data.get("privacy", "private"),
        allow_external_llm=bool(meta_data.get("allow_external_llm", False)),
        tags=list(meta_data.get("tags", [])),
    )

    logger.info("Parsed manifest: version=%s, source=%s", data["version"], source.path)

    return IngestManifest(
        version=data["version"],
        source=source,
        entry_point=data.get("entry_point"),
        sample_inputs=sample_inputs,
        golden_outputs=golden_outputs,
        constraints=constraints,
        metadata=metadata,
    )
