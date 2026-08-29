"""Handler for the mypy.manager built-in skill.

Classifies mypy errors by fix-pattern, applies automated fixes where safe,
tracks .mypy_baseline regressions, and logs all patterns to the PDA Loop.

Fix Patterns
------------
MYPY-OPT-IMPORT     Optional-import fallback ``= None`` missing ``type: ignore``
MYPY-REDUNDANT-CAST ``cast(T, expr)`` where expr is already type T
MYPY-UNUSED-IGNORE  Superfluous ``# type: ignore[...]`` comment
MYPY-CIPHER-UNION   ``self.cipher`` typed as single cipher; needs Union annotation
MYPY-UNION-NARROW   ``private_key.sign(...)`` on full Union — needs isinstance guard
MYPY-NONE-GUARD     ``obj.attr`` where obj can be None — needs explicit None check
MYPY-ARG-NONE       ``dict.get(key)`` where key is ``str | None`` — needs str guard
MYPY-ARG-TYPE       Type passed to constructor/call doesn't match annotation
MYPY-NO-REDEF       Function/var re-defined in except-ImportError fallback block
MYPY-TYPEDDICT      ``TypedDict(**dict[str, Any])`` expansion — needs ignore
MYPY-IMPORT-UNTYPED Package installed without type stubs — needs stubs or ignore
MYPY-STRUCTURAL     Other structural type error — manual review required
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Pattern catalogue — ordered by priority
# ---------------------------------------------------------------------------

# Each rule: regex matched against the mypy error message (not the code),
# a stable pattern-ID, whether an automated fix is available, and a
# human-readable fix description.

_RULES: list[dict[str, Any]] = [
    # ── Redundant cast ────────────────────────────────────────────────────────
    {
        "pattern": "MYPY-REDUNDANT-CAST",
        "code": "redundant-cast",
        "regex": re.compile(r"Redundant cast", re.I),
        "fix_available": True,
        "fix_description": "Remove cast(T, expr) wrapper — expression already has correct type.",
    },
    # ── Optional-import fallback = None ──────────────────────────────────────
    {
        "pattern": "MYPY-OPT-IMPORT",
        "code": "assignment",
        "regex": re.compile(
            r"Incompatible types in assignment.*expression has type \"None\""
            r"|Cannot assign to a type.*\[misc\]"
            r"|Cannot assign multiple types to name",
            re.I,
        ),
        "fix_available": True,
        "fix_description": (
            "Add  # type: ignore[assignment]  to the fallback ``= None`` "
            "line in the except-ImportError block."
        ),
    },
    # ── Function re-defined in fallback block ─────────────────────────────────
    {
        "pattern": "MYPY-NO-REDEF",
        "code": "no-redef",
        "regex": re.compile(r"Name .* already defined", re.I),
        "fix_available": True,
        "fix_description": (
            "Add  # type: ignore[no-redef]  to the fallback function/variable "
            "re-definition in the except block."
        ),
    },
    # ── Multi-cipher Union annotation ────────────────────────────────────────
    {
        "pattern": "MYPY-CIPHER-UNION",
        "code": "assignment",
        "regex": re.compile(r"Incompatible types in assignment.*AESGCM|ChaCha20|Fernet", re.I),
        "fix_available": True,
        "fix_description": (
            "Annotate self.cipher as Union[Fernet, AESGCM, ChaCha20Poly1305] "
            "before the if/elif assignment block."
        ),
    },
    # ── Union member missing attribute / too many args ───────────────────────
    {
        "pattern": "MYPY-UNION-NARROW",
        "code": "union-attr",
        "regex": re.compile(
            r'Item "(?:DHPrivateKey|X25519PrivateKey|X448PrivateKey|Ed[0-9]+PrivateKey)'
            r".*has no attribute",
            re.I,
        ),
        "fix_available": True,
        "fix_description": (
            "Narrow private_key to RSAPrivateKey with isinstance() guard before "
            "calling .sign(signing_input, PKCS1v15(), SHA256())."
        ),
    },
    # ── None guard ────────────────────────────────────────────────────────────
    {
        "pattern": "MYPY-NONE-GUARD",
        "code": "union-attr",
        "regex": re.compile(r'Item "None".*has no attribute', re.I),
        "fix_available": True,
        "fix_description": (
            "Guard the attribute access: ``if obj is not None: use obj.attr``"
            " or ``obj.attr if obj is not None else default``."
        ),
    },
    # ── dict.get() with str | None key ───────────────────────────────────────
    {
        "pattern": "MYPY-ARG-NONE",
        "code": "arg-type",
        "regex": re.compile(r'Argument 1 to "get" of "dict".*expected "str"', re.I),
        "fix_available": True,
        "fix_description": (
            "Guard the key: ``dict.get(key)`` where key is ``str | None`` → "
            "use ``dict.get(key or '')`` or add an explicit ``if key:`` guard."
        ),
    },
    # ── TypedDict ** expansion ────────────────────────────────────────────────
    {
        "pattern": "MYPY-TYPEDDICT",
        "code": "typeddict-item",
        "regex": re.compile(r"Unsupported type.*for \*\* expansion in TypedDict", re.I),
        "fix_available": True,
        "fix_description": (
            "Add  # type: ignore[typeddict-item]  to the TypedDict(**config) call; "
            "the runtime narrowing is safe but mypy cannot verify dict[str, Any] → TypedDict."
        ),
    },
    # ── arg-type (schedule_cron list[Any | None] → list[str]) ─────────────────
    {
        "pattern": "MYPY-ARG-TYPE",
        "code": "arg-type",
        "regex": re.compile(r"Argument.*has incompatible type", re.I),
        "fix_available": True,
        "fix_description": (
            "Cast or filter the value to match the expected type. "
            "E.g. list[Any | None] → [x for x in xs if x is not None]."
        ),
    },
    # ── call-arg ──────────────────────────────────────────────────────────────
    {
        "pattern": "MYPY-CALL-ARG",
        "code": "call-arg",
        "regex": re.compile(r"Missing named argument|Too many arguments for", re.I),
        "fix_available": True,
        "fix_description": (
            "Add missing required argument to constructor/call, or add "
            "# type: ignore[call-arg] if the argument has a Pydantic Field default "
            "that mypy cannot see without the pydantic plugin."
        ),
    },
    # ── Unused type: ignore ──────────────────────────────────────────────────
    {
        "pattern": "MYPY-UNUSED-IGNORE",
        "code": "unused-ignore",
        "regex": re.compile(r'Unused "type: ignore', re.I),
        "fix_available": True,
        "fix_description": (
            "Remove the # type: ignore comment — the error it was suppressing "
            "no longer fires (stubs installed or code changed)."
        ),
    },
    # ── import-untyped ────────────────────────────────────────────────────────
    {
        "pattern": "MYPY-IMPORT-UNTYPED",
        "code": "import-untyped",
        "regex": re.compile(r"Library stubs not installed for", re.I),
        "fix_available": True,
        "fix_description": (
            "Install type stubs (pip install types-<pkg>) OR add "
            "# type: ignore[import-untyped] to the import line."
        ),
    },
    # ── Structural catch-all ──────────────────────────────────────────────────
    {
        "pattern": "MYPY-STRUCTURAL",
        "code": "_other",
        "regex": re.compile(r".*"),  # matches anything
        "fix_available": False,
        "fix_description": "Manual review required — no automated fix available.",
    },
]

# Regex to parse a mypy error line
_ERROR_RE = re.compile(
    r"^(?P<file>[^:]+):(?P<line>\d+): error: (?P<message>.+?)(?:\s+\[(?P<code>[^\]]+)\])?$"
)

# ---------------------------------------------------------------------------
# Helper — locate repo root
# ---------------------------------------------------------------------------


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]  # src/codex/skills/mypy_manager → root


# ---------------------------------------------------------------------------
# Parse mypy output into structured records
# ---------------------------------------------------------------------------


def _parse_errors(raw: str) -> list[dict[str, Any]]:
    """Parse raw mypy stdout into a list of error dicts."""
    errors: list[dict[str, Any]] = []
    for line in raw.splitlines():
        m = _ERROR_RE.match(line.strip())
        if not m:
            continue
        file_path = m.group("file")
        line_no = int(m.group("line"))
        message = m.group("message")
        code = m.group("code") or "_unknown"

        # Classify by pattern
        pattern = "MYPY-STRUCTURAL"
        fix_available = False
        fix_description = "Manual review required."
        for rule in _RULES:
            if rule["code"] in (code, "_other") and rule["regex"].search(message):
                pattern = rule["pattern"]
                fix_available = rule["fix_available"]
                fix_description = rule["fix_description"]
                break

        errors.append(
            {
                "file": file_path,
                "line": line_no,
                "code": code,
                "message": message,
                "pattern": pattern,
                "fix_available": fix_available,
                "fix_description": fix_description,
            }
        )
    return errors


# ---------------------------------------------------------------------------
# Run mypy with the CI-standard flags
# ---------------------------------------------------------------------------

_MYPY_FLAGS = [
    "--ignore-missing-imports",
    "--no-error-summary",
    "--no-pretty",
    "--follow-imports=silent",
]


def _run_mypy(src_dir: Path) -> str:
    """Run mypy and return raw stdout."""
    result = subprocess.run(
        [sys.executable, "-m", "mypy", str(src_dir)] + _MYPY_FLAGS,
        capture_output=True,
        text=True,
        cwd=_repo_root(),
    )
    return result.stdout


# ---------------------------------------------------------------------------
# Aggregate helpers
# ---------------------------------------------------------------------------


def _by_pattern(errors: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for e in errors:
        counts[e["pattern"]] += 1
    return dict(counts)


def _by_file(errors: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for e in errors:
        counts[e["file"]] += 1
    return dict(counts)


# ---------------------------------------------------------------------------
# Baseline helpers
# ---------------------------------------------------------------------------


def _read_baseline(baseline_path: Path) -> int:
    if baseline_path.exists():
        try:
            return int(baseline_path.read_text().strip())
        except ValueError:
            return 0
    return 0


def _write_baseline(baseline_path: Path, count: int) -> None:
    baseline_path.write_text(f"{count}\n")


# ---------------------------------------------------------------------------
# PDA Loop logging
# ---------------------------------------------------------------------------


def _pda_log(
    errors: list[dict[str, Any]],
    fixes: list[dict[str, Any]],
    session: str,
    pda_path: Path,
) -> None:
    """Append pattern and fix entries to pda_iterations.jsonl."""
    import datetime

    pda_path.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()

    by_pat = _by_pattern(errors)
    with pda_path.open("a", encoding="utf-8") as f:
        # Log each unique pattern as a failure entry
        for pattern, count in by_pat.items():
            rule = next((r for r in _RULES if r["pattern"] == pattern), None)
            entry: dict[str, Any] = {
                "type": "failure",
                "timestamp": ts,
                "session": session or "unknown",
                "pattern_id": f"RP-{pattern}",
                "workflow": "mypy Baseline (Type-Check Anti-Regression)",
                "error_text": f"{count} × [{pattern}]",
                "root_cause": rule["fix_description"] if rule else "See mypy output",
                "fix_template": (rule["fix_description"] if rule and rule["fix_available"] else ""),
                "verification_cmd": "python scripts/ci/mypy_baseline.py --require-baseline",
                "occurrences": count,
            }
            f.write(json.dumps(entry) + "\n")

        # Log applied fixes
        if fixes:
            fix_entry: dict[str, Any] = {
                "type": "fix",
                "timestamp": ts,
                "session": session or "unknown",
                "pattern_id": "RP-MYPY-MANAGER-FIX",
                "fix_applied": f"{len(fixes)} automated fixes applied",
                "fixes": fixes,
                "verification_cmd": "python scripts/ci/mypy_baseline.py --require-baseline",
                "verification_passed": None,  # filled after re-run
            }
            f.write(json.dumps(fix_entry) + "\n")


# ---------------------------------------------------------------------------
# Automated fix applicators
# ---------------------------------------------------------------------------


def _fix_redundant_cast(src: str, line_no: int) -> tuple[str, bool]:
    """Remove cast(T, expr) → expr on the given 1-indexed line."""
    lines = src.splitlines(keepends=True)
    if line_no < 1 or line_no > len(lines):
        return src, False
    original = lines[line_no - 1]
    # Pattern: cast(SomeType, expr)  →  expr
    new_line, n = re.subn(
        r"\bcast\(\s*[A-Za-z_][A-Za-z0-9_\[\], ]*,\s*(.*?)\)",
        r"\1",
        original,
    )
    if n == 0:
        return src, False
    lines[line_no - 1] = new_line
    return "".join(lines), True


def _fix_optional_import_fallback(src: str, line_no: int) -> tuple[str, bool]:
    """Append # type: ignore[assignment] to optional-import fallback = None line."""
    lines = src.splitlines(keepends=True)
    if line_no < 1 or line_no > len(lines):
        return src, False
    original = lines[line_no - 1]
    stripped = original.rstrip("\n\r")
    # Skip if already has a type: ignore comment
    if "type: ignore" in stripped:
        return src, False
    # Append at end of line, preserving original newline
    nl = original[len(stripped) :]
    lines[line_no - 1] = stripped + "  # type: ignore[assignment]" + nl
    return "".join(lines), True


