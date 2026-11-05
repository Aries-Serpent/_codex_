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
Gitleaks is invoked with `--exit-code 2`: exit 2 denotes observations, while exit 1
is rejected even with findings because it can indicate partial execution.
Unresolved observations still block before any archive database is created.

### Measured private preflight producer

`python -m scripts.archive.cdx_preflight --source ABSOLUTE_SOURCE
--private-directory NEW_EMPTY_OWNER_ONLY_DIRECTORY` performs preparation only.
It calls the existing scanner contract, never the packer. Verify both pinned tools
and their upstream provenance before invoking it; measured byte identity is not
upstream authentication. The detect-secrets launcher must use the invoking Python
environment. No packages are installed or modified.

The producer copies every entry without packer exclusions or large-file skips,
using bounded no-follow reads. Resource limits (100,000 entries, 512 MiB per file,
4 GiB total), unsupported types and external symlinks block instead of narrowing
selection. Fingerprints preserve the checkpoint format: sorted directory walk,
sorted immediate children, compact ASCII JSON arrays of relative path/type/mode/
mtime-nanoseconds/size/payload, newline-delimited and SHA-256 hashed. Payload is a
file SHA-256, symlink target or null. Directories have size zero.

`measure_tree` retains that live filesystem fingerprint as `sha256` and adds
`content_sha256` with `content_identity_version: 1`. The deterministic content
digest hashes the same ordered, newline-delimited compact ASCII JSON rows with
only mtime-nanoseconds omitted: `[relative_path, type, mode, size, payload]`.
It includes empty directories and internal symlink targets, excludes the root
directory's own metadata, and applies the same safety and resource limits.
Timestamp-only drift changes the live digest but not the content digest; bytes,
paths, types, permission modes, sizes and link targets remain content-bound.
An exact snapshot preserves both digests. This additional identity is descriptive,
not a clearance, finding-identity version or reusable epoch authorization.
Producer and loader comparisons retain the complete measurement, including the
live `sha256`; `source_sha256` bindings still use that live digest. Matching content
never permits metadata drift to load an old run. Older measurements without the
explicit content fields are not upgraded implicitly and fail current comparisons.

Source and snapshot fingerprints, executable bytes, interpreter, installed
distribution files, implementation bytes and explicit configuration are measured
before and after scanning. Full-tree selection and packer-default selection have
separate descriptors; this producer never claims to have scanned the latter.
An external Gitleaks default-extension configuration, empty external ignore file,
`--ignore-gitleaks-allow`, neutral cwd and allowlisted child environment prevent
inherited credentials/configuration and project suppression overrides. Built-in
scanner heuristics, detect-secrets default filters, binary/decoding limitations
and Gitleaks default nested-archive limits remain scanner coverage limitations;
exact tree identity does not mean every byte was semantically analyzed.

Owner-only private artifacts include the session key, redacted inventory, complete
canonical scanner observations, raw subprocess reports/diagnostics, detector
report/settings, measured provenance and advisory queue. These contain sensitive
private metadata and must never enter Git,
public reports or prompts. `complete.json` is created last; partial directories
are not completed runs. The producer's endpoint/per-read checks do not establish
OS-level isolation from another same-user writer or authenticate a reviewer.
Owner-only session retention is **nondurable**, not approved escrow.
Available subprocess reports are retained before interpreting status or parsing.
A sanitized `failure.json` records known failure codes and retained stages without
copying diagnostics into public output; timeout/interruption can still leave no
complete report. Never reinterpret a failed directory as a successful baseline.
`preparation.json` retains measured source/selection/configuration/tool inputs
before subprocess execution, but does not establish a completed baseline.
Relative observation paths are resolved against the explicit scanner working
directory, not the producer's parent cwd; absolute paths must still be in-root.
When an explicit cwd is supplied, out-of-root paths cannot fall back to a
lookalike source-relative path.

