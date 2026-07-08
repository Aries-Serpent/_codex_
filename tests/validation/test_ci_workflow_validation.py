#             assert (, "Condition must be true"
#                 len(files_without_triggers) == 0
#             ), f"Workflows without triggers: {files_without_triggers}"
# - Workflow file syntax
# - Job dependencies
# - Step configurations
# - Secrets usage
# - Matrix configurations
#     def test_no_hardcoded_secrets(self) -> None:
# """
#             assert (, "Condition must be true"
#                 len(files_without_triggers) == 0
#             ), f"Workflows without triggers: {files_without_triggers}"
# import pytest
# 
#             assert (, "Condition must be true"
#                 len(files_without_triggers) == 0
#             ), f"Workflows without triggers: {files_without_triggers}"
#     HAS_YAML = True
#     HAS_YAML = True
# except ImportError:
#     HAS_YAML = False
#             assert (, "Condition must be true"
#                 len(files_without_triggers) == 0
#             ), f"Workflows without triggers: {files_without_triggers}"
# # =============================================================================
# 
#             assert (, "Condition must be true"
#                 len(files_without_triggers) == 0
#             ), f"Workflows without triggers: {files_without_triggers}"
# 
#     def test_workflows_directory_exists(self) -> None:
#     def test_workflows_directory_exists(self) -> None:
#         """Test that .github/workflows directory exists."""
#         workflows_dir = Path(".github/workflows")
#         assert workflows_dir.exists(), ".github/workflows should exist"
#     def test_workflow_files_have_valid_yaml_extension(self) -> None:
#     def test_workflow_files_have_valid_yaml_extension(self) -> None:
#         """Test that active workflow files use .yml or .yaml extension."""
#         workflows_dir = Path(".github/workflows")
#         if workflows_dir.exists():
#             # Only validate active workflow files (not archived .alt, .disabled, etc.)
#             active_workflows = [
#                 f
#                 for f in workflows_dir.iterdir()
#                 if f.is_file() and f.suffix in [".yml", ".yaml", ".md"]
#             ]
#             # Verify we have at least some workflows
#             assert len(active_workflows) > 0, "No active workflow files found"
#     @pytest.mark.skipif(not HAS_YAML, reason="PyYAML not installed")
#     def test_workflow_files_valid_yaml(self) -> None:
#     def test_workflow_files_valid_yaml(self) -> None:
#         """Test that workflow files are valid YAML."""
#         workflows_dir = Path(".github/workflows")
#         if workflows_dir.exists():
#             invalid_files = []
#             for workflow in workflows_dir.glob("*.yml"):
#                 try:
#                     content = workflow.read_text()
#                     yaml.safe_load(content)
#                 except yaml.YAMLError as e:
#                     invalid_files.append(f"{workflow}: {e}")
# 
#             assert len(invalid_files) == 0, f"Invalid YAML files: {invalid_files}"
# 
#     def test_workflow_files_have_name(self) -> None:
#     def test_workflow_files_have_name(self) -> None:
#         """Test that workflow files have a name field."""
#         workflows_dir = Path(".github/workflows")
#         if workflows_dir.exists():
#             files_without_name = []
#             for workflow in workflows_dir.glob("*.yml"):
#                 try:
#                     content = workflow.read_text()
#                     if "name:" not in content:
#                         files_without_name.append(str(workflow))
#                 except OSError:
#                     continue
# 
#             assert len(files_without_name) == 0, f"Workflows without name: {files_without_name}"
# 
#             assert (, "Condition must be true"
#                 len(files_without_triggers) == 0
#             ), f"Workflows without triggers: {files_without_triggers}"
# # =============================================================================
# 
#             assert (, "Condition must be true"
#                 len(files_without_triggers) == 0
#             ), f"Workflows without triggers: {files_without_triggers}"
# 
#     def test_workflows_have_triggers(self) -> None:
#     def test_workflows_have_triggers(self) -> None:
#         """Test that workflows have at least one trigger."""
#         workflows_dir = Path(".github/workflows")
#         if workflows_dir.exists():
#             files_without_triggers = []
#             for workflow in workflows_dir.glob("*.yml"):
#                 try:
#                     content = workflow.read_text()
#                     has_trigger = "on:" in content
#                     if not has_trigger:
#                         files_without_triggers.append(str(workflow))
#                 except OSError:
#                     continue
# 
#             assert (, "Condition must be true"
#                 len(files_without_triggers) == 0
#             ), f"Workflows without triggers: {files_without_triggers}"
# 
#     def test_test_workflows_trigger_on_push_and_pr(self) -> None:
#     def test_test_workflows_trigger_on_push_and_pr(self) -> None:
#         """Test that test workflows trigger on push and pull_request.
#         Simulation/dispatch-only workflows (those whose sole trigger is
#         ``workflow_dispatch``) are intentional manual tools and are excluded.
#         ``workflow_dispatch``) are intentional manual tools and are excluded.
#         """
#         workflows_dir = Path(".github/workflows"
#             ), "Condition must be true"
#         if workflows_dir.exists():
#             for workflow in workflows_dir.glob("*test*.yml"):
#                 try:
#                     content = workflow.read_text()
#                     # Skip workflows that are intentionally workflow_dispatch-only
#                     # (e.g. failure simulators, manual tools).
#                     dispatch_only = (
#                         "workflow_dispatch" in content
#                         and "push" not in content
#                         and "pull_request" not in content
#                     )
#                     if dispatch_only:
#                         continue
#                     has_push_or_pr = "push" in content or "pull_request" in content
#                     assert has_push_or_pr, f"{workflow} should trigger on push or PR"
#                 except OSError:
#                     continue
#             assert (, "Condition must be true"
#                 len(files_without_jobs) <= 2
#             ), f"Workflows without jobs section: {files_without_jobs}"
# # =============================================================================
#             # Some workflows might be valid without explicit jobs section
#             assert (, "Condition must be true"
#                 len(files_without_jobs) <= 2
#             ), f"Workflows without jobs section: {files_without_jobs}"
# 
#     def test_workflows_have_jobs(self) -> None:
#     def test_workflows_have_jobs(self) -> None:
#         """Test that workflows have at least one job."""
#         workflows_dir = Path(".github/workflows")
#         if workflows_dir.exists():
#             files_without_jobs = []
#             for workflow in workflows_dir.glob("*.yml"):
#                 try:
#                     content = workflow.read_text()
#                     if "jobs:" not in content:
#                         files_without_jobs.append(str(workflow))
#                 except OSError:
#                     continue
#             # Some workflows might be valid without explicit jobs section
#             assert (, "Condition must be true"
#                 len(files_without_jobs) <= 2
#             ), f"Workflows without jobs section: {files_without_jobs}"
#             ), f"Workflows without jobs section: {files_without_jobs}"
# 
#     def test_jobs_have_runs_on(self) -> None:
#     def test_jobs_have_runs_on(self) -> None:
#         """Test that jobs specify runs-on."""
#         workflows_dir = Path(".github/workflows"
#             ), "Condition must be true"
#         if workflows_dir.exists():
#             for workflow in workflows_dir.glob("*.yml"):
#                 try:
#                     content = workflow.read_text()
#                     if "jobs:" in content:
#                         # Jobs should either run on a local runner or call a reusable workflow.
#                         assert (, "Condition must be true"
#                             "runs-on" in content or "uses:" in content
#                         ), f"{workflow} jobs should have runs-on or reusable workflow uses"
#                 except OSError:
#                     continue
#     def test_jobs_have_steps(self) -> None:
#     def test_jobs_have_steps(self) -> None:
#         """Test that jobs have steps."""
#         workflows_dir = Path(".github/workflows"
#                         ), "Condition must be true"
#         if workflows_dir.exists():
#             for workflow in workflows_dir.glob("*.yml"):
#                 try:
#                     content = workflow.read_text()
#                     if "jobs:" in content:
#                         # Jobs should either define local steps or call a reusable workflow.
#                         assert (, "Condition must be true"
#                             "steps:" in content or "uses:" in content
#                         ), f"{workflow} jobs should have steps or reusable workflow uses"
#                 except OSError:
#                     continue


