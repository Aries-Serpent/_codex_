# Skills Module API Reference

**Version**: v0.2.1
**Last Updated:** 2026-07-11

**Module Path**: `src/codex/skills/`
**Version**: Phase 10+
**Purpose**: Skill registry, execution, discovery, and lifecycle management

---

## Overview

The Skills module provides a comprehensive framework for registering, discovering, executing, and managing skills (autonomous capabilities). It supports skill composition, capability matching, and execution envelopes.

## Core Classes

### SkillRegistry

Central registry for skill management and discovery.

```python
class SkillRegistry:
 """Central skill registry and discovery system.
 
 Manages skill registration, capability matching, versioning,
 and execution coordination.
 """
```

**Key Methods**:

#### `register_skill(skill_definition, version, capabilities=None)`

Register a new skill with the registry.

**Parameters**:
- `skill_definition` (SkillDefinition): Skill metadata and handlers
- `version` (str): Semantic version (e.g., "1.0.0")
- `capabilities` (List[str]): Capabilities provided by this skill

**Returns**: `SkillRegistration` with registration ID and metadata

**Example**:
```python
registry = SkillRegistry()

skill_def = SkillDefinition(
 name="code-analyzer",
 description="Analyzes code for quality issues",
 input_schema={"code": str, "language": str},
 output_schema={"issues": List[Issue], "score": float}
)

registration = registry.register_skill(
 skill_definition=skill_def,
 version="1.0.0",
 capabilities=["static-analysis", "code-quality"]
)
```

#### `find_skills_with_capability(capability)`

Find all skills providing a capability.

**Parameters**:
- `capability` (str): Capability name to search for

**Returns**: List of `SkillInfo` objects

**Example**:
```python
analysis_skills = registry.find_skills_with_capability("static-analysis")
for skill_info in analysis_skills:
 print(f"{skill_info.name} v{skill_info.version}")
```

#### `get_skill(skill_name, version=None)`

Retrieve a registered skill.

**Parameters**:
- `skill_name` (str): Skill identifier
- `version` (str, optional): Specific version (default: latest)

**Returns**: `SkillInfo` or None if not found

---

### ExecutionEnvelope

Encapsulates skill execution with input/output handling.

```python
class ExecutionEnvelope:
 """Skill execution container with IO management.
 
 Handles skill invocation, timeout management, error handling,
 and result validation.
 """
```

**Key Methods**:

#### `run()`

Execute the skill with configured inputs.

**Returns**: `ExecutionResult` with status, output, and metadata

**Example**:
```python
envelope = ExecutionEnvelope(
 skill_name="data-transform",
 inputs={"data": dataset, "format": "json"},
 timeout_seconds=300
)

result = envelope.run()

if result.status == ExecutionStatus.SUCCESS:
 output = result.get_output()
 print(f"Transformed data: {output}")
elif result.status == ExecutionStatus.TIMEOUT:
 print("Skill execution timed out")
elif result.status == ExecutionStatus.ERROR:
 print(f"Error: {result.get_error()}")
```

#### `get_output()`

Get execution result data.

**Returns**: Output dict matching skill's output schema

#### `get_error()`

Get error message if execution failed.

**Returns**: Error string or None if successful

#### `get_metadata()`

Get execution metadata (duration, resource usage, etc.).

**Returns**: `ExecutionMetadata` object

**Example**:
```python
result = envelope.run()
metadata = result.get_metadata()

print(f"Duration: {metadata.duration_ms}ms")
print(f"Memory used: {metadata.memory_used_mb}MB")
print(f"Retry count: {metadata.retry_count}")
```

---

### SkillDocLoader

Load and manage skill documentation and manifests.

```python
class SkillDocLoader:
 """Load and parse skill documentation.
 
 Handles manifest loading, documentation parsing,
 and example extraction.
 """
```

**Key Methods**:

#### `load_manifest(path)` (static)

Load a skill manifest from file.

**Parameters**:
- `path` (str): Path to manifest file (YAML or JSON)

**Returns**: `SkillManifest` object

**Example**:
```python
manifest = SkillDocLoader.load_manifest("skills/code-analyzer/manifest.yaml")

print(f"Skill: {manifest.name}")
print(f"Version: {manifest.version}")
print(f"Capabilities: {manifest.capabilities}")
print(f"Input: {manifest.input_schema}")
```

