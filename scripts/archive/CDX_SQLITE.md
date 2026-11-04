# Content-addressable SQLite archive

The `codex_packer.py`, `codex_query.py`, and `codex_rehydrate.py` commands
implement a regenerable `.cdx.sqlite` snapshot. The database is a build artifact,
not a replacement for Git history and not a file to commit to the repository.
The source directory is never modified by packing.

## Pack

Packing requires `gitleaks` with the `dir` command and `detect-secrets` on
`PATH`. Both scan the
source tree before any archive data is written. A scanner failure blocks
creation. A finding also blocks creation unless its exact source-relative path
is explicitly allow-listed; allow-list only reviewed false positives.

```bash
python -m scripts.archive.codex_packer \
  .codex/archive /tmp/codex-archive.cdx.sqlite
```

By default, `.git`, `.worktrees`, virtual environments, caches, `node_modules`,
SQLite/database files, and Python bytecode are excluded. Individual files larger
than 8 MiB are skipped; adjust `--max-file-bytes` or use `--allow-large
RELATIVE_GLOB` when a reviewed file should be included. Blobs over the independent
512 MiB ceiling are rejected; `--max-blob-bytes` adjusts that limit explicitly.
`--exclude GLOB` adds a deny rule. `--allow-secret RELATIVE_PATH` is an explicit
exception to the scanner gate and should be used sparingly.

The packer first copies the selected tree into a private temporary snapshot,
scans that snapshot, and verifies its recorded metadata and content hashes again
while packing. Source changes during or after scanning therefore cannot silently
substitute different bytes into the archive.

Archive payloads are zlib-compressed and deduplicated by SHA-256 of the original
working-tree bytes. Tracked entries also record the Git `HEAD` blob object ID;
the SHA-256 remains the integrity check for bytes actually packed, including
working-tree line endings. Text decoding is an index only: raw bytes, file
metadata, and symlink targets are retained separately. The packer writes a
temporary database, runs SQLite integrity checking, then atomically replaces
the requested output.

## Query and verify

```bash
python -m scripts.archive.codex_query /tmp/codex-archive.cdx.sqlite info
python -m scripts.archive.codex_query /tmp/codex-archive.cdx.sqlite list \
  --prefix root-consolidation
python -m scripts.archive.codex_query /tmp/codex-archive.cdx.sqlite search "Merkle root"
python -m scripts.archive.codex_query /tmp/codex-archive.cdx.sqlite symbols Greeter
python -m scripts.archive.codex_query /tmp/codex-archive.cdx.sqlite context \
  --symbol Greeter.greet --budget-tokens 1200
python -m scripts.archive.codex_rehydrate verify /tmp/codex-archive.cdx.sqlite
```

The query connection is SQLite read-only and validates all blob hashes, decoded
text indexes, FTS postings, metadata, and the Merkle root when opened. This one-time verification
cost precedes indexed lookups. `context` uses a conservative
four-characters-per-token budget estimate because tokenizers are intentionally
not a runtime dependency. Text reads default to a 64 MiB ceiling and byte reads
to the 512 MiB blob ceiling; use `--max-text-bytes` or `--max-blob-bytes` when
intentionally querying larger data. Text reads use the decoded UTF-8 search
index; byte reads verify the decompressed payload against its SHA-256.

## Rehydrate

```bash
python -m scripts.archive.codex_rehydrate extract \
  /tmp/codex-archive.cdx.sqlite /tmp/rehydrated
python -m scripts.archive.codex_rehydrate compare \
  .codex/archive /tmp/rehydrated
```

Verification checks SQLite integrity, every blob's declared size and SHA-256,
entry counts, and the canonical Merkle root before extraction starts. Extraction
rejects traversal paths and external symlinks by default. Relative
links that traverse another archived symlink are rejected to prevent a chain
from escaping the destination. Pass
`--allow-external-symlinks` only when restoring a reviewed archive intentionally
containing links outside the destination. Permission bits and nanosecond
timestamps are restored where the host filesystem supports them. Packing and
rehydration fail closed on setuid/setgid modes to avoid creating privileged
files; symlink
timestamp support is platform-dependent.

## Schema

The schema version is fixed in `cdx_common.py`. `tree_entries` stores paths and
filesystem metadata; `content_blobs` stores one zlib payload per unique raw
SHA-256; `text_documents` stores one UTF-8 decoded text value per decodable file while
retaining its recognized line endings. `fts_code_index` is an external-content FTS5 index over file text and
Python symbol line slices. `ast_symbols` records symbol relationships,
signatures, decorators, bases, call targets, and source line ranges.