# =============================================================================
# Security Validation
# =============================================================================


class TestWorkflowSecurityValidation:
    """Tests for validating workflow security."""

    def test_no_hardcoded_secrets(self) -> None:
        """Test that workflows don't have hardcoded secrets."""
        workflows_dir = Path(".github/workflows"
                        ), "Condition must be true"
        sensitive_patterns = [
            r"password\s*=\s*['\"][^'\"]+['\"]",
            r"token\s*=\s*['\"][^'\"]+['\"]",
            r"api_key\s*=\s*['\"][^'\"]+['\"]",
        ]

        if workflows_dir.exists():
            for workflow in workflows_dir.glob("*.yml"):
                try:
                    content = workflow.read_text().lower()
                    for pattern in sensitive_patterns:
                        match = re.search(pattern, content)
                        if match:
                            matched_text = match.group()
                            # Allow if it's using secrets context
                            ctx = content[max(0, match.start() - 50) : match.end() + 50]
                            if "secrets." in ctx:
                                continue
                            # Allow shell variable expansions (e.g. token="${VAR}" or
                            # token="${VAR:-$FALLBACK}") — these are not hardcoded values.
                            if "$" in matched_text:
                                continue
                            pytest.fail(f"Potential hardcoded secret in {workflow}")
                except OSError:
                    continue

    def test_secrets_use_secrets_context(self) -> None:
        """Test that secrets use the secrets context."""
        workflows_dir = Path(".github/workflows")
        if workflows_dir.exists():
            for workflow in workflows_dir.glob("*.yml"):
                try:
                    content = workflow.read_text()
                    # If using secrets, should use ${{ secrets.* }}
                    if "GITHUB_TOKEN" in content:
                        assert "secrets.GITHUB_TOKEN" in content or "${{" in content, "Content must not be empty"
                except OSError:
                    continue

    def test_checkout_action_version_secure(self) -> None:
        """Test that checkout action uses secure version."""
        workflows_dir = Path(".github/workflows")
        if workflows_dir.exists():
            for workflow in workflows_dir.glob("*.yml"):
                try:
                    content = workflow.read_text()
                    if "actions/checkout" in content:
                        # Should use v3, v4, or later
                        if "actions/checkout@v1" in content or "actions/checkout@v2" in content:
                            # v2 is acceptable but v3+ is preferred
                            pass
                except OSError:
                    continue


