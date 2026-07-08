from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_master_guide_uses_snapshot_language() -> None:
    guide = (REPO_ROOT / "docs" / "admin" / "GITHUB_VARIABLES_MASTER_GUIDE.md").read_text(
        encoding="utf-8"
    )

    assert "validated snapshot as of" in guide, "Condition must be true"
    assert "reflects live state as of" not in guide, "Condition must be true"
    assert "Python version target (minor pinned, patch floating)" in guide
    assert "pins the minor version while allowing patch updates; runtime resolves" in guide, "Condition must be true"
    assert "historical records only" not in guide, "Condition must be true"


def test_secondary_variable_docs_match_python_version_wording() -> None:
    secrets_guide = (REPO_ROOT / "docs" / "SECRETS_AND_ENVIRONMENT_VARIABLES.md").read_text(
        encoding="utf-8"
    )
    token_review = (
        REPO_ROOT / "docs" / "reference" / "ELEVATED_PRIVILEGES_TOKEN_REVIEW.md"
    ).read_text(encoding="utf-8")

    expected = "minor pinned, patch floating"
    assert expected in secrets_guide, "Condition must be true"
    assert expected in token_review, "Condition must be true"
