"""Validate semgrep suppression policies for utility scripts.

Ensures URL suppression comments remain scoped and correctly formatted.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

pytestmark = [pytest.mark.security]


EXPECTED_SUPPRESSION_FILES: dict[str, int] = {
    "scripts/maintenance/fix_github_broken_links.py": 1,
    "scripts/maintenance/fix_all_broken_links.py": 1,
    "scripts/maintenance/fix_specific_links.py": 1,
    "scripts/maintenance/fix_doc_links.py": 1,
    "scripts/mfa_enrollment_automation.py": 1,
    "scripts/phase10/automated_secrets_manager.py": 1,
    "scripts/security/close_codeql_alert.py": 1,
    "scripts/security/verify_token_scope.py": 1,
    "scripts/security/export_semgrep_alerts.py": 1,
    "scripts/security/fetch_codeql_alerts.py": 1,
    "scripts/validate_workflows.py": 1,
    "scripts/ops/codex_mint_tokens_per_run.py": 1,
    "scripts/ops/codex_repo_admin_bootstrap.py": 1,
    "scripts/ops/bootstrap_self_hosted_runner.py": 1,
    "scripts/monitor_workflow_performance.py": 1,
    "scripts/ci/batch_triage.py": 1,
    "scripts/github_user_provision.py": 1,
}

URL_LITERAL_REGEX = re.compile(r"\bhttps?://", re.IGNORECASE)


@pytest.fixture()
def repo_root() -> Path:
    """Return the repository root for semgrep suppression inspection."""

    return Path(__file__).resolve().parents[1]


@pytest.fixture()
def suppression_config(repo_root: Path) -> dict:
    """Load the semgrep suppression configuration YAML."""
    yaml = pytest.importorskip("yaml")
    config_path = repo_root / ".semgrep" / "rules" / "suppress-utility-scripts.yaml"
    return yaml.safe_load(config_path.read_text(encoding="utf-8"))


def _find_suppression_lines(content: str) -> list[int]:
    return [
        i for i, line in enumerate(content.splitlines()) if "nosemgrep: url-substring-check" in line
    ]


def _find_nearby_url_line(lines: list[str], start_index: int, window: int = 20) -> str:
    for offset in range(1, window + 1):
        if start_index + offset < len(lines) and URL_LITERAL_REGEX.search(
            lines[start_index + offset]
        ):
            return lines[start_index + offset]
    return ""


@pytest.mark.timeout(120)
def test_suppression_config_valid(suppression_config: dict) -> None:
    """Validate suppression rules YAML is parseable and contains expected rules."""
    assert isinstance(suppression_config, dict), "Suppression configuration should be a YAML mapping"
    assert "rules" in suppression_config, "Suppression configuration must contain rules"
    assert len(suppression_config["rules"]) >= 2, "Expected at least two suppression rules"


@pytest.mark.timeout(120)
@pytest.mark.parametrize("filepath,expected_count", EXPECTED_SUPPRESSION_FILES.items())
def test_inline_suppressions_present(
    repo_root: Path, filepath: str, expected_count: int
) -> None:
    """Verify all expected files have the required nosemgrep suppressions."""
    path = repo_root / filepath
    assert path.exists(), f"File not found: {filepath}"

    content = path.read_text(encoding="utf-8")
    actual_count = len(re.findall(r"#\s+nosemgrep:\s+url-substring-check", content))
    assert actual_count >= expected_count, (
        f"{filepath}: Expected {expected_count} suppressions, found {actual_count}"
    )


@pytest.mark.timeout(120)
@pytest.mark.parametrize("filepath", list(EXPECTED_SUPPRESSION_FILES.keys()))
def test_suppression_comment_format(repo_root: Path, filepath: str) -> None:
    """Ensure suppression comments include the required rule and reason format."""
    pattern = re.compile(r"#\s+nosemgrep:\s+url-substring-check\s+-\s+.+")
    content = (repo_root / filepath).read_text(encoding="utf-8")
    for line in content.splitlines():
        if "nosemgrep: url-substring-check" in line:
            assert pattern.search(line), (
                f"Suppression comment format invalid in {filepath}: {line}"
            )


@pytest.mark.timeout(120)
def test_suppression_metadata_complete(suppression_config: dict) -> None:
    """Verify suppression rule metadata includes expected fields."""
    metadata = suppression_config["rules"][0].get("metadata", {})
    assert metadata.get("category"), "Suppression metadata missing category"
    assert metadata.get("cwe"), "Suppression metadata missing CWE"
    assert metadata.get("verified_by"), "Suppression metadata missing verification owner"


@pytest.mark.timeout(120)
def test_utility_scripts_covered(suppression_config: dict) -> None:
    """Ensure suppression config covers utility scripts and fix_*.py patterns."""
    include_paths = suppression_config["rules"][0]["paths"]["include"]
    assert "fix_*.py" in include_paths, "Suppression rules should include fix_*.py"
    assert "scripts/**/*.py" in include_paths, "Suppression rules should include scripts/**/*.py"


@pytest.mark.timeout(120)
def test_no_over_suppression(repo_root: Path) -> None:
    """Confirm suppressions are only applied to intended files."""
    allowed_paths = set(EXPECTED_SUPPRESSION_FILES.keys())

    _SKIP_DIRS = {".venv_ci", ".venv", "venv", "node_modules", ".git", "__pycache__", "target", ".tox"}
    for path in repo_root.rglob("*.py"):
        if any(part in _SKIP_DIRS for part in path.parts):
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if re.search(r"#\s+nosemgrep:\s+url-substring-check", content):
            relative_path = path.relative_to(repo_root).as_posix()
            assert relative_path in allowed_paths, (
                f"Unexpected suppression in {relative_path}"
            )


@pytest.mark.timeout(120)
@pytest.mark.parametrize("filepath", list(EXPECTED_SUPPRESSION_FILES.keys()))
def test_suppression_comment_targets_url_literals(repo_root: Path, filepath: str) -> None:
    """Check suppression comments apply to URL literal checks nearby."""
    lines = (repo_root / filepath).read_text(encoding="utf-8").splitlines()
    for index in _find_suppression_lines("\n".join(lines)):
        url_line = _find_nearby_url_line(lines, index)
        assert url_line, f"No URL literal found near suppression in {filepath}"
        assert URL_LITERAL_REGEX.search(url_line), (
            f"Expected URL literal near suppression in {filepath}"
        )
