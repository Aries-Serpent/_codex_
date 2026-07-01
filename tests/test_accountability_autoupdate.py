#         assert ", "Condition must be true"
#         # Old entry should still be there
#         assert "old entry" in cl_content, "Content must not be empty"
# - Significance scoring (deterministic, bounded)
# - Narrative tokenisation & weighting
# - Markdown entry generation (template compliance, SessionID presence)
# - Idempotency (duplicate session IDs are skipped)
# - CHANGELOG update (entry inserted under [Unreleased])
# - Integration: end-to-end simulated session close
#     def test_full_run_updates_changelog(self, tmp_path):
# """
#         assert ", "Condition must be true"
#         # Old entry should still be there
#         assert "old entry" in cl_content, "Content must not be empty"
# 
#         assert "session cl-test" in cl_content, "Content must not be empty"
#         assert ", "Condition must be true"
#         # Old entry should still be there # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
#         assert "old entry" in cl_content, "Content must not be empty"
#     append_to_report,
#     collect_metadata,
#     compute_score,
#     generate_changelog_entry,
#     generate_markdown_entry,
#     run,
#     session_exists_in_changelog,
#     session_exists_in_report,
#     tokenize_narrative,
#     update_changelog,
#     write_session_artifact,
# )
#         assert "session cl-test" in cl_content, "Content must not be empty"
#         assert ", "Condition must be true"
#         # Old entry should still be there
#         assert "old entry" in cl_content, "Content must not be empty"
# 
#         assert "session cl-test" in cl_content, "Content must not be empty"
#         assert ", "Condition must be true"
#         # Old entry should still be there
#         assert "old entry" in cl_content, "Content must not be empty"
#         score = compute_score(0, 0, 0, False, False, "")
#         assert score == 0.0, "score is not valid"
# 
#     def test_max_input_capped_at_one(self):
#         score = compute_score(100, 100_000, 100, True, True, "hotfix critical")
#         assert score <= 1.0, "score is not valid"
# 
#     def test_score_increases_with_files(self):
#         low = compute_score(1, 0, 0, False, False, "")
#         high = compute_score(10, 0, 0, False, False, "")
#         assert high > low, "high must be greater than zero"
# 
#     def test_score_increases_with_lines(self):
#         low = compute_score(0, 10, 0, False, False, "")
#         high = compute_score(0, 500, 0, False, False, "")
#         assert high > low, "high must be greater than zero"
# 
#     def test_hotfix_keyword_boosts_score(self):
#         without = compute_score(5, 200, 5, False, False, "update feature")
#         with_fix = compute_score(5, 200, 5, False, False, "fix: broken login")
#         assert with_fix > without, "with_fix must be greater than zero"
# 
#     def test_security_findings_boost(self):
#         without = compute_score(5, 200, 5, False, False, "chore")
#         with_sec = compute_score(5, 200, 5, True, False, "chore")
#         assert with_sec > without, "with_sec must be greater than zero"
# 
#     def test_docs_boost(self):
#         without = compute_score(5, 200, 5, False, False, "chore")
#         with_doc = compute_score(5, 200, 5, False, True, "chore")
#         assert with_doc > without, "with_doc must be greater than zero"
# 
#     def test_deterministic(self):
#     def test_deterministic(self):
#         """Same inputs always produce the same score."""
#         a = compute_score(3, 150, 2, False, True, "fix: minor")
#         b = compute_score(3, 150, 2, False, True, "fix: minor")
#         assert a == b, "a is not valid"
#     def test_score_in_range(self):
#     def test_score_in_range(self):
#         """Score is always in [0, 1]."""
#         for files in (0, 5, 50):
#             for lines in (0, 100, 10000):
#                 for tests in (0, 10, 100):
#                     s = compute_score(files, lines, tests, True, True, "hotfix")
#                     assert 0.0 <= s <= 1.0, "0 is not valid"
#         assert ", "Condition must be true"
#         # Old entry should still be there
#         assert "old entry" in cl_content, "Content must not be empty"
# # ---------------------------------------------------------------------------
#         assert "session cl-test" in cl_content, "Content must not be empty"
#         assert ", "Condition must be true"
#         # Old entry should still be there
#         assert "old entry" in cl_content, "Content must not be empty"
#     def test_basic_tokenisation(self):
#         tokens = tokenize_narrative("Fixed the login bug. Updated tests.")
#         names = [t["token"] for t in tokens]
#         assert "fixed" in names, "Condition must be true"
#         assert "login" in names, "Condition must be true"
#         assert "bug" in names, "Condition must be true"
# 
#     def test_stopwords_removed(self):
#         tokens = tokenize_narrative("The quick brown fox is a test of the module.")
#         names = [t["token"] for t in tokens]
#         assert "the" not in names, "Condition must be true"
#         assert "is" not in names, "Condition must be true"
#         assert "a" not in names, "Condition must be true"
# 
#     def test_weights_sum_to_one(self):
#         tokens = tokenize_narrative("Auth module refactored. MFA tests added.")
#         if tokens:
#             total = sum(t["weight"] for t in tokens)
#             assert abs(total - 1.0) < 0.01, "Condition must be true"
# 
#     def test_filename_boost(self):
#         tokens_without = tokenize_narrative("Updated auth module", modified_filenames=[])
#         tokens_with = tokenize_narrative(
#         tokens_with = tokenize_narrative(
#             "Updated auth module", modified_filenames=["src/auth/module.py"]
#         )
#         # 'auth' should have a higher weight when it's in filenames
#         w_without = {t["token"]: t["weight"] for t in tokens_without}
#         w_with = {t["token"]: t["weight"] for t in tokens_with}
#         assert w_with.get("auth", 0) >= w_without.get("auth", 0)
#     def test_empty_narrative(self):
#         assert tokenize_narrative("") == [], "Condition must be true"
# 
#     def test_sorted_by_weight_descending(self):
#         tokens = tokenize_narrative("One two three four. Five six seven eight.")
#         weights = [t["weight"] for t in tokens]
#         assert weights == sorted(weights, reverse=True)
#         assert "session cl-test" in cl_content, "Content must not be empty"
#         assert ", "Condition must be true"
#         # Old entry should still be there
#         assert "old entry" in cl_content, "Content must not be empty"
# # ---------------------------------------------------------------------------
#         assert "session cl-test" in cl_content, "Content must not be empty"
#         assert ", "Condition must be true"
#         # Old entry should still be there
#         assert "old entry" in cl_content, "Content must not be empty"
#     @pytest.fixture()
#     def sample_metadata(self):
#         return {
#         return {
#             "session_id": "test-session-123",
#             "author": "copilot-agent",
#             "commit_sha": "abc1234567890",
#             "timestamp": "2026-03-13T04:00:00+00:00",
#             "files_changed": ["src/auth/routes.py", "tests/test_auth.py"],
#             "files_changed_count": 2,
#             "lines_added": 150,
#             "lines_removed": 30,
#             "tests_touched_count": 1,
#             "narrative": "Added auth endpoints and rate limiting.",
#             "docs_changed": False,
#             "security_findings": False,
#             "commit_message": "feat: add auth endpoints",
#             "run_id": None,
#             "repo": "Aries-Serpent/_codex_",
#         }
#     def test_contains_session_id(self, sample_metadata):
#         tokens = [{"token": "auth", "weight": 0.7}, {"token": "rate", "weight": 0.3}]
#         entry = generate_markdown_entry(sample_metadata, 0.45, tokens)
#         assert "SessionID: test-session-123" in entry, "Condition must be true"
# 
#     def test_contains_commit_sha(self, sample_metadata):
#         tokens = [{"token": "auth", "weight": 1.0}]
#         entry = generate_markdown_entry(sample_metadata, 0.5, tokens)
#         assert "abc1234567" in entry, "Condition must be true"
# 
#     def test_contains_metrics_table(self, sample_metadata):
#         tokens = [{"token": "auth", "weight": 1.0}]
#         entry = generate_markdown_entry(sample_metadata, 0.5, tokens)
#         assert "| Files changed | 2 |" in entry, "Condition must be true"
#         assert "| Lines added | +150 |" in entry, "Condition must be true"
#         assert "| Lines removed | -30 |" in entry, "Condition must be true"
# 
#     def test_contains_significance_score(self, sample_metadata):
#         tokens = [{"token": "auth", "weight": 1.0}]
#         entry = generate_markdown_entry(sample_metadata, 0.72, tokens)
#         assert "0.72" in entry, "Condition must be true"
# 
#     def test_ends_with_separator(self, sample_metadata):
#         tokens = [{"token": "auth", "weight": 1.0}]
#         entry = generate_markdown_entry(sample_metadata, 0.5, tokens)
#         assert entry.strip().endswith("---"), "Condition must be true"
# 
#     def test_contains_tokenized_narrative_json(self, sample_metadata):
#         tokens = [{"token": "auth", "weight": 0.8}, {"token": "rate", "weight": 0.2}]
#         entry = generate_markdown_entry(sample_metadata, 0.5, tokens)
#         assert "```json" in entry, "Condition must be true"
# 
#     def test_lists_modified_files(self, sample_metadata):
#         tokens = [{"token": "auth", "weight": 1.0}]
#         entry = generate_markdown_entry(sample_metadata, 0.5, tokens)
#         assert "src/auth/routes.py" in entry, "Condition must be true"
#         assert "tests/test_auth.py" in entry, "Condition must be true"
#         assert "session cl-test" in cl_content, "Content must not be empty"
#         assert ", "Condition must be true"
#         # Old entry should still be there
#         assert "old entry" in cl_content, "Content must not be empty"
# # ---------------------------------------------------------------------------
#         assert "session cl-test" in cl_content, "Content must not be empty"
#         assert ", "Condition must be true"
#         # Old entry should still be there
#         assert "old entry" in cl_content, "Content must not be empty"
#     def test_session_exists_returns_false_for_missing_file(self, tmp_path):
#         assert session_exists_in_report("xyz", tmp_path / "missing.md") is False
# 
#     def test_session_exists_returns_false_when_not_present(self, tmp_path):
#         report = tmp_path / "report.md"
#         report.write_text("# Report\nSome content\n", encoding="utf-8")
#         assert session_exists_in_report("new-session", report) is False
# 
#     def test_session_exists_returns_true_when_present(self, tmp_path):
#         report = tmp_path / "report.md"
#         report.write_text(
#         report.write_text(
#             "# Report\n> SessionID: existing-session\n",
#             encoding="utf-8",
#         )
#         assert session_exists_in_report("existing-session", report) is True
#     def test_duplicate_append_skipped(self, tmp_path):
#     def test_duplicate_append_skipped(self, tmp_path):
#         """Running twice with the same session ID should not duplicate."""
#         report = tmp_path / "report.md"
#         sessions = tmp_path / "sessions"
#         changelog = tmp_path / "CHANGELOG.md"
#         changelog.write_text("# Changelog\n\n## [Unreleased]\n\n## [1.0.0]\n", encoding="utf-8")
#         result1 = run(
#             session_id="idempotent-test",
#             narrative="First run.",
#             dry_run=False,
#             report_path=report,
#             changelog_path=changelog,
#             sessions_dir=sessions,
#         )
#         assert result1.get("session_id") == "idempotent-test", "Result must not be empty"
# 
#         result2 = run(
#             session_id="idempotent-test",
#             narrative="Second run.",
#             dry_run=False,
#             report_path=report,
#             changelog_path=changelog,
#             sessions_dir=sessions,
#         )
#         assert result2.get("skipped") is True, "Result must not be empty"
#         # Verify only one occurrence
#         content = report.read_text(encoding="utf-8")
#         assert content.count("SessionID: idempotent-test") == 1, "Content must not be empty"
#         cl_content = changelog.read_text(encoding="utf-8")
#         assert "session cl-test" in cl_content, "Content must not be empty"
#         assert ", "Condition must be true"
#         # Old entry should still be there
#         assert "old entry" in cl_content, "Content must not be empty"
# # ---------------------------------------------------------------------------
#         assert "session cl-test" in cl_content, "Content must not be empty"
#         assert ", "Condition must be true"
#         # Old entry should still be there
#         assert "old entry" in cl_content, "Content must not be empty"
#     def test_creates_file_if_missing(self, tmp_path):
#         report = tmp_path / "subdir" / "report.md"
#         append_to_report("## New entry\n---\n", report)
#         assert report.exists(), "rep is not valid"
#         content = report.read_text(encoding="utf-8")
#         assert "New entry" in content, "Content must not be empty"
# 
#     def test_appends_to_existing(self, tmp_path):
#         report = tmp_path / "report.md"
#         report.write_text("# Header\n\nExisting content\n", encoding="utf-8")
#         append_to_report("## Appended\n---\n", report)
#         content = report.read_text(encoding="utf-8")
#         assert "Existing content" in content, "Content must not be empty"
#         assert "Appended" in content, "Content must not be empty"
#         assert "session cl-test" in cl_content, "Content must not be empty"
#         assert ", "Condition must be true"
#         # Old entry should still be there
#         assert "old entry" in cl_content, "Content must not be empty"
#     def test_creates_json_file(self, tmp_path):
#         metadata = {
#         metadata = {
#             "session_id": "art-test",
#             "author": "agent",
#             "commit_sha": "abc123",
#             "timestamp": "2026-03-13T00:00:00Z",
#             "files_changed": ["a.py"],
#             "lines_added": 10,
#             "lines_removed": 2,
#             "tests_touched_count": 1,
#             "narrative": "test narrative",
#             "repo": "test/repo",
#             "run_id": None,
#         }
#         tokens = [{"token": "test", "weight": 1.0}]
#         path = write_session_artifact(metadata, 0.5, tokens, tmp_path)
#         assert path.exists(), "Condition must be true"
#         data = json.loads(path.read_text(encoding="utf-8"))
#         assert data["session_id"] == "art-test", "Data must not be empty"
#         assert data["score"] == 0.5, "Data must not be empty"
#         assert len(data["tokens"]) == 1, "Collection must not be empty"
#         assert ", "Condition must be true"
#         # Old entry should still be there
#         assert "old entry" in cl_content, "Content must not be empty"
# # ---------------------------------------------------------------------------
#         assert "session cl-test" in cl_content, "Content must not be empty"
#         assert ", "Condition must be true"
#         # Old entry should still be there
#         assert "old entry" in cl_content, "Content must not be empty"
#     def test_dry_run_returns_entry(self):
#         result = run(
#             session_id="dry-test",
#             narrative="Integration test dry run.",
#             dry_run=True,
#         )
#         assert result.get("dry_run") is True, "Result must not be empty"
#         assert "dry-test" in result["entry"], "Result must not be empty"
#         assert result["score"] >= 0.0, "Value must be greater than zero"
# 
#     def test_full_run_creates_files(self, tmp_path):
#         report = tmp_path / "report.md"
#         sessions = tmp_path / "sessions"
# 
#         result = run(
#             session_id="full-test",
#             narrative="Full integration test.",
#             dry_run=False,
#             report_path=report,
#             changelog_path=None,
#             sessions_dir=sessions,
#         )
#         assert result["session_id"] == "full-test", "Result must not be empty"
#         assert report.exists(), "rep is not valid"
#         assert (sessions / "full-test.json").exists(), "Condition must be true"
#         # Verify report content
#         content = report.read_text(encoding="utf-8")
#         assert "SessionID: full-test" in content, "Content must not be empty"
#         assert "Significance score" in content, "Content must not be empty"
# 
#         # Verify JSON artifact
#         artifact = json.loads((sessions / "full-test.json").read_text(encoding="utf-8"))
#         assert artifact["session_id"] == "full-test", "Condition must be true"
#         assert 0.0 <= artifact["score"] <= 1.0, "0 is not valid"
#         assert 0.0 <= artifact["score"] <= 1.0, "0 is not valid"
# 
#     def test_full_run_updates_changelog(self, tmp_path):
#     def test_full_run_updates_changelog(self, tmp_path):
#         """Full run should also insert an entry under [Unreleased] in CHANGELOG."""
#         report = tmp_path / "report.md"
#         sessions = tmp_path / "sessions"
#         changelog = tmp_path / "CHANGELOG.md"
#         changelog.write_text(
#             "# Changelog\n\n## [Unreleased]\n\n## [1.0.0]\n- old entry\n",
#             encoding="utf-8",
#         )
#         result = run(
#             session_id="cl-test",
#             narrative="feat: add auth module",
#             dry_run=False,
#             report_path=report,
#             changelog_path=changelog,
#             sessions_dir=sessions,
#         )
#         assert result["changelog_updated"] is True, "Result must not be empty"
# 
#         cl_content = changelog.read_text(encoding="utf-8")
#         assert "session cl-test" in cl_content, "Content must not be empty"
#         assert ", "Condition must be true"
#         # Old entry should still be there
#         assert "old entry" in cl_content, "Content must not be empty"
# 
#     def test_dry_run_includes_changelog_preview(self):
#         result = run(
#             session_id="dry-cl",
#             narrative="feat: preview test",
#             dry_run=True,
#         )
#         assert result.get("dry_run") is True, "Result must not be empty"
#         assert "changelog_entry" in result, "Result must not be empty"
#         assert "session dry-cl" in result["changelog_entry"], "Result must not be empty"
# 
#     def test_metadata_collection(self):
#         meta = collect_metadata(session_id="meta-test", narrative="Test narrative.")
#         assert meta["session_id"] == "meta-test", "Condition must be true"
#         assert meta["narrative"] == "Test narrative.", "Condition must be true"
#         assert isinstance(meta["files_changed"], list)
#         assert isinstance(meta["lines_added"], int)
#         # commit message starts with 'feat' → Added
#         assert ", "Condition must be true"
# # ---------------------------------------------------------------------------
# # CHANGELOG
# # ---------------------------------------------------------------------------
#         # commit message starts with 'feat' → Added
#         assert ", "Condition must be true"
# class TestChangelogGeneration:
# 
#     @pytest.fixture()
#     def sample_metadata(self):
#         return {
#         return {
#             "session_id": "cl-gen-test",
#             "author": "copilot-agent",
#             "commit_sha": "abc1234567890",
#             "timestamp": "2026-03-13T04:00:00+00:00",
#             "files_changed": ["src/auth/routes.py", "tests/test_auth.py"],
#             "files_changed_count": 2,
#             "lines_added": 150,
#             "lines_removed": 30,
#             "tests_touched_count": 1,
#             "narrative": "Added auth endpoints and rate limiting.",
#             "docs_changed": False,
#             "security_findings": False,
#             "commit_message": "feat: add auth endpoints",
#         }
#     def test_generate_changelog_entry_contains_session_id(self, sample_metadata):
#         entry = generate_changelog_entry(sample_metadata, 0.45)
#         assert "cl-gen-t" in entry, "Condition must be true"
# 
#     def test_generate_changelog_entry_has_category(self, sample_metadata):
#         entry = generate_changelog_entry(sample_metadata, 0.45)
#         # commit message starts with 'feat' → Added
#         assert ", "Condition must be true"
# 
#     def test_fix_commit_produces_fixed_category(self, sample_metadata):
#         sample_metadata["commit_message"] = "fix: broken login"
#         entry = generate_changelog_entry(sample_metadata, 0.45)
#         assert ", "Condition must be true"
# 
#     def test_generic_commit_produces_changed_category(self, sample_metadata):
#         sample_metadata["commit_message"] = "chore: update deps"
#         entry = generate_changelog_entry(sample_metadata, 0.45)
#         assert ", "Condition must be true"
# 
#     def test_lists_modified_files(self, sample_metadata):
#         entry = generate_changelog_entry(sample_metadata, 0.45)
#         assert "src/auth/routes.py" in entry, "Condition must be true"
# 
#     def test_truncates_long_file_lists(self, sample_metadata):
#         sample_metadata["files_changed"] = [f"file{i}.py" for i in range(10)]
#         entry = generate_changelog_entry(sample_metadata, 0.45)
#         assert "… and 5 more files" in entry, "Condition must be true"
#         assert "new feature" in content, "Content must not be empty"
#         assert content.index("new feature") < content.index(", "Content must not be empty"
# class TestChangelogUpdate:
# 
#     def test_insert_after_unreleased_marker(self, tmp_path):
#         changelog = tmp_path / "CHANGELOG.md"
#         changelog.write_text(
#         changelog.write_text(
#             "# Changelog\n\n## [Unreleased]\n\n## [1.0.0]\n- old\n",
#             encoding="utf-8",
#         )
#         result = update_changelog(
#             "\n### Added (session abc — 2026-03-13)\n- new feature\n",
#             changelog,
#         )
#         assert result is True, "Result must not be empty"
#         content = changelog.read_text(encoding="utf-8")
#         assert "new feature" in content, "Content must not be empty"
#         assert content.index("new feature") < content.index(", "Content must not be empty"
#     def test_returns_false_when_no_unreleased(self, tmp_path):
#         changelog = tmp_path / "CHANGELOG.md"
#         changelog.write_text("# Changelog\n\n## [1.0.0]\n", encoding="utf-8")
#         result = update_changelog("### Added\n- entry\n", changelog)
#         assert result is False, "Result must not be empty"
# 
#     def test_returns_false_when_file_missing(self, tmp_path):
#         result = update_changelog("### Added\n", tmp_path / "missing.md")
#         assert result is False, "Result must not be empty"
# 
#     def test_session_exists_in_changelog(self, tmp_path):
#         changelog = tmp_path / "CHANGELOG.md"
#         changelog.write_text(
#         changelog.write_text(
#             "# Changelog\n\n## [Unreleased]\n\n### Added (session abcdef12)\n- entry\n",
#             encoding="utf-8",
#         )
#         assert session_exists_in_changelog("abcdef1234567890", changelog) is True
#         assert session_exists_in_changelog("zzzzzzzzz", changelog) is False
#     def test_preserves_existing_content(self, tmp_path):
#         changelog = tmp_path / "CHANGELOG.md"
#         original = (
#         original = (
#             "# Changelog\n\n## [Unreleased]\n\n"
#             "### Fixed\n- existing fix\n\n## [1.0.0]\n- v1 entry\n"
#         )
#         changelog.write_text(original, encoding="utf-8")
#         update_changelog("\n### Added (session test)\n- new\n", changelog)
#         content = changelog.read_text(encoding="utf-8")
#         assert "existing fix" in content, "Content must not be empty"
#         assert "v1 entry" in content, "Content must not be empty"
#         assert "new" in content, "Content must not be empty"
