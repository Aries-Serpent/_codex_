"""
Test Pa Reader

Test module for pa reader.
"""

from codex_crm.pa_legacy.reader import to_template


def test_pa_template_shape() -> None:
    package = {"flows": {"f": {"definition": {"resources": {"conn": {"type": "api"}}}}}}
    template = to_template(package)
    assert "connections" in template, "Condition must be true"
    assert template["connections"], "Condition must be true"
    assert template["connections"][0]["placeholder"] == "${CONN_CONN}", "Condition must be true"
