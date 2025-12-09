# Copilot Space Traversal Workflow (v1.4.0)

**Roles:** [Audit Orchestrator], [Capability Cartographer]  
**Energy:** 5  
**Version:** 1.4.0

> **NOTE:** For operational commands and usage examples, see `Usage_Guide.md`

## 1. Purpose

Deterministic audit pipeline: harvest → facet → extract → score → gap → render → manifest (integrity chain).

Provides a reproducible, explainable capability maturity assessment pipeline with deterministic outputs, ensuring transparency and allowing for precise tracking of codebase evolution.

## 2. Stages (S1–S7)

The audit pipeline consists of seven sequential stages, each producing a specific artifact:

| ID | Output | Action | Details |
|----|--------|--------|---------|
| S1 | `context_index.json` | Enumerate + hash file list (sorted) | Traverses repository, collects file metadata (path, extension, size, SHA256), sorted for determinism |
| S2 | `facets.json` | Regex domain clustering | Groups files by domain patterns (checkpoint, token, train, eval, data, safety, logging, config) |
| S3 | `capabilities_raw.json` | Static + dynamic detectors merge | Applies baseline rules and dynamic detectors to identify capabilities with evidence files and pattern matches |
| S4 | `capabilities_scored.json` | Component weighting (auto-normalize) | Scores each capability using weighted components (functionality, consistency, tests, safeguards, documentation) |
| S5 | `gaps.json` | Threshold filter (low < 0.70) | Identifies capabilities below maturity threshold for remediation focus |
| S6 | `capability_matrix_<ts>.md` | Jinja render (template_hash embedded) | Generates human-readable markdown report with timestamp |
| S7 | `audit_run_manifest.json` | Hash chain (repo_root_sha + artifacts) | Creates integrity manifest with artifact hashes and configuration snapshot |

### Stage Details

#### Stage S1: Context Index
- **Input:** Repository file system
- **Process:** 
  - Recursively enumerate all files using `sorted(Path.rglob("*"))`
  - Skip `.git/`, `audit_artifacts/`, `reports/` directories
  - Compute SHA256 hash for files < 2MB
  - Record path (relative), extension, size for all files
- **Output:** `context_index.json` with sorted file list
- **Determinism:** Sorted traversal ensures consistent ordering

#### Stage S2: Facet Grouping
- **Input:** `context_index.json`
- **Process:**
  - Apply regex patterns to group files by domain
  - Default domains: checkpoint, token, train, eval, data, safety, logging, config
  - Each facet collects matching file paths
- **Output:** `facets.json` with domain-grouped file lists
- **Extensibility:** Add patterns in `DOMAIN_PATTERNS` dictionary

#### Stage S3: Capability Extraction
- **Input:** `facets.json`, detector modules
- **Process:**
  - Static baseline rules (8 core capabilities)
  - Dynamic detector loading from `scripts/space_traversal/detectors/*.py`
  - Pattern matching against file contents
  - Evidence collection with found vs required patterns
- **Output:** `capabilities_raw.json` with capability definitions
- **Extensibility:** Add detectors following the contract (see Section 9)

#### Stage S4: Scoring
- **Input:** `capabilities_raw.json`, weights from workflow.yaml
- **Process:**
  - Calculate 5 component scores per capability
  - Apply normalized weights (auto-normalize with warning)
  - Clamp values to [0, 1] range
  - Coverage augmentation via optional `coverage_map.json`
  - Documentation scoring with synonym expansion per capability
  - Duplicate heuristic selectable via `scoring.dup.heuristic` (`simple` or `token_similarity`)
  - Aggregate to final score
- **Output:** `capabilities_scored.json` with component breakdowns
- **Transparency:** All intermediate values preserved for audit

#### Stage S5: Gap Analysis
- **Input:** `capabilities_scored.json`, thresholds from workflow.yaml
- **Process:**
  - Filter capabilities where score < threshold.low (default 0.70)
  - Collect for prioritized remediation
