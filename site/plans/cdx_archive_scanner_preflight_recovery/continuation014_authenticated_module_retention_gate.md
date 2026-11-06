# 014 — Pinned module origin authenticated; private retention still unavailable

Entry HEAD: `9c3523c052a8cf778503749d6859a0d08e928634`.
Preparation: `010e77ade6b0540933e224a014a7985d4e46e758`.
Historical implementation: `696244f97c4e4ca468e5df324b01d8ef645cbcea`.
Predecessor: [013](continuation013_exact_record_reconciliation.md).
Checkpoint011 SHA-256 verified:
`933156ffcb83c0ea8cf92e4fa2178d449bba158379c0258908b34c8f8879375a`.
No behavior changes or dependency changes were needed. Current implementation,
tests and Go manifests are unchanged against entry HEAD. The historical
implementation object is unavailable locally; no ancestry comparison is claimed.

## Completed independent work, not another assumed gate pass

The required read-only `security-review` specialist inspected the current Go/
Python adapter and common/preflight/review integration, extraction/packing
safeguards, documentation and tests. It reported no high-confidence vulnerability
in the reviewed changes. This bounded static analysis did not validate runtime
isolation or retention and is **not successful CodeQL**. The previously timed-out
tool was not retried. The required external security-service gate remains open;
neither this review nor test results waive it.

The pinned module was freshly downloaded from `proxy.golang.org` with Go's
signed `sum.golang.org` verification enabled, no bypasses or replacements.
The actual ZIP's independently recomputed Go directory hash matches `go.sum`:

- Module: `github.com/zricethezav/gitleaks/v8 v8.30.1`.
- Go checksum: `h1:PmEvCfVI7ti9dV3s5aMZUY7sS2GxRvG3yzih7E+cS3w=`.
- ZIP SHA-256: `4fd70631c0f6159e38fdb99ad126e3ba60d4212420062029d3dc5f510f6f2961`.
- Proxy-recorded origin: `8d1f98c7967eb1e79cb44ac6241a124e145d2165`.
- Official origin tree: `450acd30b88dbb845a5b067be4c73854ce7c68f1`.

All **450** ZIP file contents matched official origin Git blob hashes; **122**
recursive Git tree hashes were recomputed, including the root. This closes the
incomplete pinned-source acquisition question for the actual authenticated Go
module, without relying on an incomplete local archive or an unverified mirror.
The current official upstream tag instead resolves to
`83d9cd684c87d95d656c1458ef04895a7f1cbd8e`. This is a material provenance distinction,
not proof of maliciousness: equal version strings do not establish release/
library byte-origin equivalence. No tag migration, pin change or stock-origin
claim was made.

Go **1.25.0** was independently acquired as the official
`golang.org/toolchain@v0.0.1-go1.25.0.linux-amd64` distribution. The existing Go
1.24.13 bootstrap authenticated the fresh download through signed sumdb before
execution; actual ZIP directory hash was separately recomputed:
`h1:wVC9wx2XOcP5gHiN8ZzfyTfjlrDLSS7Hu1wjI01n68U=`.
ZIP SHA-256:
`891083c63e4d7a5020bdaa1911a9c5a1a966b993d9d3c1137d1727be04435e02`.
This is a usable authenticated official distribution for the performed synthetic
work. Independent `go.dev` release metadata was also retrieved, but a fresh direct
tar download still failed DNS for `dl.google.com`. **Direct tar verification did
not pass**; no claim of tar equivalence or external policy acceptance is made.
Any policy requiring that specific additional route still needs its owner.

Before scanner execution, fresh official GitHub release API asset digests and
the separate official checksum asset authenticated the Gitleaks **8.30.1**
Linux x64 archive:
`551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb`.
Official PyPI metadata authenticated the detect-secrets **1.5.0** wheel:
`e24e7b9b5a35048c313e983f76c4bd09dad89f045ff059e354f9943bf45aa060`.
Its RECORD hashes, **89** installed package files and launcher/interpreter binding
were checked. This does not freshly authenticate every Python transitive package.
No global packages, dependency pins or repository manifests were changed.

## Actual validation and retention decision

A dedicated `ci-testing-agent` validator ran the four existing focused Python
suites. Initial result was **243 passed, 5 skipped**, because the actual adapter
executable was not supplied. After supplying the authenticated task-built adapter
and verified stock scanners, the final run was **248 passed, zero failed/skipped**,
including five existing synthetic maintained integrations: **three equal and two
divergent** cases. These are fresh results, not borrowed checkpoint011 counts.
Two unknown asyncio-option warnings occurred with plugin autoload disabled.
Black/isort/Ruff/mypy/compilation checks passed. Go download/module verification,
build/vet and **four test functions with eight large-file cases** passed;
**202** modules had no replacements. Diff checks passed.