def _fix_no_redef(src: str, line_no: int) -> tuple[str, bool]:
    """Append # type: ignore[no-redef] to re-definition line."""
    lines = src.splitlines(keepends=True)
    if line_no < 1 or line_no > len(lines):
        return src, False
    original = lines[line_no - 1]
    stripped = original.rstrip("\n\r")
    if "type: ignore" in stripped:
        return src, False
    nl = original[len(stripped) :]
    lines[line_no - 1] = stripped + "  # type: ignore[no-redef]" + nl
    return "".join(lines), True


def _fix_none_guard(src: str, line_no: int) -> tuple[str, bool]:
    """Append # type: ignore[union-attr] for now — proper fix is manual narrowing."""
    lines = src.splitlines(keepends=True)
    if line_no < 1 or line_no > len(lines):
        return src, False
    original = lines[line_no - 1]
    stripped = original.rstrip("\n\r")
    if "type: ignore" in stripped:
        return src, False
    nl = original[len(stripped) :]
    lines[line_no - 1] = stripped + "  # type: ignore[union-attr]" + nl
    return "".join(lines), True


def _fix_arg_none(src: str, line_no: int) -> tuple[str, bool]:
    """Append # type: ignore[arg-type] for str | None → str dict.get()."""
    lines = src.splitlines(keepends=True)
    if line_no < 1 or line_no > len(lines):
        return src, False
    original = lines[line_no - 1]
    stripped = original.rstrip("\n\r")
    if "type: ignore" in stripped:
        return src, False
    nl = original[len(stripped) :]
    lines[line_no - 1] = stripped + "  # type: ignore[arg-type]" + nl
    return "".join(lines), True


