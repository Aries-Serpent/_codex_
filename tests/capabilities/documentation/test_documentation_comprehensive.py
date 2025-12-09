"""Comprehensive tests for documentation capability.

Tests cover:
- API documentation generation
- Notebook execution validation
- README completeness
- Design doc linking
- Documentation coverage
"""

from __future__ import annotations

import re
from typing import Any

import pytest

pytest.importorskip("hypothesis", reason="hypothesis required for property tests")

from hypothesis import given, settings
from hypothesis import strategies as st


# --- API Documentation Tests ---


class DocstringParser:
    """Parse docstrings for documentation."""

    def parse(self, docstring: str | None) -> dict[str, Any]:
        """Parse docstring into structured format."""
        if not docstring:
            return {"summary": "", "description": "", "params": [], "returns": None}

        lines = docstring.strip().split("\n")
        summary = lines[0] if lines else ""
        description = ""
        params = []
        returns = None

        in_params = False
        in_returns = False

        for line in lines[1:]:
            line = line.strip()
            if line.lower().startswith(("args:", "parameters:", "params:")):
                in_params = True
                in_returns = False
            elif line.lower().startswith(("returns:", "return:")):
                in_returns = True
                in_params = False
            elif in_params and line:
                # Parse param: name: description
                match = re.match(r"(\w+):\s*(.*)", line)
                if match:
                    params.append({"name": match.group(1), "description": match.group(2)})
            elif in_returns and line:
                returns = line
            elif not in_params and not in_returns and line:
                description += line + " "

        return {
            "summary": summary,
            "description": description.strip(),
            "params": params,
            "returns": returns,
        }


class TestDocstringParser:
    """Tests for docstring parsing."""

    def test_parse_simple(self):
        """Parse simple docstring."""
        parser = DocstringParser()
        result = parser.parse("This is a summary.")
        assert result["summary"] == "This is a summary."

    def test_parse_with_params(self):
        """Parse docstring with parameters."""
        parser = DocstringParser()
        docstring = """Do something.

        Args:
            x: The first value
            y: The second value
        """
        result = parser.parse(docstring)
        assert len(result["params"]) == 2

    def test_parse_none(self):
        """Parse None docstring."""
        parser = DocstringParser()
        result = parser.parse(None)
        assert result["summary"] == ""


# --- Documentation Coverage Tests ---


class DocCoverage:
    """Calculate documentation coverage."""

    def __init__(self):
        self.total_items = 0
        self.documented_items = 0

    def add_item(self, name: str, has_doc: bool) -> None:
        """Add item to coverage calculation."""
        self.total_items += 1
        if has_doc:
            self.documented_items += 1

    def coverage_ratio(self) -> float:
        """Get coverage ratio."""
        if self.total_items == 0:
            return 1.0
        return self.documented_items / self.total_items

    def coverage_percent(self) -> float:
        """Get coverage percentage."""
        return self.coverage_ratio() * 100


class TestDocCoverage:
    """Tests for documentation coverage."""

    def test_full_coverage(self):
        """Full documentation coverage."""
        cov = DocCoverage()
        cov.add_item("func1", True)
        cov.add_item("func2", True)
        assert cov.coverage_percent() == 100.0

    def test_partial_coverage(self):
        """Partial documentation coverage."""
        cov = DocCoverage()
        cov.add_item("func1", True)
        cov.add_item("func2", False)
        assert cov.coverage_percent() == 50.0

    def test_empty_coverage(self):
        """Empty coverage defaults to 100%."""
        cov = DocCoverage()
        assert cov.coverage_percent() == 100.0


# --- README Validation Tests ---


class READMEValidator:
    """Validate README completeness."""

    REQUIRED_SECTIONS = [
        "installation",
        "usage",
        "requirements",
    ]

    OPTIONAL_SECTIONS = [
        "contributing",
        "license",
        "examples",
        "api",
    ]

    def validate(self, content: str) -> dict[str, Any]:
        """Validate README content."""
        content_lower = content.lower()
        missing = []
        present = []

        for section in self.REQUIRED_SECTIONS:
            if section in content_lower or f"## {section}" in content_lower:
                present.append(section)
            else:
                missing.append(section)

        optional_present = [s for s in self.OPTIONAL_SECTIONS if s in content_lower]

        return {
            "valid": len(missing) == 0,
            "present": present,
            "missing": missing,
            "optional_present": optional_present,
            "score": len(present) / len(self.REQUIRED_SECTIONS) if self.REQUIRED_SECTIONS else 1.0,
        }

    def has_quickstart(self, content: str) -> bool:
        """Check if README has quickstart section."""
        patterns = ["quickstart", "quick start", "getting started", "## usage"]
        return any(p in content.lower() for p in patterns)


