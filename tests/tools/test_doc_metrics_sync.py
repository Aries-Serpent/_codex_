"""Tests for scripts/tools/doc_metrics_sync.py — doc metric synchronisation engine.

Validates the gather-→-check-→-fix pipeline used by the ``doc-metrics-check``
pre-commit hook and the CI "Fast Validation" gate.

Root-cause context (issues #3565 / #3569)
-----------------------------------------
Stale metric references in documentation files caused the ``doc-metrics-check``
hook to fail → Fast Validation exit code 2 → cascading into the 8.2 % CI
failure rate.  These tests lock in the contract so regressions are caught at
the unit-test level rather than in a remote CI run.
"""

from __future__ import annotations

# Import the module under test -------------------------------------------
import importlib
import sys
import textwrap
from pathlib import Path
from unittest.mock import patch

import pytest

# The script lives outside ``src/``, so we load it via importlib from its
# filesystem path rather than relying on PYTHONPATH/package install.
_SCRIPT_PATH = (
    Path(__file__).resolve().parent.parent.parent / "scripts" / "tools" / "doc_metrics_sync.py"
)

_spec = importlib.util.spec_from_file_location("doc_metrics_sync", _SCRIPT_PATH)
doc_metrics_sync = importlib.util.module_from_spec(_spec)
sys.modules["doc_metrics_sync"] = doc_metrics_sync
_spec.loader.exec_module(doc_metrics_sync)

Rule = doc_metrics_sync.Rule
Finding = doc_metrics_sync.Finding
gather_metrics = doc_metrics_sync.gather_metrics
run = doc_metrics_sync.run
main = doc_metrics_sync.main
_apply_rule = doc_metrics_sync._apply_rule


# ── fixtures ──────────────────────────────────────────────────────────────


@pytest.fixture()
def fake_repo(tmp_path: Path) -> Path:
    """Minimal repo tree with the files ``gather_metrics`` reads."""
    # AGENT_REGISTRY.yaml with a known agent count
    agents_dir = tmp_path / ".github" / "agents"
    agents_dir.mkdir(parents=True)
    (agents_dir / "AGENT_REGISTRY.yaml").write_text("total_agents: 42\n")

    # pyproject.toml with a known coverage threshold
    (tmp_path / "pyproject.toml").write_text("fail_under = 85\n")

    # A small test directory with a known number of test functions
    test_dir = tmp_path / "tests"
    test_dir.mkdir()
    (test_dir / "test_alpha.py").write_text(textwrap.dedent("""\
        def test_one():
            pass

        def test_two():
            pass

        class TestGroup:
            def test_three(self):
                pass
        """))

    # Observability source-of-truth stubs
    tracing_dir = tmp_path / "src" / "mcp" / "server"
    tracing_dir.mkdir(parents=True)
    (tracing_dir / "tracing.py").write_text("def drift_span(): ...\n")

    devcontainer_dir = tmp_path / ".devcontainer"
    devcontainer_dir.mkdir()
    (devcontainer_dir / "devcontainer.json").write_text(
        '{"OTEL_EXPORTER_OTLP_ENDPOINT": "http://localhost:4317"}\n'
    )

    # SAR-G01 guide
    guide_dir = tmp_path / "docs" / "admin"
    guide_dir.mkdir(parents=True)
    (guide_dir / "GITHUB_VARIABLES_MASTER_GUIDE.md").write_text("# Variables\nSAR-G01 COMPLETE\n")

    # Feature store stub
    feast_dir = tmp_path / "src" / "codex_ml" / "features"
    feast_dir.mkdir(parents=True)
    (feast_dir / "feast_compat.py").write_text(textwrap.dedent("""\
        class InMemoryBackend: ...
        class SQLiteBackend: ...
        class RedisBackend: ...
        class DuckDBBackend: ...
        def materialize_to_arrow_ipc(): ...
        """))

    # Workflows directory
    wf_dir = tmp_path / ".github" / "workflows"
    wf_dir.mkdir(parents=True)
    (wf_dir / "ci.yml").write_text("name: CI\n")
    (wf_dir / "test.yml").write_text("name: Test\n")

    return tmp_path


# ── gather_metrics ────────────────────────────────────────────────────────


