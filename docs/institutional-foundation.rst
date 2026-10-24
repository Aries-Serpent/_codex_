Institutional foundation: inactive candidate slice
================================================

Scope and entry points
----------------------

``codex-institutional`` (or ``python -m codex.institutional``) is an additive,
offline CLI in ``codex-ml``. The existing ``codex`` ML entry point is unchanged.
This slice inventories paths, records an explicitly limited assessment and
deterministic challenge, preserves a Draft experience, and checkpoints an inactive
candidate. It does not evaluate agent effectiveness, authenticate identities,
approve proposals, activate governance, retire agents, execute imported commands,
or modify the underlying model.

Newcomer path, in a disposable target directory::

    codex-institutional inventory --root /absolute/target
    codex-institutional candidate --root /absolute/target --session trial
    codex-institutional candidate --root /absolute/target --session trial --write
    codex-institutional verify --root /absolute/target --input /absolute/target/.codex/institutional/checkpoint.json
    codex-institutional challenge --input /absolute/target/.codex/institutional/checkpoint.json
    codex-institutional disengage --root /absolute/target

``candidate`` without ``--write`` outputs the record and deterministic mutation
preview to stdout; it creates nothing. Paths, candidate digest, predecessor,
installation provenance, lifecycle and authority boundary are in the preview.
Apply rechecks the same preview, source and contracts and uses a nonblocking
OS lock. Python callers may explicitly separate ``storage.plan`` and
``storage.apply``. Filesystem targets need no Git metadata. Git census inventories
the recorded committed tree; dirty tracked bytes have a separate digest.
Untracked Git files are outside that census. Profile contents are not read.

Contracts and compatibility
---------------------------

The one validation dialect is JSON Schema Draft 2020-12, using ``jsonschema`` and
installed ``contracts.json`` through ``importlib.resources``. Envelope constraints
and identity/integrity, census reconciliation and cross-record checks are enforced
locally by the runtime. No remote schema references or network clients are used.
Schema resource bytes are configuration-bound in continuation records.

Implemented: ``codex.agent-role.v1``, ``codex.inventory.v1``,
``codex.trust-evidence.v1``, ``codex.audit-finding.v1``,
``codex.experience.v1``, ``codex.continuation-state.v1``.
The ``.v1`` suffix is the wire schema/version; it is independent of the
``codex-ml`` package version. This implementation supports only these versions.
The program's decision, dissent, institution, amendment, knowledge-lifecycle and
capability-package contracts remain unsupported. Dissent and alternatives are
preserved inside experience, not represented as implemented standalone contracts.
Authority diagnostics are a denial-only envelope, not an approval protocol.

Unknown envelope/payload fields are rejected; ``extensions`` is the explicit
inert extension container. Inspection never rewrites inputs. Checkpoint rewrites
must retain envelope extensions and preserve the complete predecessor separately.
All supported records are Draft candidates; every other lifecycle state is
rejected. ``migrate`` and ``downgrade`` return unsupported without writing.
Unsupported nested records are reported individually, other records are still
inspected, and the candidate cannot be persisted/exported as operational input.
No conversion, automatic version adoption or downgrade exists.

Canonical JSON is ASCII, sorted keys, compact separators and no NaN. Arrays have
stable order. The clock is injectable and must be timezone-aware; timestamps use
UTC Z seconds. Determinism assumes the same source, root identity, configuration,
package version and clock. Component defaults in inventory are inherited by every
entry; they are explicit unknowns, not observations. Primary classes are exclusive,
ordered by ``core.classify``. Tags are separate. Counts cover every census path;
``metadata_only`` is not semantic coverage. Git object references bind entries to
committed blobs without interpreting their contents; filesystem entries hash bytes.
Metadata-based inventory intentionally does not infer zero usage or recommend retirement.

Record identity is ``schema + ':' + SHA256(canonical(payload))``. Evidence payload
includes source identity/location, source SHA, content digest and collection method.
Collection timestamps and producer claims are outside evidence identity, so
recollection yields a new envelope event with the same evidence ID. Checkpoint
history retains earlier envelopes. Changed evidence can reference predecessor IDs.
Record integrity excludes only its own ``integrity`` field; candidate binding
hashes the complete inventory record, excluding no inventory fields. Approval
claims are not part of that inventory and cannot create self-authorizing hashes.

Hashes detect divergence against a trusted reference. They do not authenticate
producers, make data immutable, authorize execution, encrypt information, guarantee
availability or detect coordinated replacement of both data and untrusted digests.
All producer identities are explicitly unverified. Replacing a record and its
digest never establishes approval.

Authority, challenge and results
-------------------------------

Architect and Auditor role records map to existing runtime candidate construction
and structural inspection, not new persistent agents. Both may be exercised by the
same implementer and confer no authority. Existing research storage, authority and
script checkpoint mechanisms were compared in the inactive ADR
``docs/adr/institutional-foundation-001.json``.

``challenge`` performs deterministic schema, integrity, identity, reference,
required-record and candidate-binding checks, not semantic adversarial review.
``verify`` additionally checks target/source/configuration drift. ``assess`` consumes
an inventory and reports the evidence-supported unknowns, not synthetic scores.
Implementation self-tests and implementation review do not satisfy independent
reproduction or final approval. Activation always denies, including when records
assert distinct actors, approval, non-expiry or trusted status. Denial diagnostics
include operation/target/artifact mismatch, missing/colliding actors, revocation and
unverified expiry. Trusted identity verification, authenticated expiration checks
and real approval binding are unsupported, not simulated.

