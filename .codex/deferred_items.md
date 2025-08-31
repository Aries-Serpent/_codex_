# Deferred Items

- **NDJSON metrics toggle**: Train loop currently always writes NDJSON; adding a Hydra-configurable flag would require broader refactor of configs and callbacks.
- **Advanced RLHF pipeline**: Out of scope for current maintenance; substantial engineering effort.
- **Comprehensive documentation updates**: Quickstart and tracking docs not written due to time constraints.
- **requirements.lock regeneration**: Existing lockfile retained; full pip-compile run omitted for speed.
