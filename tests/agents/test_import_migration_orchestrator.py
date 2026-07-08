"""
Comprehensive tests for ImportMigrationOrchestrator.

Coverage target: Lines 670-915 in agents/physics_orchestrator.py

Test Categories:
- Import assessment and scanning
- Migration deliberation and ranking
- Migration plan optimization
- Migration execution (dry run and actual)
- End-to-end workflow integration
"""

import shutil
import tempfile
from pathlib import Path

import pytest

from agents.physics_orchestrator import ImportMigration, ImportMigrationOrchestrator


class TestImportMigration:
    """Test suite for ImportMigration dataclass."""

    @pytest.fixture
    def basic_migration(self):
        """Create a basic migration."""
        return ImportMigration(
            file_path="/test/file.py",
            old_import="from training.model import Model",
            new_import="from training.model import Model",
            line_number=5,
        )

    def test_import_migration_initialization(self, basic_migration):
        """Test ImportMigration initializes correctly."""
        assert basic_migration.file_path == "/test/file.py", "file_path is not valid"
        assert basic_migration.old_import == "from training.model import Model", "old_import is not valid"
        assert basic_migration.new_import == "from training.model import Model", "new_import is not valid"
        assert basic_migration.line_number == 5, "line_number is not valid"

    def test_calculate_properties(self, basic_migration):
        """Test physics properties calculation."""
        basic_migration.calculate_properties()

        # Should have physics properties
        assert basic_migration.potential_energy > 0, "potential_energy must be greater than zero"
        # Note: kinetic_energy is not a property of ImportMigration
        assert basic_migration.friction > 0, "friction must be greater than zero"
        assert basic_migration.momentum > 0, "momentum must be greater than zero"
        assert 0 <= basic_migration.confidence <= 1, "0 is not valid"
        assert 0 <= basic_migration.risk <= 1, "0 is not valid"
        assert 0 <= basic_migration.impact <= 1, "0 is not valid"
        assert 0 <= basic_migration.urgency <= 1, "0 is not valid"
        assert basic_migration.optimization_score > 0, "optimization_score must be greater than zero"

    def test_properties_different_lengths(self):
        """Test properties vary with import length."""
        short_migration = ImportMigration(
            file_path="/test/file.py",
            old_import="import x",
            new_import="import y",
            line_number=1,
        )
        short_migration.calculate_properties()

        long_migration = ImportMigration(
            file_path="/test/file.py",
            old_import="from very.very.deep.nested.module.path import VeryLongClassName",
            new_import="from very.very.deep.nested.module.path import VeryLongClassName",
            line_number=1,
        )
        long_migration.calculate_properties()

        # Longer imports should have higher energy
        assert long_migration.potential_energy > short_migration.potential_energy, "potential_energy must be greater than zero"