- **Output:** `gaps.json` with low-maturity capabilities
- **Actionability:** Direct input for improvement planning

#### Stage S6: Report Rendering
- **Input:** `capabilities_scored.json`, `gaps.json`, Jinja2 templates
- **Process:**
  - Load template from `templates/audit/capability_matrix.md.j2`
  - Inject capability data, scores, gaps, weights
  - Compute template hash for drift detection
  - Render markdown with timestamp and companion JSON
  - Emit `codex_status_update_<date>.md` issue body for daily status automation
- **Output:** `reports/capability_matrix_<timestamp>.md`, `reports/capability_matrix_<timestamp>.json`, `reports/codex_status_update_<date>.md`
- **Format:** Human-readable tabular report + daily status issue text

#### Stage S7: Manifest Generation
- **Input:** All artifacts, workflow.yaml
- **Process:**
  - Compute repo_root_sha from sorted file list
  - Hash each artifact JSON file
  - Concatenate template files for template_hash
  - Collect warnings (e.g., weight normalization)
  - Bundle configuration snapshot with `metrics_schema_version` and normalized weights
- **Output:** `audit_run_manifest.json` at repository root
- **Integrity:** Cryptographic chain for audit trail

## 3. Core Principles

### Determinism
- **Sorted Traversal:** All file operations use sorted iterables
- **Truncated Reads:** File content limited to 200KB to prevent non-deterministic timeouts
- **Normalized Weights:** Auto-correct weight sums ≠ 1.0 with warning
- **Hash Chains:** SHA256 for all artifacts and templates

### Transparency
- **Explain Command:** Break down any capability's score by component
- **Diff Command:** Compare two audit runs to detect regressions
- **Warnings Field:** Manifest records all normalization and configuration notes
- **Component Visibility:** All intermediate values preserved in JSON

### Extensibility
- **Dynamic Detectors:** Drop-in Python modules in `detectors/` directory
- **Configurable Weights:** Adjust in `workflow.yaml` without code changes
- **Custom Keywords:** Override safeguard list via configuration
- **Template Customization:** Modify Jinja2 templates for different report formats

### Offline Safety
- **No Network Calls:** Entire pipeline runs locally
- **Cached Dependencies:** All tools (PyYAML, Jinja2) are standard Python libraries
- **Hermetic Execution:** No external API dependencies

### Minimal Writes
- **Structured Artifacts:** All outputs to `audit_artifacts/` directory
- **Timestamped Reports:** Markdown reports to `reports/` directory
- **Single Manifest:** One manifest file at repository root
- **Clean Separation:** Build artifacts excluded via .gitignore

## 4. Scoring System

### Component Weights (Defaults)
```yaml
functionality: 0.25
consistency: 0.20
tests: 0.25
safeguards: 0.15
documentation: 0.15
```

**Total must equal 1.0** (auto-normalized with warning if not)

### Score Calculation Formula
```
score = Σ(weight_i × clamp(component_i, 0, 1))
```

Where each component is clamped to [0, 1] range before weighting.

### Component Definitions

#### Functionality (weight: 0.25)
**Formula:** `found_patterns / required_patterns`

**Measures:** How many required patterns are present in the evidence files

**Computation:**
- Count unique patterns found in capability's evidence files
- Divide by total required patterns for that capability
- Result naturally bounded [0, 1]

**Example:**
```python
required = ["save_checkpoint", "load", "resume"]
found = ["save_checkpoint", "load"]
functionality = 2 / 3 = 0.667
```

#### Consistency (weight: 0.20)
**Formula:** `1 - duplication_ratio(evidence_files)`

**Measures:** Code reuse vs duplication across evidence files

**Computation:**
- Extract file stems from all evidence file paths
- Count duplicate stems (same name, different paths)
- Calculate: `dup_ratio = sum(count - 1 for count > 1) / total_files`
- Invert: `consistency = 1 - min(1.0, dup_ratio)`

