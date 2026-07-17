# Agents Module API Reference
**Last Updated:** 2026-07-11
**Version:** v0.2.0

**Module Path**: `src/codex/agents/`  
**Version**: Phase 10+  
**Purpose**: Multi-agent framework, capability management, task delegation

---

## Overview

The Agents module provides a framework for defining autonomous agents, managing their capabilities, and coordinating multi-agent teams. It enables capability-based task delegation and collective problem-solving.

## Core Classes

### Agent

Represents an autonomous agent with defined capabilities.

```python
class Agent:
    """Autonomous agent with capabilities.
    
    Agents can declare their capabilities and be coordinated
    by an Assemblage for collaborative task execution.
    """
```

**Key Methods**:

#### `__init__(name, capabilities=None)`

Initialize an agent.

**Parameters**:
- `name` (str): Unique agent identifier
- `capabilities` (List[Capability], optional): Initial capabilities

**Example**:
```python
agent = Agent(
    name="code-reviewer",
    capabilities=[
        AgentCapability(name="peer-review"),
        AgentCapability(name="design-review")
    ]
)
```

#### `add_capability(capability)`

Add a capability to this agent.

**Parameters**:
- `capability` (AgentCapability): Capability to add

#### `can_perform(task)`

Check if this agent can perform a task.

**Parameters**:
- `task` (str): Task name or description

**Returns**: bool

**Example**:
```python
if agent.can_perform("code-review"):
    result = agent.execute("code-review", task_data)
```

#### `execute(task, task_data, timeout=300)`

Execute a task.

**Parameters**:
- `task` (str): Task identifier
- `task_data` (dict): Task input data
- `timeout` (int): Execution timeout in seconds

**Returns**: `TaskResult`

---

### Assemblage

Multi-agent team coordinator.

```python
class Assemblage:
    """Multi-agent team coordinator.
    
    Aggregates capabilities from multiple agents and coordinates
    task delegation based on capability matching.
    """
```

**Key Methods**:

#### `__init__(name, agents=None)`

Initialize an assemblage.

**Parameters**:
- `name` (str): Team name
- `agents` (List[Agent], optional): Initial agents

#### `add_agent(agent)`

Add an agent to the team.

**Parameters**:
- `agent` (Agent): Agent to add

**Example**:
```python
team = Assemblage(name="code-quality-team")
team.add_agent(Agent(name="analyzer", capabilities=[...]))
team.add_agent(Agent(name="reviewer", capabilities=[...]))
```

#### `get_collective_capabilities()`

Get all capabilities from all agents.

**Returns**: List of `Capability` objects

**Example**:
```python
capabilities = team.get_collective_capabilities()
print(f"Team can perform: {[c.name for c in capabilities]}")
```

#### `can_accomplish(task)`

Check if team can accomplish a task.

**Parameters**:
- `task` (str): Task description

**Returns**: bool

**Example**:
```python
if team.can_accomplish("comprehensive-code-review"):
    result = team.delegate_task("comprehensive-code-review", data)
```

#### `delegate_task(task_name, task_data, strategy="optimal")`

Delegate a task to appropriate agent(s).

**Parameters**:
- `task_name` (str): Task identifier
- `task_data` (dict): Task input
- `strategy` (str): Delegation strategy ("optimal", "parallel", "sequential")

**Returns**: `TaskResult`

**Example**:
```python
# Single agent delegation
result = team.delegate_task(
    task_name="code-review",
    task_data={"repo": "...", "pr": 123},
    strategy="optimal"
)

# Parallel execution with multiple agents
result = team.delegate_task(
    task_name="comprehensive-analysis",
    task_data={"code": source},
    strategy="parallel"
)
```

---

### AssemblageMapper

Agent discovery and capability mapping.

```python
class AssemblageMapper:
    """Agent registry and discovery system.
    
    Maintains mappings between agents and their capabilities
    for efficient discovery and delegation.
    """
```

**Key Methods**:

#### `register_agent(agent, capabilities)`

Register an agent and its capabilities.

**Parameters**:
- `agent` (Agent): Agent to register
- `capabilities` (List[str]): Capability names provided by agent

