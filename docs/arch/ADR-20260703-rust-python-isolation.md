# ADR: Rust-Python Environment Isolation
**Last Updated:** 2026-07-11
**Version:** v0.2.0

## Context
CI success rates dropped to 26.7%, partially due to environment pollution between Rust and Python toolchains in mixed jobs.

## Decision
We are separating Rust and Python dependencies, caches, and build layers. 
- Python environments will use `actions/setup-python` with strict virtualenv usage.
- Rust environments will use `actions-rust-lang/setup-rust-toolchain`.
- Cross-language workflows (if any) will build Rust artifacts first, then load them into the Python environment as a distinct step, preventing shared memory/path pollution.

## Consequences
- Better cache hit rates (isolated layers).
- Reduced CI failures from conflicting dependencies.
- Clearer debugging when either language ecosystem fails.
