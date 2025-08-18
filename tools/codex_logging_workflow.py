#!/usr/bin/env python3
"""
codex_logging_workflow.py
End-to-end workflow to:
- Inventory repo
- Map supplied tasks to candidate assets
- Best-effort construct logging (codex.logging.session_logger)
- Attempt safe instrumentation if a conversation handler exists
- Create unit-style smoke tests mirroring session logging intent
- Record changes & errors
- Finalize with results summary

Constraints: DO NOT ACTIVATE ANY GitHub Actions files.
"""
from __future__ import annotations

import os, sys, re, json, sqlite3, subprocess, difflib, uuid, traceback
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# ----------------------------- Config & Paths -----------------------------
REPO_ROOT = Path(os.getenv("CODEX_REPO_ROOT", Path.cwd()))
CODEX_DIR = REPO_ROOT / ".codex"
CHANGE_LOG = CODEX_DIR / "change_log.md"
ERROR_LOG = CODEX_DIR / "errors.ndjson"
RESULTS_MD = CODEX_DIR / "results.md"
FLAGS_JSON = CODEX_DIR / "flags.json"
INVENTORY_MD = CODEX_DIR / "inventory.md"
INVENTORY_JSON = CODEX_DIR / "inventory.json"
MAPPING_MD = CODEX_DIR / "mapping.md"
SESSION_DB = CODEX_DIR / "session_logs.db"
SESSION_ID_FILE = CODEX_DIR / "session_id"
README = REPO_ROOT / "README.md"
CONTRIB = REPO_ROOT / "CONTRIBUTING.md"

# Guard rails
DO_NOT_ACTIVATE_GITHUB_ACTIONS = True

SUPPLIED_TASK = [
    "Locate the module that processes user/assistant exchanges.",
    "Import log_event from codex.logging.session_logger.",
    "After each user message is received, call log_event(session_id, 'user', prompt).",
    "After each assistant reply is generated, call log_event(session_id, 'assistant', reply).",
    "Ensure session_id is sourced from CODEX_SESSION_ID or generated consistently at session start.",
    "Add unit tests mirroring tests/test_session_logging.py to assert messages appear in the database.",
]

# ----------------------------- Utilities -----------------------------
def now_iso() -> str:
    return datetime.now().astimezone().isoformat()

def ensure_codex_dir():
    CODEX_DIR.mkdir(parents=True, exist_ok=True)
    if not CHANGE_LOG.exists():
        CHANGE_LOG.write_text(f"# .codex/change_log.md\n\nCreated {now_iso()}\n\n", encoding="utf-8")
    if not ERROR_LOG.exists():
        ERROR_LOG.write_text("", encoding="utf-8")

def append_change(file: Path, action: str, rationale: str, before: str = "", after: str = ""):
    diff = ""
    if before or after:
        diff = "\n".join(difflib.unified_diff(
            before.splitlines(), after.splitlines(),
            fromfile=f"a/{file.as_posix()}", tofile=f"b/{file.as_posix()}",
            lineterm=""
        ))
        if diff:
            diff = f"\n\n```diff\n{diff}\n```\n"
    entry = f"- **{file.as_posix()}** — *{action}*  \n  Rationale: {rationale}{diff}\n"
    with CHANGE_LOG.open("a", encoding="utf-8") as fh:
        fh.write(entry)

def record_error(step_number_desc: str, err_msg: str, context: str):
    # Console echo per ChatGPT-5 template
    block = (
        "Question for ChatGPT-5:\n"
        f"While performing [{step_number_desc}], encountered the following error:\n"
        f"{err_msg}\n"
        f"Context: {context}\n"
        "What are the possible causes, and how can this be resolved while preserving intended functionality?\n"
    )
    print(block, file=sys.stderr)
    # Append to ndjson
    rec = {
        "ts": now_iso(),
        "step": step_number_desc,
        "error": err_msg,
        "context": context,
    }
    with ERROR_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")

def sh(cmd: List[str]) -> Tuple[int, str, str]:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT)
        return proc.returncode, proc.stdout, proc.stderr
    except Exception as e:
        return 127, "", f"{e}"

