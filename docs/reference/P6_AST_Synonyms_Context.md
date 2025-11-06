# [Reference]: P6 Advanced Features — AST, Synonyms, Context, Federation

> Generated: 2025-11-06 22:15:00 UTC | Author: copilot  
Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5

## 1. Overview

P6 introduces four advanced analysis capabilities to enhance audit precision and semantic understanding:
- **AST Similarity**: Structural code duplication via AST node-type vectors
- **Synonym Expansion**: Semantic pattern matching via configurable mappings
- **Secret Context Correlation**: Elevated risk assessment for sensitive file contexts
- **Federation Stub**: Multi-repo capability discovery (local-only)

All features are opt-in and deterministic.

---

## 2. AST Signature Similarity

### 2.1 Purpose
Detect structural code duplication beyond simple token similarity. Two files with different variable names but identical control flow structures will have high AST similarity.

### 2.2 Mechanism
```python
# Extract AST node type counts
ast.parse(source) → {FunctionDef: 5, ClassDef: 2, Call: 12, ...}

# Compute pairwise cosine similarity
ast_uniqueness = 1 - avg_pairwise_similarity
```

### 2.3 Integration (S4 Scoring)
Consistency blend modes:
- **multiply** (default): `consistency = (1 - dup_ratio) × token_sim × ast_unique`
- **average**: `consistency = mean(1-dup, token_sim, ast_unique)`
- **max**: `consistency = max(1-dup, token_sim, ast_unique)`

### 2.4 Knobs
| Knob | Default | Description |
|------|---------|-------------|
| AST_SIMILARITY_ENABLE | 0 | Compute AST uniqueness |
| AST_SIMILARITY_MAX_FILES | 30 | Cap evidence set |
| AST_SIMILARITY_MIN_NODES | 10 | Skip trivial files |
| AST_CONSISTENCY_BLEND_MODE | multiply | Blend strategy |

### 2.5 Output
```json
{
  "capabilities": [
    {
      "id": "training-engine",
      "ast_uniqueness": 0.7234,
      "python_files_analyzed": 12
    }
  ],
  "warnings": ["read_fail:src/broken.py"]
}
```

---

## 3. Capability Synonym Expansion

### 3.1 Purpose
Expand pattern matching via semantic equivalents. Maps domain terms to their synonyms for richer capability detection.

### 3.2 Synonym Map Format
```json
{
  "train": ["training", "epoch", "fit", "optimizer"],
  "checkpoint": ["save_checkpoint", "restore", "snapshot"],
  "tokenizer": ["tokenize", "encode", "decode", "vocab"]
}
```

### 3.3 Expansion Logic
```python
found_patterns = ["train", "checkpoint"]
# After expansion:
found_patterns = ["train", "training", "epoch", "fit", "checkpoint", "save_checkpoint", ...]
```

### 3.4 Knobs
| Knob | Default | Description |
|------|---------|-------------|
| SYNONYM_MAP_PATH | configs/synonyms/synonyms.json | Map file path |

### 3.5 Output
`capabilities_raw_expanded.json` with:
- `synonym_map_hash`: Reproducibility fingerprint
- `synonym_expansion_count`: Patterns added per capability
- `found_patterns_original`: Pre-expansion patterns

---

## 4. Secret Context Correlation

### 4.1 Purpose
Elevate entropy findings in sensitive contexts (auth/, config/, near credential keywords).

### 4.2 Context Indicators
**Path-based**:
- Contains: `auth`, `config`, `credentials`, `secrets`, `.env`, `security`

**Proximity-based** (within N lines):
- Keywords: `password`, `api_key`, `token`, `secret`, `credential`

### 4.3 Elevation Levels
| Level | Criteria |
|-------|----------|
| high | ≥2 context indicators |
| medium | 1 context indicator |

### 4.4 Knobs
| Knob | Default | Description |
|------|---------|-------------|
| SECRET_CONTEXT_ENABLE | 0 | Perform correlation |
| SECRET_CONTEXT_WINDOW | 10 | Line window for proximity |
| SECRET_CONTEXT_KEYWORDS | csv | Additional keywords |

### 4.5 Integration
- Severity classification can weight elevated findings higher
- Safeguards component influenced by high-elevation count

---

## 5. Federation Stub

### 5.1 Purpose
Local multi-repo capability discovery. Scans specified repositories for capability indicators.

### 5.2 Limitations
- **No network operations**: Local paths only
- **No scoring integration**: Future feature
- **Skips large files**: >2MB excluded

### 5.3 Knobs
| Knob | Default | Description |
|------|---------|-------------|
| FEDERATION_ENABLE | 0 | Enable scanning |
| FEDERATION_REPO_PATHS | csv | Paths to scan |

### 5.4 Output
```json
{
  "repositories": [
    {
      "path": "/path/to/repo",
      "capabilities": ["training", "checkpoint"],
      "evidence_count": 42
    }
  ],
  "total_scanned": 2,
  "total_capabilities": 5
}
```

---

## 6. Extended Manifest (S7)

### 6.1 New Provenance Fields
```json
{
  "version": "1.5.0",
  "ast_similarity_enabled": true,
  "synonym_map_hash": "a1b2c3d4e5f6g7h8",
  "secret_context_elevated": 3,
  "federation_repos_scanned": 2,
  "archival_operations": [
    {"action": "bundle", "timestamp": "...", "adr": "ADR-042"}
  ]
}
```

### 6.2 Knob
| Knob | Default | Description |
|------|---------|-------------|
| MANIFEST_EXTENDED_ENABLE | 1 | Include P6 provenance |

---

## 7. Determinism Guarantees

| Feature | Mechanism |
|---------|-----------|
| AST parsing | Sorted file list; deterministic node traversal |
| Synonym expansion | Sorted keys; stable hash |
| Context correlation | Fixed window scan; sorted indicators |
| Federation | Sorted repo paths; deterministic rglob |

---

## 8. Performance Considerations

| Feature | Complexity | Mitigation |
|---------|------------|------------|
| AST parsing | O(N×F) files×nodes | MAX_FILES cap; MIN_NODES filter |
| Token similarity | O(N²) pairwise | MAX_FILES=50 default |
| Context correlation | O(F×W) files×window | Window=10 lines default |
| Federation | O(R×F) repos×files | 2MB file size limit |

---

## 9. Example Workflow

```bash
# Full P6 audit with all features
AST_SIMILARITY_ENABLE=1 \
SYNONYM_MAP_PATH=configs/synonyms/synonyms.json \
SECRET_CONTEXT_ENABLE=1 \
FEDERATION_ENABLE=1 \
FEDERATION_REPO_PATHS="/path/repo1,/path/repo2" \
python scripts/space_traversal/audit_runner.py run

# Individual feature testing
AST_SIMILARITY_ENABLE=1 python scripts/analysis/ast_signature_similarity.py
python scripts/space_traversal/synonym_loader.py
SECRET_CONTEXT_ENABLE=1 python scripts/security/secret_context_correlate.py
FEDERATION_ENABLE=1 FEDERATION_REPO_PATHS="." python scripts/multi_repo/federated_index.py
```

---

## 10. Future Enhancements

| Feature | Description |
|---------|-------------|
| Cross-capability AST overlap | Detect shared structural patterns |
| Semantic embeddings | Vector similarity for pattern matching |
| Remote federation | GitHub API integration for multi-org discovery |
| Real-time context tracking | Line-number aware correlation |

*End of P6 Reference*
