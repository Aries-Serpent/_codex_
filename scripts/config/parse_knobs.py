"""
Knob Normalization Utilities (P2)

Additions in P2:
- Batch normalization from os.environ with schema (type, default, bounds)
- Joined warnings list for manifest aggregation
- Helper to coerce tri-state pointer style and filter modes with safe fallbacks

Note:
- Functions are side-effect free (no logging). Callers collect warnings and decide where to persist them.

Schemas:
- See DEFAULT_SCHEMA below for supported keys and semantics.
"""
from __future__ import annotations
from typing import Iterable, Tuple, Optional, Dict, Any

_TRUTHY = {"1","true","TRUE","True","yes","YES","on","ON"}
_FALSY  = {"0","false","FALSE","False","no","NO","off","OFF",""}


def normalize_truthy(raw: Optional[str], default: bool=False) -> Tuple[bool, Optional[str]]:
    if raw is None:
        return default, None
    if raw in _TRUTHY:
        return True, None
    if raw in _FALSY:
        return False, None
    return default, f"ambiguous_boolean:{raw}"


def normalize_enum(raw: Optional[str], allowed: Iterable[str], default: str) -> Tuple[str, Optional[str]]:
    allowed_set = set(allowed)
    if raw is None:
        return default, None
    if raw in allowed_set:
        return raw, None
    return default, f"invalid_enum:{raw}"


def normalize_int(raw: Optional[str], default: int, min_val: Optional[int]=None, max_val: Optional[int]=None) -> Tuple[int, Optional[str]]:
    if raw is None:
        return default, None
    try:
        val = int(raw)
    except ValueError:
        return default, f"invalid_int:{raw}"
    if min_val is not None and val < min_val:
        return default, f"int_below_min:{raw}"
    if max_val is not None and val > max_val:
        return default, f"int_above_max:{raw}"
    return val, None


def normalize_float(raw: Optional[str], default: float, min_val: Optional[float]=None, max_val: Optional[float]=None) -> Tuple[float, Optional[str]]:
    if raw is None:
        return default, None
    try:
        val = float(raw)
    except ValueError:
        return default, f"invalid_float:{raw}"
    if min_val is not None and val < min_val:
        return default, f"float_below_min:{raw}"
    if max_val is not None and val > max_val:
        return default, f"float_above_max:{raw}"
    return val, None


def normalize_csv_list(raw: Optional[str]) -> Tuple[list[str], Optional[str]]:
    if not raw:
        return [], None
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    long_items = [p for p in parts if len(p) > 256]
    if long_items:
        return parts, "suspicious_long_entries"
    return parts, None


# --- Batch normalization ---

DEFAULT_SCHEMA: Dict[str, Dict[str, Any]] = {
    # Content filtering
    "CONTENT_FILTER_MODE": {"type": "enum", "allowed": ["allowlist","pii","combined"], "default": "allowlist"},
    "ALLOWLIST_PROFILE":   {"type": "enum", "allowed": ["A","B","C","A+B","A+C","B+C","A+B+C"], "default": "A"},
    "ALLOWLIST_EXT":       {"type": "csv",  "default": ""},
    "PII_PATTERN_SET":     {"type": "enum", "allowed": ["minimal","extended","custom"], "default": "minimal"},
    "PII_CUSTOM_LIST":     {"type": "csv",  "default": ""},
    "PII_MODE":            {"type": "enum", "allowed": ["replace","union-minimal","union-extended"], "default": "union-minimal"},
    "PII_REGEX_STRATEGY":  {"type": "enum", "allowed": ["abort","skip-warn","skip-manifest"], "default": "skip-manifest"},
    # Depth
    "AUDIT_DEPTH_DEFAULT": {"type": "int",  "min": 1, "max": 4, "default": 3},
    "AUDIT_DEPTH":         {"type": "int",  "min": 1, "max": 4, "default": None},  # None means: use default
    # Archival
    "MAX_BUNDLE_MB":       {"type": "float","min": 0.1, "max": 4096.0, "default": 25.0},
    "ARCHIVE_FORMAT":      {"type": "enum", "allowed": ["tar.gz","zip"], "default": "tar.gz"},
    "AUTO_ARCHIVE_DISABLE":{"type": "bool", "default": False},
    "ARCHIVE_POINTER_STYLE":{"type":"enum","allowed": ["embedded","sidecar","both"], "default":"both"},
    # Optional future naming policy
    "BUNDLE_PREFIX_MODE":  {"type": "bool", "default": False},
}


def _get_env_map() -> Dict[str, str]:
    import os
    return dict(os.environ)  # shallow copy


def normalize_from_env(schema: Dict[str, Dict[str, Any]] = DEFAULT_SCHEMA) -> Tuple[Dict[str, Any], list[str]]:
    env = _get_env_map()
    normalized: Dict[str, Any] = {}
    warnings: list[str] = []
    
    for key, spec in schema.items():
        typ = spec["type"]
        default = spec.get("default")
        raw = env.get(key)
        
        if typ == "enum":
            val, w = normalize_enum(raw, spec["allowed"], default)
        elif typ == "bool":
            val, w = normalize_truthy(raw, bool(default))
        elif typ == "int":
            val, w = normalize_int(raw, int(default) if default is not None else 0, spec.get("min"), spec.get("max"))
            if raw is None and default is None:
                # propagate sentinel to indicate "use depth default"
                val, w = None, None
        elif typ == "float":
            val, w = normalize_float(raw, float(default), spec.get("min"), spec.get("max"))
        elif typ == "csv":
            lst, w = normalize_csv_list(raw)
            val = lst if lst else (default if default != "" else [])
        else:
            val, w = raw if raw is not None else default, None
        
        normalized[key] = val
        if w:
            warnings.append(w)
    
    return normalized, warnings


def summarize_effective(knobs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Produce a compact summary for manifest or reproducibility sidecar.
    - Flattens lists by length; hides empty values.
    """
    out: Dict[str, Any] = {}
    for k, v in knobs.items():
        if v in (None, "", [], {}):
            continue
        out[k] = v
    return out


if __name__ == "__main__":
    knobs, warns = normalize_from_env()
    print("KNOBS:", knobs)
    print("WARNINGS:", warns)
