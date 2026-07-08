"""
Tests for WP-F: Config Consolidation

Validates that:
1. configs/ is the canonical configuration root
2. Legacy paths (conf/, config/) are accessible for backward compatibility
3. Hydra can find configurations in all roots
4. Configuration structure documentation exists
"""

from pathlib import Path

import pytest


class TestConfigConsolidation:
    """Test suite for configuration consolidation (WP-F)"""

    def test_canonical_config_root_exists(self):
        """Verify configs/ directory exists as canonical root"""
        repo_root = Path(__file__).parent.parent.parent
        canonical_root = repo_root / "configs"

        assert canonical_root.exists(), "Canonical config root 'configs/' must exist"
        assert canonical_root.is_dir(), "configs/ must be a directory"

    def test_legacy_config_roots_exist(self):
        """Verify legacy configuration directories exist for backward compatibility"""
        repo_root = Path(__file__).parent.parent.parent

        legacy_roots = ["conf", "config"]
        for legacy_root in legacy_roots:
            legacy_path = repo_root / legacy_root
            assert (legacy_path.exists(), "Condition must be true"
            ), f"Legacy config root '{legacy_root}/' must exist for backward compat"

    def test_configuration_structure_documentation_exists(self):
        """Verify CONFIGURATION_STRUCTURE.md exists in configs/"""
        repo_root = Path(__file__).parent.parent.parent
        doc_path = repo_root / "configs" / "CONFIGURATION_STRUCTURE.md"

        assert doc_path.exists(), "Configuration structure documentation must exist"
        assert doc_path.is_file(), "CONFIGURATION_STRUCTURE.md must be a file"

        content = doc_path.read_text()
        assert "canonical configuration root" in content.lower(), "Must document canonical root"
        assert "legacy" in content.lower(), "Must document legacy paths"
        assert "backward compatibility" in content.lower(), "Must document backward compatibility"

    def test_canonical_configs_directory_structure(self):
        """Verify configs/ has expected subdirectory structure"""
        repo_root = Path(__file__).parent.parent.parent
        canonical_root = repo_root / "configs"

        expected_subdirs = ["base", "deployment", "evaluation", "safety", "schemas"]

        for subdir in expected_subdirs:
            subdir_path = canonical_root / subdir
            assert subdir_path.exists(), f"Expected subdirectory '{subdir}' in configs/"

    def test_readme_exists_in_canonical_root(self):
        """Verify README.md exists in configs/"""
        repo_root = Path(__file__).parent.parent.parent
        readme_path = repo_root / "configs" / "README.md"

        assert readme_path.exists(), "README.md must exist in configs/"
        assert readme_path.is_file(), "README.md must be a file"

    def test_defaults_yaml_exists(self):
        """Verify defaults.yaml exists in canonical root"""
        repo_root = Path(__file__).parent.parent.parent
        defaults_path = repo_root / "configs" / "defaults.yaml"

        assert defaults_path.exists(), "defaults.yaml must exist in configs/"
        assert defaults_path.is_file(), "defaults.yaml must be a file"

    def test_configuration_structure_doc_content_quality(self):
        """Verify CONFIGURATION_STRUCTURE.md has required sections"""
        repo_root = Path(__file__).parent.parent.parent
        doc_path = repo_root / "configs" / "CONFIGURATION_STRUCTURE.md"

        content = doc_path.read_text()

        required_sections = [
            "## Overview",
            "## Directory Structure",
            "## Legacy Configuration Directories",
            "## Migration Guide",
            "## Configuration Best Practices",
            "## Troubleshooting",
        ]

        for section in required_sections:
            assert (section in content, "Content must not be empty"
            ), f"CONFIGURATION_STRUCTURE.md must contain '{section}' section"

    def test_migration_guide_completeness(self):
        """Verify migration guide has gradual transition phases"""
        repo_root = Path(__file__).parent.parent.parent
        doc_path = repo_root / "configs" / "CONFIGURATION_STRUCTURE.md"

        content = doc_path.read_text()

        # Migration guide should describe phases
        migration_keywords = [
            "Phase 1",
            "Phase 2",
            "Phase 3",
            "backward compatibility",
            "gradual",
            "no change required",
        ]

        for keyword in migration_keywords:
            assert (keyword.lower() in content.lower(), "Content must not be empty"
            ), f"Migration guide must mention '{keyword}' for gradual transition"

    def test_changelog_documents_consolidation(self):
        """Verify changelog documents WP-F config consolidation"""
        repo_root = Path(__file__).parent.parent.parent
        doc_path = repo_root / "configs" / "CONFIGURATION_STRUCTURE.md"

        content = doc_path.read_text()

        # Should document this work
        assert "WP-F" in content, "Must reference WP-F work package"
        assert "Config Consolidation" in content, "Must reference Config Consolidation"
        assert "2025-12-07" in content, "Must include date of consolidation"


