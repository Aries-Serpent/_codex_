"""
Cli Knowledge Module

This module provides functionality for cli knowledge.

Usage:
    from codex.cli_knowledge import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import typer

from codex.archive.util import compression_codec, json_dumps_sorted, sha256_file, zstd_compress
from codex.knowledge.build import archive_and_manifest, build_kb
from codex.knowledge.chunk import approx_tokens, chunk_by_headings
from codex.release.api import pack_release, verify_bundle

DEFAULT_ROOT = Path("docs")
DEFAULT_KB_OUT = Path("artifacts/kb.ndjsonl")
DEFAULT_MANIFEST = Path("artifacts/knowledge.release.manifest.json")
DEFAULT_STAGING = Path("work/knowledge_staging")
DEFAULT_BUNDLE = Path("dist/codex-knowledge.tar.gz")
DEFAULT_MERMAID = Path("docs/diagrams/runtime_logic_map.mmd")
DEFAULT_MAPPING_DOC = Path("docs/system/mermaid_logic_map.md")
DEFAULT_SYNC_OUT = Path("artifacts/knowledge/mermaid_sync")

ROOT_OPTION = typer.Option(DEFAULT_ROOT, "--root")
OUT_OPTION = typer.Option(DEFAULT_KB_OUT, "--out")
ALLOW_GPL_OPTION = typer.Option(False, "--allow-gpl/--no-allow-gpl")
MAX_TOKENS_OPTION = typer.Option(2048, "--max-tokens")
DEDUP_OPTION = typer.Option(True, "--dedup/--no-dedup")
KB_ARGUMENT = typer.Argument(DEFAULT_KB_OUT, exists=True)
INSTRUCTIONS_OPTION = typer.Option(None, "--instructions")
EVAL_OPTION = typer.Option(None, "--eval")
ACTOR_OPTION = typer.Option("codex", "--by")
MANIFEST_ARGUMENT = typer.Argument(DEFAULT_MANIFEST, exists=True)
STAGING_OPTION = typer.Option(DEFAULT_STAGING, "--staging")
BUNDLE_OPTION = typer.Option(DEFAULT_BUNDLE, "--out")
MERMAID_OPTION = typer.Option(DEFAULT_MERMAID, "--mermaid", exists=True, dir_okay=False)
MAPPING_DOC_OPTION = typer.Option(
    DEFAULT_MAPPING_DOC,
    "--mapping-doc",
    exists=True,
    dir_okay=False,
)
SYNC_OUT_OPTION = typer.Option(DEFAULT_SYNC_OUT, "--out-dir")
QUANTUM_ALPHA_OPTION = typer.Option(1.0, "--alpha")
QUANTUM_BETA_OPTION = typer.Option(0.75, "--beta")
QUANTUM_GAMMA_OPTION = typer.Option(0.5, "--gamma")
QUANTUM_DELTA_OPTION = typer.Option(0.05, "--delta")
COMPRESSION_LEVEL_OPTION = typer.Option(6, "--compression-level", min=1, max=9)
ACTOR_SYNC_OPTION = typer.Option("copilot", "--by")
COMPRESS_OPTION = typer.Option(True, "--compress/--no-compress")

app = typer.Typer(help="Codex Knowledge (ingest → normalize → chunk → build)")


# _NODE_RE: matches a Mermaid node declaration, e.g. 'A["label"]' or 'MyNode[text]'
_NODE_RE = re.compile(r"^\s*([A-Za-z][A-Za-z0-9_]*)\s*\[")
# _EDGE_RE: matches directed edge syntax, e.g. 'A-->B', 'A-.->B', 'A==>B' (requires '>' arrowhead)
# An optional node label '[...]' between source ID and the arrow is skipped.
# Limitation: escaped brackets inside labels (e.g. A["text \] bracket"]) are not supported.
_EDGE_RE = re.compile(
    r"^\s*([A-Za-z][A-Za-z0-9_]*)(?:\[[^\]]*\])?\s*[-.=o]*>\s*([A-Za-z][A-Za-z0-9_]*)"
)
_QUANTUM_VARIABLES = ("N", "E", "V", "T")
_QUANTUM_SYMBOL_RE = re.compile(r"\b([NEVT])\b")


def _normalize_edge_syntax(line: str) -> str:
    """Normalize dotted Mermaid edge forms to solid arrows for consistent parsing.

    Converts dotted-arrow edge syntax so ``_EDGE_RE`` (which requires a ``>``
    arrowhead) can match them uniformly.  Only directed edges (those ending
    with ``>``) are normalised and extracted; undirected dotted lines without
    an arrowhead (e.g. ``A.-B``) are **not** matched by ``_EDGE_RE`` and are
    left unchanged.  Example transformations::

        A-.->B   →  A--->B  (dotted open arrow  — matched, triple hyphen result)
        A.->B    →  A->B    (short dotted arrow  — matched)
    """
    return line.replace("-.", "--").replace(".->", "->")


def _extract_mermaid_graph(mermaid_text: str) -> tuple[list[str], list[tuple[str, str]]]:
    """Return node IDs and directed edges from a Mermaid flowchart string."""

    node_ids: set[str] = set()
    edges: list[tuple[str, str]] = []
    for raw_line in mermaid_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("%%"):
            continue
        node_match = _NODE_RE.match(line)
        if node_match:
            node_ids.add(node_match.group(1))
        edge_match = _EDGE_RE.match(_normalize_edge_syntax(line))
        if edge_match:
            src, dst = edge_match.groups()
            node_ids.add(src)
            node_ids.add(dst)
            edges.append((src, dst))
    return sorted(node_ids), edges


def _build_mermaid_search_records(
    *,
    mermaid_path: Path,
    mapping_doc_path: Path,
    mermaid_text: str,
    mapping_doc_text: str,
) -> list[dict[str, object]]:
    """Build searchable records from Mermaid and mapping documents."""

    combined = (
        f"# Mermaid Source ({mermaid_path.as_posix()})\n\n{mermaid_text}\n\n"
        f"# Mapping Doc ({mapping_doc_path.as_posix()})\n\n{mapping_doc_text}"
    )
    chunks = chunk_by_headings(combined, target_tokens=512, overlap_tokens=48)
    records: list[dict[str, object]] = []
    for chunk in chunks:
        text = str(chunk.get("text", ""))
        records.append(
            {
                "id": str(chunk.get("chunk_id", "")),
                "text": text,
                "meta": {
                    "source_path": mermaid_path.as_posix(),
                    "domain": "ops",
                    "intent": "runtime",
                    "lang": "en",
                    "title": str(chunk.get("title", "")),
                    "chunk_idx": int(chunk.get("chunk_idx", 0)),
                    "token_estimate": approx_tokens(text),
                },
            }
        )
    return records


@app.command("build-kb")
def build_kb_cmd(
    root: Path = ROOT_OPTION,
    out: Path = OUT_OPTION,
    allow_gpl: bool = ALLOW_GPL_OPTION,
    max_tokens: int = MAX_TOKENS_OPTION,
    dedup: bool = DEDUP_OPTION,
) -> None:
    """Build knowledge base from documentation files.

    This command processes documentation files in the specified root directory,
    normalizes content, chunks text by headings, and generates a knowledge base
    in NDJSONL format ready for indexing or RAG pipelines.

    Args:
        root: Root documentation directory (default: docs/)
        out: Output KB file path (default: artifacts/kb.ndjsonl)
        allow_gpl: Include GPL-licensed content (default: False)
        max_tokens: Maximum tokens per record (default: 2048)
        dedup: Deduplicate content (default: True)

    Output:
        JSON summary with records processed, tokens used, deduplication stats

    Examples:
        # Build KB from default docs directory
        codex knowledge build-kb

        # Custom output and token limit
        codex knowledge build-kb --out my_kb.ndjsonl --max-tokens 4096

        # Include GPL-licensed content
        codex knowledge build-kb --allow-gpl

        # Without deduplication
        codex knowledge build-kb --no-dedup
    """
    res = build_kb(
        root,
        out,
        allow_gpl=allow_gpl,
        max_tokens_per_rec=max_tokens,
        dedup=dedup,
    )
    typer.echo(json.dumps(res, indent=2))


@app.command("archive-and-manifest")
def archive_and_manifest_cmd(
    kb: Path = KB_ARGUMENT,
    instructions: Path | None = INSTRUCTIONS_OPTION,
    evl: Path | None = EVAL_OPTION,
    by: str = ACTOR_OPTION,
) -> None:
    """Archive knowledge base and generate manifest for release.

    This command creates an archive from a built knowledge base and generates
    a manifest file that includes metadata and validation information for
    distribution or deployment.

    Args:
        kb: Path to built knowledge base file (must exist)
        instructions: Optional instructions/README file
        evl: Optional evaluation/metrics file
        by: Actor identifier for the manifest (default: "codex")

    Output:
        JSON manifest with archive metadata and checksums

    Examples:
        # Basic archive with KB only
        codex knowledge archive-and-manifest artifacts/kb.ndjsonl

        # With instructions and evaluation files
        codex knowledge archive-and-manifest artifacts/kb.ndjsonl \\
          --instructions docs/instructions.md \\
          --eval docs/eval.md

        # Specify actor
        codex knowledge archive-and-manifest artifacts/kb.ndjsonl --by bot
    """
    res = archive_and_manifest(kb, instructions, evl, actor=by)
    typer.echo(json.dumps(res, indent=2))


@app.command("pack-release")
def pack_release_cmd(
    manifest: Path = MANIFEST_ARGUMENT,
    staging: Path = STAGING_OPTION,
    out_bundle: Path = BUNDLE_OPTION,
) -> None:
    """Pack knowledge base release bundle with verification.

    This command creates a compressed bundle from a manifest, including all
    components, files, and checksums. The bundle can be verified independently
    and extracted to any destination.

    Args:
        manifest: Path to manifest file (must exist)
        staging: Staging directory for bundle creation (default: work/knowledge_staging)
        out_bundle: Output bundle path (default: dist/codex-knowledge.tar.gz)

    Output:
        JSON with bundle path, SHA256 hash, and verification status

    Examples:
        # Pack with defaults
        codex knowledge pack-release artifacts/knowledge.release.manifest.json

        # Custom staging and output
        codex knowledge pack-release artifacts/knowledge.release.manifest.json \\
          --staging /tmp/staging \\
          --out dist/codex-kb-v1.tar.gz

    See Also:
        codex knowledge archive-and-manifest - Create manifest from KB
        codex release verify - Verify bundle integrity
    """
    bundle, locked = pack_release(manifest, staging, out_bundle)
    v = verify_bundle(bundle)
    typer.echo(
        json.dumps(
            {
                "bundle": bundle.as_posix(),
                "sha256_manifest": locked["checks"]["sha256_manifest"],
                "verified": v["ok"],
            },
            indent=2,
        )
    )


@app.command("sync-mermaid-map")
def sync_mermaid_map_cmd(
    mermaid: Path = MERMAID_OPTION,
    mapping_doc: Path = MAPPING_DOC_OPTION,
    out_dir: Path = SYNC_OUT_OPTION,
    alpha: float = QUANTUM_ALPHA_OPTION,
    beta: float = QUANTUM_BETA_OPTION,
    gamma: float = QUANTUM_GAMMA_OPTION,
    delta: float = QUANTUM_DELTA_OPTION,
    compression_level: int = COMPRESSION_LEVEL_OPTION,
    by: str = ACTOR_SYNC_OPTION,
    compress: bool = COMPRESS_OPTION,
) -> None:
    """Synchronize Mermaid runtime maps into tokenized searchable datablobs."""

    mermaid_text = mermaid.read_text(encoding="utf-8")
    mapping_doc_text = mapping_doc.read_text(encoding="utf-8")
    nodes, edges = _extract_mermaid_graph(mermaid_text)
    variables = {
        "N": len(nodes),
        "E": len(edges),
        "V": len(
            set(_QUANTUM_SYMBOL_RE.findall(mapping_doc_text)).intersection(_QUANTUM_VARIABLES)
        ),
    }
    records = _build_mermaid_search_records(
        mermaid_path=mermaid,
        mapping_doc_path=mapping_doc,
        mermaid_text=mermaid_text,
        mapping_doc_text=mapping_doc_text,
    )
    token_total = 0
    for rec in records:
        meta = rec.get("meta")
        if isinstance(meta, dict):
            token_total += int(meta.get("token_estimate", 0))
    variables["T"] = token_total
    coherence_score = (
        alpha * variables["N"]
        + beta * variables["E"]
        + gamma * variables["V"]
        + delta * variables["T"]
    )
    equation = "ψ = α·N + β·E + γ·V + δ·T"

    payload: dict[str, Any] = {
        "source": {
            "mermaid": mermaid.as_posix(),
            "mapping_doc": mapping_doc.as_posix(),
        },
        "graph": {
            "nodes": nodes,
            "edges": [{"src": src, "dst": dst} for src, dst in edges],
        },
        "quantum_mapping": {
            "equation": equation,
            "coefficients": {"alpha": alpha, "beta": beta, "gamma": gamma, "delta": delta},
            "variables": variables,
            "coherence_score": round(coherence_score, 4),
        },
        "search_index": {
            "records": len(records),
        },
        "actor": by,
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    blob_json = out_dir / "mermaid_sync_datablob.json"
    payload_bytes = json.dumps(payload, indent=2).encode("utf-8")
    blob_json.write_bytes(payload_bytes)

    records_path = out_dir / "mermaid_sync_search.ndjsonl"
    with records_path.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json_dumps_sorted(rec) + "\n")

    compressed_path: str | None = None
    codec = compression_codec()
    if compress:
        suffix = ".zst" if codec == "zstd" else ".zlib"
        comp_file = out_dir / f"mermaid_sync_datablob.json{suffix}"
        comp_file.write_bytes(zstd_compress(payload_bytes, level=compression_level))
        compressed_path = comp_file.as_posix()

    typer.echo(
        json.dumps(
            {
                "ok": True,
                "blob": blob_json.as_posix(),
                "blob_sha256": sha256_file(blob_json),
                "search_records": records_path.as_posix(),
                "compressed_blob": compressed_path,
                "compression_codec": codec if compress else None,
                "compression_level": compression_level if compress else None,
                "quantum_coherence_score": payload["quantum_mapping"]["coherence_score"],
                "node_count": variables["N"],
                "edge_count": variables["E"],
                "variable_count": variables["V"],
                "token_count": variables["T"],
            },
            indent=2,
        )
    )
