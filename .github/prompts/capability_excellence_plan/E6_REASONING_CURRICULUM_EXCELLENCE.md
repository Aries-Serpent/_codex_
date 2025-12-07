# Batchset E6: Reasoning Curriculum Excellence

> **Target:** 0.80+ → ~1.00  
> **Priority:** P3 Medium  
> **Estimated Effort:** 3-4 days  
> **Impact:** +0.20 capability score

---

## 📊 Current State Analysis

### Strengths
- ✅ Curriculum scheduler implemented
- ✅ Phase transition logic working
- ✅ 60 reasoning datasets (3 difficulty levels)
- ✅ 7 evaluation metrics implemented
- ✅ 23 comprehensive tests

### Gaps to Address (0.80 → 1.00)
- ⚠️ **Datasets**: Need more diverse and challenging examples (0.75 → 0.95)
- ⚠️ **Evaluation**: Missing human evaluation integration (0.80 → 0.95)
- ⚠️ **Adaptation**: Missing adaptive curriculum based on performance (0.75 → 0.95)
- ⚠️ **Docs**: Missing curriculum design guide (0.85 → 0.98)
- ⚠️ **Benchmarking**: Missing comparison against baselines (0.75 → 0.95)

---

## 🎯 Excellence Tasks

### Task E6.1: Expanded Reasoning Datasets
**Objective**: Comprehensive dataset with 500+ diverse examples

**Acceptance Criteria**:
- [ ] 200+ warmup examples (basic reasoning)
- [ ] 200+ intermediate examples (multi-step reasoning)
- [ ] 100+ advanced examples (complex logic)
- [ ] Diverse reasoning types (math, logic, causal, analogical)
- [ ] Difficulty calibrated and validated

**Copilot Prompt**:
```
Expand reasoning datasets in datasets/reasoning/:

1. Expand datasets/reasoning/warmup.jsonl to 200 examples:
   - Simple math problems
   - Basic logic puzzles
   - Pattern recognition
   - Simple causal reasoning
   - Analogies

2. Create datasets/reasoning/intermediate.jsonl with 200 examples:
   - Multi-step math (algebra, geometry)
   - Multi-step logic (if-then chains)
   - Temporal reasoning
   - Spatial reasoning
   - Basic proofs

3. Expand datasets/reasoning/advanced.jsonl to 100 examples:
   - Complex mathematical proofs
   - Multi-hop logical reasoning
   - Counter-factual reasoning
   - Abductive reasoning
   - Meta-reasoning

4. Create datasets/reasoning/challenge.jsonl with 100 examples:
   - Competition-level problems (AMC, AIME)
   - Novel problem types
   - Adversarial examples
   - Edge cases

Add difficulty scores, reasoning types, and solution explanations to all examples.
Document in docs/datasets/reasoning_datasets.md
```

---

### Task E6.2: Human Evaluation Integration
**Objective**: Incorporate human evaluation in curriculum progression

**Acceptance Criteria**:
- [ ] Human evaluation interface
- [ ] Inter-rater reliability measurement
- [ ] Quality scoring rubric
- [ ] Batch evaluation workflows
- [ ] Integration with curriculum scheduler

**Copilot Prompt**:
```
Implement human evaluation in src/codex_ml/eval/human_evaluation.py:

1. Add HumanEvaluationInterface:
   - Web-based evaluation UI (Gradio/Streamlit)
   - Display model outputs
   - Collect ratings (1-5 scale)
   - Collect qualitative feedback
   - Track evaluation time

2. Add QualityRubric:
   - Correctness (0-1)
   - Completeness (0-1)
   - Clarity (0-1)
   - Efficiency (0-1)
   - Overall quality (0-1)

3. Add InterRaterReliability:
   - Calculate Fleiss' Kappa
   - Identify disagreement sources
   - Flag low-agreement examples
   - Recommend consensus resolution

4. Add BatchEvaluator:
   - Distribute examples to multiple evaluators
   - Aggregate ratings
   - Calculate consensus scores
   - Export results

Integrate with curriculum scheduler to use human eval scores for phase progression.
Create docs/guides/human_evaluation.md
```

