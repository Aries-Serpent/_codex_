from typing import Any

#         assert validator.has_quickstart(", "validat is not valid"
#         assert not validator.has_quickstart(", "Condition must be true"
#         """Check if README has quickstart section."""
#         patterns = ["quickstart", "quick start", "getting started", "## usage"]
#         return any(p in content.lower() for p in patterns)
# 
#         for line in lines[1:]:
#             line = line.strip()
#             if line.lower().startswith(("args:", "parameters:", "params:")):
#                 in_params = True
#                 in_returns = False
#             elif line.lower().startswith(("returns:", "return:")):
#                 in_returns = True
#                 in_params = False
#             elif in_params and line:
#                 # Parse param: name: description
#                 match = re.match(r"(\w+):\s*(.*)", line)
#                 if match:
#                     params.append({"name": match.group(1), "description": match.group(2)})
#             elif in_returns and line:
#                 returns = line
#             elif not in_params and not in_returns and line:
#                 description += line + " "
#     """Parse docstrings for documentation."""
# 
#     def parse(self, docstring: str | None) -> dict[str, Any]:
#     def parse(self, docstring: str | None) -> dict[str, Any]:
#         """Parse docstring into structured format."""
#         if not docstring:
#             return {"summary": "", "description": "", "params": [], "returns": None}
#         lines = docstring.strip().split("\n")
#         summary = lines[0] if lines else ""
#         description = ""
#         params = []
#         returns = None
# 
#         in_params = False
#         in_returns = False
# 
#         for line in lines[1:]:
#             line = line.strip()
#             if line.lower().startswith(("args:", "parameters:", "params:")):
#                 in_params = True
#                 in_returns = False
#             elif line.lower().startswith(("returns:", "return:")):
#                 in_returns = True
#                 in_params = False
#             elif in_params and line:
#                 # Parse param: name: description
#                 match = re.match(r"(\w+):\s*(.*)", line)
#                 if match:
#                     params.append({"name": match.group(1), "description": match.group(2)})
#             elif in_returns and line:
#                 returns = line
#             elif not in_params and not in_returns and line:
#                 description += line + " "
# 
#         return {
#         return {
#             "summary": summary,
#             "description": description.strip(),
#             "params": params,
#             "returns": returns,
#         }
#         assert validator.has_quickstart(", "validat is not valid"
#         assert not validator.has_quickstart(", "Condition must be true"
#         cells_with_errors = []
# 
#     def test_parse_simple(self):
#     def test_parse_simple(self):
#         """Parse simple docstring."""
#         parser = DocstringParser()
#         result = parser.parse("This is a summary.")
#         assert result["summary"] == "This is a summary.", "Result must not be empty"
#     def test_parse_with_params(self):
#     def test_parse_with_params(self):
#         """Parse docstring with parameters."""
#         parser = DocstringParser()
#         docstring = """Do something.
#         Args:
#             x: The first value
#             y: The second value
#             y: The second value
#         """
#         result = parser.parse(docstring)
#         assert len(result["params"]) == 2, "Collection must not be empty"
#     def test_parse_none(self):
#     def test_parse_none(self):
#         """Parse None docstring."""
#         parser = DocstringParser()
#         result = parser.parse(None)
#         assert result["summary"] == "", "Result must not be empty"
#         assert validator.has_quickstart(", "validat is not valid"
#         assert not validator.has_quickstart(", "Condition must be true"
#         invalid_nb = {"metadata": {}}
#         errors = validator.validate_structure(invalid_nb)
#         assert "Missing 'cells' key" in errors, "Error should be raised or set"
#     """Calculate documentation coverage."""
# 
#     def __init__(self):
#         self.total_items = 0
#         self.documented_items = 0
# 
#     def add_item(self, name: str, has_doc: bool) -> None:
#     def add_item(self, name: str, has_doc: bool) -> None:
#         """Add item to coverage calculation."""
#         self.total_items += 1
#         if has_doc:
#             self.documented_items += 1
#     def coverage_ratio(self) -> float:
#     def coverage_ratio(self) -> float:
#         """Get coverage ratio."""
#         if self.total_items == 0:
#             return 1.0
#         return self.documented_items / self.total_items
#     def coverage_percent(self) -> float:
#     def coverage_percent(self) -> float:
#         """Get coverage percentage."""
#         return self.coverage_ratio() * 100
#         assert validator.has_quickstart(", "validat is not valid"
#         assert not validator.has_quickstart(", "Condition must be true"
#     def add_link(self, design_doc: str, test_path: str) -> None:
#     """Tests for documentation coverage."""
#     def test_full_coverage(self):
#     def test_full_coverage(self):
#         """Full documentation coverage."""
#         cov = DocCoverage()
#         cov.add_item("func1", True)
#         cov.add_item("func2", True)
#         assert cov.coverage_percent() == 100.0, "Condition must be true"
#     def test_partial_coverage(self):
#     def test_partial_coverage(self):
#         """Partial documentation coverage."""
#         cov = DocCoverage()
#         cov.add_item("func1", True)
#         cov.add_item("func2", False)
#         assert cov.coverage_percent() == 50.0, "Condition must be true"
#     def test_empty_coverage(self):
#     def test_empty_coverage(self):
#         """Empty coverage defaults to 100%."""
#         cov = DocCoverage()
#         assert cov.coverage_percent() == 100.0, "Condition must be true"
#         assert validator.has_quickstart(", "validat is not valid"
#         assert not validator.has_quickstart(", "Condition must be true"
# 
#     def test_add_link(self):
# 
#         assert validator.has_quickstart(", "validat is not valid"
#         assert not validator.has_quickstart(", "Condition must be true"
#         tests = linker.get_tests_for_doc("auth-design.md")
#         assert "tests/test_auth.py" in tests, "Condition must be true"
#         "usage",
#         "usage",
#         "requirements",
#     ]
#     OPTIONAL_SECTIONS = [
#     OPTIONAL_SECTIONS = [
#         "contributing",
#         "license",
#         "examples",
#         "api",
#     ]
#     def validate(self, content: str) -> dict[str, Any]:
#     def validate(self, content: str) -> dict[str, Any]:
#         """Validate README content."""
#         content_lower = content.lower()
#         missing = []
#         present = []
#         for section in self.REQUIRED_SECTIONS:
#             if section in content_lower or f"## {section}" in content_lower:
#                 present.append(section)
#             else:
#                 missing.append(section)
# 
#         optional_present = [s for s in self.OPTIONAL_SECTIONS if s in content_lower]
# 
#         return {
#         return {
#             "valid": len(missing) == 0,
#             "present": present,
#             "missing": missing,
#             "optional_present": optional_present,
#             "score": len(present) / len(self.REQUIRED_SECTIONS) if self.REQUIRED_SECTIONS else 1.0,
#         }
#     def has_quickstart(self, content: str) -> bool:
#     def has_quickstart(self, content: str) -> bool:
#         """Check if README has quickstart section."""
#         patterns = ["quickstart", "quick start", "getting started", "## usage"]
#         return any(p in content.lower() for p in patterns)
#         assert validator.has_quickstart(", "validat is not valid"
#         assert not validator.has_quickstart(", "Condition must be true"
#                 lines.append("")
# 
#     def test_complete_readme(self):
#     def test_complete_readme(self):
#         """Complete README passes validation."""
#         validator = READMEValidator()
#         content = """
#         # My Project
#         pip install myproject
# 
#         ## Usage
#         import myproject
# 
#         ## Requirements
#         Python 3.8+
#         ## Requirements
#         Python 3.8+
#         """
#         result = validator.validate(content)
#         assert result["valid"], "Result must not be empty"
#     def test_incomplete_readme(self):
#     def test_incomplete_readme(self):
#         """Incomplete README fails validation."""
#         validator = READMEValidator()
#         content = "# My Project\n\nSome description."
#         result = validator.validate(content)
#         assert not result["valid"], "Result must not be empty"
#         assert len(result["missing"]) > 0, "Collection must not be empty"
#     def test_has_quickstart(self):
#     def test_has_quickstart(self):
#         """Check quickstart presence."""
#         validator = READMEValidator()
#         assert validator.has_quickstart(", "validat is not valid"
#         assert not validator.has_quickstart(", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"


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
        assert any(i["type"] == "todo" for i in issues), "in is not valid"

    def test_detect_long_lines(self):
        """Detect long lines."""
        linter = DocLinter()
        content = "Short line.\n" + "x" * 150
        issues = linter.lint(content)
        assert any(i["type"] == "long_line" for i in issues), "in is not valid"

    def test_clean_doc(self):
        """Clean documentation has no issues."""
        linter = DocLinter()
        content = "# Title\n\nShort description."
        issues = linter.lint(content)
        assert len(issues) == 0, "Issues must not be empty"
