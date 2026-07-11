# Data Determinism
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Last Updated: 2026-06-22

Goals:
- Stable splits & shuffles (seeded RNG).
- Canonical serialization for hashes/digests.
- Logged lineage (dataset id, version, transform params).

Checklist:
- Seed all RNGs early.
- Avoid non-deterministic ops or guard with flags.
