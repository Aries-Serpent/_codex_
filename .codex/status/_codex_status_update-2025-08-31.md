# Status Update - 2025-08-31

## Completed
- Extended `apply_lora` to merge defaults with provided configuration and keyword overrides.
- Added coverage enforcement to `noxfile.py` and refreshed basic CLI and adapter tests.
- Logged Python environment to `.codex/inventory.txt` for reproducibility.

## Deferred
See [`.codex/deferred_items.md`](.codex/deferred_items.md) for postponed tasks.

## Open Questions
- Should the LoRA helper expose per-layer rank scaling?
- Are additional CLI commands needed for codex-ml workflows?