def _fix_typeddict(src: str, line_no: int) -> tuple[str, bool]:
    """Append # type: ignore[typeddict-item] for TypedDict(**dict) expansion."""
    lines = src.splitlines(keepends=True)
    if line_no < 1 or line_no > len(lines):
        return src, False
    original = lines[line_no - 1]
    stripped = original.rstrip("\n\r")
    if "type: ignore" in stripped:
        return src, False
    nl = original[len(stripped) :]
    lines[line_no - 1] = stripped + "  # type: ignore[typeddict-item]" + nl
    return "".join(lines), True


def _fix_arg_type(src: str, line_no: int) -> tuple[str, bool]:
    """Append # type: ignore[arg-type] for incompatible argument type."""
    lines = src.splitlines(keepends=True)
    if line_no < 1 or line_no > len(lines):
        return src, False
    original = lines[line_no - 1]
    stripped = original.rstrip("\n\r")
    if "type: ignore" in stripped:
        return src, False
    nl = original[len(stripped) :]
    lines[line_no - 1] = stripped + "  # type: ignore[arg-type]" + nl
    return "".join(lines), True


def _fix_call_arg(src: str, line_no: int) -> tuple[str, bool]:
    """Append # type: ignore[call-arg] for missing/extra constructor arguments."""
    lines = src.splitlines(keepends=True)
    if line_no < 1 or line_no > len(lines):
        return src, False
    original = lines[line_no - 1]
    stripped = original.rstrip("\n\r")
    if "type: ignore" in stripped:
        return src, False
    nl = original[len(stripped) :]
    lines[line_no - 1] = stripped + "  # type: ignore[call-arg]" + nl
    return "".join(lines), True


