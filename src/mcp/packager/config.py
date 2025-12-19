from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PackageConfig:
    name: str
    description: str = ""
    template: str = "base"
    output_dir: str = "./mcp_package"
    python_package: str = "mcp_package"
    entrypoint: str = "app.py"
    include_cli: bool = True
    include_tests: bool = True
    include_docs: bool = True
    include_serverless: bool = False
    serverless_target: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    features: List[str] = field(default_factory=list)