@pytest.mark.slow
@pytest.mark.integration
class TestImportMigrationOrchestrator:
    """Test suite for ImportMigrationOrchestrator."""

    @pytest.fixture
    def temp_repo(self):
        """Create temporary repository with test files."""
        temp_dir = tempfile.mkdtemp()
        repo_path = Path(temp_dir)

        # Create test Python files with deprecated imports
        test_file1 = repo_path / "module1.py"
        test_file1.write_text("""
from training.model import Model
from models.classifier import Classifier
import training.trainer as trainer

def test():
    pass
""")

        test_file2 = repo_path / "module2.py"
        test_file2.write_text("""
import models.utils
from training.data import DataLoader

class MyClass:
    pass
""")

        # Create file that should be skipped (already migrated)
        test_file3 = repo_path / "module3.py"
        test_file3.write_text("""
from src.training.model import Model
from src.models.classifier import Classifier

def already_migrated():
    pass
""")

        # Create nested directory
        nested_dir = repo_path / "subdir"
        nested_dir.mkdir()
        nested_file = nested_dir / "nested.py"
        nested_file.write_text("""
from training.pipeline import Pipeline
""")

        yield repo_path

        # Cleanup
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def orchestrator(self):
        """Create ImportMigrationOrchestrator instance."""
        return ImportMigrationOrchestrator()

    def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initializes correctly."""
        assert orchestrator is not None, "orchestrator must be initialized"
        assert len(orchestrator.migrations) == 0, "Collection must not be empty"
        assert len(orchestrator.completed_migrations) == 0, "Collection must not be empty"
        assert len(orchestrator.migration_map) > 0, "Collection must not be empty"
        assert "from training." in orchestrator.migration_map, "Condition must be true"
        assert "from models." in orchestrator.migration_map, "Condition must be true"

    def test_migration_map_content(self, orchestrator):
        """Test migration map has expected mappings."""
        assert orchestrator.migration_map["from training."] == "from src.training.", "orchestrat is not valid"
        assert orchestrator.migration_map["from models."] == "from src.models.", "orchestrat is not valid"
        assert orchestrator.migration_map["import training."] == "import src.training.", "orchestrat is not valid"
        assert orchestrator.migration_map["import models."] == "import src.models.", "orchestrat is not valid"

    def test_assess_imports(self, orchestrator, temp_repo):
        """Test import assessment scans and finds deprecated imports."""
        assessment = orchestrator.assess_imports(temp_repo)

        # Should have scanned files
        assert assessment["files_scanned"] > 0, "Value must be greater than zero"
        assert assessment["deprecated_found"] > 0, "Value must be greater than zero"
        assert assessment["unique_files"] > 0, "Value must be greater than zero"

        # Should have found migrations
        assert len(orchestrator.migrations) > 0, "Collection must not be empty"

        # Check assessment metrics
        assert assessment["total_energy_required"] > 0, "Value must be greater than zero"
        assert 0 <= assessment["average_risk"] <= 1, "0 is not valid"

    def test_assess_imports_finds_correct_count(self, orchestrator, temp_repo):
        """Test assessment finds correct number of deprecated imports."""
        assessment = orchestrator.assess_imports(temp_repo)

        # module1.py has 3 deprecated imports
        # module2.py has 2 deprecated imports
        # module3.py has 0 (already migrated)
        # nested.py has 1 deprecated import
        # Total: 6 deprecated imports
        assert assessment["deprecated_found"] == 6, "Condition must be true"

    def test_assess_imports_skips_already_migrated(self, orchestrator, temp_repo):
        """Test assessment skips files with already migrated imports."""
        orchestrator.assess_imports(temp_repo)

        # module3.py should not contribute any migrations
        module3_migrations = [m for m in orchestrator.migrations if "module3.py" in m.file_path]
        assert len(module3_migrations) == 0, "Module3_migrations must not be empty"

    def test_assess_imports_handles_nested_directories(self, orchestrator, temp_repo):
        """Test assessment finds files in nested directories."""
        orchestrator.assess_imports(temp_repo)

        # Should find nested.py
        nested_migrations = [m for m in orchestrator.migrations if "nested.py" in m.file_path]
        assert len(nested_migrations) > 0, "Nested_migrations must not be empty"

    def test_deliberate_migrations(self, orchestrator, temp_repo):
        """Test migration deliberation ranks by optimization score."""
        orchestrator.assess_imports(temp_repo)
        ranked = orchestrator.deliberate_migrations()

        # Should return ranked list
        assert len(ranked) == len(orchestrator.migrations), "Ranked must not be empty"

        # Should be sorted by optimization score (highest first)
        scores = [m.optimization_score for m in ranked]
        assert scores == sorted(scores, reverse=True)

    def test_deliberate_migrations_empty_list(self, orchestrator):
        """Test deliberation with no migrations."""
        ranked = orchestrator.deliberate_migrations()

        assert len(ranked) == 0, "Ranked must not be empty"

    def test_optimize_migration_plan_within_budget(self, orchestrator, temp_repo):
        """Test optimization selects migrations within energy budget."""
        orchestrator.assess_imports(temp_repo)
        ranked = orchestrator.deliberate_migrations()

        # Set a reasonable budget
        budget = 100.0
        selected = orchestrator.optimize_migration_plan(ranked, energy_budget=budget)

        # Total energy should not exceed budget
        total_energy = sum(m.potential_energy for m in selected)
        assert total_energy <= budget, "total_energy is not valid"

        # Should have selected some migrations
        assert len(selected) > 0, "Selected must not be empty"

    def test_optimize_migration_plan_unlimited_budget(self, orchestrator, temp_repo):
        """Test optimization with very large budget selects all."""
        orchestrator.assess_imports(temp_repo)
        ranked = orchestrator.deliberate_migrations()

        # Set a very large budget
        budget = 10000.0
        selected = orchestrator.optimize_migration_plan(ranked, energy_budget=budget)

        # Should select all migrations
        assert len(selected) == len(ranked), "Selected must not be empty"

    def test_optimize_migration_plan_minimal_budget(self, orchestrator, temp_repo):
        """Test optimization with tiny budget selects minimal migrations."""
        orchestrator.assess_imports(temp_repo)
        ranked = orchestrator.deliberate_migrations()

        # Set a very small budget
        budget = 1.0
        selected = orchestrator.optimize_migration_plan(ranked, energy_budget=budget)

        # Should select very few (or zero) migrations
        assert len(selected) < len(ranked), "Selected must not be empty"

    def test_execute_migrations_dry_run(self, orchestrator, temp_repo):
        """Test migration execution in dry-run mode."""
        orchestrator.assess_imports(temp_repo)
        ranked = orchestrator.deliberate_migrations()
        selected = orchestrator.optimize_migration_plan(ranked, energy_budget=200.0)

        # Execute in dry-run mode
        results = orchestrator.execute_migrations(selected, dry_run=True)

        # Should have attempted migrations
        assert results["migrations_attempted"] > 0, "Value must be greater than zero"

        # In dry-run, files should not be modified
        # (check one of the original files is unchanged)
        test_file1 = temp_repo / "module1.py"
        content = test_file1.read_text()
        assert "from training.model import Model" in content, "Content must not be empty"

    def test_execute_migrations_actual(self, orchestrator, temp_repo):
        """Test actual migration execution modifies files."""
        orchestrator.assess_imports(temp_repo)
        ranked = orchestrator.deliberate_migrations()
        selected = orchestrator.optimize_migration_plan(ranked, energy_budget=500.0)

        # Execute actual migrations
        results = orchestrator.execute_migrations(selected, dry_run=False)

        # Should have successful migrations
        assert results["migrations_successful"] > 0, "Value must be greater than zero"

        # Files should be modified
        assert len(results["files_modified"]) > 0, "Collection must not be empty"

        # Check one file was actually modified
        test_file1 = temp_repo / "module1.py"
        content = test_file1.read_text()
        assert "from src.training.model import Model" in content, "Content must not be empty"
        assert "from training.model import Model" not in content, "Content must not be empty"

    def test_execute_migrations_groups_by_file(self, orchestrator, temp_repo):
        """Test execution efficiently groups migrations by file."""
        orchestrator.assess_imports(temp_repo)
        ranked = orchestrator.deliberate_migrations()
        selected = orchestrator.optimize_migration_plan(ranked, energy_budget=500.0)

        results = orchestrator.execute_migrations(selected, dry_run=True)

        # Number of files modified should be less than total migrations
        # (multiple migrations per file)
        unique_files = len(set(m.file_path for m in selected))
        assert len(results["files_modified"]) <= unique_files, "Collection must not be empty"


@pytest.mark.slow
@pytest.mark.integration
class TestImportMigrationWorkflow:
    """Integration tests for complete import migration workflow."""

    @pytest.fixture
    def complex_repo(self):
        """Create complex repository for integration testing."""
        temp_dir = tempfile.mkdtemp()
        repo_path = Path(temp_dir)

        # Create multiple files with various patterns
        (repo_path / "app.py").write_text("""
