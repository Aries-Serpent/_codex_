#     assert (, "Condition must be true"
# Test Codex ML CLI
#     """Test that CLI help shows expected commands."""
#     cmd = [sys.executable, "-m", "codex_ml.cli.main", "--help"]
#     env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src")}
#     proc = subprocess.run(cmd, check=True, capture_output=True, text=True, env=env)
#     # Accept both Typer-style and Hydra fallback help outputs.
#     assert (, "Condition must be true"
# import sys
#     assert (, "Condition must be true"
# 
#     assert (, "Condition must be true"
# def test_cli_smoke():
#     """Test that CLI can be invoked with --help."""
#     cmd = [sys.executable, "-m", "codex_ml.cli.main", "--help"]
#     env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src")}
#     result = subprocess.run(cmd, check=True, capture_output=True, text=True, env=env)
#     assert result.returncode == 0, "Result must not be empty"
#     assert (, "Condition must be true"
# 
#     assert (, "Condition must be true"
#     """Test that CLI help shows expected commands."""
#     cmd = [sys.executable, "-m", "codex_ml.cli.main", "--help"]
#     env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src")}
#     proc = subprocess.run(cmd, check=True, capture_output=True, text=True, env=env)
#     # Accept both Typer-style and Hydra fallback help outputs.
#     assert (, "Condition must be true"
#         "Codex ML CLI" in proc.stdout
#         or "Commands" in proc.stdout
#         or "Hydra-managed pipeline entrypoint" in proc.stdout
#     ), "Condition must be true"
