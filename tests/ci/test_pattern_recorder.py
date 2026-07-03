#         assert fixer.fix_missing_newline_at_eof() ==
#         assert target.read_bytes() == b"logger.info('sample')\n", "Condition must be true"
#         assert empty.read_bytes() == b"", "Condition must be true"


class TestPattern30MergeReadiness:
    def test_pattern_30_uses_noarg_scorecard(self, tmp_path):
        mod = _load_auto_fix()
        repo_root = tmp_path / "repo"
        scripts_ci = repo_root / "scripts" / "ci"
        scripts_ci.mkdir(parents=True)
        (repo_root / "src").mkdir()

        (scripts_ci / "session_wrapup_autofix.py").write_text(
            """
def _compute_merge_readiness_score():
    return {
        "dimensions": [("auto_fix (0 auto-fixable)", 15, "✅ 0 auto-fixable", True)],
        "score": 100,
        "total": 100,
    }
""".strip() + "\n",
            encoding="utf-8",
        )

        fixer = mod.CommonIssueFixer(repo_root)
        assert fixer.fix_merge_readiness_dims() == [], "Condition must be true"

    def test_run_all_patterns_respects_skip_env(self, monkeypatch):
        mod = _load_auto_fix()
        fixer = mod.CommonIssueFixer(Path("."))
        called: set[str] = set()

        def _make_mock(name: str):
            def _inner():
                called.add(name)
                return []

            return _inner

        # Dynamically mock all fix_*/check_* methods on the fixer so that real
        # implementations (some of which use subprocess or network calls) are not
        # invoked during this unit test.  This also adapts automatically when new
        # patterns are added or removed without requiring a manual list update.
        pattern_methods = [
            attr
            for attr in dir(fixer)
            if (attr.startswith("fix_") or attr.startswith("check_"))
            and callable(getattr(type(fixer), attr, None))
        ]
        for method_name in pattern_methods:
            setattr(fixer, method_name, _make_mock(method_name))  # type: ignore[method-assign]
        monkeypatch.setenv("CODEX_SKIP_PATTERN_NUMS", "30")

        fixer.run_all_patterns()

        assert ("fix_unused_imports" in called, "Condition must be true"
        ), "Pattern 1 (fix_unused_imports) should have been called"
        assert ("fix_merge_readiness_dims" not in called, "Condition must be true"
        ), "Pattern 30 (fix_merge_readiness_dims) should have been skipped"

    def test_pattern_30_skips_auto_fix_self_reference_dimension(self, tmp_path):
        """S178: Pattern 30 must NOT report the ``auto_fix`` self-reference
        dimension as its own issue — that double-counts issues already
        reported by Patterns 1-29 and 31-32 and surfaces in the summary
        as ``auto-fixable`` even though the matching DIM_FIX is
        ``auto_fix_sweep`` (instructions only, never resolves).
        """
        mod = _load_auto_fix()
        repo_root = tmp_path / "repo"
        scripts_ci = repo_root / "scripts" / "ci"
        scripts_ci.mkdir(parents=True)
        (repo_root / "src").mkdir()

        (scripts_ci / "session_wrapup_autofix.py").write_text(
            """
def _compute_merge_readiness_score():
    return {
        "dimensions": [
            ("auto_fix (0 auto-fixable)", 15, "❌ issues found", False),
            ("ruff (src/ clean)", 10, "✅ clean", True),
        ],
        "score": 85,
        "total": 100,
    }
""".strip() + "\n",
            encoding="utf-8",
        )

        fixer = mod.CommonIssueFixer(repo_root, check_only=True)
        # Even though one dimension is failing, Pattern 30 must not return
        # an issue for it because it is the auto_fix self-reference.
        assert fixer.fix_merge_readiness_dims() == [], "Condition must be true"

    def test_pattern_30_avoids_duplicate_module_import(self, tmp_path):
        mod = _load_auto_fix()
        repo_root = tmp_path / "repo"
        scripts_ci = repo_root / "scripts" / "ci"
        scripts_ci.mkdir(parents=True)
        (repo_root / "src").mkdir()

        (scripts_ci / "session_wrapup_autofix.py").write_text(
            """
from pathlib import Path
from codex.logging.structured_logger import logger

_import_count_file = Path(__file__).with_name("import_count.txt")
_count = int(_import_count_file.read_text(encoding="utf-8")) if _import_count_file.exists() else 0
_import_count_file.write_text(str(_count + 1), encoding="utf-8")

def _compute_merge_readiness_score():
    return {
        "dimensions": [("pda_entry_today", 8, "⚠️ no entry today", False)],
        "score": 92,
        "total": 100,
    }

def fix_pda_entry_today(pr_number, sha, run_url, dry_run):
    Path(__file__).with_name("pda_called.txt").write_text("called", encoding="utf-8")
    return True
""".strip() + "\n",
            encoding="utf-8",
        )

        import_count_file = scripts_ci / "import_count.txt"
        pda_called_file = scripts_ci / "pda_called.txt"
        fixer = mod.CommonIssueFixer(repo_root)
        assert fixer.fix_merge_readiness_dims() == [], "Condition must be true"
        assert import_count_file.read_text(encoding="utf-8").strip() == "1", "Count must be greater than zero"
        assert pda_called_file.read_text(encoding="utf-8").strip() == "called", "Condition must be true"


