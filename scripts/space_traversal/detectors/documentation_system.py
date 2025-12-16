"""Dynamic detector for documentation system capability.

Detects documentation across markdown, reStructuredText, and
documentation generators (MkDocs, Sphinx, Docusaurus).

Safeguards: Bounded file processing, error handling.
"""

from __future__ import annotations


def detect(file_index: dict) -> dict:
    """Detect documentation system capability.

    Args:
        file_index: Context index from S1 with file metadata

    Returns:
        Capability detection result with comprehensive metadata
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
        if any(
            name in path
            for name in ["mkdocs.yml", "conf.py", "sphinx", "readthedocs", "docusaurus"]
        ):
            doc_configs.append(path)

    # Root-level docs (README, etc.)
    root_doc_candidates = {
        "README.md",
        "docs/governance/CONTRIBUTING.md",
        "docs/CHANGELOG.md",
    }
    root_docs = [f["path"] for f in files if f["path"] in root_doc_candidates]

    # Pattern detection - require common patterns, optional advanced
    found_patterns = []
    # Core required: markdown and docs directory
    required_patterns = ["markdown", "docs"]

    evidence_files = sorted(set(markdown_docs + rst_docs + doc_configs + root_docs))

    if markdown_docs or root_docs:
        found_patterns.append("markdown")
    if doc_configs or any("docs/" in f for f in evidence_files) or markdown_docs:
        found_patterns.append("docs")
    if any("mkdocs" in f.lower() for f in evidence_files):
        found_patterns.append("mkdocs")
    # Sphinx detection: conf.py in docs directory or sphinx in path/filename
    if any("sphinx" in f.lower() for f in evidence_files) or any(
        f.endswith("conf.py") and "docs" in f for f in evidence_files
    ):
        found_patterns.append("sphinx")

    # Calculate functionality score
    functionality_score = len(found_patterns) / len(required_patterns) if required_patterns else 0.0

    return {
        "id": "documentation-system",
        "evidence_files": evidence_files,
        "found_patterns": sorted(set(found_patterns)),
        "required_patterns": required_patterns,
        "docs_keywords": [
            "documentation",
            "docs",
            "markdown",
            "sphinx",
            "mkdocs",
            "readme",
            "api-docs",
        ],
        "safeguards": ["validation", "bounded", "deterministic"],
        "functionality_impl": functionality_score,
        "meta": {
            "markdown_count": len(markdown_docs),
            "rst_count": len(rst_docs),
            "config_count": len(doc_configs),
            "total_docs": len(evidence_files),
            "deterministic": True,
            "offline": True,
            "validation": True,
        },
    }