---

### Task E6.3: Adaptive Curriculum Learning
**Objective**: Dynamically adjust curriculum based on performance

**Acceptance Criteria**:
- [ ] Performance-based difficulty adjustment
- [ ] Skill gap identification
- [ ] Targeted practice generation
- [ ] Curriculum replay for weak areas
- [ ] Adaptive pacing

**Copilot Prompt**:
```
Implement adaptive curriculum in src/codex_ml/training/adaptive_curriculum.py:

1. Add AdaptiveCurriculumScheduler:
   - Track per-skill performance
   - Identify weak areas (accuracy <70%)
   - Adjust difficulty dynamically
   - Skip mastered skills (accuracy >95%)
   - Adaptive phase transition

2. Add SkillGapAnalyzer:
   - Decompose errors by reasoning type
   - Identify systematic weaknesses
   - Recommend targeted practice
   - Track skill improvement over time

3. Add TargetedPracticeGenerator:
   - Generate similar problems for weak areas
   - Template-based generation
   - Difficulty variation
   - Synthetic data augmentation

4. Add CurriculumReplay:
   - Revisit earlier phases for weak skills
   - Interleave current and review examples
   - Spaced repetition algorithm
   - Forgetting prevention

Create tests/training/test_adaptive_curriculum.py and docs/guides/adaptive_curriculum.md
```

---

### Task E6.4: Advanced Reasoning Metrics
**Objective**: Comprehensive reasoning quality metrics

**Acceptance Criteria**:
- [ ] Step-by-step reasoning evaluation
- [ ] Logical consistency checking
- [ ] Explanation quality scoring
- [ ] Error pattern analysis
- [ ] Meta-cognitive metrics

**Copilot Prompt**:
```
Enhance reasoning metrics in src/codex_ml/eval/reasoning_metrics.py:

1. Add StepByStepEvaluator:
   - Parse reasoning steps
   - Validate each step
   - Check step dependencies
   - Identify error propagation
   - Calculate step-level accuracy

2. Add LogicalConsistencyChecker:
   - Check for contradictions
   - Validate inferences
   - Check assumption consistency
   - Detect circular reasoning
   - Measure logical soundness (0-1)

3. Add ExplanationQualityScorer:
   - Completeness of explanation
   - Clarity and conciseness
   - Use of examples
   - Pedagogical value
   - Overall quality (0-1)

4. Add ErrorPatternAnalyzer:
   - Classify error types
   - Identify common mistakes
   - Track error frequency
   - Recommend interventions

5. Add MetaCognitiveMetrics:
   - Self-assessment accuracy
   - Confidence calibration
   - Error detection ability
   - Explanation of uncertainty

Document all metrics in docs/reference/reasoning_metrics.md
```

---

### Task E6.5: Curriculum Benchmarking
**Objective**: Compare curriculum training against baselines

**Acceptance Criteria**:
- [ ] Baseline comparison (no curriculum)
- [ ] Time-to-accuracy measurements
- [ ] Sample efficiency analysis
- [ ] Final performance comparison
- [ ] Visualization and reporting

**Copilot Prompt**:
```
Create benchmarking suite in benchmarks/curriculum/:

1. benchmarks/curriculum/baseline_comparison.py:
   - Train with curriculum
   - Train without curriculum (random order)
   - Train with fixed difficulty
   - Compare convergence speed
   - Compare final performance

2. benchmarks/curriculum/sample_efficiency.py:
   - Measure accuracy vs training examples
   - Calculate AUC (area under curve)
   - Compare curriculum vs baseline
   - Identify efficiency gains

3. benchmarks/curriculum/skill_acquisition.py:
   - Track per-skill mastery over time
   - Compare acquisition rates
   - Identify curriculum advantages
   - Visualize learning trajectories

4. benchmarks/curriculum/transfer_learning.py:
   - Test on held-out reasoning types
   - Measure generalization
   - Compare transfer performance
   - Identify curriculum impact

Create benchmarks/curriculum/run_all_benchmarks.sh and docs/benchmarks/curriculum_effectiveness.md with results
```

