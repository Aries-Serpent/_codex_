# Energy Conversion — Claudeclaw / Claude Code Autonomous Management Patterns

> **Version**: 1.0.0  
> **Created**: 2026-03-21  
> **Parent agent**: `.github/agents/energy-conversion-agent.md`  
> **Research basis**: Deep research synthesis of Claude Code autonomous agent
> architecture, MCP tool registry patterns, ReAct loop implementations, and
> multi-agent orchestration — correlated to the EC system domain.
>
> **Abbrevs**: G2E = gas-to-electric · EC = energy conversion · PD = power distribution
> · CR = compute-regulated · HITL = human-in-the-loop · RPi = Raspberry Pi · SBC = single-board computer
> · EM = energy management · EMS = energy management system · OTA = over-the-air

---

## Overview

"Claudeclaw" refers to the Claude Code autonomous agent pattern family —
specifically the architectural conventions pioneered by Anthropic's Claude Code
and related open-source implementations. These patterns are adapted here for
autonomous management of the G2E conversion system running
on RPi/SBC hardware.

The core insight: the same **Think → Decide → Act → Observe** (ReAct) loop that
powers Claude Code for software development applies directly to energy control
pipelines — replacing file edits with actuator setpoints and code searches with
sensor queries.

---

## 1. ReAct Loop — Energy Control Adaptation

### Pattern: Think-Decide-Act-Observe

*Research basis: Anthropic (2025) — "How the agent loop works"; Dextral Labs (2026)*

The standard Claudeclaw ReAct loop is adapted as follows for EM:

| ReAct Phase | Software Agent (Claude Code) | Energy Agent (this system) |
|-------------|------------------------------|---------------------------|
| **Think** | Reason about codebase state | Reason about sensor readings + forecasts |
| **Decide** | Choose next edit / tool call | Choose setpoint change or hold |
| **Act** | Write file / run test | Command throttle / relay / breaker |
| **Observe** | Read test output / linter | Read new sensor values + power meter |

### Codebase Pattern

```python
# src/codex/energy/autonomous/react_loop.py
from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class AgentState:
    """Persistent agent context across ReAct iterations."""
    task: str
    history: List[Dict[str, Any]] = field(default_factory=list)
    iteration: int = 0
    max_iterations: int = 20
    done: bool = False

    def record(self, phase: str, content: Any) -> None:
        self.history.append({"iteration": self.iteration, "phase": phase, "content": content})

class EnergyReActLoop:
    """
    Claudeclaw-style ReAct loop for autonomous EC mgmt.

    References:
        Anthropic. (2025). How the agent loop works. Claude API Docs.
        https://platform.claude.com/docs/en/agent-sdk/agent-loop
    """

    def __init__(self, tools: "ToolRegistry", planner: "EnergyPlanner"):
        self.tools = tools
        self.planner = planner

    def run(self, task: str) -> AgentState:
        state = AgentState(task=task)
        while not state.done and state.iteration < state.max_iterations:
            state.iteration += 1
            # THINK: reason about current system state
            plan = self._think(state)
            state.record("think", plan)
            # DECIDE: select next tool / action
            action = self._decide(plan, state)
            state.record("decide", action)
            if action is None:
                state.done = True
                break
            # ACT: execute the action via tool registry
            result = self._act(action)
            state.record("act", {"action": action, "result": result})
            # OBSERVE: incorporate result into context
            self._observe(result, state)
            state.record("observe", result)
            logger.info("[iter=%d] %s → %s", state.iteration, action["tool"], result)
        return state

    def _think(self, state: AgentState) -> Dict[str, Any]:
        return self.planner.plan(state)

    def _decide(self, plan: Dict[str, Any], state: AgentState) -> Optional[Dict[str, Any]]:
        return plan.get("next_action")

    def _act(self, action: Dict[str, Any]) -> Any:
        tool_fn = self.tools.get(action["tool"])
        return tool_fn(**action.get("params", {}))

    def _observe(self, result: Any, state: AgentState) -> None:
        self.planner.update_context(result, state)
```

---

## 2. MCP Tool Registry — Energy Domain Adapters

