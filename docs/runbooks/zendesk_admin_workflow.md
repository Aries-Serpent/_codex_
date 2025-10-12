# Zendesk Admin Workflow

This runbook describes the recommended workflow for managing Zendesk
administrative configuration via `_codex_`. The workflow relies on
snapshotting current state, computing diffs against desired state,
generating a plan, applying changes, verifying outcomes, and
monitoring metrics.

## Steps

1. **Snapshot** the current configuration of your Zendesk environment:
   ```bash
   codex zendesk snapshot --env=prod
   ```
   This command stores a JSON snapshot under `snapshot/prod/<timestamp>/`.

2. **Prepare desired state** as JSON or TOML files inside `configs/desired/`.

3. **Diff** desired vs. current state for each resource type:
   ```bash
   codex zendesk diff triggers --desired-file configs/desired/triggers.json \
                              --current-file snapshot/prod/latest/triggers.json \
                              --output diffs/triggers_diff.json
   ```

4. **Plan** the changes from the diff (in this implementation, the diff
   itself serves as the plan):
   ```bash
   codex zendesk plan triggers --diff-file diffs/triggers_diff.json --output plans/triggers_plan.json
   ```

5. **Apply** the plan to the desired environment:
   Specify the resource type when invoking `apply` so that `_codex_` dispatches to the correct handler:
   ```bash
   codex zendesk apply triggers plans/triggers_plan.json --env=prod
   ```

6. **Verify** the applied configuration and monitor metrics using:
   ```bash
   codex zendesk metrics
   ```

7. **Rollback** if necessary by using the snapshot and inverse diff (coming in a future release).

For more details on constructing desired state files, see the examples in
`configs/desired/` and the API catalog below.