**Example**:
```python
mapper = AssemblageMapper()
mapper.register_agent(
    agent=code_analyzer,
    capabilities=["static-analysis", "complexity-check", "security-scan"]
)
```

#### `find_agents_with_capability(capability)`

Find all agents with a specific capability.

**Parameters**:
- `capability` (str): Capability name

**Returns**: List of `Agent` objects

**Example**:
```python
analyzers = mapper.find_agents_with_capability("static-analysis")
for agent in analyzers:
    print(f"Agent: {agent.name}")
```

#### `find_agents_for_task(task_description)`

Find agents capable of performing a task.

**Parameters**:
- `task_description` (str): Task to perform

**Returns**: List of `Agent` objects with relevance scores

**Example**:
```python
agents = mapper.find_agents_for_task("perform code review")
for agent, score in agents:
    print(f"{agent.name}: {score*100:.1f}% match")
```

#### `unregister_agent(agent_id)`

Unregister an agent.

**Parameters**:
- `agent_id` (str): Agent identifier

---

## Function Signatures

```python
# Agent operations
def create_agent(
    name: str,
    capabilities: Optional[List[Capability]] = None
) -> Agent: ...

def can_perform_task(
    agent: Agent,
    task: str
) -> bool: ...

def execute_task(
    agent: Agent,
    task: str,
    task_data: Dict[str, Any],
    timeout_seconds: int = 300
) -> TaskResult: ...

# Assemblage operations
def create_assemblage(
    name: str,
    agents: Optional[List[Agent]] = None
) -> Assemblage: ...

def get_team_capabilities(
    assemblage: Assemblage
) -> List[Capability]: ...

def delegate_task(
    assemblage: Assemblage,
    task: str,
    task_data: Dict[str, Any],
    strategy: str = "optimal"
) -> TaskResult: ...

# Agent discovery
def register_agent(
    mapper: AssemblageMapper,
    agent: Agent,
    capabilities: List[str]
) -> None: ...

def find_agents_with_capability(
    mapper: AssemblageMapper,
    capability: str
) -> List[Agent]: ...

def find_agents_for_task(
    mapper: AssemblageMapper,
    task: str
) -> List[Tuple[Agent, float]]: ...
```

---

## Usage Examples

### Example 1: Building a Specialized Team

```python
from codex.agents import Agent, Assemblage, AgentCapability

# Create individual agents with specific capabilities
code_analyzer = Agent(
    name="code-analyzer",
    capabilities=[
        AgentCapability(name="static-analysis"),
        AgentCapability(name="complexity-analysis"),
        AgentCapability(name="security-scan")
    ]
)

test_generator = Agent(
    name="test-generator",
    capabilities=[
        AgentCapability(name="unit-test-generation"),
        AgentCapability(name="integration-test-generation")
    ]
)

documentation_writer = Agent(
    name="doc-writer",
    capabilities=[
        AgentCapability(name="api-documentation"),
        AgentCapability(name="example-generation")
    ]
)

# Build team
dev_team = Assemblage(name="development-team")
dev_team.add_agent(code_analyzer)
dev_team.add_agent(test_generator)
dev_team.add_agent(documentation_writer)

# Check team capabilities
capabilities = dev_team.get_collective_capabilities()
print(f"Team capabilities: {[c.name for c in capabilities]}")

# Check if team can accomplish a goal
if dev_team.can_accomplish("complete code review and testing"):
    print("Team is ready for task")
```

### Example 2: Task Delegation

```python
from codex.agents import Agent, Assemblage

# Setup team (from Example 1)
team = create_development_team()

# Delegate comprehensive code review
task_data = {
    "repo": "my-project",
    "branch": "feature/auth-refactor",
    "files": ["src/auth.py", "src/login.py"],
    "changes_summary": "Refactored authentication module"
}

result = team.delegate_task(
    task_name="comprehensive-code-review",
    task_data=task_data,
    strategy="optimal"  # Let system choose best agents
)

if result.success:
    print("Review completed successfully")
    print(f"Issues found: {result.data.get('issues_count', 0)}")
    print(f"Suggestions: {result.data.get('suggestions', [])}")
else:
    print(f"Review failed: {result.error}")
```

### Example 3: Agent Discovery and Registration

