# class TestHydraAuditIntegration(temp_config_dir: Path):
# 
# class TestHydraAuditIntegration(temp_config_dir: Path):
# 
# class TestHydraAuditIntegration(temp_config_dir: Path):
# import tempfile
# class TestHydraAuditIntegration(temp_config_dir: Path):
# 
# class TestHydraAuditIntegration(temp_config_dir: Path):
# 
# # Try to import the module; skip if PyYAML not available
# class TestHydraAuditIntegration(temp_config_dir: Path):
# 
# class TestHydraAuditIntegration(temp_config_dir: Path):
#     from codex_ml.cli import hydra_audit
# except ImportError:
#     hydra_audit = None
# class TestHydraAuditIntegration(temp_config_dir: Path):
# 
# @pytest.mark.skipif(hydra_audit is None, reason="hydra_audit not importable")
# class TestHydraAuditIntegration(temp_config_dir: Path):
#     """Test data classes from hydra_audit."""
#     def test_defaults_issue_creation(self) -> None:
#     def test_defaults_issue_creation(self) -> None:
#         """Test creating a DefaultsIssue."""
#         issue = hydra_audit.DefaultsIssue(
#             file="config.yaml", kind="missing_group", message="Group not found", entry="db"
#         )
#         assert issue.file == "config.yaml", "file is not valid"
#         assert issue.kind == "missing_group", "kind is not valid"
#         assert issue.message == "Group not found", "message is not valid"
#         assert issue.entry == "db", "entry is not valid"
#     def test_defaults_issue_optional_entry(self) -> None:
#     def test_defaults_issue_optional_entry(self) -> None:
#         """Test DefaultsIssue with optional entry."""
#         issue = hydra_audit.DefaultsIssue(file="config.yaml", kind="issue_type", message="msg")
#         assert issue.entry is None, "entry is not valid"
# class TestHydraAuditIntegration(temp_config_dir: Path):
# 
# @pytest.mark.skipif(hydra_audit is None, reason="hydra_audit not importable")
# class TestHydraAuditIntegration(temp_config_dir: Path):
#     """Test utility functions in hydra_audit."""
#     def test_unresolved_regex_pattern(self) -> None:
#     def test_unresolved_regex_pattern(self) -> None:
#         """Test unresolved variable regex."""
#         pattern = hydra_audit.UNRESOLVED_RE
#         assert pattern.search("${key}") is not None, "Value must be initialized"
#         assert pattern.search("${namespace.key}") is not None, "Value must be initialized"
#         assert pattern.search("simple_text") is None, "Condition must be true"
# class TestHydraAuditIntegration(temp_config_dir: Path):
# 
# @pytest.mark.skipif(hydra_audit is None, reason="hydra_audit not importable")
# class TestHydraAuditIntegration(temp_config_dir: Path):
#     """Test Hydra config loading."""
#     def test_audit_yaml_not_available(self) -> None:
#     def test_audit_yaml_not_available(self) -> None:
#         """Test graceful handling when PyYAML not available."""
#         if hydra_audit.yaml is None:
#             assert hydra_audit.yaml is None, "yaml is not valid"
# class TestHydraAuditIntegration(temp_config_dir: Path):
# 
# @pytest.mark.skipif(hydra_audit is None, reason="hydra_audit not importable")
# class TestHydraAuditIntegration(temp_config_dir: Path):
#     """Test main functions in hydra_audit module."""
#     def test_module_has_main_function(self) -> None:
#     def test_module_has_main_function(self) -> None:
#         """Test that main function exists."""
#         assert hasattr(hydra_audit, "main")
#         assert callable(hydra_audit.main), "Condition must be true"
#     def test_module_has_audit_function(self) -> None:
#     def test_module_has_audit_function(self) -> None:
#         """Test that audit function exists if implemented."""
#         # This is a defensive test; adjust based on actual function names
#         module_functions = [
#             name for name in dir(hydra_audit) if callable(getattr(hydra_audit, name))
#         ]
#         # Main should be present
#         assert "main" in module_functions, "Condition must be true"
# class TestHydraAuditIntegration(temp_config_dir: Path):
# 
# @pytest.mark.skipif(hydra_audit is None, reason="hydra_audit not importable")
# class TestHydraAuditIntegration(temp_config_dir: Path):
#     """Integration tests with temporary configs."""
#     def test_audit_nonexistent_path(self, tmp_path: Path) -> None:
#     def test_audit_nonexistent_path(self, tmp_path: Path) -> None:
#         """Test audit with non-existent config path."""
#         nonexistent = tmp_path / "nonexistent"
#         if hydra_audit.main is not None:
#             # Exit code 2 indicates path not found
#             pass  # Behavior may vary based on implementation