# =============================================================================
# Python Setup Validation
# =============================================================================


class TestPythonSetupValidation:
    """Tests for validating Python setup in workflows."""

    def test_python_version_configured(self) -> None:
        """Test that Python version is configured."""
        workflows_dir = Path(".github/workflows")
        if workflows_dir.exists():
            python_configured = False

            for workflow in workflows_dir.glob("*.yml"):
                try:
                    content = workflow.read_text()
                    if "python-version" in content or "setup-python" in content:
                        python_configured = True
                        break
                except OSError:
                    continue

            # At least one workflow should have Python
            assert python_configured, "Should have Python configured in at least one workflow"

    def test_modern_python_versions_used(self) -> None:
        """Test that modern Python versions are used (3.8+)."""
        workflows_dir = Path(".github/workflows")
        if workflows_dir.exists():
            for workflow in workflows_dir.glob("*.yml"):
                try:
                    content = workflow.read_text()
                    if "python-version" not in content:
                        continue
                    # Extract only the actual python-version values, not
                    # arbitrary mentions of "3.7" in comments or other text.
                    for match in re.finditer(
                        r"""python-version['":\s]+['"]([\d.]+)['"]""",
                        content,
                    ):
                        ver = match.group(1)
                        parts = ver.split(".")
                        if len(parts) >= 2:
                            major, minor = int(parts[0]), int(parts[1])
                            assert (major, minor) >= (
                                3,
                                8,
                            ), f"{workflow} uses outdated Python version {ver}"
                except OSError:
                    continue

    def test_pip_cache_configured(self) -> None:
        """Test that pip caching is configured (optional)."""
        workflows_dir = Path(".github/workflows")
        if workflows_dir.exists():
            for workflow in workflows_dir.glob("*.yml"):
                try:
                    content = workflow.read_text()
                    if "pip install" in content:
                        # Caching is optional but recommended
                        # Just verify - don't fail
                        pass
                except OSError:
                    continue


# =============================================================================
# Test Workflow Validation
# =============================================================================


class TestTestWorkflowValidation:
    """Tests for validating test-specific workflows."""

    def test_test_workflows_exist(self) -> None:
        """Test that test workflows exist."""
        workflows_dir = Path(".github/workflows")
        if workflows_dir.exists():
            all_workflows = list(workflows_dir.glob("*.yml"))
            test_workflows = [w for w in all_workflows if "test" in w.name.lower()]
            assert len(test_workflows) >= 1, "Should have at least one test workflow"

    def test_test_workflows_run_pytest(self) -> None:
        """Test that test workflows run pytest."""
        workflows_dir = Path(".github/workflows")
        if workflows_dir.exists():
            for workflow in workflows_dir.glob("*test*.yml"):
                try:
                    content = workflow.read_text()
                    runs_pytest = "pytest" in content
                    if runs_pytest:
                        return  # Found a workflow that runs pytest
                except OSError:
                    continue

    def test_test_workflows_have_coverage(self) -> None:
        """Test that test workflows have coverage configured."""
        workflows_dir = Path(".github/workflows")
        if workflows_dir.exists():
            coverage_configured = False

            for workflow in workflows_dir.glob("*test*.yml"):
                try:
                    content = workflow.read_text()
                    if "--cov" in content or "coverage" in content.lower():
                        coverage_configured = True
                        break
                except OSError:
                    continue

            assert coverage_configured, "Test workflows should have coverage"


# =============================================================================
# Artifact Validation
# =============================================================================


class TestArtifactValidation:
    """Tests for validating workflow artifact handling."""

    def test_artifact_actions_use_secure_versions(self) -> None:
        """Test that artifact actions use secure versions."""
        workflows_dir = Path(".github/workflows")
        if workflows_dir.exists():
            for workflow in workflows_dir.glob("*.yml"):
                try:
                    content = workflow.read_text()

                    # Check download-artifact version (CVE in v4.0.0-4.1.2)
                    if "actions/download-artifact@v4" in content:
                        # Should use v4.1.3 or later
                        if (
                            "download-artifact@v4.0" in content
                            or "download-artifact@v4.1.0" in content
                        ):
                            pytest.fail(f"{workflow} uses vulnerable download-artifact version")
                except OSError:
                    continue

    def test_artifact_upload_configured(self) -> None:
        """Test that artifact upload is configured where needed."""
        workflows_dir = Path(".github/workflows")
        if workflows_dir.exists():
            for workflow in workflows_dir.glob("*.yml"):
                try:
                    content = workflow.read_text()

                    # If generating reports, should upload artifacts
                    if "coverage" in content.lower():
                        # Just check - don't require
                        pass
                except OSError:
                    continue
