"""
Manifest Module

This module provides functionality for manifest.

Usage:
    from release.manifest import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{2,}$", re.I)
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


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


def x__require__mutmut_orig(cond: bool, msg: str) -> None:
    if not cond:
        raise ValueError(msg)


def x__require__mutmut_1(cond: bool, msg: str) -> None:
    if cond:
        raise ValueError(msg)


def x__require__mutmut_2(cond: bool, msg: str) -> None:
    if not cond:
        raise ValueError(None)

x__require__mutmut_mutants : ClassVar[MutantDict] = {
'x__require__mutmut_1': x__require__mutmut_1, 
    'x__require__mutmut_2': x__require__mutmut_2
}

def _require(*args, **kwargs):
    result = _mutmut_trampoline(x__require__mutmut_orig, x__require__mutmut_mutants, args, kwargs)
    return result 

_require.__signature__ = _mutmut_signature(x__require__mutmut_orig)
x__require__mutmut_orig.__name__ = 'x__require'


def x__is_rel_safe__mutmut_orig(path: str) -> bool:
    # Disallow abs paths and path traversal
    return not (path.startswith("/") or ".." in Path(path).parts)


def x__is_rel_safe__mutmut_1(path: str) -> bool:
    # Disallow abs paths and path traversal
    return (path.startswith("/") or ".." in Path(path).parts)


def x__is_rel_safe__mutmut_2(path: str) -> bool:
    # Disallow abs paths and path traversal
    return not (path.startswith("/") and ".." in Path(path).parts)


def x__is_rel_safe__mutmut_3(path: str) -> bool:
    # Disallow abs paths and path traversal
    return not (path.startswith(None) or ".." in Path(path).parts)


def x__is_rel_safe__mutmut_4(path: str) -> bool:
    # Disallow abs paths and path traversal
    return not (path.startswith("XX/XX") or ".." in Path(path).parts)


def x__is_rel_safe__mutmut_5(path: str) -> bool:
    # Disallow abs paths and path traversal
    return not (path.startswith("/") or "XX..XX" in Path(path).parts)


def x__is_rel_safe__mutmut_6(path: str) -> bool:
    # Disallow abs paths and path traversal
    return not (path.startswith("/") or ".." not in Path(path).parts)


def x__is_rel_safe__mutmut_7(path: str) -> bool:
    # Disallow abs paths and path traversal
    return not (path.startswith("/") or ".." in Path(None).parts)

x__is_rel_safe__mutmut_mutants : ClassVar[MutantDict] = {
'x__is_rel_safe__mutmut_1': x__is_rel_safe__mutmut_1, 
    'x__is_rel_safe__mutmut_2': x__is_rel_safe__mutmut_2, 
    'x__is_rel_safe__mutmut_3': x__is_rel_safe__mutmut_3, 
    'x__is_rel_safe__mutmut_4': x__is_rel_safe__mutmut_4, 
    'x__is_rel_safe__mutmut_5': x__is_rel_safe__mutmut_5, 
    'x__is_rel_safe__mutmut_6': x__is_rel_safe__mutmut_6, 
    'x__is_rel_safe__mutmut_7': x__is_rel_safe__mutmut_7
}

def _is_rel_safe(*args, **kwargs):
    result = _mutmut_trampoline(x__is_rel_safe__mutmut_orig, x__is_rel_safe__mutmut_mutants, args, kwargs)
    return result 

_is_rel_safe.__signature__ = _mutmut_signature(x__is_rel_safe__mutmut_orig)
x__is_rel_safe__mutmut_orig.__name__ = 'x__is_rel_safe'


def x_load_manifest__mutmut_orig(p: Path) -> Manifest:
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


def x_load_manifest__mutmut_1(p: Path) -> Manifest:
    data = None
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


def x_load_manifest__mutmut_2(p: Path) -> Manifest:
    data = json.loads(None)
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


def x_load_manifest__mutmut_3(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding=None))
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


def x_load_manifest__mutmut_4(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="XXutf-8XX"))
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


def x_load_manifest__mutmut_5(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="UTF-8"))
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


def x_load_manifest__mutmut_6(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        None,
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


def x_load_manifest__mutmut_7(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        None,
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


def x_load_manifest__mutmut_8(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
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


def x_load_manifest__mutmut_9(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
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


def x_load_manifest__mutmut_10(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data or bool(_ID_RE.match(data["release_id"] or "")),
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


def x_load_manifest__mutmut_11(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "XXrelease_idXX" in data and bool(_ID_RE.match(data["release_id"] or "")),
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


def x_load_manifest__mutmut_12(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "RELEASE_ID" in data and bool(_ID_RE.match(data["release_id"] or "")),
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


def x_load_manifest__mutmut_13(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" not in data and bool(_ID_RE.match(data["release_id"] or "")),
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


def x_load_manifest__mutmut_14(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(None),
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


def x_load_manifest__mutmut_15(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(None)),
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


def x_load_manifest__mutmut_16(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] and "")),
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


def x_load_manifest__mutmut_17(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["XXrelease_idXX"] or "")),
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


def x_load_manifest__mutmut_18(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["RELEASE_ID"] or "")),
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


def x_load_manifest__mutmut_19(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "XXXX")),
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


def x_load_manifest__mutmut_20(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "XXinvalid or missing release_idXX",
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


def x_load_manifest__mutmut_21(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "INVALID OR MISSING RELEASE_ID",
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


def x_load_manifest__mutmut_22(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require(None, "missing version")
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


def x_load_manifest__mutmut_23(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["version"], None)
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


def x_load_manifest__mutmut_24(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("missing version")
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


def x_load_manifest__mutmut_25(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["version"], )
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


def x_load_manifest__mutmut_26(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data or data["version"], "missing version")
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


def x_load_manifest__mutmut_27(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("XXversionXX" in data and data["version"], "missing version")
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


def x_load_manifest__mutmut_28(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("VERSION" in data and data["version"], "missing version")
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


def x_load_manifest__mutmut_29(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" not in data and data["version"], "missing version")
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


def x_load_manifest__mutmut_30(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["XXversionXX"], "missing version")
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


def x_load_manifest__mutmut_31(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["VERSION"], "missing version")
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


def x_load_manifest__mutmut_32(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["version"], "XXmissing versionXX")
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


def x_load_manifest__mutmut_33(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["version"], "MISSING VERSION")
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


def x_load_manifest__mutmut_34(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["version"], "missing version")
    _require(None, "missing created_at")
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


def x_load_manifest__mutmut_35(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["version"], "missing version")
    _require("created_at" in data and data["created_at"], None)
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


def x_load_manifest__mutmut_36(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["version"], "missing version")
    _require("missing created_at")
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


def x_load_manifest__mutmut_37(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["version"], "missing version")
    _require("created_at" in data and data["created_at"], )
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


def x_load_manifest__mutmut_38(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["version"], "missing version")
    _require("created_at" in data or data["created_at"], "missing created_at")
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


def x_load_manifest__mutmut_39(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["version"], "missing version")
    _require("XXcreated_atXX" in data and data["created_at"], "missing created_at")
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


def x_load_manifest__mutmut_40(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["version"], "missing version")
    _require("CREATED_AT" in data and data["created_at"], "missing created_at")
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


def x_load_manifest__mutmut_41(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["version"], "missing version")
    _require("created_at" not in data and data["created_at"], "missing created_at")
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


def x_load_manifest__mutmut_42(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["version"], "missing version")
    _require("created_at" in data and data["XXcreated_atXX"], "missing created_at")
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


def x_load_manifest__mutmut_43(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["version"], "missing version")
    _require("created_at" in data and data["CREATED_AT"], "missing created_at")
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


def x_load_manifest__mutmut_44(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["version"], "missing version")
    _require("created_at" in data and data["created_at"], "XXmissing created_atXX")
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


def x_load_manifest__mutmut_45(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["version"], "missing version")
    _require("created_at" in data and data["created_at"], "MISSING CREATED_AT")
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


def x_load_manifest__mutmut_46(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["version"], "missing version")
    _require("created_at" in data and data["created_at"], "missing created_at")
    _require(None, "missing actor")
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


def x_load_manifest__mutmut_47(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["version"], "missing version")
    _require("created_at" in data and data["created_at"], "missing created_at")
    _require("actor" in data and data["actor"], None)
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


def x_load_manifest__mutmut_48(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["version"], "missing version")
    _require("created_at" in data and data["created_at"], "missing created_at")
    _require("missing actor")
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


def x_load_manifest__mutmut_49(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["version"], "missing version")
    _require("created_at" in data and data["created_at"], "missing created_at")
    _require("actor" in data and data["actor"], )
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


def x_load_manifest__mutmut_50(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["version"], "missing version")
    _require("created_at" in data and data["created_at"], "missing created_at")
    _require("actor" in data or data["actor"], "missing actor")
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


def x_load_manifest__mutmut_51(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["version"], "missing version")
    _require("created_at" in data and data["created_at"], "missing created_at")
    _require("XXactorXX" in data and data["actor"], "missing actor")
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


def x_load_manifest__mutmut_52(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["version"], "missing version")
    _require("created_at" in data and data["created_at"], "missing created_at")
    _require("ACTOR" in data and data["actor"], "missing actor")
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


def x_load_manifest__mutmut_53(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["version"], "missing version")
    _require("created_at" in data and data["created_at"], "missing created_at")
    _require("actor" not in data and data["actor"], "missing actor")
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


def x_load_manifest__mutmut_54(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["version"], "missing version")
    _require("created_at" in data and data["created_at"], "missing created_at")
    _require("actor" in data and data["XXactorXX"], "missing actor")
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


def x_load_manifest__mutmut_55(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["version"], "missing version")
    _require("created_at" in data and data["created_at"], "missing created_at")
    _require("actor" in data and data["ACTOR"], "missing actor")
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


def x_load_manifest__mutmut_56(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["version"], "missing version")
    _require("created_at" in data and data["created_at"], "missing created_at")
    _require("actor" in data and data["actor"], "XXmissing actorXX")
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


def x_load_manifest__mutmut_57(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["version"], "missing version")
    _require("created_at" in data and data["created_at"], "missing created_at")
    _require("actor" in data and data["actor"], "MISSING ACTOR")
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


def x_load_manifest__mutmut_58(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["version"], "missing version")
    _require("created_at" in data and data["created_at"], "missing created_at")
    _require("actor" in data and data["actor"], "missing actor")
    _require(
        None,
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


def x_load_manifest__mutmut_59(p: Path) -> Manifest:
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
        None,
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


def x_load_manifest__mutmut_60(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["version"], "missing version")
    _require("created_at" in data and data["created_at"], "missing created_at")
    _require("actor" in data and data["actor"], "missing actor")
    _require(
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


def x_load_manifest__mutmut_61(p: Path) -> Manifest:
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


def x_load_manifest__mutmut_62(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["version"], "missing version")
    _require("created_at" in data and data["created_at"], "missing created_at")
    _require("actor" in data and data["actor"], "missing actor")
    _require(
        "components" in data and isinstance(data["components"], list) or bool(data["components"]),
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


def x_load_manifest__mutmut_63(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["version"], "missing version")
    _require("created_at" in data and data["created_at"], "missing created_at")
    _require("actor" in data and data["actor"], "missing actor")
    _require(
        "components" in data or isinstance(data["components"], list) and bool(data["components"]),
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


def x_load_manifest__mutmut_64(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["version"], "missing version")
    _require("created_at" in data and data["created_at"], "missing created_at")
    _require("actor" in data and data["actor"], "missing actor")
    _require(
        "XXcomponentsXX" in data and isinstance(data["components"], list) and bool(data["components"]),
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


def x_load_manifest__mutmut_65(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["version"], "missing version")
    _require("created_at" in data and data["created_at"], "missing created_at")
    _require("actor" in data and data["actor"], "missing actor")
    _require(
        "COMPONENTS" in data and isinstance(data["components"], list) and bool(data["components"]),
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


def x_load_manifest__mutmut_66(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["version"], "missing version")
    _require("created_at" in data and data["created_at"], "missing created_at")
    _require("actor" in data and data["actor"], "missing actor")
    _require(
        "components" not in data and isinstance(data["components"], list) and bool(data["components"]),
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


def x_load_manifest__mutmut_67(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["version"], "missing version")
    _require("created_at" in data and data["created_at"], "missing created_at")
    _require("actor" in data and data["actor"], "missing actor")
    _require(
        "components" in data and isinstance(data["components"], list) and bool(None),
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


def x_load_manifest__mutmut_68(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["version"], "missing version")
    _require("created_at" in data and data["created_at"], "missing created_at")
    _require("actor" in data and data["actor"], "missing actor")
    _require(
        "components" in data and isinstance(data["components"], list) and bool(data["XXcomponentsXX"]),
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


def x_load_manifest__mutmut_69(p: Path) -> Manifest:
    data = json.loads(p.read_text(encoding="utf-8"))
    _require(
        "release_id" in data and bool(_ID_RE.match(data["release_id"] or "")),
        "invalid or missing release_id",
    )
    _require("version" in data and data["version"], "missing version")
    _require("created_at" in data and data["created_at"], "missing created_at")
    _require("actor" in data and data["actor"], "missing actor")
    _require(
        "components" in data and isinstance(data["components"], list) and bool(data["COMPONENTS"]),
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


def x_load_manifest__mutmut_70(p: Path) -> Manifest:
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
        "XXmissing components[]XX",
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


def x_load_manifest__mutmut_71(p: Path) -> Manifest:
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
        "MISSING COMPONENTS[]",
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


def x_load_manifest__mutmut_72(p: Path) -> Manifest:
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
    components: list[Component] = None
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


def x_load_manifest__mutmut_73(p: Path) -> Manifest:
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
    for c in data["XXcomponentsXX"]:
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


def x_load_manifest__mutmut_74(p: Path) -> Manifest:
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
    for c in data["COMPONENTS"]:
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


def x_load_manifest__mutmut_75(p: Path) -> Manifest:
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
        _require(None, "component missing tombstone")
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


def x_load_manifest__mutmut_76(p: Path) -> Manifest:
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
        _require("tombstone" in c and c["tombstone"], None)
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


def x_load_manifest__mutmut_77(p: Path) -> Manifest:
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
        _require("component missing tombstone")
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


def x_load_manifest__mutmut_78(p: Path) -> Manifest:
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
        _require("tombstone" in c and c["tombstone"], )
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


def x_load_manifest__mutmut_79(p: Path) -> Manifest:
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
        _require("tombstone" in c or c["tombstone"], "component missing tombstone")
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


def x_load_manifest__mutmut_80(p: Path) -> Manifest:
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
        _require("XXtombstoneXX" in c and c["tombstone"], "component missing tombstone")
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


def x_load_manifest__mutmut_81(p: Path) -> Manifest:
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
        _require("TOMBSTONE" in c and c["tombstone"], "component missing tombstone")
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


def x_load_manifest__mutmut_82(p: Path) -> Manifest:
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
        _require("tombstone" not in c and c["tombstone"], "component missing tombstone")
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


def x_load_manifest__mutmut_83(p: Path) -> Manifest:
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
        _require("tombstone" in c and c["XXtombstoneXX"], "component missing tombstone")
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


def x_load_manifest__mutmut_84(p: Path) -> Manifest:
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
        _require("tombstone" in c and c["TOMBSTONE"], "component missing tombstone")
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


def x_load_manifest__mutmut_85(p: Path) -> Manifest:
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
        _require("tombstone" in c and c["tombstone"], "XXcomponent missing tombstoneXX")
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


def x_load_manifest__mutmut_86(p: Path) -> Manifest:
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
        _require("tombstone" in c and c["tombstone"], "COMPONENT MISSING TOMBSTONE")
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


def x_load_manifest__mutmut_87(p: Path) -> Manifest:
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
        _require(None, "component missing dest_path")
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


def x_load_manifest__mutmut_88(p: Path) -> Manifest:
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
        _require("dest_path" in c and c["dest_path"], None)
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


def x_load_manifest__mutmut_89(p: Path) -> Manifest:
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
        _require("component missing dest_path")
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


def x_load_manifest__mutmut_90(p: Path) -> Manifest:
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
        _require("dest_path" in c and c["dest_path"], )
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


def x_load_manifest__mutmut_91(p: Path) -> Manifest:
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
        _require("dest_path" in c or c["dest_path"], "component missing dest_path")
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


def x_load_manifest__mutmut_92(p: Path) -> Manifest:
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
        _require("XXdest_pathXX" in c and c["dest_path"], "component missing dest_path")
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


def x_load_manifest__mutmut_93(p: Path) -> Manifest:
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
        _require("DEST_PATH" in c and c["dest_path"], "component missing dest_path")
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


def x_load_manifest__mutmut_94(p: Path) -> Manifest:
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
        _require("dest_path" not in c and c["dest_path"], "component missing dest_path")
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


def x_load_manifest__mutmut_95(p: Path) -> Manifest:
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
        _require("dest_path" in c and c["XXdest_pathXX"], "component missing dest_path")
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


def x_load_manifest__mutmut_96(p: Path) -> Manifest:
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
        _require("dest_path" in c and c["DEST_PATH"], "component missing dest_path")
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


def x_load_manifest__mutmut_97(p: Path) -> Manifest:
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
        _require("dest_path" in c and c["dest_path"], "XXcomponent missing dest_pathXX")
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


def x_load_manifest__mutmut_98(p: Path) -> Manifest:
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
        _require("dest_path" in c and c["dest_path"], "COMPONENT MISSING DEST_PATH")
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


def x_load_manifest__mutmut_99(p: Path) -> Manifest:
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
        _require(None, f"unsafe dest_path: {c['dest_path']}")
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


def x_load_manifest__mutmut_100(p: Path) -> Manifest:
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
        _require(_is_rel_safe(c["dest_path"]), None)
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


def x_load_manifest__mutmut_101(p: Path) -> Manifest:
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
        _require(f"unsafe dest_path: {c['dest_path']}")
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


def x_load_manifest__mutmut_102(p: Path) -> Manifest:
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
        _require(_is_rel_safe(c["dest_path"]), )
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


def x_load_manifest__mutmut_103(p: Path) -> Manifest:
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
        _require(_is_rel_safe(None), f"unsafe dest_path: {c['dest_path']}")
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


def x_load_manifest__mutmut_104(p: Path) -> Manifest:
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
        _require(_is_rel_safe(c["XXdest_pathXX"]), f"unsafe dest_path: {c['dest_path']}")
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


def x_load_manifest__mutmut_105(p: Path) -> Manifest:
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
        _require(_is_rel_safe(c["DEST_PATH"]), f"unsafe dest_path: {c['dest_path']}")
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


def x_load_manifest__mutmut_106(p: Path) -> Manifest:
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
        _require(_is_rel_safe(c["dest_path"]), f"unsafe dest_path: {c['XXdest_pathXX']}")
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


def x_load_manifest__mutmut_107(p: Path) -> Manifest:
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
        _require(_is_rel_safe(c["dest_path"]), f"unsafe dest_path: {c['DEST_PATH']}")
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


def x_load_manifest__mutmut_108(p: Path) -> Manifest:
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
            None
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


def x_load_manifest__mutmut_109(p: Path) -> Manifest:
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
                tombstone=None,
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


def x_load_manifest__mutmut_110(p: Path) -> Manifest:
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
                dest_path=None,
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


def x_load_manifest__mutmut_111(p: Path) -> Manifest:
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
                mode=None,
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


def x_load_manifest__mutmut_112(p: Path) -> Manifest:
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
                type=None,
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


def x_load_manifest__mutmut_113(p: Path) -> Manifest:
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
                template_vars=None,
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


def x_load_manifest__mutmut_114(p: Path) -> Manifest:
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


def x_load_manifest__mutmut_115(p: Path) -> Manifest:
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


def x_load_manifest__mutmut_116(p: Path) -> Manifest:
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


def x_load_manifest__mutmut_117(p: Path) -> Manifest:
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


def x_load_manifest__mutmut_118(p: Path) -> Manifest:
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


def x_load_manifest__mutmut_119(p: Path) -> Manifest:
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
                tombstone=c["XXtombstoneXX"],
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


def x_load_manifest__mutmut_120(p: Path) -> Manifest:
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
                tombstone=c["TOMBSTONE"],
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


def x_load_manifest__mutmut_121(p: Path) -> Manifest:
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
                dest_path=c["XXdest_pathXX"],
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


def x_load_manifest__mutmut_122(p: Path) -> Manifest:
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
                dest_path=c["DEST_PATH"],
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


def x_load_manifest__mutmut_123(p: Path) -> Manifest:
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
                mode=c.get(None, "0644"),
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


def x_load_manifest__mutmut_124(p: Path) -> Manifest:
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
                mode=c.get("mode", None),
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


def x_load_manifest__mutmut_125(p: Path) -> Manifest:
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
                mode=c.get("0644"),
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


def x_load_manifest__mutmut_126(p: Path) -> Manifest:
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
                mode=c.get("mode", ),
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


def x_load_manifest__mutmut_127(p: Path) -> Manifest:
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
                mode=c.get("XXmodeXX", "0644"),
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


def x_load_manifest__mutmut_128(p: Path) -> Manifest:
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
                mode=c.get("MODE", "0644"),
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


def x_load_manifest__mutmut_129(p: Path) -> Manifest:
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
                mode=c.get("mode", "XX0644XX"),
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


def x_load_manifest__mutmut_130(p: Path) -> Manifest:
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
                type=c.get(None, "file"),
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


def x_load_manifest__mutmut_131(p: Path) -> Manifest:
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
                type=c.get("type", None),
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


def x_load_manifest__mutmut_132(p: Path) -> Manifest:
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
                type=c.get("file"),
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


def x_load_manifest__mutmut_133(p: Path) -> Manifest:
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
                type=c.get("type", ),
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


def x_load_manifest__mutmut_134(p: Path) -> Manifest:
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
                type=c.get("XXtypeXX", "file"),
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


def x_load_manifest__mutmut_135(p: Path) -> Manifest:
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
                type=c.get("TYPE", "file"),
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


def x_load_manifest__mutmut_136(p: Path) -> Manifest:
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
                type=c.get("type", "XXfileXX"),
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


def x_load_manifest__mutmut_137(p: Path) -> Manifest:
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
                type=c.get("type", "FILE"),
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


def x_load_manifest__mutmut_138(p: Path) -> Manifest:
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
                template_vars=c.get(None),
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


def x_load_manifest__mutmut_139(p: Path) -> Manifest:
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
                template_vars=c.get("XXtemplate_varsXX"),
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


def x_load_manifest__mutmut_140(p: Path) -> Manifest:
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
                template_vars=c.get("TEMPLATE_VARS"),
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


def x_load_manifest__mutmut_141(p: Path) -> Manifest:
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
    symlinks: list[Symlink] = None
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


def x_load_manifest__mutmut_142(p: Path) -> Manifest:
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
    for s in data.get(None, []):
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


def x_load_manifest__mutmut_143(p: Path) -> Manifest:
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
    for s in data.get("symlinks", None):
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


def x_load_manifest__mutmut_144(p: Path) -> Manifest:
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
    for s in data.get([]):
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


def x_load_manifest__mutmut_145(p: Path) -> Manifest:
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
    for s in data.get("symlinks", ):
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


def x_load_manifest__mutmut_146(p: Path) -> Manifest:
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
    for s in data.get("XXsymlinksXX", []):
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


def x_load_manifest__mutmut_147(p: Path) -> Manifest:
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
    for s in data.get("SYMLINKS", []):
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


def x_load_manifest__mutmut_148(p: Path) -> Manifest:
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
        _require(None, "symlink missing link_path")
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


def x_load_manifest__mutmut_149(p: Path) -> Manifest:
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
        _require("link_path" in s and s["link_path"], None)
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


def x_load_manifest__mutmut_150(p: Path) -> Manifest:
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
        _require("symlink missing link_path")
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


def x_load_manifest__mutmut_151(p: Path) -> Manifest:
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
        _require("link_path" in s and s["link_path"], )
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


def x_load_manifest__mutmut_152(p: Path) -> Manifest:
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
        _require("link_path" in s or s["link_path"], "symlink missing link_path")
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


def x_load_manifest__mutmut_153(p: Path) -> Manifest:
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
        _require("XXlink_pathXX" in s and s["link_path"], "symlink missing link_path")
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


def x_load_manifest__mutmut_154(p: Path) -> Manifest:
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
        _require("LINK_PATH" in s and s["link_path"], "symlink missing link_path")
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


def x_load_manifest__mutmut_155(p: Path) -> Manifest:
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
        _require("link_path" not in s and s["link_path"], "symlink missing link_path")
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


def x_load_manifest__mutmut_156(p: Path) -> Manifest:
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
        _require("link_path" in s and s["XXlink_pathXX"], "symlink missing link_path")
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


def x_load_manifest__mutmut_157(p: Path) -> Manifest:
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
        _require("link_path" in s and s["LINK_PATH"], "symlink missing link_path")
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


def x_load_manifest__mutmut_158(p: Path) -> Manifest:
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
        _require("link_path" in s and s["link_path"], "XXsymlink missing link_pathXX")
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


def x_load_manifest__mutmut_159(p: Path) -> Manifest:
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
        _require("link_path" in s and s["link_path"], "SYMLINK MISSING LINK_PATH")
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


def x_load_manifest__mutmut_160(p: Path) -> Manifest:
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
        _require(None, "symlink missing target")
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


def x_load_manifest__mutmut_161(p: Path) -> Manifest:
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
        _require("target" in s and s["target"], None)
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


def x_load_manifest__mutmut_162(p: Path) -> Manifest:
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
        _require("symlink missing target")
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


def x_load_manifest__mutmut_163(p: Path) -> Manifest:
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
        _require("target" in s and s["target"], )
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


def x_load_manifest__mutmut_164(p: Path) -> Manifest:
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
        _require("target" in s or s["target"], "symlink missing target")
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


def x_load_manifest__mutmut_165(p: Path) -> Manifest:
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
        _require("XXtargetXX" in s and s["target"], "symlink missing target")
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


def x_load_manifest__mutmut_166(p: Path) -> Manifest:
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
        _require("TARGET" in s and s["target"], "symlink missing target")
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


def x_load_manifest__mutmut_167(p: Path) -> Manifest:
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
        _require("target" not in s and s["target"], "symlink missing target")
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


def x_load_manifest__mutmut_168(p: Path) -> Manifest:
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
        _require("target" in s and s["XXtargetXX"], "symlink missing target")
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


def x_load_manifest__mutmut_169(p: Path) -> Manifest:
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
        _require("target" in s and s["TARGET"], "symlink missing target")
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


def x_load_manifest__mutmut_170(p: Path) -> Manifest:
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
        _require("target" in s and s["target"], "XXsymlink missing targetXX")
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


def x_load_manifest__mutmut_171(p: Path) -> Manifest:
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
        _require("target" in s and s["target"], "SYMLINK MISSING TARGET")
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


def x_load_manifest__mutmut_172(p: Path) -> Manifest:
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
        _require(None, f"unsafe link_path: {s['link_path']}")
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


def x_load_manifest__mutmut_173(p: Path) -> Manifest:
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
        _require(_is_rel_safe(s["link_path"]), None)
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


def x_load_manifest__mutmut_174(p: Path) -> Manifest:
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
        _require(f"unsafe link_path: {s['link_path']}")
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


def x_load_manifest__mutmut_175(p: Path) -> Manifest:
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
        _require(_is_rel_safe(s["link_path"]), )
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


def x_load_manifest__mutmut_176(p: Path) -> Manifest:
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
        _require(_is_rel_safe(None), f"unsafe link_path: {s['link_path']}")
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


def x_load_manifest__mutmut_177(p: Path) -> Manifest:
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
        _require(_is_rel_safe(s["XXlink_pathXX"]), f"unsafe link_path: {s['link_path']}")
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


def x_load_manifest__mutmut_178(p: Path) -> Manifest:
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
        _require(_is_rel_safe(s["LINK_PATH"]), f"unsafe link_path: {s['link_path']}")
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


def x_load_manifest__mutmut_179(p: Path) -> Manifest:
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
        _require(_is_rel_safe(s["link_path"]), f"unsafe link_path: {s['XXlink_pathXX']}")
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


def x_load_manifest__mutmut_180(p: Path) -> Manifest:
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
        _require(_is_rel_safe(s["link_path"]), f"unsafe link_path: {s['LINK_PATH']}")
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


def x_load_manifest__mutmut_181(p: Path) -> Manifest:
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
        symlinks.append(None)
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


def x_load_manifest__mutmut_182(p: Path) -> Manifest:
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
        symlinks.append(Symlink(link_path=None, target=s["target"]))
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


def x_load_manifest__mutmut_183(p: Path) -> Manifest:
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
        symlinks.append(Symlink(link_path=s["link_path"], target=None))
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


def x_load_manifest__mutmut_184(p: Path) -> Manifest:
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
        symlinks.append(Symlink(target=s["target"]))
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


def x_load_manifest__mutmut_185(p: Path) -> Manifest:
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
        symlinks.append(Symlink(link_path=s["link_path"], ))
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


def x_load_manifest__mutmut_186(p: Path) -> Manifest:
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
        symlinks.append(Symlink(link_path=s["XXlink_pathXX"], target=s["target"]))
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


def x_load_manifest__mutmut_187(p: Path) -> Manifest:
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
        symlinks.append(Symlink(link_path=s["LINK_PATH"], target=s["target"]))
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


def x_load_manifest__mutmut_188(p: Path) -> Manifest:
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
        symlinks.append(Symlink(link_path=s["link_path"], target=s["XXtargetXX"]))
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


def x_load_manifest__mutmut_189(p: Path) -> Manifest:
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
        symlinks.append(Symlink(link_path=s["link_path"], target=s["TARGET"]))
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


def x_load_manifest__mutmut_190(p: Path) -> Manifest:
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
        release_id=None,
        version=data["version"],
        created_at=data["created_at"],
        actor=data["actor"],
        target=data.get("target", {}),
        components=components,
        symlinks=symlinks,
        post_unpack_commands=data.get("post_unpack_commands", []),
        checks=data.get("checks", {}),
    )


def x_load_manifest__mutmut_191(p: Path) -> Manifest:
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
        version=None,
        created_at=data["created_at"],
        actor=data["actor"],
        target=data.get("target", {}),
        components=components,
        symlinks=symlinks,
        post_unpack_commands=data.get("post_unpack_commands", []),
        checks=data.get("checks", {}),
    )


def x_load_manifest__mutmut_192(p: Path) -> Manifest:
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
        created_at=None,
        actor=data["actor"],
        target=data.get("target", {}),
        components=components,
        symlinks=symlinks,
        post_unpack_commands=data.get("post_unpack_commands", []),
        checks=data.get("checks", {}),
    )


def x_load_manifest__mutmut_193(p: Path) -> Manifest:
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
        actor=None,
        target=data.get("target", {}),
        components=components,
        symlinks=symlinks,
        post_unpack_commands=data.get("post_unpack_commands", []),
        checks=data.get("checks", {}),
    )


def x_load_manifest__mutmut_194(p: Path) -> Manifest:
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
        target=None,
        components=components,
        symlinks=symlinks,
        post_unpack_commands=data.get("post_unpack_commands", []),
        checks=data.get("checks", {}),
    )


def x_load_manifest__mutmut_195(p: Path) -> Manifest:
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
        components=None,
        symlinks=symlinks,
        post_unpack_commands=data.get("post_unpack_commands", []),
        checks=data.get("checks", {}),
    )


def x_load_manifest__mutmut_196(p: Path) -> Manifest:
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
        symlinks=None,
        post_unpack_commands=data.get("post_unpack_commands", []),
        checks=data.get("checks", {}),
    )


def x_load_manifest__mutmut_197(p: Path) -> Manifest:
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
        post_unpack_commands=None,
        checks=data.get("checks", {}),
    )


def x_load_manifest__mutmut_198(p: Path) -> Manifest:
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
        checks=None,
    )


def x_load_manifest__mutmut_199(p: Path) -> Manifest:
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
        version=data["version"],
        created_at=data["created_at"],
        actor=data["actor"],
        target=data.get("target", {}),
        components=components,
        symlinks=symlinks,
        post_unpack_commands=data.get("post_unpack_commands", []),
        checks=data.get("checks", {}),
    )


def x_load_manifest__mutmut_200(p: Path) -> Manifest:
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
        created_at=data["created_at"],
        actor=data["actor"],
        target=data.get("target", {}),
        components=components,
        symlinks=symlinks,
        post_unpack_commands=data.get("post_unpack_commands", []),
        checks=data.get("checks", {}),
    )


def x_load_manifest__mutmut_201(p: Path) -> Manifest:
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
        actor=data["actor"],
        target=data.get("target", {}),
        components=components,
        symlinks=symlinks,
        post_unpack_commands=data.get("post_unpack_commands", []),
        checks=data.get("checks", {}),
    )


def x_load_manifest__mutmut_202(p: Path) -> Manifest:
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
        target=data.get("target", {}),
        components=components,
        symlinks=symlinks,
        post_unpack_commands=data.get("post_unpack_commands", []),
        checks=data.get("checks", {}),
    )


def x_load_manifest__mutmut_203(p: Path) -> Manifest:
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
        components=components,
        symlinks=symlinks,
        post_unpack_commands=data.get("post_unpack_commands", []),
        checks=data.get("checks", {}),
    )


def x_load_manifest__mutmut_204(p: Path) -> Manifest:
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
        symlinks=symlinks,
        post_unpack_commands=data.get("post_unpack_commands", []),
        checks=data.get("checks", {}),
    )


def x_load_manifest__mutmut_205(p: Path) -> Manifest:
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
        post_unpack_commands=data.get("post_unpack_commands", []),
        checks=data.get("checks", {}),
    )


def x_load_manifest__mutmut_206(p: Path) -> Manifest:
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
        checks=data.get("checks", {}),
    )


def x_load_manifest__mutmut_207(p: Path) -> Manifest:
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
        )


def x_load_manifest__mutmut_208(p: Path) -> Manifest:
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
        release_id=data["XXrelease_idXX"],
        version=data["version"],
        created_at=data["created_at"],
        actor=data["actor"],
        target=data.get("target", {}),
        components=components,
        symlinks=symlinks,
        post_unpack_commands=data.get("post_unpack_commands", []),
        checks=data.get("checks", {}),
    )


def x_load_manifest__mutmut_209(p: Path) -> Manifest:
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
        release_id=data["RELEASE_ID"],
        version=data["version"],
        created_at=data["created_at"],
        actor=data["actor"],
        target=data.get("target", {}),
        components=components,
        symlinks=symlinks,
        post_unpack_commands=data.get("post_unpack_commands", []),
        checks=data.get("checks", {}),
    )


def x_load_manifest__mutmut_210(p: Path) -> Manifest:
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
        version=data["XXversionXX"],
        created_at=data["created_at"],
        actor=data["actor"],
        target=data.get("target", {}),
        components=components,
        symlinks=symlinks,
        post_unpack_commands=data.get("post_unpack_commands", []),
        checks=data.get("checks", {}),
    )


def x_load_manifest__mutmut_211(p: Path) -> Manifest:
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
        version=data["VERSION"],
        created_at=data["created_at"],
        actor=data["actor"],
        target=data.get("target", {}),
        components=components,
        symlinks=symlinks,
        post_unpack_commands=data.get("post_unpack_commands", []),
        checks=data.get("checks", {}),
    )


def x_load_manifest__mutmut_212(p: Path) -> Manifest:
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
        created_at=data["XXcreated_atXX"],
        actor=data["actor"],
        target=data.get("target", {}),
        components=components,
        symlinks=symlinks,
        post_unpack_commands=data.get("post_unpack_commands", []),
        checks=data.get("checks", {}),
    )


def x_load_manifest__mutmut_213(p: Path) -> Manifest:
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
        created_at=data["CREATED_AT"],
        actor=data["actor"],
        target=data.get("target", {}),
        components=components,
        symlinks=symlinks,
        post_unpack_commands=data.get("post_unpack_commands", []),
        checks=data.get("checks", {}),
    )


def x_load_manifest__mutmut_214(p: Path) -> Manifest:
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
        actor=data["XXactorXX"],
        target=data.get("target", {}),
        components=components,
        symlinks=symlinks,
        post_unpack_commands=data.get("post_unpack_commands", []),
        checks=data.get("checks", {}),
    )


def x_load_manifest__mutmut_215(p: Path) -> Manifest:
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
        actor=data["ACTOR"],
        target=data.get("target", {}),
        components=components,
        symlinks=symlinks,
        post_unpack_commands=data.get("post_unpack_commands", []),
        checks=data.get("checks", {}),
    )


def x_load_manifest__mutmut_216(p: Path) -> Manifest:
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
        target=data.get(None, {}),
        components=components,
        symlinks=symlinks,
        post_unpack_commands=data.get("post_unpack_commands", []),
        checks=data.get("checks", {}),
    )


def x_load_manifest__mutmut_217(p: Path) -> Manifest:
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
        target=data.get("target", None),
        components=components,
        symlinks=symlinks,
        post_unpack_commands=data.get("post_unpack_commands", []),
        checks=data.get("checks", {}),
    )


def x_load_manifest__mutmut_218(p: Path) -> Manifest:
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
        target=data.get({}),
        components=components,
        symlinks=symlinks,
        post_unpack_commands=data.get("post_unpack_commands", []),
        checks=data.get("checks", {}),
    )


def x_load_manifest__mutmut_219(p: Path) -> Manifest:
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
        target=data.get("target", ),
        components=components,
        symlinks=symlinks,
        post_unpack_commands=data.get("post_unpack_commands", []),
        checks=data.get("checks", {}),
    )


def x_load_manifest__mutmut_220(p: Path) -> Manifest:
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
        target=data.get("XXtargetXX", {}),
        components=components,
        symlinks=symlinks,
        post_unpack_commands=data.get("post_unpack_commands", []),
        checks=data.get("checks", {}),
    )


def x_load_manifest__mutmut_221(p: Path) -> Manifest:
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
        target=data.get("TARGET", {}),
        components=components,
        symlinks=symlinks,
        post_unpack_commands=data.get("post_unpack_commands", []),
        checks=data.get("checks", {}),
    )


def x_load_manifest__mutmut_222(p: Path) -> Manifest:
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
        post_unpack_commands=data.get(None, []),
        checks=data.get("checks", {}),
    )


def x_load_manifest__mutmut_223(p: Path) -> Manifest:
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
        post_unpack_commands=data.get("post_unpack_commands", None),
        checks=data.get("checks", {}),
    )


def x_load_manifest__mutmut_224(p: Path) -> Manifest:
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
        post_unpack_commands=data.get([]),
        checks=data.get("checks", {}),
    )


def x_load_manifest__mutmut_225(p: Path) -> Manifest:
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
        post_unpack_commands=data.get("post_unpack_commands", ),
        checks=data.get("checks", {}),
    )


def x_load_manifest__mutmut_226(p: Path) -> Manifest:
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
        post_unpack_commands=data.get("XXpost_unpack_commandsXX", []),
        checks=data.get("checks", {}),
    )


def x_load_manifest__mutmut_227(p: Path) -> Manifest:
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
        post_unpack_commands=data.get("POST_UNPACK_COMMANDS", []),
        checks=data.get("checks", {}),
    )


def x_load_manifest__mutmut_228(p: Path) -> Manifest:
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
        checks=data.get(None, {}),
    )


def x_load_manifest__mutmut_229(p: Path) -> Manifest:
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
        checks=data.get("checks", None),
    )


def x_load_manifest__mutmut_230(p: Path) -> Manifest:
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
        checks=data.get({}),
    )


def x_load_manifest__mutmut_231(p: Path) -> Manifest:
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
        checks=data.get("checks", ),
    )


def x_load_manifest__mutmut_232(p: Path) -> Manifest:
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
        checks=data.get("XXchecksXX", {}),
    )


def x_load_manifest__mutmut_233(p: Path) -> Manifest:
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
        checks=data.get("CHECKS", {}),
    )

x_load_manifest__mutmut_mutants : ClassVar[MutantDict] = {
'x_load_manifest__mutmut_1': x_load_manifest__mutmut_1, 
    'x_load_manifest__mutmut_2': x_load_manifest__mutmut_2, 
    'x_load_manifest__mutmut_3': x_load_manifest__mutmut_3, 
    'x_load_manifest__mutmut_4': x_load_manifest__mutmut_4, 
    'x_load_manifest__mutmut_5': x_load_manifest__mutmut_5, 
    'x_load_manifest__mutmut_6': x_load_manifest__mutmut_6, 
    'x_load_manifest__mutmut_7': x_load_manifest__mutmut_7, 
    'x_load_manifest__mutmut_8': x_load_manifest__mutmut_8, 
    'x_load_manifest__mutmut_9': x_load_manifest__mutmut_9, 
    'x_load_manifest__mutmut_10': x_load_manifest__mutmut_10, 
    'x_load_manifest__mutmut_11': x_load_manifest__mutmut_11, 
    'x_load_manifest__mutmut_12': x_load_manifest__mutmut_12, 
    'x_load_manifest__mutmut_13': x_load_manifest__mutmut_13, 
    'x_load_manifest__mutmut_14': x_load_manifest__mutmut_14, 
    'x_load_manifest__mutmut_15': x_load_manifest__mutmut_15, 
    'x_load_manifest__mutmut_16': x_load_manifest__mutmut_16, 
    'x_load_manifest__mutmut_17': x_load_manifest__mutmut_17, 
    'x_load_manifest__mutmut_18': x_load_manifest__mutmut_18, 
    'x_load_manifest__mutmut_19': x_load_manifest__mutmut_19, 
    'x_load_manifest__mutmut_20': x_load_manifest__mutmut_20, 
    'x_load_manifest__mutmut_21': x_load_manifest__mutmut_21, 
    'x_load_manifest__mutmut_22': x_load_manifest__mutmut_22, 
    'x_load_manifest__mutmut_23': x_load_manifest__mutmut_23, 
    'x_load_manifest__mutmut_24': x_load_manifest__mutmut_24, 
    'x_load_manifest__mutmut_25': x_load_manifest__mutmut_25, 
    'x_load_manifest__mutmut_26': x_load_manifest__mutmut_26, 
    'x_load_manifest__mutmut_27': x_load_manifest__mutmut_27, 
    'x_load_manifest__mutmut_28': x_load_manifest__mutmut_28, 
    'x_load_manifest__mutmut_29': x_load_manifest__mutmut_29, 
    'x_load_manifest__mutmut_30': x_load_manifest__mutmut_30, 
    'x_load_manifest__mutmut_31': x_load_manifest__mutmut_31, 
    'x_load_manifest__mutmut_32': x_load_manifest__mutmut_32, 
    'x_load_manifest__mutmut_33': x_load_manifest__mutmut_33, 
    'x_load_manifest__mutmut_34': x_load_manifest__mutmut_34, 
    'x_load_manifest__mutmut_35': x_load_manifest__mutmut_35, 
    'x_load_manifest__mutmut_36': x_load_manifest__mutmut_36, 
    'x_load_manifest__mutmut_37': x_load_manifest__mutmut_37, 
    'x_load_manifest__mutmut_38': x_load_manifest__mutmut_38, 
    'x_load_manifest__mutmut_39': x_load_manifest__mutmut_39, 
    'x_load_manifest__mutmut_40': x_load_manifest__mutmut_40, 
    'x_load_manifest__mutmut_41': x_load_manifest__mutmut_41, 
    'x_load_manifest__mutmut_42': x_load_manifest__mutmut_42, 
    'x_load_manifest__mutmut_43': x_load_manifest__mutmut_43, 
    'x_load_manifest__mutmut_44': x_load_manifest__mutmut_44, 
    'x_load_manifest__mutmut_45': x_load_manifest__mutmut_45, 
    'x_load_manifest__mutmut_46': x_load_manifest__mutmut_46, 
    'x_load_manifest__mutmut_47': x_load_manifest__mutmut_47, 
    'x_load_manifest__mutmut_48': x_load_manifest__mutmut_48, 
    'x_load_manifest__mutmut_49': x_load_manifest__mutmut_49, 
    'x_load_manifest__mutmut_50': x_load_manifest__mutmut_50, 
    'x_load_manifest__mutmut_51': x_load_manifest__mutmut_51, 
    'x_load_manifest__mutmut_52': x_load_manifest__mutmut_52, 
    'x_load_manifest__mutmut_53': x_load_manifest__mutmut_53, 
    'x_load_manifest__mutmut_54': x_load_manifest__mutmut_54, 
    'x_load_manifest__mutmut_55': x_load_manifest__mutmut_55, 
    'x_load_manifest__mutmut_56': x_load_manifest__mutmut_56, 
    'x_load_manifest__mutmut_57': x_load_manifest__mutmut_57, 
    'x_load_manifest__mutmut_58': x_load_manifest__mutmut_58, 
    'x_load_manifest__mutmut_59': x_load_manifest__mutmut_59, 
    'x_load_manifest__mutmut_60': x_load_manifest__mutmut_60, 
    'x_load_manifest__mutmut_61': x_load_manifest__mutmut_61, 
    'x_load_manifest__mutmut_62': x_load_manifest__mutmut_62, 
    'x_load_manifest__mutmut_63': x_load_manifest__mutmut_63, 
    'x_load_manifest__mutmut_64': x_load_manifest__mutmut_64, 
    'x_load_manifest__mutmut_65': x_load_manifest__mutmut_65, 
    'x_load_manifest__mutmut_66': x_load_manifest__mutmut_66, 
    'x_load_manifest__mutmut_67': x_load_manifest__mutmut_67, 
    'x_load_manifest__mutmut_68': x_load_manifest__mutmut_68, 
    'x_load_manifest__mutmut_69': x_load_manifest__mutmut_69, 
    'x_load_manifest__mutmut_70': x_load_manifest__mutmut_70, 
    'x_load_manifest__mutmut_71': x_load_manifest__mutmut_71, 
    'x_load_manifest__mutmut_72': x_load_manifest__mutmut_72, 
    'x_load_manifest__mutmut_73': x_load_manifest__mutmut_73, 
    'x_load_manifest__mutmut_74': x_load_manifest__mutmut_74, 
    'x_load_manifest__mutmut_75': x_load_manifest__mutmut_75, 
    'x_load_manifest__mutmut_76': x_load_manifest__mutmut_76, 
    'x_load_manifest__mutmut_77': x_load_manifest__mutmut_77, 
    'x_load_manifest__mutmut_78': x_load_manifest__mutmut_78, 
    'x_load_manifest__mutmut_79': x_load_manifest__mutmut_79, 
    'x_load_manifest__mutmut_80': x_load_manifest__mutmut_80, 
    'x_load_manifest__mutmut_81': x_load_manifest__mutmut_81, 
    'x_load_manifest__mutmut_82': x_load_manifest__mutmut_82, 
    'x_load_manifest__mutmut_83': x_load_manifest__mutmut_83, 
    'x_load_manifest__mutmut_84': x_load_manifest__mutmut_84, 
    'x_load_manifest__mutmut_85': x_load_manifest__mutmut_85, 
    'x_load_manifest__mutmut_86': x_load_manifest__mutmut_86, 
    'x_load_manifest__mutmut_87': x_load_manifest__mutmut_87, 
    'x_load_manifest__mutmut_88': x_load_manifest__mutmut_88, 
    'x_load_manifest__mutmut_89': x_load_manifest__mutmut_89, 
    'x_load_manifest__mutmut_90': x_load_manifest__mutmut_90, 
    'x_load_manifest__mutmut_91': x_load_manifest__mutmut_91, 
    'x_load_manifest__mutmut_92': x_load_manifest__mutmut_92, 
    'x_load_manifest__mutmut_93': x_load_manifest__mutmut_93, 
    'x_load_manifest__mutmut_94': x_load_manifest__mutmut_94, 
    'x_load_manifest__mutmut_95': x_load_manifest__mutmut_95, 
    'x_load_manifest__mutmut_96': x_load_manifest__mutmut_96, 
    'x_load_manifest__mutmut_97': x_load_manifest__mutmut_97, 
    'x_load_manifest__mutmut_98': x_load_manifest__mutmut_98, 
    'x_load_manifest__mutmut_99': x_load_manifest__mutmut_99, 
    'x_load_manifest__mutmut_100': x_load_manifest__mutmut_100, 
    'x_load_manifest__mutmut_101': x_load_manifest__mutmut_101, 
    'x_load_manifest__mutmut_102': x_load_manifest__mutmut_102, 
    'x_load_manifest__mutmut_103': x_load_manifest__mutmut_103, 
    'x_load_manifest__mutmut_104': x_load_manifest__mutmut_104, 
    'x_load_manifest__mutmut_105': x_load_manifest__mutmut_105, 
    'x_load_manifest__mutmut_106': x_load_manifest__mutmut_106, 
    'x_load_manifest__mutmut_107': x_load_manifest__mutmut_107, 
    'x_load_manifest__mutmut_108': x_load_manifest__mutmut_108, 
    'x_load_manifest__mutmut_109': x_load_manifest__mutmut_109, 
    'x_load_manifest__mutmut_110': x_load_manifest__mutmut_110, 
    'x_load_manifest__mutmut_111': x_load_manifest__mutmut_111, 
    'x_load_manifest__mutmut_112': x_load_manifest__mutmut_112, 
    'x_load_manifest__mutmut_113': x_load_manifest__mutmut_113, 
    'x_load_manifest__mutmut_114': x_load_manifest__mutmut_114, 
    'x_load_manifest__mutmut_115': x_load_manifest__mutmut_115, 
    'x_load_manifest__mutmut_116': x_load_manifest__mutmut_116, 
    'x_load_manifest__mutmut_117': x_load_manifest__mutmut_117, 
    'x_load_manifest__mutmut_118': x_load_manifest__mutmut_118, 
    'x_load_manifest__mutmut_119': x_load_manifest__mutmut_119, 
    'x_load_manifest__mutmut_120': x_load_manifest__mutmut_120, 
    'x_load_manifest__mutmut_121': x_load_manifest__mutmut_121, 
    'x_load_manifest__mutmut_122': x_load_manifest__mutmut_122, 
    'x_load_manifest__mutmut_123': x_load_manifest__mutmut_123, 
    'x_load_manifest__mutmut_124': x_load_manifest__mutmut_124, 
    'x_load_manifest__mutmut_125': x_load_manifest__mutmut_125, 
    'x_load_manifest__mutmut_126': x_load_manifest__mutmut_126, 
    'x_load_manifest__mutmut_127': x_load_manifest__mutmut_127, 
    'x_load_manifest__mutmut_128': x_load_manifest__mutmut_128, 
    'x_load_manifest__mutmut_129': x_load_manifest__mutmut_129, 
    'x_load_manifest__mutmut_130': x_load_manifest__mutmut_130, 
    'x_load_manifest__mutmut_131': x_load_manifest__mutmut_131, 
    'x_load_manifest__mutmut_132': x_load_manifest__mutmut_132, 
    'x_load_manifest__mutmut_133': x_load_manifest__mutmut_133, 
    'x_load_manifest__mutmut_134': x_load_manifest__mutmut_134, 
    'x_load_manifest__mutmut_135': x_load_manifest__mutmut_135, 
    'x_load_manifest__mutmut_136': x_load_manifest__mutmut_136, 
    'x_load_manifest__mutmut_137': x_load_manifest__mutmut_137, 
    'x_load_manifest__mutmut_138': x_load_manifest__mutmut_138, 
    'x_load_manifest__mutmut_139': x_load_manifest__mutmut_139, 
    'x_load_manifest__mutmut_140': x_load_manifest__mutmut_140, 
    'x_load_manifest__mutmut_141': x_load_manifest__mutmut_141, 
    'x_load_manifest__mutmut_142': x_load_manifest__mutmut_142, 
    'x_load_manifest__mutmut_143': x_load_manifest__mutmut_143, 
    'x_load_manifest__mutmut_144': x_load_manifest__mutmut_144, 
    'x_load_manifest__mutmut_145': x_load_manifest__mutmut_145, 
    'x_load_manifest__mutmut_146': x_load_manifest__mutmut_146, 
    'x_load_manifest__mutmut_147': x_load_manifest__mutmut_147, 
    'x_load_manifest__mutmut_148': x_load_manifest__mutmut_148, 
    'x_load_manifest__mutmut_149': x_load_manifest__mutmut_149, 
    'x_load_manifest__mutmut_150': x_load_manifest__mutmut_150, 
    'x_load_manifest__mutmut_151': x_load_manifest__mutmut_151, 
    'x_load_manifest__mutmut_152': x_load_manifest__mutmut_152, 
    'x_load_manifest__mutmut_153': x_load_manifest__mutmut_153, 
    'x_load_manifest__mutmut_154': x_load_manifest__mutmut_154, 
    'x_load_manifest__mutmut_155': x_load_manifest__mutmut_155, 
    'x_load_manifest__mutmut_156': x_load_manifest__mutmut_156, 
    'x_load_manifest__mutmut_157': x_load_manifest__mutmut_157, 
    'x_load_manifest__mutmut_158': x_load_manifest__mutmut_158, 
    'x_load_manifest__mutmut_159': x_load_manifest__mutmut_159, 
    'x_load_manifest__mutmut_160': x_load_manifest__mutmut_160, 
    'x_load_manifest__mutmut_161': x_load_manifest__mutmut_161, 
    'x_load_manifest__mutmut_162': x_load_manifest__mutmut_162, 
    'x_load_manifest__mutmut_163': x_load_manifest__mutmut_163, 
    'x_load_manifest__mutmut_164': x_load_manifest__mutmut_164, 
    'x_load_manifest__mutmut_165': x_load_manifest__mutmut_165, 
    'x_load_manifest__mutmut_166': x_load_manifest__mutmut_166, 
    'x_load_manifest__mutmut_167': x_load_manifest__mutmut_167, 
    'x_load_manifest__mutmut_168': x_load_manifest__mutmut_168, 
    'x_load_manifest__mutmut_169': x_load_manifest__mutmut_169, 
    'x_load_manifest__mutmut_170': x_load_manifest__mutmut_170, 
    'x_load_manifest__mutmut_171': x_load_manifest__mutmut_171, 
    'x_load_manifest__mutmut_172': x_load_manifest__mutmut_172, 
    'x_load_manifest__mutmut_173': x_load_manifest__mutmut_173, 
    'x_load_manifest__mutmut_174': x_load_manifest__mutmut_174, 
    'x_load_manifest__mutmut_175': x_load_manifest__mutmut_175, 
    'x_load_manifest__mutmut_176': x_load_manifest__mutmut_176, 
    'x_load_manifest__mutmut_177': x_load_manifest__mutmut_177, 
    'x_load_manifest__mutmut_178': x_load_manifest__mutmut_178, 
    'x_load_manifest__mutmut_179': x_load_manifest__mutmut_179, 
    'x_load_manifest__mutmut_180': x_load_manifest__mutmut_180, 
    'x_load_manifest__mutmut_181': x_load_manifest__mutmut_181, 
    'x_load_manifest__mutmut_182': x_load_manifest__mutmut_182, 
    'x_load_manifest__mutmut_183': x_load_manifest__mutmut_183, 
    'x_load_manifest__mutmut_184': x_load_manifest__mutmut_184, 
    'x_load_manifest__mutmut_185': x_load_manifest__mutmut_185, 
    'x_load_manifest__mutmut_186': x_load_manifest__mutmut_186, 
    'x_load_manifest__mutmut_187': x_load_manifest__mutmut_187, 
    'x_load_manifest__mutmut_188': x_load_manifest__mutmut_188, 
    'x_load_manifest__mutmut_189': x_load_manifest__mutmut_189, 
    'x_load_manifest__mutmut_190': x_load_manifest__mutmut_190, 
    'x_load_manifest__mutmut_191': x_load_manifest__mutmut_191, 
    'x_load_manifest__mutmut_192': x_load_manifest__mutmut_192, 
    'x_load_manifest__mutmut_193': x_load_manifest__mutmut_193, 
    'x_load_manifest__mutmut_194': x_load_manifest__mutmut_194, 
    'x_load_manifest__mutmut_195': x_load_manifest__mutmut_195, 
    'x_load_manifest__mutmut_196': x_load_manifest__mutmut_196, 
    'x_load_manifest__mutmut_197': x_load_manifest__mutmut_197, 
    'x_load_manifest__mutmut_198': x_load_manifest__mutmut_198, 
    'x_load_manifest__mutmut_199': x_load_manifest__mutmut_199, 
    'x_load_manifest__mutmut_200': x_load_manifest__mutmut_200, 
    'x_load_manifest__mutmut_201': x_load_manifest__mutmut_201, 
    'x_load_manifest__mutmut_202': x_load_manifest__mutmut_202, 
    'x_load_manifest__mutmut_203': x_load_manifest__mutmut_203, 
    'x_load_manifest__mutmut_204': x_load_manifest__mutmut_204, 
    'x_load_manifest__mutmut_205': x_load_manifest__mutmut_205, 
    'x_load_manifest__mutmut_206': x_load_manifest__mutmut_206, 
    'x_load_manifest__mutmut_207': x_load_manifest__mutmut_207, 
    'x_load_manifest__mutmut_208': x_load_manifest__mutmut_208, 
    'x_load_manifest__mutmut_209': x_load_manifest__mutmut_209, 
    'x_load_manifest__mutmut_210': x_load_manifest__mutmut_210, 
    'x_load_manifest__mutmut_211': x_load_manifest__mutmut_211, 
    'x_load_manifest__mutmut_212': x_load_manifest__mutmut_212, 
    'x_load_manifest__mutmut_213': x_load_manifest__mutmut_213, 
    'x_load_manifest__mutmut_214': x_load_manifest__mutmut_214, 
    'x_load_manifest__mutmut_215': x_load_manifest__mutmut_215, 
    'x_load_manifest__mutmut_216': x_load_manifest__mutmut_216, 
    'x_load_manifest__mutmut_217': x_load_manifest__mutmut_217, 
    'x_load_manifest__mutmut_218': x_load_manifest__mutmut_218, 
    'x_load_manifest__mutmut_219': x_load_manifest__mutmut_219, 
    'x_load_manifest__mutmut_220': x_load_manifest__mutmut_220, 
    'x_load_manifest__mutmut_221': x_load_manifest__mutmut_221, 
    'x_load_manifest__mutmut_222': x_load_manifest__mutmut_222, 
    'x_load_manifest__mutmut_223': x_load_manifest__mutmut_223, 
    'x_load_manifest__mutmut_224': x_load_manifest__mutmut_224, 
    'x_load_manifest__mutmut_225': x_load_manifest__mutmut_225, 
    'x_load_manifest__mutmut_226': x_load_manifest__mutmut_226, 
    'x_load_manifest__mutmut_227': x_load_manifest__mutmut_227, 
    'x_load_manifest__mutmut_228': x_load_manifest__mutmut_228, 
    'x_load_manifest__mutmut_229': x_load_manifest__mutmut_229, 
    'x_load_manifest__mutmut_230': x_load_manifest__mutmut_230, 
    'x_load_manifest__mutmut_231': x_load_manifest__mutmut_231, 
    'x_load_manifest__mutmut_232': x_load_manifest__mutmut_232, 
    'x_load_manifest__mutmut_233': x_load_manifest__mutmut_233
}

def load_manifest(*args, **kwargs):
    result = _mutmut_trampoline(x_load_manifest__mutmut_orig, x_load_manifest__mutmut_mutants, args, kwargs)
    return result 

load_manifest.__signature__ = _mutmut_signature(x_load_manifest__mutmut_orig)
x_load_manifest__mutmut_orig.__name__ = 'x_load_manifest'


def x_dump_manifest_locked__mutmut_orig(m: dict[str, Any], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(m, indent=2), encoding="utf-8")


def x_dump_manifest_locked__mutmut_1(m: dict[str, Any], out: Path) -> None:
    out.parent.mkdir(parents=None, exist_ok=True)
    out.write_text(json.dumps(m, indent=2), encoding="utf-8")


def x_dump_manifest_locked__mutmut_2(m: dict[str, Any], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=None)
    out.write_text(json.dumps(m, indent=2), encoding="utf-8")


def x_dump_manifest_locked__mutmut_3(m: dict[str, Any], out: Path) -> None:
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(m, indent=2), encoding="utf-8")


def x_dump_manifest_locked__mutmut_4(m: dict[str, Any], out: Path) -> None:
    out.parent.mkdir(parents=True, )
    out.write_text(json.dumps(m, indent=2), encoding="utf-8")


def x_dump_manifest_locked__mutmut_5(m: dict[str, Any], out: Path) -> None:
    out.parent.mkdir(parents=False, exist_ok=True)
    out.write_text(json.dumps(m, indent=2), encoding="utf-8")


def x_dump_manifest_locked__mutmut_6(m: dict[str, Any], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=False)
    out.write_text(json.dumps(m, indent=2), encoding="utf-8")


def x_dump_manifest_locked__mutmut_7(m: dict[str, Any], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(None, encoding="utf-8")


def x_dump_manifest_locked__mutmut_8(m: dict[str, Any], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(m, indent=2), encoding=None)


def x_dump_manifest_locked__mutmut_9(m: dict[str, Any], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(encoding="utf-8")


def x_dump_manifest_locked__mutmut_10(m: dict[str, Any], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(m, indent=2), )


def x_dump_manifest_locked__mutmut_11(m: dict[str, Any], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(None, indent=2), encoding="utf-8")


def x_dump_manifest_locked__mutmut_12(m: dict[str, Any], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(m, indent=None), encoding="utf-8")


def x_dump_manifest_locked__mutmut_13(m: dict[str, Any], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(indent=2), encoding="utf-8")


def x_dump_manifest_locked__mutmut_14(m: dict[str, Any], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(m, ), encoding="utf-8")


def x_dump_manifest_locked__mutmut_15(m: dict[str, Any], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(m, indent=3), encoding="utf-8")


def x_dump_manifest_locked__mutmut_16(m: dict[str, Any], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(m, indent=2), encoding="XXutf-8XX")


def x_dump_manifest_locked__mutmut_17(m: dict[str, Any], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(m, indent=2), encoding="UTF-8")

x_dump_manifest_locked__mutmut_mutants : ClassVar[MutantDict] = {
'x_dump_manifest_locked__mutmut_1': x_dump_manifest_locked__mutmut_1, 
    'x_dump_manifest_locked__mutmut_2': x_dump_manifest_locked__mutmut_2, 
    'x_dump_manifest_locked__mutmut_3': x_dump_manifest_locked__mutmut_3, 
    'x_dump_manifest_locked__mutmut_4': x_dump_manifest_locked__mutmut_4, 
    'x_dump_manifest_locked__mutmut_5': x_dump_manifest_locked__mutmut_5, 
    'x_dump_manifest_locked__mutmut_6': x_dump_manifest_locked__mutmut_6, 
    'x_dump_manifest_locked__mutmut_7': x_dump_manifest_locked__mutmut_7, 
    'x_dump_manifest_locked__mutmut_8': x_dump_manifest_locked__mutmut_8, 
    'x_dump_manifest_locked__mutmut_9': x_dump_manifest_locked__mutmut_9, 
    'x_dump_manifest_locked__mutmut_10': x_dump_manifest_locked__mutmut_10, 
    'x_dump_manifest_locked__mutmut_11': x_dump_manifest_locked__mutmut_11, 
    'x_dump_manifest_locked__mutmut_12': x_dump_manifest_locked__mutmut_12, 
    'x_dump_manifest_locked__mutmut_13': x_dump_manifest_locked__mutmut_13, 
    'x_dump_manifest_locked__mutmut_14': x_dump_manifest_locked__mutmut_14, 
    'x_dump_manifest_locked__mutmut_15': x_dump_manifest_locked__mutmut_15, 
    'x_dump_manifest_locked__mutmut_16': x_dump_manifest_locked__mutmut_16, 
    'x_dump_manifest_locked__mutmut_17': x_dump_manifest_locked__mutmut_17
}

def dump_manifest_locked(*args, **kwargs):
    result = _mutmut_trampoline(x_dump_manifest_locked__mutmut_orig, x_dump_manifest_locked__mutmut_mutants, args, kwargs)
    return result 

dump_manifest_locked.__signature__ = _mutmut_signature(x_dump_manifest_locked__mutmut_orig)
x_dump_manifest_locked__mutmut_orig.__name__ = 'x_dump_manifest_locked'
