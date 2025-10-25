"""Structural checks for repository templates."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_ROOT = REPO_ROOT / "templates"
AUDIT_DIR = TEMPLATES_ROOT / "audit"
GITHUB_DIR = TEMPLATES_ROOT / "github_repo_baseline"
GITHUB_ISSUE_DIR = GITHUB_DIR / "ISSUE_TEMPLATE"

CAPABILITY_MATRIX = (AUDIT_DIR / "capability_matrix.md.j2").read_text(encoding="utf-8")
STATUS_UPDATE_REPORT = (AUDIT_DIR / "status_update_report.md.j2").read_text(encoding="utf-8")
PULL_REQUEST_TEMPLATE = (GITHUB_DIR / "PULL_REQUEST_TEMPLATE.md").read_text(encoding="utf-8")
CODEOWNERS = (GITHUB_DIR / "CODEOWNERS").read_text(encoding="utf-8")
BUG_TEMPLATE = (GITHUB_ISSUE_DIR / "bug_report.md").read_text(encoding="utf-8")
FEATURE_TEMPLATE = (GITHUB_ISSUE_DIR / "feature_request.md").read_text(encoding="utf-8")
ISSUE_CONFIG = (GITHUB_ISSUE_DIR / "config.yml").read_text(encoding="utf-8")


def test_capability_matrix_sections_and_placeholders() -> None:
    """Ensure the capability matrix template retains all mandated structure."""

    required_sections = [
        "## 1. Summary",
        "## 2. Capability Scores",
        "## 3. Low Maturity Focus",
        "## 4. Weight Reference",
        "## 5. Capability Detail Sections",
        "## 6. Appendix",
    ]
    for section in required_sections:
        assert section in CAPABILITY_MATRIX, f"Capability matrix missing section {section!r}"

    placeholders = [
        "{{ timestamp }}",
        "{{ capabilities|length }}",
        "{{ gaps|length }}",
        "{{ cap.id }}",
        "{{ cap.components.functionality }}",
        "cap.meta",
        '{{ template_hash|default("UNKNOWN") }}',
    ]
    for placeholder in placeholders:
        assert (
            placeholder in CAPABILITY_MATRIX
        ), f"Capability matrix missing placeholder {placeholder}"


def test_status_update_report_structure_and_metadata() -> None:
    """Validate the status update audit template includes required metadata."""

    required_sections = [
        "## 1) Executive Summary",
        "## 2) Low Maturity Focus (Top {{ low_maturity|length }})",
        "## 3) Movement Since Baseline (if provided)",
        "## 4) Weights (Effective)",
        "## 5) Integrity Chain (Manifest)",
        "## 6) Next Actions",
    ]
    for section in required_sections:
        assert section in STATUS_UPDATE_REPORT, f"Status update report missing section {section!r}"

    placeholders = [
        "{{ timestamp }}",
        "{{ version }}",
        "{{ summary.total_capabilities }}",
        '{{ "%.3f"|format(summary.average_score) }}',
        "{{ summary.low_count }}",
        "{{ low_maturity|length }}",
        "deltas.improvements",
        "deltas.regressions",
        "weights.items()",
        '{{ integrity.repo_root_sha if integrity.repo_root_sha else "N/A" }}',
        '{{ integrity.template_hash if integrity.template_hash else "N/A" }}',
    ]
    for placeholder in placeholders:
        assert (
            placeholder in STATUS_UPDATE_REPORT
        ), f"Status update report missing placeholder {placeholder}"

    assert "Spec: v{{ version }}" in STATUS_UPDATE_REPORT, "Status update version metadata missing"


def test_github_issue_templates_structure() -> None:
    """Issue templates should preserve front-matter and navigation prompts."""

    bug_expected = [
        "name: Bug report",
        "about: Help us fix something that isn't working",
        "labels: type:bug",
        "**Describe the bug**",
        "**Steps to reproduce**",
        "**Expected behavior**",
        "**Additional context**",
    ]
    for phrase in bug_expected:
        assert phrase in BUG_TEMPLATE, f"Bug issue template missing {phrase!r}"

    feature_expected = [
        "name: Feature request",
        "about: Suggest an idea for this project",
        "labels: type:feature",
        "**Problem**",
        "**Proposed solution**",
        "**Alternatives considered**",
    ]
    for phrase in feature_expected:
        assert phrase in FEATURE_TEMPLATE, f"Feature issue template missing {phrase!r}"

    assert (
        "blank_issues_enabled: false" in ISSUE_CONFIG
    ), "Issue template config missing blank issue guard"


def test_pull_request_template_structure() -> None:
    """PR template must keep reviewer guidance and risk assessment sections."""

    sections = ["## Summary", "## Checklist", "## Risk / Rollout"]
    for section in sections:
        assert section in PULL_REQUEST_TEMPLATE, f"PR template missing section {section!r}"

    checkboxes = [
        "- [ ] Small, focused commit(s) with clear message(s)",
        "- [ ] Docs updated where helpful",
        "- [ ] Pre-commit hooks passed locally",
        "- [ ] Low risk",
        "- [ ] Includes plan to revert if needed",
    ]
    for checkbox in checkboxes:
        assert checkbox in PULL_REQUEST_TEMPLATE, f"PR template missing checkbox {checkbox!r}"


def test_codeowners_entries_cover_core_paths() -> None:
    """CODEOWNERS template should enumerate the core ownership rules."""

    expected_paths = [
        "* @Aries-Serpent/codex-admins",
        "/src/ @Aries-Serpent/codex-admins",
        "/tests/ @Aries-Serpent/codex-admins",
        "/docs/ @Aries-Serpent/codex-admins",
    ]
    for entry in expected_paths:
        assert entry in CODEOWNERS, f"CODEOWNERS missing entry {entry!r}"