### Pattern: Unified Tool Registry

*Research basis: Anthropic MCP Spec (2025); Alex Op (2025) Claude Code Full Stack*

The Model Context Protocol (MCP) defines a universal interface for agent tool
registration. For the energy system, each sensor driver and SCADA adapter is
registered as an MCP-compatible tool with explicit input/output schemas.

```python
# src/codex/energy/autonomous/tool_registry.py
from typing import Any, Callable, Dict, Optional
from dataclasses import dataclass

@dataclass
class ToolSchema:
    name: str
    description: str
    input_schema: Dict[str, Any]   # JSON-Schema compatible
    output_schema: Dict[str, Any]
    req_approval: bool = False  # HITL for risky ops

class ToolRegistry:
    """
    MCP-compatible tool registry for energy system actors.

    References:
        Oikon, D. (2025). Enhancing Claude Code with MCP servers and subagents.
        dev.to. https://dev.to/oikon/enhancing-claude-code-with-mcp-servers-and-subagents
    """
    _tools: Dict[str, Callable] = {}
    _schemas: Dict[str, ToolSchema] = {}

    def register(self, schema: ToolSchema):
        """Decorator: register a callable as an MCP tool."""
        def decorator(fn: Callable) -> Callable:
            self._tools[schema.name] = fn
            self._schemas[schema.name] = schema
            return fn
        return decorator

    def get(self, name: str) -> Callable:
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' not registered in ToolRegistry")
        return self._tools[name]

    def list_tools(self) -> Dict[str, ToolSchema]:
        return dict(self._schemas)

# --- Energy domain tool registrations ---

ENERGY_TOOLS = ToolRegistry()

@ENERGY_TOOLS.register(ToolSchema(
    name="read_gas_sensor",
    description="Read current gas concentration in PPM from MQ-6 sensor via SPI",
    input_schema={"type": "object", "properties": {"channel": {"type": "integer"}},
                  "required": ["channel"]},
    output_schema={"type": "object", "properties": {
        "ppm": {"type": "number"}, "voltage": {"type": "number"}}},
))
def read_gas_sensor(channel: int = 0) -> Dict[str, float]:
    from codex.energy.hardware.gas_sensor import MQ6SensorSPI
    reading = MQ6SensorSPI(channel=channel).read()
    return {"ppm": reading.concentration_ppm or 0.0, "voltage": reading.voltage}

@ENERGY_TOOLS.register(ToolSchema(
    name="read_power_meter",
    description="Read real-time electrical output from PZEM-004T energy meter",
    input_schema={"type": "object", "properties": {"port": {"type": "string"}}},
    output_schema={"type": "object", "properties": {
        "voltage_v": {"type": "number"}, "power_w": {"type": "number"},
        "energy_kwh": {"type": "number"}, "frequency_hz": {"type": "number"}}},
))
def read_power_meter(port: str = "/dev/ttyUSB0") -> Dict[str, float]:
    from codex.energy.hardware.pzem_meter import PZEM004TMeter
    r = PZEM004TMeter(port).read()
    return {"voltage_v": r.voltage_v, "power_w": r.power_w,
            "energy_kwh": r.energy_kwh, "frequency_hz": r.frequency_hz}

@ENERGY_TOOLS.register(ToolSchema(
    name="set_throttle",
    description="Command generator throttle position (0–100%)",
    input_schema={"type": "object",
                  "properties": {"position_pct": {"type": "number", "minimum": 0, "maximum": 100}},
                  "required": ["position_pct"]},
    output_schema={"type": "object", "properties": {"accepted": {"type": "boolean"}}},
    req_approval=False,   # within safe operating envelope
))
def set_throttle(position_pct: float) -> Dict[str, bool]:
    from codex.energy.control.pid_controller import ThrottleActuator
    ThrottleActuator().set(position_pct)
    return {"accepted": True}

@ENERGY_TOOLS.register(ToolSchema(
    name="trigger_fuel_cutoff",
    description="Emergency fuel solenoid cutoff. IRREVERSIBLE until manual reset.",
    input_schema={"type": "object",
                  "properties": {"reason": {"type": "string"}}, "required": ["reason"]},
    output_schema={"type": "object", "properties": {"cutoff_activated": {"type": "boolean"}}},
    req_approval=True,   # HITL required
))
def trigger_fuel_cutoff(reason: str) -> Dict[str, bool]:
    import RPi.GPIO as GPIO
    GPIO.output(17, GPIO.HIGH)   # relay: normally-closed solenoid
    return {"cutoff_activated": True}
```

