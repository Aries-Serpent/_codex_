from pathlib import Path

EXPECTED = [
  ".codex/status", ".codex/notes",
  "audit_artifacts", "_codex_reports", "reports",
  "docs/templates/status/codex_status_template.schema.yaml",
  "tools/status/generate_status_update.py", "noxfile.py", "Dockerfile"
]

def coverage():
    found = 0
    root = Path(".")
    for p in EXPECTED:
        if (root/p).exists():
            found += 1
    return found, len(EXPECTED)