class TestGatherMetrics:
    """Tests for the metric extraction layer."""

    def test_agent_count_from_registry(self, fake_repo: Path) -> None:
        m = gather_metrics(fake_repo)
        assert m["agent_count"] == "42", "Count must be greater than zero"

    def test_coverage_threshold_from_pyproject(self, fake_repo: Path) -> None:
        m = gather_metrics(fake_repo)
        assert m["coverage_threshold"] == "85", "Condition must be true"

    def test_test_count_floors_to_500(self, fake_repo: Path) -> None:
        """3 test functions → floor(3 / 500) * 500 = 0, but min is 500."""
        m = gather_metrics(fake_repo)
        assert m["test_count_display"] == "500+", "Count must be greater than zero"

    def test_test_count_url_encoded(self, fake_repo: Path) -> None:
        m = gather_metrics(fake_repo)
        assert m["test_count_url"] == "500%2B", "Count must be greater than zero"

    def test_workflow_count(self, fake_repo: Path) -> None:
        m = gather_metrics(fake_repo)
        assert m["workflow_count"] == "2", "Count must be greater than zero"

    def test_sar_g02_score_full_backends(self, fake_repo: Path) -> None:
        m = gather_metrics(fake_repo)
        assert m["sar_g02_score"] == "97", "Condition must be true"

    def test_sar_g05_score_full_observability(self, fake_repo: Path) -> None:
        m = gather_metrics(fake_repo)
        assert m["sar_g05_score"] == "100", "Condition must be true"

    def test_mlops_level(self, fake_repo: Path) -> None:
        m = gather_metrics(fake_repo)
        level = float(m["mlops_level"])
        assert 3.9 <= level <= 3.99, "9 is not valid"

    def test_today_is_iso_format(self, fake_repo: Path) -> None:
        m = gather_metrics(fake_repo)
        assert len(m["today"]) == 10, "Collection must not be empty"
        assert m["today"].count("-") == 2, "Count must be greater than zero"

    def test_defaults_when_files_missing(self, tmp_path: Path) -> None:
        """When no source-of-truth files exist, defaults kick in."""
        m = gather_metrics(tmp_path)
        assert m["agent_count"] == "153", "Count must be greater than zero"
        assert m["coverage_threshold"] == "75", "Condition must be true"
        assert m["test_count_display"] == "500+", "Count must be greater than zero"


# ── _apply_rule ───────────────────────────────────────────────────────────


class TestApplyRule:
    """Tests for the single-rule engine."""

    def test_check_detects_stale_metric(self, tmp_path: Path) -> None:
        doc = tmp_path / "doc.md"
        doc.write_text("We have 100+ tests, hooray!\n")

        rule = Rule(
            id="test_rule",
            files=[str(doc)],
            pattern=r"(\d+\+) tests,",
            replacement="{test_count_display} tests,",
        )
        # Temporarily make the rule think REPO_ROOT is tmp_path
        # by using absolute paths in files list
        metrics = {"test_count_display": "500+"}
        with patch.object(doc_metrics_sync, "REPO_ROOT", tmp_path):
            rule.files = ["doc.md"]
            findings = _apply_rule(rule, metrics, fix=False)
        assert len(findings) == 1, "Findings must not be empty"
        assert findings[0].old_text == "100+ tests,"
        assert findings[0].new_text == "500+ tests,"

    def test_fix_updates_file_in_place(self, tmp_path: Path) -> None:
        doc = tmp_path / "doc.md"
        doc.write_text("We have 100+ tests, hooray!\n")

        rule = Rule(
            id="test_rule",
            files=["doc.md"],
            pattern=r"(\d+\+) tests,",
            replacement="{test_count_display} tests,",
        )
        metrics = {"test_count_display": "500+"}
        with patch.object(doc_metrics_sync, "REPO_ROOT", tmp_path):
            findings = _apply_rule(rule, metrics, fix=True)
        assert len(findings) == 1, "Findings must not be empty"
        assert "500+ tests," in doc.read_text()

    def test_no_finding_when_already_current(self, tmp_path: Path) -> None:
        doc = tmp_path / "doc.md"
        doc.write_text("We have 500+ tests, hooray!\n")

        rule = Rule(
            id="test_rule",
            files=["doc.md"],
            pattern=r"(\d+\+) tests,",
            replacement="{test_count_display} tests,",
        )
        metrics = {"test_count_display": "500+"}
        with patch.object(doc_metrics_sync, "REPO_ROOT", tmp_path):
            findings = _apply_rule(rule, metrics, fix=False)
        assert len(findings) == 0, "Findings must not be empty"

    def test_missing_metric_key_produces_no_findings(self, tmp_path: Path) -> None:
        doc = tmp_path / "doc.md"
        doc.write_text("We have 100+ tests, hooray!\n")

        rule = Rule(
            id="test_rule",
            files=["doc.md"],
            pattern=r"(\d+\+) tests,",
            replacement="{nonexistent_key} tests,",
        )
        with patch.object(doc_metrics_sync, "REPO_ROOT", tmp_path):
            findings = _apply_rule(rule, {}, fix=False)
        assert len(findings) == 0, "Findings must not be empty"

    def test_missing_file_is_skipped(self, tmp_path: Path) -> None:
        rule = Rule(
            id="test_rule",
            files=["does_not_exist.md"],
            pattern=r"(\d+) items",
            replacement="{count} items",
        )
        with patch.object(doc_metrics_sync, "REPO_ROOT", tmp_path):
            findings = _apply_rule(rule, {"count": "5"}, fix=False)
        assert len(findings) == 0, "Findings must not be empty"


