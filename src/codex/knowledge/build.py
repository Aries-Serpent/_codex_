from __future__ import annotations

import hashlib
import json
from pathlib import Path

from codex.archive.api import store
from codex.archive.util import json_dumps_sorted, utcnow_iso
from codex.knowledge.chunk import approx_tokens, chunk_by_headings
from codex.knowledge.normalize import normalize_file
from codex.knowledge.pii import scrub
from codex.knowledge.schema import validate_kb

DOMAINS = ("zendesk", "d365", "relocation", "sla", "ops")
INTENTS = ("admin", "consultant", "runtime", "devops")


def infer_domain(path: str) -> str:
    p = path.lower()
    for d in DOMAINS:
        if d in p:
            return d
    return "ops"


def infer_intent(path: str) -> str:
    p = path.lower()
    if "admin" in p or "runbook" in p:
        return "admin"
    if "consultant" in p:
        return "consultant"
    if "runtime" in p:
        return "runtime"
    return "admin"


def iter_source_files(root: Path) -> list[Path]:
    excluded = {".git", ".venv", "artifacts", ".codex", "__pycache__"}
    out: list[Path] = []
    for candidate in root.rglob("*"):
        if candidate.is_dir():
            if candidate.name in excluded:
                continue
            continue
        if candidate.suffix.lower() in {".md", ".txt", ".html", ".htm", ".pdf"}:
            out.append(candidate)
    return out


def build_kb(
    root: Path,
    out_ndjson: Path,
    *,
    allow_gpl: bool = False,
    max_tokens_per_rec: int = 2048,
) -> dict[str, str | int]:
    out_ndjson.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with out_ndjson.open("w", encoding="utf-8") as fh:
        for src in iter_source_files(root):
            normalized, mime = normalize_file(src)
            scrubbed, flags = scrub(normalized, allow_gpl=allow_gpl)
            chunks = chunk_by_headings(
                scrubbed,
                target_tokens=min(1024, max_tokens_per_rec),
            )
            for ch in chunks:
                rid = ch["chunk_id"]
                text = ch["text"]
                if approx_tokens(text) > max_tokens_per_rec:
                    # extra guard
                    continue
                rec: dict[str, object] = {
                    "id": rid,
                    "text": text,
                    "meta": {
                        "source_path": src.as_posix(),
                        "domain": infer_domain(src.as_posix()),
                        "intent": infer_intent(src.as_posix()),
                        "lang": "en",
                        "flags": flags,
                        "title": ch.get("title", ""),
                        "chunk_idx": ch.get("chunk_idx", 0),
                        "mime": mime,
                    },
                }
                validate_kb(rec)
                fh.write(json_dumps_sorted(rec) + "\n")
                n += 1
    return {"written": n, "out": out_ndjson.as_posix()}


def archive_and_manifest(
    kb_path: Path,
    instructions_path: Path | None,
    eval_path: Path | None,
    *,
    actor: str = "codex",
) -> dict[str, object]:
    """Archive dataset files and emit a minimal release manifest JSON."""

    components: list[dict[str, object]] = []

    def _store_one(path: Path, dest: str, mode: str = "0644") -> dict[str, object]:
        payload = path.read_bytes()
        sha = hashlib.sha256(payload).hexdigest()
        stored = store(
            repo="_codex_",
            path=dest,
            by=actor,
            reason="dataset",
            commit_sha="HEAD",
            bytes_in=payload,
            mime="application/x-ndjson",
            lang="text",
        )
        components.append(
            {
                "tombstone": stored["tombstone"],
                "dest_path": dest,
                "mode": mode,
                "type": "file",
                "sha256": sha,
            }
        )
        return stored

    _store_one(kb_path, f"knowledge/{kb_path.name}")
    if instructions_path and instructions_path.exists():
        _store_one(instructions_path, f"knowledge/{instructions_path.name}")
    if eval_path and eval_path.exists():
        _store_one(eval_path, f"knowledge/{eval_path.name}")

    release_id = "codex-knowledge-" + utcnow_iso().replace(":", "").replace("-", "")[:15]
    manifest = {
        "release_id": release_id,
        "version": "v" + utcnow_iso()[:10],
        "created_at": utcnow_iso(),
        "actor": actor,
        "target": {"corpus": "knowledge"},
        "components": components,
        "symlinks": [],
        "post_unpack_commands": [],
        "checks": {"sha256_manifest": "<filled at pack time>"},
    }
    out_path = Path("artifacts/knowledge.release.manifest.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return {"manifest": out_path.as_posix(), "components": len(components)}
