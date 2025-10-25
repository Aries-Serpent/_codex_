from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = REPO_ROOT / "templates"


def read_lines(relative_path: str) -> list[str]:
    path = TEMPLATES_DIR / relative_path
    return path.read_text(encoding="utf-8").splitlines()


audit_template_sections = {
    "audit/capability_matrix.md.j2": [
        "## 1. Summary",
        "## 2. Capability Scores",
        "## 3. Low Maturity Focus",
        "## 4. Weight Reference",
        "## 5. Capability Detail Sections",
        "## 6. Appendix",
    ],
    "audit/status_update_report.md.j2": [
        "## 1) Executive Summary",
        "## 2) Low Maturity Focus",
        "## 3) Movement Since Baseline (if provided)",
        "## 4) Weights (Effective)",
        "## 5) Integrity Chain (Manifest)",
        "## 6) Next Actions",
    ],
}


audit_template_placeholders = {
    "audit/capability_matrix.md.j2": [
        "{{ timestamp }}",
        "{{ capabilities|length }}",
        "{{ gaps|length }}",
        "{% for cap in capabilities -%}",
        "{{ cap.id }}",
        "{{ cap.components.functionality }}",
        "cap.meta",
        '{{ template_hash|default("UNKNOWN") }}',
    ],
    "audit/status_update_report.md.j2": [
        "{{ timestamp }}",
        "{{ version }}",
        "{{ summary.total_capabilities }}",
        "{{ low_maturity|length }}",
        "{% for w in warnings -%}",
        "{% for c in low_maturity -%}",
        "deltas.improvements",
        "deltas.regressions",
        "weights.items()",
        '{{ integrity.repo_root_sha if integrity.repo_root_sha else "N/A" }}',
        '{{ integrity.template_hash if integrity.template_hash else "N/A" }}',
    ],
}


def test_audit_templates_have_required_sections():
    for relative_path, sections in audit_template_sections.items():
        lines = "\n".join(read_lines(relative_path))
        for section in sections:
            assert section in lines, f"Section '{section}' missing from {relative_path}"


def test_audit_templates_include_required_placeholders():
    for relative_path, placeholders in audit_template_placeholders.items():
        content = "\n".join(read_lines(relative_path))
        for placeholder in placeholders:
            assert (
                placeholder in content
            ), f"Placeholder '{placeholder}' missing from {relative_path}"


@pytest.mark.parametrize(
    "relative_path, required_snippets",
    [
        (
            "github_repo_baseline/ISSUE_TEMPLATE/feature_request.md",
            [
                "---",
                "name: Feature request",
                "about: Suggest an idea for this project",
                "labels: type:feature",
                "**Problem**",
                "**Proposed solution**",
                "**Alternatives considered**",
            ],
        ),
        (
            "github_repo_baseline/ISSUE_TEMPLATE/bug_report.md",
            [
                "---",
                "name: Bug report",
                "about: Help us fix something that isn't working",
                "labels: type:bug",
                "**Describe the bug**",
                "**Steps to reproduce**",
                "**Expected behavior**",
                "**Additional context**",
            ],
        ),
        (
            "github_repo_baseline/PULL_REQUEST_TEMPLATE.md",
            [
                "## Summary",
                "<!-- What does this change and why? -->",
                "## Checklist",
                "- [ ] Small, focused commit(s) with clear message(s)",
                "- [ ] Docs updated where helpful",
                "- [ ] Pre-commit hooks passed locally",
                "## Risk / Rollout",
                "- [ ] Low risk",
                "- [ ] Includes plan to revert if needed",
            ],
        ),
        (
            "github_repo_baseline/CODEOWNERS",
            [
                "* @Aries-Serpent/codex-admins",
                "/src/ @Aries-Serpent/codex-admins",
                "/tests/ @Aries-Serpent/codex-admins",
                "/docs/ @Aries-Serpent/codex-admins",
            ],
        ),
        (
            "github_repo_baseline/ISSUE_TEMPLATE/config.yml",
            [
                "blank_issues_enabled: false",
            ],
        ),
    ],
)
def test_repository_templates_have_required_structure(
    relative_path: str, required_snippets: list[str]
):
    content = "\n".join(read_lines(relative_path))
    for snippet in required_snippets:
        assert snippet in content, f"Snippet '{snippet}' missing from {relative_path}"


@pytest.mark.parametrize(
    "relative_path, expected_metadata",
    [
        ("audit/capability_matrix.md.j2", "> Generated: {{ timestamp }}"),
        ("audit/status_update_report.md.j2", "> Generated: {{ timestamp }} | Spec: v{{ version }}"),
    ],
)
def test_audit_templates_start_with_metadata(relative_path: str, expected_metadata: str):
    lines = read_lines(relative_path)
    assert lines[1].startswith(
        expected_metadata
    ), f"Metadata line does not start as expected in {relative_path}"