`--assess-first-batch` privately assesses at most 16 observations per scanner.
The Python API `assess_batch(source, private, batch_index=N)` supports batches
1–999 (default 1). Batch 1 resumes `queue.json`; subsequent batches require the
immediately preceding `queue-NNN.json` in the same bound inventory/run. Scheduling
revalidates that checkpoint through `build_queue`, rejecting stale bindings,
duplicate observations and evidence/approval claims. It selects only `unreviewed`
observations, in bound inventory order within each scanner, at most 16 per
scanner / 32 total. Previously assessed or otherwise non-unreviewed rows are not
reselected. `batch-NNN.json` and `queue-NNN.json` are create-only: existing
destinations, including interrupted history, must not be overwritten. Publication
of the pair is not transactional; interruption can leave a batch without its
queue, which must not be treated as a completed checkpoint.
The loader rechecks actual current source/snapshot/tools/configuration, artifact
digests and every canonical observation's keyed identity. Offline detector replay
has verification filters disabled; bounded context predicates are recorded
without exporting values or lines. Every assigned observation remains advisory
`indeterminate`, with an explicit evidence gap, zero false-positive proofs and
zero approvals. Context predicates are investigation aids, not harmlessness proof.
The existing advisory CLI still accepts structurally valid supplied bindings;
only the measured producer/loader makes these additional local provenance checks.

### Supported private Gitleaks coordinate contract

The shared private span helper is pinned to **Gitleaks 8.30.1**, based on official
[`detect/location.go`](https://github.com/gitleaks/gitleaks/blob/v8.30.1/detect/location.go),
[`detect/detect.go`](https://github.com/gitleaks/gitleaks/blob/v8.30.1/detect/detect.go),
[`sources/file.go`](https://github.com/gitleaks/gitleaks/blob/v8.30.1/sources/file.go)
and [`report/finding.go`](https://github.com/gitleaks/gitleaks/blob/v8.30.1/report/finding.go).
It does not emulate Go regular expressions or infer secret capture groups.

- `StartLine`/`EndLine` and byte columns are positive integers (not booleans).
  `EndColumn` is inclusive. Columns count **bytes, not Unicode characters**.
  Importantly, the pinned implementation measures subsequent-line columns from
  the preceding **LF byte index**, not the byte after LF; the first content byte
  on such a line is column 2. First-line columns start at 1.
- Only strict UTF-8 regular-file content smaller than the pinned 100,000-byte
  default fragment buffer is supported, with LF or CRLF (including mixed LF/CRLF).
  No NUL, lone CR, split UTF-8 code points, archive-member paths, commit/symlink
  source metadata or non-null `Fragment` metadata is supported. A span is limited
  to 65,536 bytes and a line-number difference of at most 100. Endpoints must be
  inside content, not line terminators; intervening LF/CRLF bytes are preserved.
- Single-line spans may end on an unterminated final line. Multi-line spans
  ending on that line are unsupported: the pinned location implementation does
  not produce a usable end column in that case. Missing/malformed coordinates,
  large/chunked files and other versions/encodings remain explicitly unsupported,
  not guessed or converted through character indexes.
- Decoding is unsupported, including `Encoded`/`Decoded` metadata or tags and
  native `decoded:<kind>` / `decode-depth:N` tags (including nested decoding).
  See [`detect/codec/segment.go`](https://github.com/gitleaks/gitleaks/blob/v8.30.1/detect/codec/segment.go).
  Encoded-source coordinates cannot establish a decoded secret's exact bytes.

Coordinates locate the reported **Match**, not necessarily **Secret**. At 100%
redaction the scanner replaces Secret with `REDACTED` and replaces occurrences
of Secret inside Match; the remaining Match can still include sensitive context.
A redaction marker is only a payload predicate, never proof that a secret was
recovered, harmless, or entirely removed from every report field. Even a mapped
Match leaves `exact_secret_recovered` false and candidate origin/use proofs
`unavailable`. Only safe mapping/redaction predicates are persisted by assessment;
private span bytes and source lines/values are never exported in its results.
Every row remains `indeterminate`, with zero semantic false-positive proofs or
approvals. No disposition/evidence acceptance rules are changed.

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
