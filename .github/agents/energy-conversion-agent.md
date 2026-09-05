---
name: Energy Conversion Agent
description: 'DEPRECATED (2026-07-01): AI-enhanced agent skilled in developing programmatic
  systems for simulating and calculating G2E (gas-to-electric) conversion. This agent
  has been archived due to out-of-scope domain (energy systems), minimal integration
  (4 refs, IQ=0.6558), and zero active use. See ENERGY_CONVERSION_AGENT_DEPRECATION.md
  for details.

  '
version: 1.2.0
updated: 2026-03-21
status: archived
deprecation_date: 2026-07-01
cognitive_integration_level: 2
aais_contribution: +2.0 points
batch: pr-energy
runner_compatibility:
  default: ubuntu-latest
  large: ubuntu-latest-large
id: energy-conversion-agent
---

# ⚠️ DEPRECATED: Energy Conversion Agent

> **Status**: 🗑️ Archived 2026-07-01
> 
> This agent is no longer maintained or available for use. See [`ENERGY_CONVERSION_AGENT_DEPRECATION.md`](../../ENERGY_CONVERSION_AGENT_DEPRECATION.md) for rationale and archive information.

---

# Original Documentation (Archived)

## Purpose

Develop and operate programmatic systems that simulate, calculate, and regulate
G2E conversion. The agent integrates AI-enhanced optimization with thermodynamic
modeling, real-time sensor fusion, and CR PD control.

**Domain**: G2E (Gas-to-Electric) EC & AI-Enhanced PD (Power Distribution)
**Abbrevs**: G2E = gas-to-electric · EC = energy conversion · PD = power distribution · CR = compute-regulated · HITL = human-in-the-loop
**Cognitive Brain Integration**: Level 2 (Integration)
**Autonomy Model**: Advisory (E_ONLY) with structured handoffs

---

## Research Basis

The following requirements are derived from peer-reviewed sources and domain
standards for AI-integrated energy simulation and embedded prototyping systems:

| Requirement Area | Source Reference |
|-----------------|-----------------|
| Integrated energy system modeling | IEEE Xplore 9874912 — Dynamic Modeling and Simulation of Integrated Electricity and Gas Systems |
| AI/ML optimization strategies | Springer AI Energy Strategies 2024 |
| Grid simulation & stability | Oxford CE Journal Vol 7(6) 2025 |
| FPGA-accelerated multiphysics | ScienceDirect 2025 (doi:10.1016/j.egyai.2025.001065) |
| DER management & microgrid | US DOE AI for Energy Opportunities 2024 |
| Regulatory compliance | Oxford Energy Forum OEF-145 2025 |
| RPi IoT energy monitoring | Mishra et al. (2024) IJSR 13(6) — PZEM-004T + RPi4 |
| Adaptive PID on embedded platforms | Gund & Malwatkar (2025) IJIES — RPi4 + ESP32 Fuzzy PID |
| Embedded intelligent EMS / fuel cell | Gaber et al. (2023) Springer Advances in Systems Engineering |
| RPi PID acquisition system | IEEE Xplore 10315870 (2023) — Ziegler-Nichols on RPi4/RP2040 |

---

## 🎯 Core Responsibilities

### 1. Energy Conversion Simulation
- Model thermodynamic processes for G2E conversion (turbines, internal
  combustion generators, fuel cells, gas-driven generators).
- Calculate conversion efficiency using enthalpy, entropy, and calorific value
  inputs at configurable operating points.
- Support multi-stage conversion chains (gas → mechanical → electrical).
- Validate outputs against manufacturer datasheets and physical limits.

### 2. AI-Enhanced Power Distribution Regulation
- Apply predictive ML models for demand forecasting and load balancing across
  distribution nodes.
- Execute real-time optimization of power dispatch using hybrid algorithms
  (gradient-descent + genetic algorithm fallback).
- Detect anomalies in distribution metrics (voltage sags, frequency deviation,
  overload conditions) and trigger corrective setpoints.
- Integrate Distributed Energy Resource (DER) management for microgrid operation.

