"""
Context Distillation Tool

Uses sentencepiece to compress code from src/ and codex_ml/ into
token-friendly digest.md for AI agent context understanding.

Part of Phase 5: AI Agent Tooling Enhancement
"""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Repository root
REPO_ROOT = Path(__file__).resolve().parents[1]


class ContextDistiller:
    """
    Distills codebase context into token-efficient summaries.

    Compresses source code, documentation, and configurations into
    digestible context for AI agents.
    """

    def __init__(
        self,
        src_dirs: Optional[list[Path]] = None,
        max_tokens: int = 100000,
        output_path: Optional[Path] = None,
    ):
        """
        Initialize context distiller.

        Args:
            src_dirs: Directories to process (defaults to src/ and codex_ml/)
            max_tokens: Maximum tokens in output
            output_path: Output file path (defaults to digest.md)
        """
        self.src_dirs = src_dirs or [
            REPO_ROOT / "src",
            REPO_ROOT / "codex_ml",
            REPO_ROOT / "agents",
        ]
        self.max_tokens = max_tokens
        self.output_path = output_path or REPO_ROOT / "digest.md"

        # File extensions to process
        self.code_extensions = {
            ".py",
            ".js",
            ".ts",
            ".jsx",
            ".tsx",
            ".java",
            ".go",
            ".rs",
            ".cpp",
            ".c",
            ".h",
        }
        self.doc_extensions = {".md", ".rst", ".txt"}
        self.config_extensions = {".yaml", ".yml", ".json", ".toml", ".ini"}

        logger.info(f"ContextDistiller initialized: max_tokens={max_tokens}")

    def scan_codebase(self) -> dict[str, list[Path]]:
        """
        Scan codebase for relevant files.

        Returns:
            Dictionary mapping categories to file lists
        """
        results: dict[str, list[Path]] = {"code": [], "docs": [], "configs": []}

        for src_dir in self.src_dirs:
            if not src_dir.exists():
                logger.warning(f"Directory not found: {src_dir}")
                continue

            for file_path in src_dir.rglob("*"):
                if not file_path.is_file():
                    continue

                # Skip common ignorable patterns
                if self._should_ignore(file_path):
                    continue

                suffix = file_path.suffix.lower()

                if suffix in self.code_extensions:
                    results["code"].append(file_path)
                elif suffix in self.doc_extensions:
                    results["docs"].append(file_path)
                elif suffix in self.config_extensions:
                    results["configs"].append(file_path)

        logger.info(
            f"Scanned codebase: {len(results['code'])} code files, "
            f"{len(results['docs'])} docs, {len(results['configs'])} configs"
        )

        return results

    def _should_ignore(self, file_path: Path) -> bool:
        """Check if file should be ignored."""
        ignore_patterns = {
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            ".hypothesis",
            "node_modules",
            ".git",
            ".venv",
            "venv",
            "dist",
            "build",
            ".egg-info",
            "test_",  # Test files
            "_test.",
        }

        path_str = str(file_path)
        return any(pattern in path_str for pattern in ignore_patterns)

    def extract_code_structure(self, file_path: Path) -> dict[str, Any]:
        """
        Extract high-level structure from code file.

        Args:
            file_path: Path to code file

        Returns:
            Dictionary with structure information
        """
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except (IOError, OSError) as e:
            type(e).__name__
            logger.error(f"Failed to read {file_path}: <ERROR_TYPE>")
            return {}

        structure = {
            "path": str(file_path.relative_to(REPO_ROOT)),
            "size": len(content),
            "lines": content.count("\n"),
            "classes": [],
            "functions": [],
            "imports": [],
        }

        # Simple pattern matching for Python
        if file_path.suffix == ".py":
            import re

            # Extract classes
            class_pattern = r"^class\s+(\w+)"
            structure["classes"] = re.findall(class_pattern, content, re.MULTILINE)

            # Extract functions
            func_pattern = r"^def\s+(\w+)"
            structure["functions"] = re.findall(func_pattern, content, re.MULTILINE)

            # Extract imports (handle both forms, skip relative and star imports)
            import_pattern = r"^(?:from\s+([\w.]+)\s+)?import\s+([\w, ]+)"
            imports = []
            for match in re.finditer(import_pattern, content, re.MULTILINE):
                module, names = match.groups()
                # Skip relative imports (from . import) and star imports
                if (module and not module.startswith(".") and "*" not in names) or (
                    not module and "*" not in names
                ):
                    imports.extend([n.strip() for n in names.split(",")])
            structure["imports"] = imports[:20]  # Limit to first 20 for brevity

        return structure

    def generate_digest(self) -> str:
        """
        Generate context digest.

        Returns:
            Markdown-formatted digest
        """
        files = self.scan_codebase()

        digest = []
        digest.append("# Codebase Context Digest\n")
        digest.append(f"**Generated:** {datetime.now(timezone.utc).isoformat()}\n")
        digest.append(f"**Token Budget:** {self.max_tokens:,}\n\n")

        # Summary statistics
        digest.append("## Summary\n")
        total_files = sum(len(f) for f in files.values())
        digest.append(f"- **Total Files:** {total_files}\n")
        digest.append(f"- **Code Files:** {len(files['code'])}\n")
        digest.append(f"- **Documentation:** {len(files['docs'])}\n")
        digest.append(f"- **Configurations:** {len(files['configs'])}\n\n")

        # Code structure
        digest.append("## Code Structure\n\n")

        for code_file in sorted(files["code"][:50]):  # Limit to 50 files
            structure = self.extract_code_structure(code_file)

            if not structure:
                continue

            digest.append(f"### `{structure['path']}`\n")
            digest.append(f"- **Lines:** {structure['lines']}\n")

            if structure.get("classes"):
                digest.append(f"- **Classes:** {', '.join(structure['classes'][:10])}\n")

            if structure.get("functions"):
                digest.append(f"- **Functions:** {', '.join(structure['functions'][:10])}\n")

            digest.append("\n")

        if len(files["code"]) > 50:
            digest.append(f"... and {len(files['code']) - 50} more code files\n\n")

        # Key documentation
        digest.append("## Key Documentation\n\n")

        for doc_file in sorted(files["docs"][:20]):
            rel_path = doc_file.relative_to(REPO_ROOT)
            digest.append(f"- `{rel_path}`\n")

        if len(files["docs"]) > 20:
            digest.append(f"- ... and {len(files['docs']) - 20} more docs\n")

        digest.append("\n")

        # Configuration files
        digest.append("## Configuration Files\n\n")

        for config_file in sorted(files["configs"][:15]):
            rel_path = config_file.relative_to(REPO_ROOT)
            digest.append(f"- `{rel_path}`\n")

        if len(files["configs"]) > 15:
            digest.append(f"- ... and {len(files['configs']) - 15} more configs\n")

        digest.append("\n")

        # Module map
        digest.append("## Module Map\n\n")
        digest.append("```\n")
        digest.append("src/\n")
        digest.append("├── cognitive_brain/    # Cognitive architecture ABCs\n")
        digest.append("├── bridge_manager.py   # Secure IPC bridge\n")
        digest.append("├── bridge_types.py     # Typed message formats\n")
        digest.append("├── codex_init.py       # Configuration loader\n")
        digest.append("└── workflow_refactor.py # CI/CD utilities\n\n")
        digest.append("agents/\n")
        digest.append("├── cognitive_adapter.py # Legacy agent adapter\n")
        digest.append("├── agent_memory.py     # Agent memory system\n")
        digest.append("└── [35+ agent modules]\n\n")
        digest.append("cognitive_app/\n")
        digest.append("└── src/orchestrator.py # OODA Loop orchestrator\n")
        digest.append("```\n\n")

        # Digest metadata
        digest_text = "".join(digest)
        digest.append(f"**Digest Size:** {len(digest_text)} chars\n")
        digest.append(f"**Estimated Tokens:** ~{len(digest_text) // 4}\n")

        return "".join(digest)

    def save_digest(self, content: Optional[str] = None) -> Path:
        """
        Save digest to file.

        Args:
            content: Digest content (generates if not provided)

        Returns:
            Path to saved digest file
        """
        if content is None:
            content = self.generate_digest()

        # Ensure output directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write digest
        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Calculate checksum
        checksum = hashlib.sha256(content.encode()).hexdigest()[:16]

        logger.info(
            f"Digest saved: {self.output_path} ({len(content)} chars, checksum: {checksum})"
        )

        return self.output_path

    def compress_with_sentencepiece(self, content: str, model_path: Optional[Path] = None) -> str:
        """
        Compress content using sentencepiece tokenization.

        Args:
            content: Content to compress
            model_path: Path to sentencepiece model (optional)

        Returns:
            Compressed content
        """
        try:
            import sentencepiece as spm
        except ImportError:
            logger.warning("sentencepiece not installed. Install with: pip install sentencepiece")
            return content  # Return uncompressed

        if model_path and model_path.exists():
            sp = spm.SentencePieceProcessor(model_file=str(model_path))
            tokens = sp.encode(content, out_type=str)  # type: ignore[func-returns-value]

            # Reconstruct with token IDs for compression
            if tokens:
                compressed = " ".join(tokens[: self.max_tokens])

                logger.info(
                    f"Compressed with sentencepiece: {len(content)} → {len(compressed)} chars"
                )

                return compressed
        logger.warning("Sentencepiece model not found, skipping compression")
        return content


def generate_context_digest(output_path: Optional[Path] = None, max_tokens: int = 100000) -> Path:
    """
    Convenience function to generate context digest.

    Args:
        output_path: Output file path
        max_tokens: Maximum tokens

    Returns:
        Path to generated digest
    """
    distiller = ContextDistiller(max_tokens=max_tokens, output_path=output_path)
    return distiller.save_digest()


if __name__ == "__main__":
    # Generate digest when run as script
    print("🔍 Generating context digest...\n")

    digest_path = generate_context_digest()

    print(f"✅ Digest generated: {digest_path}")
    print(f"   Size: {digest_path.stat().st_size:,} bytes")
