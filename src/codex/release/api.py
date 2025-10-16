from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import shutil
import tarfile
from pathlib import Path

from codex.archive.api import restore
from codex.archive.dal import ArchiveDAL
from codex.evidence.core import evidence_append
from codex.release.manifest import dump_manifest_locked, load_manifest


def _set_mode(path: Path, mode_str: str) -> None:
    mode = int(mode_str, 8)
    os.chmod(path, (path.stat().st_mode & ~0o777) | mode)


def _templated_bytes(data: bytes, vars: dict) -> bytes:
    if not vars:
        return data
    try:
        s = data.decode("utf-8", "ignore")
    except Exception:
        return data
    for k, v in vars.items():
        s = s.replace("{{" + str(k) + "}}", str(v))
    return s.encode("utf-8")


def _tar_add_bytes(tar: tarfile.TarFile, arcname: str, b: bytes, mode: int = 0o644) -> None:
    ti = tarfile.TarInfo(arcname)
    ti.size = len(b)
    ti.mtime = 0
    ti.uid = ti.gid = 0
    ti.uname = ti.gname = ""
    ti.mode = mode
    tar.addfile(ti, io.BytesIO(b))


def _tar_add_symlink(tar: tarfile.TarFile, linkname: str, target: str) -> None:
    ti = tarfile.TarInfo(linkname)
    ti.mtime = 0
    ti.uid = ti.gid = 0
    ti.uname = ti.gname = ""
    ti.type = tarfile.SYMTYPE
    ti.linkname = target
    ti.mode = 0o777
    tar.addfile(ti)


def _is_safe_member(member: tarfile.TarInfo) -> bool:
    name = Path(member.name)
    return not name.is_absolute() and ".." not in name.parts


def _ensure_within(base: Path, candidate: Path, what: str) -> None:
    candidate_abs = candidate.resolve(strict=False)
    try:
        candidate_abs.relative_to(base)
    except ValueError as exc:  # pragma: no cover - defensive guard
        raise ValueError(f"{what} escapes destination: {candidate}") from exc


def _safe_extract(tar: tarfile.TarFile, dest: Path) -> None:
    base = dest.resolve()
    for member in tar.getmembers():
        if not _is_safe_member(member):
            raise ValueError(f"unsafe path in archive: {member.name}")
        if member.ischr() or member.isblk() or member.isfifo():
            raise ValueError(f"unsupported special file in archive: {member.name}")
        target = dest / member.name
        _ensure_within(base, target, "member path")
        if member.issym():
            link_target = Path(member.linkname)
            if link_target.is_absolute():
                raise ValueError(f"absolute symlink target not allowed: {member.linkname}")
            _ensure_within(
                base,
                target.parent / link_target,
                f"symlink target for {member.name}",
            )
        elif member.islnk():
            _ensure_within(
                base,
                dest / member.linkname,
                f"hardlink target for {member.name}",
            )
        target.parent.mkdir(parents=True, exist_ok=True)
        tar.extract(member, dest.as_posix())


def _evidence_append_release(action: str, payload: dict) -> None:
    actor = os.getenv("CODEX_ACTOR", "codex")
    evidence_append(action=action, actor=actor, tool="release", repo="_codex_", context=payload)


def _clean_path(path: Path) -> None:
    """Remove ``path`` regardless of whether it is a file, directory, or symlink."""

    if path.is_symlink():
        path.unlink()
        return

    if not path.exists():
        return

    if path.is_file():
        path.unlink()
        return

    if path.is_dir():

        def _onerror(func, p, exc_info):  # pragma: no cover - defensive cleanup
            with contextlib.suppress(OSError):
                os.chmod(p, 0o700)
            func(p)

        shutil.rmtree(path, onerror=_onerror)
        return

    path.unlink()