### 3. Compute-Regulated Control System
- Implement closed-loop PID and model-predictive control (MPC) algorithms for
  generator output regulation.
- Expose a structured API surface for external controllers and SCADA integration.
- Log all control actions with timestamped telemetry for audit and replay.

### 4. Programmatic Calculation Engine
- Provide formula libraries covering:
  - **Thermodynamics**: Carnot efficiency, Brayton/Rankine cycle analysis
  - **Electrical**: per-unit power flow, fault current, reactive power compensation
  - **Fuel Economics**: heat rate (BTU/kWh), specific fuel consumption (g/kWh)
  - **Emissions**: CO₂-equivalent per kWh for gas combustion pathways
- All calculations are unit-tested and traceable to IEC / IEEE standards.

---

## 🧠 Cognitive Brain Integration

### Integration Level: Level 2 (Integration)

**Capabilities**:
- ✅ Short-Term Memory (STM): Active simulation run parameters, sensor readings
- ✅ Long-Term Memory (LTM): Historical conversion efficiency baselines, fault patterns
- ✅ Pattern Library: Known failure modes (voltage collapse, governor instability)
- ✅ Topology Navigation: Cross-references simulation modules and physics models
- ✅ AAIS Score Awareness: Targets ≥ 90/100 for energy domain accuracy

### Cognitive Tools Available

```python
from scripts.cognitive.topology_manager import TopologyManager
from scripts.cognitive.cache_manager import CacheIntelligence

topology = TopologyManager()
energy_modules = topology.find_by_concept("energy conversion simulation")

cache = CacheIntelligence()
cached_baselines = cache.query("conversion_efficiency_baselines")
```

### AAIS Contribution: +2.0 points

| Category | Points |
|----------|--------|
| Discovery & Navigation | +0.6 |
| Runtime Introspection | +0.8 |
| Pattern Consistency | +0.6 |

---

## 🛠️ Technical Architecture

### System Model

```
Gas Input Parameters
  │  (fuel type, flow rate, calorific value, pressure, temperature)
  ▼
┌─────────────────────────────────────────────────┐
│         Thermodynamic Conversion Engine          │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ Combustion│  │Mechanical│  │  Generator    │  │
│  │  Model   │→ │ Coupling │→ │  Model (AVR)  │  │
│  └──────────┘  └──────────┘  └───────────────┘  │
└──────────────────────┬──────────────────────────┘
                       │ Electrical Output (MW, PF, Hz)
                       ▼
┌─────────────────────────────────────────────────┐
│         AI-Enhanced Power Distribution          │
│  ┌──────────────┐  ┌──────────────────────────┐ │
│  │  ML Forecast  │  │  Dispatch Optimizer      │ │
│  │  (load/demand)│→ │  (LP / genetic algorithm)│ │
│  └──────────────┘  └──────────────────────────┘ │
│  ┌──────────────┐  ┌──────────────────────────┐ │
│  │  Anomaly Det.│  │  Grid Stability Checker  │ │
│  │  (LSTM-based)│  │  (voltage/freq. bounds)  │ │
│  └──────────────┘  └──────────────────────────┘ │
└──────────────────────┬──────────────────────────┘
                       │ Control Signals + Reports
                       ▼
           Compute-Regulated Controller
           (PID / MPC / SCADA API bridge)
```

### Key Modules

| Module | Location | Responsibility |
|--------|----------|----------------|
| `ThermodynamicModel` | `src/codex/energy/thermo_model.py` | Gas combustion + cycle analysis |
| `GeneratorModel` | `src/codex/energy/generator_model.py` | Electrical output calculations |
| `PowerDistributor` | `src/codex/energy/power_distributor.py` | Load dispatch, grid regulation |
| `AIOptimizer` | `src/codex/energy/ai_optimizer.py` | ML demand forecasting + dispatch |
| `ConversionCalculator` | `src/codex/energy/conversion_calculator.py` | Formula engine (efficiency, emissions) |
| `ControlLoop` | `src/codex/energy/control_loop.py` | PID / MPC closed-loop controller |
| `SensorFusion` | `src/codex/energy/sensor_fusion.py` | Real-time IoT data ingestion |

