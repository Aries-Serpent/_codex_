"""
Test Detector Safeguards

Test module for detector safeguards.
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


def test_detector_safeguards_hits(tmp_path: Path) -> None:
    file_a = tmp_path / "a.py"
    file_b = tmp_path / "b.md"
    file_a.write_text("seed = 123\n", encoding="utf-8")
    file_b.write_text("We run WANDB_MODE=offline for safety.\n", encoding="utf-8")

    detector_path = Path("scripts/space_traversal/detectors/detector_safeguards.py")
    module = _load_module(detector_path, "detector_safeguards")
    context_index = _context_index_for([file_a, file_b])
    result = module.detect(context_index)  # type: ignore[attr-defined]

    assert result["id"] == "safeguards_keywords", "Result must not be empty"
    assert result["total_hits"] >= 2, "Value must be greater than zero"
    assert result["unique_files"] == 2, "Result must not be empty"
    assert "a.py" in "".join(result["evidence"].keys()), "Result must not be empty"
