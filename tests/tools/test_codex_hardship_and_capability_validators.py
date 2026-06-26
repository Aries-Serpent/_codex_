"""
Test Codex Hardship And Capability Validators

Test module for codex hardship and capability validators.
"""

from pathlib import Path

import yaml

import tools.codex_capability_map_validate as cv
import tools.codex_gap_registry as gr
import tools.codex_hardship_validate as hv


def test_hardship_validator_accepts_valid_file(tmp_path: Path):
    path = tmp_path / "codex_hardship.yaml"
    path.write_text(
        yaml.safe_dump(
            {
                "gaps": {
                    "training.grad_accumulation": {
                        "risk_level": "high",
                        "notes": "test note",
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    data = hv.load_hardship(path)
    hv.validate_structure(data)  # should not raise


def test_capability_map_validator_accepts_valid_file(tmp_path: Path):
    path = tmp_path / "codex_capability_map.yaml"
    path.write_text(
        yaml.safe_dump(
            {
                "capabilities": {
                    "tokenization": {
                        "code": ["src/codex_ml/tokenization/"],
                        "tests": ["tests/codex_ml/test_tokenization_basic.py"],
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    data = cv.load_capability_map(path)
    cv.validate_structure(data)  # should not raise


def test_gap_registry_applies_hardship_and_capability_map(tmp_path: Path):
    audit = tmp_path / "audit.md"
    audit.write_text(
        "# _codex_: Status Update (2025-11-27)\n\n"
        "## High-Signal Findings\n\n"
        "- Training loop does not expose gradient accumulation settings\n",
        encoding="utf-8",
    )

    hardship_path = tmp_path / "codex_hardship.yaml"
    hardship_path.write_text(
        yaml.safe_dump(
            {
                "gaps": {
                    "training.training.loop.does.not.expose.gradient.accumulation.settings": {
                        "risk_level": "high",
                        "notes": "critical for correctness",
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    cap_map_path = tmp_path / "codex_capability_map.yaml"
    cap_map_path.write_text(
        yaml.safe_dump(
            {
                "capabilities": {
                    "training": {
                        "code": ["src/codex_ml/training/"],
                        "tests": ["tests/codex_ml/test_training_loop_smoke.py"],
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    registry = gr.build_registry(
        audit=audit,
        change_log=None,
        errors=None,
        hardship=hardship_path,
        cap_map=cap_map_path,
    )

    gaps = registry["gaps"]
    assert len(gaps) >= 1, "Gaps must not be empty"
    g0 = gaps[0]
    assert g0["capability"] == "training", "Condition must be true"
    assert g0.get("risk_level") in {None, "high"}
    assert isinstance(g0.get("location"), list)
    assert any("training" in loc for loc in g0["location"]), "Condition must be true"
