"""Python AST Parser for function/class extraction."""

import ast
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class FunctionSignature:
    """Represents a function or method signature."""

    name: str
    file_path: str
    start_line: int
    end_line: int
    parameters: List[str]
    return_type: Optional[str]
    ast_hash: str
    body_hash: str
    is_method: bool = False
    class_name: Optional[str] = None


class PythonASTParser:
    """Parses Python files to extract functions and classes."""

    def parse_file(self, file_path: Path) -> List[FunctionSignature]:
        """
        Extract all functions from Python file.

        Args:
            file_path: Path to Python file

        Returns:
            List of function signatures
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content, filename=str(file_path))
            signatures = []

            # Extract top-level functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    sig = self._extract_function(node, str(file_path))
                    if sig:
                        signatures.append(sig)
                elif isinstance(node, ast.AsyncFunctionDef):
                    sig = self._extract_function(node, str(file_path))
                    if sig:
                        signatures.append(sig)

            # Extract class methods
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_name = node.name
                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            sig = self._extract_function(
                                item, str(file_path), class_name=class_name
                            )
                            if sig:
                                signatures.append(sig)

            return signatures

        except SyntaxError:
            # Gracefully handle syntax errors
            return []
        except Exception:
            # Handle other parsing errors
            return []

    def _extract_function(
        self,
        node: ast.FunctionDef,
        file_path: str,
        class_name: Optional[str] = None,
    ) -> Optional[FunctionSignature]:
        """
        Extract function signature from AST node.

        Args:
            node: AST FunctionDef node
            file_path: Path to source file
            class_name: Optional class name if this is a method

        Returns:
            FunctionSignature or None if extraction fails
        """
        try:
            # Extract parameters
            params = []
            for arg in node.args.args:
                params.append(arg.arg)

            # Extract return type if annotated
            return_type = None
            if node.returns:
                return_type = ast.unparse(node.returns)

            # Compute hashes
            ast_hash = self.compute_ast_hash(node)
            body_hash = self._compute_body_hash(node)

            return FunctionSignature(
                name=node.name,
                file_path=file_path,
                start_line=node.lineno,
                end_line=node.end_lineno or node.lineno,
                parameters=params,
                return_type=return_type,
                ast_hash=ast_hash,
                body_hash=body_hash,
                is_method=class_name is not None,
                class_name=class_name,
            )

        except Exception:
            return None

    def compute_ast_hash(self, node: ast.AST) -> str:
        """
        Compute hash of AST structure.

        This creates a hash based on the structure of the AST,
        independent of variable names.

        Args:
            node: AST node

        Returns:
            SHA256 hash of AST structure
        """
        # Create a string representation of AST structure
        ast_str = ast.dump(node, annotate_fields=False, include_attributes=False)
        return hashlib.sha256(ast_str.encode()).hexdigest()[:16]

    def _compute_body_hash(self, node: ast.FunctionDef) -> str:
        """
        Compute hash of function body only.

        Args:
            node: Function AST node

        Returns:
            SHA256 hash of function body
        """
        body_str = ""
        for stmt in node.body:
            body_str += ast.dump(stmt, annotate_fields=False)
        return hashlib.sha256(body_str.encode()).hexdigest()[:16]

    def get_structural_similarity(self, ast1: ast.AST, ast2: ast.AST) -> float:
        """
        Compute similarity score between two AST structures.

        Uses a simple approach: if AST hashes match, similarity is 1.0,
        otherwise compare node counts and types.

        Args:
            ast1: First AST node
            ast2: Second AST node

        Returns:
            Similarity score from 0.0 to 1.0
        """
        hash1 = self.compute_ast_hash(ast1)
        hash2 = self.compute_ast_hash(ast2)

        if hash1 == hash2:
            return 1.0

        # Compare node types
        nodes1 = list(ast.walk(ast1))
        nodes2 = list(ast.walk(ast2))

        types1 = [type(n).__name__ for n in nodes1]
        types2 = [type(n).__name__ for n in nodes2]

        # Jaccard similarity
        set1 = set(types1)
        set2 = set(types2)

        if not set1 and not set2:
            return 1.0

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        return intersection / union if union > 0 else 0.0
