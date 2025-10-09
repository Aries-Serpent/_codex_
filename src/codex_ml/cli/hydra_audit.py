"""Hydra defaults audit CLI.

Scans a config root for YAML configs, inspects ``defaults`` lists and reports:

* presence and placement of ``_self_``
* missing groups/options that do not resolve to YAML files under the config root
* unresolved interpolations (``${...}``)

The audit outputs a JSON payload to stdout and can optionally persist JSON and
Markdown reports to disk. The command avoids executing Hydra applications and
only operates on static files.

Exit codes
==========

``0``
    Success with no issues found.
``2``
    Config root path not found.
``3``
    Audit completed but issues were detected (non-fatal).
``4``
    Required dependency (``PyYAML``) missing.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

try:  # pragma: no cover - handled in tests via importorskip
    import yaml  # type: ignore
except Exception:  # pragma: no cover - reported via exit code
    yaml = None


UNRESOLVED_RE = re.compile(r"\$\{[^}]+}")


@dataclass
class DefaultsIssue:
    """Description of an issue discovered in a defaults list."""

    file: str
    kind: str
    message: str
    entry: Optional[str] = None


@dataclass
class DefaultRef:
    """Structured representation of a defaults list reference."""

    raw: str
    group: Optional[str]
    name: Optional[str]
    package: Optional[str]
    optional: bool


@dataclass
class FileAudit:
    file: str
    has_defaults: bool
    has_self: bool
    self_position: Optional[str]  # "first"|"last"|"middle"|None
    unresolved_keys: List[str]
    missing_required: List[str]
    missing_optional: List[str]
    issues: List[DefaultsIssue]


def _scan_yaml_files(root: Path) -> List[Path]:
    yaml_files = list(root.rglob("*.yaml"))
    yaml_files.extend(root.rglob("*.yml"))
    return sorted(set(yaml_files))


def _self_position(defaults: Sequence[Any]) -> Optional[str]:
    if "_self_" not in defaults:
        return None
    idx = defaults.index("_self_")
    if idx == 0:
        return "first"
    if idx == len(defaults) - 1:
        return "last"
    return "middle"


def _load_yaml(path: Path) -> Dict[str, Any]:
    if yaml is None:
        return {}
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    try:
        data = yaml.safe_load(text)
    except Exception:
        return {}
    return data or {}


def _find_unresolved(node: Any, prefix: str = "") -> List[str]:
    hits: List[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            key_path = f"{prefix}.{key}" if prefix else str(key)
            hits.extend(_find_unresolved(value, key_path))
    elif isinstance(node, list):
        for idx, value in enumerate(node):
            key_path = f"{prefix}[{idx}]" if prefix else f"[{idx}]"
            hits.extend(_find_unresolved(value, key_path))
    elif isinstance(node, str):
        if UNRESOLVED_RE.search(node):
            hits.append(prefix or "<root>")
    return hits


def _normalize_path(base: Path, parts: Iterable[str]) -> Path:
    path = base
    for part in parts:
        part = part.strip()
        if not part:
            continue
        path = path / part
    return path


def _candidate_files(root: Path, ref: DefaultRef) -> List[Path]:
    if not ref.group or not ref.name:
        return []

    group = ref.group.replace(".", "/")
    name = ref.name

    extra_packages: List[str] = []
    package = ref.package

    if "@" in name:
        maybe_name, pkg = name.split("@", 1)
        maybe_name = maybe_name.strip()
        pkg = pkg.strip()
        if maybe_name:
            name = maybe_name
        if pkg:
            extra_packages.append(pkg)

    bases: List[Path] = []
    if package:
        bases.append(_normalize_path(root, package.split("/")))
    for pkg in extra_packages:
        bases.append(_normalize_path(root, pkg.split("/")))
    bases.append(root)

    group_parts = group.split("/")
    name_path = Path(name.replace(".", "/"))

    candidates: List[Path] = []
    for base in bases:
        group_path = _normalize_path(base, group_parts)
        target = group_path / name_path
        if target.suffix:
            candidates.append(target)
        else:
            candidates.append(target.with_suffix(".yaml"))
            candidates.append(target.with_suffix(".yml"))
    # Deduplicate while preserving order
    seen: set[Path] = set()
    unique: List[Path] = []
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        unique.append(candidate)
    return unique


def _parse_default_entry(entry: Any) -> Optional[DefaultRef]:
    if isinstance(entry, str):
        raw = entry.strip()
        if not raw or raw in {"_self_", "..."}:
            return None
        optional = raw.startswith("?")
        normalized = raw.lstrip("?").strip()
        if normalized.startswith("+"):
            normalized = normalized[1:].strip()
        if normalized in {"_self_", ""}:
            return None
        if normalized.startswith("/"):
            # Relative/absolute includes are tricky to resolve statically
            return None
        if ":" not in normalized:
            return None
        group, name = normalized.split(":", 1)
        group = group.strip()
        name = name.strip()
        if not group or not name or name in {"???", "_self_"}:
            return None
        if "${" in name:
            return None
        package = None
        if "@" in group:
            group_part, pkg = group.split("@", 1)
            group_part = group_part.strip()
            pkg = pkg.strip()
            group = group_part or group
            package = pkg or None
        return DefaultRef(raw=raw, group=group, name=name, package=package, optional=optional)

    if isinstance(entry, dict):
        if {"group", "name"}.issubset(entry.keys()):
            group = str(entry.get("group", "")).strip()
            name = str(entry.get("name", "")).strip()
            package = str(entry.get("package", "")).strip() or None
            optional = bool(entry.get("optional", False))
            if not group or not name or name in {"???", "_self_"}:
                return None
            if "${" in name:
                return None
            return DefaultRef(
                raw=f"{group}:{name}",
                group=group,
                name=name,
                package=package,
                optional=optional,
            )
        if len(entry) == 1:
            ((group, name),) = entry.items()
            group_str = str(group).strip()
            if not group_str:
                return None
            if isinstance(name, str):
                name_str = name.strip()
                if not name_str or name_str in {"???", "_self_"}:
                    return None
                if "${" in name_str:
                    return None
                return DefaultRef(
                    raw=f"{group_str}:{name_str}",
                    group=group_str,
                    name=name_str,
                    package=None,
                    optional=False,
                )
    return None


def _audit_file(path: Path, root: Path) -> FileAudit:
    data = _load_yaml(path)
    defaults = data.get("defaults")
    has_defaults = isinstance(defaults, list)
    has_self = False
    self_pos: Optional[str] = None
    issues: List[DefaultsIssue] = []
    missing_required: List[str] = []
    missing_optional: List[str] = []

    if has_defaults:
        has_self = "_self_" in defaults
        self_pos = _self_position(defaults)
        if not has_self:
            issues.append(
                DefaultsIssue(
                    file=str(path),
                    kind="missing_self",
                    message="defaults missing _self_ entry",
                )
            )
        elif self_pos == "middle":
            issues.append(
                DefaultsIssue(
                    file=str(path),
                    kind="self_middle",
                    message="_self_ appears in the middle of defaults list",
                    entry="_self_",
                )
            )

        for entry in defaults:
            ref = _parse_default_entry(entry)
            if not ref:
                continue
            for candidate in _candidate_files(root, ref):
                if candidate.exists():
                    break
            else:
                text = ref.raw
                if ref.optional:
                    missing_optional.append(text)
                    issues.append(
                        DefaultsIssue(
                            file=str(path),
                            kind="missing_optional",
                            message=f"optional defaults entry not found: {text}",
                            entry=text,
                        )
                    )
                else:
                    missing_required.append(text)
                    issues.append(
                        DefaultsIssue(
                            file=str(path),
                            kind="missing_target",
                            message=f"defaults entry target not found: {text}",
                            entry=text,
                        )
                    )

    unresolved = _find_unresolved(data)

    try:
        rel_file = str(path.relative_to(root))
    except ValueError:
        rel_file = str(path)

    return FileAudit(
        file=rel_file,
        has_defaults=bool(has_defaults),
        has_self=has_self,
        self_position=self_pos,
        unresolved_keys=unresolved,
        missing_required=missing_required,
        missing_optional=missing_optional,
        issues=issues,
    )


def _write_markdown(out_path: Path, audits: Sequence[FileAudit]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines: List[str] = []
    lines.append("# Hydra Defaults Audit")
    lines.append("")
    header = (
        "| file | has_defaults | _self_ | _self_ position | unresolved | "
        "missing required | missing optional | issues |"
    )
    lines.append(header)
    lines.append("|---|---:|:---:|:---:|---|---|---|---|")
    for audit in audits:
        issue_summary = "; ".join(f"{iss.kind}: {iss.entry or iss.message}" for iss in audit.issues)
        lines.append(
            "| {file} | {has_defaults} | {has_self} | {pos} | {unresolved} | {missing_req} | {missing_opt} | {issues} |".format(
                file=audit.file,
                has_defaults=str(audit.has_defaults),
                has_self=str(audit.has_self),
                pos=audit.self_position or "",
                unresolved=len(audit.unresolved_keys),
                missing_req=len(audit.missing_required),
                missing_opt=len(audit.missing_optional),
                issues=issue_summary,
            )
        )
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def cmd_defaults_audit(args: argparse.Namespace) -> int:
    if yaml is None:
        print("[hydra-audit] PyYAML is required", file=sys.stderr)
        return 4

    root = Path(args.config_root).expanduser().resolve()
    if not root.exists():
        print(f"[hydra-audit] config root not found: {root}", file=sys.stderr)
        return 2

    files = _scan_yaml_files(root)
    audits = [_audit_file(path, root) for path in files]

    payload: Dict[str, Any] = {
        "ok": True,
        "files": len(files),
        "issues": sum(len(audit.issues) for audit in audits),
        "unresolved_total": sum(len(audit.unresolved_keys) for audit in audits),
        "audits": [asdict(audit) for audit in audits],
    }

    out_json = Path(args.out_json).expanduser().resolve() if args.out_json else None
    if out_json:
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    out_md = Path(args.out_md).expanduser().resolve() if args.out_md else None
    if out_md:
        _write_markdown(out_md, audits)

    print(json.dumps(payload))
    return 0 if payload["issues"] == 0 else 3


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="codex hydra", description="Hydra defaults utilities")
    sub = parser.add_subparsers(dest="subcommand", required=True)
    defaults = sub.add_parser(
        "defaults-audit",
        help="Audit defaults/_self_ placement and unresolved interpolations",
    )
    defaults.add_argument(
        "--config-root",
        required=True,
        help="Root directory containing Hydra YAML configs",
    )
    defaults.add_argument("--out-json", help="Optional JSON report path")
    defaults.add_argument("--out-md", help="Optional Markdown report path")
    defaults.set_defaults(func=cmd_defaults_audit)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
