"""Validate status update template remains placeholder-only."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
STATUS_UPDATE = REPO_ROOT / "docs" / "status_updates" / "status_update_2025-09-22.md"


def read_status() -> str:
    return STATUS_UPDATE.read_text(encoding="utf-8")


def test_mandated_structure_present() -> None:
    text = read_status()
    required_phrases = [
        "Check for must recent active branch:",
        "//fetch https://github.com/Aries-Serpent/_codex_/activity?time_period=day",
        "Branches:",
        "//fetch https://github.com/Aries-Serpent/_codex_/tree/0C_base_",
        "Objective:",
        "Audit Scope",
        "# 📍_codex_: Status Update ({{date}})",
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
        "**Supplied Task (expand on task as needed for Codex to action each until completion):**",
    ]
    for phrase in required_phrases:
        assert phrase in text, f"Missing mandated template phrase: {phrase!r}"


def test_capability_table_placeholders() -> None:
    text = read_status()
    placeholder_tokens = [
        "{{tokenization_status}}",
        "{{modeling_status}}",
        "{{training_status}}",
        "{{config_status}}",
        "{{evaluation_status}}",
        "{{logging_status}}",
        "{{checkpointing_status}}",
        "{{data_status}}",
        "{{security_status}}",
        "{{ci_status}}",
        "{{deployment_status}}",
        "{{docs_status}}",
        "{{tracking_status}}",
        "{{extensibility_status}}",
    ]
    for token in placeholder_tokens:
        assert token in text, f"Capability placeholder missing: {token}"


def test_atomic_diff_sections_placeholder_only() -> None:
    text = read_status()
    for diff_index in range(1, 4):
        assert f"### Atomic Diff {diff_index}" in text, "Expected atomic diff heading"
    placeholder_snippets = [
        "{{atomic_diff_1_title}}",
        "{{atomic_diff_2_title}}",
        "{{atomic_diff_3_title}}",
        "{{atomic_diff_1_patch}}",
        "{{atomic_diff_2_patch}}",
        "{{atomic_diff_3_patch}}",
    ]
    for snippet in placeholder_snippets:
        assert snippet in text, f"Atomic diff placeholder missing: {snippet}"
    assert "{{atomic_diff_1_why}}" in text
    assert "{{atomic_diff_1_risk}}" in text
    assert "{{atomic_diff_1_tests}}" in text


def test_task_sequence_and_script_templates() -> None:
    text = read_status()
    assert "```yaml" in text, "Codex-ready task sequence must be fenced as YAML"
    assert "{{task_sequence_preparation_step_1}}" in text
    assert "```python" in text, "Executable script must be provided in fenced python block"
    assert '"""Codex remediation workflow template."""' in text
    assert 'raise NotImplementedError("{{implement_context_loader}}")' in text
    assert "{{script_completion_message}}" in text


def test_supplied_tasks_placeholders_present() -> None:
    text = read_status()
    for token in (
        "{{codex_supplied_task_01}}",
        "{{codex_supplied_task_02}}",
        "{{codex_supplied_task_03}}",
    ):
        assert token in text, f"Supplied task placeholder missing: {token}"


def test_placeholder_tokens_used_in_high_signal_section() -> None:
    text = read_status()
    for idx in range(1, 11):
        token = f"{{{{high_signal_{idx:02d}}}}}"
        assert token in text, f"High-signal placeholder missing: {token}"


def test_reproducibility_table_placeholders() -> None:
    text = read_status()
    for token in (
        "{{repro_seeds_status}}",
        "{{repro_env_status}}",
        "{{repro_data_status}}",
        "{{repro_config_status}}",
        "{{repro_hardware_status}}",
        "{{repro_results_status}}",
    ):
        assert token in text, f"Reproducibility placeholder missing: {token}"


def test_error_capture_placeholder_present() -> None:
    text = read_status()
    assert "{{error_capture_summary}}" in text, "Error capture placeholder missing"
    assert (
        "{{task_sequence_error_capture_step_1}}" in text
    ), "Error capture phase placeholder missing"
    assert (
        "Question for ChatGPT @codex" not in text
    ), "Template should not contain filled error capture block"