class TestREADMEValidator:
    """Tests for README validation."""

    def test_complete_readme(self):
        """Complete README passes validation."""
        validator = READMEValidator()
        content = """
        # My Project
        
        ## Installation
        pip install myproject
        
        ## Usage
        import myproject
        
        ## Requirements
        Python 3.8+
        """
        result = validator.validate(content)
        assert result["valid"]

    def test_incomplete_readme(self):
        """Incomplete README fails validation."""
        validator = READMEValidator()
        content = "# My Project\n\nSome description."
        result = validator.validate(content)
        assert not result["valid"]
        assert len(result["missing"]) > 0

    def test_has_quickstart(self):
        """Check quickstart presence."""
        validator = READMEValidator()
        assert validator.has_quickstart("## Getting Started\nHere's how...")
        assert not validator.has_quickstart("# My Project\nDescription.")


# --- Notebook Validation Tests ---


class NotebookValidator:
    """Validate Jupyter notebook execution."""

    def __init__(self):
        self.errors: list[dict[str, Any]] = []

    def validate_structure(self, notebook: dict[str, Any]) -> list[str]:
        """Validate notebook structure."""
        errors = []
        if "cells" not in notebook:
            errors.append("Missing 'cells' key")
        if "metadata" not in notebook:
            errors.append("Missing 'metadata' key")
        return errors

    def check_outputs(self, notebook: dict[str, Any]) -> dict[str, Any]:
        """Check cell outputs for errors."""
        cells = notebook.get("cells", [])
        code_cells = [c for c in cells if c.get("cell_type") == "code"]
        cells_with_output = [c for c in code_cells if c.get("outputs")]
        cells_with_errors = []

        for i, cell in enumerate(code_cells):
            for output in cell.get("outputs", []):
                if output.get("output_type") == "error":
                    cells_with_errors.append({"cell": i, "error": output.get("ename")})

        return {
            "total_code_cells": len(code_cells),
            "cells_with_output": len(cells_with_output),
            "cells_with_errors": cells_with_errors,
            "all_executed": len(cells_with_output) == len(code_cells),
        }


class TestNotebookValidator:
    """Tests for notebook validation."""

    def test_validate_structure(self):
        """Validate notebook structure."""
        validator = NotebookValidator()
        valid_nb = {"cells": [], "metadata": {}}
        errors = validator.validate_structure(valid_nb)
        assert len(errors) == 0

    def test_missing_cells(self):
        """Missing cells is detected."""
        validator = NotebookValidator()
        invalid_nb = {"metadata": {}}
        errors = validator.validate_structure(invalid_nb)
        assert "Missing 'cells' key" in errors

    def test_check_outputs(self):
        """Check cell outputs."""
        validator = NotebookValidator()
        notebook = {
            "cells": [
                {"cell_type": "code", "outputs": [{"output_type": "execute_result"}]},
                {"cell_type": "code", "outputs": []},
            ]
        }
        result = validator.check_outputs(notebook)
        assert result["total_code_cells"] == 2
        assert result["cells_with_output"] == 1


# --- Design Doc Linking Tests ---


class DesignDocLinker:
    """Link design docs to tests."""

    def __init__(self):
        self.links: dict[str, list[str]] = {}

    def add_link(self, design_doc: str, test_path: str) -> None:
        """Link design doc to test."""
        if design_doc not in self.links:
            self.links[design_doc] = []
        self.links[design_doc].append(test_path)

    def get_tests_for_doc(self, design_doc: str) -> list[str]:
        """Get tests linked to design doc."""
        return self.links.get(design_doc, [])

    def get_coverage(self, all_docs: list[str]) -> dict[str, Any]:
        """Get coverage of design docs by tests."""
        linked = [d for d in all_docs if d in self.links]
        unlinked = [d for d in all_docs if d not in self.links]
        return {
            "linked": linked,
            "unlinked": unlinked,
            "coverage": len(linked) / len(all_docs) if all_docs else 1.0,
        }


