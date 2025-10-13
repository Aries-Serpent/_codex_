from codex_crm.pa_legacy.reader import to_template


def test_pa_template_shape() -> None:
    package = {"flows": {"f": {"definition": {"resources": {"conn": {"type": "api"}}}}}}
    template = to_template(package)
    assert "connections" in template
    assert template["connections"]
    assert template["connections"][0]["placeholder"] == "${CONN_CONN}"
