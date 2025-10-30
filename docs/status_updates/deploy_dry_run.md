# Deploy Dry-Run (2025-10-30, work)

```json
{
  "status": "validated",
  "dry_run_only": true,
  "rollout_ring": "0D_base_",
  "pod_ring": "0D_base_",
  "config": "configs/deploy/reasoning_pod.yaml",
  "image": {
    "repository": "local/offline/codex",
    "tag": "latest"
  },
  "resources": {
    "cpu": "2",
    "memory": "8Gi"
  },
  "notes": "Offline dry-run only; no infrastructure changes were made."
}
```
