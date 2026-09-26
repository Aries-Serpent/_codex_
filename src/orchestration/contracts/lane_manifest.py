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
            "lane_isolation": {
                "type": "object",
                "properties": {
                    "namespace": {"type": "string"},
                    "read_scope": {"type": "array", "items": {"type": "string"}},
                    "write_scope": {"type": "array", "items": {"type": "string"}},
                    "shared_state": {"type": "array", "items": {"type": "string"}},
                    "cutover_guard": {"type": "string"},
                },
            },
            "handoff": {
                "type": "object",
                "properties": {
                    "source_lane": {"type": "string"},
                    "target_lane": {"type": "string"},
                    "mode": {
                        "type": "string",
                        "enum": ["pass", "yield", "checkpoint", "escalate", "abort"],
                    },
                    "status": {
                        "type": "string",
                        "enum": ["pending", "accepted", "rejected", "blocked"],
                    },
                    "result_contract": {"type": "string"},
                    "checkpoint_id": {"type": "string"},
                },
            },
            "azimuth": {
                "type": "object",
                "properties": {
                    "target": {"type": "integer", "minimum": 0, "maximum": 359},
                    "reference": {"type": "string"},
                    "alignment": {
                        "type": "string",
                        "enum": ["aligned", "reoriented", "blocked"],
                    },
                    "delta_deg": {"type": "integer", "minimum": 0, "maximum": 180},
                    "locked": {"type": "boolean"},
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
        lane_isolation: Optional[Dict[str, Any]] = None,
        handoff: Optional[Dict[str, Any]] = None,
        azimuth: Optional[Dict[str, Any]] = None,
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
            lane_isolation: Optional isolation contract describing read/write scopes
            handoff: Optional handoff contract for lane-to-lane transfer
            azimuth: Optional azimuth alignment metadata for directional compliance

        Returns:
            Immutable manifest dictionary

        Raises:
            LaneManifestError: If generation fails or validation fails
        """
        try:
            # Generate UUID for run_id
            run_id = str(uuid.uuid4())

            # Build manifest
            manifest: Dict[str, Any] = {
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

            if lane_isolation is not None:
                manifest["lane_isolation"] = lane_isolation

            if handoff is not None:
                manifest["handoff"] = handoff

            if azimuth is not None:
                manifest["azimuth"] = azimuth

            if git_sha:
                manifest["provenance"]["git_sha"] = git_sha

            if execution_order:
                manifest["execution_order"] = execution_order

            if expected_outputs:
                manifest["expected_outputs"] = expected_outputs

            # Validate against schema and semantic invariants before returning.
            jsonschema.validate(manifest, cls.SCHEMA)
            cls.validate_lane_isolation(manifest)
            cls.validate_handoff_contract(manifest)
            cls.validate_azimuth_alignment(manifest)

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
            cls.validate_lane_isolation(manifest)
            cls.validate_handoff_contract(manifest)
            cls.validate_azimuth_alignment(manifest)
            return True
        except jsonschema.ValidationError as e:
            raise LaneManifestError(f"Manifest validation failed: {e}")
        except Exception as e:
            raise LaneManifestError(f"Failed to validate manifest: {e}")

    @staticmethod
    def _normalize_lane_namespace(namespace: str) -> str:
        """Normalize a lane namespace such as `lane/A` to a canonical lane key."""
        if not isinstance(namespace, str):
            return ""
        normalized = namespace.strip().rstrip("/")
        if normalized.startswith("lane/"):
            return normalized.split("/", 1)[1]
        return normalized

    @classmethod
    def validate_lane_isolation(cls, manifest: Dict[str, Any]) -> bool:
        """Validate lane isolation semantics for a manifest.

        A lane may read only its shared and upstream artifacts plus its own
        namespace, and must not mutate sibling lane state without an explicit
        handoff contract.
        """
        lane_isolation = manifest.get("lane_isolation")
        if lane_isolation is None:
            return True

        required = {"namespace", "read_scope", "write_scope"}
        missing = sorted(required - set(lane_isolation.keys()))
        if missing:
            raise LaneManifestError("lane_isolation missing required fields: " + ", ".join(missing))

        read_scope = lane_isolation.get("read_scope")
        write_scope = lane_isolation.get("write_scope")
        if not isinstance(read_scope, list):
            raise LaneManifestError("lane_isolation.read_scope must be a list")
        if not isinstance(write_scope, list):
            raise LaneManifestError("lane_isolation.write_scope must be a list")

        lane_namespace = cls._normalize_lane_namespace(lane_isolation.get("namespace", ""))
        lane_key = lane_namespace.split("/", 1)[0] if lane_namespace else ""

        for scope in read_scope:
            if not isinstance(scope, str):
                raise LaneManifestError("lane_isolation.read_scope entries must be strings")
            normalized = scope.strip()
            if not normalized:
                raise LaneManifestError("lane_isolation.read_scope entries cannot be empty")
            if normalized in {
                "shared",
                "shared/*",
                "shared/**",
                "upstream",
                "upstream/*",
                "upstream/**",
            }:
                continue
            if normalized.startswith("shared/") or normalized.startswith("upstream/"):
                continue
            if lane_key and (
                normalized == f"lane/{lane_key}" or normalized.startswith(f"lane/{lane_key}/")
            ):
                continue
            if lane_key and normalized == lane_key:
                continue
            raise LaneManifestError(
                "lane_isolation.read_scope exceeds the documented shared/upstream/own allowance: "
                f"{scope}"
            )

        for scope in write_scope:
            if not isinstance(scope, str):
                raise LaneManifestError("lane_isolation.write_scope entries must be strings")
            normalized = scope.strip()
            if not normalized:
                raise LaneManifestError("lane_isolation.write_scope entries cannot be empty")
            if normalized in {
                "shared",
                "shared/*",
                "shared/**",
                "upstream",
                "upstream/*",
                "upstream/**",
            }:
                continue
            if normalized.startswith("shared/") or normalized.startswith("upstream/"):
                continue
            if lane_key and (
                normalized == f"lane/{lane_key}" or normalized.startswith(f"lane/{lane_key}/")
            ):
                continue
            if normalized.startswith("lane/"):
                target_lane = normalized.split("/", 2)[1]
                if target_lane != lane_key:
                    raise LaneManifestError(
                        f"lane_isolation.write_scope must not target sibling lanes: {scope}"
                    )
                continue
            raise LaneManifestError(
                "lane_isolation.write_scope must stay within shared/upstream or the current lane: "
                f"{scope}"
            )
        return True

    @classmethod
    def validate_handoff_contract(cls, manifest: Dict[str, Any]) -> bool:
        """Validate lane-to-lane handoff semantics.

        Handoffs are only valid when the origin and target lanes are declared and
        the mode is one of the supported explicit checkpoint handoff states.
        """
        handoff = manifest.get("handoff")
        if handoff is None:
            return True

        for key in ("source_lane", "target_lane", "mode", "status", "result_contract"):
            if key not in handoff:
                raise LaneManifestError(f"handoff missing required field: {key}")

        source_lane = handoff.get("source_lane")
        target_lane = handoff.get("target_lane")
        if source_lane not in set("ABCDEFGHIJK") or target_lane not in set("ABCDEFGHIJK"):
            raise LaneManifestError(
                "handoff source_lane and target_lane must be declared lane IDs A-K"
            )
        if source_lane == target_lane:
            raise LaneManifestError("handoff source_lane and target_lane must differ")

        if handoff["mode"] not in {"pass", "yield", "checkpoint", "escalate", "abort"}:
            raise LaneManifestError(f"Unsupported handoff mode: {handoff['mode']}")

        if handoff["status"] not in {"pending", "accepted", "rejected", "blocked"}:
            raise LaneManifestError(f"Unsupported handoff status: {handoff['status']}")

        if handoff["status"] == "accepted" and not handoff.get("result_contract"):
            raise LaneManifestError("accepted handoffs require a result_contract")
        if (
            handoff.get("mode") == "checkpoint"
            and handoff.get("status") == "accepted"
            and not handoff.get("checkpoint_id")
        ):
            raise LaneManifestError("checkpoint handoffs require a checkpoint_id when accepted")
        return True

    @classmethod
    def validate_azimuth_alignment(cls, manifest: Dict[str, Any]) -> bool:
        """Validate azimuth alignment and lane directional intent.

        Azimuth is a directional objective vector for an active lane. Any lane
        receiving a handoff must either be aligned to the same target azimuth or
        be explicitly marked as reoriented or blocked before work continues.
        """
        azimuth = manifest.get("azimuth")
        if azimuth is None:
            return True

        target = azimuth.get("target")
        if target is not None and not 0 <= int(target) <= 359:
            raise LaneManifestError("azimuth.target must be an integer between 0 and 359")

        if azimuth.get("alignment") not in {"aligned", "reoriented", "blocked"}:
            raise LaneManifestError("azimuth.alignment must be aligned, reoriented, or blocked")

        delta_deg = azimuth.get("delta_deg")
        if delta_deg is not None and not 0 <= int(delta_deg) <= 180:
            raise LaneManifestError("azimuth.delta_deg must be between 0 and 180")

        if azimuth.get("alignment") == "aligned" and delta_deg is not None and int(delta_deg) > 15:
            raise LaneManifestError(
                "aligned azimuth must remain within the 15 degree coherence window"
            )

        if azimuth.get("alignment") == "blocked" and azimuth.get("locked") is not False:
            raise LaneManifestError("blocked azimuth must be explicitly unlocked before resume")

        return True

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
                raise LaneManifestError(f"Upstream gate '{gate_name}' is still pending")
            if gate_status not in ["pass", "fail"]:
                raise LaneManifestError(
                    f"Invalid gate status '{gate_status}' for gate '{gate_name}'"
                )

        return True

    @classmethod
    def write_manifest_file(cls, manifest: Dict[str, Any], output_path: Path) -> None:
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