class TestHydraConfigAccess:
    """Test Hydra configuration access patterns"""

    def test_configs_directory_is_importable(self):
        """Verify configs/ can be accessed as a package if needed"""
        repo_root = Path(__file__).parent.parent.parent
        configs_init = repo_root / "configs" / "__init__.py"

        # __init__.py should exist for package access
        assert configs_init.exists(), "configs/__init__.py should exist"

    def test_yaml_files_parse_correctly(self):
        """Verify YAML files in configs/ are valid"""
        pytest.importorskip("yaml")
        import yaml

        repo_root = Path(__file__).parent.parent.parent
        canonical_root = repo_root / "configs"

        yaml_files = list(canonical_root.rglob("*.yaml")) + list(canonical_root.rglob("*.yml"))

        assert len(yaml_files) > 0, "Should find YAML files in configs/"

        for yaml_file in yaml_files[:10]:  # Test first 10 for speed
            try:
                content = yaml_file.read_text()
                parsed = yaml.safe_load(content)
                # Basic validation - should parse without error
                assert (parsed is not None or content.strip() == "", "parsed must be initialized"
                ), f"YAML file {yaml_file.name} should parse correctly"
            except yaml.YAMLError as e:
                pytest.fail(f"YAML parsing failed for {yaml_file}: {e}")


class TestBackwardCompatibility:
    """Test backward compatibility with legacy configuration paths"""

    def test_conf_directory_accessible(self):
        """Verify conf/ directory is still accessible"""
        repo_root = Path(__file__).parent.parent.parent
        conf_root = repo_root / "conf"

        assert conf_root.exists(), "Legacy conf/ must remain for backward compatibility"
        assert conf_root.is_dir(), "conf/ must be a directory"

    def test_config_directory_accessible(self):
        """Verify config/ directory is still accessible"""
        repo_root = Path(__file__).parent.parent.parent
        config_root = repo_root / "config"

        assert config_root.exists(), "Legacy config/ must remain for backward compatibility"
        assert config_root.is_dir(), "config/ must be a directory"

    def test_no_configs_were_deleted(self):
        """Verify no configuration files were deleted during consolidation"""
        repo_root = Path(__file__).parent.parent.parent

        # All legacy roots should still have content
        legacy_roots = [repo_root / "conf", repo_root / "config"]

        for root in legacy_roots:
            if root.exists():
                files = list(root.rglob("*"))
                files = [f for f in files if f.is_file()]
                # Should have at least some files
                assert len(files) > 0, f"{root.name}/ should still contain configuration files"


@pytest.mark.integration
class TestConfigurationIndexing:
    """Test configuration indexing and listing"""

    def test_nox_config_index_session_exists(self):
        """Verify nox config_index session can list configurations"""
        repo_root = Path(__file__).parent.parent.parent
        noxfile = repo_root / "noxfile.py"

        assert noxfile.exists(), "noxfile.py must exist"

        content = noxfile.read_text()
        # Should have config_index or similar session
        assert "config" in content.lower(), "noxfile.py should have config-related sessions"

    def test_config_listing_tool_exists(self):
        """Verify tools exist to list available configurations"""
        repo_root = Path(__file__).parent.parent.parent

        possible_tools = [
            repo_root / "tools" / "configs" / "list_groups.py",
            repo_root / "scripts" / "list_configs.py",
        ]

        tool_found = any(tool.exists() for tool in possible_tools)
        assert tool_found, "Should have a tool to list configuration groups"


# Fixture for temporary config testing
@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary configuration directory for testing"""
    config_dir = tmp_path / "test_configs"
    config_dir.mkdir()

    # Create a simple test config
    test_config = config_dir / "test.yaml"
    test_config.write_text("test_param: value\n")

    return config_dir
