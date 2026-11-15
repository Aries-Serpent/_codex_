# Content-addressable SQLite archive

The `codex_packer.py`, `codex_query.py`, and `codex_rehydrate.py` commands
implement a regenerable `.cdx.sqlite` snapshot. The database is a build artifact,
not a replacement for Git history and not a file to commit to the repository.
The source directory is never modified by packing.

## Offline skills catalog and common preflight

`python -m scripts.archive.cdx_common --preflight-context --json` exposes local
capability context, not a secret scan, review approval, or permission to pack.
The session startup packet persists `skills_registry`, `cdx_module_index`, and
`cdx_common_preflight`, including exact source lines and CLI/test commands.
`scripts/ci/cdx_context.py` regenerates these from explicit local source/test paths
without network access or scanning agent directories.
`python -m scripts.ci.startup_health --refresh-context` updates only catalog fields
without changing health data or its timestamp; `--validate` rejects missing/stale
CDX catalogs while allowing unrelated skills/candidates and registry metadata.
Context refresh retains those unrelated registry extensions.
Normal generation also includes the CDX fields.
The repository profile `.github/agents/cdx-archive-lifecycle.agent.md` is
registered locally, never proof of hosted activation or authority. Its explicit
read/search/execute/edit tools support inspection, lifecycle commands and
task-authorized same-scope fixes, not blanket filesystem or network isolation.
`python -m scripts.archive.cdx_preflight --preflight-summary --json` exposes
the shared read-only summary without scanning a selected source. The common
public API also exports `inspect_and_pack_blob`, `validate_safe_rel_path`,
`validate_symlink_target`, `verify_archive_connection`, `verify_archive`, and
`validate_inventory`, with lazy delegation to existing implementations.
Their exact locations, and preflight `assess_acquired_batch`, are catalogued.
The candidate ID is `cdx-archive-lifecycle`; both `agent_candidates` and `skills`
expose it as `local_profile`, not a runtime/hosted activation. The compatibility
container `agent_candidates` retains its name; its status describes local
registration only. Refresh removes the old holding-path record while preserving
unrelated candidates. `hosted_activation` remains `not_established`, and
`authorization` remains `none_granted`: catalog generation grants no authority.
Verify actual discovery, selection, effective tools and bounded invocation
separately in VS Code/Copilot SDK and GitHub's hosted runtime. GitHub's documented
repository route integrates the profile into the default branch before selector
discovery; a local test or feature-branch entry cannot establish hosted activation.
The generated JSON compatibility-alias description has one exact detect-secrets
baseline entry because JSON cannot carry the source's line-scoped pragma.
This does not exclude the packet, change scanners or regenerate a broad baseline;
changed values remain detectable and archive-finding approval rules are unchanged.
`cdx_common_preflight.functions` explicitly maps `inspect_text`,
`compute_merkle_root`, `_canonical_scanner_finding`, `_validate_external_path`,
`run_secret_scanners`, `pack_archive`, `CodexArchiveQuery`, `rehydrate_archive`,
and `verify_archive`. **`pack_directory` does not exist**: use `pack_archive`.
The canonical scanner function is plural `run_secret_scanners`;
`run_secret_scanner` is an exported compatibility alias of that same function,
not an independent scanner or clearance mechanism.

### Actual CLI parser contracts

Each module index entry includes `cli_contract`: parser-derived root arguments,
subcommands and their arguments, with source lines. This is static AST discovery,
not execution or inferred command support.
`exported_signatures` includes public top-level/class-method signatures and
requested private helpers across all eight explicit Python/Go source modules.
Commands below use prefix `python -m scripts.archive.` (except the Go executable):

