#!/usr/bin/env python3
import re
from pathlib import Path

SOURCES = [
    ".codex/status/ERROR_CAPTURE_BLOCKS.md",
    ".codex/status/errors.ndjson",
    "docs/troubleshooting/open_questions.md",
    "docs/reference/audit_prompt.md",
    "docs/ops/RUNBOOK.md",
    "docs/validation/status_update_exhaustiveness.md",
    "reports/critical_repo_summary.md",
    "reports/report_templates.md",
]

def iter_questions():
    qpat = re.compile(r"(?:^|\W)(.+\?)\s*$")
    for src in SOURCES:
        p = Path(src)
        if not p.exists(): 
            continue
        for i, line in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            s = line.strip()
            if s.startswith(":::") and "Question for ChatGPT @codex" in s:
                yield (src, i, s)
            else:
                m = qpat.search(s)
                if m:
                    yield (src, i, m.group(1))

def main():
    rows = list(iter_questions())
    out = ["# Open Questions by Capability", ""]
    for n,(src, ln, q) in enumerate(rows, 1):
        out.append(f"- **Q{n:04d}** — {q}  \n  _source:_ `{src}:{ln}`")
    Path("docs/reference").mkdir(parents=True, exist_ok=True)
    Path("docs/reference/open_questions_by_capability.md").write_text("\n".join(out)+"\n", encoding="utf-8")
    print("docs/reference/open_questions_by_capability.md")

if __name__ == "__main__":
    main()
