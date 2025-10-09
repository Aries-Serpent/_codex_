from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any, Optional


OWNER_RX = re.compile(r"^@([A-Za-z0-9_.-]+)(/[A-Za-z0-9_.-]+)?$")


@dataclass
class CodeownersRule:
    pattern: str
    owners: List[str]
    line_no: int


@dataclass
class CodeownersReport:
    exists: bool
    default_rule: bool
    owners_ok: bool
    coverage: Dict[str, bool]
    errors: List[str]
    warnings: List[str]
    rules: List[Dict[str, Any]]


def parse_codeowners(text: str) -> List[CodeownersRule]:
    rules: List[CodeownersRule] = []
    for i, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            # pattern without owners: skip but record warning upstream
            rules.append(CodeownersRule(pattern=parts[0], owners=[], line_no=i))
            continue
        pat, owners = parts[0], parts[1:]
        rules.append(CodeownersRule(pattern=pat, owners=owners, line_no=i))
    return rules


def validate_owners(rules: List[CodeownersRule]) -> bool:
    ok = True
    for r in rules:
        for o in r.owners:
            if not OWNER_RX.match(o):
                ok = False
    return ok


def has_default_rule(rules: List[CodeownersRule]) -> bool:
    for r in rules:
        if r.pattern == "*":
            return True
    return False


def heuristic_coverage(rules: List[CodeownersRule]) -> Dict[str, bool]:
    pats = {r.pattern for r in rules}
    return {
        "src": any(p.startswith("src") or p.startswith("/src") for p in pats),
        "tests": any(p.startswith("tests") or p.startswith("/tests") for p in pats),
        "docs": any(p.startswith("docs") or p.startswith("/docs") or p.startswith(".github") for p in pats),
    }


def validate_codeowners_text(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: List[str] = []
    warns: List[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})")
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[{"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules],
    )


def validate_repo_codeowners(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )