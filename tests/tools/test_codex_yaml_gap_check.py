"""
Test Codex Yaml Gap Check

Test module for codex yaml gap check.
"""

import textwrap
from pathlib import Path

import tools.codex_yaml_gap_check as cygc


def test_yaml_gap_check_reports_unmapped_gap(tmp_path: Path):
    registry_path = tmp_path / "codex_gap_registry.yaml"
    registry_path.write_text(
        textwrap.dedent("""
            gaps:
              - id: tokenization.fast_backend
                yaml_phase_step: "2.4"
              - id: training.grad_accumulation
            """),
        encoding="utf-8",
    )

    sequence_path = tmp_path / "codex_task_sequence.yaml"
    sequence_path.write_text(
        textwrap.dedent("""
            codex_task_sequence:
              phases:
                - id: 2
                  name: Search & Mapping
                  steps:
                    - id: "2.4"
                      description: Dummy
                      actions: []
            """),
        encoding="utf-8",
    )

    report_path = tmp_path / "codex_yaml_gap_report.md"

    cygc.main(
        [
            "--gaps",
            str(registry_path),
            "--yaml",
            str(sequence_path),
            "--out",
            str(report_path),
        ]
    )

    text = report_path.read_text(encoding="utf-8")
    assert "training.grad_accumulation" in text, "Condition must be true"