```python
from codex.agents import AssemblageMapper, Agent

mapper = AssemblageMapper()

# Register agents with their capabilities
analyzer = Agent(name="code-analyzer")
mapper.register_agent(
    agent=analyzer,
    capabilities=["static-analysis", "metrics", "complexity-check"]
)

reviewer = Agent(name="code-reviewer")
mapper.register_agent(
    agent=reviewer,
    capabilities=["peer-review", "architecture-review", "design-patterns"]
)

# Find agents for specific capability
analysts = mapper.find_agents_with_capability("static-analysis")
print(f"Agents with static-analysis: {[a.name for a in analysts]}")

# Find best agents for a task
best_agents = mapper.find_agents_for_task("analyze code quality")
for agent, relevance in best_agents:
    print(f"{agent.name}: {relevance*100:.0f}% relevant")
```

### Example 4: Parallel Task Execution

```python
from codex.agents import Assemblage, Agent

# Create team with independent analyzers
team = Assemblage(name="parallel-analysis-team")
for i in range(3):
    team.add_agent(Agent(
        name=f"analyzer-{i}",
        capabilities=[AgentCapability(name="parallel-analysis")]
    ))

# Split large task across agents
large_dataset = [...100,000 items...]
chunk_size = len(large_dataset) // 3

result = team.delegate_task(
    task_name="parallel-analysis",
    task_data={
        "chunks": [
            large_dataset[0:chunk_size],
            large_dataset[chunk_size:2*chunk_size],
            large_dataset[2*chunk_size:]
        ]
    },
    strategy="parallel"  # Execute on all agents in parallel
)

print(f"Processed {result.data['items_processed']} items")
print(f"Total duration: {result.data['duration_seconds']}s")
```

---

## Best Practices

### 1. Agent Design

```python
#  GOOD: Clear, specific capabilities
agent = Agent(
    name="security-analyzer",
    capabilities=[
        AgentCapability(
            name="vulnerability-scan",
            description="Scans code for security vulnerabilities",
            supported_languages=["python", "go", "rust"]
        ),
        AgentCapability(
            name="dependency-audit",
            description="Audits dependencies for known vulnerabilities"
        )
    ]
)

#  POOR: Vague, overly broad capabilities
agent = Agent(
    name="analyzer",
    capabilities=[
        AgentCapability(name="analysis"),  # Too vague
        AgentCapability(name="checking")   # What is being checked?
    ]
)
```

### 2. Team Composition

```python
#  GOOD: Balanced team with complementary skills
team = Assemblage(name="code-quality-team")

# Different specialists
team.add_agent(create_static_analyzer())      # Code quality
team.add_agent(create_security_scanner())     # Security
team.add_agent(create_performance_profiler()) # Performance
team.add_agent(create_test_coverage_checker()) # Testing

#  POOR: Redundant team with overlapping capabilities
team = Assemblage(name="team")
team.add_agent(create_generic_analyzer())  # Does everything vaguely
team.add_agent(create_generic_analyzer())  # Duplicate agent
team.add_agent(create_generic_analyzer())  # More duplication
```

### 3. Task Delegation Strategy

```python
#  GOOD: Appropriate strategy for task type
def delegate_tasks(team):
    # Independent analysis - parallelize
    result1 = team.delegate_task(
        task_name="parallel-analysis",
        task_data={...},
        strategy="parallel"
    )
    
    # Sequential workflow - maintain order
    result2 = team.delegate_task(
        task_name="build-then-test",
        task_data={...},
        strategy="sequential"
    )
    
    # Single best agent - optimal
    result3 = team.delegate_task(
        task_name="code-review",
        task_data={...},
        strategy="optimal"  # Use single best reviewer
    )

#  POOR: Wrong strategy for task
team.delegate_task(
    task_name="parallel-analysis",
    strategy="sequential"  # Wastes team capacity
)
```

---

## Related APIs

- [Skills API Reference](skills-api-reference.md)
- [Brain API Reference](brain-api-reference.md)
- [Observability API Reference](observability-api-reference.md)

---

**Last Updated**: 2026-07-08  
**Status**: Phase 10+ (Active)  
**Author**: Codex Agents Team