# ── run() integration ─────────────────────────────────────────────────────


class TestRun:
    """Tests for the full rule-set pipeline."""

    def test_run_with_custom_rules_and_metrics(self, tmp_path: Path) -> None:
        doc = tmp_path / "README.md"
        doc.write_text("Badge: tests-100%2B%20total\n")

        rules = [
            Rule(
                id="badge",
                files=["README.md"],
                pattern=r"tests-(\d+%2B)%20total",
                replacement="tests-{test_count_url}%20total",
            ),
        ]
        metrics = {"test_count_url": "500%2B"}
        with patch.object(doc_metrics_sync, "REPO_ROOT", tmp_path):
            findings = run(fix=False, rules=rules, metrics=metrics)
        assert len(findings) == 1, "Findings must not be empty"
        assert findings[0].rule_id == "badge", "rule_id is not valid"

    def test_run_fix_mode_updates_all_stale(self, tmp_path: Path) -> None:
        doc1 = tmp_path / "README.md"
        doc1.write_text("Badge: tests-100%2B%20total\n")
        doc2 = tmp_path / "ARCH.md"
        doc2.write_text("📊 100+ Tests\n")

        rules = [
            Rule(
                id="badge",
                files=["README.md"],
                pattern=r"tests-(\d+%2B)%20total",
                replacement="tests-{test_count_url}%20total",
            ),
            Rule(
                id="arch",
                files=["ARCH.md"],
                pattern=r"📊 (\d+\+ Tests)",
                replacement="📊 {test_count_display} Tests",
            ),
        ]
        metrics = {"test_count_url": "500%2B", "test_count_display": "500+"}
        with patch.object(doc_metrics_sync, "REPO_ROOT", tmp_path):
            findings = run(fix=True, rules=rules, metrics=metrics)
        assert len(findings) == 2, "Findings must not be empty"
        assert "500%2B" in doc1.read_text(), "Condition must be true"
        assert "500+" in doc2.read_text(), "Condition must be true"


# ── CLI main() ────────────────────────────────────────────────────────────


