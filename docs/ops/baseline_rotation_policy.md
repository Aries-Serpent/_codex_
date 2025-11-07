# Baseline Rotation Policy

> **Purpose**: Define retention and archival process for audit baselines to prevent repository growth.

## Storage Location

- **Active baselines**: `audit_artifacts/baselines/`
- **Archive**: Separate archive branch or Git LFS (if size concerns arise)

## Retention Rules

| Baseline Type | Keep Count | Rotation Strategy |
|---------------|------------|-------------------|
| Main branch | Last 10 | Archive older baselines to archive branch |
| Release tags | All | Keep indefinitely (tagged baselines) |
| PR baselines | Last 3 | Auto-delete on PR merge/close |

## Rotation Process

### Manual Rotation (Current)

When baselines exceed retention limits:

```bash
# List baselines by date
ls -lt audit_artifacts/baselines/

# Move old baselines to archive directory
mkdir -p audit_artifacts/baselines/archive
mv audit_artifacts/baselines/baseline_*.json audit_artifacts/baselines/archive/

# Commit rotation
git add audit_artifacts/baselines/
git commit -m "chore: rotate old baselines to archive"
```

### Automated Rotation (Future)

A rotation script will be added in a future PR to automate this process:

```bash
# Future command
python scripts/baseline_rotation.py --keep 10 --archive
```

## Size Monitoring

Monitor repository size impact:

```bash
# Check baseline directory size
du -sh audit_artifacts/baselines/

# Check total repo size
git count-objects -vH
```

## Archive Strategy

If baseline storage impacts repository performance:

1. **Git LFS**: Move baselines to Git LFS for large file handling
2. **Archive Branch**: Create `baselines-archive` branch for historical baselines
3. **External Storage**: Store in artifact management system (e.g., Artifactory)

## Baseline Naming Convention

```text
baseline_<branch>_<timestamp>_<short-sha>.json
```
Example:
```text
baseline_main_20251106_3a59994.json
baseline_pr2123_20251106_91fe32d.json
```
## Notes

- Baselines are deterministic and should produce identical SHAs when regenerated
- Keep at least one baseline per release for regression testing
- PR baselines are temporary and cleaned up post-merge
- Tagged releases maintain baselines indefinitely for compliance