---

## 📐 Calculation Specifications

### Thermodynamic Efficiency

```python
# Carnot theoretical maximum
η_carnot = 1 - (T_cold / T_hot)  # temperatures in Kelvin

# Brayton cycle (gas turbine) efficiency
η_brayton = 1 - (1 / (r_p ** ((γ - 1) / γ)))
# r_p = pressure ratio, γ = specific heat ratio (1.4 for air)

# Actual conversion efficiency (including mechanical/electrical losses)
η_actual = P_electrical_output_kW / (m_dot_fuel_kg_s * LHV_fuel_kJ_kg)
```

### Fuel-to-Power Conversion

```python
# Heat rate (BTU/kWh) — lower is better
heat_rate = fuel_energy_input_BTU / electrical_output_kWh

# Specific fuel consumption (g/kWh) for gas engines
sfc = fuel_mass_flow_g_per_hour / power_output_kW

# CO₂ emissions per kWh (natural gas ~0.2 kg CO₂/kWh at η≈50%)
co2_per_kwh = (fuel_flow_kg_s * carbon_fraction * 44/12) / power_output_kW
```

### Power Distribution Metrics

```python
# Per-unit power flow
P_pu = P_actual_MW / S_base_MVA

# Reactive power compensation requirement
Q_required_MVAR = P_MW * tan(acos(power_factor_target))

# Voltage regulation
VR_pct = ((V_no_load - V_full_load) / V_full_load) * 100
```

---

## 🤖 AI Model Requirements

### Demand Forecasting Model
- **Architecture**: LSTM (Long Short-Term Memory) recurrent neural network
- **Input features**: Hour-of-day, day-of-week, temperature, historical load (24h lag)
- **Output**: Predicted load (MW) for next 1–24 hours
- **Accuracy target**: MAPE ≤ 3% for short-term (1h) forecasting
- **Training data**: Minimum 2 years of hourly load + meteorological data

### Anomaly Detection Model
- **Architecture**: Autoencoder with LSTM encoder
- **Input**: Time-series of voltage, frequency, current, power factor
- **Output**: Anomaly score (0–1); threshold > 0.7 triggers alert
- **Latency**: < 200 ms end-to-end from sensor reading to alert

### Dispatch Optimization
- **Objective**: Minimize total operating cost subject to:
  - Power balance constraint: ΣP_gen = P_load + P_losses
  - Generator limits: P_min ≤ P_gen ≤ P_max
  - Ramp rate constraints: |ΔP/Δt| ≤ ramp_rate_limit
- **Algorithm**: Linear Programming (primary) + Genetic Algorithm (fallback for nonlinear)
- **Solve time target**: < 500 ms for systems up to 100 nodes

---

## 🔬 Simulation Requirements

### Performance
- Real-time simulation step: ≤ 100 ms per simulation tick
- Support for up to 500 distribution nodes in a single simulation instance
- GPU acceleration optional via PyTorch for ML inference; CPU-only mode required
- Deterministic replay from saved simulation state snapshots

### Scalability
- Modular architecture supporting addition of subsystems (hydrogen blending,
  battery storage, renewable intermittent sources) without core refactoring
- Horizontal scaling via message queue (e.g., Redis pub/sub) for multi-instance simulation

### Interoperability
- REST API for external SCADA / EMS integration
- CIM (Common Information Model, IEC 61968/61970) compatible data models
- OpenADR 2.0 demand response interface
- Modbus TCP / DNP3 protocol adapters for field device integration

---

## 🔒 Security & Compliance

### Cybersecurity
- All sensor data transmitted over encrypted channels (TLS 1.3 minimum)
- Role-based access control (RBAC) for control command authority
- Immutable audit log for all setpoint changes and control actions
- AI model inference sandboxed from control-plane execution

### Regulatory Standards
- IEC 61511: Functional safety for industrial process sectors
- IEEE 1547: Standard for interconnection of distributed resources
- NERC CIP: Critical Infrastructure Protection standards for grid-connected systems
- ISO 50001: Energy Management System alignment for efficiency reporting

---

## 🛡️ Safety & Constraints