---

### Task E6.6: Reasoning Evaluation Harness
**Objective**: Standardized evaluation framework

**Acceptance Criteria**:
- [ ] Multiple evaluation protocols
- [ ] Automated evaluation pipeline
- [ ] Result visualization
- [ ] Comparison with SOTA models
- [ ] Leaderboard generation

**Copilot Prompt**:
```
Create evaluation harness in src/codex_ml/eval/reasoning_harness.py:

1. Add ReasoningEvaluationHarness:
   - Load evaluation datasets
   - Run model inference
   - Calculate all metrics
   - Generate reports
   - Save results to MLflow

2. Add EvaluationProtocols:
   - Zero-shot evaluation
   - Few-shot evaluation (k=1,5,10)
   - Chain-of-thought prompting
   - Self-consistency evaluation
   - Multiple protocol comparison

3. Add ResultVisualizer:
   - Generate metric tables
   - Create comparison charts
   - Error analysis visualizations
   - Export to HTML/PDF

4. Add Leaderboard:
   - Track model performance over time
   - Compare different checkpoints
   - Compare against baselines
   - Export to markdown/JSON

Create tools/evaluate_reasoning.py CLI and docs/guides/reasoning_evaluation.md
```

---

### Task E6.7: Curriculum Design Guide
**Objective**: Comprehensive guide for designing reasoning curricula

**Acceptance Criteria**:
- [ ] Curriculum design principles
- [ ] Difficulty calibration guide
- [ ] Phase transition strategies
- [ ] Best practices and pitfalls
- [ ] Example curricula

**Copilot Prompt**:
```
Create curriculum design documentation:

1. docs/guides/curriculum_design_principles.md:
   - Incremental difficulty increase
   - Skill composition strategies
   - Phase transition timing
   - Evaluation frequency
   - Adaptation strategies

2. docs/guides/difficulty_calibration.md:
   - Methods for difficulty assessment
   - Automated difficulty scoring
   - Human calibration procedures
   - Balancing curriculum difficulty
   - Validation techniques

3. docs/guides/phase_transition_strategies.md:
   - Threshold-based transitions
   - Adaptive transitions
   - Smooth vs abrupt transitions
   - Curriculum replay strategies
   - Failure handling

4. docs/guides/curriculum_best_practices.md:
   - Start easy, increase gradually
   - Mix reasoning types within phases
   - Include review and practice
   - Monitor for forgetting
   - Adjust based on performance

5. docs/examples/example_curricula.md:
   - Math curriculum example
   - Logic curriculum example
   - Multi-domain curriculum
   - Adaptive curriculum example
   - Curriculum configuration files

Also create docs/troubleshooting/curriculum_training.md
```

---

## 📊 Success Metrics

### Target Outcomes
- **Functionality**: 1.00 (adaptive curriculum, human eval, comprehensive metrics)
- **Consistency**: 0.98 (standard evaluation protocols)
- **Tests**: 0.98 (comprehensive benchmarks)
- **Safeguards**: 0.98 (quality checks, validation)
- **Documentation**: 0.98 (design guide, best practices)

**Overall Capability**: 0.80 → **0.98** (+0.18)

### Validation Checklist
- [ ] All E6.1-E6.7 tasks complete
- [ ] 500+ reasoning examples
- [ ] Human evaluation working
- [ ] Adaptive curriculum functional
- [ ] Benchmarks show improvement
- [ ] Documentation comprehensive

---

**Batchset Status**: Ready for Implementation  
**Estimated Timeline**: 3-4 days  
**Priority**: P3 Medium
