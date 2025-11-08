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
import os
from typing import Iterable, Tuple, Optional, Dict, Any, List

_TRUTHY = {"1","true","TRUE","True","yes","YES","on","ON","y","Y"}
_FALSY  = {"0","false","FALSE","False","no","NO","off","OFF","","n","N"}

_WARNINGS: List[str] = []


def _warn(msg: str) -> None:
    _WARNINGS.append(msg)


def normalize_truthy(raw: Optional[str], default: bool=False) -> Tuple[bool, Optional[str]]:
    if raw is None:
        return default, None
    if raw in _TRUTHY:
        return True, None
    if raw in _FALSY:
        return False, None
    return default, f"ambiguous_boolean:{raw}"


def parse_truthy(raw: Optional[str], default: bool=False) -> bool:
    if raw is None:
        return default
    if raw in _TRUTHY:
        return True
    if raw in _FALSY:
        return False
    return default


def normalize_enum(raw: Optional[str], allowed: Iterable[str], default: str) -> Tuple[str, Optional[str]]:
    allowed_set = set(allowed)
    if raw is None:
        return default, None
    if raw in allowed_set:
        return raw, None
    return default, f"invalid_enum:{raw}"


def parse_enum(raw: Optional[str], allowed: Iterable[str], default: str, var_name: str) -> str:
    if raw is None or raw == "":
        _warn(f"required_selection_missing:{var_name}")
        return default
    if raw in allowed:
        return raw
    _warn(f"invalid_value:{var_name}")
    return default


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


def parse_int(raw: Optional[str], default: int, min_val: Optional[int]=None, max_val: Optional[int]=None) -> int:
    if raw is None or raw == "":
        return default
    try:
        val = int(raw)
    except (TypeError, ValueError):
        return default
    if min_val is not None and val < min_val:
        return default
    if max_val is not None and val > max_val:
        return default
    return val


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


def parse_csv_list(raw: Optional[str]) -> list[str]:
    if not raw:
        return []
    return [part.strip() for part in raw.split(",") if part.strip()]


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
    # Prefix naming policy
    "BUNDLE_PREFIX_MODE":  {"type": "bool", "default": False},
    # P6 Advanced Features
    "AST_SIMILARITY_ENABLE": {"type": "bool", "default": False},
    "AST_SIMILARITY_MAX_FILES": {"type": "int", "min": 1, "max": 100, "default": 30},
    "AST_SIMILARITY_MIN_NODES": {"type": "int", "min": 1, "max": 1000, "default": 10},
    "AST_CONSISTENCY_BLEND_MODE": {"type": "enum", "allowed": ["multiply","average","max"], "default": "multiply"},
    "SYNONYM_MAP_PATH": {"type": "str", "default": "configs/synonyms/synonyms.json"},
    "SECRET_CONTEXT_ENABLE": {"type": "bool", "default": False},
    "SECRET_CONTEXT_WINDOW": {"type": "int", "min": 1, "max": 100, "default": 10},
    "SECRET_CONTEXT_KEYWORDS": {"type": "csv", "default": ""},
    "FEDERATION_ENABLE": {"type": "bool", "default": False},
    "FEDERATION_REPO_PATHS": {"type": "csv", "default": ""},
    "MANIFEST_EXTENDED_ENABLE": {"type": "bool", "default": True},
}


def _get_env_map() -> Dict[str, str]:
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
        elif typ == "str":
            val, w = raw if raw is not None else default, None
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


def get_warnings() -> List[str]:
    return list(_WARNINGS)


def clear_warnings() -> None:
    _WARNINGS.clear()


def _get_env(name: str) -> Optional[str]:
    return os.environ.get(name)


def get_depth() -> Tuple[int, bool]:
    raw_depth = _get_env("AUDIT_DEPTH")
    raw_default = _get_env("AUDIT_DEPTH_DEFAULT")

    default_depth = parse_int(raw_default, 3, min_val=1, max_val=4)
    default_source = "env" if raw_default not in (None, "") else "hardcoded"

    depth_warning = False

    if raw_depth not in (None, ""):
        depth = parse_int(raw_depth, default_depth, min_val=1, max_val=4)
        if depth < 4:
            depth_warning = True
            _warn("depth_restriction_active")
        return depth, depth_warning

    # Only warn if the default source is env (overridden), or if the default is restrictive
    # Warn when using env-based default or hardcoded default
    if default_source in ("env", "hardcoded"):
        _warn(f"depth_default_used:{default_source}")
    if default_depth < 4:
        depth_warning = True
        _warn("depth_restriction_active")
    return default_depth, depth_warning


def get_pii_mode() -> str:
    raw = _get_env("PII_MODE")
    return parse_enum(raw, ["replace", "union-minimal", "union-extended"], "union-minimal", "PII_MODE")


def get_pii_pattern_set() -> str:
    raw = _get_env("PII_PATTERN_SET")
    return parse_enum(raw, ["minimal", "extended", "custom"], "minimal", "PII_PATTERN_SET")


def get_pii_custom_list() -> list[str]:
    raw = _get_env("PII_CUSTOM_LIST")
    return parse_csv_list(raw)


def get_pii_regex_strategy() -> str:
    raw = _get_env("PII_REGEX_STRATEGY")
    return parse_enum(raw, ["abort", "skip-warn", "skip-manifest"], "skip-manifest", "PII_REGEX_STRATEGY")


def get_content_filter_mode() -> str:
    raw = _get_env("CONTENT_FILTER_MODE")
    return parse_enum(raw, ["allowlist", "pii", "combined"], "allowlist", "CONTENT_FILTER_MODE")


def get_allowlist_profile() -> str:
    raw = _get_env("ALLOWLIST_PROFILE")
    value = parse_enum(raw, ["A", "B", "C", "A+B", "A+C", "B+C", "A+B+C"], "A", "ALLOWLIST_PROFILE")
    if raw in (None, ""):
        _warn("allowlist_default_used")
    return value


def get_allowlist_extensions() -> list[str]:
    raw = _get_env("ALLOWLIST_EXT")
    return parse_csv_list(raw)


def get_max_bundle_mb() -> int:
    raw = _get_env("MAX_BUNDLE_MB")
    return parse_int(raw, 25, min_val=1)


def get_auto_archive_enabled() -> bool:
    raw = _get_env("AUTO_ARCHIVE_DISABLE")
    disabled = parse_truthy(raw, default=False)
    if disabled:
        _warn("auto_archive_disabled")
    return not disabled


def get_archive_format() -> str:
    raw = _get_env("ARCHIVE_FORMAT")
    return parse_enum(raw, ["tar.gz", "zip"], "tar.gz", "ARCHIVE_FORMAT")


def get_archive_pointer_style() -> str:
    raw = _get_env("ARCHIVE_POINTER_STYLE")
    return parse_enum(raw, ["embedded", "sidecar", "both"], "both", "ARCHIVE_POINTER_STYLE")


def get_bundle_prefix_mode() -> bool:
    raw = _get_env("BUNDLE_PREFIX_MODE")
    return parse_truthy(raw, default=False)


if __name__ == "__main__":
    knobs, warns = normalize_from_env()
    print("KNOBS:", knobs)
    print("WARNINGS:", warns)