### Operational Safety Guards
- **Hard limits**: Electrical output never commanded beyond rated nameplate ± 5%
- **Frequency guardrails**: System trips if frequency deviates > ±0.5 Hz from nominal
- **Voltage bounds**: Automatic tap changer commands blocked if bus voltage < 0.9 pu or > 1.1 pu
- **Fuel cutoff**: Gas supply shutdown triggered if conversion efficiency < 20% (fault condition)

### Agent Safety (Pre-Genesis)
- Operates in advisory mode only (E_ONLY autonomy model)
- Does not issue live control commands without human operator approval
- All proposed setpoints reviewed by control room before dispatch
- Simulation outputs clearly labeled to prevent confusion with live system data

---

## 🖥️ MCP Integration

### Primary MCP Capabilities

1. **File System Operations**
   - `view`: Read simulation configuration files and results
   - `grep`/`glob`: Search energy model definitions
   - `edit`: Update simulation parameters and thresholds

2. **Code Analysis**
   - `search_code`: Find existing thermodynamic calculation utilities
   - `bash`: Execute simulation runs and validation scripts

3. **GitHub Operations**
   - `get_file_contents`: Retrieve physics model definitions
   - `search_code`: Cross-reference formula implementations

### Workflow Integration

```yaml
# Example activation in GitHub Actions
- name: Run Energy Conversion Simulation
  uses: ./.github/actions/agent-runner
  with:
    agent: energy-conversion-agent
    parameters: |
      fuel_type: natural_gas
      load_profile: data/load_profile_2026.csv
      simulation_duration_hours: 24
      optimization_mode: cost_minimization
```

---

## ✅ Activation Examples

```markdown
@copilot Use the Energy Conversion Agent to simulate a 24-hour natural gas generator dispatch plan optimized for minimum fuel cost.

@copilot Use the Energy Conversion Agent to calculate CO₂ emissions and conversion efficiency for a 500 kW gas generator at 75% load.

@copilot Use the Energy Conversion Agent to detect anomalies in voltage/frequency time-series data and recommend corrective actions.
```

---

## 📊 Success Metrics

| Metric | Target |
|--------|--------|
| Conversion efficiency accuracy | ≤ 2% error |
| Demand forecast MAPE | ≤ 3% |
| Anomaly detection latency | < 200 ms |
| Dispatch optimization time | < 500 ms |
| Grid stability compliance | 100% |
| Regulatory report automation | 95%+ |

---

---

## 🍓 Embedded Hardware Integration (RPi/SBC Prototyping)

### Supported Hardware Platforms

The agent natively targets SBCs for field-deployable
EC prototypes. The following platforms are supported and have
been validated against correlated research:

| Platform | CPU / AI | RAM | Best For |
|----------|----------|-----|----------|
| **RPi 4B** | ARM Cortex-A72 | 2–8 GB | Primary prototyping target; full Linux, Python 3, GPIO |
| **RPi 5** | ARM Cortex-A76 | 4–8 GB | Higher-throughput edge AI inference; PCIe slot for AI HAT |
| **RPi Zero 2W** | ARM Cortex-A53 | 512 MB | Ultra-compact installation in retrofit products |
| **NVIDIA Jetson Orin Nano** | 6-core ARM + 1024-core GPU | 8 GB | On-device neural network inference for LSTM/autoencoder |
| **BeagleBone AI-64** | TDA4VM dual Cortex-A72 | 4 GB | Real-time PRU co-processors for Modbus / DNP3 sampling |
| **ESP32 (co-processor)** | Xtensa LX6 dual-core | 520 KB SRAM | Sensor node, PWM actuator, watchdog; MicroPython firmware |

> **Recommended starter kit**: RPi 4 (4 GB) + MCP3008 ADC HAT + PZEM-004T meter + MQ-6/MQ-135 sensors.
> *Citation: Gund & Malwatkar (2025); Mishra et al. (2024)*

---

### Hardware Sensor Wiring Patterns

#### Gas Sensor Array (MQ-Series via MCP3008 ADC)

The RPi has no native analog inputs. An SPI-connected 10-bit ADC
(MCP3008) bridges analog gas sensor outputs to the RPi GPIO header.

