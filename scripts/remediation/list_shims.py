#!/usr/bin/env python3
"""
List shims & canonical module inventory.

Scans specified roots (e.g., training/, src/training/) and emits a merged inventory YAML
with module ownership, canonical path, and status. Designed to be deterministic.

Usage:
  python scripts/remediation/list_shims.py --roots training src/training tokenization src/tokenization --output .github/SHIM_INVENTORY.yaml
"""
from __future__ import annotations
import argparse
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]

def scan_modules(root: Path) -> dict[str, Path]:
    """Scan a directory for Python modules, returning module name -> path mapping."""
    modules = {}
    if not root.exists():
        return modules
    for p in sorted(root.glob("*.py")):
        if p.name == "__init__.py":
            continue
        mod_name = f"{root.name}.{p.stem}"
        modules[mod_name] = p.relative_to(ROOT)
    return modules

def merge_inventory(legacy: dict[str, Path], canonical: dict[str, Path]) -> list[dict]:
    """Merge legacy and canonical module inventories into structured records."""
    items = []
    all_mods = sorted(set(legacy) | set(canonical))
    for mod in all_mods:
        items.append({
            "module": mod,
            "legacy_path": str(legacy.get(mod) or ""),
            "canonical_path": str(canonical.get(mod) or ""),
            "owner": "unknown",
            "status": "shim" if (mod in legacy and mod in canonical) else ("migrated" if mod in canonical else "active"),
            "rationale": "",
            "deprecation_date": None,
            "whitelist_duplicates": [],
            "notes": "",
        })
    return items

def main():
    ap = argparse.ArgumentParser(description="Generate shim inventory YAML")
    ap.add_argument("--roots", nargs="+", required=True, help="Root directories to scan (e.g., training src/training)")
    ap.add_argument("--output", required=True, help="Output YAML file path")
    args = ap.parse_args()

    roots = [ROOT / r for r in args.roots]
    legacy = {}
    canonical = {}
    
    for r in roots:
        # Classify as canonical (src/*) or legacy (root)
        if "src" in r.parts:
            canonical.update(scan_modules(r))
        else:
            legacy.update(scan_modules(r))

    inventory = merge_inventory(legacy, canonical)
    doc = {
        "inventory": inventory, 
        "policy": {
            "strict_conflicts": {
                "enabled": True, 
                "whitelist_source": ".github/SHIM_INVENTORY.yaml"
            },
            "decision_gates": {
                "min_equivalence_overlap": 3,
                "usage_trend_threshold_pct": 10,
                "usage_trend_window_days": 90,
                "low_risk_tests_threshold": 10
            }
        }
    }
    
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
    print(f"[OK] Inventory written to {out}")
    print(f"[INFO] Found {len(inventory)} modules ({len(legacy)} legacy, {len(canonical)} canonical)")

if __name__ == "__main__":
    main()
