"""Tests for the Phase 6 pattern tooling suite.

Covers:
  - scripts/ci/pattern_recorder.py   (recorder + knowledge-graph helpers)
  - scripts/ci/ci_pattern_pipeline.py (pipeline orchestrator)
  - scripts/hooks/pre_commit_pattern_check.py (pre-commit hook)
  - scripts/ci/auto_fix_common_issues.py     (helper + classification fixes)
"""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Module loaders
# ---------------------------------------------------------------------------

_ROOT = Path(__file__).parent.parent.parent


def _load(rel: str):
    path = _ROOT / rel
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


pr = _load("scripts/ci/pattern_recorder.py")
pipeline = _load("scripts/ci/ci_pattern_pipeline.py")
hook = _load("scripts/hooks/pre_commit_pattern_check.py")


@pytest.fixture()
def tmp_db(tmp_path):
    return str(tmp_path / "test.db")


@pytest.fixture()
def conn(tmp_db):
    c = pr._open_db(tmp_db)
    yield c
    c.close()


def _make_report(tmp_path, issues=None, fixes_applied=None):
    data = {
        "timestamp": "2026-03-24T18:00:00Z",
        "status": "failed",
        "total_issues": len(issues or []),
        "issues": issues or [],
        "fixes_applied": fixes_applied or {},
    }
    p = tmp_path / "report.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


# ===========================================================================
# pattern_recorder.py
# ===========================================================================


