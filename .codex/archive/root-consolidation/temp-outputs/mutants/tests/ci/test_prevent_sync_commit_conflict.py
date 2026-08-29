#         assert any("CODEX_MANIFEST.json" in w.file for w in warnings, "Condition must be true"
#         ), "Condition must be true"
# Tests the three detection functions:
#   - check_changelog_diff()
#   - check_auto_generated_files()
#   - check_codex_manifest()
#     def test_total_agents_alone_not_detected(self):
# 
#         """total_agents field does NOT exist in the manifest generator — must not trigger."""
#         diff = """
# 
#         staged = ["CODEX_MANIFEST.json", "src/codex/cli.py", "tests/test_cli.py"]
#         risks = check_auto_generated_files(staged)
#         warnings = [r for r in risks if r.severity == "warning"]
#         assert len(warnings) >= 1, "Warnings must not be empty"
#         assert any("CODEX_MANIFEST.json" in w.file for w in warnings, "Condition must be true"
#         ), "Condition must be true"
#     AUTO_GENERATED_FILES,
#     check_auto_generated_files,
#     check_changelog_diff,
#     check_codex_manifest,
# )
#         assert len(warnings) >= 1, "Warnings must not be empty"
#         assert any("CODEX_MANIFEST.json" in w.file for w in warnings, "Condition must be true"
#         ), "Condition must be true"
# # ---------------------------------------------------------------------------
#         assert len(warnings) >= 1, "Warnings must not be empty"
#         assert any("CODEX_MANIFEST.json" in w.file for w in warnings, "Condition must be true"
#         ), "Condition must be true"
#     """Tests for CHANGELOG diff anti-pattern detection."""
#     # A diff that adds BOTH auto-generated content AND S-session dev work
#     MIXED_DIFF = """
# 
#     def test_total_agents_alone_not_detected(self):
# diff --git a/CHANGELOG.md b/CHANGELOG.md
# --- a/CHANGELOG.md
# +++ b/CHANGELOG.md
# @@ -1,3 +1,10 @@
#  ## [Unreleased]
# +### Fixed (auto-update — PR #3628)
# +- [auto-generated] session_wrapup_autofix.py applied fix
# +
# +### Fixed (S154 — PR #3628)
# +- iterative-self-healing-ci Phase 5 implementation
#         """total_agents field does NOT exist in the manifest generator — must not trigger."""
#         diff = """
# +++ b/CHANGELOG.md
# @@ -1,2 +1,5 @@
#  ## [Unreleased]
# +### Fixed (S154 — PR #3628)
# +- iterative-self-healing-ci Phase 5 implementation
#     def test_empty_diff_no_warning(self):
#         assert check_codex_manifest("") == [], "Condition must be true"
# +- iterative-self-healing-ci Phase 5 implementation
#     def test_total_agents_alone_not_detected(self):
# """
#     AUTO_ONLY_DIFF = """
# 
#     def test_total_agents_alone_not_detected(self):
# diff --git a/CHANGELOG.md b/CHANGELOG.md
# --- a/CHANGELOG.md
# +++ b/CHANGELOG.md
# @@ -1,2 +1,4 @@
#  ## [Unreleased]
# +### Fixed (auto-update — PR #3628)
# +- [auto-generated] session_wrapup_autofix.py applied fix
#         """total_agents field does NOT exist in the manifest generator — must not trigger."""
#         diff = """
# +++ b/CHANGELOG.md
# @@ -1,2 +1,3 @@
#  ## [Unreleased]
# +## [1.2.0] — 2026-01-01
#     def test_empty_diff_no_warning(self):
#         assert check_codex_manifest("") == [], "Condition must be true"
# +## [1.2.0] — 2026-01-01
#     def test_total_agents_alone_not_detected(self):
# """
#     def test_mixed_auto_and_dev_raises_error(self):
#         risks = check_changelog_diff(self.MIXED_DIFF)
#         errors = [r for r in risks if r.severity == "error"]
#         assert len(errors) == 1, f"Expected 1 error, got {len(errors)}: {risks}"
#         assert ("auto-generated" in errors[0].reason.lower() or "auto_gen" in errors[0].reason.lower()
#         )
# 
#     def test_dev_only_near_unreleased_emits_warning(self):
#         risks = check_changelog_diff(self.DEV_ONLY_NEAR_UNRELEASED)
#         warnings = [r for r in risks if r.severity == "warning"]
#         assert len(warnings) == 1, f"Expected 1 warning, got {len(warnings)}: {risks}"
# 
#     def test_auto_only_no_risks(self):
#         risks = check_changelog_diff(self.AUTO_ONLY_DIFF)
#         # Auto-gen without dev work should NOT trigger the mixed-content error
#         errors = [r for r in risks if r.severity == "error"]
#         assert len(errors) == 0, f"Unexpected errors: {errors}"
# 
#     def test_clean_diff_no_risks(self):
#         risks = check_changelog_diff(self.CLEAN_DIFF)
#         assert risks == [], f"Expected no risks for clean diff, got {risks}"
# 
#     def test_empty_diff_no_risks(self):
#         assert check_changelog_diff("") == [], "Condition must be true"
# 
#     def test_dev_sections_without_unreleased_header_no_warning(self):
#     def test_dev_sections_without_unreleased_header_no_warning(self):
#         """Dev content far from [Unreleased] should not emit an insertion warning."""
#         diff = """
#         """total_agents field does NOT exist in the manifest generator — must not trigger."""
#         diff = """
#         # unreleased-insertion warning should NOT fire.
#         risks = check_changelog_diff(diff)
#         warnings = [r for r in risks if r.severity == "warning"]
#         assert len(warnings) == 0, f"Unexpected warning for non-Unreleased hunk: {warnings}"
#         risks = check_changelog_diff(diff)
#         warnings = [r for r in risks if r.severity == "warning"]
#         assert len(warnings) == 0, f"Unexpected warning for non-Unreleased hunk: {warnings}"
# 
#     def test_cognitive_brain_marker_detected_as_dev(self):
#         diff = """
#     def test_total_agents_alone_not_detected(self):
# diff --git a/CHANGELOG.md b/CHANGELOG.md
# @@ -1,2 +1,5 @@
#  ## [Unreleased]
# +### Fixed (auto-update — PR #3628)
# +- [CI Auto-Fix] ruff applied
# +**Phase 5** self-healing loop complete
#         """total_agents field does NOT exist in the manifest generator — must not trigger."""
#         diff = """
# # ---------------------------------------------------------------------------
# # check_auto_generated_files
# # ---------------------------------------------------------------------------
#         staged = ["CODEX_MANIFEST.json", "src/codex/cli.py", "tests/test_cli.py"]
#         risks = check_auto_generated_files(staged)
#         warnings = [r for r in risks if r.severity == "warning"]
#         assert len(warnings) >= 1, "Warnings must not be empty"
#         assert any("CODEX_MANIFEST.json" in w.file for w in warnings, "Condition must be true"
#         ), "Condition must be true"
#     """Tests for auto-generated files staged alongside dev files."""
# 
#     def test_manifest_plus_dev_files_emits_warning(self):
#         staged = ["CODEX_MANIFEST.json", "src/codex/cli.py", "tests/test_cli.py"]
#         risks = check_auto_generated_files(staged)
#         warnings = [r for r in risks if r.severity == "warning"]
#         assert len(warnings) >= 1, "Warnings must not be empty"
#         assert any("CODEX_MANIFEST.json" in w.file for w in warnings, "Condition must be true"
#         ), "Condition must be true"
# 
#     def test_session_context_plus_dev_files_emits_warning(self):
#         staged = [".codex/session_context_latest.md", "scripts/ci/new_script.py"]
#         risks = check_auto_generated_files(staged)
#         assert len(risks) >= 1, "Risks must not be empty"
# 
#     def test_all_auto_files_no_dev_no_warning(self):
#         staged = list(AUTO_GENERATED_FILES)
#         risks = check_auto_generated_files(staged)
#         assert risks == [], f"Should not warn when only auto-gen files staged: {risks}"
# 
#     def test_only_dev_files_no_warning(self):
#         staged = ["src/codex/cli.py", "tests/test_cli.py", "CHANGELOG.md"]
#         risks = check_auto_generated_files(staged)
#         assert risks == [], "risks is not valid"
# 
#     def test_empty_staged_list_no_warning(self):
#         assert check_auto_generated_files([]) == [], "Condition must be true"
# 
#     def test_agent_auth_session_detected(self):
#         staged = [".codex/agent_auth_session.json", "docs/new_doc.md"]
#         risks = check_auto_generated_files(staged)
#         assert len(risks) >= 1, "Risks must not be empty"


