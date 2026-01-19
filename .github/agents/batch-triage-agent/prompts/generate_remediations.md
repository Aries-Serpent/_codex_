# Remediation Generation Prompt

## Context

You are generating specific, actionable fix suggestions for grouped CI failures with risk classification and confidence scoring.

## Input

- Failure group with common root cause
- Historical remediation success rates
- Cognitive brain patterns
- Codebase context (recent changes, file structure)

## Your Task

1. **Generate Fix Suggestions**:
   - Provide specific, actionable remediation steps
   - Include code examples and file paths
   - Estimate effort and impact
   - Classify risk level

2. **Risk Classification**:
   - **Low Risk** (Auto-applicable):
     - Confidence > 90%
     - Minimal impact (single file, reversible)
     - Historical success rate > 85%
     - Examples: Add import, fix typo, update version pin
   
   - **Medium Risk** (Requires Review):
     - Confidence 70-90%
     - Moderate impact (multiple files, requires testing)
     - Historical success rate 70-85%
     - Examples: Refactor function, update config, add feature flag
   
   - **High Risk** (Manual Investigation):
     - Confidence < 70%
     - Significant impact (architecture change, data migration)
     - Historical success rate < 70% or no history
     - Examples: Major refactor, dependency upgrade, breaking change

3. **Prioritize Suggestions**:
   - Sort by: impact × confidence × success_rate
   - Consider dependencies between fixes
   - Identify quick wins vs. strategic improvements

## Output Format

```json
{
  "group_id": "group_1",
  "remediations": [
    {
      "remediation_id": "REM_001",
      "title": "Add hydra-core to test dependencies",
      "description": "Install hydra-core==1.3.2 as test dependency to resolve ModuleNotFoundError",
      "risk": "low",
      "confidence": 0.95,
      "estimated_effort_minutes": 5,
      "impact": "Resolves 3 failing test suites",
      "success_probability": 0.92,
      "reversibility": "easy",
      "steps": [
        {
          "step": 1,
          "action": "Add dependency to requirements-test.txt",
          "command": "echo 'hydra-core==1.3.2' >> requirements-test.txt"
        },
        {
          "step": 2,
          "action": "Reinstall test dependencies",
          "command": "pip install -r requirements-test.txt"
        },
        {
          "step": 3,
          "action": "Verify tests pass",
          "command": "pytest tests/test_config.py -v"
        }
      ],
      "code_changes": [
        {
          "file": "requirements-test.txt",
          "action": "append",
          "content": "hydra-core==1.3.2  # For config management tests"
        }
      ],
      "validation": {
        "pre_check": "grep -q 'hydra-core' requirements-test.txt || echo 'Not found'",
        "post_check": "python -c 'import hydra' && echo 'Success'",
        "rollback": "git checkout requirements-test.txt"
      },
      "historical_context": {
        "similar_fixes": 12,
        "success_rate": 0.95,
        "avg_time_to_resolve": "15 minutes",
        "last_application": "2026-01-15"
      },
      "approval_requirements": {
        "auto_apply": true,
        "requires_human_review": false,
        "requires_owner_approval": false,
        "can_create_pr": true
      }
    },
    {
      "remediation_id": "REM_002",
      "title": "Add optional import guard for hydra",
      "description": "Wrap hydra imports in try-except for graceful degradation",
      "risk": "medium",
      "confidence": 0.75,
      "estimated_effort_minutes": 30,
      "impact": "Makes tests resilient to missing optional dependencies",
      "success_probability": 0.80,
      "reversibility": "moderate",
      "steps": [
        {
          "step": 1,
          "action": "Identify all hydra import locations",
          "command": "rg 'from hydra|import hydra' --type py"
        },
        {
          "step": 2,
          "action": "Add try-except guards",
          "files_to_modify": [
            "src/tokenization/train_tokenizer.py",
            "src/codex_ml/config_loader.py"
          ]
        },
        {
          "step": 3,
          "action": "Test with and without hydra installed",
          "command": "pytest tests/ --with-hydra && pytest tests/ --without-hydra"
        }
      ],
      "code_changes": [
        {
          "file": "src/tokenization/train_tokenizer.py",
          "action": "replace",
          "before": "import hydra\nfrom hydra import compose",
          "after": "try:\n    import hydra\n    from hydra import compose\n    HAS_HYDRA = True\nexcept ImportError:\n    HAS_HYDRA = False\n    hydra = None"
        }
      ],
      "validation": {
        "pre_check": "Run affected tests before changes",
        "post_check": "Run affected tests after changes + verify optional behavior",
        "rollback": "git checkout src/tokenization/train_tokenizer.py src/codex_ml/config_loader.py"
      },
      "approval_requirements": {
        "auto_apply": false,
        "requires_human_review": true,
        "requires_owner_approval": false,
        "can_create_pr": true
      }
    }
  ],
  "execution_plan": {
    "phase_1_low_risk": {
      "remediations": ["REM_001"],
      "estimated_total_time": "5 minutes",
      "can_auto_apply": true
    },
    "phase_2_medium_risk": {
      "remediations": ["REM_002"],
      "estimated_total_time": "30 minutes",
      "requires_pr_review": true
    },
    "dependencies": [
      {
        "remediation": "REM_002",
        "depends_on": ["REM_001"],
        "reason": "Should apply immediate fix before structural changes"
      }
    ]
  }
}
```

## Remediation Categories

### 1. Dependency Fixes
- Add missing packages
- Update version pins
- Resolve conflicts

### 2. Import Fixes
- Fix import paths
- Add missing modules
- Refactor circular imports

### 3. Configuration Fixes
- Update YAML syntax
- Add missing keys
- Fix type mismatches

### 4. Code Fixes
- Fix typos
- Update deprecated APIs
- Resolve lint errors

### 5. Test Fixes
- Update assertions
- Fix flaky tests
- Add missing mocks

### 6. Build Fixes
- Update workflows
- Fix permissions
- Resolve path issues

## Quality Criteria

1. **Specificity**: Exact commands, file paths, line numbers
2. **Testability**: Clear validation steps
3. **Reversibility**: Easy rollback if needed
4. **Documentation**: Explain why, not just what
5. **Safety**: Consider edge cases and side effects

## Success Metrics

Track for each remediation:
- Application count
- Success rate
- Average resolution time
- Rollback frequency
- User satisfaction

## Integration with Automated Workflow

Low-risk fixes (auto_apply: true):
1. Applied automatically via GitHub Actions
2. Create PR with changes
3. Run CI validation
4. Auto-merge if tests pass

Medium-risk fixes (requires_review: true):
1. Create PR with changes
2. Request human review
3. Wait for approval
4. Merge after approval

High-risk fixes (requires_investigation: true):
1. Create tracking issue
2. Notify engineering lead
3. Provide investigation guide
4. Manual resolution required