| Module | Actual subcommands / principal options |
| --- | --- |
| `cdx_common` | `--preflight-context --json` |
| `cdx_preflight` | `--preflight-summary --json`; preparation `--source`, `--private-directory`, `--assess-first-batch`, `--assess-acquired-batch`, `--gitleaks-adapter` |
| `cdx_review` | `--source`, `--inventory`, `--bindings`, `--output`, optional `--resume` or read-only `--list-batches` |
| `cdx_adapter` | `--list-batches`, `--source`, `--private-directory`, `--gitleaks-adapter` |
| `codex_packer` | positional `SOURCE OUTPUT`; `--max-file-bytes`, `--max-blob-bytes`, `--exclude`, `--allow-large`, `--finding-dispositions`, `--finding-inventory` |
| `codex_query` | positional archive then `info`, `list`, `read`, `search`, `symbols`, `callgraph`, `context`; `context --budget-tokens --format`, `search --limit`, `list --prefix --glob --type --language` |
| `codex_rehydrate` | `verify ARCHIVE`, `extract ARCHIVE DESTINATION`, `compare LEFT RIGHT`; `extract --allow-external-symlinks`, `verify/extract --max-blob-bytes --max-text-bytes` |
| Go adapter executable | `identity`; no-argument scan consumes owner-only request JSON on stdin |

For example, the extraction CLI is
`python -m scripts.archive.codex_rehydrate extract ARCHIVE.cdx.sqlite DESTINATION`,
not an archive/destination invocation without `extract`.

| Source module | Key functions | CLI entrypoint | Tests |
| --- | --- | --- | --- |
| `scripts/archive/cdx_common.py` | `iter_deterministic_tree`, `run_secret_scanners`, `run_cdx_common_preflight` | `python -m scripts.archive.cdx_common --preflight-context --json` | `tests/archive/test_cdx_context.py`, `test_cdx_sqlite_archive.py` |
| `scripts/archive/cdx_preflight.py` | `measure_tree`, `measure_toolchain`, `run_preflight`, `load_preflight`, `assess_batch` | `python -m scripts.archive.cdx_preflight --help` | `tests/archive/test_cdx_preflight.py` |
| `scripts/archive/cdx_review.py` | `read_private_json`, `validate_inventory`, `build_queue`, `schedule_batch`, `write_checkpoint` | `python -m scripts.archive.cdx_review --help` | `tests/archive/test_cdx_review.py` |
| `scripts/archive/cdx_adapter.py` | `measure_adapter`, `run_adapter`, `load_adapter`, `stock_relationship`, `acquired_span`, `list_batches` | `python -m scripts.archive.cdx_adapter --list-batches --source SOURCE --private-directory PRIVATE --gitleaks-adapter EXECUTABLE` | `tests/archive/test_cdx_adapter.py` |
| `scripts/archive/codex_packer.py` | `pack_archive` | `python -m scripts.archive.codex_packer --help` | `tests/archive/test_cdx_sqlite_archive.py` |
| `scripts/archive/codex_query.py` | `CodexArchiveQuery.list_tree`, `search_fts`, `query_symbols`, `build_llm_context` | `python -m scripts.archive.codex_query --help` | `tests/archive/test_cdx_sqlite_archive.py` |
| `scripts/archive/codex_rehydrate.py` | `verify_archive`, `rehydrate_archive`, `compare_trees` | `python -m scripts.archive.codex_rehydrate --help` | `tests/archive/test_cdx_sqlite_archive.py` |
| `scripts/archive/gitleaks_adapter/main.go` | `provenance`, `readFile`, `selectedFiles`, `localize`, `scan` | `EXECUTABLE identity`; owner-only JSON request on stdin | `cd scripts/archive/gitleaks_adapter && GOPROXY=off GOSUMDB=off go test ./...` |

Adapter `--list-batches` revalidates the completed current bundle, never scans or
creates checkpoints, and indexes **all** observations in deterministic batches
of at most 32. Batch indices are zero-based, consistent with review batch
discovery; `start_ordinal` and
`end_ordinal_exclusive` form zero-based half-open ranges. Zero observations produce
an empty list. Output includes only bindings/counts/index ranges, not matched
values or spans; the operation always retains `packer_clearance_compatible: false`.
The executable's local `identity` operation is still checked during revalidation;
listing is not a substitute for actual adapter provenance or completed scans.
Discovery indices are distinct from the historical one-based
`cdx_preflight.assess_batch(..., batch_index=N)` checkpoint numbering.

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

#### Optional acquisition-bound report adapter (functional PoC)

