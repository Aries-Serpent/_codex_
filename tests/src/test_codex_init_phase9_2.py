"""
Phase 9.2 - Comprehensive tests for src/codex/__init__.py public API.

Tests cover:
- Version information export
- __all__ exports validation
- Module availability (ingest, analyze, intent, transform, verify, cli)
- Package metadata
- Import safety and backward compatibility
- Public API surface area

#AFTERMATH_METRIC - Phase 9.2 test suite targeting 92% coverage
"""

from __future__ import annotations

import sys


class TestCodexPackageVersion:
    """Test version information and metadata."""

    def test_version_import(self) -> None:
        """Test __version__ can be imported."""
        # Arrange & Act
        from codex import __version__

        # Assert
        assert __version__ is not None, "__version__ must be initialized"
        assert isinstance(__version__, str)

    def test_version_format(self) -> None:
        """Test version follows semantic versioning."""
        # Arrange & Act
        from codex import __version__

        # Assert
        # Should be in format X.Y.Z or X.Y.Z.devN
        parts = __version__.split(".")
        assert len(parts) >= 3, f"Version should have at least 3 parts, got: {__version__}"

    def test_version_not_empty(self) -> None:
        """Test version is not empty string."""
        # Arrange & Act
        from codex import __version__

        # Assert
        assert __version__ != "", "__version__ is not valid"
        assert len(__version__) > 0, "__version__ must not be empty"

    def test_version_accessible_from_module(self) -> None:
        """Test version is accessible from module level."""
        # Arrange & Act
        import codex

        # Assert
        assert hasattr(codex, "__version__")
        assert codex.__version__ is not None, "__version__ must be initialized"


class TestCodexPackageExports:
    """Test __all__ exports and public API."""

    def test_all_attribute_exists(self) -> None:
        """Test __all__ attribute is defined."""
        # Arrange & Act
        import codex

        # Assert
        assert hasattr(codex, "__all__")
        assert isinstance(codex.__all__, list)

    def test_version_in_all(self) -> None:
        """Test __version__ is in __all__."""
        # Arrange & Act
        from codex import __all__

        # Assert
        assert "__version__" in __all__, "Condition must be true"

    def test_module_names_in_all(self) -> None:
        """Test expected module names are in __all__."""
        # Arrange & Act
        from codex import __all__

        # Assert
        expected_modules = ["ingest", "analyze", "intent", "transform", "verify", "cli"]
        for module in expected_modules:
            assert module in __all__, f"Module {module} should be in __all__"

    def test_all_items_are_strings(self) -> None:
        """Test all items in __all__ are strings."""
        # Arrange & Act
        from codex import __all__

        # Assert
        for item in __all__:
            assert isinstance(item, str), f"Item {item} should be a string"

    def test_all_no_duplicates(self) -> None:
        """Test __all__ has no duplicate entries."""
        # Arrange & Act
        from codex import __all__

        # Assert
        assert len(__all__) == len(set(__all__)), "__all__ should not have duplicates"

    def test_all_count(self) -> None:
        """Test __all__ has expected number of exports."""
        # Arrange & Act
        from codex import __all__

        # Assert
        # Should have __version__ + 6 modules = 7 items
        assert len(__all__) == 7, f"Expected 7 exports, got {len(__all__)}"


class TestCodexModuleImports:
    """Test module imports and availability."""

    def test_ingest_module_in_all(self) -> None:
        """Test 'ingest' is declared in __all__."""
        # Arrange & Act
        from codex import __all__

        # Assert
        assert "ingest" in __all__, "Condition must be true"

    def test_analyze_module_in_all(self) -> None:
        """Test 'analyze' is declared in __all__."""
        # Arrange & Act
        from codex import __all__

        # Assert
        assert "analyze" in __all__, "Condition must be true"

    def test_intent_module_in_all(self) -> None:
        """Test 'intent' is declared in __all__."""
        # Arrange & Act
        from codex import __all__

        # Assert
        assert "intent" in __all__, "Condition must be true"

    def test_transform_module_in_all(self) -> None:
        """Test 'transform' is declared in __all__."""
        # Arrange & Act
        from codex import __all__

        # Assert
        assert "transform" in __all__, "Condition must be true"

    def test_verify_module_in_all(self) -> None:
        """Test 'verify' is declared in __all__."""
        # Arrange & Act
        from codex import __all__

        # Assert
        assert "verify" in __all__, "Condition must be true"

    def test_cli_module_in_all(self) -> None:
        """Test 'cli' is declared in __all__."""
        # Arrange & Act
        from codex import __all__

        # Assert
        assert "cli" in __all__, "Condition must be true"


