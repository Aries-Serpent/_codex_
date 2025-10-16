from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{2,}$", re.I)


@dataclass
class Component:
    tombstone: str
    dest_path: str
    mode: str = "0644"
    type: str = "file"  # file only in this scaffold
    template_vars: dict[str, Any] | None = None


@dataclass
class Symlink:
    link_path: str
    target: str


@dataclass
class Manifest:
    release_id: str
    version: str
    created_at: str
    actor: str
    target: dict[str, Any]
    components: list[Component]
    symlinks: list[Symlink]
    post_unpack_commands: list[str]
    checks: dict[str, Any]


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise ValueError(msg)


def _is_rel_safe(path: str) -> bool:
    # Disallow abs paths and path traversal
    return not (path.startswith("/") or ".." in Path(path).parts)


def load_manifest(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["version"], "missing version")
    _require("created_at" in data and data["created_at"], "missing created_at")
    _require("actor" in data and data["actor"], "missing actor")
    _require(
        "components" in data and isinstance(data["components"], list) and bool(data["components"]),
        "missing components[]",
    )
    components: list[Component] = []
    for c in data["components"]:
        _require("tombstone" in c and c["tombstone"], "component missing tombstone")
        _require("dest_path" in c and c["dest_path"], "component missing dest_path")
        _require(_is_rel_safe(c["dest_path"]), f"unsafe dest_path: {c['dest_path']}")
        components.append(
            Component(
                tombstone=c["tombstone"],
                dest_path=c["dest_path"],
                mode=c.get("mode", "0644"),
                type=c.get("type", "file"),
                template_vars=c.get("template_vars"),
            )
        )
    symlinks: list[Symlink] = []
    for s in data.get("symlinks", []):
        _require("link_path" in s and s["link_path"], "symlink missing link_path")
        _require("target" in s and s["target"], "symlink missing target")
        _require(_is_rel_safe(s["link_path"]), f"unsafe link_path: {s['link_path']}")
        symlinks.append(Symlink(link_path=s["link_path"], target=s["target"]))
    return Manifest(
        release_id=data["release_id"],
        version=data["version"],
        created_at=data["created_at"],
        actor=data["actor"],
        target=data.get("target", {}),
        components=components,
        symlinks=symlinks,
        post_unpack_commands=data.get("post_unpack_commands", []),
        checks=data.get("checks", {}),
    )


def dump_manifest_locked(m: dict[str, Any], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(m, indent=2), encoding="utf-8")