```
MQ-6 (LPG)  ──┬──(AOUT)──► MCP3008 CH0 ──(SPI)──► RPi GPIO
MQ-135 (Air)──┤──(AOUT)──► MCP3008 CH1
MQ-2 (CO)  ───┘──(AOUT)──► MCP3008 CH2

MCP3008 VDD/VREF ── 3.3 V
MCP3008 CLK/MOSI/MISO/CS ── RPi SPI0 (GPIO 11/10/9/8)
```

#### Electrical Output Metering (PZEM-004T)

```
Generator AC output ──► PZEM-004T ──(UART 9600 baud)──► RPi GPIO 14/15
                                        (RS485 variant: USB-RS485 dongle)
Reads: V (V), I (A), P (W), Energy (kWh), freq (Hz), PF
```

#### Actuator Control (Relay / PWM)

```
RPi GPIO 17 ──► 5 V Relay Module ──► Gas solenoid valve (fuel cutoff)
RPi GPIO 18 (PWM) ──► Gate driver ──► Generator throttle servo
RPi GPIO 27 ──► Status LED array (normal / warning / fault)
```

---

### Codebase Logic Patterns (APA-Correlated)

The following Python class patterns are derived directly from the correlated
peer-reviewed sources listed in the APA citation table below.

#### Pattern 1 — Sensor Abstraction (Observer + Strategy)
*Correlates with: Mishra et al. (2024); Johal (2024) GPIO guide*

```python
# src/codex/energy/hardware/gas_sensor.py
import spidev
import time
from dataclasses import dataclass
from typing import Optional

@dataclass
class GasReading:
    channel: int
    raw_value: int        # 0–1023 (10-bit ADC)
    voltage: float        # 0–3.3 V
    concentration_ppm: Optional[float] = None

class MQ6SensorSPI:
    """LPG/propane gas sensor via MCP3008 ADC over SPI."""
    VCC = 5.0             # sensor supply voltage
    RL_KOHM = 10.0        # load resistance
    RO_CLEAN_AIR_FACTOR = 9.83
    MQ6_LPG_A = 10_000.0  # LPG calibration coeff a (datasheet curve)
    MQ6_LPG_B = -2.44     # LPG calibration coeff b (power exponent)

    def __init__(self, spi_bus: int = 0, spi_device: int = 0, channel: int = 0):
        self._spi = spidev.SpiDev()
        self._spi.open(spi_bus, spi_device)
        self._spi.max_speed_hz = 1_350_000
        self.channel = channel
        self._ema_voltage: float = 0.0  # exponential moving average (EMA)

    def _read_adc(self) -> int:
        adc = self._spi.xfer2([1, (8 + self.channel) << 4, 0])
        return ((adc[1] & 3) << 8) + adc[2]

    def read(self) -> GasReading:
        raw = self._read_adc()
        voltage = (raw / 1023.0) * 3.3
        # EMA filter α=0.2 for noise suppression
        self._ema_voltage = 0.2 * voltage + 0.8 * self._ema_voltage
        return GasReading(
            channel=self.channel,
            raw_value=raw,
            voltage=self._ema_voltage,
            concentration_ppm=self._voltage_to_ppm(self._ema_voltage),
        )

    def _voltage_to_ppm(self, v: float) -> float:
        """RS = (VCC-v)/v * RL; PPM = A*(RS/RO)^B (MQ-6 LPG datasheet)."""
        if v < 0.001:
            return 0.0
        rs_kohm = (self.VCC - v) / v * self.RL_KOHM
        rs_ro = rs_kohm / self.RO_CLEAN_AIR_FACTOR
        return self.MQ6_LPG_A * (rs_ro ** self.MQ6_LPG_B)
```

#### Pattern 2 — PZEM-004T Energy Metering
*Correlates with: Mishra et al. (2024); IJSR 13(6)*

