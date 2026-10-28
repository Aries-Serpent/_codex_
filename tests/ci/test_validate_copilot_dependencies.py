"""Regression coverage for the setup workflow's required environment contract."""

from pathlib import Path

from scripts.ci import validate_copilot_dependencies as validator


def test_checked_in_workflow_satisfies_required_environment_contract() -> None:
    workflow = (
        Path(__file__).resolve().parents[2] / ".github/workflows/copilot-setup-steps.yml"
    ).read_text(encoding="utf-8")

    result = validator.test_env_var_propagation(workflow, validator.EXPECTED_ENV_VARS)

    assert result.passed, result.message


def test_lfs_credentials_are_not_unconditionally_required() -> None:
    result = validator.test_env_var_propagation(
        'env:\n  GIT_LFS_SKIP_SMUDGE: "1"\n', validator.EXPECTED_ENV_VARS
    )

    assert result.passed, result.message


def test_lfs_smudge_guard_is_still_required() -> None:
    result = validator.test_env_var_propagation("env: {}\n", validator.EXPECTED_ENV_VARS)

    assert not result.passed
    assert "GIT_LFS_SKIP_SMUDGE" in result.message