**Example:**
```python
evidence = ["src/train.py", "tests/train.py", "train.py", "scripts/helper.py"]
stems = ["train", "train", "train", "helper"]
duplicates = 2  # "train" appears 3 times, so 2 extras
dup_ratio = 2 / 4 = 0.5
consistency = 1 - 0.5 = 0.5
```

#### Tests (weight: 0.25)
**Formula:** `test_files_linked / evidence_files` (clamped ≤1)

**Measures:** Test coverage depth for the capability

**Computation:**
- Count files in evidence set starting with `tests/`
- Search `tests/` directory for files containing capability token
- Compute ratio: unique test files / unique evidence files
- Clamp result to [0, 1]

**Example:**
```python
evidence = ["src/checkpoint.py", "src/storage.py", "docs/checkpoint.md"]
tests_found = ["tests/test_checkpoint.py"]
tests = min(1.0, 1 / 3) = 0.333
```

#### Safeguards (weight: 0.15)
**Formula:** `keywords_with_hits / total_safeguard_keywords`

**Measures:** Security and reproducibility keyword coverage

**Computation:**
- Check each safeguard keyword against all evidence file contents
- Count how many keywords have ≥1 occurrence
- Divide by total safeguard keyword count

**Default Keywords:**
```python
["sha256", "checksum", "rng", "seed", "offline", "WANDB_MODE",
 "confirm", "dry_run", "RateLimitExceeded", "Unauthorized", "ValidationError"]
```

**Example:**
```python
keywords = ["sha256", "checksum", "seed", "offline"]
evidence_content = "Use sha256 for hashing. Set offline mode."
hits = ["sha256", "offline"]  # 2 keywords found
safeguards = 2 / 4 = 0.5
```

#### Documentation (weight: 0.15)
**Formula:** `doc_files_mentioning_token / scaled_doc_corpus`

**Measures:** Documentation coverage with capability mentions

**Computation:**
- Collect markdown files from `docs/`, top-level `*.md`, `_codex/*.md`
- Exclude `audit_artifacts/`, `logs/` to reduce noise
- Extract capability token (first word before hyphen in ID)
- Count doc files containing token (case-insensitive)
- Scale: `min(1.0, hits / max(3, len(docs) * 0.1))`

**Example:**
```python
capability_id = "logging-tracking"
token = "logging"
docs = ["docs/logging.md", "docs/config.md", "README.md"]
hits = 1  # only "docs/logging.md" mentions "logging"
documentation = min(1.0, 1 / max(3, 3*0.1)) = min(1.0, 1/3) = 0.333
```

### Scoring Properties
- **Bounded:** All component values and final score in [0, 1]
- **Weighted:** Configurable relative importance via workflow.yaml
- **Normalized:** Weights auto-corrected to sum=1.0 if needed
- **Transparent:** All intermediate values in capabilities_scored.json
- **Reproducible:** Same inputs always produce same scores

## 5. Duplicate Heuristic

### Simple Method (Default)
**Formula:** `dup_ratio = (sum(duplicate_stems)) / evidence_count` (clamped ≤1)

**Algorithm:**
1. Extract file stem (filename without extension) from each evidence file path
2. Count occurrences of each stem
3. For stems appearing >1 time, sum up the excess: `count - 1`
4. Divide by total evidence file count
5. Clamp result to maximum of 1.0

**Example:**
```python
evidence = ["src/train.py", "tests/train.py", "scripts/train_helper.py", "docs/training.md"]
stems = ["train", "train", "train_helper", "training"]
stem_counts = {"train": 2, "train_helper": 1, "training": 1}
duplicates = (2-1) = 1
dup_ratio = min(1.0, 1 / 4) = 0.25
consistency_component = 1 - 0.25 = 0.75
```

### Token Similarity Method (Experimental)
**Status:** Available via `dup_similarity.py` module
**Configuration:** Set `scoring.dup.heuristic: token_similarity` in workflow.yaml
**Note:** Not enabled by default; requires additional dependencies

**Algorithm:**
- Tokenize file contents
- Compute Jaccard similarity or edit distance
- Aggregate pairwise similarities
- Higher similarity → higher duplication ratio

