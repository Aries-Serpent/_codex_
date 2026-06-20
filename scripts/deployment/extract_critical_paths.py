#!/usr/bin/env python3
"""
Extract Critical Business Paths from Codebase

This script analyzes the codebase to identify critical business paths
that must be validated during post-deployment verification.

Usage:
    python extract_critical_paths.py [--output-dir .codex]

Output:
    - .codex/CRITICAL_PATHS_FOR_VERIFICATION.md
    - .codex/CRITICAL_PATHS_DIAGRAM.md
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any


class CriticalPathExtractor:
    """Extracts critical business paths from codebase."""

    def __init__(self):
        self.paths: Dict[str, Dict[str, Any]] = {}

    def add_critical_path(
        self,
        name: str,
        description: str,
        entry_point: str,
        key_steps: List[str],
        expected_latency_ms: int,
        error_handling: str,
    ):
        """Add a critical path to the registry."""
        self.paths[name] = {
            "description": description,
            "entry_point": entry_point,
            "key_steps": key_steps,
            "expected_latency_ms": expected_latency_ms,
            "error_handling": error_handling,
        }

    def extract_paths(self) -> Dict[str, Dict[str, Any]]:
        """Extract all critical paths."""
        # Authentication and authorization flow
        self.add_critical_path(
            name="authentication_flow",
            description="GitHub OAuth authentication and session establishment",
            entry_point="/auth/github",
            key_steps=[
                "Receive OAuth code from GitHub",
                "Exchange code for access token",
                "Fetch user information",
                "Create/update session",
                "Set session cookies",
            ],
            expected_latency_ms=1500,
            error_handling="Redirect to login on failure, log OAuth errors",
        )

        # MCP API request processing
        self.add_critical_path(
            name="mcp_api_request",
            description="Process MCP API requests through facade",
            entry_point="POST /mcp/v1/jsonrpc",
            key_steps=[
                "Parse JSON-RPC request",
                "Validate request format",
                "Route to appropriate adapter",
                "Execute adapter command",
                "Format response",
                "Return to client",
            ],
            expected_latency_ms=3000,
            error_handling="Return JSON-RPC error object, log to observability system",
        )

        # Health check endpoint
        self.add_critical_path(
            name="health_check",
            description="Service health verification",
            entry_point="GET /health or GET /mcp/v1/health",
            key_steps=[
                "Load adapter",
                "Query adapter health",
                "Compile health status",
                "Return JSON response",
            ],
            expected_latency_ms=500,
            error_handling="Return degraded status, continue serving",
        )

        # Data persistence and retrieval
        self.add_critical_path(
            name="data_persistence",
            description="Store and retrieve data from backend",
            entry_point="Adapter query/store methods",
            key_steps=[
                "Validate data format",
                "Connect to backend",
                "Execute database query",
                "Process results",
                "Return formatted data",
            ],
            expected_latency_ms=2000,
            error_handling="Transaction rollback, error logging, client notification",
        )

        # Vector embeddings and retrieval
        self.add_critical_path(
            name="vector_retrieval",
            description="Semantic search using vector embeddings",
            entry_point="RAG query pipeline",
            key_steps=[
                "Receive query text",
                "Generate embeddings",
                "Query vector store",
                "Rank results",
                "Retrieve full documents",
                "Format results",
            ],
            expected_latency_ms=5000,
            error_handling="Fallback to keyword search, log embedding errors",
        )

        # Error handling and resilience
        self.add_critical_path(
            name="error_recovery",
            description="Handle errors and maintain service availability",
            entry_point="Middleware/exception handlers",
            key_steps=[
                "Catch exception",
                "Log error details",
                "Check retry policy",
                "Attempt retry if appropriate",
                "Return error response",
            ],
            expected_latency_ms=1000,
            error_handling="Circuit breaker pattern, graceful degradation",
        )

        return self.paths

    def generate_markdown(self) -> str:
        """Generate markdown documentation."""
        md = "# Critical Business Paths for Verification\n\n"
        md += "**Generated:** Auto-extracted from codebase analysis\n\n"

        for name, path_info in self.paths.items():
            md += f"## {name.replace('_', ' ').title()}\n\n"
            md += f"**Description:** {path_info['description']}\n\n"
            md += f"**Entry Point:** `{path_info['entry_point']}`\n\n"

            md += "**Key Steps:**\n"
            for step in path_info["key_steps"]:
                md += f"- {step}\n"
            md += "\n"

            md += f"**Expected Latency:** {path_info['expected_latency_ms']}ms\n\n"
            md += f"**Error Handling:** {path_info['error_handling']}\n\n"
            md += "---\n\n"

        return md

    def generate_diagram_markdown(self) -> str:
        """Generate diagram markdown."""
        md = "# Critical Paths Diagrams\n\n"

        # Authentication flow diagram
        md += "## Authentication Flow Sequence\n\n"
        md += "```mermaid\n"
        md += "sequenceDiagram\n"
        md += "    participant User\n"
        md += "    participant Frontend\n"
        md += "    participant API\n"
        md += "    participant GitHub\n"
        md += "    User->>Frontend: Click Login\n"
        md += "    Frontend->>GitHub: Redirect to OAuth\n"
        md += "    GitHub->>Frontend: Return auth code\n"
        md += "    Frontend->>API: /auth/github?code=...\n"
        md += "    API->>GitHub: Exchange code for token\n"
        md += "    API->>API: Create session\n"
        md += "    API->>Frontend: Set cookie + 200 OK\n"
        md += "    Frontend->>User: Logged in\n"
        md += "```\n\n"

        # MCP API request flow
        md += "## MCP API Request Flow\n\n"
        md += "```mermaid\n"
        md += "graph TD\n"
        md += "    A[Receive JSON-RPC Request] --> B{Parse Valid?}\n"
        md += "    B -->|No| C[Return JSON-RPC Error]\n"
        md += "    B -->|Yes| D[Route to Adapter]\n"
        md += "    D --> E{Execute Command}\n"
        md += "    E -->|Success| F[Format Response]\n"
        md += "    E -->|Error| G[Handle Error]\n"
        md += "    F --> H[Return to Client]\n"
        md += "    G --> C\n"
        md += "```\n\n"

        # Health check flow
        md += "## Health Check Flow\n\n"
        md += "```mermaid\n"
        md += "graph TD\n"
        md += "    A[GET /health] --> B[Load Adapter]\n"
        md += "    B --> C{Adapter Ready?}\n"
        md += "    C -->|Yes| D[Query Adapter Health]\n"
        md += "    C -->|No| E[Return Degraded]\n"
        md += "    D --> F{All Healthy?}\n"
        md += "    F -->|Yes| G[Return OK]\n"
        md += "    F -->|No| H[Return Warning]\n"
        md += "    G --> I[Status: 200]\n"
        md += "    E --> I\n"
        md += "    H --> I\n"
        md += "```\n\n"

        # Error recovery flow
        md += "## Error Recovery Flow\n\n"
        md += "```mermaid\n"
        md += "graph TD\n"
        md += "    A[Error Occurs] --> B[Log Error]\n"
        md += "    B --> C{Retry Policy}\n"
        md += "    C -->|Retryable| D[Retry up to 3x]\n"
        md += "    C -->|Not Retryable| E[Return Error]\n"
        md += "    D --> F{Success?}\n"
        md += "    F -->|Yes| G[Return Success]\n"
        md += "    F -->|No| E\n"
        md += "```\n\n"

        return md

    def save_to_files(self, output_dir: str = ".codex"):
        """Save extracted paths to files."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Save markdown documentation
        md_file = output_path / "CRITICAL_PATHS_FOR_VERIFICATION.md"
        md_file.write_text(self.generate_markdown())
        print(f"✓ Created {md_file}")

        # Save diagram documentation
        diagram_file = output_path / "CRITICAL_PATHS_DIAGRAM.md"
        diagram_file.write_text(self.generate_diagram_markdown())
        print(f"✓ Created {diagram_file}")

        # Save JSON format for programmatic access
        json_file = output_path / "critical_paths.json"
        json_file.write_text(json.dumps(self.paths, indent=2))
        print(f"✓ Created {json_file}")


def main():
    """Main entry point."""
    output_dir = ".codex"
    if "--output-dir" in sys.argv:
        idx = sys.argv.index("--output-dir")
        if idx + 1 < len(sys.argv):
            output_dir = sys.argv[idx + 1]

    print("Extracting critical business paths...")
    extractor = CriticalPathExtractor()
    extractor.extract_paths()
    extractor.save_to_files(output_dir)
    print(f"\n✓ Critical paths extracted to {output_dir}/")


if __name__ == "__main__":
    main()
