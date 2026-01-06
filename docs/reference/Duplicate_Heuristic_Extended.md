# [Reference]: Duplicate & Similarity Heuristic (Extended P4/P5)

> Generated: Previous Cycle-11-06 19:02:11 UTC | Author: mbaetiong  
> Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5

## 1. Original Duplication (Pre-P4)

`duplication_ratio = duplicate_stems / total_evidence_files (clamped ≤1)`

## 2. Token Similarity Augmentation

| Step | Action |
|------|--------|
| 1 | Tokenize evidence file contents (min length filter) |
| 2 | Build TF vectors per file |
| 3 | Compute pairwise cosine similarities |
| 4 | Average similarity → similarity_avg |
| 5 | similarity_index = 1 - similarity_avg |

## 3. Combined Consistency Metric

`consistency = (1 - duplication_ratio) * similarity_index`

This penalizes both redundant filenames and near-identical content.

## 4. Parameter Controls

| Knob | Effect | Default |
|------|--------|---------|
| TOKEN_SIMILARITY_ENABLE | Run similarity engine | off |
| TOKEN_SIMILARITY_MAX_FILES | Cap evidence considered | 50 |
| TOKEN_SIMILARITY_MIN_LEN | Minimum token length | 5 |

## 5. Coverage Enhancement (Tests Component)

`tests = max(test_file_ratio, coverage_percent)` — chooses strongest evidence.

## 6. Edge Cases

| Case | Handling |
|------|----------|
| Single evidence file | similarity_index = 1.0 |
| Empty token set | similarity contribution = neutral (1.0 - 0) |
| Large binary file | Skipped by extension filter |

## 7. Performance Considerations

- Complexity O(N^2) pairwise; cap via TOKEN_SIMILARITY_MAX_FILES.
- Potential future optimization: MinHash / locality-sensitive hashing.

## 8. Planned Extensions

| Feature | Description |
|---------|-------------|
| Token Category Weighting | Distinguish code vs doc token duplication |
| AST Signature Overlap | Structural duplication detection |
| Cross-capability Similarity | Identify overlapping domains for consolidation |

*End of Extended Duplicate Heuristic*
