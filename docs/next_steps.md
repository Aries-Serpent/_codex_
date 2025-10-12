# Next Steps for Zendesk Integration

This document outlines future work items after completing the initial
implementation of the Zendesk configuration-as-code framework.

1. **Implement adapters** for each resource type using the API catalog. These
   clients should handle authentication, pagination, rate-limiting, and
   idempotent creation/update of resources.
2. **Add apply logic** to the CLI. Currently, the `apply` command is a
   placeholder; it needs to read plan files, call the appropriate
   adapters, and update monitoring counters accordingly.
3. **Introduce rollback** functionality by generating inverse operations for
   each applied change and storing them alongside snapshots.
4. **Integrate with existing monitoring framework** to record metric values in
   a persistent store and expose dashboards.
5. **Expand tests** to include integration tests with a mock Zendesk API
   server and contract tests for each adapter.
6. **Enhance CLI UX**: add interactive prompts, dry-run mode, and
   human-readable summaries of diffs/plans.
7. **Document security considerations** such as secret management, scope
   permissions, and audit trails.