#### `load_many(paths)` (static)

Batch load multiple skill manifests.

**Parameters**:
- `paths` (List[str]): Paths to manifest files

**Returns**: List of `SkillManifest` objects

**Example**:
```python
manifests = SkillDocLoader.load_many([
 "skills/code-analyzer/manifest.yaml",
 "skills/test-generator/manifest.yaml",
 "skills/doc-writer/manifest.yaml"
])

for manifest in manifests:
 print(f"Loaded: {manifest.name}")
```

---

### AAISScorer

Evaluates skill quality using AI Agent Intuitiveness Score (AAIS).

```python
class AAISScorer:
 """Score skills using AAIS metrics.
 
 Evaluates skill quality, usability, and effectiveness
 against AAIS criteria.
 """
```

**Key Methods**:

#### `score(skill_info)`

Generate AAIS score for a skill.

**Parameters**:
- `skill_info` (SkillInfo): Skill to score

**Returns**: `AAISScore` with overall score and category breakdowns

**Example**:
```python
scorer = AAISScorer()
skill_info = registry.get_skill("code-analyzer")
aais_score = scorer.score(skill_info)

print(f"Overall AAIS Score: {aais_score.overall}/100")
print(f" Intuitiveness: {aais_score.intuitiveness}/100")
print(f" Reliability: {aais_score.reliability}/100")
print(f" Usability: {aais_score.usability}/100")

if aais_score.overall < 70:
 print(f"Warning: Low AAIS score. Issues: {aais_score.issues}")
```

---

## Function Signatures

```python
# Registry operations
def register_skill(
 skill_definition: SkillDefinition,
 version: str,
 capabilities: Optional[List[str]] = None
) -> SkillRegistration: ...

def find_skills_with_capability(
 capability: str
) -> List[SkillInfo]: ...

def get_skill(
 skill_name: str,
 version: Optional[str] = None
) -> Optional[SkillInfo]: ...

def list_all_skills(
 limit: int = 100,
 offset: int = 0
) -> List[SkillInfo]: ...

def unregister_skill(
 skill_name: str,
 version: Optional[str] = None
) -> bool: ...

# Execution
def run_skill(
 skill_name: str,
 inputs: Dict[str, Any],
 timeout_seconds: int = 300,
 retry_policy: Optional[RetryPolicy] = None
) -> ExecutionResult: ...

# Documentation
def load_manifest(path: str) -> SkillManifest: ...

def load_many_manifests(paths: List[str]) -> List[SkillManifest]: ...
```

---

## Usage Examples

### Example 1: Skill Registration and Discovery

```python
from codex.skills import SkillRegistry, SkillDefinition

registry = SkillRegistry()

# Define a skill
skill_def = SkillDefinition(
 name="test-generator",
 description="Generates unit tests from code",
 input_schema={
 "code": str,
 "test_framework": str,
 "coverage_target": int
 },
 output_schema={
 "tests": List[str],
 "coverage_estimate": float
 }
)

# Register it
registration = registry.register_skill(
 skill_definition=skill_def,
 version="1.0.0",
 capabilities=["test-generation", "unit-testing"]
)

print(f"Registered: {registration.skill_id}")

# Discover skills with test-generation capability
test_skills = registry.find_skills_with_capability("test-generation")
for skill in test_skills:
 print(f" - {skill.name} (v{skill.version})")
```

### Example 2: Skill Execution with Error Handling

```python
from codex.skills import ExecutionEnvelope, ExecutionStatus

def safe_skill_execution(skill_name, inputs, max_retries=3):
 for attempt in range(max_retries):
 try:
 envelope = ExecutionEnvelope(
 skill_name=skill_name,
 inputs=inputs,
 timeout_seconds=300
 )
 
 result = envelope.run()
 
 if result.status == ExecutionStatus.SUCCESS:
 return result.get_output()
 elif result.status == ExecutionStatus.TIMEOUT:
 print(f"Attempt {attempt+1}: Timeout")
 if attempt < max_retries - 1:
 continue
 raise TimeoutError(f"Skill {skill_name} timed out")
 else:
 error = result.get_error()
 print(f"Attempt {attempt+1}: {error}")
 if attempt < max_retries - 1:
 continue
 raise RuntimeError(f"Skill error: {error}")
 
 except Exception as e:
 if attempt == max_retries - 1:
 raise
 print(f"Attempt {attempt+1} failed: {e}, retrying...")
 time.sleep(2 ** attempt) # Exponential backoff
```

