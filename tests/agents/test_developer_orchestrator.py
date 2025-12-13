"""
Tests for PhysicsGuidedDeveloperOrchestrator module.

Tests physics-guided Python app generation.
"""

import pytest
import tempfile
from pathlib import Path
from agents.developer_orchestrator import (
    PhysicsGuidedDeveloperOrchestrator,
    CodeComponent,
    AppType,
    DevelopmentPhase
)


class TestPhysicsGuidedDeveloperOrchestrator:
    """Test physics-guided developer orchestrator functionality."""
    
    def test_initialization(self):
        """Test PhysicsGuidedDeveloperOrchestrator initializes correctly."""
        orchestrator = PhysicsGuidedDeveloperOrchestrator(
            app_name="test_app",
            app_type=AppType.PYTHON_CLI
        )
        
        assert orchestrator.app_name == "test_app"
        assert orchestrator.app_type == AppType.PYTHON_CLI
        assert isinstance(orchestrator.components, dict)
        assert len(orchestrator.physics_log) == 0
    
    def test_add_component(self):
        """Test adding a component."""
        orchestrator = PhysicsGuidedDeveloperOrchestrator(
            app_name="test_app",
            app_type=AppType.PYTHON_WEB
        )
        
        orchestrator.add_component(
            name="main.py",
            code="print('hello')",
            dependencies=[]
        )
        
        assert "main.py" in orchestrator.components
        component = orchestrator.components["main.py"]
        assert component.name == "main.py"
        assert component.code == "print('hello')"
    
    def test_add_component_with_dependencies(self):
        """Test adding a component with dependencies."""
        orchestrator = PhysicsGuidedDeveloperOrchestrator(
            app_name="test_app",
            app_type=AppType.PYTHON_CLI
        )
        
        orchestrator.add_component(
            name="utils.py",
            code="def helper(): pass",
            dependencies=["typing", "pathlib"]
        )
        
        component = orchestrator.components["utils.py"]
        assert "typing" in component.dependencies
        assert "pathlib" in component.dependencies
    
    def test_remove_component(self):
        """Test removing a component."""
        orchestrator = PhysicsGuidedDeveloperOrchestrator(
            app_name="test_app",
            app_type=AppType.PYTHON_CLI
        )
        
        orchestrator.add_component(
            name="temp.py",
            code="pass"
        )
        
        assert "temp.py" in orchestrator.components
        
        removed = orchestrator.remove_component("temp.py")
        
        assert removed is True
        assert "temp.py" not in orchestrator.components
    
    def test_remove_nonexistent_component(self):
        """Test removing a component that doesn't exist."""
        orchestrator = PhysicsGuidedDeveloperOrchestrator(
            app_name="test_app",
            app_type=AppType.PYTHON_CLI
        )
        
        removed = orchestrator.remove_component("does_not_exist.py")
        
        assert removed is False
    
    def test_get_component(self):
        """Test retrieving a component."""
        orchestrator = PhysicsGuidedDeveloperOrchestrator(
            app_name="test_app",
            app_type=AppType.PYTHON_CLI
        )
        
        orchestrator.add_component(
            name="config.py",
            code="CONFIG = {}"
        )
        
        component = orchestrator.get_component("config.py")
        
        assert component is not None
        assert component.name == "config.py"
    
    def test_get_nonexistent_component(self):
        """Test retrieving a component that doesn't exist."""
        orchestrator = PhysicsGuidedDeveloperOrchestrator(
            app_name="test_app",
            app_type=AppType.PYTHON_CLI
        )
        
        component = orchestrator.get_component("missing.py")
        
        assert component is None
    
    def test_list_components(self):
        """Test listing all components."""
        orchestrator = PhysicsGuidedDeveloperOrchestrator(
            app_name="test_app",
            app_type=AppType.PYTHON_CLI
        )
        
        orchestrator.add_component("file1.py", "pass")
        orchestrator.add_component("file2.py", "pass")
        
        components = orchestrator.list_components()
        
        assert len(components) >= 2
        assert any(c.name == "file1.py" for c in components)
        assert any(c.name == "file2.py" for c in components)
    
    def test_export_app_to_directory(self, tmp_path):
        """Test exporting app to a directory."""
        orchestrator = PhysicsGuidedDeveloperOrchestrator(
            app_name="test_app",
            app_type=AppType.PYTHON_CLI
        )
        
        orchestrator.add_component(
            name="main.py",
            code="print('hello world')"
        )
        
        output_dir = tmp_path / "output"
        result = orchestrator.export_app(str(output_dir))
        
        assert isinstance(result, dict)
        assert "main.py" in result
        assert (output_dir / "main.py").exists()
    
    def test_export_app_no_overwrite(self, tmp_path):
        """Test export respects no-overwrite flag."""
        orchestrator = PhysicsGuidedDeveloperOrchestrator(
            app_name="test_app",
            app_type=AppType.PYTHON_CLI
        )
        
        orchestrator.add_component(
            name="main.py",
            code="print('hello')"
        )
        
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        (output_dir / "main.py").write_text("existing content")
        
        result = orchestrator.export_app(str(output_dir), overwrite=False)
        
        # Should skip existing file
        assert "Skipped" in result.get("main.py", "")
        assert (output_dir / "main.py").read_text() == "existing content"
    
    def test_export_app_with_overwrite(self, tmp_path):
        """Test export with overwrite flag."""
        orchestrator = PhysicsGuidedDeveloperOrchestrator(
            app_name="test_app",
            app_type=AppType.PYTHON_CLI
        )
        
        orchestrator.add_component(
            name="main.py",
            code="print('new content')"
        )
        
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        (output_dir / "main.py").write_text("old content")
        
        result = orchestrator.export_app(str(output_dir), overwrite=True)
        
        # Should overwrite
        assert (output_dir / "main.py").read_text() == "print('new content')"
    
    def test_export_app_invalid_directory(self, tmp_path):
        """Test export with invalid output directory."""
        orchestrator = PhysicsGuidedDeveloperOrchestrator(
            app_name="test_app",
            app_type=AppType.PYTHON_CLI
        )
        
        orchestrator.add_component(
            name="main.py",
            code="print('test')"
        )
        
        # Create a file instead of directory
        invalid_path = tmp_path / "not_a_dir"
        invalid_path.write_text("I am a file")
        
        with pytest.raises(ValueError, match="not a directory"):
            orchestrator.export_app(str(invalid_path))


class TestCodeComponent:
    """Test CodeComponent dataclass."""
    
    def test_component_initialization(self):
        """Test CodeComponent initializes correctly."""
        component = CodeComponent(
            name="test.py",
            code="def test(): pass",
            dependencies=["typing"],
            description="Test module"
        )
        
        assert component.name == "test.py"
        assert component.code == "def test(): pass"
        assert component.dependencies == ["typing"]
        assert component.description == "Test module"
