# Quantum Agent Framework

## Overview

The Quantum Agent Framework implements a controlled dynamical system for agent behavior, inspired by quantum mechanics and energy minimization principles. This framework provides a rigorous mathematical foundation for agent configuration, optimization, and response generation.

## Core Concepts

### 1. Agent Configuration State (θ)

The agent configuration state θ encapsulates all parameters defining agent behavior:

```
θ ≡ {θ_name, θ_desc, θ_instr, θ_sources, θ_caps, θ_prompts}
```

- **θ_name**: Agent identifier
- **θ_desc**: Capability description
- **θ_instr**: Instruction set (behavior guidelines)
- **θ_sources**: Knowledge source configurations
- **θ_caps**: Available capability operators
- **θ_prompts**: Template configurations

### 2. Source Hilbert Space (ℋ_S)

Knowledge sources are represented as basis states in a Hilbert space:

```
ℋ_S = span(|s_1⟩, |s_2⟩, ..., |s_n⟩)
```

Each |s_i⟩ represents:
- Websites
- Allowed domains
- Organizational directories
- Document repositories

### 3. Query and Response States

**Query State** |x⟩ ∈ ℋ_X:
- Input prompt representation
- Context embeddings
- Intent classification

**Response State** |y⟩ ∈ ℋ_Y:
- Generated output
- Confidence scores
- Source citations

### 4. Policy Function

The response generator uses a policy function:

```
π_θ(y | x, S, O) = softmax(f_θ(x; S, O))
```

Where:
- x: Query state
- S: Source set
- O: Capability operators
- θ: Configuration parameters

## Initialization vs Optimization

### Describe Phase (Initialization)

Fast prior initialization from description:

```
θ_0 ~ p(θ | Describe)
```

Provides quick setup with reasonable defaults.

### Configure Phase (Optimization)

Constrained energy minimization:

```
θ* = argmin_{θ∈Ω} E(θ)
```

Where Ω encodes hard constraints:
- Output format requirements
- Scope limitations
- Source access rules

## Energy Functional

The energy functional decomposes as:

```
E(θ) = λ_hall·𝔼[L_hall] + λ_fmt·𝔼[L_fmt] + λ_src·𝔼[L_src] + λ_coh·𝔼[L_coh]
```

### Energy Components

1. **Hallucination Loss (L_hall)**
   - Measures factual inconsistency
   - Penalizes unsourced claims
   - Enforces grounding in provided sources

2. **Formatting Loss (L_fmt)**
   - Output format violations
   - Structure compliance
   - Template adherence

3. **Source Compliance Loss (L_src)**
   - Required source usage
   - Access restriction violations
   - Citation completeness

4. **Coherence Loss (L_coh)**
   - Logical consistency
   - Reasoning flow
   - Internal contradictions

### Energy Weights

Default weights:
- λ_hall = 1.0 (hallucination penalty)
- λ_fmt = 0.5 (format violations)
- λ_src = 0.8 (source constraints)
- λ_coh = 0.7 (coherence)

Specialized agents can adjust weights (e.g., research agents use λ_hall = 2.0).

## Usage Examples

### Creating a Standard Agent

```typescript
import { createStandardAgent, SourceState } from './quantum-agent-framework';

const sources: SourceState[] = [
  {
    id: 'docs-1',
    type: 'document',
    uri: 'https://docs.example.com',
    accessLevel: 'public',
    reliability: 0.95,
    metadata: {},
  },
];

const agent = createStandardAgent(
  'general-assistant',
  'A helpful general-purpose assistant',
  sources
);
```

### Creating a Research Agent

```typescript
import { createResearchAgent } from './quantum-agent-framework';

const agent = createResearchAgent(
  'research-assistant',
  ['machine learning', 'quantum computing', 'physics'],
  sources
);
```

### Optimizing Configuration

```typescript
// Optimize with custom constraints
await agent.optimizeConfiguration({
  maxResponseTokens: 3000,
  hallucinationThreshold: 0.1,
  requiredSources: ['peer-reviewed'],
});
```

### Generating Responses

```typescript
import { QueryState } from './quantum-agent-framework';

const query: QueryState = {
  prompt: 'Explain quantum entanglement',
  context: ['physics', 'quantum mechanics'],
  intent: 'question',
  priority: 0.8,
  metadata: {},
};

const response = await agent.generateResponse(query);

console.log(response.content);
console.log('Confidence:', response.confidence);
console.log('Sources:', response.sources);
```

### Source Projection

```typescript
// Project query onto available sources
const relevantSources = agent.projectOntoSources(query);

console.log('Relevant sources:', relevantSources.map(s => s.uri));
```

## Advanced Features

### Custom Capability Operators

```typescript
import { CapabilityOperator } from './quantum-agent-framework';

const customRetrieval: CapabilityOperator = {
  name: 'semantic-retrieval',
  type: 'retrieval',
  operator: async (query, context) => {
    // Custom retrieval logic
    return {
      content: 'Retrieved content',
      confidence: 0.9,
      sources: context.config.θ_sources,
      reasoning: ['semantic search', 'relevance ranking'],
      metadata: {},
    };
  },
  constraints: {
    maxTokens: 1000,
    outputFormat: 'text',
  },
};

agent.updateConfiguration({
  θ_caps: [customRetrieval, ...agent.getConfiguration().θ_caps],
});
```

### Energy-Based Selection

The framework automatically selects configurations with minimal energy:

```typescript
// Framework internally computes:
// E(θ) for candidate configurations
// Selects θ* with minimum E(θ)
```

### Constraint Domain (Ω)

Hard constraints define the feasible configuration space:

```typescript
const constraints = {
  maxResponseTokens: 2000,
  allowedOutputFormats: ['json', 'markdown'],
  requiredSources: ['verified'],
  hallucinationThreshold: 0.15,
  energyBudget: 100,
};
```

## Integration with Cognitive Brain

The Quantum Agent Framework integrates with the cognitive brain architecture:

1. **Layer Integration**
   - UI Layer: Agent selection interface
   - AI Generation: Policy function implementation
   - Quantum Processing: Source Hilbert space operations
   - Workflow: Multi-agent orchestration

2. **State Management**
   - Agent configurations persist across sessions
   - Query history maintained for context
   - Energy metrics tracked for optimization

3. **Capability Composition**
   - Operators combine for complex behaviors
   - Pipeline construction for multi-step reasoning
   - Parallel execution for independent operations

## Future Enhancements

1. **Quantum Superposition**
   - Multiple candidate responses in superposition
   - Measurement collapses to optimal response
   - Interference between reasoning paths

2. **Entanglement**
   - Correlated agent behaviors
   - Multi-agent quantum states
   - Non-local information sharing

3. **Adaptive Weights**
   - Learn optimal λ values from feedback
   - Context-dependent weight adjustment
   - Meta-learning for weight initialization

4. **Advanced Energy Functionals**
   - User preference alignment terms
   - Computational efficiency penalties
   - Multi-objective optimization

## References

- Quantum-inspired optimization techniques
- Controlled dynamical systems theory
- Energy-based learning methods
- Multi-agent reinforcement learning

## API Documentation

See `cognitive_app/src/lib/quantum-agent-framework.ts` for complete API documentation.

## Testing

Run tests:
```bash
npm test src/lib/__tests__/quantum-agent-framework.test.ts
```

## Contributing

Follow the quantum agent framework design principles:
1. Maintain mathematical rigor
2. Preserve energy functional decomposition
3. Document all operator implementations
4. Include comprehensive tests

---

**Version**: 1.0.0  
**Status**: Production Ready  
**Integration**: Cognitive Brain v3.0+