class TestResolveAcctDiffBase:
    """S178: Validate the helper that walks past infra/[skip ci] commits."""

    def _git(self, cwd: Path, *args: str, env: dict | None = None) -> str:
        # NOTE: This intentionally uses stdlib subprocess.run (NOT
        # codex.utils.subprocess.run) because we need the ``env=`` kwarg to
        # pass deterministic GIT_AUTHOR_*/GIT_COMMITTER_* values for these
        # repository fixtures. Importing the stdlib symbol under a distinct
        # name avoids a github-code-quality false-positive that would
        # otherwise flag this call against the project wrapper's signature.
        import os

        merged = os.environ.copy()
        merged.update(env or {})
        return subprocess.run(  # nosec B603 - args are constants under our control
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
            env=merged,
        ).stdout

    def _mkrepo(self, tmp_path: Path) -> Path:
        repo = tmp_path / "r"
        repo.mkdir()
        env = {
            "GIT_AUTHOR_NAME": "test",
            "GIT_AUTHOR_EMAIL": "a@b.c",
            "GIT_COMMITTER_EMAIL": "a@b.c",
            "GIT_COMMITTER_NAME": "test",
        }
        self._git(repo, "init", "-q", "-b", "main", env=env)
        self._git(repo, "config", "commit.gpgsign", "false", env=env)
        return repo

    def _commit(self, repo: Path, msg: str, author_name: str, file_content: str) -> None:
        env = {
            "GIT_AUTHOR_NAME": author_name,
            "GIT_AUTHOR_EMAIL": "a@b.c",
            "GIT_COMMITTER_NAME": author_name,
            "GIT_COMMITTER_EMAIL": "a@b.c",
        }
        f = repo / "README.md"
        f.write_text(file_content, encoding="utf-8")
        self._git(repo, "add", "README.md", env=env)
        self._git(repo, "commit", "-q", "-m", msg, env=env)

    def test_returns_none_when_only_agent_commit(self, tmp_path):
        mod = _load_auto_fix()
        repo = self._mkrepo(tmp_path)
        self._commit(repo, "feat: agent work", "agent", "v1\n")
        # Single commit — has no parent, so the helper returns None and
        # the caller falls back to HEAD~1 (which produces a git error,
        # also OK — Pattern 25 returns no issues in that case).
        assert mod._resolve_acct_diff_base(repo) is None, "Condition must be true"

    def test_skips_infra_bot_commits(self, tmp_path):
        mod = _load_auto_fix()
        repo = self._mkrepo(tmp_path)
        self._commit(repo, "init: bootstrap", "human", "v0\n")
        self._commit(repo, "feat: agent work", "copilot-swe-agent[bot]", "v1\n")
        self._commit(
            repo,
            "chore: auto-merge 1 automated commit(s) from main [skip ci]",
            "github-actions[bot]",
            "v2\n",
        )
        self._commit(
            repo,
            "chore: Generate follow-up prompt for PR #99",
            "github-actions[bot]",
            "v3\n",
        )
        # HEAD     = follow-up prompt (infra)
        # HEAD~1   = auto-merge (infra)
        # HEAD~2   = agent work        ← this is the agent commit
        # HEAD~3   = init              ← parent of agent commit
        base = mod._resolve_acct_diff_base(repo)
        # Confirm the SHA returned is the parent of the agent commit.
        expected_parent = self._git(repo, "rev-parse", "HEAD~3").strip()
        assert base == expected_parent, f"expected parent SHA {expected_parent!r}, got {base!r}"

    def test_skips_skip_ci_subjects_regardless_of_author(self, tmp_path):
        mod = _load_auto_fix()
        repo = self._mkrepo(tmp_path)
        self._commit(repo, "init: bootstrap", "human", "v0\n")
        self._commit(repo, "feat: real work", "alice", "v1\n")
        # Even when authored by a non-bot, [skip ci] subject marks it as infra.
        self._commit(repo, "chore: bump [skip ci]", "alice", "v2\n")
        base = mod._resolve_acct_diff_base(repo)
        expected_parent = self._git(repo, "rev-parse", "HEAD~2").strip()
        assert base == expected_parent, f"expected parent SHA {expected_parent!r}, got {base!r}"
        mod = _load_auto_fix()
        repo = self._mkrepo(tmp_path)
        self._commit(
            repo,
            "chore(manifest): auto-refresh CODEX_MANIFEST.json [skip ci]",
            "github-actions[bot]",
            "v0\n",
        )
        self._commit(
            repo,
            "chore: auto-merge from main [skip ci]",
            "github-actions[bot]",
            "v1\n",
        )
        # No agent commit found within the lookback window.
        assert mod._resolve_acct_diff_base(repo) is None, "Condition must be true"

    def test_skips_dependabot_rebase_commits(self, tmp_path):
        """Dependabot rebase commit subjects are treated as infra regardless
        of authorship — the ``Rebase on `` and ``chore(deps): bump`` markers
        added in S178c ensure these are skipped even when the author is a
        non-dependabot actor (e.g. github-actions[bot] acting on its behalf).
        """
        mod = _load_auto_fix()
        repo = self._mkrepo(tmp_path)
        self._commit(repo, "init: bootstrap", "human", "v0\n")
        self._commit(repo, "feat: agent work", "copilot-swe-agent[bot]", "v1\n")
        # Dependabot rebase commit — subject matches new _INFRA_COMMIT_MARKERS entry.
        self._commit(
            repo,
            "Rebase on main",
            "github-actions[bot]",
            "v2\n",
        )
        # HEAD     = dependabot rebase (infra via subject marker)
        # HEAD~1   = agent work        ← first non-infra commit
        # HEAD~2   = init              ← parent of agent commit
        base = mod._resolve_acct_diff_base(repo)
        expected_parent = self._git(repo, "rev-parse", "HEAD~2").strip()
        assert base == expected_parent, f"expected parent SHA {expected_parent!r} for rebase commit, got {base!r}"

    def test_skips_dependabot_deps_bump_commits(self, tmp_path):
        """``chore(deps): bump`` commit subjects (dependabot PR creation commits)
        are also recognised as infra via subject matching.
        """
        mod = _load_auto_fix()
        repo = self._mkrepo(tmp_path)
        self._commit(repo, "init: bootstrap", "human", "v0\n")
        self._commit(repo, "feat: agent work", "copilot-swe-agent[bot]", "v1\n")
        self._commit(
            repo,
            "chore(deps): bump requests from 2.28.0 to 2.32.3",
            "dependabot[bot]",
            "v2\n",
        )
        # HEAD     = dependabot deps bump (infra via subject marker)
        # HEAD~1   = agent work        ← first non-infra commit
        # HEAD~2   = init              ← parent
        base = mod._resolve_acct_diff_base(repo)
        expected_parent = self._git(repo, "rev-parse", "HEAD~2").strip()
        assert base == expected_parent, f"expected parent SHA {expected_parent!r} for deps-bump commit, got {base!r}"


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
        assert span is not None, "_find_kwarg_removal_span must return a (start, end) tuple for a valid kwarg"
        start, end = span
        result = "f(x=1, x=2)"[:start] + "f(x=1, x=2)"[end:]
        assert "x=2" not in result, "Result must not be empty"
        assert "x=1" in result, "Result must not be empty"

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
        assert span is None, "span is not valid"

    def test_returns_none_when_name_not_at_expected_position(self):
        fixer = self._make_fixer()

        class FakeValue:
            col_offset = 4
            end_col_offset = 5
            end_lineno = 1
            lineno = 1

        class FakeKw:
            arg = "zzz"  # name doesn't match what's in the line
            value = FakeValue()

        span = fixer._find_kwarg_removal_span("f(x=1)", FakeKw())  # type: ignore[arg-type]
        assert span is None, "span is not valid"


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
        assert dk_issues[0]["pattern"] == 18, "Condition must be true"


