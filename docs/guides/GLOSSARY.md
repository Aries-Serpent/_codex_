# Glossary

## Quantum-Inspired Terms

**k₁ (Kolmogorov Complexity Coefficient)**
- Decision error rate: k₁ = 1 - avg(DecisionScore)
- Target: ≤ 0.28 for Phase 8.7
- Lower is better (indicates higher intelligence)

**Quantum Advantage**
- Ratio: 1/k₁
- Target: ≥ 3.57x for Phase 8.7
- Speedup over classical approaches

**Superposition**
- Quantum state |ψ⟩ = Σᵢ αᵢ |sᵢ⟩
- Multiple strategies existing simultaneously
- Collapses upon measurement (strategy selection)

**Decoherence**
- Loss of quantum coherence
- In cognitive brain: negative transfer effect
- Triggers domain isolation

**Entanglement**
- Correlation between quantum states
- In cognitive brain: cross-domain knowledge correlation

## Meta-Learning Terms

**MAML (Model-Agnostic Meta-Learning)**
- Meta-learning algorithm by Finn et al.
- Learns good initialization for fast adaptation
- Two-level optimization: inner and outer loops

**Reptile**
- Simpler alternative to MAML by Nichol et al.
- First-order meta-learning
- Direct parameter interpolation

**Meta-Parameters**
- Initialization parameters θ
- Learned across multiple tasks
- Enables fast adaptation

**Inner Loop**
- Task-specific adaptation
- Gradient descent on single task
- Typically 5-10 steps

**Outer Loop**
- Meta-parameter updates
- Aggregates across tasks
- Meta-gradient computation

## Cognitive Brain Terms

**UTI (Universal Task Interface)**
- Standard interface for task execution
- Supports any computable environment μ
- Deterministic with fixed seeds

**MPR (Meta-Policy Router)**
- Dynamic strategy selection
- Maintains strategy superposition
- Collapses to single strategy via measurement

**UPS (Universal Pattern Store)**
- Cross-domain pattern repository
- Similarity-based retrieval
- Pattern versioning and deprecation

**Abstraction Engine**
- Hierarchical concept extraction
- Relation mapping (causal, temporal, spatial)
- Analogy-based transfer

**Grounding Layer**
- Maps abstractions to feasible actions
- Action validation pipeline
- Execution trace replay

**Safety Monitor**
- Prevents negative transfer
- Detects catastrophic forgetting
- Triggers rollback when needed

## Transfer Learning Terms

**Zero-Shot Transfer**
- Applying learned knowledge to new task without training
- Target: >60% accuracy for Phase 8.7

**Few-Shot Transfer**
- Learning from small number of examples
- K=10: Learning from 10 examples
- Target: >80% accuracy for Phase 8.7

**Negative Transfer**
- When transfer hurts performance
- Threshold: <5% degradation
- Triggers safety mechanisms

**Catastrophic Forgetting**
- Losing performance on old tasks when learning new ones
- Threshold: <20% degradation
- Triggers domain isolation

**Domain Adaptation**
- Adjusting model to new domain
- Automatic domain detection
- Cross-domain knowledge sharing

## Validation Terms

**EXP-10 Benchmark**
- 10 diverse tasks for validation
- Tests zero-shot and few-shot transfer
- Validates k₁ ≤ 0.28 achievement

**Baseline Performance**
- Reference performance for comparison
- Stored per domain
- Used for forgetting detection

**Feasibility Score**
- Measure of action executability
- 0.0-0.3: infeasible
- 0.3-0.7: risky
- 0.7-1.0: feasible

## Pattern Recognition Terms

**Concept**
- Abstract pattern extracted from experience
- Has properties and support count
- Hierarchical levels: leaf, intermediate, root

**Relation**
- Connection between concepts
- Types: causal, temporal, spatial, generic
- Directed: source → target

**Analogy**
- Mapping between domains
- Source domain → Target domain
- Quality scored by structural similarity

**Embedding**
- 32-dimensional vector representation
- Used for similarity computation
- Cosine similarity for retrieval

## Technical Terms

**Deterministic Execution**
- Same inputs always produce same outputs
- Achieved through fixed random seeds
- Critical for regression testing

**Golden Snapshot**
- Reference output for regression testing
- JSON representation of expected results
- Ensures stability across changes

**JSONL (JSON Lines)**
- One JSON object per line
- Easy streaming and appending
- Used for metrics artifacts

**Semantic Versioning**
- Version format: MAJOR.MINOR.PATCH
- Breaking changes increment MAJOR
- New features increment MINOR
- Bug fixes increment PATCH