---

## 3. Subagent Orchestration

### Pattern: Specialized Parallel Subagents

*Research basis: SitePoint (2025) Claude Code Agent Teams; Chiang (2025)*

Claude Code Agent Teams use multiple subagents with isolated context windows
and defined roles. The energy system maps each role to a bounded domain:

```
┌──────────────────────────────────────────────────────────────┐
│                   MetaController (Orchestrator)              │
│   Routes tasks, resolves conflicts, owns .codex/archive/deprecated/CLAUDE.md context   │
└────────┬─────────────────┬────────────────┬──────────────────┘
         │                 │                │                │
    ┌────▼────┐       ┌────▼────┐    ┌─────▼─────┐   ┌─────▼─────┐
    │ Sensor  │       │Optimizer│    │ Reporter  │   │  Safety   │
    │ Reader  │       │ Agent   │    │  Agent    │   │ Monitor   │
    │(poll    │       │(dispatch│    │(MQTT/dash)│   │(fault     │
    │ sensors)│       │ LP/GA)  │    │           │   │ detection)│
    └─────────┘       └─────────┘    └───────────┘   └───────────┘
```

```python
# src/codex/energy/autonomous/subagents.py
import asyncio
import logging
from abc import ABC, abstractmethod
from codex.energy.autonomous.tool_registry import ENERGY_TOOLS

logger = logging.getLogger(__name__)

class BaseSubagent(ABC):
    """Single-responsibility subagent with its own bounded context."""
    name: str

    @abstractmethod
    async def run_cycle(self) -> dict:
        """Execute one control cycle; return results dict."""

class SensorReaderAgent(BaseSubagent):
    """Continuously polls all sensors; publishes readings to shared queue."""
    name = "sensor-reader"
    POLL_INTERVAL_S = 1.0

    async def run_cycle(self) -> dict:
        gas  = ENERGY_TOOLS.get("read_gas_sensor")(channel=0)
        pwr  = ENERGY_TOOLS.get("read_power_meter")()
        readings = {**gas, **pwr}
        logger.debug("[%s] %s", self.name, readings)
        return readings

class OptimizerAgent(BaseSubagent):
    """Runs dispatch optimization; outputs throttle setpoints."""
    name = "optimizer"

    async def run_cycle(self) -> dict:
        from codex.energy.ai_optimizer import AIOptimizer
        optimizer = AIOptimizer()
        setpoint = optimizer.compute_optimal_throttle()
        ENERGY_TOOLS.get("set_throttle")(position_pct=setpoint)
        return {"throttle_pct": setpoint}

class SafetyMonitorAgent(BaseSubagent):
    """Continuously checks fault conditions; escalates or trips on violation."""
    name = "safety-monitor"
    GAS_LIMIT_PPM = 5_000   # early-warning: ~20% of LPG LEL (0.5% vol)
    FREQ_DEVIATION_HZ = 0.5

    async def run_cycle(self) -> dict:
        gas = ENERGY_TOOLS.get("read_gas_sensor")(channel=0)
        pwr = ENERGY_TOOLS.get("read_power_meter")()
        faults = []
        if gas["ppm"] > self.GAS_LIMIT_PPM:
            faults.append(f"gas_over_limit: {gas['ppm']:.0f} ppm")
            ENERGY_TOOLS.get("trigger_fuel_cutoff")(reason=faults[-1])
        if abs(pwr["frequency_hz"] - 60.0) > self.FREQ_DEVIATION_HZ:
            faults.append(f"freq_deviation: {pwr['frequency_hz']:.2f} Hz")
        return {"faults": faults}

class MetaController:
    """
    Orchestrates all subagents; adapts Claudeclaw multi-agent team pattern.

    References:
        SitePoint. (2025). Claude Code Agent Teams: Run parallel AI agents.
        https://www.sitepoint.com/anthropic-claude-code-agent-teams/
    """
    def __init__(self):
        self.subagents: list[BaseSubagent] = [
            SensorReaderAgent(),
            OptimizerAgent(),
            SafetyMonitorAgent(),
        ]

    async def run(self):
        """Run all subagents concurrently in an infinite control loop."""
        while True:
            tasks = [asyncio.create_task(a.run_cycle()) for a in self.subagents]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for agent, result in zip(self.subagents, results):
                if isinstance(result, Exception):
                    logger.error("[%s] cycle error: %s", agent.name, result)
            await asyncio.sleep(1.0)
```

