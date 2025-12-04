import textwrap
from pathlib import Path

import tools.codex_gap_registry as cgr


def test_build_registry_from_minimal_audit(tmp_path: Path):
    audit = tmp_path / "audit.md"
    audit.write_text(
        textwrap.dedent(
            """
            # _codex_: Status Update (2025-11-27)

            ## High-Signal Findings

            - Fast tokenizer backend missing, parity tests absent
            - Training loop does not expose gradient accumulation settings
            """
        ),
        encoding="utf-8",
    )

    change_log = tmp_path / "codex_change_log.md"
    change_log.write_text("", encoding="utf-8")
    errors = tmp_path / "codex_error_questions.md"
    errors.write_text("", encoding="utf-8")

    registry = cgr.build_registry(
        audit=audit,
        change_log=change_log,
        errors=errors,
        hardship=None,
    )

    assert "gaps" in registry
    gaps = registry["gaps"]
    assert isinstance(gaps, list)
    assert len(gaps) >= 2

    first = gaps[0]
    assert "id" in first
    assert "capability" in first
    assert first["status"] in {"missing", "partial", "stubbed", "implemented"}


def test_build_registry_handles_missing_inputs():
    registry = cgr.build_registry(
        audit=None,
        change_log=None,
        errors=None,
        hardship=None,
    )
    assert "gaps" in registry
    assert isinstance(registry["gaps"], list)