from training.model import Model
from models.classifier import Classifier
import training.trainer as trainer

def main():
    model = Model()
    classifier = Classifier()
""")

        (repo_path / "utils.py").write_text("""
import models.preprocessing
from training.data import load_data

def preprocess():
    return models.preprocessing.clean()
""")

        # Create src directory structure (migration target)
        src_dir = repo_path / "src"
        src_dir.mkdir()

        training_dir = src_dir / "training"
        training_dir.mkdir(parents=True)
        (training_dir / "__init__.py").write_text("")

        models_dir = src_dir / "models"
        models_dir.mkdir(parents=True)
        (models_dir / "__init__.py").write_text("")

        yield repo_path

        shutil.rmtree(temp_dir)

    def test_end_to_end_migration_workflow(self, complex_repo):
        """Test complete ASSESS→DELIBERATE→OPTIMIZE→ACT workflow."""
        orchestrator = ImportMigrationOrchestrator()

        # ASSESS
        assessment = orchestrator.assess_imports(complex_repo)
        assert assessment["deprecated_found"] > 0, "Value must be greater than zero"

        # DELIBERATE
        ranked = orchestrator.deliberate_migrations()
        assert len(ranked) > 0, "Ranked must not be empty"
        assert all(hasattr(m, "optimization_score") for m in ranked)

        # OPTIMIZE
        selected = orchestrator.optimize_migration_plan(ranked, energy_budget=300.0)
        assert len(selected) > 0, "Selected must not be empty"

        # ACT
        results = orchestrator.execute_migrations(selected, dry_run=False)
        assert results["migrations_successful"] > 0, "Value must be greater than zero"
        assert len(results["files_modified"]) > 0, "Collection must not be empty"

        # Verify migrations were applied
        app_file = complex_repo / "app.py"
        app_content = app_file.read_text()
        assert "from src.training.model import Model" in app_content, "Content must not be empty"

    def test_workflow_with_no_deprecated_imports(self):
        """Test workflow when repository has no deprecated imports."""
        temp_dir = tempfile.mkdtemp()
        repo_path = Path(temp_dir)

        # Create file with only modern imports
        (repo_path / "modern.py").write_text("""