---

## 4. Context Management (.codex/archive/deprecated/CLAUDE.md Equivalent)

### Pattern: Persistent Agent Knowledge Base

*Research basis: Softcery (2025) Agentic Coding Best Practices;  
Cometapi (2025) Managing Claude Code's Context*

Claude Code uses `.codex/archive/deprecated/CLAUDE.md` as a persistent context document injected into
every agent session. The energy system equivalent is:

**File**: `src/codex/energy/AGENT_CONTEXT.md` (auto-loaded by `MetaController`)

```markdown
# Energy Conversion Agent — Session Context

## System Configuration
- Hardware: RPi 4 (4 GB) + MCP3008 ADC + PZEM-004T
- Gas: natural gas, LHV = 47,100 kJ/kg
- Generator rated output: 500 W at 60 Hz / 120 V
- Nominal throttle: 75% at full load

## Operating Envelopes
- Gas concentration fault threshold: 5,000 ppm (early-warning, ~20% of LPG LEL; LEL ≈ 21,000 ppm / 2.1% vol)
- Frequency: 60.0 Hz ± 0.5 Hz
- Voltage: 120 V ± 10%
- Conversion efficiency baseline: 35–42% (measured 2026-03)

## Known Patterns
- At cold start (<5 min runtime), efficiency reads 5–10% low — discard
- PZEM-004T returns 0 W for loads < 1 W — filter before calculations
- MQ-6 reading stabilizes after 30 s warm-up period

## Escalation Protocol
- Faults P0 (gas over LEL, freq out of range): immediate fuel cutoff + alert
- Faults P1 (efficiency < 20%): alert + recommend shutdown
- Faults P2 (forecast MAPE > 10%): retrain AI model, advisory only
```

---

## 5. Session Continuity and Artifact Passing

### Pattern: Checkpoint + Handoff

*Research basis: Anthropic Engineering. (2025). Effective harnesses for  
long-run agents. https://www.anthropic.com/engineering/effective-harnesses-for-long-run-agents*

For long-run EM sessions, the agent maintains checkpoint
files so context is preserved across restarts (power cycling of the RPi, OTA
updates, etc.):

```python
# src/codex/energy/autonomous/checkpoint.py
import json
from pathlib import Path
from datetime import datetime, timezone
from codex.utils.path_utils import windows_safe_timestamp

CHECKPOINT_DIR = Path(".codex/energy_checkpoints")
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

def save_checkpoint(state: dict) -> Path:
    """Write agent state to a timestamped checkpoint file."""
    fname = CHECKPOINT_DIR / f"checkpoint_{windows_safe_timestamp('compact')}.json"
    state["saved_at"] = datetime.now(timezone.utc).isoformat()
    fname.write_text(json.dumps(state, indent=2))
    return fname

def load_latest_checkpoint() -> dict | None:
    """Load the most recent checkpoint if available."""
    files = sorted(CHECKPOINT_DIR.glob("checkpoint_*.json"))
    if not files:
        return None
    return json.loads(files[-1].read_text())
```

---

## 6. Security & Permission Gates

### Pattern: Human-in-Loop Approval for Risky Tools

*Research basis: Collabnix. (2025). Claude and Autonomous Agents: Practical
Implementation Guide.
https://collabnix.com/claude-and-autonomous-agents-practical-implementation-guide/*

Tools marked `req_approval=True` in the registry are intercepted before
execution and routed through an approval gate:

