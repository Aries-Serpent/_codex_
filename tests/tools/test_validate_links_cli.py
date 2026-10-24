"""Regression tests for changed-file and full-scan link validation modes."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = REPO_ROOT / ".github" / "scripts" / "validate-links.py"
PRE_COMMIT_CONFIGS = (
    REPO_ROOT / ".pre-commit-config.yaml",
    REPO_ROOT / ".config" / ".pre-commit-config.yaml",
)


@pytest.fixture
def isolated_repo(tmp_path: Path) -> Path:
    """Copy the CLI so its normal root discovery points at a small fixture repo."""
    script = tmp_path / ".github" / "scripts" / "validate-links.py"
    script.parent.mkdir(parents=True)
    shutil.copy2(VALIDATOR, script)
    for directory in (
        ".github/workflows",
        ".github/docs",
        ".github/agents",
        "docs",
    ):
        (tmp_path / directory).mkdir(parents=True, exist_ok=True)
    return tmp_path


def run_validator(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    script = repo / ".github" / "scripts" / "validate-links.py"
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )


def test_changed_file_mode_ignores_unrelated_repo_link_debt(
    isolated_repo: Path,
) -> None:
    changed_file = isolated_repo / "docs" / "changed.md"
    changed_file.write_text("[Existing target](target.md)\n", encoding="utf-8")
    (isolated_repo / "docs" / "target.md").write_text("target\n", encoding="utf-8")

    # Model the existing repository-wide debt without letting it affect this PR's
    # changed-file gate.
    for index in range(303):
        (isolated_repo / "docs" / f"legacy-{index}.md").write_text(
            f"[Missing](missing-{index}.md)\n",
            encoding="utf-8",
        )

    result = run_validator(
        isolated_repo,
        "--fail-on-errors",
        "docs/changed.md",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Files checked: 1" in result.stdout
    assert "Errors: 0" in result.stdout


def test_changed_file_mode_fails_for_a_broken_link(isolated_repo: Path) -> None:
    changed_file = isolated_repo / "docs" / "changed.md"
    changed_file.write_text("[Missing](missing.md)\n", encoding="utf-8")

    result = run_validator(
        isolated_repo,
        "--fail-on-errors",
        "docs/changed.md",
    )

    assert result.returncode == 1
    assert "Errors: 1" in result.stdout
    assert "File not found: missing.md" in result.stdout


def test_no_file_arguments_preserves_full_repository_scan(isolated_repo: Path) -> None:
    (isolated_repo / "docs" / "legacy.md").write_text(
        "[Missing](missing.md)\n",
        encoding="utf-8",
    )

    result = run_validator(isolated_repo, "--fail-on-errors")

    assert result.returncode == 1
    assert "Files checked: 1" in result.stdout
    assert "Errors: 1" in result.stdout


@pytest.mark.parametrize("config_path", PRE_COMMIT_CONFIGS)
def test_pre_commit_hook_passes_changed_filenames(config_path: Path) -> None:
    config = config_path.read_text(encoding="utf-8")
    hook = config.split("- id: validate-internal-links", maxsplit=1)[1].split(
        "\n      - id:", maxsplit=1
    )[0]

    assert "pass_filenames: true" in hook
    assert "entry: python .github/scripts/validate-links.py --fail-on-errors" in hook
