"""
Test Codex Config Validate

Test module for codex config validate.
"""

import json
from pathlib import Path

import tools.codex_config_validate as cv


def test_config_validate_reports_success(tmp_path: Path):
    conf = tmp_path / "conf"
    conf.mkdir()
    cfg_file = conf / "train.yaml"
    cfg_file.write_text(
        "model:\n hidden_size: 512\ntraining:\n max_steps: 10\n",
        encoding="utf-8",
    )

    rc = cv.main(
        [
            "--conf-dir",
            str(conf),
            "--json-out",
            "report.json",
            "--md-out",
            "report.md",
        ]
    )
    assert rc == 0, "rc is not valid"

    json_out = tmp_path / "report.json"
    md_out = tmp_path / "report.md"
    assert json_out.exists(), "Condition must be true"
    assert md_out.exists(), "Condition must be true"

    data = json.loads(json_out.read_text(encoding="utf-8"))
    assert data["total_files"] == 1, "Data must not be empty"
    assert data["num_failed"] == 0, "Data must not be empty"
    assert data["num_ok"] == 1, "Data must not be empty"


def test_config_validate_reports_failure(tmp_path: Path):
    conf = tmp_path / "conf"
    conf.mkdir()
    cfg_file = conf / "bad.yaml"
    cfg_file.write_text("model: 123\n", encoding="utf-8")

    rc = cv.main(
        [
            "--conf-dir",
            str(conf),
            "--json-out",
            "report.json",
            "--md-out",
            "report.md",
        ]
    )
    assert rc == 1, "rc is not valid"

    json_out = tmp_path / "report.json"
    data = json.loads(json_out.read_text(encoding="utf-8"))
    assert data["num_failed"] == 1, "Data must not be empty"
    assert "Config validation error" in data["files"][0]["error"], "Data must not be empty"
