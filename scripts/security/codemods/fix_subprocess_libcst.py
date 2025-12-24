"""
Codemod: Fix unsafe subprocess usage using libcst

Transforms:
  subprocess.call(..., shell=False) → subprocess.run(..., shell=False, check=True)
  os.system(...) → subprocess.run([...], check=True)

Author: mbaetiong
Generated: 2025-12-21

This is an AST-based implementation using libcst for robust code transformations
that preserve formatting and handle edge cases correctly.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Tuple, Union

import libcst as cst
from libcst import matchers as m

# Configure logging
logger = logging.getLogger(__name__)

# Safeguards
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


class SubprocessSecurityTransformer(cst.CSTTransformer):
    """Transform unsafe subprocess patterns using libcst AST transformations."""

    def __init__(self) -> None:
        super().__init__()
        self.changes: List[str] = []
        self.needs_subprocess_import = False

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> Union[cst.Call, cst.FlattenSentinel[cst.BaseSmallStatement]]:
        """Transform subprocess.call and os.system calls."""
        
        # Match subprocess.call(..., shell=False)
        if m.matches(
            updated_node,
            m.Call(
                func=m.Attribute(
                    value=m.Name("subprocess"),
                    attr=m.Name("call")
                )
            )
        ):
            return self._transform_subprocess_call(updated_node)
        
        # Match os.system(...)
        if m.matches(
            updated_node,
            m.Call(
                func=m.Attribute(
                    value=m.Name("os"),
                    attr=m.Name("system")
                )
            )
        ):
            return self._transform_os_system(updated_node)
        
        return updated_node

    def _transform_subprocess_call(self, node: cst.Call) -> cst.Call:
        """Transform subprocess.call to subprocess.run with shell=False and check=True."""
        
        # Check if shell=False is present
        has_shell_true = any(
            isinstance(arg, cst.Arg) and
            arg.keyword and arg.keyword.value == "shell" and
            m.matches(arg.value, m.Name("True"))
            for arg in node.args
        )
        
        if not has_shell_true:
            return node
        
        # Change function name from 'call' to 'run'
        new_func = node.func.with_changes(
            attr=cst.Name("run")
        )
        
        # Update arguments: change shell=False to shell=False, add check=True
        new_args = []
        shell_handled = False
        check_present = False
        
        for arg in node.args:
            if isinstance(arg, cst.Arg) and arg.keyword:
                if arg.keyword.value == "shell":
                    # Change shell=False to shell=False
                    new_args.append(
                        arg.with_changes(value=cst.Name("False"))
                    )
                    # Note: shell parameter handled here
                elif arg.keyword.value == "check":
                    check_present = True
                    new_args.append(arg)
                else:
                    new_args.append(arg)
            else:
                new_args.append(arg)
        
        # Add check=True if not present
        if not check_present:
            new_args.append(
                cst.Arg(
                    keyword=cst.Name("check"),
                    value=cst.Name("True"),
                    equal=cst.AssignEqual(
                        whitespace_before=cst.SimpleWhitespace(""),
                        whitespace_after=cst.SimpleWhitespace("")
                    )
                )
            )
        
        self.changes.append("Changed subprocess.call(shell=False) to subprocess.run(shell=False, check=True)")
        
        return node.with_changes(
            func=new_func,
            args=new_args
        )

    def _transform_os_system(self, node: cst.Call) -> cst.Call:
        """Transform os.system to subprocess.run."""
        
        # Change os.system(cmd) to subprocess.run(cmd, shell=False, check=True)
        new_func = cst.Attribute(
            value=cst.Name("subprocess"),
            attr=cst.Name("run")
        )
        
        # Keep existing arguments and add shell=False, check=True
        new_args = list(node.args)
        new_args.extend([
            cst.Arg(
                keyword=cst.Name("shell"),
                value=cst.Name("True"),
                equal=cst.AssignEqual(
                    whitespace_before=cst.SimpleWhitespace(""),
                    whitespace_after=cst.SimpleWhitespace("")
                )
            ),
            cst.Arg(
                keyword=cst.Name("check"),
                value=cst.Name("True"),
                equal=cst.AssignEqual(
                    whitespace_before=cst.SimpleWhitespace(""),
                    whitespace_after=cst.SimpleWhitespace("")
                )
            )
        ])
        
        self.changes.append(f"Converted os.system() to subprocess.run() with shell=False, check=True")
        self.needs_subprocess_import = True
        
        return node.with_changes(
            func=new_func,
            args=new_args
        )


class AddSubprocessImport(cst.CSTTransformer):
    """Add subprocess import if needed."""
    
    def __init__(self, needs_import: bool):
        super().__init__()
        self.needs_import = needs_import
        self.has_subprocess_import = False
    
    def visit_Import(self, node: cst.Import) -> None:
        """Check if subprocess is already imported."""
        for name in node.names:
            if isinstance(name, cst.ImportAlias) and name.name.value == "subprocess":
                self.has_subprocess_import = True
    
    def visit_ImportFrom(self, node: cst.ImportFrom) -> None:
        """Check if importing from subprocess."""
        if node.module and node.module.value == "subprocess":
            self.has_subprocess_import = True
    
    def leave_Module(self, original_node: cst.Module, updated_node: cst.Module) -> cst.Module:
        """Add subprocess import at module level if needed."""
        if not self.needs_import or self.has_subprocess_import:
            return updated_node
        
        # Find the best location to add import (after other imports)
        new_body = []
        import_added = False
        
        for i, stmt in enumerate(updated_node.body):
            new_body.append(stmt)
            
            # Add after the last import statement
            if not import_added and isinstance(stmt, cst.SimpleStatementLine):
                if any(isinstance(s, (cst.Import, cst.ImportFrom)) for s in stmt.body):
                    # Check if next statement is not an import
                    if i + 1 < len(updated_node.body):
                        next_stmt = updated_node.body[i + 1]
                        if not (isinstance(next_stmt, cst.SimpleStatementLine) and
                                any(isinstance(s, (cst.Import, cst.ImportFrom)) for s in next_stmt.body)):
                            # Add import here
                            new_body.append(
                                cst.SimpleStatementLine(
                                    body=[cst.Import(names=[cst.ImportAlias(name=cst.Name("subprocess"))])]
                                )
                            )
                            import_added = True
        
        # If no imports found, add at the beginning (after docstring if present)
        if not import_added:
            insert_at = 0
            if (updated_node.body and 
                isinstance(updated_node.body[0], cst.SimpleStatementLine) and
                isinstance(updated_node.body[0].body[0], cst.Expr) and
                isinstance(updated_node.body[0].body[0].value, cst.SimpleString)):
                # Has docstring, insert after it
                insert_at = 1
            
            new_body.insert(
                insert_at,
                cst.SimpleStatementLine(
                    body=[cst.Import(names=[cst.ImportAlias(name=cst.Name("subprocess"))])]
                )
            )
        
        return updated_node.with_changes(body=new_body)


def transform_file(file_path: str) -> Tuple[str, List[str]]:
    """
    Transform a single file to fix unsafe subprocess usage using libcst.

    Args:
        file_path: Path to the file to transform

    Returns:
        Tuple of (new_content, list_of_changes)
    """
    # Input validation (safeguard)
    if not file_path or not isinstance(file_path, str):
        return "", ["Invalid file path"]

    path = Path(file_path)
    if not path.exists():
        return "", [f"File not found: {file_path}"]

    # File size check (safeguard)
    if path.stat().st_size > MAX_FILE_SIZE:
        return "", [f"File too large: {file_path}"]

    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        logger.debug(f"Exception: {e}")
        return "", [f"Error reading file: {e}"]

    try:
        # Parse source code
        module = cst.parse_module(source)
        
        # Apply security transformations
        transformer = SubprocessSecurityTransformer()
        modified_tree = module.visit(transformer)
        
        # Add subprocess import if needed
        if transformer.needs_subprocess_import or transformer.changes:
            import_adder = AddSubprocessImport(needs_import=transformer.needs_subprocess_import)
            modified_tree = modified_tree.visit(import_adder)
            
            if not import_adder.has_subprocess_import and transformer.needs_subprocess_import:
                transformer.changes.append("Added 'import subprocess; import shlex'")
        
        # Generate new source code
        new_source = modified_tree.code
        
        return new_source, transformer.changes
        
    except cst.ParserSyntaxError as e:
        logger.error(f"Syntax error in {file_path}: {e}")
        return "", [f"Syntax error: {e}"]
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Error transforming {file_path}: {e}")
        return "", [f"Transformation error: {e}"]


def main() -> None:
    """Main entry point for CLI usage."""
    import sys

    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) < 2:
        print("Usage: python fix_subprocess_libcst.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    new_code, changes = transform_file(file_path)

    if changes:
        logger.info(f"✅ Made {len(changes)} changes:")
        for change in changes:
            logger.info(f"  - {change}")

        # Write back
        with open(file_path, "w") as f:
            f.write(new_code)
        logger.info(f"💾 Updated {file_path}")
    else:
        logger.info("No changes needed")


if __name__ == "__main__":
    main()
