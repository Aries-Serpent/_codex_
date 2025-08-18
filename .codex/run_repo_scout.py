#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_repo_scout_: Traverse the repo to surface unfinished/missing code and convert errors into
ChatGPT-5 research questions with rich context. SAFE_MODE: writes only under ./.codex/**.

Usage:
  python3 .codex/run_repo_scout.py
"""

import os, sys, re, json, time, shutil, subprocess, textwrap
from pathlib import Path
from datetime import datetime

# -----------------------------
# Phase 1 — Preparation
# -----------------------------

SAFE_MODE = True
DO_NOT_ACTIVATE_GITHUB_ACTIONS = True
START_TS = datetime.utcnow().isoformat() + "Z"
STEPN = 0

def step(n, desc):  # annotate steps in logs
    return f"{n:02d} {desc}"

def now():
    return datetime.utcnow().isoformat() + "Z"

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def write_append(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(content if content.endswith("\n") else content + "\n")

def write_jsonl(path: Path, obj: dict):
    line = json.dumps(obj, ensure_ascii=False)
    write_append(path, line)

def echo_chatgpt5_question(step_number: str, step_desc: str, error_message: str, context: str):
    block = f"""Question for ChatGPT-5:
While performing [{step_number}: {step_desc}], encountered the following error:
{error_message}
Context: {context}
What are the possible causes, and how can this be resolved while preserving intended functionality?"""
    print(block)
    return block

def run_cmd(cmd, cwd, desc, timeout=120):
    """Run a command safely; return (rc, out, err). Capture failures to errors.ndjson and console."""
    global STEPN
    STEPN += 1
    step_id = step(STEPN, desc)
    try:
        p = subprocess.run(
            cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout, check=False
        )
        rc, out, err = p.returncode, p.stdout, p.stderr
        if rc != 0:
            ctx = f"cmd={' '.join(cmd)} cwd={cwd} rc={rc} stderr_head={err[:800]}"
            q = echo_chatgpt5_question(step_id, desc, err.strip()[:1200], ctx)
            write_jsonl(ERRORS, {
                "time": now(), "step": step_id, "desc": desc,
                "cmd": cmd, "cwd": str(cwd), "rc": rc,
                "stdout": out[-1200:], "stderr": err[-2000:],
                "question_for_chatgpt5": q
            })
        return rc, out, err
    except Exception as e:
        ctx = f"cmd={' '.join(cmd)} cwd={cwd} exception={type(e).__name__}"
        q = echo_chatgpt5_question(step_id, desc, str(e), ctx)
        write_jsonl(ERRORS, {
            "time": now(), "step": step_id, "desc": desc,
            "cmd": cmd, "cwd": str(cwd), "exception": repr(e),
            "question_for_chatgpt5": q
        })
        return 1, "", repr(e)

def git_clean_state(repo: Path):
    rc, out, _ = run_cmd(["git", "status", "--porcelain"], repo, "Check working tree clean")
    return rc == 0 and out.strip() == ""

def lang_guess(path: Path):
    ext = path.suffix.lower()
    return {
        ".py": "python", ".js": "javascript", ".ts": "typescript",
        ".sh": "bash", ".sql": "sql", ".html": "html", ".htm": "html",
        ".md": "markdown", ".yml": "yaml", ".yaml": "yaml",
        ".json": "json"
    }.get(ext, "other")

# Resolve repository root
try:
    rc, out, _ = run_cmd(["git", "rev-parse", "--show-toplevel"], Path.cwd(), "Locate git toplevel")
    REPO_ROOT = Path(out.strip()) if rc == 0 and out.strip() else Path.cwd()
except Exception:
    REPO_ROOT = Path.cwd()

CODEX_DIR = REPO_ROOT / ".codex"
ensure_dir(CODEX_DIR)
CHANGELOG = CODEX_DIR / "change_log.md"
ERRORS = CODEX_DIR / "errors.ndjson"
RESULTS = CODEX_DIR / "results.md"
MAPPING = CODEX_DIR / "mapping_table.md"
SMOKE_DIR = CODEX_DIR / "smoke"
ensure_dir(SMOKE_DIR)

write_append(CHANGELOG, f"# Change Log — _repo_scout_  \nStart: {START_TS}\n")
write_append(RESULTS, f"# Results Summary — _repo_scout_  \nStart: {START_TS}\n")
write_append(MAPPING, f"# Mapping Table\nGenerated: {START_TS}\n")

# 1.1 Clean state note
clean = git_clean_state(REPO_ROOT)
if not clean:
    q = echo_chatgpt5_question("01", "Verify clean working state",
                               "Git working directory not clean.",
                               "Run `git status --porcelain`; uncommitted changes may affect traversal.")
    write_jsonl(ERRORS, {"time": now(), "step": "01", "desc": "Working tree dirty",
                         "question_for_chatgpt5": q})

# 1.2 Load guardrails (best effort)
README_PATHS = [p for p in REPO_ROOT.glob("README*") if p.is_file()]
CONTRIB_PATHS = [p for p in REPO_ROOT.glob("CONTRIBUTING*") if p.is_file()]

# 1.3 Inventory
IGNORE_DIRS = {".git", ".github/workflows", "node_modules", "dist", "build",
               ".venv", "__pycache__", ".tox", ".mypy_cache"}
INVENTORY = CODEX_DIR / "inventory.ndjson"

def should_skip_dir(p: Path):
    parts = set(p.parts)
    return any(seg in IGNORE_DIRS for seg in parts)

for root, dirs, files in os.walk(REPO_ROOT):
    # prevent descending into ignored dirs
    dirs[:] = [d for d in dirs if not should_skip_dir(Path(root) / d)]
    for f in files:
        path = Path(root) / f
        if CODEX_DIR in path.parents:
            continue
        if any(seg == ".github" for seg in path.parts) and "workflows" in path.parts:
            # read-only awareness only; never modify
            continue
        rel = path.relative_to(REPO_ROOT)
        role_hint = "code" if lang_guess(path) in {"python","javascript","typescript","bash","sql","html"} else "other"
        write_jsonl(INVENTORY, {"path": str(rel), "lang": lang_guess(path), "role": role_hint})

write_append(CHANGELOG, "- Created `.codex/inventory.ndjson` (repo walk, safe mode).")

# -----------------------------
# Phase 2 — Search & Mapping
# -----------------------------

UNFINISHED_PATTERNS = [
    r"\bTODO\b", r"\bFIXME\b", r"\bTBD\b", r"\bWIP\b", r"\bHACK\b",
    r"NOT\s+IMPLEMENTED", r"\bPLACEHOLDER\b", r"\bSTUB\b", r"\bPENDING\b",
]
LANG_SPECIFIC = {
    "python": [r"raise\s+NotImplementedError", r"^\s*pass\s*(#.*)?$", r"assert\s+False"],
    "javascript": [r"throw\s+new\s+Error\(['\"]TODO", r"function\s+\w+\(.*\)\s*{\s*}", r"=>\s*{\s*}"],
    "typescript": [r"throw\s+new\s+Error\(['\"]TODO", r"function\s+\w+\(.*\)\s*{\s*}", r"=>\s*{\s*}"],
    "bash": [r"^\s*\w+\s*\(\)\s*{\s*:\s*;?\s*}$"],
    "sql": [r"--\s*TODO", r"/\*\s*TODO"],
    "html": [r"<!--\s*TODO"]
}
unfinished_hits = []
kloc_total = 0

def read_text_safe(p: Path):
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""

for item in json.loads("[" + ",".join([l.strip() for l in INVENTORY.read_text(encoding="utf-8").splitlines()]) + "]"):
    fpath = REPO_ROOT / item["path"]
    lang = item["lang"]
    if not fpath.is_file():
        continue
    text = read_text_safe(fpath)
    if not text:
        continue
    lines = text.splitlines()
    kloc_total += max(1, len(lines)) / 1000.0
    # general patterns
    for i, line in enumerate(lines, 1):
        if any(re.search(pat, line) for pat in UNFINISHED_PATTERNS):
            unfinished_hits.append({"path": item["path"], "line": i, "lang": lang, "snippet": line.strip()})
    # lang-specific
    for pat in LANG_SPECIFIC.get(lang, []):
        for i, line in enumerate(lines, 1):
            if re.search(pat, line):
                unfinished_hits.append({"path": item["path"], "line": i, "lang": lang, "snippet": line.strip()})

# Rank by a simple heuristic Fitness: F = α*C + β*S + γ*R − δ*D
# For this static scout we approximate:
# C=1 (unknown), S=#markers in file normalized, R~ path depth inverse, D=0 (unknown).
file_signal = {}
for hit in unfinished_hits:
    file_signal.setdefault(hit["path"], 0)
    file_signal[hit["path"]] += 1

def path_centrality(path: str):
    depth = len(Path(path).parts)
    return 1.0 / (1 + depth)

alpha, beta, gamma, delta = 0.1, 0.7, 0.2, 0.0
ranked = []
for p, s in file_signal.items():
    F = alpha*1.0 + beta*(s) + gamma*path_centrality(p) - delta*0.0
    ranked.append((F, p, s))
ranked.sort(reverse=True)

write_append(MAPPING, "## Task → Candidate Assets → Rationale\n")
if ranked:
    write_append(MAPPING, "| Rank | File | Score F | Signal S | Rationale |")
    write_append(MAPPING, "|---:|---|---:|---:|---|")
    for idx, (F, p, s) in enumerate(ranked[:200], 1):
        rationale = "High unfinished markers; central path weight."
        write_append(MAPPING, f"| {idx} | `{p}` | {F:.2f} | {s} | {rationale} |")
else:
    write_append(MAPPING, "_No unfinished candidates detected by heuristics._")

write_append(CHANGELOG, "- Generated `.codex/mapping_table.md` with ranked candidates.")

# -----------------------------
# Phase 3 — Best-Effort Construction
# -----------------------------

ensure_dir(SMOKE_DIR)
IMPORT_CHECK = SMOKE_DIR / "import_check.py"

# Create minimal, non-intrusive Python import smoke (guarded)
py_targets = [x["path"] for x in json.loads("[" + ",".join([l.strip() for l in INVENTORY.read_text(encoding="utf-8").splitlines()]) + "]") if x["lang"]=="python" and x["path"].endswith(".py")]
if py_targets:
    body = ["# Auto-generated SAFE import smoke; avoids side effects by try/except.\n",
            "import importlib, traceback, sys\n",
            "failures = []\n",
            "targets = []\n"]
    # Try top-level modules inferred from file paths under repo root
    for p in py_targets:
        mod = Path(p).with_suffix("").name
        # skip dunder and tests by default; import only simple module names
        if mod.startswith("_"):
            continue
        # best-effort guard
        body.append(f"targets.append({json.dumps(mod)})\n")
    body += [
        "for name in sorted(set(targets)):\n",
        "    try:\n",
        "        importlib.import_module(name)\n",
        "    except Exception as e:\n",
        "        failures.append((name, ''.join(traceback.format_exception_only(type(e), e)).strip()))\n",
        "if failures:\n",
        "    print('IMPORT_SMOKE_FAILURES:')\n",
        "    for n, msg in failures:\n",
        "        print(f'{n}: {msg}')\n",
        "    sys.exit(2)\n",
        "print('IMPORT_SMOKE_OK')\n"
    ]
    IMPORT_CHECK.write_text("".join(body), encoding="utf-8")
    write_append(CHANGELOG, "- Created `.codex/smoke/import_check.py` (non-intrusive).")

# Tool-assisted checks (only if locally available)
def has_tool(name):
    return shutil.which(name) is not None

tool_failures = 0

# Python: ruff
if any(p.endswith(".py") for p in py_targets) and has_tool("ruff"):
    rc, out, err = run_cmd(["ruff", "check", "--quiet", "."], REPO_ROOT, "Run ruff check (if present)")
    if rc != 0:
        tool_failures += 1

# Python: flake8 (fallback)
if any(p.endswith(".py") for p in py_targets) and has_tool("flake8"):
    rc, out, err = run_cmd(["flake8", "."], REPO_ROOT, "Run flake8 (if present)")
    if rc != 0:
        tool_failures += 1

# Python: pyflakes
if any(p.endswith(".py") for p in py_targets) and (has_tool("pyflakes") or shutil.which(sys.executable)):
    # try module invocation
    rc, out, err = run_cmd([sys.executable, "-m", "pyflakes", "."], REPO_ROOT, "Run pyflakes (if present)")
    if rc != 0:
        tool_failures += 1

# Python: pytest if tests exist
tests_exist = any(Path(p).parts[0].lower().startswith("tests") for p in py_targets)
if tests_exist and has_tool("pytest"):
    rc, out, err = run_cmd(["pytest", "-q"], REPO_ROOT, "Run pytest -q (if present)")
    if rc != 0:
        tool_failures += 1

# Bash: shellcheck
bash_files = [x["path"] for x in json.loads("[" + ",".join([l.strip() for l in INVENTORY.read_text(encoding="utf-8").splitlines()]) + "]") if x["lang"]=="bash" and x["path"].endswith(".sh")]
if bash_files and has_tool("shellcheck"):
    for bf in bash_files:
        rc, out, err = run_cmd(["shellcheck", bf], REPO_ROOT, f"Shellcheck {bf}")
        if rc != 0:
            tool_failures += 1

# SQL: sqlfluff
sql_files = [x["path"] for x in json.loads("[" + ",".join([l.strip() for l in INVENTORY.read_text(encoding="utf-8").splitlines()]) + "]") if x["lang"]=="sql" and x["path"].endswith(".sql")]
if sql_files and has_tool("sqlfluff"):
    rc, out, err = run_cmd(["sqlfluff", "lint", "."], REPO_ROOT, "Run sqlfluff lint (if present)")
    if rc != 0:
        tool_failures += 1

# HTML: tidy
html_files = [x["path"] for x in json.loads("[" + ",".join([l.strip() for l in INVENTORY.read_text(encoding="utf-8").splitlines()]) + "]") if x["lang"]=="html"]
if html_files and has_tool("tidy"):
    for hf in html_files:
        rc, out, err = run_cmd(["tidy", "-qe", hf], REPO_ROOT, f"tidy -qe {hf}")
        if rc != 0:
            tool_failures += 1

# README hygiene (non-destructive): broken relative links → suggestions
READMES = README_PATHS
BROKEN = []
link_re = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
for rp in READMES:
    txt = read_text_safe(rp)
    for m in link_re.finditer(txt):
        label, target = m.group(1), m.group(2)
        if "://" in target:
            continue
        target_path = (rp.parent / target).resolve()
        if not target_path.exists():
            BROKEN.append({"readme": str(rp.relative_to(REPO_ROOT)), "label": label, "target": target})
if BROKEN:
    RU = REPO_ROOT / ".codex/readme_updates.md"
    write_append(RU, "## Suggested README Fixes (non-destructive)\n")
    for b in BROKEN:
        write_append(RU, f"- `{b['readme']}`: Link label **{b['label']}** → missing target `{b['target']}`. Suggest verifying path or removing.")
    write_append(CHANGELOG, "- Added `.codex/readme_updates.md` with suggested README link fixes.")

# -----------------------------
# Phase 4 — Controlled Pruning
# -----------------------------

# For this SAFE run, we only consider duplicate smoke files in .codex/smoke
# (No pruning performed unless duplicates are found).
write_append(CHANGELOG, "## Pruning\n- No pruning performed (SAFE_MODE).")

# -----------------------------
# Phase 5 — Error Capture (already integrated)
# -----------------------------

# -----------------------------
# Phase 6 — Finalization
# -----------------------------

unfinished_count = len(unfinished_hits)
U = (unfinished_count / max(1.0, kloc_total))  # Unfinishedness per KLoC
kappa = 0.02  # scaling constant for readability
K = 1.0 - min(1.0, U * kappa)

write_append(RESULTS, "## Unfinished/Missing Code Findings\n")
write_append(RESULTS, f"- Files with signals: **{len(file_signal)}**")
write_append(RESULTS, f"- Total markers detected: **{unfinished_count}**")
write_append(RESULTS, f"- KLoC (approx): **{kloc_total:.2f}**")
write_append(RESULTS, f"- Unfinishedness Index U: **{U:.2f}**")
write_append(RESULTS, f"- Completeness Score K: **{K:.2f}** (K = 1 − min(1, U·{kappa}))\n")

if unfinished_hits:
    write_append(RESULTS, "### Sample Findings (first 50)\n")
    write_append(RESULTS, "| File | Line | Lang | Snippet |")
    write_append(RESULTS, "|---|---:|---|---|")
    for h in unfinished_hits[:50]:
        sn = h["snippet"].replace("|", "\\|")[:180]
        write_append(RESULTS, f"| `{h['path']}` | {h['line']} | {h['lang']} | `{sn}` |")
else:
    write_append(RESULTS, "_No unfinished code markers detected by heuristics._\n")

if tool_failures > 0:
    write_append(RESULTS, f"### Tooling\n- One or more linters/tests reported issues. See `.codex/errors.ndjson`.")

# Final statements & constraints
write_append(RESULTS, "\n**Constraint:** DO NOT ACTIVATE ANY GitHub Actions files.\n")
write_append(CHANGELOG, "- Finalized results.md and metrics.")
print("DONE. See ./.codex/ for outputs.")

# Exit code: non-zero if unresolved errors exist
exit_code = 0
if ERRORS.exists() and (ERROR_S := ERRORS.read_text(encoding="utf-8").strip()):
    # a non-empty errors.ndjson -> unresolved
    exit_code = 2
sys.exit(exit_code)
