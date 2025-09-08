# Deferred Items

- Advanced RL support: implementing RL agents and reward models is complex and not required for initial production. Minimal plan: finish scaffolding and add a trivial reward model for testing.
- Full multi-node distributed training: single-node multi-GPU is sufficient now; multi-node support deferred until needed. Deepspeed/FSDP integration remains out of scope.
- Comprehensive secret scanning integration: third-party tools (e.g., trufflehog, gitleaks) will be evaluated in a future security audit to avoid false positives.
- Notebook auto-generation: interactive notebooks may be useful but are not critical; manual examples will be provided first.
