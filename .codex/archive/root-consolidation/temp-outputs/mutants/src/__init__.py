"""Top-level package marker for Codex platform libraries.

🧭 NAVIGATION HINT: This is the src/ root for library code.
   Key subsystems:
   - src/codex/ - Core CLI and utilities
   - src/codex_ml/ - ML training and evaluation framework
   - src/services/ - Service integrations (GitHub, MCP, workflows)

   IMPORT GUIDANCE (choose based on context):
   - In test files (development / editable install), both forms work:
       ``from src.services.workflow import WorkflowInventory``  (src-prefixed, legacy)
       ``from codex.cli import main``                           (direct-package, preferred)
   - In installed / production environments, ONLY the direct-package style works:
       ``from codex.cli import main``
       ``from mcp.packager.generator import generate_package``
   - pytest.ini `pythonpath = . src` propagates both styles to xdist workers (GAP-001/GAP-011 fix).
   - New code SHOULD prefer `from codex.xxx` / `from mcp.xxx` (no `src.` prefix).

   For a complete navigation guide, see the AGENTS document in the repo root
   and, if present, .codex/ai_agent_manifest.json.
   Tiered Mermaid navigation: see .codex/AGENT_NAVIGATION.md
"""

__all__: list[str] = []
