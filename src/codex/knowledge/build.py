from __future__ import annotations

import hashlib
import json
from pathlib import Path

from codex.archive.api import store
from codex.archive.util import json_dumps_sorted, utcnow_iso
from codex.knowledge.chunk import approx_tokens, chunk_by_headings
from codex.knowledge.dedup import dedup_records
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


def iter_sources(root: Path):
    exclude = {".git", ".venv", ".codex", "artifacts", "dist", "__pycache__"}
    for p in root.rglob("*"):
        if p.is_dir():
            if p.name in exclude:
                continue
            continue
        if p.suffix.lower() in (".md", ".txt", ".html", ".htm", ".pdf"):
            yield p


def build_kb(
    root: Path,
    out_ndjson: Path,
    *,
    allow_gpl: bool = False,
    max_tokens_per_rec: int = 2048,
    dedup: bool = True,
) -> dict:
    staged: list[dict[str, object]] = []
    for src in iter_sources(root):
        norm, mime = normalize_file(src)
        scrubbed, flags = scrub(norm, allow_gpl=allow_gpl)
        chunks = chunk_by_headings(scrubbed, target_tokens=min(1024, max_tokens_per_rec))
        for ch in chunks:
            text = ch["text"]
            if approx_tokens(text) > max_tokens_per_rec:
                continue
            rec = {
                "id": ch["chunk_id"],
                "text": text,
                "meta": {
                    "source_path": src.as_posix(),
                    "domain": infer_domain(src.as_posix()),
                    "intent": infer_intent(src.as_posix()),
                    "lang": "en",
                    "title": ch.get("title", ""),
                    "chunk_idx": ch.get("chunk_idx", 0),
                    "mime": mime,
                    "flags": flags,
                },
            }
            validate_kb(rec)
            staged.append(rec)

    total_records = len(staged)
    if dedup and staged:
        keep = set(dedup_records((str(rec["text"]) for rec in staged), threshold=3))
        staged = [rec for idx, rec in enumerate(staged) if idx in keep]

    out_ndjson.parent.mkdir(parents=True, exist_ok=True)
    with out_ndjson.open("w", encoding="utf-8") as fh:
        for rec in staged:
            fh.write(json_dumps_sorted(rec) + "\n")

    written = len(staged)
    return {
        "written": written,
        "out": out_ndjson.as_posix(),
        "deduped": bool(dedup),
        "source_records": total_records,
    }


def archive_and_manifest(
    kb_path: Path,
    instructions_path: Path | None,
    eval_path: Path | None,
    *,
    actor: str = "codex",
) -> dict:
    comps = []

    def _store(p: Path, dest: str) -> None:
        out = store(
            repo="_codex_",
            path=dest,
            by=actor,
            reason="dataset",
            commit_sha="HEAD",
            bytes_in=p.read_bytes(),
            mime="application/x-ndjson",
            lang="text",
        )
        comps.append(
            {
                "tombstone": out["tombstone"],
                "dest_path": dest,
                "mode": "0644",
                "type": "file",
            }
        )

    _store(kb_path, f"knowledge/{kb_path.name}")
    if instructions_path and instructions_path.exists():
        _store(instructions_path, f"knowledge/{instructions_path.name}")
    if eval_path and eval_path.exists():
        _store(eval_path, f"knowledge/{eval_path.name}")
    manifest = {
        "release_id": "codex-knowledge-" + hashlib.sha256(kb_path.read_bytes()).hexdigest()[:12],
        "version": "v" + utcnow_iso()[:10],
        "created_at": utcnow_iso(),
        "actor": actor,
        "target": {"corpus": "knowledge"},
        "components": comps,
        "symlinks": [],
        "post_unpack_commands": [],
        "checks": {"sha256_manifest": "<filled at pack time>"},
    }
    outp = Path("artifacts/knowledge.release.manifest.json")
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return {"manifest": outp.as_posix(), "components": len(comps)}
