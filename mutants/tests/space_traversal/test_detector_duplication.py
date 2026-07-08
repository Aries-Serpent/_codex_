"""
Test Detector Duplication

Test module for detector duplication.
"""

from __future__ import annotations

import importlib.util
import types
from collections.abc import Iterable
from pathlib import Path
from typing import Any


def _load_module(path: Path, name: str) -> types.ModuleType:
    if not path.is_absolute():
        repo_root = Path(__file__).resolve().parents[2]
        path = repo_root / path
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    assert spec and spec.loader, "spec is not valid"
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def _context_index_for(paths: Iterable[Path]) -> dict[str, Any]:
    return {
        "files": [
            {
                "path": str(path.resolve()),
            }
            for path in paths
        ],
    }


def test_detector_duplication_ratio(tmp_path: Path) -> None:
    files = [
        tmp_path / "foo.py",
        tmp_path / "foo.md",
        tmp_path / "bar.py",
    ]
    files[0].write_text("logger.info('x')\n", encoding="utf-8")
    files[1].write_text("# doc\n", encoding="utf-8")
    files[2].write_text("logger.info('y')\n", encoding="utf-8")

    detector_path = Path("scripts/space_traversal/detectors/detector_duplication.py")
    module = _load_module(detector_path, "detector_duplication")
    context_index = _context_index_for(files)
    result = module.detect(context_index)  # type: ignore[attr-defined]

    assert result["id"] == "duplication_ratio", "Result must not be empty"
    assert 0.0 <= result["dup_ratio"] <= 1.0, "Result must not be empty"
    assert result["counts"]["foo"] == 2, "Result must not be empty"
    assert result["evidence_count"] == 3, "Result must not be empty"
    assert result["dup_ratio"] > 0.0, "Value must be greater than zero"
