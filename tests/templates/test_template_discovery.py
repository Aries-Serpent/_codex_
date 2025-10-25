from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = REPO_ROOT / "templates"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_template_directories_exist():
    expected_dirs = [
        TEMPLATES_DIR,
        TEMPLATES_DIR / "audit",
        TEMPLATES_DIR / "github_repo_baseline",
        TEMPLATES_DIR / "github_repo_baseline" / "ISSUE_TEMPLATE",
    ]

    for directory in expected_dirs:
        assert directory.exists() and directory.is_dir(), f"Missing template directory: {directory}"


def test_template_files_present():
    expected_files = {
        "audit/capability_matrix.md.j2",
        "audit/status_update_report.md.j2",
        "github_repo_baseline/CODEOWNERS",
        "github_repo_baseline/ISSUE_TEMPLATE/config.yml",
        "github_repo_baseline/ISSUE_TEMPLATE/feature_request.md",
        "github_repo_baseline/ISSUE_TEMPLATE/bug_report.md",
        "github_repo_baseline/PULL_REQUEST_TEMPLATE.md",
    }

    missing = [
        relative_path
        for relative_path in expected_files
        if not (TEMPLATES_DIR / relative_path).is_file()
    ]

    assert not missing, f"Missing template files: {missing}"


@pytest.mark.parametrize(
    "relative_path",
    [
        "audit/capability_matrix.md.j2",
        "audit/status_update_report.md.j2",
        "github_repo_baseline/CODEOWNERS",
        "github_repo_baseline/ISSUE_TEMPLATE/config.yml",
        "github_repo_baseline/ISSUE_TEMPLATE/feature_request.md",
        "github_repo_baseline/ISSUE_TEMPLATE/bug_report.md",
        "github_repo_baseline/PULL_REQUEST_TEMPLATE.md",
    ],
)
def test_templates_are_readable(relative_path: str):
    path = TEMPLATES_DIR / relative_path
    contents = read(path)

    assert contents.strip(), f"Template appears empty: {relative_path}"


def test_audit_templates_have_metadata_headers():
    audit_templates = {
        "capability_matrix.md.j2": "# [Report]: Capability Matrix",
        "status_update_report.md.j2": "# [Report]: Codex Status Update Audit",
    }

    for filename, expected_header in audit_templates.items():
        path = TEMPLATES_DIR / "audit" / filename
        first_line = read(path).splitlines()[0]
        assert first_line == expected_header, f"Unexpected header in {filename}: {first_line!r}"


def test_repository_templates_reference_documentation():
    codeowners = read(TEMPLATES_DIR / "github_repo_baseline" / "CODEOWNERS")
    pr_template = read(TEMPLATES_DIR / "github_repo_baseline" / "PULL_REQUEST_TEMPLATE.md")

    assert "/docs/" in codeowners, "CODEOWNERS should reference documentation ownership"
    assert (
        "Docs updated where helpful" in pr_template
    ), "PR template should remind about documentation updates"