**Use Case:** More sophisticated detection of copy-paste code vs. legitimate reuse

## 6. Safeguard Keywords

### Default Set
```yaml
safeguards:
  keywords:
    - sha256
    - checksum
    - rng
    - seed
    - offline
    - WANDB_MODE
    - confirm       # MCP-specific
    - dry_run       # MCP-specific
    - RateLimitExceeded    # MCP-specific
    - Unauthorized         # MCP-specific
    - ValidationError      # MCP-specific
```

### Purpose
- **Security:** Cryptographic and validation keywords
- **Reproducibility:** Random seed and offline mode indicators
- **MCP Safety:** Confirmation prompts and error handling

### Customization
Edit the `safeguards.keywords` list in `.copilot-space/workflow.yaml` to override defaults.

**Example:**
```yaml
safeguards:
  keywords:
    - sha256
    - checksum
    - encrypt
    - decrypt
    - sanitize
    - validate_input
```

### Scoring Impact
The safeguards component score equals:
```
(number of keywords with ≥1 hit) / (total keywords)
```

More keywords = finer granularity, but may lower scores if not all are present.

## 7. Key Commands

### Full Pipeline
```bash
python scripts/space_traversal/audit_runner.py run
```
Executes S1 → S2 → S3 → S4 → S5 → S6 → S7 sequentially.

### Single Stage Execution
```bash
python scripts/space_traversal/audit_runner.py stage S4
```
Run only stage S4 (scoring). Requires prior stages' outputs to exist.

### Score Explanation
```bash
python scripts/space_traversal/audit_runner.py explain checkpointing
```
Breaks down the score for `checkpointing` capability, showing component values, weights, and contributions.

### Compare Two Runs
```bash
python scripts/space_traversal/audit_runner.py diff \
  --old audit_artifacts/capabilities_scored_baseline.json \
  --new audit_artifacts/capabilities_scored.json
```
Outputs CSV with columns: ID, OLD, NEW, DELTA. Non-zero exit if regressions detected (based on workflow.yaml options).

### Makefile Shortcuts
```bash
make space-audit          # Full run
make space-audit-fast     # Fast path (S1, S3, S4, S6)
make space-explain cap=logging-tracking
make space-diff old=<path> new=<path>
make space-clean          # Remove all audit artifacts
```

## 8. Configuration (workflow.yaml)

Located at `.copilot-space/workflow.yaml`

### Key Sections

#### Version & Stages
```yaml
version: 1.4.0
stages:
  - id: index
    script: audit_runner.py
    entry: stage
    args: ["S1"]
  # ... S2-S7 definitions
```

#### Weights
```yaml
weights:
  functionality: 0.25
  consistency: 0.20
  tests: 0.25
  safeguards: 0.15
  documentation: 0.15
```
**Must sum to 1.0** (auto-normalized with warning)

#### Thresholds
```yaml
scoring:
  thresholds:
    low: 0.70    # Below this = gap
    medium: 0.85  # Informational only
```

#### Dynamic Detectors
```yaml
capability_map:
  dynamic: true
  overrides:
    training-engine: ["train_loop", "functional_training"]
    # Add aliases here
```

#### Output Paths
```yaml
output:
  reports_dir: reports
  artifacts_dir: audit_artifacts
  matrix_template: templates/audit/capability_matrix.md.j2
```

#### Quality Gates
```yaml
options:
  fail_on_score_regression: true
  regression_delta_threshold: 0.02
  fail_on_low_maturity: true
  fail_on_missing_detector: true
```

### Editing Guidelines
1. **Backup first:** `cp .copilot-space/workflow.yaml .copilot-space/workflow.yaml.bak`
2. **Validate YAML:** Use `python -c "import yaml; yaml.safe_load(open('.copilot-space/workflow.yaml'))"`
3. **Test incrementally:** Run `make space-audit-fast` after changes
4. **Check warnings:** Inspect `audit_run_manifest.json` for normalization warnings

## 9. Adding a Dynamic Detector

