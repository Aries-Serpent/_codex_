"""Discovery checks for repository templates."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_ROOT = REPO_ROOT / "templates"
AUDIT_DIR = TEMPLATES_ROOT / "audit"
GITHUB_DIR = TEMPLATES_ROOT / "github_repo_baseline"
GITHUB_ISSUE_DIR = GITHUB_DIR / "ISSUE_TEMPLATE"

TEMPLATE_FILES = {
    "audit_capability": AUDIT_DIR / "capability_matrix.md.j2",
    "audit_status_update": AUDIT_DIR / "status_update_report.md.j2",
    "codeowners": GITHUB_DIR / "CODEOWNERS",
    "pr_template": GITHUB_DIR / "PULL_REQUEST_TEMPLATE.md",
    "issue_bug": GITHUB_ISSUE_DIR / "bug_report.md",
    "issue_feature": GITHUB_ISSUE_DIR / "feature_request.md",
    "issue_config": GITHUB_ISSUE_DIR / "config.yml",
}


@pytest.mark.parametrize(
    "path",
    [
        TEMPLATES_ROOT,
        AUDIT_DIR,
        GITHUB_DIR,
        GITHUB_ISSUE_DIR,
    ],
)
def test_template_directories_exist(path: Path) -> None:
    """Expected template directories must exist in the repository."""

    assert path.is_dir(), f"Missing template directory: {path}"  # pragma: no cover


@pytest.mark.parametrize("path", list(TEMPLATE_FILES.values()))
def test_template_files_are_readable(path: Path) -> None:
    """Templates should be present and readable as UTF-8 text."""

    assert path.is_file(), f"Template missing: {path}"  # pragma: no cover
    text = path.read_text(encoding="utf-8")
    assert text.strip(), f"Template appears empty: {path}"  # pragma: no cover


def test_audit_templates_have_metadata_headers() -> None:
    """Audit report templates must include metadata headers."""

    for key in ("audit_capability", "audit_status_update"):
        text = TEMPLATE_FILES[key].read_text(encoding="utf-8")
        lines = text.splitlines()
        assert lines[0].startswith("# [Report]: "), "Missing report heading"
        assert any("> Generated:" in line for line in lines[:3]), "Missing generated metadata"
        assert any("Roles:" in line for line in lines[:4]), "Missing roles metadata"


def test_issue_templates_have_front_matter() -> None:
    """GitHub issue templates require YAML front matter for metadata."""

    for key in ("issue_bug", "issue_feature"):
        text = TEMPLATE_FILES[key].read_text(encoding="utf-8")
        lines = text.splitlines()
        assert lines[0] == "---", "Expected YAML front matter fence"
        assert any(line.startswith("name:") for line in lines[1:5]), "Missing name metadata"
        assert any(line.startswith("about:") for line in lines[1:5]), "Missing about metadata"


def test_navigation_references_present() -> None:
    """Templates should provide consistent navigation cues for consumers."""

    expected_sections = {
        "audit_capability": [
            "## 1. Summary",
            "## 2. Capability Scores",
            "## 3. Low Maturity Focus",
            "## 4. Weight Reference",
            "## 5. Capability Detail Sections",
            "## 6. Appendix",
        ],
        "audit_status_update": [
            "## 1) Executive Summary",
            "## 2) Low Maturity Focus (Top {{ low_maturity|length }})",
            "## 3) Movement Since Baseline (if provided)",
            "## 4) Weights (Effective)",
            "## 5) Integrity Chain (Manifest)",
            "## 6) Next Actions",
        ],
        "pr_template": [
            "## Summary",
            "## Checklist",
            "## Risk / Rollout",
        ],
        "issue_bug": [
            "**Describe the bug**",
            "**Steps to reproduce**",
            "**Expected behavior**",
            "**Additional context**",
        ],
        "issue_feature": [
            "**Problem**",
            "**Proposed solution**",
            "**Alternatives considered**",
        ],
    }

    for key, sections in expected_sections.items():
        text = TEMPLATE_FILES[key].read_text(encoding="utf-8")
        for section in sections:
            assert (
                section in text
            ), f"Missing navigation reference {section!r} in {TEMPLATE_FILES[key]}"
