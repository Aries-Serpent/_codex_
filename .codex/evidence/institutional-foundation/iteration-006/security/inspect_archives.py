"""Bounded, offline inspection; never extracts or executes archive members."""

import collections
import gzip
import hashlib
import importlib.metadata
import json
import pathlib
import stat
import sys
import tarfile
import time
import zipfile
from typing import Any, BinaryIO, cast

from detect_secrets.core import scan
from detect_secrets.settings import default_settings

ROOT = pathlib.Path.cwd().resolve()
SOURCE = ROOT / ".codex/evidence/institutional-foundation/iteration-005"
OUTPUT = ROOT / ".codex/evidence/institutional-foundation/iteration-006/security"
MEMBER_LIMIT = 16 * 1024 * 1024
ARCHIVE_LIMIT = 64 * 1024 * 1024
TOTAL_LIMIT = 256 * 1024 * 1024
COUNT_LIMIT = 10000
COMMAND = (
    "PYTHONDONTWRITEBYTECODE=1 .venv_ci/bin/python -B "
    ".codex/evidence/institutional-foundation/iteration-006/security/inspect_archives.py"
)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save(name, value):
    (OUTPUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def safe_name(name):
    parts = pathlib.PurePosixPath(name).parts
    return (
        not name.startswith(("/", "\\"))
        and "\\" not in name
        and ".." not in parts
        and not (parts and ":" in parts[0])
        and not any(parts[i : i + 2] == (".github", "agents") for i in range(len(parts) - 1))
    )


def offline_guard(event, args):
    if event.startswith(("socket.", "subprocess.")) or event in (
        "os.system",
        "os.exec",
        "os.posix_spawn",
    ):
        raise PermissionError("Network and child execution disabled")


sys.addaudithook(offline_guard)
started = time.time()
receipt = json.loads((SOURCE / "final-secret-scan.json").read_text())
reused, absent, changed = [], [], []
old = receipt["coverage"]["post_scan_file_manifest"]
for name, expected in old.items():
    path = ROOT / name
    if not path.is_relative_to(SOURCE) or not safe_name(name):
        raise ValueError("Unsafe historical path")
    if not path.is_file():
        absent.append(str(path))
        continue
    data = path.read_bytes()
    item = {"path": str(path), "bytes": len(data), "sha256": sha(data)}
    if item["bytes"] == expected["bytes"] and item["sha256"] == expected["sha256"]:
        reused.append(item)
    else:
        changed.append(item)
current = sorted(p for p in SOURCE.rglob("*") if p.is_file())
reused_names = {x["path"] for x in reused}
root_text = [
    {"path": str(p), "bytes": p.stat().st_size, "sha256": sha(p.read_bytes())}
    for p in current
    if p.parent == SOURCE and str(p) not in reused_names and p.suffix != ".gz"
]
save(
    "current-scope.json",
    {
        "prior_receipt": str(SOURCE / "final-secret-scan.json"),
        "prior_receipt_sha256": sha((SOURCE / "final-secret-scan.json").read_bytes()),
        "reused_exact_hash": reused,
        "missing_previously_scanned": absent,
        "changed_previously_scanned": changed,
        "root_text_requires_runtime_scan": root_text,
        "reuse_limit": "Prior generic tool responses, not independently established member traversal.",
    },
)
archives = [p for p in current if p.suffix in (".whl", ".tar", ".gz")]
members: list[dict[str, Any]] = []
archive_results: list[dict[str, Any]] = []
unique: dict[str, dict[str, Any]] = {}
findings: list[dict[str, str]] = []
aggregate = 0
settings_metadata = None
with default_settings() as settings:
    settings_metadata = settings.json()

    def inspect_member(archive, name, data):
        digest = sha(data)
        item = {
            "archive": str(archive),
            "member": name,
            "bytes": len(data),
            "sha256": digest,
        }
        if digest in unique:
            item["status"] = "DEDUPLICATED"
            item["content_status"] = unique[digest]["status"]
            members.append(item)
            return
        if b"\x00" in data:
            item["status"] = "UNSUPPORTED_BINARY_NUL"
        else:
            try:
                text = data.decode("utf-8", errors="strict")
            except UnicodeDecodeError:
                item["status"] = "UNSUPPORTED_NON_UTF8"
            else:
                item["status"] = "SCANNED_UTF8"
                lines = list(enumerate(text.splitlines(keepends=True), start=1))
                hits = list(
                    scan._process_line_based_plugins(lines=lines, filename="bounded-member.txt")
                )
                if hits:
                    item["status"] = "SUSPECTED_FINDINGS_DISCLOSURE_HALTED"
                for hit in hits:
                    identity = (
                        digest
                        + ":"
                        + str(hit.line_number)
                        + ":"
                        + hit.type
                        + ":"
                        + sha(hit.secret_value.encode())
                    )
                    findings.append(
                        {
                            "finding_id": sha(identity.encode()),
                            "path": str(archive) + "!/" + name,
                        }
                    )
        unique[digest] = item
        members.append(item)

    for archive in archives:
        result = {
            "path": str(archive),
            "bytes": archive.stat().st_size,
            "sha256": sha(archive.read_bytes()),
            "expanded_bytes": 0,
            "member_count": 0,
            "status": "INSPECTED",
        }
        archive_results.append(result)
        seen: set[str] = set()

        def accept(name, size, reader):
            global aggregate
            if not safe_name(name) or name in seen:
                raise ValueError("Unsafe or duplicate member path")
            seen.add(name)
            if (
                size > MEMBER_LIMIT
                or result["expanded_bytes"] + size > ARCHIVE_LIMIT
                or aggregate + size > TOTAL_LIMIT
            ):
                raise ValueError("Expanded-byte budget exceeded")
            data = reader(MEMBER_LIMIT + 1)
            if len(data) != size or len(data) > MEMBER_LIMIT:
                raise ValueError("Member size mismatch or budget exceeded")
            result["expanded_bytes"] += len(data)
            aggregate += len(data)
            inspect_member(archive, name, data)

        try:
            if archive.suffix == ".whl":
                with zipfile.ZipFile(archive) as z:
                    infos = z.infolist()
                    if len(infos) > COUNT_LIMIT:
                        raise ValueError("Member count exceeded")
                    for info in infos:
                        result["member_count"] += 1
                        mode = info.external_attr >> 16
                        kind = stat.S_IFMT(mode)
                        if (
                            not safe_name(info.filename)
                            or kind not in (0, stat.S_IFREG, stat.S_IFDIR)
                            or info.flag_bits & 1
                        ):
                            raise ValueError("Unsafe or encrypted ZIP member")
                        if info.is_dir():
                            continue
                        with z.open(info) as zip_stream:
                            accept(info.filename, info.file_size, zip_stream.read)
            elif archive.suffix == ".tar":
                with tarfile.open(archive, "r:") as t:
                    for tar_info in t:
                        result["member_count"] += 1
                        if (
                            result["member_count"] > COUNT_LIMIT
                            or not safe_name(tar_info.name)
                            or not (tar_info.isdir() or tar_info.isfile())
                        ):
                            raise ValueError("Unsafe TAR member or count")
                        if tar_info.isdir():
                            continue
                        with cast(BinaryIO, t.extractfile(tar_info)) as tar_stream:
                            accept(tar_info.name, tar_info.size, tar_stream.read)
            else:
                with gzip.open(archive, "rb") as gzip_stream:
                    data = gzip_stream.read(MEMBER_LIMIT + 1)
                result["member_count"] = 1
                accept(archive.stem, len(data), lambda limit: data[:limit])
        except Exception as exc:
            result["status"] = "INCOMPLETE"
            result["error_type"] = type(exc).__name__
            # Exception messages may contain attacker-controlled archive values.

save("archive-member-manifest.json", members)
save("findings-redacted.json", findings)
save(
    "scan-result.json",
    {
        "command": COMMAND,
        "python": sys.version.split()[0],
        "detect_secrets_version": importlib.metadata.version("detect-secrets"),
        "settings": settings_metadata,
        "limits": {
            "per_file_bytes": MEMBER_LIMIT,
            "per_archive_expanded_bytes": ARCHIVE_LIMIT,
            "aggregate_expanded_bytes": TOTAL_LIMIT,
            "per_archive_member_count": COUNT_LIMIT,
        },
        "offline": "Audit guard rejects sockets and child execution; default local detectors/filters.",
        "archive_results": archive_results,
        "expanded_bytes_total": aggregate,
        "member_occurrences": len(members),
        "unique_content_count": len(unique),
        "unique_content_status_counts": dict(
            collections.Counter(x["status"] for x in unique.values())
        ),
        "finding_count": len(findings),
        "findings_policy": "Only hashed finding IDs and paths retained; affected content disclosure halted. Findings are untriaged, not confirmed credentials.",
        "unsupported_formats": "Binary NUL-containing or non-UTF8 member contents are not declared clean. Nested archives are not recursively decompressed. No arbitrary format handlers.",
        "scope_limit": "Current retained iteration-005 contents only; missing historical logs unavailable; no authenticated independence or acceptance.",
        "runtime_root_text_scan": "Separate approved runtime tool receipt required.",
        "elapsed_seconds": round(time.time() - started, 3),
    },
)
print(
    json.dumps(
        {
            "archives": len(archives),
            "expanded_bytes": aggregate,
            "unique_contents": len(unique),
            "findings": len(findings),
            "incomplete_archives": sum(x["status"] != "INSPECTED" for x in archive_results),
            "output": str(OUTPUT),
        }
    )
)
