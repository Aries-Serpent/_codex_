"""Tests for cpu_baseline.py — P10-04.

Verifies that the baseline runner produces valid output on CPU-only machines.
All tests are hardware-agnostic and complete in < 5 s.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "scripts" / "benchmark"))
from cpu_baseline import compare_with_baseline, run_benchmarks


class TestRunBenchmarks:
    def test_returns_dict_with_required_keys(self):
        results = run_benchmarks(["cpu"])
        assert isinstance(results, dict)
        assert "timestamp" in results, "Result must not be empty"
        assert "machine" in results, "Result must not be empty"
        assert "suites" in results, "Result must not be empty"

    def test_machine_block_has_platform_info(self):
        results = run_benchmarks(["cpu"])
        m = results["machine"]
        assert isinstance(m["platform"], str)
        assert isinstance(m["python"], str)
        assert isinstance(m["cpu_count"], int)
        assert m["cpu_count"] >= 1, "Value must be greater than zero"

    def test_cpu_suite_runs_all_benchmarks(self):
        results = run_benchmarks(["cpu"])
        benchmarks = results["suites"]["cpu"]["benchmarks"]
        assert "sha256_1MB" in benchmarks, "Condition must be true"
        assert "int_sort_10k" in benchmarks, "Condition must be true"
        assert "math_sqrt_loop" in benchmarks, "Condition must be true"
        assert "json_roundtrip_100k_chars" in benchmarks, "Condition must be true"

    def test_benchmark_result_has_numeric_timing(self):
        results = run_benchmarks(["cpu"])
        for bench_name, bdata in results["suites"]["cpu"]["benchmarks"].items():
            assert bdata["status"] == "ok", f"{bench_name} failed: {bdata['status']}"
            assert bdata["per_rep_us"] > 0, f"{bench_name} per_rep_us should be > 0"
            assert bdata["reps"] > 0, "Value must be greater than zero"

    def test_io_suite_completes(self):
        results = run_benchmarks(["io"])
        assert "io" in results["suites"], "Result must not be empty"
        assert results["suites"]["io"]["elapsed_s"] >= 0, "Value must be greater than zero"

    def test_import_suite_completes(self):
        results = run_benchmarks(["import"])
        assert "import" in results["suites"], "Result must not be empty"
        benchmarks = results["suites"]["import"]["benchmarks"]
        assert len(benchmarks) >= 3, "Benchmarks must not be empty"

    def test_ml_suite_completes_or_skips_gracefully(self):
        """ML suite skips gracefully if torch/numpy not installed."""
        results = run_benchmarks(["ml"])
        assert "ml" in results["suites"], "Result must not be empty"
        # Each benchmark either succeeds or shows skip/error — no crash
        for bdata in results["suites"]["ml"]["benchmarks"].values():
            assert "status" in bdata, "Data must not be empty"

    def test_all_suites_run_without_error(self):
        """Full baseline completes without raising an exception."""
        results = run_benchmarks()
        assert isinstance(results["suites"], dict)
        assert len(results["suites"]) >= 3, "Collection must not be empty"

    def test_json_serialisable(self):
        results = run_benchmarks(["cpu"])
        dumped = json.dumps(results)
        loaded = json.loads(dumped)
        assert loaded["suites"]["cpu"]["benchmarks"]["sha256_1MB"]["status"] == "ok", "Condition must be true"


class TestCompareWithBaseline:
    def _mock_result(self, per_rep_us: float) -> dict:
        return {
            "suites": {
                "cpu": {
                    "benchmarks": {
                        "sha256_1MB": {
                            "status": "ok",
                            "reps": 100,
                            "total_s": per_rep_us * 100 / 1_000_000,
                            "per_rep_us": per_rep_us,
                        }
                    }
                }
            }
        }

    def test_no_regression_within_threshold(self):
        baseline = self._mock_result(500.0)
        current = self._mock_result(750.0)  # 1.5× — within 2.0× threshold
        regressions = compare_with_baseline(current, baseline, threshold=2.0)
        assert regressions == [], "regressions is not valid"

    def test_regression_detected_above_threshold(self):
        baseline = self._mock_result(500.0)
        current = self._mock_result(1200.0)  # 2.4× — above 2.0× threshold
        regressions = compare_with_baseline(current, baseline, threshold=2.0)
        assert len(regressions) == 1, "Regressions must not be empty"
        assert "REGRESSION" in regressions[0], "Condition must be true"

    def test_skipped_benchmarks_not_flagged(self):
        baseline = {
            "suites": {
                "ml": {
                    "benchmarks": {
                        "torch_matmul_64x64_cpu": {"status": "error: No module named 'torch'"}
                    }
                }
            }
        }
        current = {
            "suites": {
                "ml": {
                    "benchmarks": {
                        "torch_matmul_64x64_cpu": {"status": "error: No module named 'torch'"}
                    }
                }
            }
        }
        regressions = compare_with_baseline(current, baseline)
        assert regressions == [], "regressions is not valid"

    def test_missing_baseline_benchmark_not_flagged(self):
        """New benchmarks not in baseline should not cause false regressions."""
        baseline = {"suites": {}}
        current = self._mock_result(500.0)
        regressions = compare_with_baseline(current, baseline, threshold=2.0)
        assert regressions == [], "regressions is not valid"


class TestCLI:
    def test_cli_suite_flag(self, tmp_path):
        from cpu_baseline import main

        json_path = tmp_path / "result.json"
        rc = main(["--suite", "cpu", "--json", str(json_path)])
        assert rc == 0, "rc is not valid"
        assert json_path.exists(), "Condition must be true"
        data = json.loads(json_path.read_text())
        assert "cpu" in data["suites"], "Data must not be empty"

    def test_cli_compare_creates_baseline_if_missing(self, tmp_path):
        from cpu_baseline import main

        baseline_path = tmp_path / "baseline.json"
        rc = main(["--suite", "cpu", "--compare", str(baseline_path)])
        assert rc == 0, "rc is not valid"
        assert baseline_path.exists(), "Condition must be true"

    def test_cli_compare_no_regression(self, tmp_path):
        from cpu_baseline import main, run_benchmarks

        # Save a baseline first
        baseline_path = tmp_path / "baseline.json"
        baseline = run_benchmarks(["cpu"])
        baseline_path.write_text(json.dumps(baseline))
        # Compare against itself — should be 0 regressions
        rc = main(["--suite", "cpu", "--compare", str(baseline_path)])
        assert rc == 0, "rc is not valid"
