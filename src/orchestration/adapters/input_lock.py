"""Input-Lock Adapter — Deterministic input-lock generation using SHA256.

Generates immutable input locks incorporating policy config, solver info,
environment, and input checksums for deterministic replay.
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import jsonschema


class InputLockError(Exception):
    """Raised when input lock generation or validation fails."""

    pass


class InputLockAdapter:
    """Generates deterministic input locks using SHA256."""

    LOCK_VERSION = "1"
    SCHEMA = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Input Lock",
        "type": "object",
        "required": ["lock_version", "lock_hash", "generated_at", "context"],
        "properties": {
            "lock_version": {"type": "string", "const": "1"},
            "lock_hash": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
            "generated_at": {
                "type": "string",
                "pattern": r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$",
            },
            "context": {
                "type": "object",
                "required": [
                    "policy_config",
                    "solver_info",
                    "environment",
                    "input_checksums",
                ],
                "properties": {
                    "policy_config": {"type": "object"},
                    "solver_info": {"type": "object"},
                    "environment": {"type": "object"},
                    "input_checksums": {
                        "type": "object",
                        "additionalProperties": {"type": "string"},
                    },
                },
            },
        },
    }

    @staticmethod
    def _utc_timestamp() -> str:
        """Generate ISO 8601 UTC timestamp with Z suffix (no +00:00)."""
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    @staticmethod
    def _compute_hash(
        policy_config: Dict[str, Any],
        solver_info: Dict[str, Any],
        environment: Dict[str, Any],
        input_checksums: Dict[str, str],
    ) -> str:
        """Compute SHA256 hash of combined context.

        Args:
            policy_config: Policy configuration dict
            solver_info: Solver information dict
            environment: Environment dict
            input_checksums: Mapping of input names to their checksums

        Returns:
            SHA256 hex digest (64 character string)
        """
        # Serialize each component in a deterministic order
        data_to_hash = json.dumps(
            {
                "policy_config": policy_config,
                "solver_info": solver_info,
                "environment": environment,
                "input_checksums": input_checksums,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(data_to_hash.encode()).hexdigest()

    @classmethod
    def generate(
        cls,
        policy_config: Dict[str, Any],
        solver_info: Dict[str, Any],
        environment: Dict[str, Any],
        input_checksums: Dict[str, str],
    ) -> tuple[str, Dict[str, Any]]:
        """Generate input lock with SHA256 hash.

        Args:
            policy_config: Policy configuration dict
            solver_info: Solver information dict
            environment: Environment dict
            input_checksums: Mapping of input names to checksums

        Returns:
            Tuple of (lock_hash, lock_dict)

        Raises:
            InputLockError: If generation fails
        """
        try:
            lock_hash = cls._compute_hash(
                policy_config, solver_info, environment, input_checksums
            )

            lock_dict = {
                "lock_version": cls.LOCK_VERSION,
                "lock_hash": lock_hash,
                "generated_at": cls._utc_timestamp(),
                "context": {
                    "policy_config": policy_config,
                    "solver_info": solver_info,
                    "environment": environment,
                    "input_checksums": input_checksums,
                },
            }

            # Validate against schema
            jsonschema.validate(lock_dict, cls.SCHEMA)

            return lock_hash, lock_dict
        except jsonschema.ValidationError as e:
            raise InputLockError(f"Lock dict validation failed: {e}")
        except Exception as e:
            raise InputLockError(f"Failed to generate input lock: {e}")

    @classmethod
    def write_lock_file(
        cls, lock_dict: Dict[str, Any], output_path: Path
    ) -> None:
        """Write input-lock.json to disk.

        Args:
            lock_dict: Lock dictionary from generate()
            output_path: Path to write lock file

        Raises:
            InputLockError: If write fails
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(lock_dict, f, indent=2)
        except Exception as e:
            raise InputLockError(f"Failed to write lock file: {e}")

    @classmethod
    def validate_lock_hash(
        cls,
        lock_dict: Dict[str, Any],
    ) -> bool:
        """Validate that lock_hash matches recalculation.

        Args:
            lock_dict: Lock dictionary to validate

        Returns:
            True if hash is valid

        Raises:
            InputLockError: If validation fails
        """
        try:
            # Validate schema first
            jsonschema.validate(lock_dict, cls.SCHEMA)

            context = lock_dict["context"]
            recalculated_hash = cls._compute_hash(
                context["policy_config"],
                context["solver_info"],
                context["environment"],
                context["input_checksums"],
            )

            if recalculated_hash != lock_dict["lock_hash"]:
                raise InputLockError(
                    f"Hash mismatch: expected {lock_dict['lock_hash']}, "
                    f"got {recalculated_hash}"
                )

            return True
        except jsonschema.ValidationError as e:
            raise InputLockError(f"Schema validation failed: {e}")
        except InputLockError:
            raise
        except Exception as e:
            raise InputLockError(f"Failed to validate lock hash: {e}")
