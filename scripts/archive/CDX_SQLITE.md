# Content-addressable SQLite archive

The `codex_packer.py`, `codex_query.py`, and `codex_rehydrate.py` commands
implement a regenerable `.cdx.sqlite` snapshot. The database is a build artifact,
not a replacement for Git history and not a file to commit to the repository.
The source directory is never modified by packing.

## Pack

Packing requires pinned `gitleaks` 8.30.1 with the `dir` command and
`detect-secrets` 1.5.0 on `PATH`. Other versions are rejected. Both scan the
source tree before any archive data is written. A scanner failure blocks
creation. Every finding blocks creation unless it has an exact, current
false-positive disposition bound to the scanner/version, source-relative path,
source-file SHA-256, rule, line range, and keyed finding identity. Path, glob,
rule, and directory allowlists are not supported.
Gitleaks runs with JSON output and `--redact=100`; detect-secrets runs with
`scan --all-files` and network verification disabled.

```bash
python -m scripts.archive.codex_packer \
  .codex/archive /tmp/codex-archive.cdx.sqlite
```

For a tree with findings, the packer can write a redacted inventory outside the
scanned tree and will still fail without approved dispositions:

```bash
CDX_FINDING_HMAC_KEY="$PRIVATE_FINDING_KEY" \
  python -m scripts.archive.codex_packer \
  .codex/archive /tmp/codex-archive.cdx.sqlite \
  --finding-inventory /tmp/codex-findings.json
```

The key must be at least 32 UTF-8 bytes and must be retained in an approved
secret store; never put it in the repository or command history. The inventory
contains opaque HMAC identities and finding metadata, not matched values or
source lines. A disposition JSON has `schema_version: 1` and a `dispositions`
array copied from the inventory. Each item must retain its exact scanner,
version, finding ID, path, source digest, rule, and line range, and set
`disposition` to `false_positive` with `evidence_ref` naming an accessible
review-evidence file outside the source tree and `reviewed_by` naming the
reviewer. `evidence_sha256` must match that evidence file's SHA-256 digest.
Review evidence must be stored separately and must affirmatively establish
that the exact finding is harmless. Never infer that from nearby test/example
markers. Supply the reviewed file using
`--finding-dispositions /secure/path/dispositions.json` and the same private
`CDX_FINDING_HMAC_KEY`. Missing, stale, duplicate, malformed, or mismatched
dispositions block packing; scanner versions, source digests, and locations
are rechecked on every run.

### Exact-finding recovery (no packing)

`scripts.archive.cdx_review` prepares private **advisory-only** observation queues.
It never invokes scanners, writes dispositions, authenticates reviewers, or
authorizes packing. Inventory counts are scanner observations, not unique secrets.
Every observation initially remains `unreviewed`; cross-scanner overlaps remain
separate. Resume preserves only conservative scheduling states, requires identical
run/source/selection/toolchain/configuration/inventory and identity-version
bindings, and rejects approval or evidence claims. The reserved evidence/accepted
states are always zero in this tool: supporting them requires a separate actual
review trust contract, not another agent label.

Use owner-only files in an owner-only private directory outside the source.
The inventory must be complete schema version 1 output from the maintained scanner
contract; loading it establishes structure and byte identity, not authenticity.
Bindings are a JSON object with `identity_version: 2`, a fresh 32-character
hexadecimal `run_namespace`, and 64-character hexadecimal `source_sha256`,
`selection_sha256`, `toolchain_sha256`, and `config_sha256`. Record how those
digests were independently measured in a separate sanitized checkpoint; labels
alone do not prove that scanners ran or configurations are trustworthy.

Invoke `python -m scripts.archive.cdx_review` with absolute `--source`,
`--inventory`, `--bindings`, and a new numbered `--output` path. Add `--resume`
with the previous private queue to preserve conservative scheduling. Output is
aggregate counts and checkpoint digest only. Reads reject duplicate keys,
nonfinite JSON, oversized documents, symlinks (including ancestors), hardlinks,
nonregular files, and permissive modes. Checkpoints use descriptor-relative,
create-only atomic publication and fsync; existing history is never overwritten.
An interrupted run must resume from the last complete checkpoint, not a temporary
file. Publication fsyncs the directory again after removing the temporary link.
A crash between linking and unlinking can leave a two-link checkpoint: private
loading rejects it. Resume from the preceding complete checkpoint or regenerate
a new numbered queue from the bound inventory; do not promote the interrupted
file or remove unknown temporary files automatically. No key, raw report,
inventory, or private queue belongs in Git.

Finding identity algorithm **2** canonicalizes scanner `File` to the validated
source-relative path. For Gitleaks `dir` observations it also canonicalizes the
exact `File:RuleID:StartLine` fingerprint form and sorts string tags without
deduplicating them. Other record fields, including columns and opaque secret
identifiers, remain identity-bound. Unknown fingerprint forms remain verbatim
and may therefore remain snapshot-dependent; git-history scans are not supported
by the packer. All algorithm-1 identities are historical and intentionally fail
new disposition matching. Never migrate an approval solely by matching exported
metadata. A discarded HMAC key or omitted raw record cannot be reconstructed
from a redacted inventory.

The scanner contract bounds each subprocess to 600 seconds, rejects ambiguous
JSON and Gitleaks status/report disagreement, and writes inventories mode 0600.
Gitleaks exit 1 denotes observations, not scanner clearance; unresolved
observations still block before any archive database is created.

**Review trust limitation:** the maintained disposition validator checks exact
metadata, a nonblank reviewer label, external evidence accessibility and digest.
It does not authenticate that label or decide whether evidence is relevant.
A valid digest for irrelevant evidence is not affirmative proof. These review
obligations remain blocking until fulfilled by a genuine authorized review
process. Revoked, archived or duplicated real secrets are not false positives.
Session-private `/tmp` files are not durable escrow; cross-session reuse needs an
actually approved private retention mechanism for the key and relevant evidence.

By default, `.git`, `.worktrees`, virtual environments, caches, `node_modules`,
SQLite/database files, and Python bytecode are excluded. Individual files larger
than 8 MiB are skipped; adjust `--max-file-bytes` or use `--allow-large
RELATIVE_GLOB` when a reviewed file should be included. Blobs over the independent
512 MiB ceiling are rejected; `--max-blob-bytes` adjusts that limit explicitly.
`--exclude GLOB` adds a deny rule. No secret allowlist option exists.

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