from src.training.model import Model
from src.models.classifier import Classifier

def test():
    pass
""")

        orchestrator = ImportMigrationOrchestrator()

        try:
            # ASSESS
            assessment = orchestrator.assess_imports(repo_path)
            assert assessment["deprecated_found"] == 0, "Condition must be true"

            # DELIBERATE
            ranked = orchestrator.deliberate_migrations()
            assert len(ranked) == 0, "Ranked must not be empty"

            # OPTIMIZE
            selected = orchestrator.optimize_migration_plan(ranked, energy_budget=100.0)
            assert len(selected) == 0, "Selected must not be empty"

            # ACT
            results = orchestrator.execute_migrations(selected, dry_run=False)
            assert results["migrations_successful"] == 0, "Result must not be empty"
        finally:
            shutil.rmtree(temp_dir)

    def test_workflow_preserves_file_structure(self, complex_repo):
        """Test migration preserves non-import code."""
        orchestrator = ImportMigrationOrchestrator()

        # Read original file content
        app_file = complex_repo / "app.py"
        original_lines = app_file.read_text().split("\n")

        # Run full workflow
        orchestrator.assess_imports(complex_repo)
        ranked = orchestrator.deliberate_migrations()
        selected = orchestrator.optimize_migration_plan(ranked, energy_budget=500.0)
        orchestrator.execute_migrations(selected, dry_run=False)

        # Read modified file content
        modified_lines = app_file.read_text().split("\n")

        # Should have same number of lines
        assert len(modified_lines) == len(original_lines), "Modified_lines must not be empty"

        # Non-import lines should be unchanged
        for orig, mod in zip(original_lines, modified_lines):
            if not orig.strip().startswith(("from ", "import ")):
                assert orig == mod, "orig is not valid"

    def test_multiple_migrations_same_file(self, complex_repo):
        """Test multiple migrations in same file are handled correctly."""
        orchestrator = ImportMigrationOrchestrator()

        orchestrator.assess_imports(complex_repo)

        # Find migrations for app.py (should have multiple)
        app_migrations = [m for m in orchestrator.migrations if "app.py" in m.file_path]

        assert len(app_migrations) >= 3, "App_migrations must not be empty"

        # Execute all
        ranked = orchestrator.deliberate_migrations()
        selected = orchestrator.optimize_migration_plan(ranked, energy_budget=1000.0)
        orchestrator.execute_migrations(selected, dry_run=False)

        # All migrations should succeed
        app_file = complex_repo / "app.py"
        final_content = app_file.read_text()

        # Verify all old imports are gone
        assert "from training.model" not in final_content, "Content must not be empty"
        assert "from models.classifier" not in final_content, "Content must not be empty"
        assert "import training.trainer" not in final_content, "Content must not be empty"

        # Verify all new imports are present
        assert "from src.training.model" in final_content, "Content must not be empty"
        assert "from src.models.classifier" in final_content, "Content must not be empty"
        assert "import src.training.trainer" in final_content, "Content must not be empty"