### Detector Contract
Create `scripts/space_traversal/detectors/<capability_id>.py`:

```python
def detect(file_index: dict) -> dict:
    """
    Detect capability from file index.
    
    Args:
        file_index: Dictionary with 'files' list, each item has:
                    {'path': str, 'ext': str, 'size': int, 'sha': str}
    
    Returns:
        Dictionary with required fields:
        {
            "id": "capability-name",           # Required: kebab-case ID
            "evidence_files": [str, ...],       # Required: relative paths
            "found_patterns": [str, ...],       # Required: detected patterns
            "required_patterns": [str, ...],    # Required: expected patterns
            "meta": {}                          # Optional: additional info
        }
    """
    # Implementation here
    evidence_files = []
    found_patterns = []
    required_patterns = ["pattern1", "pattern2"]
    
    for file_meta in file_index["files"]:
        if file_meta["ext"] == ".py" and "serve" in file_meta["path"]:
            evidence_files.append(file_meta["path"])
            found_patterns.append("serve")
    
    return {
        "id": "new-capability",
        "evidence_files": sorted(set(evidence_files)),
        "found_patterns": sorted(set(found_patterns)),
        "required_patterns": required_patterns,
        "meta": {"detector_version": "1.0"}
    }
```

### Detector Best Practices
1. **Unique IDs:** Use kebab-case, no conflicts with existing capabilities
2. **Sorted outputs:** Always sort lists for determinism
3. **Defensive coding:** Handle missing files, catch exceptions
4. **Pattern precision:** Balance recall (finding evidence) vs precision (avoiding noise)
5. **Performance:** Minimize file I/O; reuse file_index metadata

### Integration Steps
1. Create detector file: `scripts/space_traversal/detectors/my_capability.py`
2. Test import: `python -c "from scripts.space_traversal.detectors import my_capability; print(my_capability.detect)"`
3. Run S3: `python scripts/space_traversal/audit_runner.py stage S3`
4. Verify in raw: `jq '.capabilities[] | select(.id=="my-capability")' audit_artifacts/capabilities_raw.json`
5. Run S4-S7: `make space-audit` or `make space-audit-fast`
6. Check score: `python scripts/space_traversal/audit_runner.py explain my-capability`

### Common Detector Patterns

#### Pattern: File Extension Filter
```python
def detect(file_index):
    py_files = [f["path"] for f in file_index["files"] if f["ext"] == ".py"]
    # ... process py_files
```

#### Pattern: Path Prefix Filter
```python
def detect(file_index):
    mcp_files = [f["path"] for f in file_index["files"] if f["path"].startswith("mcp/")]
    # ... process mcp_files
```

#### Pattern: Content Matching (requires lazy load)
```python
from pathlib import Path

def detect(file_index):
    evidence = []
    root = Path(__file__).resolve().parents[3]  # Adjust to repo root
    for f in file_index["files"]:
        if f["ext"] == ".py":
            try:
                content = (root / f["path"]).read_text(encoding="utf-8", errors="ignore")
                if "FastAPI" in content:
                    evidence.append(f["path"])
            except Exception:
                pass
    # ... build return dict
```

## 10. Manifest Fields

The `audit_run_manifest.json` file contains:

### Core Fields

#### repo_root_sha
**Type:** String (SHA256 hex)
**Computation:** Hash of sorted list of all file paths in repository
**Purpose:** Detect any file additions/deletions between runs

#### timestamp
**Type:** Float (Unix epoch seconds)
**Purpose:** Record when manifest was generated

#### version
**Type:** String (semver)
**Value:** Audit pipeline version (e.g., "1.1.0")
**Purpose:** Track specification changes over time

#### artifacts
**Type:** Array of objects
**Schema:** `[{"name": str, "sha": str}, ...]`
**Purpose:** Hash chain for all artifact JSON files in audit_artifacts/
**Example:**
```json
"artifacts": [
  {"name": "context_index.json", "sha": "abc123..."},
  {"name": "capabilities_scored.json", "sha": "def456..."}
]
```