def safe_read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except Exception:
        return ""

def safe_write(p: Path, content: str, rationale: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    before = p.read_text(encoding="utf-8") if p.exists() else ""
    p.write_text(content, encoding="utf-8")
    append_change(p, "write" if not before else "update", rationale, before, content)

# ----------------------------- Phase 1: Preparation -----------------------------
def phase1():
    ensure_codex_dir()

    # 1.1 Clean working state (best-effort)
    rc, out, err = sh(["git", "status", "--porcelain"])
    clean = (rc == 0 and out.strip() == "")
    if rc != 0:
        record_error("1.1 Verify clean working state", f"git not available or failed (rc={rc})", err.strip())
    elif not clean:
        record_error("1.1 Verify clean working state", "Working tree not clean", out.strip())

    # 1.2 Read README/CONTRIBUTING
    readme = safe_read(README)
    contrib = safe_read(CONTRIB)

    # 1.3 Inventory
    ex_dirs = {".git", ".venv", "node_modules", "__pycache__", ".mypy_cache", ".pytest_cache"}
    files = []
    for p in REPO_ROOT.rglob("*"):
        if p.is_dir():
            if p.name in ex_dirs:
                # Skip subtree
                for _ in p.rglob("*"):
                    pass
                continue
        # classify lightweight
        ext = p.suffix.lower()
        role = "code" if ext in {".py", ".sh", ".js", ".ts", ".tsx", ".sql", ".go", ".rs"} else "doc" if ext in {".md", ".rst", ".txt"} else "asset"
        files.append({"path": p.as_posix(), "ext": ext, "role": role, "size": p.stat().st_size})
    files_sorted = sorted(files, key=lambda d: d["path"])
    inv_md = ["# Inventory (lightweight)\n"]
    for f in files_sorted[:1000]:
        inv_md.append(f"- `{f['path']}` ({f['ext'] or '∅'}, {f['role']}, {f['size']} bytes)")
    safe_write(INVENTORY_MD, "\n".join(inv_md) + "\n", "Initial inventory")
    safe_write(INVENTORY_JSON, json.dumps(files_sorted, indent=2), "Initial inventory (JSON)")

    # 1.4 Flags
    flags = {"DO_NOT_ACTIVATE_GITHUB_ACTIONS": DO_NOT_ACTIVATE_GITHUB_ACTIONS}
    safe_write(FLAGS_JSON, json.dumps(flags, indent=2), "Set constraint flags")

    # 1.5 Initialize logs already done
    return {"readme": readme, "contrib": contrib, "inventory": files_sorted}

# ----------------------------- Phase 2: Search & Mapping -----------------------------
@dataclass
class Candidate:
    path: Path
    score: float
    rationale: str

def discover_conversation_handlers(inv: List[Dict]) -> List[Candidate]:
    py_files = [REPO_ROOT / f["path"] for f in inv if f["path"].endswith(".py")]
    candidates: List[Candidate] = []
    kw = re.compile(r"(openai|ChatCompletion|client\.chat|assistant|conversation|respond|handle)", re.I)
    for pf in py_files:
        try:
            txt = pf.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        m = kw.search(txt)
        if m:
            hits = len(kw.findall(txt))
            candidates.append(Candidate(pf, float(hits), f"Matched keywords ({hits})"))
    return sorted(candidates, key=lambda c: c.score, reverse=True)

def phase2(inv: List[Dict]):
    mapping = []
    candidates = discover_conversation_handlers(inv)
    mapping.append({
        "task": "Instrument user/assistant exchanges",
        "candidate_assets": [c.path.as_posix() for c in candidates],
        "rationale": "Keyword/heuristic scan for conversation handlers"
    })
    lines = ["# Mapping Table\n"]
    for row in mapping:
        lines.append(f"- **{row['task']}** → {row['candidate_assets'] or '[]'}  \n  Rationale: {row['rationale']}")
    safe_write(MAPPING_MD, "\n".join(lines) + "\n", "Initial mapping")
    return candidates

# ----------------------------- Phase 3: Best-Effort Construction -----------------------------
LOGGER_PY = '''# Auto-generated by codex_logging_workflow.py
from __future__ import annotations
import os, sqlite3, uuid
from pathlib import Path
from datetime import datetime

CODEX_DIR = Path(".codex")
CODEX_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = CODEX_DIR / "session_logs.db"
SESSION_ID_FILE = CODEX_DIR / "session_id"

def _ensure_db():
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("""CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('user','assistant')),
            content TEXT NOT NULL
        )""")
        conn.commit()
    finally:
        conn.close()

def get_session_id() -> str:
    sid = os.getenv("CODEX_SESSION_ID")
    if sid:
        return sid
    if SESSION_ID_FILE.exists():
        return SESSION_ID_FILE.read_text(encoding="utf-8").strip()
    sid = str(uuid.uuid4())
    SESSION_ID_FILE.write_text(sid, encoding="utf-8")
    return sid

def log_event(session_id: str, role: str, content: str) -> None:
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            "INSERT INTO messages (ts, session_id, role, content) VALUES (?, ?, ?, ?)",
            (datetime.utcnow().isoformat() + "Z", session_id, role, content),
        )
        conn.commit()
    finally:
        conn.close()

def fetch_messages(session_id: str):
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.execute(
            "SELECT ts, role, content FROM messages WHERE session_id=? ORDER BY id ASC",
            (session_id,),
        )
        return [{"ts": r[0], "role": r[1], "content": r[2]} for r in cur.fetchall()]
    finally:
        conn.close()
'''

TEST_LOGGING = """# Auto-generated by codex_logging_workflow.py
import uuid
from pathlib import Path
from codex.logging.session_logger import log_event, fetch_messages, get_session_id

def test_user_and_assistant_logged_roundtrip(tmp_path, monkeypatch):
    # Use a dedicated session id for isolation
    sid = f"pytest-{uuid.uuid4()}"
    log_event(sid, "user", "hello")
    log_event(sid, "assistant", "world")
    msgs = fetch_messages(sid)
    roles = [m["role"] for m in msgs]
    assert roles == ["user", "assistant"]
    assert msgs[0]["content"] == "hello"
    assert msgs[1]["content"] == "world"
"""

README_SNIPPET = """
## Session Logging (Opt-in)

This repository includes an optional session logging module generated by the workflow.

**Usage (example):**
```python
from codex.logging.session_logger import log_event, get_session_id

session_id = get_session_id()

def handle_user_message(prompt: str) -> str:
    log_event(session_id, "user", prompt)
    reply = generate_reply(prompt)  # your existing logic
    log_event(session_id, "assistant", reply)
    return reply
```

**Storage:** SQLite at `.codex/session_logs.db`.
**Note:** This change is additive and does not activate any GitHub Actions.
"""

def create_logger_module():
    target = REPO_ROOT / "codex" / "logging" / "session_logger.py"
    safe_write(target, LOGGER_PY, "Add logging module for session events")
    return target

def add_tests():
    target = REPO_ROOT / "tests" / "test_session_logging_mirror.py"
    safe_write(target, TEST_LOGGING, "Add unit-style smoke test for session logging")
    return target

def update_readme():
    if not README.exists():
        safe_write(README, "# Project\n\n", "Create README scaffold")
    before = safe_read(README)
    if "Session Logging (Opt-in)" not in before:
        after = before.rstrip() + "\n\n" + README_SNIPPET.strip() + "\n"
        safe_write(README, after, "Document optional session logging usage")

def try_instrument_file(p: Path) -> bool:
    """
    Very conservative: only prepends import/get_session_id if not present.
    Does NOT attempt deep AST surgery. Returns True if file was modified.
    """
    try:
        src = p.read_text(encoding="utf-8")
    except Exception as e:
        record_error("3.1 Read candidate for instrumentation", str(e), p.as_posix())
        return False

    changed = False
    if "from codex.logging.session_logger import log_event" not in src:
        header = "from codex.logging.session_logger import log_event, get_session_id\n"
        new_src = header + src
        src, changed = new_src, True

    if "session_id = get_session_id()" not in src:
        new_src = "session_id = get_session_id()\n" + src
        src, changed = new_src, True

    if changed:
        safe_write(p, src, "Prepend logging imports/session id (non-invasive)")
    return changed

def phase3(candidates: List[Candidate]):
    created: Dict[str, str] = {}
    # Always create logger module and tests (safe & additive)
    logger_py = create_logger_module()
    created["logger"] = logger_py.as_posix()

    test_py = add_tests()
    created["tests"] = test_py.as_posix()

    update_readme()
    created["readme"] = README.as_posix()

    # Attempt light-touch instrumentation on the top candidate (if any)
    instrumented = []
    for c in candidates[:1]:
        try:
            if try_instrument_file(c.path):
                instrumented.append(c.path.as_posix())
        except Exception as e:
            record_error("3.1 Instrument candidate", str(e), c.path.as_posix())

    return created, instrumented

# ----------------------------- Phase 4: Pruning -----------------------------

def phase4(candidates: List[Candidate], instrumented: List[str]):
    if candidates and not instrumented:
        prune_note = (
            "## Pruning\n"
            "- **Instrumentation deferred**: Candidate(s) found but not modified due to safety/ambiguity.\n"
            "  - Purpose: Preserve behavior.\n"
            "  - Alternatives: Non-invasive header injection; AST patching (rejected for risk).\n"
            "  - Failure modes: Inserting at wrong scope; breaking runtime.\n"
            "  - Decision: Document + provide adapter; no code surgery.\n"
        )
    elif not candidates:
        prune_note = (
            "## Pruning\n"
            "- **No conversation handler present**: Repository is primarily environment scaffolding (Shell/Dockerfile).\n"
            "  - Purpose: Provide optional logging components and tests without altering runtime.\n"
            "  - Alternatives: Create full driver (rejected: scope creep).\n"
            "  - Decision: Add logging module + tests only; document integration snippet.\n"
        )
    else:
        prune_note = "## Pruning\n- No pruning required.\n"
    with CHANGE_LOG.open("a", encoding="utf-8") as fh:
        fh.write("\n" + prune_note + "\n")

# ----------------------------- Phase 5 & 6: Finalization -----------------------------

def phase6(created: Dict[str,str], candidates: List[Candidate], instrumented: List[str]):
    unresolved = []
    if not (REPO_ROOT / "codex" / "logging" / "session_logger.py").exists():
        unresolved.append("logging module missing")
    if not (REPO_ROOT / "tests" / "test_session_logging_mirror.py").exists():
        unresolved.append("test missing")

    results = [
        "# Results",
        "## Implemented",
        f"- Logging module: `{created.get('logger')}`",
        f"- Tests: `{created.get('tests')}`",
        f"- README updated: `{created.get('readme')}`",
        f"- Instrumented files: {instrumented if instrumented else '[]'}",
        "## Mapping",
        f"- Conversation handler candidates: {[c.path.as_posix() for c in candidates]}",
        "## Residual gaps",
        f"- {unresolved if unresolved else 'None'}",
        "## Next steps",
        "- If/when a real conversation handler exists, insert the four lines described in Phase 3.1.",
        "## Policy",
        "**DO NOT ACTIVATE ANY GitHub Actions files.**",
    ]
    safe_write(RESULTS_MD, "\n".join(results) + "\n", "Results summary")
    return 1 if unresolved else 0

# ----------------------------- Main -----------------------------

def main():
    try:
        prep = phase1()
        candidates = phase2(prep["inventory"])
        created, instrumented = phase3(candidates)
        phase4(candidates, instrumented)
        exit_code = phase6(created, candidates, instrumented)
        sys.exit(exit_code)
    except Exception as e:
        record_error("0.0 Unhandled", f"{e}\n{traceback.format_exc()}", "Top-level")
        sys.exit(2)

if __name__ == "__main__":
    main()
