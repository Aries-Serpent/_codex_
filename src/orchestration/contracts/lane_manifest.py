"""Lane Manifest Contract — Immutable lane execution manifest.

Generates and validates lane manifests containing identity, dependencies,
inputs, and metadata for orchestration contracts.
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import jsonschema


class LaneManifestError(Exception):
    """Raised when lane manifest operations fail."""

    pass


class LaneManifestContract:
    """Manages immutable lane manifest generation and validation."""

    SCHEMA = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Lane Manifest",
        "type": "object",
        "required": [
            "lane_id",
            "lane_name",
            "execution_mode",
            "owner",
            "run_id",
            "timestamp",
            "dependencies",
            "inputs",
            "provenance",
        ],
        "properties": {
            "lane_id": {
                "type": "string",
                "enum": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K"],
            },
            "lane_name": {"type": "string"},
            "execution_mode": {
                "type": "string",
                "enum": ["sequential", "parallel", "parallel_sharded"],
            },
            "owner": {"type": "string"},
            "run_id": {"type": "string", "format": "uuid"},
            "timestamp": {
                "type": "string",
                "pattern": r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$",
            },
            "dependencies": {
                "type": "object",
                "properties": {
                    "upstream_lanes": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K"],
                        },
                    },
                    "upstream_gates": {
                        "type": "object",
                        "additionalProperties": {
                            "type": "string",
                            "enum": ["pass", "fail", "pending"],
                        },
                    },
                },
            },
            "inputs": {
                "type": "object",
                "properties": {
                    "input_lock": {"type": "string"},
                    "seed": {"type": "integer"},
                    "policy_version": {"type": "string"},
                    "solver_version": {"type": "string"},
                },
            },
            "execution_order": {"type": "array", "items": {"type": "string"}},
            "expected_outputs": {"type": "array", "items": {"type": "string"}},
            "provenance": {
                "type": "object",
                "properties": {
                    "created_by": {"type": "string"},
                    "created_at": {
                        "type": "string",
                        "pattern": r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$",
                    },
                    "git_sha": {"type": "string", "pattern": "^[a-f0-9]{40}$"},
                },
            },
        },
    }

    @staticmethod
    def _utc_timestamp() -> str:
        """Generate ISO 8601 UTC timestamp with Z suffix."""
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    @classmethod
    def generate(
        cls,
        lane_id: str,
        lane_name: str,
        execution_mode: str,
        owner: str,
        inputs: Dict[str, Any],
        dependencies: Optional[Dict[str, Any]] = None,
        execution_order: Optional[List[str]] = None,
        expected_outputs: Optional[List[str]] = None,
        git_sha: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate an immutable lane manifest.

        Args:
            lane_id: Lane identifier (A-K)
            lane_name: Human-readable lane name
            execution_mode: Execution mode (sequential, parallel, etc.)
            owner: Agent or user responsible for lane
            inputs: Dict with input_lock, seed, policy_version, solver_version
            dependencies: Optional dict with upstream_lanes and upstream_gates
            execution_order: Optional list of tasks to execute
            expected_outputs: Optional list of expected output files
            git_sha: Optional Git SHA for provenance

        Returns:
            Immutable manifest dictionary

        Raises:
            LaneManifestError: If generation fails or validation fails
        """
        try:
            # Generate UUID for run_id
            run_id = str(uuid.uuid4())

            # Build manifest
            manifest = {
                "lane_id": lane_id,
                "lane_name": lane_name,
                "execution_mode": execution_mode,
                "owner": owner,
                "run_id": run_id,
                "timestamp": cls._utc_timestamp(),
                "dependencies": dependencies or {"upstream_lanes": [], "upstream_gates": {}},
                "inputs": inputs,
                "provenance": {
                    "created_by": owner,
                    "created_at": cls._utc_timestamp(),
                },
            }

            if git_sha:
                manifest["provenance"]["git_sha"] = git_sha

            if execution_order:
                manifest["execution_order"] = execution_order

            if expected_outputs:
                manifest["expected_outputs"] = expected_outputs

            # Validate against schema
            jsonschema.validate(manifest, cls.SCHEMA)

            return manifest

        except jsonschema.ValidationError as e:
            raise LaneManifestError(f"Manifest validation failed: {e}")
        except Exception as e:
            raise LaneManifestError(f"Failed to generate manifest: {e}")

    @classmethod
    def validate_manifest(cls, manifest: Dict[str, Any]) -> bool:
        """Validate that a manifest conforms to schema.

        Args:
            manifest: Manifest dictionary to validate

        Returns:
            True if valid

        Raises:
            LaneManifestError: If validation fails
        """
        try:
            jsonschema.validate(manifest, cls.SCHEMA)
            return True
        except jsonschema.ValidationError as e:
            raise LaneManifestError(f"Manifest validation failed: {e}")
        except Exception as e:
            raise LaneManifestError(f"Failed to validate manifest: {e}")

    @classmethod
    def validate_upstream_gates(cls, manifest: Dict[str, Any]) -> bool:
        """Validate that all upstream gates are resolved (not pending).

        Args:
            manifest: Manifest to validate

        Returns:
            True if all gates are resolved

        Raises:
            LaneManifestError: If gates are not resolved
        """
        upstream_gates = manifest.get("dependencies", {}).get("upstream_gates", {})

        for gate_name, gate_status in upstream_gates.items():
            if gate_status == "pending":
                raise LaneManifestError(
                    f"Upstream gate '{gate_name}' is still pending"
                )
            if gate_status not in ["pass", "fail"]:
                raise LaneManifestError(
                    f"Invalid gate status '{gate_status}' for gate '{gate_name}'"
                )

        return True

    @classmethod
    def write_manifest_file(
        cls, manifest: Dict[str, Any], output_path: Path
    ) -> None:
        """Write lane-manifest.json to disk.

        Args:
            manifest: Manifest dictionary
            output_path: Path to write manifest file

        Raises:
            LaneManifestError: If write fails
        """
        try:
            # Validate first
            cls.validate_manifest(manifest)

            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(manifest, f, indent=2)
        except LaneManifestError:
            raise
        except Exception as e:
            raise LaneManifestError(f"Failed to write manifest file: {e}")