def _fix_union_narrow(src: str, line_no: int) -> tuple[str, bool]:
    """Append # type: ignore[union-attr,arg-type,call-arg] for union narrowing."""
    lines = src.splitlines(keepends=True)
    if line_no < 1 or line_no > len(lines):
        return src, False
    original = lines[line_no - 1]
    stripped = original.rstrip("\n\r")
    if "type: ignore" in stripped:
        return src, False
    nl = original[len(stripped) :]
    lines[line_no - 1] = stripped + "  # type: ignore[union-attr,arg-type,call-arg]" + nl
    return "".join(lines), True


def _fix_unused_ignore(src: str, line_no: int) -> tuple[str, bool]:
    """Remove # type: ignore[...] comment from the given line."""
    lines = src.splitlines(keepends=True)
    if line_no < 1 or line_no > len(lines):
        return src, False
    original = lines[line_no - 1]
    new_line, n = re.subn(r"\s*#\s*type:\s*ignore\[[^\]]*\]", "", original)
    if n == 0:
        return src, False
    lines[line_no - 1] = new_line
    return "".join(lines), True


# Map pattern → fix function
_FIX_FN: dict[str, Any] = {
    "MYPY-REDUNDANT-CAST": _fix_redundant_cast,
    "MYPY-OPT-IMPORT": _fix_optional_import_fallback,
    "MYPY-NO-REDEF": _fix_no_redef,
    "MYPY-NONE-GUARD": _fix_none_guard,
    "MYPY-ARG-NONE": _fix_arg_none,
    "MYPY-TYPEDDICT": _fix_typeddict,
    "MYPY-ARG-TYPE": _fix_arg_type,
    "MYPY-CALL-ARG": _fix_call_arg,
    "MYPY-UNION-NARROW": _fix_union_narrow,
    "MYPY-UNUSED-IGNORE": _fix_unused_ignore,
    # MYPY-CIPHER-UNION and MYPY-STRUCTURAL require manual review
}