#### template_hash
**Type:** String (SHA256 hex)
**Computation:** Concatenated bytes of all `*.j2` files in template directory, sorted by name
**Purpose:** Detect template drift between runs (impacts report format)

#### weights
**Type:** Object
**Schema:** `{component: float, ...}`
**Purpose:** Snapshot of configured weights for this run
**Example:**
```json
"weights": {
  "functionality": 0.25,
  "consistency": 0.20,
  "tests": 0.25,
  "safeguards": 0.15,
  "documentation": 0.15
}
```

#### normalized_weights
**Type:** Object (optional)
**Schema:** Same as weights
**Purpose:** Show auto-corrected weights when original sum ≠ 1.0
**Note:** Only present when normalization occurred

#### warnings
**Type:** Array of strings
**Purpose:** Record configuration issues (e.g., `"weights_normalized_from:0.98"`)
**Actionability:** Review and fix workflow.yaml if warnings present

### Optional Fields (Future)
- `detector_versions`: Track individual detector module versions
- `coverage_stats`: Integration with coverage.xml (planned 1.3.x)
- `trend_id`: Link to historical trend database (planned 1.4.x)

### Manifest Usage
- **Integrity Audit:** Verify artifact hashes haven't been tampered with
- **Reproducibility:** Compare manifests to ensure deterministic runs
- **Drift Detection:** Monitor template_hash and warnings across runs
- **Configuration Snapshot:** Recover exact weights/thresholds used for historical runs

## 11. Quality Gates (Optional)

Configured in `workflow.yaml` under `options:` section.

### Low Maturity Fail
```yaml
options:
  fail_on_low_maturity: true
```
**Behavior:** Non-zero exit if any capability score < `thresholds.low` (0.70)
**Use Case:** CI/CD gate to prevent merging low-quality capabilities
**Override:** Set to `false` for informational-only runs

### Score Regression Fail
```yaml
options:
  fail_on_score_regression: true
  regression_delta_threshold: 0.02
```
**Behavior:** `diff` command exits non-zero if any score drops > threshold
**Use Case:** Prevent capability maturity regressions between branches
**Example:** Score drops from 0.80 to 0.77 (Δ = -0.03) exceeds 0.02 → fails

### Missing Detector Fail
```yaml
options:
  fail_on_missing_detector: true
```
**Behavior:** Non-zero exit if `capability_map.overrides` references a detector ID that produces no capability
**Use Case:** Ensure configuration stays in sync with detector implementations
**Note:** Only applies when `dynamic: true`

### Hash Drift Warning
**Automatic:** Always computed, warning in manifest if template_hash changed
**Manual Review:** Check if report format intentionally changed or templates accidentally modified

### Custom Gates (Implementation)
To add custom gates, modify `audit_runner.py`:
1. Load gate config from workflow.yaml
2. Check condition after relevant stage
3. Call `sys.exit(non_zero_code)` on failure
4. Add warning to manifest

## 12. Determinism Check

### Two-Run Verification
```bash
# Run 1
make space-audit
cp audit_run_manifest.json manifest_run1.json
cp audit_artifacts/capabilities_scored.json scored_run1.json

# Run 2 (no changes)
make space-audit
cp audit_run_manifest.json manifest_run2.json
cp audit_artifacts/capabilities_scored.json scored_run2.json

# Compare
diff <(jq -S 'del(.timestamp)' manifest_run1.json) \
     <(jq -S 'del(.timestamp)' manifest_run2.json)
# Should output: empty (identical)

diff <(jq -S 'del(.generated)' scored_run1.json) \
     <(jq -S 'del(.generated)' scored_run2.json)
# Should output: empty (identical)
```

### Expected Differences
- **timestamp / generated:** Unix epoch seconds will differ
- **Reports:** Markdown filenames contain timestamps

### Unexpected Differences Indicate
- Non-deterministic detector logic (fix: sort all outputs)
- File system race conditions (fix: use sorted glob)
- Floating point precision issues (fix: round to 4 decimals)
- External state leakage (fix: isolate detector implementations)