```python
# src/codex/energy/autonomous/approval_gate.py
import logging
from codex.energy.autonomous.tool_registry import ToolRegistry

logger = logging.getLogger(__name__)

class ApprovalGate:
    """
    HITL gate for risky tool executions.
    In production: sends push notification; waits for TOTP-signed approval.
    In simulation: logs warning and proceeds (simulation mode only).
    """
    def __init__(self, registry: ToolRegistry, simulation_mode: bool = False):
        self._registry = registry
        self._simulation = simulation_mode

    def execute(self, tool_name: str, params: dict):
        schema = self._registry.list_tools().get(tool_name)
        if schema and schema.req_approval and not self._simulation:
            logger.warning("APPROVAL REQUIRED for '%s' — awaiting operator", tool_name)
            self._send_approval_request(tool_name, params)
            approved = self._await_operator_response(timeout_s=30)
            if not approved:
                raise PermissionError(f"Operator rejected '{tool_name}' execution")
        fn = self._registry.get(tool_name)
        return fn(**params)

    def _send_approval_request(self, tool_name: str, params: dict) -> None:
        # In production: push notification via Pushover/PagerDuty/MQTT alert topic
        logger.critical("APPROVAL REQUEST: %s(%s)", tool_name, params)

    def _await_operator_response(self, timeout_s: int = 30) -> bool:
        # In production: poll approval endpoint or listen on MQTT control topic
        import time; time.sleep(timeout_s)
        return False  # default: deny if no response
```

---

## 7. APA Citation Library — Autonomous Agent Research

Anthropic. (2025). *How the agent loop works*. Claude Platform API Docs.
https://platform.claude.com/docs/en/agent-sdk/agent-loop

Anthropic Engineering. (2025). *Effective harnesses for long-run agents*.
https://www.anthropic.com/engineering/effective-harnesses-for-long-run-agents

Chiang, E. (2025). *My study notes on Anthropic Claude Code*.
https://www.ernestchiang.com/en/notes/ai/claude-code/

Collabnix. (2025). *Claude and autonomous agents: Practical implementation
guide*. https://collabnix.com/claude-and-autonomous-agents-practical-implementation-guide/

Dextral Labs. (2026). *Claude AI agents: Architecture & deployment guide 2026*.
https://dextralabs.com/blog/claude-ai-agents-architecture-deployment-guide/

Oikon, D. (2025). *Enhancing Claude Code with MCP servers and subagents*.
dev.to. https://dev.to/oikon/enhancing-claude-code-with-mcp-servers-and-subagents

Op, A. (2025). *Understanding Claude Code's full stack: MCP, skills, subagents*.
https://alexop.dev/posts/understanding-claude-code-full-stack/

Softcery. (2025). *Agentic coding with Claude Code and Cursor: Context files,
workflows, working memory*.
https://softcery.com/lab/softcerys-guide-agentic-coding-best-practices

SitePoint. (2025). *Claude Code Agent Teams: Run parallel AI agents on your
codebase*. https://www.sitepoint.com/anthropic-claude-code-agent-teams/

Zilliz. (2025). *claude-context: Code search MCP for Claude Code* [Software].
GitHub. https://github.com/zilliztech/claude-context

---

## 8. Summary: Claudeclaw Pattern Map → Energy System

| Claudeclaw Pattern | Energy System Implementation |
|-------------------|------------------------------|
| ReAct agent loop | `EnergyReActLoop` — sensor → plan → setpoint → observe |
| MCP tool registry | `ToolRegistry` — sensor drivers, SCADA adapters, actuators |
| `.codex/archive/deprecated/CLAUDE.md` context | `src/codex/energy/AGENT_CONTEXT.md` — system config + baselines |
| Subagent teams | `MetaController` + 3 specialized subagents (async) |
| Checkpoint harness | `save_checkpoint()` / `load_latest_checkpoint()` — RPi OTA safe |
| HITL gate | `ApprovalGate` — `req_approval=True` for fuel cutoff |
| Context compaction | EMA filtering on sensor data; rolling 24h history window |
| Semantic search | `TopologyManager.find_by_concept("energy conversion")` |
