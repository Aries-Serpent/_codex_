"""
Test Detector Peft

Test module for detector peft.
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


def test_detector_peft_finds_tokens(tmp_path: Path) -> None:
    content = (
        "\nfrom peft import LoraConfig, get_peft_model\n"
        "def wire(model):\n"
        "    return get_peft_model(model, LoraConfig(r=8, lora_alpha=16))\n"
    )
    file_path = tmp_path / "modeling.py"
    file_path.write_text(content, encoding="utf-8")

    detector_path = Path("scripts/space_traversal/detectors/detector_peft.py")
    module = _load_module(detector_path, "detector_peft")
    context_index = _context_index_for([file_path])
    result = module.detect(context_index)  # type: ignore[attr-defined]

    assert result["id"] == "peft_hooks", "Result must not be empty"
    assert result["files_with_peft"] == 1, "Result must not be empty"
    assert "LoraConfig" in list(result["evidence"].values())[0], "Result must not be empty"
