from __future__ import annotations

import fnmatch
import re
from pathlib import Path
from typing import Dict, Iterable, List

import pytest

pytestmark = [pytest.mark.security]


EXPECTED_SUPPRESSION_FILES: Dict[str, int] = {
    "fix_github_broken_links.py": 1,
    "fix_all_broken_links.py": 1,
    "fix_specific_links.py": 1,
    "fix_doc_links.py": 1,
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


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _load_yaml(path: Path) -> dict:
    yaml = pytest.importorskip("yaml")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _find_suppression_lines(content: str) -> List[int]:
    return [i for i, line in enumerate(content.splitlines()) if "nosemgrep: url-substring-check" in line]


def _find_nearby_url_line(lines: List[str], start_index: int, window: int = 20) -> str:
    for offset in range(1, window + 1):
        if start_index + offset < len(lines) and "http" in lines[start_index + offset]:
            return lines[start_index + offset]
    return ""


@pytest.mark.timeout(120)
def test_suppression_config_valid() -> None:
    """Validate suppression rules YAML is parseable and contains expected rules."""
    config_path = _repo_root() / ".semgrep" / "rules" / "suppress-utility-scripts.yaml"
    assert config_path.exists(), "Suppression configuration file is missing"

    config = _load_yaml(config_path)
    assert isinstance(config, dict), "Suppression configuration should be a YAML mapping"
    assert "rules" in config, "Suppression configuration must contain rules"
    assert len(config["rules"]) >= 2, "Expected at least two suppression rules"


@pytest.mark.timeout(120)
def test_inline_suppressions_present() -> None:
    """Verify all expected files have the required nosemgrep suppressions."""
    repo_root = _repo_root()

    for filepath, expected_count in EXPECTED_SUPPRESSION_FILES.items():
        path = repo_root / filepath
        assert path.exists(), f"File not found: {filepath}"

        content = path.read_text(encoding="utf-8")
        actual_count = len(re.findall(r"#\s+nosemgrep:\s+url-substring-check", content))
        assert actual_count >= expected_count, (
            f"{filepath}: Expected {expected_count} suppressions, found {actual_count}"
        )


@pytest.mark.timeout(120)
def test_suppression_comment_format() -> None:
    """Ensure suppression comments include the required rule and reason format."""
    repo_root = _repo_root()
    pattern = re.compile(r"#\s+nosemgrep:\s+url-substring-check\s+-\s+.+")

    for filepath in EXPECTED_SUPPRESSION_FILES:
        content = (repo_root / filepath).read_text(encoding="utf-8")
        for line in content.splitlines():
            if "nosemgrep: url-substring-check" in line:
                assert pattern.search(line), (
                    f"Suppression comment format invalid in {filepath}: {line}"
                )


@pytest.mark.timeout(120)
def test_no_actual_security_issues() -> None:
    """Run basic safety checks against code that includes suppressions."""
    repo_root = _repo_root()
    banned_patterns = [r"\beval\(", r"\bexec\(", r"subprocess\.Popen\(.*shell=True"]

    for filepath in EXPECTED_SUPPRESSION_FILES:
        content = (repo_root / filepath).read_text(encoding="utf-8")
        for pattern in banned_patterns:
            assert not re.search(pattern, content), (
                f"Potential unsafe pattern '{pattern}' found in {filepath}"
            )


@pytest.mark.timeout(120)
def test_suppression_metadata_complete() -> None:
    """Verify suppression rule metadata includes expected fields."""
    config_path = _repo_root() / ".semgrep" / "rules" / "suppress-utility-scripts.yaml"
    config = _load_yaml(config_path)

    metadata = config["rules"][0].get("metadata", {})
    assert metadata.get("category"), "Suppression metadata missing category"
    assert metadata.get("cwe"), "Suppression metadata missing CWE"
    assert metadata.get("verified_by"), "Suppression metadata missing verification owner"


@pytest.mark.timeout(120)
def test_utility_scripts_covered() -> None:
    """Ensure suppression config covers utility scripts and fix_*.py patterns."""
    config_path = _repo_root() / ".semgrep" / "rules" / "suppress-utility-scripts.yaml"
    config = _load_yaml(config_path)

    include_paths = config["rules"][0]["paths"]["include"]
    assert "fix_*.py" in include_paths, "Suppression rules should include fix_*.py"
    assert "scripts/**/*.py" in include_paths, "Suppression rules should include scripts/**/*.py"


@pytest.mark.timeout(120)
def test_no_over_suppression() -> None:
    """Confirm suppressions are only applied to intended files."""
    repo_root = _repo_root()
    allowed_paths = set(EXPECTED_SUPPRESSION_FILES.keys())

    for path in repo_root.rglob("*.py"):
        content = path.read_text(encoding="utf-8")
        if re.search(r"#\s+nosemgrep:\s+url-substring-check", content):
            relative_path = path.relative_to(repo_root).as_posix()
            assert relative_path in allowed_paths, (
                f"Unexpected suppression in {relative_path}"
            )


@pytest.mark.timeout(120)
def test_suppression_comment_targets_url_literals() -> None:
    """Check suppression comments apply to URL literal checks nearby."""
    repo_root = _repo_root()

    for filepath in EXPECTED_SUPPRESSION_FILES:
        lines = (repo_root / filepath).read_text(encoding="utf-8").splitlines()
        for index in _find_suppression_lines("\n".join(lines)):
            url_line = _find_nearby_url_line(lines, index)
            assert url_line, f"No URL literal found near suppression in {filepath}"
            assert "http" in url_line, f"Expected URL literal near suppression in {filepath}"