```python
# src/codex/energy/hardware/pzem_meter.py
import serial
import struct
from dataclasses import dataclass

@dataclass
class PowerReading:
    voltage_v: float
    current_a: float
    power_w: float
    energy_kwh: float
    frequency_hz: float
    power_factor: float

class PZEM004TMeter:
    """UART AC energy meter (Modbus RTU)."""
    BAUD = 9600
    SLAVE_ADDR = 0xF8

    def __init__(self, port: str = "/dev/ttyUSB0"):
        self._ser = serial.Serial(port, self.BAUD, timeout=1.0)

    def read(self) -> PowerReading:
        cmd = bytes([self.SLAVE_ADDR, 0x04, 0x00, 0x00, 0x00, 0x0A, 0xF0, 0xF8])
        self._ser.write(cmd)
        raw = self._ser.read(25)
        if len(raw) < 25:
            raise IOError("PZEM-004T: incomplete response")
        v  = struct.unpack(">H", raw[3:5])[0] / 10.0    # 0.1 V LSB
        i  = struct.unpack(">I", raw[5:9])[0] / 1000.0  # mA LSB
        p  = struct.unpack(">I", raw[9:13])[0] / 10.0   # 0.1 W LSB
        e  = struct.unpack(">I", raw[13:17])[0]          # Wh
        hz = struct.unpack(">H", raw[17:19])[0] / 10.0
        pf = struct.unpack(">H", raw[19:21])[0] / 100.0
        return PowerReading(v, i, p, e / 1000.0, hz, pf)
```

#### Pattern 3 — PID Controller (Ziegler-Nichols tuned)
*Correlates with: IEEE Xplore 10315870 (2023); Gund & Malwatkar (2025)*

```python
# src/codex/energy/control/pid_controller.py
import time

class PIDController:
    """Discrete-time PID with anti-windup clamp.
    Tuned via Ziegler-Nichols: Kp=0.6*Ku, Ti=0.5*Tu, Td=0.125*Tu
    """
    def __init__(self, kp: float, ki: float, kd: float,
                 output_min: float = -100.0, output_max: float = 100.0):
        self.kp, self.ki, self.kd = kp, ki, kd
        self.output_min, self.output_max = output_min, output_max
        self._integral = 0.0
        self._prev_error = 0.0
        self._prev_time = time.monotonic()

    def compute(self, setpoint: float, measured: float) -> float:
        now = time.monotonic()
        dt = max(now - self._prev_time, 1e-6)
        error = setpoint - measured
        self._integral += error * dt
        derivative = (error - self._prev_error) / dt
        output = self.kp*error + self.ki*self._integral + self.kd*derivative
        output_clamped = max(self.output_min, min(self.output_max, output))
        if output != output_clamped:
            self._integral -= error * dt  # anti-windup back-calculation
        self._prev_error = error
        self._prev_time = now
        return output_clamped
```

#### Pattern 4 — MQTT Telemetry Publisher
*Correlates with: Wevolver (2024) Edge AI SBC architecture; GitHub SBC topics*

```python
# src/codex/energy/telemetry/mqtt_publisher.py
import json, ssl
import paho.mqtt.client as mqtt
from datetime import datetime, timezone

class EnergyTelemetryPublisher:
    """Publish energy readings to MQTT broker with TLS 1.3."""
    TOPIC_TMPL = "energy/{device_id}/telemetry"

    def __init__(self, broker: str, port: int = 8883, device_id: str = "proto-01",
                 ca_certs: str = "/etc/ssl/certs/ca-certificates.crt"):
        self.device_id = device_id
        self.topic = self.TOPIC_TMPL.format(device_id=device_id)
        self._client = mqtt.Client(client_id=device_id, protocol=mqtt.MQTTv5)
        self._client.tls_set(ca_certs=ca_certs, tls_version=ssl.PROTOCOL_TLS_CLIENT)
        self._client.connect(broker, port, keepalive=60)
        self._client.loop_start()

    def publish(self, power: "PowerReading", gas_ppm: float, efficiency_pct: float) -> None:
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),  # JSON field, not filename
            "device": self.device_id,
            "voltage_v": power.voltage_v, "current_a": power.current_a,
            "power_w": power.power_w, "energy_kwh": power.energy_kwh,
            "frequency_hz": power.frequency_hz, "power_factor": power.power_factor,
            "gas_concentration_ppm": gas_ppm,
            "conversion_efficiency_pct": efficiency_pct,
        }
        self._client.publish(self.topic, json.dumps(payload), qos=1)
```

