from codex_ml.eval.metrics import run_unit_tests


def test_run_unit_tests_counts(tmp_path):
    tests_dir = tmp_path / "t"
    tests_dir.mkdir()
    (tests_dir / "test_one.py").write_text(
        "from candidate import buggy\n\n" "def test_one():\n" "    buggy()\n",
        encoding="utf-8",
    )
    (tests_dir / "test_two.py").write_text(
        "from candidate import buggy\n\n" "def test_two():\n" "    buggy()\n",
        encoding="utf-8",
    )
    code = "def buggy():\n    raise RuntimeError('bug')\n"
    summary = run_unit_tests(code, str(tests_dir))
    assert summary == {"passed": 0, "failed": 0, "errors": 2}