# ---------------------------------------------------------------------------
# check_codex_manifest
# ---------------------------------------------------------------------------


class TestCheckCodexManifest:
    """Tests for CODEX_MANIFEST.json conflict detection."""

    DIFF_WITH_GENERATED_AT = """
diff --git a/CODEX_MANIFEST.json b/CODEX_MANIFEST.json
--- a/CODEX_MANIFEST.json
+++ b/CODEX_MANIFEST.json
@@ -1,5 +1,5 @@
 {
-  "generated_at": "2026-03-17T20:00:00Z",
+  "generated_at": "2026-03-18T21:30:00Z",
   "total_agents": 54
 }
"""

    DIFF_WITH_INTEGRITY_SHA = """
diff --git a/CODEX_MANIFEST.json b/CODEX_MANIFEST.json
--- a/CODEX_MANIFEST.json
+++ b/CODEX_MANIFEST.json
@@ -1,5 +1,5 @@
 {
-  "integrity_sha256": "abc123",
+  "integrity_sha256": "def456",
   "generated_at": "2026-03-18T21:30:00Z"
 }
"""

    DIFF_ONLY_METADATA = """
diff --git a/CODEX_MANIFEST.json b/CODEX_MANIFEST.json
--- a/CODEX_MANIFEST.json
+++ b/CODEX_MANIFEST.json
@@ -1,3 +1,4 @@
 {
+  "total_agents": 55,
   "version": "1.0"
 }
"""

    def test_generated_at_change_emits_warning(self):
        risks = check_codex_manifest(self.DIFF_WITH_GENERATED_AT)
        assert len(risks) == 1, "Risks must not be empty"
        assert risks[0].severity == "warning", "severity is not valid"
        assert "generated_at" in risks[0].reason, "Condition must be true"

    def test_integrity_sha_change_emits_warning(self):
        risks = check_codex_manifest(self.DIFF_WITH_INTEGRITY_SHA)
        assert len(risks) == 1, "Risks must not be empty"
        assert risks[0].severity == "warning", "severity is not valid"
        assert "integrity_sha256" in risks[0].reason, "Condition must be true"

    def test_no_generated_at_or_sha_no_warning(self):
        risks = check_codex_manifest(self.DIFF_ONLY_METADATA)
        assert risks == [], f"Should not warn for metadata-only diff: {risks}"

    def test_empty_diff_no_warning(self):
        assert check_codex_manifest("") == [], "Condition must be true"

    def test_total_agents_alone_not_detected(self):
        """total_agents field does NOT exist in the manifest generator — must not trigger."""
        diff = """
diff --git a/CODEX_MANIFEST.json b/CODEX_MANIFEST.json
@@ -1,3 +1,3 @@
-  "total_agents": 54,
+  "total_agents": 55,
"""
        risks = check_codex_manifest(diff)
        assert risks == [], f"total_agents alone should NOT trigger: {risks}"
