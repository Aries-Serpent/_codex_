# Data Determinism

Goals:
- Stable splits & shuffles (seeded RNG).
- Canonical serialization for hashes/digests.
- Logged lineage (dataset id, version, transform params).

Checklist:
- Seed all RNGs early.
- Avoid non-deterministic ops or guard with flags.
