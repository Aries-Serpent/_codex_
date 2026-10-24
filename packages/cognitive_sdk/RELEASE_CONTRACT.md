# `codex-cognitive-sdk` Release Contract (MVP Distribution)

This document declares the focused Python MVP distribution contract for the
Cognitive Brain runtime. It is the acceptance baseline for what ships as the
first Python artifact and what explicitly does not. The decision itself is
recorded in `docs/architecture/COGNITIVE_BRAIN_PACKAGE_BOUNDARY.md` and is
not reopened here.

## Decision (locked)

The MVP distribution is the **Python control plane on the
`codex-cognitive-sdk` contracts**. The Rust extension (`codex_swarm`) is a
separate, optional, separately-versioned wheel and is **not** part of this
distribution. The repository root `pyproject.toml` uses
`setuptools.build_meta` and intentionally does **not** build the Rust
extension; `[tool.maturin]` there configures only the optional
`codex_swarm` wheel.

## Distribution identity

| Field | Value |
|---|---|
| Distribution name | `codex-cognitive-sdk` |
| Import package | `codex_cognitive_sdk` |
| Build backend | `hatchling` (pinned `hatchling==1.32.0`) |
| Version source | `src/codex_cognitive_sdk/__about__.py` (`__version__`) |
| Python support | `>=3.12,<3.13` (CPython) |
| Runtime dependencies | **Zero** — stdlib only |
| Wheel contents | `src/codex_cognitive_sdk` only (contracts + `py.typed`) |

## Scope of the contract

This wheel is the **contracts-only boundary** for the Cognitive Brain
runtime MVP. It carries the frozen, stdlib-only dataclass contracts that
producers and consumers serialize offline:

- **Evidence** (`codex_cognitive_sdk.evidence`): `ImprovementEvent`,
  `ImprovementResult`, `SignalEvidence`, `SignalSource`,
  `DataAvailability`, `PatternRef`, `PatchProposal`, `GateResult`,
  `ExecutionEnvironment`, `EVIDENCE_SCHEMA_VERSION`, `make_event_id`,
  `event_to_dict` / `event_from_dict`, `result_to_dict` /
  `result_from_dict`, plus the fail-closed validation errors.
- **OODA, governance, and memory protocols** (`codex_cognitive_sdk.ooda`,
  `.governance`, `.memory`) exposed through the package-root `_EXPORTS`.

Out of scope for this wheel: policy execution, authority envelopes, GitHub
interaction, and the Rust bounded executor (`codex_swarm`). Those remain in
the Python control plane / optional wheels and consume these contracts
across a stable seam.

## `codex_swarm` is separate and optional

`codex_swarm` ships as an optional, separately-versioned wheel once its
task/result contract is stable. Consumers of `codex-cognitive-sdk` must not
require `codex_swarm` at install or import time. The Rust executor never
makes policy decisions and never holds credentials; it only executes
bounded tasks described by these contracts.

## Acceptance gate (offline)

Every release candidate of this distribution must pass the following gate
**offline** — no index access, no network, no extra dependencies:

1. **Build** — `python -m build --wheel` produces a
   `codex_cognitive_sdk-<version>-py3-none-any.whl` from this directory.
2. **Install** — `pip install --no-deps --no-index --target <dir> <wheel>`
   installs into a clean target directory using only the locally built
   wheel.
3. **Import** — a clean interpreter (target dir prepended to `sys.path`,
   source tree not importable) can `import codex_cognitive_sdk` and read
   `__version__`.
4. **Functional** — that same interpreter can construct a minimal
   `ImprovementEvent` with `schema_version=EVIDENCE_SCHEMA_VERSION`, pass
   `event.validate()`, and round-trip:
   `event_from_dict(event_to_dict(event)) == event`.

The gate is automated by `tests/test_wheel_functional.py`, which builds,
installs, and exercises the wheel in a subprocess. The test skips cleanly
(recording the reason) when `pip`, the `build` frontend, or the pinned
build backend cannot be provisioned offline; a skip must never mask a real
failure in an environment where those tools are present.

## Versioning

`EVIDENCE_SCHEMA_VERSION` (in `codex_cognitive_sdk.evidence`) is the schema
contract version and is bumped on any breaking change to the event/result
schema. The wheel `__version__` tracks the package release. They evolve
independently but a schema-major bump must be called out in the release
notes for the wheel that carries it.
