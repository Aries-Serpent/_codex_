#!/usr/bin/env python3
"""
Build API documentation using pdoc3.

This script generates HTML API reference documentation for the codex_ml package
and its public modules. Output is written to artifacts/docs/api/ (local only).

Usage:
    python tools/build_api_docs.py [--output-dir DIRECTORY]

Environment variables:
    CODEX_SKIP_OPTIONAL_IMPORTS - Skip modules requiring optional dependencies
"""
import argparse
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Add src to Python path for imports
_REPO_ROOT = Path(__file__).parent.parent.resolve()
_SRC_DIR = _REPO_ROOT / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# Default output directory
DEFAULT_OUTPUT_DIR = Path("artifacts/docs/api")

# Modules to document (public API surface)
# Start with core modules that are most likely to be importable
MODULES_TO_DOCUMENT = [
    "codex.cli",
    "codex.logging",
]

# Modules that require optional dependencies (gracefully skip if unavailable)
OPTIONAL_MODULES = [
    "codex_ml",  # May require torch and other heavy dependencies
    "codex_ml.peft",
    "codex_ml.distributed",
]


def check_pdoc_installed() -> bool:
    """Check if pdoc3 is installed."""
    try:
        subprocess.run(
            ["pdoc", "--version"],
            capture_output=True,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def install_pdoc() -> None:
    """Install pdoc3 if not already installed."""
    logger.info("Installing pdoc3...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "pdoc3"],
        check=True,
    )
    logger.info("pdoc3 installed successfully")


def filter_modules(modules: list[str]) -> list[str]:
    """Filter modules based on availability.

    Args:
        modules: List of module names to check for importability

    Returns:
        List of modules that are successfully importable
    """
    import importlib.util

    # Check if each module can be imported (without actually importing)
    available_modules = []
    for module in modules:
        spec = importlib.util.find_spec(module)
        if spec is not None:
            available_modules.append(module)
            logger.info(f"✓ Module {module} is importable")
        else:
            logger.warning(f"Skipping {module}: module not found or not importable")

    return available_modules


def build_docs(output_dir: Path, modules: list[str]) -> None:
    """Build API documentation using pdoc3.

    Args:
        output_dir: Directory to write documentation
        modules: List of module names to document
    """
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Clean existing docs
    if output_dir.exists() and any(output_dir.iterdir()):
        logger.info(f"Cleaning existing docs in {output_dir}")
        for item in output_dir.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()

    logger.info(f"Building API docs for modules: {', '.join(modules)}")
    logger.info(f"Output directory: {output_dir.resolve()}")

    # Build documentation with pdoc3
    cmd = [
        "pdoc",
        "--html",
        "--output-dir",
        str(output_dir),
        "--force",
    ]
    cmd.extend(modules)

    # Set PYTHONPATH to include src directory
    env = os.environ.copy()
    pythonpath = env.get("PYTHONPATH", "")
    src_path = str(_SRC_DIR)
    if pythonpath:
        env["PYTHONPATH"] = f"{src_path}:{pythonpath}"
    else:
        env["PYTHONPATH"] = src_path

    logger.debug(f"Running: {' '.join(cmd)}")
    logger.debug(f"PYTHONPATH: {env['PYTHONPATH']}")

    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )
        logger.info("API documentation built successfully")

        # Log output for debugging
        if result.stdout:
            logger.debug(f"pdoc stdout: {result.stdout}")
        if result.stderr:
            logger.debug(f"pdoc stderr: {result.stderr}")

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to build API docs: {e}")
        if e.stdout:
            logger.error(f"stdout: {e.stdout}")
        if e.stderr:
            logger.error(f"stderr: {e.stderr}")
        sys.exit(1)

    # Create index file
    create_index(output_dir, modules)

    logger.info(f"Documentation written to: {output_dir.resolve()}")


def create_index(output_dir: Path, modules: list[str]) -> None:
    """Create an index.html that links to all module documentation.

    Args:
        output_dir: Documentation output directory
        modules: List of documented modules
    """
    index_path = output_dir / "index.html"

    html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Codex API Documentation</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica,
                Arial, sans-serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 0 20px;
            line-height: 1.6;
        }
        h1 {
            border-bottom: 2px solid #e1e4e8;
            padding-bottom: 10px;
        }
        ul {
            list-style: none;
            padding: 0;
        }
        li {
            margin: 10px 0;
        }
        a {
            color: #0366d6;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        .module-link {
            font-size: 1.1em;
            font-weight: 500;
        }
        .description {
            color: #586069;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <h1>Codex API Documentation</h1>
    <p class="description">
        API reference documentation for the Codex ML training, evaluation, and plugin framework.
        This documentation is generated from source code docstrings.
    </p>
    <h2>Modules</h2>
    <ul>
"""

    for module in sorted(modules):
        # pdoc3 creates a directory for each top-level module
        module_dir = module.split(".")[0]
        html_content += (
            f'        <li><a class="module-link" href="{module_dir}/index.html">{module}</a></li>\n'
        )

    html_content += """    </ul>
    <hr>
    <p class="description">
        Generated with <a href="https://pdoc3.github.io/pdoc/">pdoc3</a>.
        For guides and tutorials, see the <a href="../../docs/">main documentation</a>.
    </p>
</body>
</html>
"""

    index_path.write_text(html_content, encoding="utf-8")
    logger.info(f"Created index: {index_path}")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build API documentation for Codex",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory for API docs (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--skip-optional",
        action="store_true",
        help="Skip modules requiring optional dependencies",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Check/install pdoc
    if not check_pdoc_installed():
        logger.info("pdoc3 not found, installing...")
        install_pdoc()

    # Determine which modules to document
    skip_optional = args.skip_optional or os.getenv("CODEX_SKIP_OPTIONAL_IMPORTS") == "1"

    # Combine core modules with optional modules
    all_modules = MODULES_TO_DOCUMENT.copy()
    if not skip_optional:
        all_modules.extend(OPTIONAL_MODULES)

    modules = filter_modules(all_modules)

    if not modules:
        logger.error("No modules available to document")
        sys.exit(1)

    logger.info(f"Final module list to document: {', '.join(modules)}")

    # Build documentation
    build_docs(args.output_dir, modules)

    logger.info("✓ API documentation build complete")


if __name__ == "__main__":
    main()
