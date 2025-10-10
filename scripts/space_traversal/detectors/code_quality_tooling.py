"""Dynamic detector for code quality tooling capability.

Detects linters (Ruff, Flake8), formatters (Black), type checkers
(mypy), security scanners (Semgrep), and related configurations.
"""
from __future__ import annotations


def detect(file_index: dict) -> dict:
    """Detect code quality tooling capability.

    Args:
        file_index: Context index from S1 with file metadata

    Returns:
        Capability detection result
    """
    files = file_index.get("files", [])

    # Evidence collection
    formatter_configs = []
    linter_configs = []
    type_check_configs = []
    security_tools = []
    quality_scripts = []

    for f in files:
        path = f["path"]

        # Formatters (Black, autopep8, YAPF)
        if any(kw in path.lower() for kw in ["black", "autopep8", "yapf", ".editorconfig"]):
            formatter_configs.append(path)

        # Linters (Ruff, Flake8, Pylint)
        if (
            any(
                name in path
                for name in [
                    "ruff.toml",
                    ".flake8",
                    "pylintrc",
                    ".pylintrc",
                    "setup.cfg",
                ]
            )
            or "ruff" in path.lower()
        ):
            linter_configs.append(path)

        # Type checkers (mypy)
        if any(name in path for name in ["mypy.ini", ".mypy.ini", "pyproject.toml"]):
            type_check_configs.append(path)

        # Security tools (Semgrep, Bandit)
        if any(kw in path.lower() for kw in ["semgrep", "bandit", "safety", "security"]):
            security_tools.append(path)

        # Quality scripts
        if any(
            kw in path.lower() for kw in ["lint", "format", "check_", "validate_", "quality"]
        ) and path.endswith((".py", ".sh")):
            quality_scripts.append(path)

    # Pattern detection
    found_patterns = []
    required_patterns = ["lint", "format", "type-check", "security-scan", "quality"]

    evidence_files = sorted(
        set(
            formatter_configs
            + linter_configs
            + type_check_configs
            + security_tools
            + quality_scripts
        )
    )

    if linter_configs or any("ruff" in f.lower() for f in evidence_files):
        found_patterns.append("lint")
    if formatter_configs or any("black" in f.lower() for f in evidence_files):
        found_patterns.append("format")
    if type_check_configs or any("mypy" in f.lower() for f in evidence_files):
        found_patterns.append("type-check")
    if security_tools:
        found_patterns.append("security-scan")
    if quality_scripts or evidence_files:
        found_patterns.append("quality")

    return {
        "id": "code-quality-tooling",
        "evidence_files": evidence_files,
        "found_patterns": sorted(set(found_patterns)),
        "required_patterns": required_patterns,
        "meta": {
            "formatters": len(formatter_configs),
            "linters": len(linter_configs),
            "type_checkers": len(type_check_configs),
            "security_scanners": len(security_tools),
            "quality_scripts": len(quality_scripts),
        },
    }
