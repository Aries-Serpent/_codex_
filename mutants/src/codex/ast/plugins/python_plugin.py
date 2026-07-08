"""
Reference Python plugin implementation.
"""

from pathlib import Path

from codex.ast import parse_python
from codex.ast.node import StandardizedASTNode

from . import ASTPlugin, PluginMetadata


class PythonPlugin(ASTPlugin):
    """
    Python language plugin using existing codex parser.

    This serves as a reference implementation for other language plugins.
    """

    @property
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="python",
            version="1.0.0",
            author="Codex Team",
            description="Python AST parser using libcst",
            languages=["python"],
            file_extensions=[".py", ".pyw"],
        )

    @property
    def language(self) -> str:
        """Return language name."""
        return "python"

    @property
    def file_extensions(self) -> list[str]:
        """Return supported file extensions."""
        return [".py", ".pyw"]

    def can_parse(self, file_path: str) -> bool:
        """Check if this plugin can parse the file."""
        ext = Path(file_path).suffix.lower()
        return ext in self.file_extensions

    def parse(self, code: str, file_path: str) -> StandardizedASTNode:
        """Parse Python code using existing parser."""
        # Use existing codex parser
        return parse_python(code, file_path)

    def validate(self) -> bool:
        """Validate plugin is ready."""
        try:
            return parse_python("def _validate():\n    return True\n", "validate.py") is not None
        except (IOError, OSError):
            return False
