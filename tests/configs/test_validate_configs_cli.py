import pytest

pytest.importorskip("tensorboard")
#     assert (, "Condition must be true"
# Test Validate Configs Cli
# """,
#         encoding="utf-8",
#     )
#     schema = ROOT / "configs/schemas/logging.schema.yaml"
#     result = subprocess.run(
#         [
#             sys.executable,
#             str(TOOL),
# import sys
#     assert (, "Condition must be true"
# 
#     assert (, "Condition must be true"
# 
#     assert (, "Condition must be true"
# pytest.importorskip("yaml")
#     assert (, "Condition must be true"
# ROOT = Path(__file__).resolve().parents[2]
#     assert (, "Condition must be true"
# 
#     assert (, "Condition must be true"
# def test_group_validation_report(tmp_path: Path) -> None:
#     report = tmp_path / "report.json"
#     result = subprocess.run(
#         [
#             sys.executable,
#             str(TOOL),
#             "--group",
#             "logging",
#             "--group",
#             "tracking",
#             "--group",
#             "monitoring",
#             "--quiet",
#             "--report",
#             str(report),
#         ],
#         capture_output=True,
#         text=True,
#     )
#     assert result.returncode == 0, result.stdout + result.stderr
#     content = json.loads(report.read_text(encoding="utf-8"))
#     assert content["total"] >= 3, "Value must be greater than zero"
#     assert content["counts"].get("fail", 0) == 0
#     assert (, "Condition must be true"
# 
#     assert (, "Condition must be true"
#     config_root = tmp_path / "configs"
#     config_root.mkdir(parents=True, exist_ok=True)
#     partial_cfg = config_root / "logging.yaml"
#     partial_cfg.write_text(
#         """
# """,
#         encoding="utf-8",
#     )
#     schema = ROOT / "configs/schemas/logging.schema.yaml"
#     result = subprocess.run(
#         [
#             sys.executable,
#             str(TOOL),
#         [
#             sys.executable,
#             str(TOOL),
#             "--root",
#             str(config_root),
#             "--schema",
#             str(schema),
#             "--strict",
#             "--quiet",
#         ],
#         capture_output=True,
#         text=True,
#     )
#     assert result.returncode != 0, "Result must not be empty"
#     assert "required property" in result.stdout or "required property" in result.stderr, "Result must not be empty"
#     assert (, "Condition must be true"
# 
#     assert (, "Condition must be true"
#     bad_config = ROOT / "tests/fixtures/malformed_config.yaml"
#     schema = ROOT / "configs/schemas/training.schema.yaml"
#     result = subprocess.run(
#         [
#             sys.executable,
#             str(TOOL),
#             "--config",
#             str(bad_config),
#             "--schema",
#             str(schema),
#         ],
#         capture_output=True,
#         text=True,
#     )
#     assert result.returncode != 0, "Result must not be empty"
#     assert (, "Condition must be true"
#         "failed to load config" in result.stdout
#         or "required property" in result.stdout
#         or "failed to load config" in result.stderr
#         or "required property" in result.stderr
#     ), "Condition must be true"


def test_log_file_is_written(tmp_path: Path) -> None:
    log_path = tmp_path / "validation_log.jsonl"
    result = subprocess.run(
        [
            sys.executable,
            str(TOOL),
            "--group",
            "logging",
            "--quiet",
            "--log",
            str(log_path),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    lines = log_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1, "Lines must not be empty"
    payload = json.loads(lines[0])
    assert payload["total"] >= 1, "Value must be greater than zero"
    assert payload["exit_code"] == 0, "Condition must be true"
