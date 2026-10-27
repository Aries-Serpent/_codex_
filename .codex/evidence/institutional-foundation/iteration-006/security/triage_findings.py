"""Reidentify only previously reported findings; retain no matched values."""

import ast
import collections
import gzip
import hashlib
import json
import pathlib
import re
import sys
import zipfile

from detect_secrets.core import scan
from detect_secrets.settings import default_settings

ROOT = pathlib.Path.cwd().resolve()
OUT = ROOT / ".codex/evidence/institutional-foundation/iteration-006/security"
SOURCE = ROOT / ".codex/evidence/institutional-foundation/iteration-005"
LIMIT = 16 * 1024 * 1024


def deny_network(event, args):
    if event.startswith(("socket.", "subprocess.")) or event in (
        "os.system",
        "os.exec",
        "os.posix_spawn",
    ):
        raise PermissionError("Offline inspection only")


sys.addaudithook(deny_network)


def digest(value):
    return hashlib.sha256(value).hexdigest()


def safe(name):
    parts = pathlib.PurePosixPath(name).parts
    return (
        not name.startswith(("/", "\\"))
        and "\\" not in name
        and ".." not in parts
        and not any(parts[i : i + 2] == (".github", "agents") for i in range(len(parts) - 1))
    )


def classify(text, name, hit):
    value = hit.secret_value
    line = text.splitlines()[hit.line_number - 1]
    if name.endswith("Cargo.lock") and re.fullmatch(r'\s*checksum\s*=\s*"[0-9a-f]{64}"\s*', line):
        return "LOCKFILE_CHECKSUM_NOT_CREDENTIAL"
    if re.fullmatch(r"[0-9a-fA-F]{32,128}", value):
        if re.search(
            r"(?i)(sha256|sha1|checksum|digest|integrity|candidate_ref|"
            r"source_sha|git_blob|source_tree|commit|fingerprint|hash)",
            line,
        ):
            return "HASH_OR_SOURCE_IDENTIFIER_CONTEXT"
    if name.endswith(".py"):
        try:
            tree = ast.parse(text)
        except SyntaxError:
            tree = None
        if tree is not None:
            constants = [
                node
                for node in ast.walk(tree)
                if isinstance(node, ast.Constant)
                and isinstance(node.value, str)
                and node.lineno <= hit.line_number <= node.end_lineno
            ]
            if any(
                value in node.value
                and any(
                    marker in node.value
                    for marker in (r"\s", r"\b", r"\w", "[A-Z", "[a-z", "(?:", "(?i)")
                )
                for node in constants
            ):
                return "REGEX_PATTERN_LITERAL"
    if re.search(
        r"(?i)(your[-_ ]|example|placeholder|dummy|changeme|change[-_]me|"
        r"replace[-_]|test[-_]|sample|<[^>]+>)",
        value,
    ):
        return "EXPLICIT_PLACEHOLDER_OR_EXAMPLE"
    if "/tests/" in name or name.startswith("tests/"):
        return "TEST_CONTEXT_UNVERIFIED"
    return "UNRESOLVED_CREDENTIAL_LIKE_REQUIRES_OWNER_TRIAGE"


original = json.loads((OUT / "findings-redacted.json").read_text())
manifest = json.loads((OUT / "archive-member-manifest.json").read_text())
provenance = {item["archive"] + "!/" + item["member"]: item for item in manifest}
expected = {item["finding_id"] for item in original}
rows = []
bytes_read = 0
with default_settings():
    for path in sorted({item["path"] for item in original}):
        archive_name, member = path.split("!/", 1)
        archive = pathlib.Path(archive_name)
        assert archive.is_relative_to(SOURCE) and safe(member)
        if archive.suffix == ".gz":
            with gzip.open(archive, "rb") as gzip_stream:
                data = gzip_stream.read(LIMIT + 1)
        else:
            with zipfile.ZipFile(archive) as container:
                info = container.getinfo(member)
                assert info.file_size <= LIMIT
                with container.open(info) as zip_stream:
                    data = zip_stream.read(LIMIT + 1)
        assert len(data) <= LIMIT
        bytes_read += len(data)
        assert bytes_read <= 64 * 1024 * 1024
        content_digest = digest(data)
        assert content_digest == provenance[path]["sha256"]
        text = data.decode("utf-8", errors="strict")
        hits = scan._process_line_based_plugins(
            lines=list(enumerate(text.splitlines(keepends=True), start=1)),
            filename="bounded-member.txt",
        )
        for hit in hits:
            identity = (
                content_digest
                + ":"
                + str(hit.line_number)
                + ":"
                + hit.type
                + ":"
                + digest(hit.secret_value.encode())
            )
            finding_id = digest(identity.encode())
            assert finding_id in expected
            rows.append(
                {
                    "finding_id": finding_id,
                    "path": path,
                    "plugin": hit.type,
                    "classification": classify(text, member, hit),
                }
            )
assert {item["finding_id"] for item in rows} == expected
(OUT / "triage-redacted.json").write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n")
summary = {
    "status": "BOUNDED_TRIAGE_NOT_A_CLEAN_SCAN",
    "existing_findings_reidentified": len(rows),
    "existing_unique_contents_revisited": len({item["path"] for item in rows}),
    "bytes_revisited": bytes_read,
    "classification_counts": dict(collections.Counter(item["classification"] for item in rows)),
    "plugin_counts": dict(collections.Counter(item["plugin"] for item in rows)),
    "limits": "Only 12 existing finding contents revisited. No external verification, raw extraction, repository-wide scan or matched-value disclosure.",
    "classification_limit": "Context classification is local and bounded, not proof of credential validity or universal absence. Unresolved findings require owner triage; affected content must not be published.",
    "command": "PYTHONDONTWRITEBYTECODE=1 .venv_ci/bin/python -B .codex/evidence/institutional-foundation/iteration-006/security/triage_findings.py",
}
(OUT / "triage-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
print(json.dumps(summary))
