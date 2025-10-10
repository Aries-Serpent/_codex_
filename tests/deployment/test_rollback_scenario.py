import subprocess


def test_orchestrate_dry_run_outputs_command() -> None:
    result = subprocess.run(
        ["scripts/deploy/orchestrate.sh", "run", "--dry-run"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "[dry-run]" in result.stdout
