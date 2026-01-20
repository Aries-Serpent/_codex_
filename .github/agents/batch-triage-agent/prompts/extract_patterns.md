# Pattern Extraction Prompt

## Context

You are extracting recurring failure patterns from historical data to improve future triage accuracy and remediation suggestions.

## Input

- Historical failure records from `.codex/cognitive_brain/patterns/ci_failures/`
- Current batch analysis results
- Remediation outcomes (success/failure)
- Time-series data showing pattern evolution

## Your Task

1. **Identify Recurring Patterns**:
   - Group similar failures across different time periods
   - Calculate pattern frequency and recency
   - Identify correlations (e.g., "fails after dependency update")
   - Detect emerging vs. declining patterns

2. **Extract Pattern Features**:
   - Error message templates (with wildcards)
   - Common stack trace patterns
   - Associated file paths or modules
   - Typical root causes
   - Successful remediation strategies

3. **Classify Pattern Types**:
   - **Systemic**: Infrastructure, configuration issues
   - **Code Quality**: Lint, format, type errors
   - **Dependencies**: Import errors, version conflicts
   - **Test-Specific**: Flaky tests, timing issues
   - **Environmental**: Platform-specific, resource constraints

4. **Calculate Pattern Metrics**:
   - Frequency (occurrences per time period)
   - Recency (days since last occurrence)
   - Severity distribution
   - Resolution success rate
   - Average time to resolve

## Output Format

```json
{
  "patterns": [
    {
      "pattern_id": "PATTERN_IMPORT_HYDRA",
      "pattern_type": "dependencies",
      "description": "Missing hydra-core in test environment",
      "error_template": "ModuleNotFoundError: No module named 'hydra*'",
      "affected_modules": ["src/tokenization/*", "src/codex_ml/*"],
      "frequency": {
        "total_occurrences": 15,
        "last_30_days": 8,
        "trend": "increasing"
      },
      "severity": {
        "critical": 0,
        "high": 12,
        "medium": 3,
        "low": 0
      },
      "successful_remediations": [
        {
          "description": "Add hydra-core==1.3.2 to requirements-test.txt",
          "success_rate": 0.95,
          "avg_resolution_time_minutes": 15,
          "applications": 12
        },
        {
          "description": "Add try-except block with graceful degradation",
          "success_rate": 0.85,
          "avg_resolution_time_minutes": 30,
          "applications": 3
        }
      ],
      "predictive_indicators": [
        "PR modifies files in src/tokenization/",
        "Recent dependency version bump",
        "New test files added"
      ],
      "recommendations": {
        "immediate": "Ensure hydra-core in test dependencies",
        "short_term": "Add pre-import validation in affected modules",
        "long_term": "Make hydra truly optional with feature flags"
      }
    }
  ],
  "pattern_relationships": [
    {
      "parent_pattern": "PATTERN_IMPORT_HYDRA",
      "child_pattern": "PATTERN_CONFIG_MISSING",
      "relationship": "often_follows",
      "confidence": 0.8
    }
  ],
  "emerging_patterns": [
    {
      "pattern_id": "PATTERN_NEW_001",
      "description": "Timeout in test_quantum_integration",
      "occurrences": 3,
      "first_seen": "2026-01-15",
      "status": "monitoring"
    }
  ]
}
```

## Pattern Learning Algorithm

1. **Feature Extraction**:
   ```python
   features = extract_features(failure)
   # - Error message (normalized)
   # - Stack trace signature
   # - Affected files
   # - Failure type
   # - Context (recent changes, env)
   ```

2. **Similarity Matching**:
   ```python
   similarity = calculate_similarity(new_failure, historical_patterns)
   # Use: Levenshtein distance, TF-IDF, embeddings
   # Threshold: 0.8 for match
   ```

3. **Pattern Clustering**:
   ```python
   clusters = cluster_failures(historical_data)
   # Use: DBSCAN, hierarchical clustering
   # Min cluster size: 3
   ```

4. **Success Rate Calculation**:
   ```python
   success_rate = successful_fixes / total_fixes
   # Weight recent outcomes more heavily
   # Decay factor: 0.95 per week
   ```

## Best Practices

1. **Normalize Data**: Remove timestamps, IDs, specific values
2. **Weight Recency**: Recent patterns more relevant than old
3. **Track Evolution**: Patterns change over time
4. **Validate Accuracy**: Compare predictions with actual outcomes
5. **Handle Noise**: Filter one-off failures vs. patterns

## Integration with Cognitive Brain

Store patterns in structured format:
```
.codex/cognitive_brain/patterns/ci_failures/
├── patterns_catalog.json         # All known patterns
├── pattern_IMPORT_HYDRA.json     # Individual pattern details
├── pattern_relationships.json    # How patterns relate
└── outcomes/
    ├── batch_001_outcomes.json   # Remediation results
    └── success_rates.json        # Aggregated metrics
```

## Continuous Learning

After each batch triage:
1. Update pattern frequencies
2. Record remediation outcomes
3. Adjust success rates
4. Identify new patterns
5. Archive obsolete patterns (>90 days no occurrence)
