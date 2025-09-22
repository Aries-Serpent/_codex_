"""Validate status update formatting against mandated template."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
STATUS_UPDATE = REPO_ROOT / "docs" / "status_updates" / "status_update_2025-09-22.md"


def read_status() -> str:
    return STATUS_UPDATE.read_text(encoding="utf-8")


def test_mandated_headers_present() -> None:
    text = read_status()
    required_phrases = [
        "Check for must recent active branch:",
        "//fetch https://github.com/Aries-Serpent/_codex_/activity?time_period=day",
        "Branches:",
        "//fetch https://github.com/Aries-Serpent/_codex_/tree/0A_base_",
        "Objective:",
        "Audit Scope",
        "# 📍_codex_: Status Update (2025-09-22)",
        "1. **Repo Map**",
        "2. **Capability Audit Table**",
        "3. **High-Signal Findings**",
        "4. **Atomic Diffs**",
        "5. **Local Tests & Gates**",
        "6. **Reproducibility Checklist**",
        "7. **Deferred Items**",
        "8. **Error Capture Blocks**",
        "## Codex-ready Task Sequence",
        "**Additional Deliverable — Executable Script**",
        "Question from ChatGPT @codex",
    ]
    for phrase in required_phrases:
        assert phrase in text, f"Missing mandated template phrase: {phrase!r}"


def test_atomic_diff_structure() -> None:
    text = read_status()
    # Every atomic diff must include Why/Risk/Rollback/Tests blocks.
    for diff_index in range(1, 4):
        marker = f"### Atomic Diff {diff_index}"
        assert marker in text, f"Expected atomic diff heading for index {diff_index}"
    for bullet in ("- **Why:", "- **Risk:", "- **Rollback:", "- **Tests/docs:"):
        assert bullet in text, f"Atomic diff section missing bullet {bullet}"


def test_task_sequence_is_yaml_block() -> None:
    text = read_status()
    assert "```yaml" in text, "Codex-ready task sequence must be fenced as YAML"
    assert "Codex-ready Task Sequence:" in text, "YAML block must declare Codex-ready Task Sequence"


def test_executable_script_block_present() -> None:
    text = read_status()
    assert "```python" in text, "Executable script must be provided in fenced python block"
    assert (
        "Offline Codex remediation workflow orchestrator" in text
    ), "Script docstring missing mandated description"
