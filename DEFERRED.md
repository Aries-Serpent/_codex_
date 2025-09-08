# Deferred Items

Some features remain out of scope for the immediate patch cycle. These are noted with a rationale and suggested future plans:

* **Advanced RL support:** Implementing RL agents and reward models is complex and not required for initial production. Defer until a clear use case arises. Minimal plan: finish scaffolding and implement a trivial reward model for testing.
* **Full multi-node distributed training:** While single-node multi-GPU support is important, adding multi-node support requires significant engineering and may not be necessary for the current scale. Defer until model sizes demand it.
* **Comprehensive secret scanning integration:** Adding third-party secret scanning tools requires careful tuning to avoid false positives. Schedule for a later security audit.
* **Notebook auto-generation:** Automatically generating interactive notebooks (e.g., quick start) can be helpful but is not critical. Provide manual examples first.
