"""Dynamic detector for documentation system capability.

Detects documentation across markdown, reStructuredText, and
documentation generators (MkDocs, Sphinx).
"""
from __future__ import annotations


def detect(file_index: dict) -> dict:
    """Detect documentation system capability.

    Args:
        file_index: Context index from S1 with file metadata

    Returns:
        Capability detection result
    """
    files = file_index.get("files", [])

    # Evidence collection
    markdown_docs = []
    rst_docs = []
    doc_configs = []

    for f in files:
        path = f["path"]

        # Markdown documentation
        if path.endswith(".md") and any(path.startswith(p) for p in ["docs/", "documentation/"]):
            markdown_docs.append(path)

        # reStructuredText
        if path.endswith(".rst"):
            rst_docs.append(path)

        # Documentation configs
        if any(name in path for name in ["mkdocs.yml", "conf.py", "sphinx", "readthedocs"]):
            doc_configs.append(path)

    # Root-level docs (README, etc.)
    root_docs = [
        f["path"] for f in files if f["path"] in ["README.md", "CONTRIBUTING.md", "CHANGELOG.md"]
    ]

    # Pattern detection
    found_patterns = []
    required_patterns = ["markdown", "docs", "mkdocs", "sphinx"]

    evidence_files = sorted(set(markdown_docs + rst_docs + doc_configs + root_docs))

    if markdown_docs:
        found_patterns.append("markdown")
    if doc_configs or any("docs/" in f for f in evidence_files):
        found_patterns.append("docs")
    if any("mkdocs" in f for f in evidence_files):
        found_patterns.append("mkdocs")
    if any("sphinx" in f for f in evidence_files):
        found_patterns.append("sphinx")

    return {
        "id": "documentation-system",
        "evidence_files": evidence_files,
        "found_patterns": sorted(set(found_patterns)),
        "required_patterns": required_patterns,
        "meta": {
            "markdown_count": len(markdown_docs),
            "rst_count": len(rst_docs),
            "config_count": len(doc_configs),
            "total_docs": len(evidence_files),
        },
    }
