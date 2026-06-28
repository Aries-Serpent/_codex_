# 📚 Codex ML: Structured Learning Paths

> **Version:** v0.1.0 Pre-Release  
> **Last Updated:** 2026-06-27  
> **Total Estimated Time:** 20-40 hours depending on path  

---

## 🎯 Choose Your Path

- **[Beginner Path](#beginner-path)** — 2-4 hours — Setup to first code contribution
- **[Intermediate Path](#intermediate-path)** — 6-8 hours — Extending components, custom models
- **[Advanced Path](#advanced-path)** — 10-16 hours — Architecture deep dive, optimization
- **[Specialized Paths](#specialized-paths)** — Variable — ML, Agents, Infrastructure focus

---

## Beginner Path

**Target Audience:** New developers, ML engineers new to this codebase  
**Time Commitment:** 2-4 hours  
**Prerequisites:** Python knowledge, basic ML concepts  

### Step 1: Installation & First Run (30 min)

**Goal:** Get the codebase running locally

1. **Read:** [Quick Start Guide](./ONBOARDING_QUICKSTART.md)
2. **Do:** Follow "Path 1: Local Development Setup"
3. **Verify:** Run the minimal example successfully
4. **Checkpoint:** Verify training logs appear in console

**Key Files:**
- `docs/ONBOARDING_QUICKSTART.md` — Setup instructions
- `config/examples/minimal.yaml` — Minimal config
- `examples/basic_training.py` — First example

**Deliverable:** Successful training run saved to `outputs/`

---

### Step 2: Navigate the Codebase (30 min)

**Goal:** Understand project structure

1. **Explore directory structure:**
   ```bash
   find src -type f -name "*.py" | head -20
   ls -la docs/
   ```

2. **Understand key directories:**
   - `src/codex/` — Main source code
   - `configs/` — Configuration files (Hydra)
   - `tests/` — Test suite
   - `docs/` — Documentation

3. **Read:** [Architecture Overview](./ARCHITECTURE.md) (skim first 20% to understand layers)

4. **Checkpoint:** Can you identify the 5 layers?

**Key Concepts:**
- Layer 1: Foundation & runtime
- Layer 2: Infrastructure & config
- Layer 3: ML pipeline
- Layer 4: Cognitive systems
- Layer 5: Presentation (CLI/API)

---

### Step 3: Understand Configuration (45 min)

**Goal:** Learn how to configure Codex ML with Hydra

1. **Read:** [Hydra Quick Start](./configuration/hydra_quickstart.md)

2. **Explore configs:**
   ```bash
   cat configs/base.yaml
   cat configs/train/base.yaml
   cat config/examples/minimal.yaml
   ```

3. **Hands-on: Modify a config**
   ```bash
   # Copy minimal config
   cp config/examples/minimal.yaml config/test.yaml
   
   # Edit: change batch_size
   # Run with custom config
   python -m codex.cli train --config config/test.yaml
   ```

4. **Checkpoint:** Can you run training with a custom batch size?

**Key Concepts:**
- Hydra defaults and composition
- Environment variable substitution
- Config overrides on command line

---

### Step 4: Run Your First Test (30 min)

**Goal:** Write and run a simple test

1. **Explore test structure:**
   ```bash
   ls tests/unit/
   cat tests/unit/test_imports.py
   ```

2. **Run existing tests:**
   ```bash
   pytest tests/unit/test_imports.py -v
   ```

3. **Write a simple test:**
   ```python# tests/unit/test_beginner.py
def test_codex_imports():
    from codex.cli import app
    assert app is not None

def test_config_loads():
    from hydra import compose, initialize
    from omegaconf import OmegaConf
    
    initialize(config_path="../../configs")
    cfg = compose(config_name="base")
    assert cfg is not None

```

4. **Run your test:**
   ```bash
   pytest tests/unit/test_beginner.py -v
   ```

4. **Checkpoint:** Test passes ✅

---

## ✅ Beginner Path Complete!

You've learned:
- ✅ How to set up Codex ML
- ✅ The 5-layer architecture
- ✅ How Hydra configuration works
- ✅ How to write basic tests

**Next:** Choose [Intermediate Path](#intermediate-path) or a [Specialized Path](#specialized-paths)

---

## Intermediate Path

**Target Audience:** Developers ready to extend Codex ML  
**Time Commitment:** 6-8 hours  
**Prerequisites:** Completed beginner path  

### Step 1: Understand Configuration Deep Dive (90 min)

**Goal:** Master Hydra configuration system

1. **Read:** [Hydra Advanced Guide](./configuration/hydra-advanced-guide.md)

2. **Hands-on: Create a custom model config**
   ```yaml
   # configs/models/my_model.yaml
   name: my-custom-model
   architecture: transformer
   hidden_size: 768
   num_layers: 12
   ```

3. **Hands-on: Create a custom training config**
   ```yaml
   # configs/train/my_experiment.yaml
   defaults:
     - base
     - models/my_model
   
   training:
     batch_size: 16
     learning_rate: 0.001
     warmup_steps: 100
   ```

4. **Test your configs:**
   ```bash
   python -m codex.cli train --config configs/train/my_experiment.yaml --help
   ```

5. **Checkpoint:** Can you override configs from command line?

---

### Step 2: Train a Custom Model (120 min)

**Goal:** Train your own model with custom configuration

1. **Choose a training script:**
   - Use existing: `python -m codex.cli train --config configs/train/base.yaml`
   - OR create custom: `examples/my_training.py`

2. **Create custom training script:**
   ```python# examples/my_training.py
from codex.training import Trainer
from hydra import compose, initialize

initialize(config_path="../configs")
cfg = compose(config_name="train/my_experiment")

trainer = Trainer(cfg)
trainer.train()

```

3. **Run training:**
   ```bash
   python examples/my_training.py
   ```

4. **Monitor training:**
   - Watch logs in `outputs/logs/`
   - Check checkpoint in `outputs/checkpoints/`

5. **Checkpoint:** Training completes successfully ✅

---

### Step 3: Evaluate & Debug (90 min)

**Goal:** Evaluate models and understand debugging tools

1. **Run evaluation:**
   ```bash
   python -m codex.cli eval --config configs/eval/base.yaml
   ```

2. **Understand metrics:**
   ```pythonfrom codex.evaluation import list_metrics
print(list_metrics())

```

3. **Debug training issues:**
   - Add print statements and use `--log-level DEBUG`
   - Profile memory with `memory_profiler`
   - Check logs in `outputs/logs/`

4. **Checkpoint:** Can you identify training metrics from logs?

---

### Step 4: Add a Custom Component (120 min)

**Goal:** Extend Codex ML with custom code

#### Option A: Add a custom metric

```python
# src/codex/evaluation/custom_metrics.py
from codex.evaluation.base import BaseMetric

@register_metric("my_metric")
class MyMetric(BaseMetric):
    def compute(self, predictions, references):
        # Your metric implementation
        return {"score": ...}
```

#### Option B: Add a custom model

```python
# src/codex/models/my_model.py
from codex.models.base import BaseModel

@register_model("my_model")
class MyModel(BaseModel):
    def __init__(self, config):
        super().__init__(config)
        # Your model implementation
        
    def forward(self, input_ids):
        # Your forward pass
        return output
```

#### Option C: Add a CLI command

```python
# src/codex/cli/my_command.py
import typer
from typing import Optional

app = typer.Typer()

@app.command()
def my_command(input_path: str = typer.Argument(...)):
    """My custom command."""
    # Your command logic
    typer.echo("Done!")
```

5. **Write tests for your component:**
   ```python# tests/unit/test_my_component.py
def test_my_component():
    from codex.evaluation.custom_metrics import MyMetric
    metric = MyMetric()
    result = metric.compute([1, 2], [1, 2])
    assert result["score"] > 0

```

6. **Checkpoint:** Tests pass ✅

---

## ✅ Intermediate Path Complete!

You've learned:
- ✅ Advanced Hydra configuration
- ✅ How to train custom models
- ✅ How to evaluate and debug
- ✅ How to extend Codex ML

**Next:** Choose [Advanced Path](#advanced-path) or a [Specialized Path](#specialized-paths)

---

## Advanced Path

**Target Audience:** Contributors, system architects  
**Time Commitment:** 10-16 hours  
**Prerequisites:** Completed intermediate path  

### Step 1: Architecture Deep Dive (120 min)

**Goal:** Understand the 5-layer architecture in detail

1. **Read:** [Complete Architecture Guide](./ARCHITECTURE.md)

2. **Map the architecture:**
   - Draw each layer on paper
   - Identify key components in each layer
   - Trace a request from Layer 5 → Layer 1

3. **Study design patterns:**
   - Plugin architecture (registry pattern)
   - Configuration composition (strategy pattern)
   - Memory management (observer pattern)

4. **Checkpoint:** Can you explain each layer's responsibility?

---

### Step 2: Cognitive Brain & Agents (150 min)

**Goal:** Understand autonomous agent systems

1. **Read:** [Agent Development Guide](../AGENTS.md)

2. **Explore agent system:**
   ```python
from codex.agents import list_agents
agents = list_agents()
print(f"Available agents: {len(agents)}")

for agent in agents[:5]:
    print(f"- {agent.name}: {agent.capabilities}")
```

3. **Create a simple agent:**
   ```python# src/codex/agents/my_agent.py
from codex.agents.base import BaseAgent

class MyAgent(BaseAgent):
    agent_id = "my-agent"
    capabilities = ["process", "analyze"]
    
    async def execute(self, task):
        # Your agent logic
        return {"result": "..."}

```

4. **Trigger agent execution:**
   ```pythonfrom codex.orchestration import get_orchestrator

orchestrator = get_orchestrator()
task_id = orchestrator.submit_to_agent(
    "my-agent", 
    {"input": "data"}
)
result = orchestrator.get_result(task_id)

```

5. **Checkpoint:** Can you explain agent orchestration?

---

### Step 3: Memory Systems (120 min)

**Goal:** Understand STM/LTM memory with compression

1. **Study memory architecture:**
   ```pythonfrom codex.memory import MemoryManager

memory = MemoryManager()

# Store a pattern
memory.store_pattern("pattern_id", pattern_data)

# Retrieve with ranking
results = memory.retrieve("query", k=5, rank_by="recency")

# Check compression stats
stats = memory.get_stats()
print(f"Compression ratio: {stats['compression_ratio']}")

```

2. **Implement custom memory patterns:**
   ```pythonfrom codex.memory.patterns import BasePattern

class MyPattern(BasePattern):
    def __init__(self, pattern_id, data):
        self.pattern_id = pattern_id
        self.data = data
    
    def compress(self):
        # 60% compression target
        return compressed_data

```

3. **Checkpoint:** Can you retrieve and store patterns?

---

### Step 4: Performance Optimization (120 min)

**Goal:** Optimize Codex ML for production

1. **Profile performance:**
   ```pythonimport cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative').print_stats(20)

```

2. **Memory optimization:**
   ```pythonimport tracemalloc

tracemalloc.start()

# Your code

current, peak = tracemalloc.get_traced_memory()
print(f"Peak: {peak / 1024 / 1024:.1f} MB")

```

3. **Optimize key bottlenecks:**
   - Data loading (batch size, workers)
   - Model inference (quantization, distillation)
   - Memory usage (gradient checkpointing)

4. **Benchmark improvements:**
   ```bash
   # Before optimization
   time python examples/training.py
   
   # After optimization
   time python examples/training.py
   ```

5. **Checkpoint:** Achieved 20%+ performance improvement ✅

---

### Step 5: Contributing to Core (120 min)

**Goal:** Make your first contribution to core

1. **Read:** [Contributing Guide](../CONTRIBUTING.md)

2. **Find a good first issue:**
   - Search GitHub issues for "good first issue"
   - Or pick a module to improve

3. **Create feature branch:**
   ```bash
   git checkout -b feature/my-improvement
   ```

4. **Make your changes:**
   - Update code
   - Add tests
   - Update documentation

5. **Run full test suite:**
   ```bash
   pytest tests/ -v --cov=src/codex
   ```

6. **Submit pull request:**
   - Clear description
   - Link related issues
   - Include test results

7. **Checkpoint:** PR merged ✅

---

## ✅ Advanced Path Complete!

You've learned:
- ✅ Complete 5-layer architecture
- ✅ Agent orchestration systems
- ✅ Memory-augmented reasoning
- ✅ Performance optimization
- ✅ Open-source contribution workflow

**Congratulations!** You're now a Codex ML expert! 🎉

---

## Specialized Paths

Choose a specialization based on your interests:

### 🤖 ML Engineering Path

**Time:** 6-8 hours  
**Focus:** Training, evaluation, optimization

1. **[Distributed Training](./training/distributed_training_guide.md)**
   - Multi-GPU training (DDP)
   - Parameter server approach
   - Gradient accumulation

2. **[Hyperparameter Tuning](./configuration/hydra_quickstart.md#sweeps)**
   - Hydra sweeper
   - Bayesian optimization
   - Experiment tracking

3. **[Model Evaluation](./guides/fairness_evaluation_guide.md)**
   - Custom metrics
   - Benchmarking
   - A/B testing

4. **[Model Serving](./guides/inference_server_guide.md)**
   - Ray Serve setup
   - Batch inference
   - Real-time serving

### 🏗️ Infrastructure & Deployment Path

**Time:** 6-8 hours  
**Focus:** DevOps, deployment, monitoring

1. **[Docker & Containerization](./docker_guide.md)**
   - Building images
   - Multi-stage builds
   - Image optimization

2. **[Kubernetes Deployment](./infrastructure/README.md)**
   - Pod configuration
   - Service setup
   - Auto-scaling

3. **[Cloud Integration](./infrastructure/README.md)**
   - S3/GCS storage
   - Cloud training
   - Monitoring and logging

4. **[CI/CD Pipelines](./CI.md)**
   - GitHub Actions setup
   - Testing automation
   - Deployment automation

### 🤖 Cognitive Systems & Agents Path

**Time:** 8-10 hours  
**Focus:** Agent design, decision-making, memory

1. **[Cognitive Brain Fundamentals](./cognitive_brain/INDEX.md)**
   - Quantum decision engine
   - Probability weighting
   - Decision-making architecture

2. **[Agent Development](./agent/OPERATIONAL_GUIDELINES.md)**
   - Creating custom agents
   - Task routing
   - Error handling

3. **[Memory Systems](./cognitive_brain/INDEX.md#memory)**
   - STM/LTM architecture
   - Pattern compression
   - Semantic retrieval

4. **[Agent Orchestration](./agent/OPERATIONAL_GUIDELINES.md#orchestration)**
   - Workflow definition
   - Task dependency graphs
   - Agent coordination

### 📊 Data & Testing Path

**Time:** 6-8 hours  
**Focus:** Data engineering, testing strategies

1. **[Data Loading & Processing](./data/INDEX.md)**
   - Dataset loading
   - Preprocessing
   - Data validation

2. **[Testing Strategies](./TESTING.md)**
   - Unit testing
   - Integration testing
   - End-to-end testing

3. **[Mutation Testing](./testing/ai_test_generation_guide.md)**
   - Mutmut setup
   - Coverage analysis
   - Test quality metrics

4. **[Continuous Monitoring](./operations/monitoring_guide.md)**
   - Metrics collection
   - Alerting
   - Dashboards

---

## Progress Tracking

Use this checklist to track your progress:

### Beginner Path
- [ ] Step 1: Installation complete
- [ ] Step 2: Project structure understood
- [ ] Step 3: Hydra configuration working
- [ ] Step 4: First test running
- [ ] Beginner path complete ✅

### Intermediate Path
- [ ] Step 1: Configuration mastered
- [ ] Step 2: Custom model trained
- [ ] Step 3: Evaluation working
- [ ] Step 4: Custom component added
- [ ] Intermediate path complete ✅

### Advanced Path
- [ ] Step 1: Architecture mastered
- [ ] Step 2: Agents understood
- [ ] Step 3: Memory systems explored
- [ ] Step 4: Performance optimized
- [ ] Step 5: Contribution submitted
- [ ] Advanced path complete ✅

---

## Resources by Topic

| Topic | Time | Resource |
|-------|------|----------|
| **Quick Start** | 15 min | [Onboarding](./ONBOARDING_QUICKSTART.md) |
| **Architecture** | 20 min | [Architecture Guide](./ARCHITECTURE.md) |
| **Configuration** | 30 min | [Hydra Guide](./configuration/HYDRA_GUIDE.md) |
| **Training** | 60 min | [Training Guide](./training/README.md) |
| **Evaluation** | 45 min | [Evaluation Guide](./guides/fairness_evaluation_guide.md) |
| **Agents** | 60 min | [Custom Agents](../AGENTS.md) |
| **Deployment** | 90 min | [Infrastructure Guide](./infrastructure/README.md) |
| **Contributing** | 30 min | [Contributing Guide](../CONTRIBUTING.md) |
| **Troubleshooting** | As-needed | [Troubleshooting Guide](./TROUBLESHOOTING.md) |

---

## Tips for Success

1. **Follow sequentially:** Each step builds on previous ones
2. **Do the hands-on:** Reading alone isn't enough; code along
3. **Ask for help:** Open issues or discussion threads if stuck
4. **Take notes:** Capture key concepts and learnings
5. **Contribute back:** Share what you've learned with others

---

## Get Help

- **Stuck on a step?** Check [Troubleshooting Guide](./TROUBLESHOOTING.md)
- **Need clarification?** Open a GitHub discussion
- **Found an error?** Submit a PR with the fix
- **Want to contribute?** Read [Contributing Guide](../CONTRIBUTING.md)

---

**Happy learning!** 🚀