No owner-supplied approved durable private-retention mechanism was present in the
authorized task inputs. Bounded inspection stayed under
`/home/runner/work/_codex_/_codex_/.codex/tasks/issue5757`; no broad private search
or `/tmp` access occurred. Task-local public downloads, synthetic artifacts and
owner-only directory modes are not approved escrow, isolation or durable custody.
No synthetic artifact was promoted to real evidence.

**Concrete missing owner dependency:** the data owner must provide an explicitly
approved durable private store with trusted access identity, retention and cleanup
policy, and authority to restore a complete bound inventory or acquire a new exact
epoch. Runtime containment and source quiescence also require actual evidence.
No artificial policy flag or self-issued approval was created. Real-source scans,
measurement, private review and evidence retention were stopped before execution.
Current inventory, mapping/reconciliation and review counts remain **unavailable,
not zero**. Historical 16,533 entries / 124,233,523 bytes remain historical.

| Question | Reasoning and adversarial check | Selected action and verification | Residual constraint |
| --- | --- | --- | --- |
| Is the pinned source archive complete/authenticated? | Version labels and partial archives are insufficient | Verify signed module sum, actual ZIP contents and official origin Git objects | Current tag is a distinct commit |
| Can the toolchain execute safely for synthetic validation? | Do not execute an unverified download | Authenticate official toolchain module first; independently recompute ZIP hash | Direct tar route failed; no containment claim |
| Can local modes establish retention approval? | Same-user access and session survival do not confer owner authority | No approval inferred; stop real-source work | Data-owner durable-store contract absent |
| Can an alternate review close CodeQL? | A bounded reviewer cannot manufacture service completion | Report actual review and retain incomplete external gate | Security owner must supply authorized service result |

Preexisting dirty startup metadata was inspected, secret-scanned and captured
unchanged by the required preparation publisher. Its SHA-256 remains
`c1c6d89a17fcf1b4d8ddf73db0a8e84ce58cc20534cd772cd94fe46f8c0588d8`.
Historical checkpoints and archive bytes were preserved. Only sanitized aggregates
are persisted; task-owned downloads/caches and synthetic artifacts are removed
before publication, not treated as durable private evidence.

### Next Iteration Follow-Up Prompt for Copilot Cloud Agent

```markdown
Continue in /home/runner/work/_codex_/_codex_ using absolute paths. Read actual
HEAD/status, current agency policy, .github/AGENTS.md, scripts/AGENTS.md, applicable
instructions, this continuation, checkpoint-012.json, checkpoint-011.json,
scripts/archive/CDX_SQLITE.md and the 002/003 contracts. Never read .github/agents/.
Preserve all dirty bytes. Verify checkpoint digests and actual introducing footer.

Do not rebuild implemented reconciliation or repeat successful provenance work
as a plan-only substitute. Retain the authenticated module origin8d1f98c... and
distinct current upstream tag83d9cd...; version equality is not byte-origin proof.
Reacquire and freshly authenticate tools before any later execution; local caches
were intentionally not retained as operational evidence. Direct Go tar verification
remains incomplete; obtain owner acceptance of the authenticated official module
route or a genuinely verified required direct distribution, never a fabricated pass.

Complete the actual required external security-service gate in an authorized
environment WITHOUT retrying the timed-out codeql tool. The bounded specialist
analysis is not CodeQL success or a waiver. For further explicit vulnerability
investigation invoke the security-review specialist before direct investigation.

The next dependency-ready operational task requires the data owner's approved
durable private store, access identity, retention/cleanup rules and restore/new-epoch
authority, plus trusted runtime containment and quiescent exact source. No such
owner mechanism was supplied. If still absent, stop real-source scanning and
private evidence acquisition, name that exact dependency and continue only safe
independent work supported by new evidence; do not invent approval flags or escrow.

Only when all actual gates hold evaluate the authorized exact real-source epoch,
with complete current measured bindings and retained inventory. Preserve raw
multisets, duplicate ambiguity, missing/extra records and independent stock gates.
Exact-record association is not stock byte origin, use, harmlessness or approval.
No finding approval, packing, PR, merge, workflow/settings mutation or deployment
is authorized. Future packing needs separate authorization and maintained
independent stock rescan/dispositions/SQLite integrity/byte/Merkle checks.

If implementation becomes necessary, challenge/review the actual change, use
apply_patch, report_progress before the first edit, secret-scan before commits,
and use a dedicated custom validator with synthetic fixtures. Do not retry CodeQL.
Persist the next unused checkpoint and continuation015 with INDEX and the two-step
actual introducing-SHA footer. Report final HEAD, actual implementation changes,
checkpoint digest/status, current versus historical counts and remaining owners.
Keep this fenced follow-up chain until an actually authorized archive is created
and verified. Never publish raw reports, source lines, matches, keys or run refs.
```

## Commit provenance

The actual introducing commit and checkpoint012 digest are appended after first
publication in a separate metadata commit, not guessed in this creation body.
