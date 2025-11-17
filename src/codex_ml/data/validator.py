"""Dataset manifest validation utilities."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

try:  # pragma: no cover - optional dependency
    from jsonschema import ValidationError, validate
except Exception:  # pragma: no cover
    ValidationError = Exception  # type: ignore[assignment]

    def validate(*_args: Any, **_kwargs: Any) -> None:
        raise ImportError("jsonschema is required for dataset validation")


LOGGER = logging.getLogger(__name__)


class DatasetValidator:
    """Validate dataset manifests against the Codex schema."""

    _ROOT = next(
        (
            parent
            for parent in Path(__file__).resolve().parents
            if (parent / "pyproject.toml").exists()
        ),
        Path(__file__).resolve().parents[3],
    )
    SCHEMA_PATH = _ROOT / "configs/schemas/dataset_manifest.schema.json"

    @classmethod
    def _load_json(cls, path: Path) -> Any:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    @classmethod
    def validate_manifest(cls, manifest_path: Path) -> bool:
        manifest_path = manifest_path.expanduser()
        schema = cls._load_json(cls.SCHEMA_PATH)
        manifest = cls._load_json(manifest_path)
        try:
            validate(instance=manifest, schema=schema)
            LOGGER.info("✓ Manifest valid: %s", manifest_path)
            return True
        except ImportError:
            raise
        except ValidationError as exc:
            # ValidationError has a 'message' attribute when jsonschema is available
            error_msg = getattr(exc, "message", str(exc))
            LOGGER.error("✗ Manifest invalid (%s): %s", manifest_path, error_msg)
            return False
        except Exception as exc:  # pragma: no cover - defensive
            LOGGER.error("✗ Manifest validation failed: %s", exc)
            return False

    @classmethod
    def validate_splits(cls, manifest_path: Path) -> bool:
        manifest_path = manifest_path.expanduser()
        manifest = cls._load_json(manifest_path)
        base_path = manifest_path.parent
        missing: list[Path] = []

        splits = manifest.get("splits")
        if isinstance(splits, list):
            for split_info in splits:
                if isinstance(split_info, dict) and "path" in split_info:
                    candidate = base_path / str(split_info["path"])
                    if not candidate.exists():
                        missing.append(candidate)
        checksums = manifest.get("checksums", [])
        if isinstance(checksums, list):
            for entry in checksums:
                if isinstance(entry, dict) and "path" in entry:
                    candidate = base_path / str(entry["path"])
                    if not candidate.exists():
                        missing.append(candidate)

        if missing:
            for candidate in missing:
                LOGGER.error("✗ Referenced dataset file missing: %s", candidate)
            return False

        LOGGER.info("✓ All referenced dataset files present")
        return True


__all__ = ["DatasetValidator"]