#### Pattern 5 — Main Acquisition Loop (Observer / Event-Driven)
*Correlates with: Mishra et al. (2024); Gaber et al. (2023)*

```python
# src/codex/energy/hardware/acquisition_loop.py
import time, logging
from codex.energy.hardware.gas_sensor import MQ6SensorSPI
from codex.energy.hardware.pzem_meter import PZEM004TMeter
from codex.energy.control.pid_controller import PIDController
from codex.energy.telemetry.mqtt_publisher import EnergyTelemetryPublisher
from codex.energy.conversion_calculator import ConversionCalculator

logger = logging.getLogger(__name__)
GAS_FAULT_PPM = 5_000   # early-warning: ~20% of LPG LEL (0.5% vol; LEL ≈ 21,000 ppm)
POWER_SETPOINT_W = 500  # target generator output

def run_acquisition_loop(broker: str, device_id: str = "prototype-01"):
    gas  = MQ6SensorSPI(channel=0)
    meter = PZEM004TMeter("/dev/ttyUSB0")
    pid  = PIDController(kp=0.6, ki=0.3, kd=0.075)
    pub  = EnergyTelemetryPublisher(broker, device_id=device_id)
    calc = ConversionCalculator()

    while True:
        gas_rdg = gas.read()
        pwr_rdg = meter.read()
        if gas_rdg.concentration_ppm and gas_rdg.concentration_ppm > GAS_FAULT_PPM:
            logger.critical("GAS FAULT %.0f ppm — fuel cutoff", gas_rdg.concentration_ppm)
            break  # trigger GPIO fuel cutoff here
        throttle = pid.compute(POWER_SETPOINT_W, pwr_rdg.power_w)
        η = calc.actual_efficiency(
            p_electrical_kw=pwr_rdg.power_w / 1000.0,
            m_dot_fuel_kg_s=0.05,
            lhv_fuel_kj_kg=47_100.0,
        )
        pub.publish(pwr_rdg, gas_rdg.concentration_ppm or 0.0, η * 100)
        logger.info("P=%.1fW η=%.1f%% throttle=%.1f", pwr_rdg.power_w, η*100, throttle)
        time.sleep(1.0)
```

---

## 📚 APA Citation Library

The following peer-reviewed and authoritative sources directly correlate with
the codebase patterns, calculation specifications, and hardware integration
requirements in this agent:

### Embedded Systems & RPi Research

Gaber, M., Khamis, A., & Zydek, D. (2023). Evaluating the performance of
intelligent EMS for hybrid electric vehicles based on
embedded RPi module. In *Advances in Systems Engineering* (pp. 284–292).
Springer. https://doi.org/10.1007/978-3-031-40579-2_28
*(Validates: Pattern 5 acquisition loop; fuel cell EMS on embedded hardware.)*

Gund, A. M., & Malwatkar, G. M. (2025). Energy-efficient industrial automation
using low-power embedded platforms and adaptive control algorithms.
*International Journal of Innovation in Engineering & Science*, 10102.
https://ijies.net/final-docs/final-pdf/10102.pdf
*(Validates: Pattern 3 PID controller; Fuzzy Logic + PID on RPi4 + ESP32.)*

Mishra, A., Srivastav, J., & Srivastav, M. (2024). Real-time IoT-based energy
and power monitoring and management system for small-scale applications using a
RPi web UI. *International Journal of Science and Research*,
13(6), 284–294. https://dx.doi.org/10.21275/SR24603083200
*(Validates: Pattern 2 PZEM-004T metering; Pattern 5 main acquisition loop.)*

Utilisation of RPi 4 & RP2040 microcontroller for PID acquisition
and control system design. (2023). *IEEE Xplore*, Article 10315870.
https://ieeexplore.ieee.org/document/10315870
*(Validates: Pattern 3 Ziegler-Nichols PID tuning; RPi real-time control.)*