### Example 3: Batch Skill Loading

```python
from codex.skills import SkillDocLoader, SkillRegistry

# Load all skill manifests from a directory
loader = SkillDocLoader()
manifest_paths = glob.glob("skills/**/manifest.yaml")

manifests = loader.load_many(manifest_paths)
print(f"Loaded {len(manifests)} skills")

# Register all loaded skills
registry = SkillRegistry()
for manifest in manifests:
 registry.register_skill(
 skill_definition=SkillDefinition.from_manifest(manifest),
 version=manifest.version,
 capabilities=manifest.capabilities
 )
```

### Example 4: Skill Quality Scoring

```python
from codex.skills import AAISScorer, SkillRegistry

registry = SkillRegistry()
scorer = AAISScorer()

# Score all registered skills
all_skills = registry.list_all_skills()

high_quality_skills = []
for skill_info in all_skills:
 score = scorer.score(skill_info)
 
 print(f"{skill_info.name}: {score.overall}/100")
 
 if score.overall >= 80:
 high_quality_skills.append(skill_info)
 elif score.overall < 70:
 print(f" Low quality score. Issues: {score.issues}")

print(f"\nHigh-quality skills: {len(high_quality_skills)}")
```

---

## Best Practices

### 1. Skill Definition

```python
# GOOD: Clear, well-documented skill definition
skill_def = SkillDefinition(
 name="code-analyzer",
 description="Analyzes Python code for quality issues, complexity, and style violations",
 long_description="""
 Performs static analysis on Python code including:
 - Code quality metrics
 - Complexity analysis
 - PEP 8 compliance
 - Security vulnerability detection
 """,
 input_schema={
 "code": str, # Python source code
 "language": str, # Programming language
 "config": Dict # Analysis configuration
 },
 output_schema={
 "issues": List[CodeIssue],
 "metrics": CodeMetrics,
 "suggestions": List[str]
 },
 timeout_seconds=60,
 retry_policy=RetryPolicy(max_attempts=3, backoff_factor=2)
)

# POOR: Vague, undocumented definition
skill_def = SkillDefinition(
 name="analyzer",
 description="Analyzes code",
 input_schema={"data": Any},
 output_schema={"result": Any}
)
```

### 2. Execution with Timeout

```python
# GOOD: Proper timeout handling
envelope = ExecutionEnvelope(
 skill_name="long-running-analysis",
 inputs={"data": large_dataset},
 timeout_seconds=600 # 10 minute timeout
)

try:
 result = envelope.run()
except TimeoutError:
 logger.error("Skill execution exceeded timeout")
 # Handle gracefully - perhaps with partial results
 cleanup_resources()

# POOR: No timeout protection
envelope = ExecutionEnvelope(
 skill_name="long-running-analysis",
 inputs={"data": large_dataset}
 # No timeout specified - could hang indefinitely
)
```

### 3. Error Recovery

```python
# GOOD: Comprehensive error handling
def robust_skill_execution(skill_name, inputs):
 envelope = ExecutionEnvelope(
 skill_name=skill_name,
 inputs=inputs,
 timeout_seconds=300
 )
 
 try:
 result = envelope.run()
 
 if result.status == ExecutionStatus.SUCCESS:
 return result.get_output()
 else:
 error = result.get_error()
 logger.error(f"Skill execution failed: {error}")
 raise SkillExecutionError(error)
 
 except TimeoutError:
 logger.error(f"Skill {skill_name} timed out")
 raise
 except Exception as e:
 logger.exception(f"Unexpected error: {e}")
 raise

# POOR: No error handling
def unsafe_skill_execution(skill_name, inputs):
 envelope = ExecutionEnvelope(skill_name, inputs)
 return envelope.run().get_output() # Crashes on any error
```

---

## Related APIs

- [Agents API Reference](agents-api-reference.md)
- [Observability API Reference](observability-api-reference.md)
- [Brain API Reference](brain-api-reference.md)

---

**Last Updated**: 2026-07-08
**Status**: Phase 10+ (Active)
**Author**: Codex Skills Team