`scripts/archive/gitleaks_adapter` is a **locally built adapter**, not an
official Gitleaks release executable. Its Go module pins
`github.com/zricethezav/gitleaks/v8 v8.30.1` and verifies the module version,
checksum and absence of replacement in executable build information.
`go.sum` preserves the ecosystem-verified closure. Advisory remediation raises
only transitive `golang.org/x/crypto` to 0.52.0 and
`github.com/klauspost/compress` to 1.18.7; this requires Go >=1.25.
The scanner pins remain Gitleaks 8.30.1 and detect-secrets 1.5.0.

Build with the standard Go toolchain in
`/home/runner/work/_codex_/_codex_/scripts/archive/gitleaks_adapter` using
`go mod verify`, `go test ./...`, and `go build -o "$CDX_ADAPTER_EXECUTABLE" .`.
Set Go caches/build scratch directories to task-owned directories outside the
source selection. The current adapter targets Linux. Absolute executable and
private-directory paths are required; never place binaries/private reports in
the scanned source or commit them.

The maintained preflight CLI accepts `--gitleaks-adapter "$CDX_ADAPTER_EXECUTABLE"`.
It first performs the existing two-scanner preflight, then invokes the adapter
as a **separate advisory supplement** on that exact private snapshot.
`cdx_adapter.run_adapter` also supports a completed maintained preflight.
The producer generates the request, fresh namespace/key and complete sorted
regular-file manifest, measures executable/consumer/configuration bytes, and
retains owner-only request/report/completion artifacts. Adapter failures have a
separate `adapter-failure.json`; an existing stock `complete.json` does not imply
adapter completion. Existing histories, including interrupted ones, are never
overwritten.

Each regular file is read through no-follow ancestor descriptors and checked
against the expected size/digest. **Those exact acquired bytes**, without slices
or overlaps, become one full-file `DetectContext` call with line origin 1.
The adapter records observed input interval `[0, file_size)`, invocation bindings
and every library-returned observation, without adapter deduplication. Before
redaction it checks the reported Match against its exact acquired byte interval
and retains a private keyed Match binding. The loader rechecks the actual current
stock bundle, complete manifest, report/request digests, measured adapter,
consumer/configuration and source; `acquired_span` accepts an observation ID from
that reverified run, **not caller-selected origin metadata**. Match localization
does not recover the captured Secret or prove its origin, consumer use or
harmlessness. Unsupported library match coordinates remain explicitly unmapped.

Limits block instead of skipping: 8 MiB/file, 256 MiB/tree, 10,000 regular files,
100,000 entries, 50,000 findings, 16 MiB request/report and 256 MiB total mapped
Match bytes. The library deadline/CPU limit is 120 seconds, the subprocess timeout
150 seconds; address space is limited to 4 GiB with a 512 MiB soft Go memory limit.
The consumer indexes newlines and checks UTF-8 once per acquisition, with a total
mapped-byte budget. Non-UTF-8, NUL and bare CR block. LF/CRLF/UTF-8 byte columns are
supported; nested archives, decoding and git-history modes are not. Internal
symlinks remain recorded by the maintained snapshot, never followed by the
adapter. Embedded default rules, built-in allowlists and rule precedence remain
scanner coverage limitations; source `gitleaks:allow` comments are ignored.

**Compatibility is measured, never presumed:** the producer compares complete
canonical Gitleaks record multisets against the independent stock report, without
deduplication. Equal records mean equality only on that snapshot; divergence is
`BLOCKED_CONTEXT_OR_COVERAGE_DIVERGENCE`. Whole-file context can change detection
and columns. The adapter always reports `packer_clearance_compatible: false`:
its fresh advisory identities cannot authorize the packer's later independent
stock snapshot/rescan, and the packer/scanner/disposition gate is unchanged.
No report-mode bypass, approval migration or historical-count reconciliation is
provided. Private reconciliation version 1 now retains every occurrence in
separate zero-based stock/adapter ordinal lists, grouped by pinned version, exact
file path/digest and complete canonical record digest. Matched, missing-from-
adapter, extra-in-adapter and duplicate multiplicities are explicit; duplicates
remain ambiguous even when multisets agree. Unique exact-record associations
are descriptive only. Unmatched changed-context records remain separate, without
guessed fragment columns, redacted-text joins or arbitrary duplicate pairing.
Raw reports and canonical records remain retained in their original namespaces.

