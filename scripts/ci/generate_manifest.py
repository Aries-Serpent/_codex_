"""
scripts/ci/generate_manifest.py
The central manifest generator for Aries-Serpent/_codex_
Connects: Phase 0 audit → Phase 1 registry → Phase 3 corpus → Phase 5 auto-docs

Usage:
  python scripts/ci/generate_manifest.py
  python scripts/ci/generate_manifest.py --update-enforcement-doc
  python scripts/ci/generate_manifest.py --verify-integrity
  python scripts/ci/generate_manifest.py --dump-safe-injection
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
import sqlite3
import time
from typing import Any

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
REGISTRY = REPO_ROOT / ".github" / "agents" / "AGENT_REGISTRY.yaml"
MANIFEST = REPO_ROOT / "CODEX_MANIFEST.json"
GVS_DOC = REPO_ROOT / ".codex" / "docs" / "GROUNDED_VS_SOFT_ENFORCEMENT.md"
WF_DIR = REPO_ROOT / ".github" / "workflows"
AGENTS_DIR = REPO_ROOT / ".github" / "agents"
DB_PATH = REPO_ROOT / ".codex" / "codex_corpus.db"
EMBED_META = REPO_ROOT / ".codex" / "embeddings" / "codex_index_meta.json"

# ── Security: fields safe for agent_context.json injection ──────────────────
SAFE_INJECTION_FIELDS = {
    "agents",
    "workflows",
    "policies",
    "enforcement_kpis",
    "operating_model",
    "generated_at",
    "schema_version",
}

INJECTION_BLOCKLIST = [
    r"<script",
    r"eval\(",
    r"exec\(",
    r"__import__",
    r"os\.system",
    r"\$\{.*?\}",
    r"<!--",
]

# R-12: Maximum serialised context size allowed for injection into agent_context.json.
# Prevents prompt-injection surface expansion via manifest inflation.
# Current safe payload is ~30 KB; 32 KB provides headroom while blocking malicious growth.
# Wired to COGNITIVE_BRAIN_MAX_CONTEXT_TOKENS repo variable (P2.1) so CI can override
# without a code change.  Defaults to 32 000 if the variable is absent.
CONTEXT_WINDOW_BUDGET: int = int(os.environ.get("COGNITIVE_BRAIN_MAX_CONTEXT_TOKENS", 32_000))


# ── KPI extraction from GROUNDED_VS_SOFT_ENFORCEMENT.md ─────────────────────
def extract_enforcement_kpis() -> dict[str, int]:
    if not GVS_DOC.exists():
        return {}
    text = GVS_DOC.read_text(encoding="utf-8")
    return {
        "tier1_count": len(re.findall(r"✅ \*\*GROUNDED\*\*", text)),
        "tier2_count": len(re.findall(r"🟡 \*\*(PARTIAL|TIER-2)\*\*", text)),
        "tier3_count": len(re.findall(r"❌ \*\*SOFT\*\*", text)),
        "ungatable": 2,  # confirmed permanent
    }


# ── Violation rate from SQLite ───────────────────────────────────────────────
def get_violation_rate_30d() -> float:
    if not DB_PATH.exists():
        return 0.0
    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute(
            "SELECT COUNT(*), SUM(violation_count) FROM agent_sessions "
            "WHERE start_time > datetime('now', '-30 days')"
        ).fetchone()
        conn.close()
        sessions = rows[0] or 0
        violations = rows[1] or 0
        return round(violations / sessions, 2) if sessions else 0.0
    except Exception:
        return 0.0


# ── Workflow index ────────────────────────────────────────────────────────────
def index_workflows() -> list[dict]:
    workflows = []
    for wf_path in sorted(WF_DIR.glob("*.yml")):
        text = wf_path.read_text(encoding="utf-8", errors="ignore")
        tier = (
            "GROUNDED"
            if ("exit 1" in text or "cognitive-preflight" in text)
            else "PARTIAL" if ("::warning::" in text or "createComment" in text) else "SOFT"
        )
        workflows.append(
            {
                "name": wf_path.stem,
                "path": str(wf_path.relative_to(REPO_ROOT)),
                "enforcement_tier": tier,
                "has_concurrency": "concurrency:" in text,
                "has_timeout": "timeout-minutes:" in text,
            }
        )
    return workflows


# ── Agent registry loader ────────────────────────────────────────────────────
def load_registry() -> list[dict]:
    if not REGISTRY.exists():
        return []
    data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    return data.get("agents", [])


# ── E→D operating model status ──────────────────────────────────────────────
def get_operating_model_status() -> dict[str, Any]:
    agents = load_registry()
    d_capable = sum(1 for a in agents if a.get("autonomy_model") == "D_CAPABLE")
    return {
        "current": "E",
        "target": "D",
        "d_capable_agents": d_capable,
        "transition_active": d_capable > 0,
    }


# ── Security: sanitize manifest before injection ─────────────────────────────
def sanitize_for_injection(
    manifest: dict[str, Any],
    context_window_budget: int = CONTEXT_WINDOW_BUDGET,
) -> dict[str, Any]:
    """Return only safe injection fields, enforcing blocklist and budget (R-12).

    Args:
        manifest: Raw manifest dict (as loaded from CODEX_MANIFEST.json).
        context_window_budget: Maximum allowed size (chars) for the serialised
            safe payload.  Defaults to ``CONTEXT_WINDOW_BUDGET`` (32 000).
            Raise ``ValueError`` when the payload exceeds this limit to prevent
            prompt-injection surface expansion via manifest inflation (R-12).

    Returns:
        Dict containing only the fields in ``SAFE_INJECTION_FIELDS``.

    Raises:
        ValueError: If any ``INJECTION_BLOCKLIST`` pattern is found, or if the
            serialised payload exceeds ``context_window_budget``.
    """
    safe = {k: v for k, v in manifest.items() if k in SAFE_INJECTION_FIELDS}
    safe_str = json.dumps(safe)
    for pattern in INJECTION_BLOCKLIST:
        if re.search(pattern, safe_str, re.IGNORECASE):
            raise ValueError(f"Injection pattern blocked: {pattern}")
    if len(safe_str) > context_window_budget:
        raise ValueError(
            f"Context window budget exceeded: {len(safe_str)} chars"
            f" > {context_window_budget} limit (R-12)"
        )
    return safe


def add_integrity_hash(manifest: dict[str, Any]) -> dict[str, Any]:
    m = {k: v for k, v in manifest.items() if k != "integrity_sha256"}
    content = json.dumps(m, sort_keys=True, separators=(",", ":"))
    result = dict(manifest)
    result["integrity_sha256"] = hashlib.sha256(content.encode()).hexdigest()
    return result


def verify_integrity(path: pathlib.Path) -> bool:
    data = json.loads(path.read_text(encoding="utf-8"))
    stored = data.pop("integrity_sha256", None)
    if not stored:
        return False
    content = json.dumps(data, sort_keys=True, separators=(",", ":"))
    computed = hashlib.sha256(content.encode()).hexdigest()
    return computed == stored


# ── Enforcement doc auto-update ──────────────────────────────────────────────
def update_enforcement_doc(kpis: dict[str, int]) -> None:
    if not GVS_DOC.exists():
        return
    text = GVS_DOC.read_text(encoding="utf-8")
    new_bar = (
        f"    bar [{min(9 + kpis.get('tier1_count', 0) // 2, 10)}, "
        f"{kpis.get('tier1_count', 9)}, "
        f"7, 8, 5, 5, "
        f"{min(9 + kpis.get('tier1_count', 0) // 3, 10)}, "
        f"1, 5, "
        f"{min(9 + kpis.get('tier1_count', 0) // 2, 10)}, 6]"
    )
    updated = re.sub(r"    bar \[[\d, ]+\]", new_bar, text, count=1)
    GVS_DOC.write_text(updated, encoding="utf-8")
    print("Updated enforcement doc reliability chart")


# ── Main manifest generation ─────────────────────────────────────────────────
def generate() -> dict[str, Any]:
    kpis = extract_enforcement_kpis()
    workflows = index_workflows()
    agents = load_registry()

    manifest: dict[str, Any] = {
        "schema_version": "1.0",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "agents": [
            {
                "name": a.get("id", a.get("name", "")),
                "role": a.get("role", "specialist"),
                "enforcement_tier": a.get("enforcement_tier", "SOFT"),
                "autonomy_model": a.get("autonomy_model", "E"),
            }
            for a in agents
        ],
        "workflows": [
            {
                "name": w["name"],
                "enforcement_tier": w["enforcement_tier"],
                "has_concurrency": w["has_concurrency"],
            }
            for w in workflows
        ],
        "policies": [
            {"path": str(p.relative_to(REPO_ROOT)), "type": "enforcement"}
            for p in sorted(REPO_ROOT.glob(".codex/docs/*.md"))
        ],
        "datasets": {
            "session_db": str(DB_PATH.relative_to(REPO_ROOT)),
            "embedding_meta": (
                str(EMBED_META.relative_to(REPO_ROOT)) if EMBED_META.exists() else None
            ),
        },
        "enforcement_kpis": kpis,
        "operating_model": get_operating_model_status(),
        "violation_rate_30d": get_violation_rate_30d(),
    }

    manifest = add_integrity_hash(manifest)
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Manifest written: {MANIFEST} ({len(agents)} agents, {len(workflows)} workflows)")
    return manifest


# ── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="Generate CODEX_MANIFEST.json from AGENT_REGISTRY.yaml"
    )
    ap.add_argument(
        "--update-enforcement-doc",
        action="store_true",
        help="Auto-update GROUNDED_VS_SOFT_ENFORCEMENT.md reliability chart",
    )
    ap.add_argument(
        "--verify-integrity",
        action="store_true",
        help="Verify integrity_sha256 of existing CODEX_MANIFEST.json",
    )
    ap.add_argument(
        "--dump-safe-injection",
        action="store_true",
        help="Print sanitized manifest safe for agent_context.json injection",
    )
    args = ap.parse_args()

    if args.verify_integrity:
        if not MANIFEST.exists():
            print(f"ERROR: {MANIFEST} not found — run generate_manifest.py first")
            raise SystemExit(1)
        ok = verify_integrity(MANIFEST)
        if ok:
            print(f"✅ Integrity valid: {MANIFEST}")
        else:
            print(f"❌ Integrity INVALID: {MANIFEST}")
            raise SystemExit(1)
    elif args.dump_safe_injection:
        manifest = (
            json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else generate()
        )
        safe = sanitize_for_injection(manifest)
        print(json.dumps(safe, indent=2))
    else:
        manifest = generate()
        if args.update_enforcement_doc:
            update_enforcement_doc(manifest.get("enforcement_kpis", {}))