class TestOpenDb:
    def test_creates_patterns_table(self, tmp_db):
        c = pr._open_db(tmp_db)
        tables = {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert "patterns" in tables
        c.close()

    def test_creates_indexes(self, tmp_db):
        c = pr._open_db(tmp_db)
        idxs = {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='index'")}
        assert "idx_patterns_name" in idxs
        assert "idx_patterns_session" in idxs
        c.close()

    def test_idempotent(self, tmp_db):
        pr._open_db(tmp_db).close()
        pr._open_db(tmp_db).close()


class TestInsertPattern:
    def test_basic_insert(self, conn):
        row_id = pr._insert_pattern(
            conn, pattern_id=18, pattern_name="Duplicate Kwargs",
            file_path="src/foo.py", line_number=42,
            description="Duplicate 'x' removed",
            auto_fixable=True, fixed=True, session="PR#3740", git_sha="abc123",
        )
        assert row_id >= 1

    def test_row_values_stored_correctly(self, conn):
        pr._insert_pattern(
            conn, pattern_id=1, pattern_name="Unused Imports",
            file_path="tests/test_foo.py", line_number=5,
            description="Import 'Mock' unused",
            auto_fixable=True, fixed=False, session="S186", git_sha=None,
        )
        row = conn.execute("SELECT * FROM patterns WHERE pattern_id=1").fetchone()
        assert row["pattern_name"] == "Unused Imports"
        assert row["auto_fixable"] == 1
        assert row["fixed"] == 0
        assert row["session"] == "S186"
        assert row["git_sha"] is None

    def test_null_file_and_line_allowed(self, conn):
        row_id = pr._insert_pattern(
            conn, pattern_id=4, pattern_name="Coverage Thresholds",
            file_path=None, line_number=None,
            description="Coverage standardised",
            auto_fixable=True, fixed=True, session=None, git_sha=None,
        )
        row = conn.execute("SELECT * FROM patterns WHERE id=?", (row_id,)).fetchone()
        assert row["file_path"] is None
        assert row["line_number"] is None

    def test_multiple_inserts_same_pattern(self, conn):
        for i in range(5):
            pr._insert_pattern(
                conn, pattern_id=18, pattern_name="Duplicate Kwargs",
                file_path=f"src/f{i}.py", line_number=i,
                description="dup", auto_fixable=True, fixed=True,
                session=None, git_sha=None,
            )
        count = conn.execute(
            "SELECT COUNT(*) FROM patterns WHERE pattern_id=18"
        ).fetchone()[0]
        assert count == 5


class TestRecordFromReport:
    def test_records_all_issues(self, conn, tmp_path):
        issues = [
            {"pattern": 18, "pattern_name": "Duplicate Kwargs", "file": "a.py",
             "line": 1, "message": "dup", "auto_fix_available": True},
            {"pattern": 1, "pattern_name": "Unused Imports", "file": "b.py",
             "line": 2, "message": "import", "auto_fix_available": True},
        ]
        n = pr.record_from_report(
            _make_report(tmp_path, issues, {"Duplicate Kwargs": 1, "Unused Imports": 1}),
            conn, session="S186", git_sha="abc",
        )
        assert n == 2
        assert conn.execute("SELECT COUNT(*) FROM patterns").fetchone()[0] == 2

    def test_fixed_flag_from_fixes_applied(self, conn, tmp_path):
        issues = [{"pattern": 18, "pattern_name": "Duplicate Kwargs",
                   "file": "a.py", "line": 1, "message": "dup",
                   "auto_fix_available": True}]
        pr.record_from_report(
            _make_report(tmp_path, issues, {"Duplicate Kwargs": 1}),
            conn, session=None, git_sha=None,
        )
        row = conn.execute("SELECT fixed FROM patterns").fetchone()
        assert row["fixed"] == 1

    def test_unfixed_when_no_fixes_applied(self, conn, tmp_path):
        issues = [{"pattern": 2, "pattern_name": "Unused Variables",
                   "file": "a.py", "line": 5, "message": "unused",
                   "auto_fix_available": False}]
        pr.record_from_report(_make_report(tmp_path, issues), conn, None, None)
        assert conn.execute("SELECT fixed FROM patterns").fetchone()["fixed"] == 0

    def test_bad_path_returns_zero(self, conn):
        assert pr.record_from_report(Path("/nonexistent.json"), conn, None, None) == 0

    def test_empty_issues(self, conn, tmp_path):
        assert pr.record_from_report(_make_report(tmp_path, []), conn, None, None) == 0


class TestHighRecurrence:
    def _seed(self, conn, name, pid, count, fixed_count):
        for i in range(count):
            pr._insert_pattern(
                conn, pattern_id=pid, pattern_name=name,
                file_path=f"f{i}.py", line_number=i,
                description="test", auto_fixable=True,
                fixed=(i < fixed_count), session=None, git_sha=None,
            )

    def test_returns_qualifying_patterns(self, conn):
        self._seed(conn, "Duplicate Kwargs", 18, 5, 4)   # 80% fix-rate
        result = pr.high_recurrence(conn, min_occurrences=3, min_fix_rate=0.5)
        names = [r["pattern_name"] for r in result]
        assert "Duplicate Kwargs" in names

    def test_excludes_below_threshold(self, conn):
        self._seed(conn, "Duplicate Kwargs", 18, 2, 2)   # only 2 occurrences
        result = pr.high_recurrence(conn, min_occurrences=3, min_fix_rate=0.5)
        assert not result

    def test_excludes_low_fix_rate(self, conn):
        self._seed(conn, "Duplicate Kwargs", 18, 5, 0)   # 0% fix-rate
        result = pr.high_recurrence(conn, min_occurrences=3, min_fix_rate=0.5)
        assert not result


class TestExportJson:
    def test_exports_all_rows(self, conn, tmp_path):
        pr._insert_pattern(
            conn, pattern_id=18, pattern_name="Duplicate Kwargs",
            file_path="a.py", line_number=1, description="dup",
            auto_fixable=True, fixed=True, session=None, git_sha=None,
        )
        data = pr.export_json(conn)
        assert data["total"] == 1
        assert data["occurrences"][0]["pattern_name"] == "Duplicate Kwargs"

    def test_writes_file_when_path_given(self, conn, tmp_path):
        pr._insert_pattern(
            conn, pattern_id=1, pattern_name="Unused Imports",
            file_path="a.py", line_number=1, description="unused",
            auto_fixable=True, fixed=True, session=None, git_sha=None,
        )
        out = tmp_path / "export.json"
        pr.export_json(conn, output_path=out)
        assert out.exists()
        loaded = json.loads(out.read_text())
        assert loaded["total"] == 1

    def test_summary_included(self, conn):
        for i in range(3):
            pr._insert_pattern(
                conn, pattern_id=18, pattern_name="Duplicate Kwargs",
                file_path=f"f{i}.py", line_number=i, description="dup",
                auto_fixable=True, fixed=(i < 2), session=None, git_sha=None,
            )
        data = pr.export_json(conn)
        assert "summary" in data
        assert data["summary"][0]["total"] == 3


class TestPatternRecorderCli:
    def test_summary_empty(self, tmp_db, capsys):
        pr.main(["--db", tmp_db, "summary"])
        assert "No pattern occurrences" in capsys.readouterr().out

    def test_query_empty(self, tmp_db, capsys):
        pr.main(["--db", tmp_db, "query"])
        assert "No pattern occurrences" in capsys.readouterr().out

    def test_insert_and_query(self, tmp_db, capsys):
        pr.main(["--db", tmp_db, "insert",
                 "--pattern-id", "18", "--pattern-name", "Duplicate Kwargs",
                 "--description", "dup removed", "--auto-fixable", "--fixed"])
        pr.main(["--db", tmp_db, "query", "--limit", "5"])
        out = capsys.readouterr().out
        assert "Duplicate Kwargs" in out

    def test_high_recurrence_json(self, tmp_db, capsys):
        conn = pr._open_db(tmp_db)
        for i in range(4):
            pr._insert_pattern(conn, pattern_id=18, pattern_name="Duplicate Kwargs",
                                file_path=f"f{i}.py", line_number=i, description="dup",
                                auto_fixable=True, fixed=True, session=None, git_sha=None)
        conn.close()
        pr.main(["--db", tmp_db, "high-recurrence", "--json"])
        out = capsys.readouterr().out
        data = json.loads(out)
        assert any(r["pattern_name"] == "Duplicate Kwargs" for r in data)

    def test_export_stdout(self, tmp_db, capsys):
        conn = pr._open_db(tmp_db)
        pr._insert_pattern(conn, pattern_id=1, pattern_name="Unused Imports",
                            file_path="a.py", line_number=1, description="unused",
                            auto_fixable=True, fixed=True, session=None, git_sha=None)
        conn.close()
        pr.main(["--db", tmp_db, "export"])
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["total"] == 1

    def test_record_from_report_cli(self, tmp_db, tmp_path, capsys):
        issues = [{"pattern": 18, "pattern_name": "Duplicate Kwargs",
                   "file": "src/foo.py", "line": 3, "message": "dup",
                   "auto_fix_available": True}]
        report = _make_report(tmp_path, issues, {"Duplicate Kwargs": 1})
        pr.main(["--db", tmp_db, "record", "--report", str(report)])
        assert "Recorded 1" in capsys.readouterr().out

    def test_trend_empty(self, tmp_db, capsys):
        """trend subcommand prints a table with zero counts when DB is empty."""
        pr.main(["--db", tmp_db, "trend", "--days", "3"])
        out = capsys.readouterr().out
        assert "Count" in out
        assert "0" in out

    def test_trend_json_empty(self, tmp_db, capsys):
        """trend --json emits a valid JSON array of length <days> with count=0."""
        pr.main(["--db", tmp_db, "trend", "--days", "3", "--json"])
        rows = json.loads(capsys.readouterr().out)
        assert len(rows) == 3
        assert all(r["count"] == 0 for r in rows)

    def test_trend_counts_today(self, tmp_db, capsys):
        """trend counts today's insertion in the last day slot."""
        conn = pr._open_db(tmp_db)
        pr._insert_pattern(conn, pattern_id=1, pattern_name="Unused Imports",
                           file_path="a.py", line_number=1, description="u",
                           auto_fixable=True, fixed=True, session=None, git_sha=None)
        conn.close()
        pr.main(["--db", tmp_db, "trend", "--days", "3", "--json"])
        rows = json.loads(capsys.readouterr().out)
        assert rows[-1]["count"] == 1   # today's slot


# ===========================================================================
# auto_fix_common_issues.py — Pattern 18 classification + helper
# ===========================================================================

_AUTO_FIX_PATH = _ROOT / "scripts" / "ci" / "auto_fix_common_issues.py"


def _load_auto_fix():
    spec = importlib.util.spec_from_file_location("auto_fix_common_issues", _AUTO_FIX_PATH)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


class TestPattern18Classification:
    def test_duplicate_kwargs_in_auto_fixable(self):
        mod = _load_auto_fix()
        fixer = mod.CommonIssueFixer(Path("."))
        assert "Duplicate Kwargs" in fixer.auto_fixable_patterns

    def test_duplicate_kwargs_not_in_manual_review(self):
        mod = _load_auto_fix()
        fixer = mod.CommonIssueFixer(Path("."))
        assert "Duplicate Kwargs" not in fixer.manual_review_patterns

    def test_no_pattern_in_both_sets(self):
        mod = _load_auto_fix()
        fixer = mod.CommonIssueFixer(Path("."))
        overlap = fixer.auto_fixable_patterns & fixer.manual_review_patterns
        assert not overlap, f"Patterns in both sets: {overlap}"


class TestAutoFixCheckOnlyBehavior:
    def test_check_only_implies_dry_run(self):
        mod = _load_auto_fix()
        fixer = mod.CommonIssueFixer(Path("."), check_only=True)
        assert fixer.check_only is True
        assert fixer.dry_run is True

    def test_pattern_32_check_only_does_not_modify_file(self, tmp_path):
        mod = _load_auto_fix()
        repo_root = tmp_path / "repo"
        src_dir = repo_root / "src"
        src_dir.mkdir(parents=True)
        target = src_dir / "sample.py"
        original = "value = None  # type: ignore\n"
        target.write_text(original, encoding="utf-8")

        fixer = mod.CommonIssueFixer(repo_root, check_only=True)
        issues = fixer.fix_bare_type_ignore_assign()

        assert issues == [f"{target}:1: fallback assignment ignore should use [assignment,misc]"]
        assert target.read_text(encoding="utf-8") == original

    def test_pattern_32_upgrades_assignment_only_ignore(self, tmp_path):
        mod = _load_auto_fix()
        repo_root = tmp_path / "repo"
        src_dir = repo_root / "src"
        src_dir.mkdir(parents=True)
        target = src_dir / "sample.py"
        target.write_text("value = None  # type: ignore[assignment]\n", encoding="utf-8")

        fixer = mod.CommonIssueFixer(repo_root)
        issues = fixer.fix_bare_type_ignore_assign()

        assert issues == []
        assert target.read_text(encoding="utf-8") == "value = None  # type: ignore[assignment,misc]\n"


class TestFindKwargRemovalSpan:
    def _make_fixer(self):
        mod = _load_auto_fix()
        return mod.CommonIssueFixer(Path("."))

    def _make_kw(self, line: str, name: str, value_src: str):
        """Build an ast.keyword for *name=value_src* within *line*."""
        import ast
        # Parse value to get a real AST node with offsets
        tree = ast.parse(f"f({line.strip()})", mode="eval")
        call = tree.body  # type: ignore[attr-defined]
        for kw in call.keywords:
            if kw.arg == name:
                return kw
        raise ValueError(f"kw '{name}' not found in '{line}'")

    def test_simple_kwarg(self):
        fixer = self._make_fixer()
        import ast
        src = "f(x=1, x=2)"
        tree = ast.parse(src, mode="eval")
        call = tree.body  # type: ignore[attr-defined]
        # Second kwarg named 'x'
        kw = call.keywords[1]
        span = fixer._find_kwarg_removal_span("f(x=1, x=2)", kw)
        assert span is not None
        start, end = span
        result = "f(x=1, x=2)"[:start] + "f(x=1, x=2)"[end:]
        assert "x=2" not in result
        assert "x=1" in result

    def test_returns_none_for_missing_eq(self):
        fixer = self._make_fixer()

        class FakeValue:
            col_offset = 10
            end_col_offset = 12
            end_lineno = 1
            lineno = 1

        class FakeKw:
            arg = "foo"
            value = FakeValue()

        # Line without '=' before col 10
        span = fixer._find_kwarg_removal_span("f(bar bar)", FakeKw())  # type: ignore[arg-type]
        assert span is None

    def test_returns_none_when_name_not_at_expected_position(self):
        fixer = self._make_fixer()

        class FakeValue:
            col_offset = 4
            end_col_offset = 5
            end_lineno = 1
            lineno = 1

        class FakeKw:
            arg = "zzz"   # name doesn't match what's in the line
            value = FakeValue()

        span = fixer._find_kwarg_removal_span("f(x=1)", FakeKw())  # type: ignore[arg-type]
        assert span is None


class TestPattern18InReport:
    """Ensure Pattern 18 appears in generate_json_report output with correct id."""

    def test_pattern_18_in_report_map(self):
        mod = _load_auto_fix()
        fixer = mod.CommonIssueFixer(Path("."))
        # Inject a fake detected issue for Duplicate Kwargs
        fixer.issues_found["Duplicate Kwargs"] = ["src/foo.py:10 - Duplicate kwarg 'x'"]
        report = fixer.generate_json_report()
        dk_issues = [i for i in report["issues"] if i["pattern_name"] == "Duplicate Kwargs"]
        assert dk_issues, "Duplicate Kwargs missing from report issues"
        assert dk_issues[0]["pattern"] == 18


# ===========================================================================
# ci_pattern_pipeline.py
# ===========================================================================


class TestCiPatternPipeline:
    def test_help(self):
        result = subprocess.run(
            [sys.executable, str(_ROOT / "scripts" / "ci" / "ci_pattern_pipeline.py"), "--help"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert "detect" in result.stdout.lower() or "pipeline" in result.stdout.lower()

    @pytest.mark.slow
    @pytest.mark.timeout(300)
    def test_check_only_returns_zero_on_clean_repo(self, tmp_db):
        """Running --check-only on the current repo (which is clean) exits 0."""
        result = subprocess.run(
            [
                sys.executable,
                str(_ROOT / "scripts" / "ci" / "ci_pattern_pipeline.py"),
                "--check-only",
                "--no-record",
                "--db", tmp_db,
            ],
            capture_output=True, text=True, cwd=_ROOT, timeout=240,
        )
        # Should exit 0 (clean) or 1 (issues found — acceptable in a live repo)
        assert result.returncode in (0, 1)

    @pytest.mark.slow
    @pytest.mark.timeout(300)
    def test_artefact_written(self, tmp_path, tmp_db):
        artefact = str(tmp_path / "pipeline.json")
        result = subprocess.run(
            [
                sys.executable,
                str(_ROOT / "scripts" / "ci" / "ci_pattern_pipeline.py"),
                "--check-only",
                "--no-record",
                "--db", tmp_db,
                "--artefact", artefact,
            ],
            capture_output=True, text=True, cwd=_ROOT, timeout=240,
        )
        assert result.returncode in (0, 1)
        assert Path(artefact).exists(), "Artefact file not created"
        data = json.loads(Path(artefact).read_text())
        assert "pipeline_status" in data
        assert "diagnostic_report" in data

    @pytest.mark.slow
    @pytest.mark.timeout(300)
    def test_main_returns_int(self, tmp_db):
        code = pipeline.main(["--check-only", "--no-record", "--db", tmp_db])
        assert isinstance(code, int)
        assert code in (0, 1, 2)


# ===========================================================================
# pre_commit_pattern_check.py
# ===========================================================================


class TestPreCommitHook:
    def test_skip_env_skips_check(self, monkeypatch):
        monkeypatch.setenv("CODEX_SKIP_PATTERN_WARN", "1")
        # Reload with new env
        spec = importlib.util.spec_from_file_location(
            "hook_skip", _ROOT / "scripts" / "hooks" / "pre_commit_pattern_check.py"
        )
        mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        assert mod.run_check() == 0

    def test_no_db_returns_zero(self, tmp_db, monkeypatch):
        """When DB doesn't exist yet, hook should silently pass."""
        monkeypatch.setenv("CODEX_SKIP_PATTERN_WARN", "0")
        monkeypatch.setenv("CODEX_DB_PATH", "/tmp/__nonexistent_db_xyz__.db")
        spec = importlib.util.spec_from_file_location(
            "hook_nodb", _ROOT / "scripts" / "hooks" / "pre_commit_pattern_check.py"
        )
        mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        assert mod.run_check() == 0

    def test_detect_patterns_duplicate_kwargs(self):
        """_detect_patterns_in_source identifies Duplicate Kwargs."""
        source = "def f():\n    return g(x=1, x=2)\n"
        detected = hook._detect_patterns_in_source(source, "test.py")
        assert "Duplicate Kwargs" in detected

    def test_detect_patterns_clean_source(self):
        source = "def f():\n    return g(x=1, y=2)\n"
        detected = hook._detect_patterns_in_source(source, "test.py")
        assert "Duplicate Kwargs" not in detected

    def test_detect_patterns_syntax_error_does_not_raise(self):
        source = "def f(\n    return g(x=1\n"
        # Should not raise
        detected = hook._detect_patterns_in_source(source, "broken.py")
        assert isinstance(detected, set)

    def test_no_high_recurrence_patterns_returns_zero(self, tmp_db, monkeypatch):
        monkeypatch.setenv("CODEX_SKIP_PATTERN_WARN", "0")
        monkeypatch.setenv("CODEX_DB_PATH", tmp_db)
        monkeypatch.setenv("CODEX_PATTERN_MIN_OCC", "10")  # impossible threshold
        spec = importlib.util.spec_from_file_location(
            "hook_nhr", _ROOT / "scripts" / "hooks" / "pre_commit_pattern_check.py"
        )
        mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        # DB exists but empty — no high-recurrence patterns
        pr._open_db(tmp_db).close()
        assert mod.run_check() == 0


# ===========================================================================
# cross_pr_correlation — Phase 8 P1
# ===========================================================================


class TestCrossPrCorrelation:
    """Tests for pattern_recorder.cross_pr_correlation() (Phase 8 P1)."""

    def _insert(self, conn, name: str, sha: str, pid: int = 1) -> None:
        pr._insert_pattern(
            conn,
            pattern_id=pid,
            pattern_name=name,
            file_path="f.py",
            line_number=1,
            description="d",
            auto_fixable=True,
            fixed=False,
            session="s",
            git_sha=sha,
        )

    def test_empty_db_returns_empty(self, conn):
        assert pr.cross_pr_correlation(conn, min_prs=2) == []

    def test_pattern_in_one_sha_excluded(self, conn):
        self._insert(conn, "Unused Imports", "abc123")
        self._insert(conn, "Unused Imports", "abc123")
        result = pr.cross_pr_correlation(conn, min_prs=2)
        assert result == [], "Should exclude patterns with only 1 distinct SHA"

    def test_pattern_in_exact_min_prs_included(self, conn):
        """Pattern appearing in exactly min_prs distinct SHAs is included."""
        for sha in ("sha1", "sha2", "sha3"):
            self._insert(conn, "Line Length", sha)
        result = pr.cross_pr_correlation(conn, min_prs=3)
        assert len(result) == 1
        assert result[0]["pattern_name"] == "Line Length"
        assert result[0]["pr_count"] == 3
        assert result[0]["total"] == 3

    def test_multiple_occurrences_same_sha_counted_once(self, conn):
        """10 insertions with the same SHA still count as 1 PR."""
        for _ in range(10):
            self._insert(conn, "Unsorted Imports", "deadbeef")
        result = pr.cross_pr_correlation(conn, min_prs=2)
        assert result == [], "Same SHA repeated does not count as multiple PRs"

    def test_multiple_patterns_sorted_by_pr_count(self, conn):
        """Results sorted by descending pr_count."""
        # 'Unused Imports' in 4 SHAs; 'Line Length' in 2 SHAs
        for i, sha in enumerate(("s1", "s2", "s3", "s4")):
            self._insert(conn, "Unused Imports", sha, pid=1)
        for sha in ("s5", "s6"):
            self._insert(conn, "Line Length", sha, pid=12)
        result = pr.cross_pr_correlation(conn, min_prs=2)
        assert result[0]["pattern_name"] == "Unused Imports"
        assert result[0]["pr_count"] == 4
        assert result[1]["pattern_name"] == "Line Length"
        assert result[1]["pr_count"] == 2

    def test_null_sha_rows_excluded_from_count(self, conn):
        """Rows with NULL git_sha do not count toward pr_count."""
        self._insert(conn, "Duplicate Kwargs", "realsha")
        # Insert a row with None sha via direct SQL (simulate untagged)
        conn.execute(
            "INSERT INTO patterns (pattern_id, pattern_name, file_path, "
            "line_number, description, auto_fixable, fixed, session, git_sha, timestamp) "
            "VALUES (18, 'Duplicate Kwargs', 'f.py', 1, 'd', 1, 0, 's', NULL, '2026-01-01')"
        )
        conn.commit()
        result = pr.cross_pr_correlation(conn, min_prs=2)
        assert result == [], "NULL sha row should not boost pr_count to 2"

    def test_cli_cross_pr_empty(self, tmp_db, capsys):
        """CLI cross-pr subcommand prints 'No patterns' when DB empty."""
        rc = pr.main(["--db", tmp_db, "cross-pr", "--min-prs", "2"])
        out = capsys.readouterr().out
        assert rc == 0
        assert "No patterns" in out

    def test_cli_cross_pr_json(self, tmp_db, capsys):
        """CLI cross-pr --json returns valid JSON."""
        conn = pr._open_db(tmp_db)
        for sha in ("aaa", "bbb", "ccc"):
            pr._insert_pattern(
                conn,
                pattern_id=1,
                pattern_name="Unused Imports",
                file_path="f.py",
                line_number=1,
                description="d",
                auto_fixable=True,
                fixed=False,
                session="s",
                git_sha=sha,
            )
        conn.close()
        pr.main(["--db", tmp_db, "cross-pr", "--min-prs", "3", "--json"])
        data = json.loads(capsys.readouterr().out)
        assert len(data) == 1
        assert data[0]["pattern_name"] == "Unused Imports"
        assert data[0]["pr_count"] == 3
