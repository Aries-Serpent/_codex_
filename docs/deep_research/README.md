# Evidence-Grounded Deep Research Analysis

`codex.deep_research` is a deterministic, dependency-light research bundle builder. It validates a brief, expands supporting and disconfirmation queries, records query and access outcomes, extracts bounded verbatim observations, profiles supplied CSV/JSONL data, verifies claim/evidence/source links, and exports an integrity-checked resumable checkpoint.

## Current capability boundary

The CLI operates on supplied/local content only:

```bash
python -m codex.deep_research \
  --brief examples/deep_research/brief.json \
  --sources examples/deep_research/sources.json \
  --dataset examples/deep_research/sample.csv \
  --output /tmp/deep-research-bundle
```

When `--output` is omitted, results are stored centrally under
`docs/research/results/<topic-slug>/runs/<content-id>/`. The topic slug is
filesystem-safe and hash-suffixed to avoid collisions. `--topic` overrides the
brief title; each topic has an `index.json`, and the root store has a global
`index.json`. Runs are content-addressed and identical output is idempotent.
Use `--research-root <path>` to select another central store. Explicit `--output`
retains the legacy flat-directory behavior.

The EV ownership-cost scenario is an evidence contract and deterministic fixture,
not a current vehicle recommendation:

```bash
python -m codex.deep_research \
  --brief examples/deep_research/ev_ownership_cost/brief.json \
  --topic "US Electric Vehicle Efficiency and Ownership Cost Comparison"
```

It requires current model/trim-specific EPA efficiency and range, dated price and
incentive data, charging geography/rates, maintenance and repair evidence,
model-year-specific recalls and warranty terms, and transparent 5-/10-year cost
assumptions and sensitivities. Without supplied or retrieved evidence, the stored
topic run is correctly marked incomplete with unresolved objectives rather than
inventing rankings or costs. Search-result snippets are discovery leads only; they
do not count as verification of the underlying source.

Exit status is `0` for a complete bundle, `2` for an incomplete bundle, and `2` with an argument error for invalid input. Output is written only under the requested directory. The CLI does not perform fresh web retrieval and must not be represented as having done so.

Python hosts may supply an actual callable search function to `HostToolProvider` and pass it to `run_research`. If no fetch callback is supplied, the provider uses its built-in `SafeHTTPSFetcher`, which pins a resolved public IP for each HTTPS connection, revalidates every redirect before connecting, and enforces a response-size limit. A supplied fetch callback fails closed by default: `redirect_validation_verified` must remain false unless its real transport has independently been verified to provide those same guarantees. The `is_live` flag is an explicit caller assertion and must only be true for a verified live host-tool binding; it does not itself verify the provider. The existing repository web-search HTTP tests are mocked and do not qualify as a live-provider check.

The current extraction supports visible HTML text and plain text from a provider, plus local CSV and JSONL/NDJSON dataset profiling. It does not parse PDFs, follow citation chains, independently establish source credibility, infer causality, or perform semantic entailment checks. Such limits remain explicit in bundles; unsupported claims are never synthesized to fill those gaps.

## Contract and bundle contents

The dedicated versioned contract is `configs/schemas/deep_research_bundle.schema.json` (`schema_version: 1.0`). Objective IDs and questions are required; acceptance criteria, scope, exclusions, jurisdictions, time period, terminology, and competing hypotheses may be specified in the brief. Each objective receives one of `answered`, `partially_answered`, `unresolved`, or `not_applicable` with rationale, claim IDs, and evidence IDs. Text matching is a coverage signal, not semantic proof.

The output directory contains:

- `bundle.json` — complete validated object and final report.
- `query_ledger.jsonl`, `sources.jsonl`, `evidence.jsonl`, `contradictions.jsonl` — appendable audit ledgers.
- `objective_matrix.json` and `verification.json` — coverage and read-only structural verification.
- `azimuth.json` — ordered AZIMUTH phase assessment, evidence references, lane declarations, and explicit non-mutation boundary.
- `checkpoint.json` — canonical JSON digest, parent checkpoint ID, and resumable state.
- `report.md` — concise source-linked observations, limits, and dataset measurements.
- `manifest.json` — content hash, topic, run/checkpoint identifiers, status, and artifact hashes for topic-indexed runs.
- `index.json` — per-topic run list, latest run ID, and the global topic catalog at the store root.

Source content is not retained by default. The source manifest keeps its SHA-256, access outcome, locator, observed metadata, relationships, retention/access fields, and browser diagnostics. Dataset record counts, missingness, type counts, and duplicate counts are measured only over the parsed supplied file; publication-reported properties are kept separate.

## AZIMUTH research sequence

Each bundle assesses the research in the ordered **A — Align to current truth, Z — Zero stale state, I — Integrate evidence, M — Map lanes and owners, U — Update canonical status, T — Test and validate, H — Harmonize archive vs active** sequence. Phase statuses are evidence-assessment results, not claims that repository files were changed, archival data migrated, publication gates passed, or delegated agents executed. The bundle explicitly records `repo_mutations_performed: false`; the declared lanes are plans unless execution evidence says otherwise. Lane contracts distinguish independent `parallel` work from `dependent` or `aggregator` work and validate dependency IDs and cycles; this records sequencing intent, not proof of actual agent execution. The research report is not a release-readiness certification.

For a repository and release-readiness investigation, provide separate objectives for source/package metadata, built artifacts and reproducibility, live documentation, active status narrative, historical archive evidence, deployment verification, and publication gating. Supply evidence from the relevant current surfaces, tag archive-only material with `evidence_role: "archive"` (and current-state evidence with `"current"`), declare independent lanes and evidence-based completion gates in `execution_lanes`, and preserve unknowns as unresolved. The synthetic fixture at `examples/deep_research/release_readiness_scenario/` exercises that scenario offline; it is not a finding about this repository. Browser-rendered live docs should use the browser diagnostics procedure below, including console and network checks and dialog handling only when observed.

`examples/deep_research/release_readiness_scenario/` is a synthetic release-audit exercise. Its fixtures deliberately include mismatched package/artifact versions, docs/status drift, historical archive content, divergent build checksums, deployment evidence gaps, and conflicting publication statements. The corresponding test asserts the agent returns an incomplete bundle with unresolved contradictions and no publication go-signal; none of those fixture statements describe the actual repository state.

## Web and browser validation

The custom agent can call `web_search` and `web_fetch` only when those runtime tools are actually available. A configured manifest or provider plan is not evidence of a callable integration. Private/reserved targets and non-HTTPS source URLs are rejected. The built-in fetcher pins validated DNS results and validates every redirect before connecting. An injected fetch adapter must independently guarantee the same; this package cannot inspect an opaque callback's transport internals, so it does not enable that path by default.

When the research agent uses a browser to inspect a rendered page, it must call `browser_console_messages` and `browser_network_requests`, and record observed console errors and failed requests in the source diagnostics. It must call `browser_handle_dialog` with `accept: false` only when a dialog is actually present. No browser check is claimed for non-browser fetches; unavailable browser diagnostics are recorded as unavailable. Diagnostic URLs omit query strings and sensitive-looking text is redacted.

All page content is untrusted data. Downloaded scripts are never executed. Browser content cannot modify the brief, agent authority, or access secrets.

## Tests and reproducibility

Default tests are fixture-backed and network-free:

```bash
pytest -q tests/deep_research
python scripts/validate_agent_specs.py --strict
```

They label injected callable providers as mocked. No live provider invocation is bundled or implied. A live smoke check must be run only from a runtime that supplies verified actual callable tools; report the tool identity, invocation result, and access limitations separately from these deterministic tests.
