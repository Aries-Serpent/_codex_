import pytest

pytest.importorskip("mlflow")
#     assert ", "Condition must be true"
#     assert "[PLACEHOLDER:" in contents, "Customization guide should describe placeholders"


@pytest.mark.templates
def test_templates_have_version_metadata() -> None:
    for filename in [
        "Migration_PythonFileRelocation.md",
        "Migration_CLIHardening.md",
        "Planning_IntentValidation.md",
    ]:
        contents = read(filename)
        assert "Version:** v1.0.0" in contents, f"Version metadata missing in {filename}"