class TestMain:
    """Tests for the CLI entry-point (--check, --fix, --report)."""

    def test_check_exits_1_when_stale(self, tmp_path: Path) -> None:
        doc = tmp_path / "doc.md"
        doc.write_text("We have 100+ tests, hooray!\n")

        rules = [
            Rule(
                id="t",
                files=["doc.md"],
                pattern=r"(\d+\+) tests,",
                replacement="{test_count_display} tests,",
            ),
        ]
        metrics = {"test_count_display": "500+"}
        with (
            patch.object(doc_metrics_sync, "REPO_ROOT", tmp_path),
            patch.object(doc_metrics_sync, "RULES", rules),
            patch.object(doc_metrics_sync, "gather_metrics", return_value=metrics),
        ):
            rc = main(["--check"])
        assert rc == 1, "rc is not valid"

    def test_check_exits_0_when_current(self, tmp_path: Path) -> None:
        doc = tmp_path / "doc.md"
        doc.write_text("We have 500+ tests, hooray!\n")

        rules = [
            Rule(
                id="t",
                files=["doc.md"],
                pattern=r"(\d+\+) tests,",
                replacement="{test_count_display} tests,",
            ),
        ]
        metrics = {"test_count_display": "500+"}
        with (
            patch.object(doc_metrics_sync, "REPO_ROOT", tmp_path),
            patch.object(doc_metrics_sync, "RULES", rules),
            patch.object(doc_metrics_sync, "gather_metrics", return_value=metrics),
        ):
            rc = main(["--check"])
        assert rc == 0, "rc is not valid"

    def test_fix_exits_0_and_updates_file(self, tmp_path: Path) -> None:
        doc = tmp_path / "doc.md"
        doc.write_text("We have 100+ tests, hooray!\n")

        rules = [
            Rule(
                id="t",
                files=["doc.md"],
                pattern=r"(\d+\+) tests,",
                replacement="{test_count_display} tests,",
            ),
        ]
        metrics = {"test_count_display": "500+"}
        with (
            patch.object(doc_metrics_sync, "REPO_ROOT", tmp_path),
            patch.object(doc_metrics_sync, "RULES", rules),
            patch.object(doc_metrics_sync, "gather_metrics", return_value=metrics),
        ):
            rc = main(["--fix"])
        assert rc == 0, "rc is not valid"
        assert "500+ tests," in doc.read_text()

    def test_report_always_exits_0(self, tmp_path: Path) -> None:
        doc = tmp_path / "doc.md"
        doc.write_text("We have 100+ tests, hooray!\n")

        rules = [
            Rule(
                id="t",
                files=["doc.md"],
                pattern=r"(\d+\+) tests,",
                replacement="{test_count_display} tests,",
            ),
        ]
        metrics = {"test_count_display": "500+"}
        with (
            patch.object(doc_metrics_sync, "REPO_ROOT", tmp_path),
            patch.object(doc_metrics_sync, "RULES", rules),
            patch.object(doc_metrics_sync, "gather_metrics", return_value=metrics),
        ):
            rc = main(["--report"])
        assert rc == 0, "rc is not valid"


# ── Production RULES smoke-test ───────────────────────────────────────────


class TestProductionRules:
    """Verify that the shipped RULES list is internally consistent."""

    def test_all_rules_have_unique_ids(self) -> None:
        ids = [r.id for r in doc_metrics_sync.RULES]
        duplicates = [i for i in ids if ids.count(i) > 1]
        assert len(ids) == len(set(ids)), f"Duplicate rule IDs: {duplicates}"

    def test_all_rule_patterns_compile(self) -> None:
        import re

        for rule in doc_metrics_sync.RULES:
            try:
                re.compile(rule.pattern, flags=rule.flags)
            except re.error as exc:
                pytest.fail(f"Rule {rule.id!r}: pattern does not compile — {exc}")

    def test_all_rule_files_are_relative(self) -> None:
        for rule in doc_metrics_sync.RULES:
            for f in rule.files:
                msg = f"Rule {rule.id!r}: file path must be relative, got {f!r}"
                assert not f.startswith("/"), msg

    def test_gather_metrics_returns_all_keys_used_by_rules(self) -> None:
        """Ensure no rule references a metric key that gather_metrics doesn't produce."""
        import re

        metrics = gather_metrics(doc_metrics_sync.REPO_ROOT)
        for rule in doc_metrics_sync.RULES:
            keys = re.findall(r"\{(\w+)\}", rule.replacement)
            for key in keys:
                assert key in metrics, (
                    f"Rule {rule.id!r} references {{{{ {key} }}}} "
                    f"but gather_metrics() does not produce it"
                )

    def test_current_repo_has_zero_stale_metrics(self) -> None:
        """After the --fix we ran, no stale metrics should remain."""
        findings = run(fix=False)
        if findings:
            stale = ", ".join(f"{f.rule_id}:{f.file}:{f.line_no}" for f in findings)
            pytest.fail(f"Stale metrics still present: {stale}")