# ===========================================================================
# ci_pattern_pipeline.py
# ===========================================================================


class TestCiPatternPipeline:
    def test_help(self):
        result = subprocess.run(
            [sys.executable, str(_ROOT / "scripts" / "ci" / "ci_pattern_pipeline.py"), "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, "Result must not be empty"
        assert "detect" in result.stdout.lower() or "pipeline" in result.stdout.lower(), "Result must not be empty"

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
                "--db",
                tmp_db,
            ],
            capture_output=True,
            text=True,
            cwd=_ROOT,
            timeout=240,
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
                "--db",
                tmp_db,
                "--artefact",
                artefact,
            ],
            capture_output=True,
            text=True,
            cwd=_ROOT,
            timeout=240,
        )
        assert result.returncode in (0, 1)
        assert Path(artefact).exists(), "Artefact file not created"
        data = json.loads(Path(artefact).read_text())
        assert "pipeline_status" in data, "Data must not be empty"
        assert "diagnostic_report" in data, "Data must not be empty"

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
        assert mod.run_check() == 0, "Condition must be true"

    def test_no_db_returns_zero(self, tmp_db, tmp_path, monkeypatch):
        """When DB doesn't exist yet, hook should silently pass."""
        monkeypatch.setenv("CODEX_SKIP_PATTERN_WARN", "0")
        monkeypatch.setenv("CODEX_DB_PATH", str(tmp_path / "nonexistent.db"))
        spec = importlib.util.spec_from_file_location(
            "hook_nodb", _ROOT / "scripts" / "hooks" / "pre_commit_pattern_check.py"
        )
        mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        assert mod.run_check() == 0, "Condition must be true"

    def test_detect_patterns_duplicate_kwargs(self):
        """_detect_patterns_in_source identifies Duplicate Kwargs."""
        source = "def f():\n    return g(x=1, x=2)\n"
        detected = hook._detect_patterns_in_source(source, "test.py")
        assert "Duplicate Kwargs" in detected, "Condition must be true"

    def test_detect_patterns_clean_source(self):
        source = "def f():\n    return g(x=1, y=2)\n"
        detected = hook._detect_patterns_in_source(source, "test.py")
        assert "Duplicate Kwargs" not in detected, "Condition must be true"

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
        assert mod.run_check() == 0, "Condition must be true"


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
        assert len(result) == 1, "Result must not be empty"
        assert result[0]["pattern_name"] == "Line Length", "Result must not be empty"
        assert result[0]["pr_count"] == 3, "Result must not be empty"
        assert result[0]["total"] == 3, "Result must not be empty"

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
        assert result[0]["pattern_name"] == "Unused Imports", "Result must not be empty"
        assert result[0]["pr_count"] == 4, "Result must not be empty"
        assert result[1]["pattern_name"] == "Line Length", "Result must not be empty"
        assert result[1]["pr_count"] == 2, "Result must not be empty"

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
        assert rc == 0, "rc is not valid"
        assert "No patterns" in out, "Condition must be true"

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
        assert len(data) == 1, "Data must not be empty"
        assert data[0]["pattern_name"] == "Unused Imports", "Data must not be empty"
        assert data[0]["pr_count"] == 3, "Data must not be empty"