### Troubleshooting Non-Determinism
1. **Check detector sort:** Ensure all lists in detector returns are sorted
2. **Verify file traversal:** Confirm `sorted(Path.rglob())` everywhere
3. **Inspect float precision:** Use `round(value, 4)` for all scores
4. **Review warnings:** Check manifest for normalization inconsistencies
5. **Diff raw capabilities:** Compare S3 output between runs

## 13. Failure Radar

Quick reference for common issues and fixes:

| Symptom | Likely Root Cause | Mitigation |
|---------|------------------|------------|
| Missing capability in output | Detector script has syntax error or returns invalid structure | Run `python -m py_compile scripts/space_traversal/detectors/<file>.py`; check stderr during S3 |
| All safeguards score 0 | Safeguard keywords not found in evidence files | Update keyword list in workflow.yaml; verify keywords are actually in code |
| High duplication ratio (>0.5) | Over-broad facet regex matches unrelated files | Narrow DOMAIN_PATTERNS in audit_runner.py; create specialized detector |
| Zero documentation score | No doc files mention capability token | Add documentation with capability keywords; verify docs/ directory not excluded |
| Template hash mismatch warning | Template files modified between runs | Review git diff for templates/audit/*.j2; regenerate baseline if intentional |
| Score regression on `diff` | Code changes reduced pattern matches or increased duplication | Inspect capabilities_scored.json components; run `explain` command; address gaps |
| Manifest missing normalized_weights | Weights already sum to 1.0 | No action needed; this field only appears when normalization occurs |
| Detector not found | File in detectors/ but not imported | Check filename is `<id>.py`; verify `detect` function signature; check for import errors in stderr |
| Non-deterministic scores | Floating point or sorting issue | Add `round(score, 4)` in detector; sort all list returns; use sorted(Path.rglob()) |
| Stage fails with "file not found" | Running stages out of order | Run prerequisite stages first or use `make space-audit` for full pipeline |

## 14. Pre-Commit Checklist

Before committing changes that affect capabilities:

- [ ] Run full audit: `make space-audit`
- [ ] Check for warnings: `jq '.warnings' audit_run_manifest.json`
- [ ] Review gaps: `jq '.low_maturity[] | .id' audit_artifacts/gaps.json`
- [ ] Verify no regressions: `make space-diff old=<baseline> new=audit_artifacts/capabilities_scored.json`
- [ ] Add/update documentation for new capabilities
- [ ] Test detector implementations: `python -m pytest tests/space_traversal/`
- [ ] Update workflow.yaml if adding capability overrides
- [ ] Commit manifest and latest report: `git add audit_run_manifest.json reports/capability_matrix_*.md`
- [ ] Document any intentional score decreases in commit message

## 15. Upgrade Path (Planned / Experimental)

### Version 1.2.x: Token Similarity
- Status: **configurable** via `scoring.dup.heuristic: token_similarity` (fallbacks to simple if helper absent)
- Approach: token-level overlap to refine duplication penalty

### Version 1.3.x: Coverage XML Integration
- Status: **partially** satisfied via `coverage_map.json` augmentation; XML ingestion remains roadmap
- Goal: replace heuristic test depth with line coverage

### Version 1.4.x: Trend Aggregation
- Status: **roadmap** — trend DB and visualization hooks pending
- Goal: store historical scores and chart regressions over time

### Version 2.0.0: Multi-Repo Federation
- Aggregate audit results across multiple repositories
- Cross-repo capability comparison
- Federated manifest chain
- Configuration: `federation.repos: [...]`

### Migration Notes
- **Backward Compatibility:** Manifests include version field for detection
- **Data Migration:** Scripts provided in `scripts/space_traversal/migrations/`
- **Deprecation Policy:** Warnings issued one minor version before removal

---

**Last Updated:** 2025-12-09  
**Specification Version:** 1.4.0  
**Maintained By:** Codex Audit Orchestrator Team
