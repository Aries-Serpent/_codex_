# API Reference

Complete API reference for all Cognitive Brain modules.

## Core Modules

```{toctree}
---
maxdepth: 2
---

adaptive_learning
transfer_learning
production_deployment
advanced_optimization
universal_intelligence
```

## Universal Intelligence Components

### Universal Task Interface (UTI)

```{eval-rst}
.. autoclass:: core.universal_intelligence.UniversalTaskInterface
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: core.universal_intelligence.TaskSpec
   :members:
   :undoc-members:

.. autoclass:: core.universal_intelligence.TaskResult
   :members:
   :undoc-members:
```

### Environment Adapters

```{eval-rst}
.. autoclass:: core.universal_intelligence.EnvironmentAdapter
   :members:
   :undoc-members:

.. autoclass:: core.universal_intelligence.GridWorldAdapter
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: core.universal_intelligence.BanditAdapter
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: core.universal_intelligence.ClassificationAdapter
   :members:
   :undoc-members:
   :show-inheritance:
```

### Meta-Policy Router

```{eval-rst}
.. autoclass:: core.universal_intelligence.MetaPolicyRouter
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: core.universal_intelligence.MAMLState
   :members:
   :undoc-members:

.. autoclass:: core.universal_intelligence.ReptileState
   :members:
   :undoc-members:

.. autoclass:: core.universal_intelligence.StrategyPerformance
   :members:
   :undoc-members:

.. autoclass:: core.universal_intelligence.DynamicHyperparamTuner
   :members:
   :undoc-members:

.. autoclass:: core.universal_intelligence.StrategyBenchmark
   :members:
   :undoc-members:
```

### Abstraction Engine

```{eval-rst}
.. autoclass:: core.universal_intelligence.AbstractionEngine
   :members:
   :undoc-members:

.. autoclass:: core.universal_intelligence.Concept
   :members:
   :undoc-members:

.. autoclass:: core.universal_intelligence.Relation
   :members:
   :undoc-members:

.. autoclass:: core.universal_intelligence.Analogy
   :members:
   :undoc-members:
```

### Grounding Layer

```{eval-rst}
.. autoclass:: core.universal_intelligence.GroundingLayer
   :members:
   :undoc-members:

.. autoclass:: core.universal_intelligence.GroundedAction
   :members:
   :undoc-members:

.. autoclass:: core.universal_intelligence.ActionConstraint
   :members:
   :undoc-members:

.. autoclass:: core.universal_intelligence.ValidationResult
   :members:
   :undoc-members:
```

### Pattern Store

```{eval-rst}
.. autoclass:: core.universal_intelligence.UniversalPatternStore
   :members:
   :undoc-members:

.. autoclass:: core.universal_intelligence.Pattern
   :members:
   :undoc-members:
```

### Safety Monitor

```{eval-rst}
.. autoclass:: core.universal_intelligence.SafetyMonitor
   :members:
   :undoc-members:

.. autoclass:: core.universal_intelligence.DomainBaseline
   :members:
   :undoc-members:
```

### EXP-10 Validation

```{eval-rst}
.. autoclass:: core.universal_intelligence.EXP10BenchmarkHarness
   :members:
   :undoc-members:
```

## Helper Functions

```{eval-rst}
.. autofunction:: core.universal_intelligence.calculate_safe_quantum_advantage

.. autofunction:: core.universal_intelligence.estimate_task_complexity

.. autofunction:: core.universal_intelligence.validate_task_spec_schema
```

## Constants

```{eval-rst}
.. autodata:: core.universal_intelligence.K1_TARGET
.. autodata:: core.universal_intelligence.K1_STRETCH_TARGET
.. autodata:: core.universal_intelligence.QUANTUM_ADVANTAGE_TARGET
.. autodata:: core.universal_intelligence.NEGATIVE_TRANSFER_THRESHOLD
.. autodata:: core.universal_intelligence.FORGETTING_THRESHOLD
.. autodata:: core.universal_intelligence.STRATEGIES
```