def pack_release(manifest_path: Path, staging_dir: Path, bundle_path: Path) -> tuple[Path, dict]:
    """
    Build a deterministic tar.gz bundle from a manifest referencing archive tombstones.
    Returns (bundle_path, locked_manifest_dict).
    """

    m = load_manifest(manifest_path)
    _clean_path(staging_dir)
    staging_dir.mkdir(parents=True, exist_ok=True)
    # hydrate components
    for c in m.components:
        obj = restore(c.tombstone)
        outp = staging_dir / c.dest_path
        outp.parent.mkdir(parents=True, exist_ok=True)
        data = _templated_bytes(obj["bytes"], c.template_vars or {})
        outp.write_bytes(data)
        _set_mode(outp, c.mode)
    # symlinks
    for s in m.symlinks:
        p = staging_dir / s.link_path
        p.parent.mkdir(parents=True, exist_ok=True)
        if p.exists() or p.is_symlink():
            with contextlib.suppress(OSError):
                p.unlink()
        os.symlink(s.target, p)
    # lock manifest with sha256 of canonical JSON
    manifest_dict = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_for_hash = json.loads(json.dumps(manifest_dict))
    checks = manifest_for_hash.get("checks", {})
    if isinstance(checks, dict) and "sha256_manifest" in checks:
        checks = dict(checks)
        checks.pop("sha256_manifest", None)
        if checks:
            manifest_for_hash["checks"] = checks
        else:
            manifest_for_hash.pop("checks", None)
    manifest_bytes = json.dumps(manifest_for_hash, sort_keys=True, separators=(",", ":")).encode()
    sha = hashlib.sha256(manifest_bytes).hexdigest()
    manifest_dict.setdefault("checks", {})["sha256_manifest"] = sha
    dump_manifest_locked(manifest_dict, Path("dist/release.manifest.lock.json"))
    # build deterministic tar.gz
    bundle_path.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(
        bundle_path.as_posix(), "w:gz", compresslevel=9, format=tarfile.GNU_FORMAT
    ) as tar:
        # embed staged files
        for f in sorted(staging_dir.rglob("*")):
            if f == staging_dir:
                continue
            arc = f.relative_to(staging_dir).as_posix()
            if f.is_symlink():
                _tar_add_symlink(tar, arc, os.readlink(f))
            elif f.is_file():
                b = f.read_bytes()
                mode = f.stat().st_mode & 0o777
                _tar_add_bytes(tar, arc, b, mode)
        # embed locked manifest as well
        locked = Path("dist/release.manifest.lock.json")
        _tar_add_bytes(tar, "release.manifest.lock.json", locked.read_bytes(), 0o644)
    _evidence_append_release(
        "PACK",
        {"release_id": m.release_id, "version": m.version, "bundle": bundle_path.as_posix()},
    )
    try:
        dal = ArchiveDAL.from_env()
        meta = dal.create_release_meta(
            release_id=m.release_id,
            version=m.version,
            created_at=m.created_at,
            actor=m.actor,
            metadata={
                "target": m.target,
                "checks": manifest_dict.get("checks", {}),
            },
        )
        release_meta_id = meta.get("id", "")
        for component in m.components:
            item_id: str | None
            try:
                item_row, _ = dal.fetch_by_tombstone(component.tombstone)
                item_id = item_row.id
            except Exception:
                item_id = None
            dal.add_release_component(
                release_meta_id=release_meta_id,
                item_id=item_id,
                tombstone=component.tombstone,
                dest_path=component.dest_path,
                mode=component.mode,
                template_vars=component.template_vars or {},
            )
        _evidence_append_release(
            "RELEASE_PERSIST", {"release_id": m.release_id, "meta_id": release_meta_id}
        )
    except Exception as exc:  # pragma: no cover - best effort logging
        _evidence_append_release(
            "RELEASE_PERSIST_FAIL",
            {"release_id": m.release_id, "error": str(exc)},
        )
    return bundle_path, manifest_dict


def verify_bundle(bundle_path: Path) -> dict:
    import json
    import tarfile

    with tarfile.open(bundle_path.as_posix(), "r:gz") as tar:
        extracted = tar.extractfile("release.manifest.lock.json")
        if extracted is None:
            raise FileNotFoundError("release.manifest.lock.json missing from bundle")
        manifest_bytes = extracted.read()
        locked_manifest = json.loads(manifest_bytes)
        stored = locked_manifest.get("checks", {}).get("sha256_manifest")
        manifest_for_hash = json.loads(json.dumps(locked_manifest))
        checks = manifest_for_hash.get("checks", {})
        if isinstance(checks, dict):
            checks = dict(checks)
            checks.pop("sha256_manifest", None)
            if checks:
                manifest_for_hash["checks"] = checks
            else:
                manifest_for_hash.pop("checks", None)
        canonical_bytes = json.dumps(
            manifest_for_hash, sort_keys=True, separators=(",", ":")
        ).encode()
        recomputed = hashlib.sha256(canonical_bytes).hexdigest()
        ok = stored == recomputed
    _evidence_append_release("VERIFY", {"bundle": bundle_path.as_posix(), "ok": ok})
    if not ok:
        raise RuntimeError("manifest sha mismatch")
    return {"ok": ok, "sha256_manifest": stored}


def unpack_bundle(bundle_path: Path, dest_dir: Path, allow_scripts: bool = False) -> Path:
    import tarfile

    dest_dir.mkdir(parents=True, exist_ok=True)
    with tarfile.open(bundle_path.as_posix(), "r:gz") as tar:
        _safe_extract(tar, dest_dir)
        # Do not execute any scripts by default; a future flag can explicitly allow it.
        if not allow_scripts:
            # noop
            pass
    _evidence_append_release(
        "UNPACK", {"bundle": bundle_path.as_posix(), "dest": dest_dir.as_posix()}
    )
    return dest_dir
