#!/usr/bin/env python3
"""
Disable remote CI costs by:
- Converting every workflow trigger to `workflow_dispatch`.
- Guarding every job with `if: ${{ false }}`.
- Adding docs/ci.md explaining policy: web search allowed; remote CI disallowed.
Notes:
- Local lint/tests/coverage should run in the Codex Ubuntu environment only.
- This does NOT block analysts from using web search.
"""
from __future__ import annotations
import sys, re, json, datetime as dt
from pathlib import Path

try:
    import yaml  # PyYAML
except Exception:
    print("[WARN] PyYAML not found; attempting minimal regex fallback", file=sys.stderr)
    yaml = None

ROOT = Path.cwd()
WF_DIR = ROOT / ".github" / "workflows"
DOCS = ROOT / "docs"
CODEX = ROOT / ".codex"
ERRORS_MD = CODEX / "errors.md"
ERRORS_ND = CODEX / "errors.ndjson"
CHANGELOG = ROOT / "CHANGELOG_codex.md"


def utcnow():
    return dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def record_error(step, desc, err, ctx=""):
    CODEX.mkdir(parents=True, exist_ok=True)
    msg = f"""Question for ChatGPT-5 {utcnow()}:
While performing [{step}:{desc}], encountered the following error:
{type(err).__name__}: {err}
Context: {ctx}
What are the possible causes, and how can this be resolved while preserving intended functionality?
"""
    ERRORS_MD.write_text((ERRORS_MD.read_text() if ERRORS_MD.exists() else "") + "\n\n" + msg, encoding="utf-8")
    with ERRORS_ND.open("a", encoding="utf-8") as f:
        json.dump({"ts": utcnow(), "step": step, "desc": desc, "error": f"{type(err).__name__}: {err}", "ctx": ctx}, f)
        f.write("\n")


def append_changelog(title, bullets):
    body = "".join([f"- {b}\n" for b in bullets])
    with open(CHANGELOG, "a", encoding="utf-8") as f:
        f.write(f"## {title} — {utcnow()}\n{body}\n")


def hard_guard_jobs(doc: dict) -> int:
    """Add `if: ${{ false }}` to every job."""
    jobs = doc.get("jobs", {}) or {}
    count = 0
    for name, job in jobs.items():
        if isinstance(job, dict):
            if_cond = job.get("if")
            if str(if_cond).strip() != "${{ false }}":
                job["if"] = "${{ false }}"
                count += 1
    doc["jobs"] = jobs
    return count


def set_manual_trigger(doc: dict) -> bool:
    """Replace any `on:` with only workflow_dispatch."""
    changed = False
    on_val = doc.get("on")
    target = {"workflow_dispatch": None}
    if on_val != target:
        doc["on"] = target
        changed = True
    return changed


def patch_yaml(path: Path) -> tuple[bool, int]:
    """Patch a workflow file; return (any_change, jobs_guarded)."""
    text = path.read_text(encoding="utf-8")
    if yaml:
        data = yaml.safe_load(text) or {}
        if not isinstance(data, dict):
            data = {}
        c1 = set_manual_trigger(data)
        c2 = hard_guard_jobs(data)
        if c1 or c2:
            path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
        return (c1 or c2, c2)
    # Fallback (coarse regex) if PyYAML missing
    any_change = False
    # Replace entire on: block with `on:\n  workflow_dispatch:`
    new = re.sub(r"(?ms)^on:\s*(?:.+?)(?=^\S|\Z)", "on:\n  workflow_dispatch:\n", text)
    if new != text:
        any_change = True
        text = new
    # For each job under jobs:, inject if line when missing (best-effort)
    def guard_jobs(txt: str) -> tuple[str, int]:
        jobs_guarded = 0
        pattern = re.compile(r"(?m)^(\s{2}[A-Za-z0-9_.-]+:\s*\n(\s{4}.+\n)*)")
        pos = 0
        out = ""
        for m in pattern.finditer(txt):
            block = m.group(0)
            if "\n    if:" not in block:
                block = block.splitlines()
                indent = "    "
                block.insert(1, f"{indent}if: ${{ false }}")
                jobs_guarded += 1
                block = "\n".join(block) + "\n"
            out += txt[pos:m.start()] + block
            pos = m.end()
        out += txt[pos:]
        return out, jobs_guarded
    text, guarded = guard_jobs(text)
    if any_change or guarded:
        path.write_text(text, encoding="utf-8")
    return (any_change or bool(guarded), guarded)


def write_ci_doc():
    DOCS.mkdir(parents=True, exist_ok=True)
    p = DOCS / "ci.md"
    content = f"""# CI Policy (Codex Environment)

- **Web search:** allowed for research/documentation.
- **Remote CI / GitHub Actions on hosted runners:** **disallowed** by default to avoid cost.
- All workflows in `.github/workflows/` are configured for manual runs only via `workflow_dispatch`, and **every job** is guarded with:
  ```yaml
  if: ${{{{ false }}}}
  ```

This prevents automatic execution on GitHub-hosted runners.

## How to re-enable *manually* (rare)

If you intentionally need to run a workflow, you may replace a job guard with a condition using manual inputs, still via `workflow_dispatch`. See GitHub docs for manual workflows and conditions. ({utcnow()})
"""
    p.write_text(content, encoding="utf-8")
    append_changelog("CI policy docs", [f"Created {p} (web search allowed; remote CI disallowed)"])


def main():
    if not WF_DIR.exists():
        print("[INFO] No workflows directory; nothing to patch.")
        write_ci_doc()
        return
    changed_files = 0
    total_jobs_guarded = 0
    for wf in sorted(WF_DIR.glob("*.y*ml")):
        try:
            changed, guarded = patch_yaml(wf)
            if changed:
                changed_files += 1
                total_jobs_guarded += guarded
        except Exception as e:
            record_error("STEP_06", "Patch workflow triggers/guards", e, ctx=str(wf))
    write_ci_doc()
    append_changelog("Disable remote CI", [
        f"Patched {changed_files} workflow file(s) to `workflow_dispatch` and guarded jobs.",
        f"Total jobs guarded: {total_jobs_guarded}",
    ])
    print(f"[Summary] Patched files: {changed_files} | Jobs guarded: {total_jobs_guarded}")
    print(f"[Docs]    Wrote: {DOCS / 'ci.md'}")
    if ERRORS_MD.exists():
        print(f"[Errors]  See: {ERRORS_MD} and {ERRORS_ND}")


if __name__ == "__main__":
    main()