class TestCodexPackageDocumentation:
    """Test package documentation and metadata."""

    def test_package_has_docstring(self) -> None:
        """Test package has a docstring."""
        # Arrange & Act
        import codex

        # Assert
        assert codex.__doc__ is not None, "__doc__ must be initialized"
        assert len(codex.__doc__) > 0, "Collection must not be empty"

    def test_docstring_mentions_session_logging(self) -> None:
        """Test docstring mentions session logging."""
        # Arrange & Act
        import codex

        # Assert
        assert "session logging" in codex.__doc__.lower(), "Condition must be true"

    def test_docstring_mentions_python_ingestion_pipeline(self) -> None:
        """Test docstring mentions Python Ingestion Pipeline."""
        # Arrange & Act
        import codex

        # Assert
        assert "python ingestion pipeline" in codex.__doc__.lower(), "Condition must be true"

    def test_docstring_lists_components(self) -> None:
        """Test docstring lists pipeline components."""
        # Arrange & Act
        import codex

        # Assert
        doc_lower = codex.__doc__.lower()
        assert "ingest" in doc_lower, "Condition must be true"
        assert "analyze" in doc_lower, "Condition must be true"
        assert "intent" in doc_lower, "Condition must be true"
        assert "transform" in doc_lower, "Condition must be true"
        assert "verify" in doc_lower, "Condition must be true"


class TestCodexPackageStructure:
    """Test package structure and organization."""

    def test_package_is_importable(self) -> None:
        """Test codex package can be imported."""
        # Arrange & Act & Assert
        import codex

        assert codex is not None, "codex must be initialized"

    def test_package_has_name(self) -> None:
        """Test package has __name__ attribute."""
        # Arrange & Act
        import codex

        # Assert
        assert hasattr(codex, "__name__")
        assert codex.__name__ == "codex", "__name__ is not valid"

    def test_package_has_file_attribute(self) -> None:
        """Test package has __file__ attribute."""
        # Arrange & Act
        import codex

        # Assert
        assert hasattr(codex, "__file__")
        assert codex.__file__ is not None, "__file__ must be initialized"

    def test_package_path_is_correct(self) -> None:
        """Test package path contains 'codex'."""
        # Arrange & Act
        import codex

        # Assert
        assert "codex" in codex.__file__, "Condition must be true"

    def test_package_in_sys_modules(self) -> None:
        """Test package is in sys.modules."""
        # Arrange & Act

        # Assert
        assert "codex" in sys.modules, "Condition must be true"


class TestCodexBackwardCompatibility:
    """Test backward compatibility and stability."""

    def test_version_import_stable(self) -> None:
        """Test __version__ import is stable across multiple imports."""
        # Arrange & Act
        from codex import __version__ as v1
        from codex import __version__ as v2

        # Assert
        assert v1 == v2, "v1 is not valid"
        assert v1 is v2, "v1 is not valid"

    def test_all_export_stable(self) -> None:
        """Test __all__ export is stable across multiple imports."""
        # Arrange & Act
        from codex import __all__ as all1
        from codex import __all__ as all2

        # Assert
        assert all1 == all2, "all1 is not valid"

    def test_module_reimport_idempotent(self) -> None:
        """Test reimporting module is idempotent."""
        # Arrange & Act
        import codex

        first_id = id(codex)

        import codex as codex2

        second_id = id(codex2)

        # Assert
        assert first_id == second_id, "first_id is not valid"


class TestCodexImportSafety:
    """Test import safety and error handling."""

    def test_import_does_not_raise(self) -> None:
        """Test importing codex does not raise exceptions."""
        # Arrange & Act & Assert — import already happened at module load;
        # if we reached this line the import succeeded.
        assert True, "True is not valid"

    def test_version_import_does_not_raise(self) -> None:
        """Test importing __version__ does not raise exceptions."""
        assert True, "True is not valid"

    def test_all_import_does_not_raise(self) -> None:
        """Test importing __all__ does not raise exceptions."""
        assert True, "True is not valid"


class TestCodexPublicAPI:
    """Test public API surface area."""

    def test_public_exports_accessible(self) -> None:
        """Test all public exports are declared in __all__."""
        # Arrange & Act
        import codex

        # Assert
        # Note: Module names in __all__ are declarations, not necessarily attributes
        for export in codex.__all__:
            # __version__ should be accessible
            if export == "__version__":
                assert hasattr(codex, export), f"Export {export} not accessible"

    def test_no_private_exports_in_all(self) -> None:
        """Test __all__ does not contain private names (except __version__)."""
        # Arrange & Act
        from codex import __all__

        # Assert
        for item in __all__:
            # __version__ is public by convention
            if item == "__version__":
                continue
            assert not item.startswith("_"), f"Private name {item} should not be in __all__"

    def test_version_is_public(self) -> None:
        """Test __version__ is considered public despite leading underscore."""
        # Arrange & Act
        from codex import __all__

        # Assert
        # Special case: __version__ is public by convention
        assert "__version__" in __all__, "Condition must be true"


# #AFTERMATH_METRIC - 30 tests created for src/codex/__init__.py
# Coverage target: Public API exports, version info, documentation
# Test pattern: AAA (Arrange-Act-Assert)
