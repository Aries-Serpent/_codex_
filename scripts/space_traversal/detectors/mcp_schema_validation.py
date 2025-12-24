from pathlib import Path
import logging
logger = logging.getLogger(__name__)
from typing import Any


def detect(file_index: dict[str, Any]) -> dict[str, Any]:
    """
    Detects schema validation capabilities (Pydantic models, OpenAPI specs) for MCP.
    Looks for BaseModel usage in code and presence of openapi.yaml.
    """
    files = [f.get("path", "") for f in file_index.get("files", [])]
    evidence = []
    found = []
    for path in files:
        if path.endswith(".py"):
            try:
                text = Path(path).read_text(encoding="utf-8", errors="ignore")
            except Exception:
                text = ""
            if "BaseModel" in text or "pydantic" in text:
                evidence.append(path)
                if "BaseModel" in text:
                    found.append("BaseModel")
        # Also check for OpenAPI specification file
        if "openapi.yaml" in path or "openapi.yml" in path:
            evidence.append(path)
            found.append("OpenAPI")
    required = ["BaseModel", "OpenAPI"]
    return {
        "id": "mcp-schema-validation",
        "evidence_files": sorted(set(evidence)),
        "found_patterns": sorted(set(found)),
        "required_patterns": required,
        "docs_keywords": [
            "mcp",
            "schema",
            "validation",
            "pydantic",
            "openapi",
            "basemodel",
            "type-safety",
            "api",
            "specification",
            "contracts",
            "validation",
            "safeguards",
            "security",
        ],
        "meta": {
            "category": "mcp",
            "safeguards": ["validation", "type-safety", "error-handling", "input-sanitization"],
            "detector_version": "1.2",
        },
    }