`cdx_adapter.stock_relationship(source, private, executable, stock_ordinal)`
revalidates the complete current run and returns that stock occurrence's private
relationship with both namespaces/bindings. Non-Gitleaks, invalid or absent
ordinals fail closed. It returns no stock byte span or semantic evidence.
The loader recomputes all groups/counts, rejecting altered association metadata.
Consumer changes invalidate historical runs; reconciliation cannot upgrade them.
Real-source use remains gated on synthetic proof, review and explicit
independent-scan compatibility assessment; an unresolved divergence cannot clear
stock observations.

Remaining components for actual clearance are not supplied by this PoC:
exact-observation origin/use/harmlessness evidence, independently authenticated
reviewer authority, approved durable private retention, and a separately reviewed
clearance mechanism if descriptive stock/adapter associations are proposed as
evidence. Exact redacted-record equality cannot supply missing stock byte origin.
Same-user endpoint/HMAC integrity is neither OS snapshot isolation nor external
authentication. No archive operation is authorized by adapter development.

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

### Separate acquisition-bound assessment

`python -m scripts.archive.cdx_preflight --source SOURCE --private-directory PRIVATE
--gitleaks-adapter EXECUTABLE --assess-acquired-batch` requires the measured adapter
and assesses at most 32 freshly revalidated acquisition observations.
`assess_acquired_batch(source, private, executable, batch_index=1)` uses one-based
assessment checkpoint numbering and writes create-only `acquired-batch-NNN.json`;
this numbering is separate from zero-based discovery indices.
The output namespace is `acquired_full_file_adapter_not_stock`, with purpose
`acquired_adapter_assessment_not_stock_mapping_or_clearance`.
Only the independently validated full-file acquisition permits the mapper's
caller-only `unfragmented=True` input, including acquired input at or above
100,000 bytes. Every assessed row remains advisory `indeterminate`, with zero
accepted observations, semantic false-positive proofs and stock fragment-origin
proofs. `--assess-first-batch` remains stock-only; record equality never transfers
acquisition provenance to stock reports or authorizes packing.

### Supported private Gitleaks coordinate contract