Target separation before future material activation is proposer != material
implementer != independent verifier != final approver. The compensating control
for disclosed overlap in this slice is complete non-activation. Integrating a real
authority provider and applicable independent human approval is a later cycle.
The requested governance YAML paths are absent in the source checkout; this patch
does not create or adopt a constitution or alter existing policy.

Exit codes and precedence:

* 0: declared execution/inspection scope completed; unknowns do not imply acceptance.
* 2: validation findings/malformed argparse invocation.
* 3: authority/disclosure denied.
* 4: resource blocking.
* 5: malformed records, unsafe inputs or required arguments.
* 6: unsupported schema/transition/platform locking.
* 7: prohibited mutation, collision, stale preview or concurrent modification.
* 8: I/O or interrupted execution; preserve last valid state and partial outputs.
* 9: unresolved required review evidence under ``--strict``.

Parsing/loading fails before command-specific checks. Validation findings take
precedence over strict missing-review status. Structural checks preserve all
findings; denial diagnostics preserve all known reasons. Operational activation
is denied regardless of other successful checks. ``--strict`` never reports
acceptance while semantic review/independent reproduction remain NOT_RUN.
Gate values embedded in a candidate are implementer work records, not independently
established acceptance. They may be inspected but are never authority inputs.

Persistence, recovery, disclosure and disengagement
--------------------------------------------------

Generated target state stays under ``.codex/institutional``. Installation provenance
and contract/version manifest are required to recognize existing state; names alone
do not establish ownership. This manifest is a local ownership claim, not signed
provenance or privilege. Unknown files, mismatching manifests, incompatible versions
and symlink namespaces block writes. Checkpoint mutation uses ``--previous`` and
``--expected`` (the canonical digest of the old record), plus the same session ID.
Sequence must increase by one and predecessor binding must match.

Continuation example::

    codex-institutional candidate --root /absolute/target --session trial --previous /absolute/target/.codex/institutional/checkpoint.json --expected OLD_CANONICAL_SHA256

Review the stdout preview before repeating with ``--write``. Prior evidence
references are linked on source changes. Changed artifacts invalidate previews.
Regenerate candidates after drift; never edit a hash to establish authority.

One checkpoint is atomically replaced after fsync, using a same-directory temporary
file and an OS lock; the previous checkpoint is retained first. This is not a
multi-file transaction, an authenticated audit log, or a guarantee against a
malicious same-user process racing filesystem changes. POSIX locking is required
for writes; read-only inspection remains portable. Parent directory fsync and
power-loss durability are not guaranteed. Initialization may leave a manifest-only
namespace; matching installation provenance permits retry. Unrecognized partial
initialization requires inspection, not adoption or deletion. Interrupted replacement
retains the old checkpoint and removes its temporary file; an earlier history copy
may remain. Never claim a failed save succeeded. CLI I/O failures report unsaved work;
inspect the last valid ``checkpoint.json`` before resuming.

Read-only imports accept plain JSON and gzip JSON, with a 64 MiB decompressed limit,
duplicate-key rejection and no executable hooks. Historical commands in extensions
remain inert. Filesystem inventory has a 50,000-path and 64 MiB content budget;
Git subprocesses have a 20-second timeout. These are slice bounds, not host telemetry
or a guarantee against arbitrary hostile filesystem growth. Resource denial is
not completion. Development builds and fixtures are separately placed under ``/tmp``.

``export`` requires an explicit new destination, ``--classification Public``, a
nonempty ``--basis`` and ``--assessor``; default is Unknown and denied. Only the
candidate and checksummed manifest are allowlisted. No artifact is silently omitted.
Repository-Internal/Restricted need a future recipient-authority implementation
and are currently denied; Secret/Prohibited-From-Export/Unknown are denied.
Classification is an explicit caller assertion, not a content-secrecy detector.
Never label repository records Public merely to bypass this check. Redaction and
compliant-subset derivation are unsupported; originals are never silently changed.
The manifest records IDs, schema, namespace, classification and lineage.
It is a checksum manifest, not a signature or approval. Export failure may leave
partial outputs, which must be preserved and inspected; no clobbering retry exists.

``disengage`` produces a non-destructive plan identifying manifest-claimed and
ambiguous namespace files, the shared parent, user-owned external paths, preserved
history and residuals. No integration is enabled, so no disablement is necessary.
It does not uninstall packages or erase audit history. Destructive removal is
unsupported and would require separate authority and preview.

Acceptance and continuation
---------------------------

The source safety suite is ``tests/institutional/test_foundation.py``. It is also
the external installed-wheel harness; this is implementer-owned evaluation, not
withheld or independent verification. Network sockets are denied during exercised
tests. The test claim covers exercised paths only, not universal resistance to
poisoning, deception, collusion or prompt injection.

Remaining prioritized adversarial work: conflicting valid decisions, compromised
trusted agents, stale trusted operational knowledge, minority findings later
confirmed, incompatible imported capabilities and institutional collusion.
These surfaces are not implemented. Maintain baseline assertions rather than
weakening safety to get a passing run. Keep source and wheel observations separate.
Next deterministic cycles and rollback/troubleshooting conventions are in the ADR.
No package publication, governance activation or program-completion claim is made.