### Energy Simulation & AI Optimization

Artificial Intelligence and Machine Learning in Energy Conversion and Storage.
(2023). *Energies (MDPI)*, 16(23), 7773. https://doi.org/10.3390/en16237773
*(Validates: LSTM / autoencoder AI model requirements; thermodynamic efficiency.)*

An FPGA-accelerated multi-level AI-integrated simulation framework for
integrated energy systems. (2025). *Energy and AI (ScienceDirect)*.
https://doi.org/10.1016/j.egyai.2025.001065
*(Validates: High-performance compute requirements; simulation architecture.)*

Applications of artificial intelligence in power system operation and control.
(2025). *Clean Energy*, 7(6), 1199–1215. https://doi.org/10.1093/ce/zkad080
*(Validates: Grid stability checker; dispatch optimizer; DER management.)*

Dynamic Modeling and Simulation of Integrated Electricity and Gas Systems.
(2022). *IEEE Transactions on Power Systems*. IEEE Xplore 9874912.
https://ieeexplore.ieee.org/document/9874912
*(Validates: Thermodynamic conversion engine; gas-electric system model.)*

### IoT & Edge AI Architecture

Johal, P. (2024). RPi IoT projects: Python GPIO control for sensor
data acquisition. *johal.in*.
https://johal.in/raspberry-pi-iot-projects-python-gpio-control-for-sensor-data-acquisition/
*(Validates: Pattern 1 sensor abstraction; GPIO + SPI wiring patterns.)*

Wevolver. (2024). Exploring the frontier of edge AI: Top 5 single board
computers (SBCs). *wevolver.com*.
https://www.wevolver.com/article/exploring-the-frontier-of-edge-ai-top-5-single-board-computers-sbcs
*(Validates: Pattern 4 MQTT telemetry; SBC hardware selection guidance.)*

---

## 🔗 Integration Points

- `src/codex/energy/` — core simulation modules
- `src/codex/energy/hardware/` — SBC sensor/actuator drivers
- `src/codex/energy/control/` — PID / MPC controllers
- `src/codex/energy/telemetry/` — MQTT publisher + data pipeline
- `.codex/docs/ENERGY_CONVERSION_AUTONOMOUS_PATTERNS.md` — Claudeclaw autonomous patterns
- `.codex/docs/ENERGY_CONVERSION_SPEC.md` — extended technical specification
- `tests/energy/` — physics model validation suite
- `scripts/cognitive/topology_manager.py` — cognitive brain navigation
- `scripts/cognitive/cache_manager.py` — simulation result cache

---

## Version History

### v1.2.0 (2026-03-21)
- ✅ Claudeclaw-style autonomous management patterns — see `.codex/docs/ENERGY_CONVERSION_AUTONOMOUS_PATTERNS.md`

### v1.1.0 (2026-03-21)
- ✅ Embedded hardware integration: RPi 4/5, Jetson, BeagleBone AI, ESP32
- ✅ Sensor wiring: MQ-6/MQ-135/MQ-2 + MCP3008 ADC, PZEM-004T
- ✅ 5 APA-correlated Python codebase logic patterns
  - Pattern 1: Sensor abstraction with EMA filter (MQ-6 via SPI)
  - Pattern 2: PZEM-004T Modbus RTU energy metering
  - Pattern 3: Ziegler-Nichols PID with anti-windup
  - Pattern 4: MQTT telemetry publisher (TLS 1.3)
  - Pattern 5: Main acquisition loop (observer/event-driven)
- ✅ APA citation library: 10 peer-reviewed + authoritative sources
- ✅ Module structure: `hardware/`, `control/`, `telemetry/`

### v1.0.0 (2026-03-21)
- ✅ Initial agent specification based on deep research of peer-reviewed requirements
- ✅ Thermodynamic + electrical calculation engine specification
- ✅ AI model architecture (LSTM demand forecast, autoencoder anomaly detection)
- ✅ Power distribution optimizer design (LP + genetic algorithm)
- ✅ Security, compliance, and safety guard definitions
- ✅ Cognitive Brain Level 2 integration
- ✅ AAIS contribution: +2.0 points