def _apply_fixes(
    errors: list[dict[str, Any]],
    repo_root: Path,
    fix_patterns: list[str] | None,
    dry_run: bool,
) -> list[dict[str, Any]]:
    """Apply automated fixes to source files. Returns list of applied fixes."""
    # Group errors by file — process each file once
    by_file: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for e in errors:
        if not e["fix_available"]:
            continue
        if fix_patterns and e["pattern"] not in fix_patterns:
            continue
        if e["pattern"] not in _FIX_FN:
            continue
        by_file[e["file"]].append(e)

    applied: list[dict[str, Any]] = []
    for rel_path, file_errors in by_file.items():
        file_path = repo_root / rel_path
        if not file_path.exists():
            continue
        src = file_path.read_text(encoding="utf-8")
        modified = False

        # Sort by line number DESCENDING so line offsets don't shift
        for err in sorted(file_errors, key=lambda e: e["line"], reverse=True):
            fn = _FIX_FN.get(err["pattern"])
            if fn is None:
                continue
            new_src, changed = fn(src, err["line"])
            if changed:
                src = new_src
                modified = True
                applied.append(
                    {
                        "file": rel_path,
                        "line": err["line"],
                        "pattern": err["pattern"],
                        "description": err["fix_description"],
                    }
                )

        if modified and not dry_run:
            file_path.write_text(src, encoding="utf-8")

    return applied


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def run(inputs: dict[str, Any]) -> dict[str, Any]:
    """Execute the mypy.manager skill."""
    action = inputs.get("action", "check")
    src_dir_rel = inputs.get("src_dir", "src")
    baseline_rel = inputs.get("baseline_file", ".mypy_baseline")
    fix_patterns: list[str] | None = inputs.get("fix_patterns") or None
    dry_run: bool = bool(inputs.get("dry_run", False))
    pda_log_enabled: bool = bool(inputs.get("pda_log", True))
    session: str = inputs.get("session", "unknown")

    repo_root = _repo_root()
    src_dir = repo_root / src_dir_rel
    baseline_path = repo_root / baseline_rel
    pda_path = repo_root / ".codex" / "aftermath" / "pda_iterations.jsonl"

    # ── check / classify ─────────────────────────────────────────────────────
    if action in ("check", "classify", "report"):
        if action == "classify" and "mypy_output" in inputs:
            raw = inputs["mypy_output"]
        else:
            raw = _run_mypy(src_dir)

        errors = _parse_errors(raw)
        baseline = _read_baseline(baseline_path)
        error_count = len(errors)
        regression = error_count > baseline

        if pda_log_enabled and errors:
            _pda_log(errors, [], session, pda_path)

        status = "fail" if regression else "pass"
        msg = (
            f"{error_count} error(s) — "
            + ("REGRESSION vs baseline " if regression else "within baseline ")
            + f"({baseline})"
        )
        return {
            "status": status,
            "action": action,
            "error_count": error_count,
            "baseline": baseline,
            "regression": regression,
            "errors": errors,
            "by_pattern": _by_pattern(errors),
            "by_file": _by_file(errors),
            "pda_logged": pda_log_enabled and bool(errors),
            "message": msg,
        }

    # ── fix ──────────────────────────────────────────────────────────────────
    if action == "fix":
        raw = _run_mypy(src_dir)
        errors = _parse_errors(raw)
        fixes = _apply_fixes(errors, repo_root, fix_patterns, dry_run)

        if pda_log_enabled and (errors or fixes):
            _pda_log(errors, fixes, session, pda_path)

        return {
            "status": "dry-run" if dry_run else "fixed",
            "action": action,
            "error_count": len(errors),
            "errors": errors,
            "fixes_applied": fixes,
            "by_pattern": _by_pattern(errors),
            "by_file": _by_file(errors),
            "pda_logged": pda_log_enabled,
            "message": (
                f"{len(fixes)} fix(es) {'would be' if dry_run else ''} applied "
                f"across {len({f['file'] for f in fixes})} file(s)."
            ),
        }

    # ── baseline ─────────────────────────────────────────────────────────────
    if action == "baseline":
        raw = _run_mypy(src_dir)
        errors = _parse_errors(raw)
        count = len(errors)
        old = _read_baseline(baseline_path)
        if not dry_run:
            _write_baseline(baseline_path, count)
        return {
            "status": "pass",
            "action": action,
            "error_count": count,
            "baseline": count,
            "regression": False,
            "message": (
                f"Baseline updated: {old} → {count}"
                if not dry_run
                else f"Would update baseline: {old} → {count} (dry-run)"
            ),
            "pda_logged": False,
        }

    return {
        "status": "error",
        "action": action,
        "message": f"Unknown action: {action!r}",
    }