The shared private span helper is pinned to **Gitleaks 8.30.1**, based on official
[`detect/location.go`](https://github.com/gitleaks/gitleaks/blob/v8.30.1/detect/location.go),
[`detect/detect.go`](https://github.com/gitleaks/gitleaks/blob/v8.30.1/detect/detect.go),
[`sources/file.go`](https://github.com/gitleaks/gitleaks/blob/v8.30.1/sources/file.go),
[`sources/common.go`](https://github.com/gitleaks/gitleaks/blob/v8.30.1/sources/common.go),
and [`report/finding.go`](https://github.com/gitleaks/gitleaks/blob/v8.30.1/report/finding.go).
It does not emulate Go regular expressions or infer secret capture groups.

- `StartLine`/`EndLine` and byte columns are positive integers (not booleans).
  `EndColumn` is inclusive. Columns count **bytes, not Unicode characters**.
  Importantly, the pinned implementation measures subsequent-line columns from
  the preceding **LF byte index**, not the byte after LF; the first content byte
  on such a line is column 2. First-line columns start at 1.
- By default, only strict UTF-8 regular-file content smaller than the pinned
  100,000-byte fragment buffer is mapped, with LF or CRLF (including mixed LF/CRLF).
  The private helper also accepts caller-verified acquisition provenance through
  the mutually exclusive keywords `unfragmented=True` or
  `source_window=(byte_origin, byte_end)`. These are caller-only inputs, never
  report-controlled fields or inferred from stock Gitleaks coordinates.
  Unfragmented provenance establishes that the complete acquired input was one
  detector invocation; a window identifies that invocation's exact half-open byte
  interval in the original source. Windows convert reported global LF line numbers
  to local lines and retain fragment-local byte-column origins.
  No NUL, lone CR, split UTF-8 code points, archive-member paths, commit/symlink
  source metadata or non-null `Fragment` metadata is supported. A span is limited
  to 65,536 bytes and a line-number difference of at most 100. Endpoints must be
  inside content, not line terminators; intervening LF/CRLF bytes are preserved.
  Selected input remains bounded by `DEFAULT_MAX_TEXT_BYTES` (64 MiB).
- Single-line spans may end on an unterminated final line. Multi-line spans
  ending on that line are unsupported: the pinned location implementation does
  not produce a usable end column in that case. Missing/malformed coordinates,
  large/chunked files without caller-verified provenance and other
  versions/encodings remain explicitly unsupported, not guessed or converted
  through character indexes.
- Without caller-verified provenance, at **100,000 bytes inclusive**, mapping
  returns `unsupported_fragment_origin`, including when the file also has malformed
  encoding. Below that threshold,
  NUL, lone CR and invalid UTF-8 retain `unsupported_source_encoding_or_size`.
  This is a conservative origin guard, not a claim that every file at the
  threshold was split: the pinned reader can extend its buffer by up to 25,000
  bytes looking for a blank-line boundary.
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

#### Why stock large-file coordinates alone remain unsupported

Stock v8.30.1 reports omit the actual observed fragment's byte interval.
The reader accumulates LF counts into `Fragment.StartLine`; `DetectContext` adds
that line offset to local finding lines but preserves fragment-local columns.
A later fragment beginning immediately after LF measures its
first content byte from local offset zero (column 1); a whole-file interpretation
of that same line measures from the preceding LF (column 2). Merely applying the
reported global line therefore produces a one-byte error on that fragment's
first line. CRLF and preceding multi-byte Unicode do not remove this mismatch.

Without a blank-line boundary, successive fragments can begin midline without
increasing the accumulated line number. Buffered reads can be shorter than
100,000 bytes; the default buffer plus lookahead is not a fixed chunk stride.
Distinct global byte intervals, even containing different bytes, can then have
identical reported line/column coordinates and identical redacted payloads.
The synthetic regressions use explicitly known fragments/windows as local mapping
oracles, including caller-verified unfragmented large input and explicit windows.
The corresponding complete large stock inputs without provenance remain rejected.
They are negative demonstrations, **not**
a fragment-origin producer or semantic origin/use proof. Searching for matching
text, guessing chunk boundaries or hashing the report cannot resolve this
missing provenance.

Any future producer-bound fragment contract must retain at acquisition the
**actual observed** half-open byte interval in the exact measured file, its raw
bytes/encoding and local coordinate basis (including the starting line and preceding-LF convention),
and link each scanner observation to that interval and the exact file identity,
complete report, run namespace, selection, configuration and pinned toolchain.
It must preserve every observation, validate interval bounds and byte consistency,
handle transformation/nested-source limitations explicitly, and fail closed on
missing, stale or ambiguous associations. Digest agreement establishes byte
consistency, not authentic origin: an execution-bound producer must actually
observe and bind scanner input to output. Even authentic fragment provenance
would locate a reported Match, not establish Secret recovery or harmlessness.

An explicit **full-file pinned-library adapter** could pass one measured file as
one detector fragment and retain its actual origin at acquisition, binding every
observation privately to that input/output for each detector invocation, subject
to resource, UTF-8, coordinate and transformation limits. A digest alone would
establish neither authentic origin nor semantic origin/use proof.
That would be a distinct scan mode,
requiring its own measured producer, configuration/tool bindings and compatibility
validation; it cannot relabel observations from an earlier stock `dir` scan.
A wrapper replaying CLI slices, even overlapping ones, instead changes the
detector's context, anchors and fragment boundaries. Arbitrary regex rules can
span multiple lines or require unbounded context, so **no universal finite
overlap guarantees completeness** or equivalence. Such replay must never silently
replace the original directory scan, infer its fragment origins, or deduplicate
scanner observations. Neither approach is implemented by this diagnostic change;
the strict size guard and all acceptance rules remain intact.

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
