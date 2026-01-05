# Tiered Cache Strategy for Python Dependencies

This composite action provides a **three-tier caching system** for Python pip packages across all workflows, optimizing for different usage patterns and retention needs.

## Cache Tiers

### 🟢 LIVE Tier (Permanent, High Priority)
- **Use for**: Critical workflows that run frequently (CI, tests, deployment)
- **Retention**: Permanent (or GitHub's maximum retention)
- **Examples**: 
  - `audit-improvement-pipeline.yml`
  - `code-quality.yml`
  - `security-suite.yml`
  - `pr-checks.yml`
- **Key prefix**: `live-pip-`

### 🟡 COMMON Tier (7-day Retention)
- **Use for**: Regular workflows that run periodically
- **Retention**: ~7 days (automatically pruned when unused)
- **Examples**: 
  - `scheduled-dependency-audit.yml`
  - `monthly-model-retraining.yml`
  - `wiki-assemble.yml`
- **Key prefix**: `common-pip-`

### 🔴 EPHEMERAL Tier (1-day Retention)
- **Use for**: One-off workflows, experiments, testing
- **Retention**: ~1 day (frequently deleted)
- **Examples**: 
  - Development/debug workflows
  - Experimental feature workflows
  - One-time migration scripts
- **Key prefix**: `ephemeral-pip-`

## Usage

### Basic Usage
```yaml
- name: Setup Python with Tiered Cache
  uses: ./.github/actions/setup-python-cached
  with:
    python-version: '3.11'
    cache-tier: 'live'  # or 'common' or 'ephemeral'
```

### Complete Example
```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      
      - name: Setup Python with Live Cache
        uses: ./.github/actions/setup-python-cached
        with:
          python-version: '3.11'
          cache-tier: 'live'
          architecture: 'x64'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -e .
```

## Cache Key Structure

The action creates cache keys in this format:
```
{tier}-pip-{os}-py{major.minor}-{deps_hash}
```

Examples:
- `live-pip-Linux-py3.11-a1b2c3d4e5f6`
- `common-pip-Linux-py3.11-a1b2c3d4e5f6`
- `ephemeral-pip-Linux-py3.12-x9y8z7w6v5u4`

## Cache Fallback Strategy

The action implements intelligent fallback:

1. **Try exact match** in the specified tier
2. **Fallback to LIVE tier** (same Python version, any deps)
3. **Fallback to COMMON tier** (same Python version, any deps)

This ensures workflows always get some cache benefit, even if their specific cache is missing.

## Benefits

### Performance
- **Shared cache** reduces redundant downloads across workflows
- **Tiered strategy** optimizes cache storage for different access patterns
- **Smart fallback** ensures cache hits even when exact match fails

### Cost Optimization
- **Live tier** keeps frequently-used packages cached permanently
- **Common tier** auto-prunes less-used packages after 7 days
- **Ephemeral tier** quickly deletes temporary caches

### Maintainability
- **Centralized** cache management in one composite action
- **Self-documenting** tier names make usage patterns clear
- **Automatic** cache key generation based on dependencies

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `python-version` | Python version to use | No | `'3.11'` |
| `cache-tier` | Cache tier: `live`, `common`, or `ephemeral` | No | `'common'` |
| `architecture` | Python architecture: `x64`, `x86`, `arm64` | No | `'x64'` |

## Outputs

| Output | Description |
|--------|-------------|
| `python-version` | The installed Python version |
| `cache-hit` | Whether the cache was hit (`'true'` or `'false'`) |

## Cache Warming

A dedicated `cache-warmup.yml` workflow runs daily to pre-populate the LIVE tier cache with common dependencies, ensuring fast CI runs.

## Monitoring

Each workflow run logs cache statistics:
- ✅ Cache HIT - confirms successful cache usage
- ⚠️  Cache MISS - indicates cache needs warming

## Migration Guide

### From setup-python with built-in cache:
```diff
- - name: Set up Python
-   uses: actions/setup-python@v6
-   with:
-     python-version: '3.11'
-     cache: 'pip'
-     cache-dependency-path: |
-       requirements*.txt
-       pyproject.toml

+ - name: Setup Python with Tiered Cache
+   uses: ./.github/actions/setup-python-cached
+   with:
+     python-version: '3.11'
+     cache-tier: 'live'
```

### From manual actions/cache:
```diff
- - uses: actions/setup-python@v6
-   with:
-     python-version: '3.11'
- 
- - uses: actions/cache@v4
-   with:
-     path: ~/.cache/pip
-     key: pip-${{ runner.os }}-${{ hashFiles('requirements*.txt') }}

+ - name: Setup Python with Tiered Cache
+   uses: ./.github/actions/setup-python-cached
+   with:
+     python-version: '3.11'
+     cache-tier: 'live'
```

## Troubleshooting

### Cache not hitting
1. Check if dependencies changed (new hash generated)
2. Verify the correct tier is specified
3. Run cache-warmup workflow manually to rebuild LIVE cache

### Cache size concerns
1. Move infrequently-used workflows to `common` or `ephemeral` tier
2. Let GitHub automatically prune unused caches
3. Use cache-cleanup workflow to manually prune old caches

## Related Files

- Action definition: `.github/actions/setup-python-cached/action.yml`
- Cache warmup workflow: `.github/workflows/cache-warmup.yml`
- Cache cleanup workflow: `.github/workflows/cache-cleanup.yml`