class TestDesignDocLinker:
    """Tests for design doc linking."""

    def test_add_link(self):
        """Add link between doc and test."""
        linker = DesignDocLinker()
        linker.add_link("auth-design.md", "tests/test_auth.py")
        tests = linker.get_tests_for_doc("auth-design.md")
        assert "tests/test_auth.py" in tests

    def test_coverage(self):
        """Calculate coverage."""
        linker = DesignDocLinker()
        linker.add_link("doc1.md", "test1.py")
        all_docs = ["doc1.md", "doc2.md", "doc3.md"]
        coverage = linker.get_coverage(all_docs)
        assert len(coverage["unlinked"]) == 2


# --- API Reference Generator Tests ---


class APIReference:
    """API reference documentation."""

    def __init__(self, module_name: str):
        self.module_name = module_name
        self.classes: list[dict[str, Any]] = []
        self.functions: list[dict[str, Any]] = []
        self.constants: list[dict[str, Any]] = []

    def add_class(self, name: str, docstring: str, methods: list[str]) -> None:
        """Add class to API reference."""
        self.classes.append({"name": name, "docstring": docstring, "methods": methods})

    def add_function(self, name: str, docstring: str, signature: str) -> None:
        """Add function to API reference."""
        self.functions.append({"name": name, "docstring": docstring, "signature": signature})

    def to_markdown(self) -> str:
        """Generate markdown documentation."""
        lines = [f"# {self.module_name} API Reference", ""]

        if self.classes:
            lines.append("## Classes")
            lines.append("")
            for cls in self.classes:
                lines.append(f"### {cls['name']}")
                lines.append(cls["docstring"])
                lines.append("")

        if self.functions:
            lines.append("## Functions")
            lines.append("")
            for func in self.functions:
                lines.append(f"### {func['name']}")
                lines.append(f"```python\n{func['signature']}\n```")
                lines.append(func["docstring"])
                lines.append("")

        return "\n".join(lines)


class TestAPIReference:
    """Tests for API reference generation."""

    def test_add_class(self):
        """Add class to reference."""
        ref = APIReference("mymodule")
        ref.add_class("MyClass", "A class.", ["method1", "method2"])
        assert len(ref.classes) == 1

    def test_add_function(self):
        """Add function to reference."""
        ref = APIReference("mymodule")
        ref.add_function("my_func", "A function.", "def my_func(x: int) -> str")
        assert len(ref.functions) == 1

    def test_to_markdown(self):
        """Generate markdown."""
        ref = APIReference("mymodule")
        ref.add_function("func1", "Does something.", "def func1()")
        md = ref.to_markdown()
        assert "# mymodule API Reference" in md
        assert "## Functions" in md


# --- Documentation Linter Tests ---


class DocLinter:
    """Lint documentation for issues."""

    def lint(self, content: str) -> list[dict[str, Any]]:
        """Lint documentation content."""
        issues = []

        # Check for broken links
        link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
        for match in re.finditer(link_pattern, content):
            url = match.group(2)
            if not url.startswith(("http://", "https://", "#", "/")):
                if not url.endswith((".md", ".py", ".txt")):
                    issues.append({"type": "broken_link", "url": url, "position": match.start()})

        # Check for TODO/FIXME comments
        for pattern in ["TODO", "FIXME", "XXX"]:
            for match in re.finditer(pattern, content):
                issues.append({"type": "todo", "pattern": pattern, "position": match.start()})

        # Check for very long lines
        for i, line in enumerate(content.split("\n")):
            if len(line) > 120:
                issues.append({"type": "long_line", "line": i + 1, "length": len(line)})

        return issues


class TestDocLinter:
    """Tests for documentation linter."""

    def test_detect_todo(self):
        """Detect TODO comments."""
        linter = DocLinter()
        content = "This is a document.\n\nTODO: Fix this later."
        issues = linter.lint(content)
        assert any(i["type"] == "todo" for i in issues)

    def test_detect_long_lines(self):
        """Detect long lines."""
        linter = DocLinter()
        content = "Short line.\n" + "x" * 150
        issues = linter.lint(content)
        assert any(i["type"] == "long_line" for i in issues)

    def test_clean_doc(self):
        """Clean documentation has no issues."""
        linter = DocLinter()
        content = "# Title\n\nShort description."
        issues = linter.lint(content)
        assert len(issues) == 0
