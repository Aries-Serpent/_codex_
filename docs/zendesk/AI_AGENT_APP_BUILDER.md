# Zendesk AI Agent App Builder: Mathematical Model & Design Guide

This document provides a formal, physics-inspired mathematical model for understanding the capabilities, limitations, and optimal design patterns for **Zendesk AI Agent App Builder** (distinct from the traditional Zendesk App Framework/ZAF).

> **Note**: For a visual-first overview with comprehensive ASCII diagrams and AI transparency notes, see [CANONICAL_CAPABILITY_MAP.md](CANONICAL_CAPABILITY_MAP.md).

## Table of Contents

1. [Overview](#overview)
2. [Visual Capability Maps](#visual-capability-maps)
3. [Mathematical Foundation](#mathematical-foundation)
4. [Location Manifold & Capacity Fields](#location-manifold--capacity-fields)
5. [Capability Spectrum](#capability-spectrum)
6. [Security Boundary Constraints](#security-boundary-constraints)
7. [Data Flow & Latency Model](#data-flow--latency-model)
8. [Feature Feasibility Classification](#feature-feasibility-classification)
9. [Location-Capability Coupling](#location-capability-coupling)
10. [Optimization Framework](#optimization-framework)
11. [Practical Decision Rules](#practical-decision-rules)
12. [Worked Examples](#worked-examples)
13. [Implementation Guidance](#implementation-guidance)
14. [Extended Visual Reference](#extended-visual-reference)
15. [AI Assistant Context & Limitations](#ai-assistant-context--limitations)

## Overview

Zendesk AI Agent App Builder operates within a constrained environment with specific capabilities and limitations. This document models these as a **constrained field theory** where:

- **Locations** (Sidebar, Topbar, Navbar) have different capacity profiles
- **Capabilities** exist on a spectrum of feasibility
- **Security boundaries** act as hard constraints
- **Latency** and **rate limits** impose natural bottlenecks
- **Feature decisions** can be optimized using a physics-inspired action functional

### Key Distinction: App Builder vs ZAF

| Aspect | AI Agent App Builder | ZAF (Zendesk App Framework) |
|--------|---------------------|----------------------------|
| **Primary Use** | AI-driven agent workflows | Custom UI extensions |
| **Deployment** | Native Zendesk locations | iFrame-based apps |
| **Capabilities** | Constrained by mathematical model | More flexible, developer-controlled |
| **Security Model** | Proxy-based, sandboxed | OAuth, controlled API access |

## Visual Capability Maps

This section provides ASCII-based visual representations of the Zendesk App Builder ecosystem, complementing the mathematical model with intuitive diagrams.

### Location Spectrum

```text
┌─────────────────────────────────────────────────────────────────────┐
│ ZENDESK APP BUILDER ECOSYSTEM (Navbar Context)                     │
└─────────────────────────────────────────────────────────────────────┘

Ticket Sidebar            Topbar                   Navbar (App Area)
▓▓▓                       ▓▓▓▓▓                    ▓▓▓▓▓▓▓▓▓▓
[|||]                     [=====]                  [═══════════════]
│                         │                        │
├─ Context: ████          ├─ Context: ██           ├─ Context: █
├─ Space:   █             ├─ Space:   ██           ├─ Space:   ██████████
├─ Persist: ████          ├─ Persist: █            ├─ Persist: █████
└─ Complex: █             └─ Complex: ██           └─ Complex: ████████
```text
**Interpretation**:
- **Sidebar**: High contextual awareness (sees current ticket), minimal space
- **Topbar**: Balanced but limited in all dimensions
- **Navbar**: Maximum space and complexity support, minimal ticket context

### Capability Matrix

```text
DIMENSION                CAPABILITY [▓]  LIMITATION [▒]  BLOCKED [░]
────────────────────────────────────────────────────────────────────────
UI Complexity            [▓▓▓▓▓▓▓▓░░]  Multi-step ✓       Native modal ✗
Data Rendering           [▓▓▓▓▓▓▓▓▓░]  Tables/Charts ✓     Real-time push ✗
External APIs            [▓▓▓▓▓▒▒▒░░]  REST via proxy ✓     Direct calls ✗
Authentication           [▓▓▓▓▓▒▒░░░]  OAuth/API key ✓     Custom SSO ✗
State Management         [▓▓▓▓▓▓▒░░░]  React state ✓       Redux/Context ≈
Backend Logic            [░░░░░░░░░░]  Client-side ✓       Custom server ✗
Real-time Data           [▓▓▒▒░░░░░░]  Polling ✓           WebSockets ✗
Data Persistence         [▓▓▓▒▒▒░░░░]  Zendesk objects ✓   Custom DB ✗
Bulk Operations          [▓▓▓▒▒▒▒░░░]  Small batches ✓     1000s records ✗
Custom Navigation        [▓▓▓▓▓▓▒░░░]  In-app routing ✓    Chrome override ✗
```text
**Legend**:
- **▓** = Full or strong support
- **▒** = Partial support with limitations
- **░** = Minimal or no support

### Architectural Boundaries

```text
┌───────────────────────────────────┐
│ BROWSER RUNTIME (Client-Side)     │
├───────────────────────────────────┤
│ ┌────────────────────────────────┐ │
│ │ APPLICATION (JavaScript/React) │ │
│ │ • Render UI ✓                  │ │
│ │ • Handle events ✓              │ │
│ │ • Call APIs via proxy ✓        │ │
│ │ • Store state (ephemeral) ✓    │ │
│ └────────────────────────────────┘ │
│                                     │
│ ╔═══════════════╩═══════════════╗   │
│ ║       ZENDESK SECURITY PROXY  ║   │
│ ║ • API key hiding ✓            ║   │
│ ║ • Rate limiting ✓             ║   │
│ ║ • CORS bypass ✓               ║   │
│ ╚═══════════════╤═══════════════╝   │
│                 ║                   │
└─────────────────╫──[External APIs]  │
                  ║
                  ╫──[Zendesk Core APIs]
                  ║
            ╔═════╩═════╗
            ║ FORBIDDEN ║
            ║   ZONE    ║
            ║ • Custom server ✗
            ║ • Direct DB ✗
            ║ • File system ✗
            ║ • Native code ✗
            ╚═════════════╝
```text
### Data Flow Topology

```json
Agent Action → App UI → Client Logic → API Proxy → External Service
      ↓           ↓            ↓             ↓             ↓
    [FAST]      [FAST]       [MEDIUM]      [SLOW]        [SLOW]
     <1ms        <10ms        <100ms       200-500ms     500-2000ms
       ▓           ▓            ▒            ▒              ░

BOTTLENECK POINTS:
⚠ API Proxy (rate limits, latency)
⚠ External Service (downtime, throttling)
⚠ Client Processing (heavy computation freezes UI)
```text
### Security Boundary Map

```text
┌─────────────────┐
│   PUBLIC WEB    │ (Untrusted)
└────────┬────────┘
         │
╔════════▼════════╗   ← CSP, CORS, Auth
║   ZENDESK WALL  ║
╚════════╤════════╝
         │
┌────────▼────────┐
│     APPLICATION │ (Sandboxed)
└────────┬────────┘
         │
┌────────┼──────────────┬──────────────┐
│   ┌────▼────┐   ┌─────▼────┐   ┌────▼────┐
│   │ Zendesk │   │  Agent   │   │ External│
│   │   API   │   │   Data   │   │  APIs   │
│   │  [✓]    │   │   [✓]    │   │  [≈]    │
│   └─────────┘   └──────────┘   └─────────┘
│
│ ALLOWED:    ✓ Read agent-permitted data
│             ✓ Write via Zendesk APIs
│             ✓ Call external APIs (proxied)
│
│ FORBIDDEN:  ✗ Access other agents' private data
│             ✗ Bypass Zendesk permissions
│             ✗ Store credentials client-side
│             ✗ Direct external API calls
```text
### Performance Profile

```text
Operation Type         Speed   Reliability   Scalability
────────────────────────────────────────────────────────
UI Rendering           ▓▓▓▓▓   ▓▓▓▓▓         ▓▓▓▓▓
Local State Updates    ▓▓▓▓▓   ▓▓▓▓▓         ▓▓▓░
Zendesk API (single)   ▓▓▓░░   ▓▓▓▓░         ▓▓▓░░
Zendesk API (bulk)     ▓▓░░░   ▓▓▓░░         ▓░░░░
External API (proxied) ▓▓░░░   ▓▓░░░         ▓▓░░░
Heavy Computation      ▓░░░░   ▓▓▓▓▓         ░░░░░
Real-time Updates      ▓░░░░   ▓▓░░░         ▓░░░░

LEGEND: ▓ = Good, ░ = Poor   (Speed in ms: ▓ < 100, ░ > 1000)
```text
### Navbar Space Allocation

```text
┌─────────────────────────────────────────────────────────────┐
│ [Z] Zendesk Global Header         [Agent]  [Settings]  ▼    │ ← FIXED
├─────────────────────────────────────────────────────────────┤
│ [☰]                                                         │
│ Nav                                                         │
│ bar  ┌───────────────────────────────────────────────────┐  │
│      │                                                   │  │
│      │         APP CONTENT AREA                          │  │
│      │         (Full width ~1200-1800px)                 │  │
│      │         (Full height = viewport - chrome)         │  │
│      │                                                   │  │
│      │   ✓ Multi-column layouts                          │  │
│      │   ✓ Data tables                                   │  │
│      │   ✓ Dashboards                                    │  │
│      │   ✓ Forms & wizards                               │  │
│      └───────────────────────────────────────────────────┘  │
└──────┴──────────────────────────────────────────────────────┘

↑ FIXED CONSTRAINTS:
✗ Cannot hide Zendesk header/sidebar
✗ Cannot go full-screen
✓ Can use tabs/routing within the app area
✓ Can open modals/overlays
```text
### Navbar Capability Signature

```text
CAPABILITY FINGERPRINT:
Space:       ██████████  10/10
Complexity:  ████████░░   8/10
Context:     █░░░░░░░░░   1/10
Performance: ██████░░░░   6/10
Integration: ███████░░░   7/10
Real-time:   ██░░░░░░░░   2/10

OVERALL SCORE: 34/60  (Navbar excels at complex, space-intensive apps)
```text
## Mathematical Foundation

### Notation & Conventions

- **Spaces**: Calligraphic letters (e.g., $\mathcal{L}$, $\mathcal{D}$)
- **Fields**: Bold lowercase (e.g., $\mathbf{s}$, $\mathbf{f}$)
- **Scalars**: Greek letters (e.g., $\phi$, $\alpha$, $\lambda$)
- **Sets**: Uppercase Roman (e.g., $V$, $E$, $\Omega$)
- **Normalization**: All capacity/capability values ∈ [0,1]

### Physical Interpretation

Think of this model as a **constrained field theory** where:

- **Potential wells** represent capability availability ($\phi_d$)
- **Action functionals** guide optimal feature selection ($\mathcal{S}$)
- **Conservation laws** enforce security invariants ($\nabla \cdot J = 0$)
- **Projection operators** map ideal designs onto feasible space ($\mathcal{P}$)

## Location Manifold & Capacity Fields

### 1. UI Location Manifold

The **UI location manifold** represents the three primary deployment locations:

$$
\mathcal{L} = \{\mathrm{SB}, \mathrm{TB}, \mathrm{NB}\}
$$

where:
- **SB** = Sidebar
- **TB** = Topbar  
- **NB** = Navbar

### 2. Capacity Field Definition

Each location $\ell \in \mathcal{L}$ has a 4-component **capacity field**:

$$
\mathbf{s}(\ell) = \big(C_{\text{ctx}}, C_{\text{space}}, C_{\text{persist}}, C_{\text{complex}}\big) \in [0,1]^4
$$

**Components**:
- $C_{\text{ctx}}$ — Contextual information availability
- $C_{\text{space}}$ — UI space/real estate
- $C_{\text{persist}}$ — State persistence capability
- $C_{\text{complex}}$ — Support for complex interactions

### 3. Location Capacity Values

Normalized from empirical "block" measurements (k blocks → k/10):

$$
\begin{aligned}
\mathbf{s}(\mathrm{SB}) &= (0.4, 0.1, 0.4, 0.1) \\
\mathbf{s}(\mathrm{TB}) &= (0.2, 0.2, 0.1, 0.2) \\
\mathbf{s}(\mathrm{NB}) &= (0.1, 1.0, 0.5, 0.8)
\end{aligned}
$$

**Interpretation**:
- **Sidebar**: High context, limited space
- **Topbar**: Balanced but constrained
- **Navbar**: Massive space, excellent for complex UIs

### 4. Extended Navbar Fingerprint

For the **Navbar**, we use an extended 6-component fingerprint:

$$
\mathbf{f}(\mathrm{NB}) = (C_{\text{space}}, C_{\text{complex}}, C_{\text{ctx}}, C_{\text{perf}}, C_{\text{integ}}, C_{\text{rt}})
$$

$$
\mathbf{f}(\mathrm{NB}) = (1.0, 0.8, 0.1, 0.6, 0.7, 0.2)
$$

**Additional Components**:
- $C_{\text{perf}}$ — Performance headroom (0.6)
- $C_{\text{integ}}$ — Integration capability (0.7)
- $C_{\text{rt}}$ — Real-time support (0.2)

## Capability Spectrum

### 1. Capability Dimensions

The **capability dimension space**:

$$
\mathcal{D} = \{\text{UI}, \text{Render}, \text{ExtAPI}, \text{Auth}, \text{State}, \text{Backend}, \text{Realtime}, \text{Persist}, \text{Bulk}, \text{Nav}\}
$$

### 2. Available-Capability Field

For each dimension $d \in \mathcal{D}$, define the **available-capability field**:

$$
\phi_d \in [0,1] \quad (d \in \mathcal{D})
$$

Measured as the fraction of "▓" (available) in a 10-cell visual bar:

$$
\begin{aligned}
\phi_{\text{UI}} &= 0.8 & \phi_{\text{Render}} &= 0.9 & \phi_{\text{ExtAPI}} &= 0.5 \\
\phi_{\text{Auth}} &= 0.5 & \phi_{\text{State}} &= 0.6 & \phi_{\text{Backend}} &= 0.0 \\
\phi_{\text{Realtime}} &= 0.2 & \phi_{\text{Persist}} &= 0.3 & \phi_{\text{Bulk}} &= 0.3 \\
\phi_{\text{Nav}} &= 0.6
\end{aligned}
$$

### 3. Capability Interpretation

| Capability | $\phi$ | Interpretation |
|-----------|--------|----------------|
| **UI** | 0.8 | Rich UI components available |
| **Render** | 0.9 | Excellent rendering performance |
| **ExtAPI** | 0.5 | Moderate external API access (via proxy) |
| **Auth** | 0.5 | OAuth flows supported but constrained |
| **State** | 0.6 | Good client-side state management |
| **Backend** | 0.0 | **No custom backend** (hard limit) |
| **Realtime** | 0.2 | Limited real-time capabilities |
| **Persist** | 0.3 | Limited persistent storage |
| **Bulk** | 0.3 | Limited bulk operations |
| **Nav** | 0.6 | Good navigation/routing support |

### 4. Potential Well Interpretation

Interpret $\phi_d$ as a **potential well**:
- **High $\phi_d$** → Low "action cost" to realize capability
- **Low $\phi_d$** → High friction, may not be feasible
- $\phi_d = 0$ → Forbidden/impossible

## Security Boundary Constraints

### 1. Forbidden Operations Set

Define the **forbidden operation set**:

$$
\mathcal{F} = \{\text{DirectExternalCalls}, \text{CustomServer}, \text{DirectDB}, \text{NativeCode}, \text{ClientStoredCreds}\}
$$

**Rationale**: Zendesk App Builder operates in a sandboxed environment with proxy-mediated external access.

### 2. Feasible Design Space

The **feasible design space** $\Omega$ is defined by constraints:

$$
\Omega = \{x \in \{0,1\}^n \mid g_j(x) \leq 0, \; h_k(x) = 0, \; \chi_{\mathcal{F}}(x) = 0\}
$$

where:
- $x$ — Feature toggle vector (binary: include feature or not)
- $g_j(x) \leq 0$ — Inequality constraints (rate limits, latency ceilings, resource limits)
- $h_k(x) = 0$ — Equality constraints (permission invariants)
- $\chi_{\mathcal{F}}(x) = 0$ — Indicator function: nulls any design using forbidden operations

### 3. Projection Operator

**Project** an ideal design $x$ onto the feasible space:

$$
\mathcal{P}(x) = \arg\min_{y \in \Omega} \|y - x\|_2
$$

This models "what survives" the Zendesk security wall (CSP, CORS, Auth, Proxy).

### 4. Permission Conservation Law

Define a **permission current** $J$ with conservation law:

$$
\nabla \cdot J = 0 \quad \text{(inside sandbox)}
$$

$$
J \cdot n\big|_{\text{wall}} = 0 \quad \text{(for forbidden ops)}
$$

**Interpretation**: Permissions neither appear nor vanish; flows that violate the wall have zero normal component (they don't pass).

## Data Flow & Latency Model

### 1. Directed Flow Graph

Model the system as a **directed graph**:

$$
\mathcal{G} = (V, E)
$$

where:

$$
V = \{\mathrm{Agent}, \mathrm{UI}, \mathrm{Client}, \mathrm{Proxy}, \mathrm{External}\}
$$

### 2. Latency Weights

Edges $e \in E$ carry **latency weights** $w_e$:

$$
\begin{aligned}
w_{\mathrm{Agent} \to \mathrm{UI}} &\approx 0.5 \text{ ms} \\
w_{\mathrm{UI} \to \mathrm{Client}} &\approx 5 \text{ ms} \\
w_{\mathrm{Client} \to \mathrm{Proxy}} &\approx 50 \text{ ms} \\
w_{\mathrm{Proxy} \to \mathrm{External}} &\approx 350 \text{ ms} \\
w_{\mathrm{External} \to \mathrm{Resp}} &\approx 1200 \text{ ms}
\end{aligned}
$$

### 3. Path Latency Functional

For a data flow path $\pi$, define **path latency**:

$$
\mathcal{L}(\pi) = \sum_{e \in \pi} w_e
$$

**Expected latency** for typical external API call:

$$
\mathbb{E}[\mathcal{L}] \approx 1.6 \text{ s}
$$

### 4. Rate Limit Stability

Model rate limiting as **queueing stability**:

$$
\rho = \frac{\lambda}{\mu_{\text{proxy}}} < 1
$$

where:
- $\lambda$ — Request arrival rate
- $\mu_{\text{proxy}}$ — Proxy service rate
- $\rho < 1$ — Stability condition (avoid saturation)

Use **exponential backoff** policies to maintain $\rho$ subcritical.

### 5. Visual Data Flow

```text
Agent → UI → Client → Proxy → External API
 ↓      ↓      ↓        ↓          ↓
0.5ms  5ms   50ms    350ms     1200ms

Total Expected Latency: ~1.6s
```text
## Feature Feasibility Classification

### 1. Feature Feasibility Amplitude

For a feature $i$ requiring dimensions $D_i \subseteq \mathcal{D}$, define:

$$
\Psi_i = \prod_{d \in D_i} \phi_d^{\alpha_{i,d}}
$$

where $\alpha_{i,d} \geq 0$ encodes how strongly feature $i$ depends on dimension $d$.

### 2. Feasibility Classification

Classify features by $\Psi_i$:

$$
\Psi_i \begin{cases}
> 0.7 & \text{Highly feasible (█)} \\
\in (0.4, 0.7] & \text{Feasible (▓)} \\
\in (0.2, 0.4] & \text{Difficult (▒)} \\
\leq 0.2 & \text{Not recommended (░)}
\end{cases}
$$

### 3. Visual Scorecard Mapping

| Symbol | Range | Recommendation |
|--------|-------|----------------|
| █ | >0.7 | **Highly feasible** — Build in Navbar |
| ▓ | 0.4-0.7 | **Feasible** — Good fit for Navbar |
| ▒ | 0.2-0.4 | **Difficult** — Consider alternatives |
| ░ | ≤0.2 | **Not recommended** — Use different approach |

## Location-Capability Coupling

### 1. Compatibility Tensor

Define a **compatibility tensor** coupling locations and capabilities:

$$
\Gamma_{d\ell} = \beta_d^\top \mathbf{s}(\ell)
$$

where $\beta_d \in \mathbb{R}^4_{\geq 0}$ weights which capacity components ($\text{ctx, space, persist, complex}$) a dimension $d$ consumes.

**Example $\beta$ vectors**:
- Tables/Charts: $\beta = (0, 1, 0, 0.5)$ — needs space + some complexity
- Real-time: $\beta = (0.7, 0, 0.5, 0.3)$ — needs context + persistence
- Navigation: $\beta = (0, 0.5, 0.2, 0.8)$ — needs space + complexity

### 2. Effective Capability

The **effective capability** in location $\ell$ is:

$$
\tilde{\phi}_{d,\ell} = \min\{\phi_d, \Gamma_{d\ell}\}
$$

**Interpretation**: 
- Navbar wins when $d$ needs **space/complexity**
- Sidebar wins when $d$ needs **context**
- Location mismatch reduces effective capability

### 3. Location Selection Rule

For feature $i$ with dimensions $D_i$:

$$
\ell^* = \arg\max_{\ell \in \mathcal{L}} \sum_{d \in D_i} \tilde{\phi}_{d,\ell}
$$

Choose the location that maximizes total effective capability.

## Optimization Framework

### 1. Value-Complexity Action Functional

Define a **design action** (Lagrangian-style):

$$
\mathcal{S}(x) = -\sum_i v_i \cdot x_i \cdot \underbrace{\left(\sum_{d \in D_i} \tilde{\phi}_{d,\mathrm{NB}}\right)}_{\text{capability gain}} + \lambda \sum_i c_i \cdot x_i + \mu \cdot \mathbb{E}[\mathcal{L}(x)] + \nu \cdot \rho(x)
$$

**Terms**:
- $v_i$ — Business value of feature $i$
- $c_i$ — Complexity/cost of feature $i$
- $x_i \in \{0,1\}$ — Feature inclusion indicator
- $\lambda, \mu, \nu \geq 0$ — Penalty multipliers
- $\mathbb{E}[\mathcal{L}(x)]$ — Expected latency given feature set
- $\rho(x)$ — Load/saturation factor

### 2. Optimal Feature Selection

The **optimal Navbar plan** solves:

$$
x^* = \arg\min_{x \in \Omega} \mathcal{S}(x)
$$

This yields the "sweet spot" region: **high value, moderate complexity**.

### 3. Sweet Spot Region

```text
Value (v)
    ↑
    │          ┌─────────────┐
    │          │ SWEET SPOT  │  High value
    │          │  (BUILD)    │  Moderate complexity
    │          └─────────────┘  High capability
    │     ┌──────────────────────┐
    │     │   CONSIDER OTHER     │
    │     │    LOCATIONS         │
    │     └──────────────────────┘
    │  ┌──────────────────────────────┐
    │  │   DON'T BUILD IN NAVBAR      │
    │  └──────────────────────────────┘
    └─────────────────────────────────→ Complexity (c)
```text
## Practical Decision Rules

### 1. Closed-Form Heuristic

For candidate feature $i$ in **Navbar**:

$$
\text{Build}_i = \mathbf{1}\left[
\underbrace{\sum_{d \in D_i} \tilde{\phi}_{d,\mathrm{NB}}}_{\text{capability mass}} \cdot \underbrace{v_i}_{\text{value}} - \underbrace{(\lambda c_i + \mu \mathbb{E}[\mathcal{L}_i] + \nu \rho_i)}_{\text{cost/drag}} > \tau
\right]
$$

where $\tau$ is a calibrated threshold.

### 2. Quick Decision Matrix

| Condition | Decision | Notes |
|-----------|----------|-------|
| $\Psi_i > 0.7$ AND $v_i/c_i > 2$ | **BUILD** | High feasibility, high value |
| $\Psi_i \in [0.4, 0.7]$ AND $v_i/c_i > 1.5$ | **CONSIDER** | Feasible if value justifies |
| $\Psi_i < 0.4$ OR $v_i/c_i < 1$ | **DON'T BUILD** | Low feasibility or poor value |
| $\phi_{\text{Backend}} > 0$ needed | **IMPOSSIBLE** | No custom backend |
| $\mathbb{E}[\mathcal{L}] > 3$s | **RECONSIDER** | Too slow for UX |

### 3. Location Decision Tree

```text
Feature Needs Space + Complexity?
    │
    ├─ YES → Navbar ✓
    │
    └─ NO → Feature Needs Context?
            │
            ├─ YES → Sidebar ✓
            │
            └─ NO → Feature Needs Real-time?
                    │
                    ├─ YES → Sidebar (limited) or External
                    │
                    └─ NO → Topbar or Navbar
```text
## Worked Examples

### Example A: Multi-Step Configuration Wizard

**Requirements**:
- Dimensions: $D_A = \{\text{UI}, \text{Render}, \text{State}, \text{Nav}\}$
- Complexity: $c_A = 7$ (moderate-high)
- Value: $v_A = 8$ (high business value)

**Raw Feasibility**:
$$
\Psi_A = \phi_{\text{UI}} \cdot \phi_{\text{Render}} \cdot \phi_{\text{State}} \cdot \phi_{\text{Nav}}
$$
$$
\Psi_A = 0.8 \times 0.9 \times 0.6 \times 0.6 \approx 0.26 \quad \text{(▒ Difficult)}
$$

**Location Coupling**:
- Needs: space (1.0), complexity (0.8), some persistence (0.5)
- Navbar $\mathbf{s}(\mathrm{NB}) = (0.1, 1.0, 0.5, 0.8)$ matches well
- $\Gamma_{\cdot,\mathrm{NB}}$ boosts effective capability

**Effective Capability**:
$$
\sum_{d \in D_A} \tilde{\phi}_{d,\mathrm{NB}} \approx 0.8 + 0.9 + 0.6 + 0.6 = 2.9
$$

**Decision**:
$$
2.9 \times 8 - (1.0 \times 7 + 0.5 \times 1.0 + 0.3 \times 0.2) = 23.2 - 7.56 \approx 15.6 > \tau
$$

**Verdict**: ✅ **YES — Build in Navbar** (sweet spot: high value, manageable complexity, location match)

---

### Example B: Real-Time Ticket Monitor

**Requirements**:
- Dimensions: $D_B = \{\text{Realtime}, \text{UI}, \text{State}\}$
- Complexity: $c_B = 6$
- Value: $v_B = 7$

**Raw Feasibility**:
$$
\Psi_B = \phi_{\text{Realtime}} \cdot \phi_{\text{UI}} \cdot \phi_{\text{State}}
$$
$$
\Psi_B = 0.2 \times 0.8 \times 0.6 = 0.096 \quad \text{(░ Not recommended)}
$$

**Location Coupling**:
- Needs: context (high), real-time support
- Navbar $C_{\text{ctx}} = 0.1$, $C_{\text{rt}} = 0.2$ — both low
- Sidebar $C_{\text{ctx}} = 0.4$, better for context-heavy features

**Effective Capability**:
$$
\tilde{\phi}_{\text{Realtime}, \mathrm{NB}} \approx \min\{0.2, 0.1\} = 0.1
$$

**Decision**:
$$
(0.1 + 0.8 + 0.6) \times 7 - (1.0 \times 6 + 0.5 \times 1.2) = 10.5 - 6.6 = 3.9
$$

Borderline, but $\phi_{\text{Realtime}}$ is critically low.

**Verdict**: ❌ **NO — Don't build in Navbar** → Move to **Sidebar** or use **external polling service**

---

### Example C: Bulk Data Export Tool

**Requirements**:
- Dimensions: $D_C = \{\text{Bulk}, \text{ExtAPI}, \text{UI}\}$
- Complexity: $c_C = 5$
- Value: $v_C = 6$

**Raw Feasibility**:
$$
\Psi_C = \phi_{\text{Bulk}} \cdot \phi_{\text{ExtAPI}} \cdot \phi_{\text{UI}}
$$
$$
\Psi_C = 0.3 \times 0.5 \times 0.8 = 0.12 \quad \text{(░ Not recommended)}
$$

**Latency Concern**:
- Bulk operations trigger multiple external API calls
- $\mathbb{E}[\mathcal{L}] \approx 1.6 \text{ s per call} \times N$ calls
- For $N=50$ records → ~80s total (unacceptable UX)

**Decision**:
$$
\text{Latency penalty} = \mu \cdot 80 \gg v_C
$$

**Verdict**: ❌ **NO — Don't build in Navbar** → Use **async job queue** or **external service** with status polling

---

### Example D: Simple Form with External Validation

**Requirements**:
- Dimensions: $D_D = \{\text{UI}, \text{ExtAPI}, \text{State}\}$
- Complexity: $c_D = 3$ (low)
- Value: $v_D = 5$

**Raw Feasibility**:
$$
\Psi_D = \phi_{\text{UI}} \cdot \phi_{\text{ExtAPI}} \cdot \phi_{\text{State}}
$$
$$
\Psi_D = 0.8 \times 0.5 \times 0.6 = 0.24 \quad \text{(▒ Difficult)}
$$

**Mitigations**:
- Use debouncing for external validation calls
- Cache validation results in state
- Show loading states for UX

**Decision**:
$$
(0.8 + 0.5 + 0.6) \times 5 - (1.0 \times 3 + 0.5 \times 1.6) = 9.5 - 3.8 = 5.7
$$

**Verdict**: ✅ **YES — Build with care** (low complexity makes it viable despite moderate $\Psi$)

## Implementation Guidance

### 1. Design Checklist

Before implementing a Navbar feature:

- [ ] **Capability Check**: Compute $\Psi_i$ for your feature
- [ ] **Location Match**: Verify $\tilde{\phi}_{d,\ell}$ favors Navbar
- [ ] **Security Audit**: Ensure no operations in $\mathcal{F}$
- [ ] **Latency Budget**: Estimate $\mathbb{E}[\mathcal{L}]$ < 3s
- [ ] **Rate Limit**: Plan for $\rho < 0.8$ (leave headroom)
- [ ] **Value/Complexity**: Check $v_i/c_i > 1.5$
- [ ] **Action Score**: Compute $\mathcal{S}$ and verify < $\tau$

### 2. Capability Mapping Template

```json
{
  "feature": "My Feature Name",
  "dimensions": {
    "UI": {"required": true, "weight": 0.8},
    "Render": {"required": true, "weight": 0.9},
    "ExtAPI": {"required": false, "weight": 0.5},
    "State": {"required": true, "weight": 0.6}
  },
  "location": {
    "target": "Navbar",
    "capacities_needed": {
      "space": 0.7,
      "complexity": 0.6,
      "context": 0.1,
      "persist": 0.3
    }
  },
  "metrics": {
    "complexity": 5,
    "value": 7,
    "psi": 0.432,
    "classification": "Feasible (▓)"
  },
  "decision": "BUILD"
}
```text

### 3. Forbidden Patterns

**Never attempt in App Builder**:

```javascript
// ❌ Direct external API call (bypassing proxy)
fetch('https://external-api.com/data')

// ❌ Custom backend server
const server = express()

// ❌ Direct database access
const db = mongoose.connect('mongodb://...')

// ❌ Native code execution
eval(userInput)

// ❌ Client-stored credentials
localStorage.setItem('api_key', secretKey)
```text

**Always use**:

```javascript
// ✅ Proxy-mediated API calls
zendeskAPI.request({
  url: '/api/v2/external/proxy',
  type: 'GET'
})

// ✅ Zendesk-managed state
client.set('mykey', value)

// ✅ OAuth flows
client.invoke('oauth', {provider: 'custom'})
```text

### 4. Performance Optimization

**Reduce Latency**:
```javascript
// Batch API calls
const promises = items.map(item => 
  zendeskAPI.request({url: `/api/v2/items/${item.id}`})
)
await Promise.all(promises)

// Cache results
const cache = new Map()
function getCached(key, fetchFn) {
  if (!cache.has(key)) {
    cache.set(key, fetchFn())
  }
  return cache.get(key)
}

// Debounce external calls
const debouncedValidate = debounce(validateExternal, 500)
```text

**Manage Rate Limits**:
```javascript
// Exponential backoff
async function retryWithBackoff(fn, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn()
    } catch (err) {
      if (err.status === 429 && i < maxRetries - 1) {
        await sleep(Math.pow(2, i) * 1000)
      } else {
        throw err
      }
    }
  }
}
```text

### 5. Testing Strategy

**Test Matrix**:

| Test Type | Focus | Tools |
|-----------|-------|-------|
| **Unit** | Component logic | Jest, Mocha |
| **Integration** | API interactions | Mock proxy responses |
| **Performance** | Latency, rate limits | Load testing, profiling |
| **Security** | Constraint violations | Static analysis, CSP audits |
| **UX** | User workflows | Selenium, Playwright |

### 6. Monitoring & Metrics

**Track**:
- API call latency distribution
- Rate limit hit rate
- Error rates by type
- User interaction patterns
- Feature usage analytics

**Alert on**:
- $\mathbb{E}[\mathcal{L}] > 3$s (latency threshold)
- $\rho > 0.9$ (approaching rate limit)
- Error rate > 5%
- Security constraint violations

### 7. Migration from ZAF

If migrating from traditional ZAF apps:

| ZAF Pattern | App Builder Equivalent |
|-------------|----------------------|
| Custom backend | ❌ Not supported → Use Zendesk APIs + external webhook targets |
| Direct API calls | Proxy-mediated calls via Zendesk API |
| iFrame embedding | Native UI components |
| Custom OAuth | Zendesk-managed OAuth flows |
| Local storage | Zendesk client.set/get |

## Summary

### Key Takeaways

1. **Mathematical Model**: App Builder capabilities modeled as constrained field theory
2. **Locations**: Navbar excels at space/complexity; Sidebar at context
3. **Feasibility**: Use $\Psi_i$ to classify features (█▓▒░)
4. **Constraints**: Hard limits on backend, limited real-time, proxy-only external access
5. **Optimization**: Minimize action $\mathcal{S}$ to find sweet spot
6. **Latency**: Budget ~1.6s per external API call
7. **Security**: Permissions conserved; forbidden operations blocked at wall

### Quick Reference

```python
def should_build_in_navbar(feature):
    psi = calculate_feasibility(feature)
    value_complexity_ratio = feature.value / feature.complexity
    latency = estimate_latency(feature)
    
    if psi > 0.7 and value_complexity_ratio > 2:
        return "BUILD"
    elif psi >= 0.4 and value_complexity_ratio > 1.5 and latency < 3:
        return "CONSIDER"
    else:
        return "DON'T BUILD - Use alternative"
```text

### Next Steps

1. **Read**: [ZENDESK_NEWCOMER_GUIDE.md](ZENDESK_NEWCOMER_GUIDE.md)
2. **Review**: Existing App Builder limitations doc
3. **Calculate**: $\Psi_i$ for your features
4. **Optimize**: Use $\mathcal{S}$ to prioritize roadmap
5. **Build**: Follow implementation guidance
6. **Monitor**: Track latency and rate limits

## Extended Visual Reference

This section provides additional visual aids and reference materials for understanding Zendesk App Builder capabilities in practical terms.

### Integration Pattern Matrix

```text
Pattern                Supported   Complexity   Recommended
──────────────────────────────────────────────────────────
REST API                 ✓            ✓          ✓  YES
OAuth 2.0                ✓            ✓          ✓  YES
API Keys (proxied)       ✓            ✓          ✓  YES
Basic Auth               ✓            ░          ≈  OK
Webhooks (inbound)       ✓            ░          ✗  NO (use polling)
WebSockets               ✗            ✗          ✗  NO
GraphQL                  ✓            ░          ≈  OK
SOAP                     ✓            ░          ✗  AVOID
Server-Sent Events       ✗            ✗          ✗  NO
```text
### Development Lifecycle

```text
Phase          Duration   Complexity   Friction Points
────────────────────────────────────────────────────────────
Ideation         ░░░░░      ▒░░░░      Requirements clarity
Setup            ░░░        ▒▒░░░      OAuth config, proxies
Development      ░░░░░░░    ▒▒▒▒▒      API limitations, debugging
Testing          ░░░░░      ▒▒▒▒░      Limited test data
Private Beta     ░░░        ▒▒░░░      Agent feedback cycles
Publication      ░░░░░░     ▒▒▒▒▒      Marketplace approval
Maintenance      ░░░░...    ▒▒▒░░      Platform changes, support

TIME SCALE: ░ = Days/Weeks, ▒ = Complexity level
```text
### Feature Feasibility Scorecard (Navbar Context)

```text
Feature Type              Simple   Medium   Complex   Not Possible
──────────────────────────────────────────────────────────────────
Read-only dashboards       ████     ▓▓▓       ▒▒          ░
Single-step actions        ████     ▓▓▓       ▒           ░
Multi-step wizards         ▓▓▓      ▓▓▓▓      ▒▒▒         ░
Real-time monitoring       ▓        ▒▒▒       ▒▒▒▒        ░░░
Data export (small)        ████     ▓▓▓       ▒           ░
Data export (bulk)         ▓        ▒▒▒       ▒▒▒▒        ░░
Complex filters/search     ▓▓▓      ▓▓▓▓      ▒▒▒         ░
User permissions (custom)  ▓        ▒▒        ▒▒▒▒        ░░░
Offline functionality      ░        ░         ░░          ░░░░
AI/ML features (external)  ▓▓       ▓▓▓       ▒▒▒▒        ░
File uploads/processing    ▓▓       ▓▓▓       ▒▒▒         ░
Custom notifications       ▓        ▒▒▒       ▒▒▒▒        ░░░

LEGEND: █ Highly Feasible | ▓ Feasible | ▒ Difficult | ░ Not Recommended
```text
### Anti-Patterns to Avoid

```text
🚫 NEVER:
├─ Store API keys in client code
├─ Make direct external API calls (bypass proxy)
├─ Store sensitive data in localStorage
├─ Implement custom authentication
├─ Try to hide Zendesk UI chrome
├─ Perform heavy computation on main thread
└─ Assume real-time data without polling

⚠️ USE WITH CAUTION:
├─ Bulk operations (>100 items)
├─ Nested API calls (waterfall requests)
├─ Complex state management without clear patterns
├─ Third-party libraries (bundle size)
├─ Animations/transitions (performance)
└─ Multi-language support (maintenance burden)

✓ RECOMMENDED PRACTICES:
├─ Use Zendesk Garden components
├─ Implement error boundaries
├─ Show loading states
├─ Handle API rate limits gracefully
├─ Use async/await for API calls
├─ Keep bundle size minimal
└─ Test with representative Zendesk data
```text
### Cost-Benefit Zones

```text
               HIGH VALUE ↑
                  ┌────────────────┐
                  │  SWEET SPOT    │
                  │ • Read-only    │
                  │   dashboards   │
                  │ • Simple       │
                  │   integrations │
                  │ • Visualization│
                  └────────────────┘
                           │
     ┌─────────────────────┐      ┌──────────────────────┐
     │ POSSIBLE BUT HARD   │      │       LOW VALUE      │
     │ • Complex workflows │      │ • Trivial displays   │
     │ • Real-time features│      │ • Over-engineered    │
     │ • Heavy computation │      │ • Simple tasks       │
     └─────────────────────┘      └──────────────────────┘
                           │
LOW COMPLEXITY ───────────────────────────────────────────→ HIGH COMPLEXITY
                           │
                         LOW VALUE
```text
### Optimal Use Cases Summary

```text
OPTIMAL USE CASES:
✓✓✓ Configuration interfaces
✓✓✓ Reporting dashboards
✓✓✓ Data management tools
✓✓  Multi-step workflows
✓✓  Search & filter interfaces
✓   Analytics & insights

AVOID IN NAVBAR:
✗✗✗ Real-time ticket monitoring (prefer Sidebar)
✗✗  Quick actions (prefer Topbar)
✗✗  Context-heavy features (prefer Sidebar)
✗   Single-purpose simple tools
```text
### Recommended Workflow

```text
Developer Team → AI Assistant (ideation/planning) → Official Docs (validation)
              → Development Environment (testing) → AI Assistant (refinement)
              → Production
```text
### Final Recommendations for Navbar App Projects

```text
1) INITIATE:
   ├─ Define scope and features
   ├─ Identify integration points
   ├─ Draft technical architecture
   └─ Generate initial code structure

2) VALIDATE:
   ├─ Check Zendesk Developer docs
   ├─ Review Garden component patterns
   ├─ Test authentication flows in sandbox
   └─ Verify current rate limits and quotas

3) ITERATE:
   ├─ Start with minimum viable feature
   ├─ Test early in a real environment
   ├─ Increase complexity incrementally
   └─ Revisit architecture decisions as needed

4) WHEN BLOCKED:
   ├─ Review trade-offs and alternatives
   ├─ Consider fallback patterns (polling vs webhooks)
   ├─ Refactor for performance/bundle size
   └─ Escalate platform issues via official support
```text
## AI Assistant Context & Limitations

This documentation was created with assistance from AI language models. Understanding the context and limitations of AI-generated content is important for proper usage.

### Knowledge Basis

**Training Foundation**:
- Trained on broad technical materials (architecture patterns, API design, web security, developer resources)
- Knowledge cutoff: Phase 4 2024
- No direct access to live Zendesk documentation or proprietary systems

**Approach for This Output**:
- Applied constraints for app locations (Navbar, Sidebar, Topbar) and associated UI/UX limits
- Drew from general patterns in:
  - Web application architecture
  - Client-side JavaScript frameworks (e.g., React)
  - API integration (REST, OAuth, proxies)
  - Browser security models (CSP, CORS, sandboxing)
  - Common SaaS marketplace constraints

### Limitations & Validation

**AI Assistant Limitations**:
- Not authoritative on current Zendesk specifics
- Patterns are generalized; verify against official documentation
- Not version-specific; capabilities may have changed post-cutoff
- ASCII diagrams are illustrative, not a substitute for platform specs

**Recommended Validation Steps**:
1. Cross-reference with official Zendesk Developer Documentation
2. Build small prototypes to validate assumptions
3. Confirm current rate limits, payload sizes, and timeouts
4. Engage Zendesk Support for edge cases

### Confidence Calibration

```text
HIGH CONFIDENCE (≈90%+):
• Location constraints (Navbar vs Sidebar)
• General API patterns (REST, OAuth)
• React/JavaScript best practices
• SaaS UX principles
• Browser security fundamentals
• Common integration patterns

MEDIUM CONFIDENCE (≈70-90%):
• Specific Zendesk API endpoints
• Garden component usage patterns
• App framework conventions
• Performance characteristics
• Rate-limiting strategies
• Authentication flows

LOW CONFIDENCE (≈50-70%):
• Exact API parameter names (post-2024)
• New framework features released after cutoff
• Specific current rate limits
• Account-specific configurations
• Marketplace approval criteria details
• Latest Garden component updates

SHOULD BE VERIFIED EXTERNALLY:
• Current Zendesk documentation and deprecations
• Security best practices (evolving)
• Browser compatibility (latest versions)
• Third-party API specifications
• Pricing and billing details
```text
### AI Assistant Capability Profile

```text
PHASE                  CAPABILITY LEVEL         LIMITATION LEVEL
────────────────────────────────────────────────────────────────────────
Ideation               ▓▓▓▓▓▓▓▓▓▓               ░░
Planning               ▓▓▓▓▓▓▓▓▓░               ░░
Code Generation        ▓▓▓▓▓▓▓▓░░               ░░░
Architecture           ▓▓▓▓▓▓▓▓░░               ░░░
Debugging              ▓▓▓░░░░░░░               ░░░░░░
Testing                ░░░░░░░░░░               ▓▓▓▓▓▓▓▓▓▓
Deployment             ░░░░░░░░░░               ▓▓▓▓▓▓▓▓▓▓
Maintenance            ▓▓▓▓░░░░░░               ░░░░░░░

EXCELS AT: Design, planning, code scaffolding, constraint explanation
CANNOT: Execute code, test applications, access live systems, update model knowledge
```text
### Effective Usage Guidelines

**Effective Prompts**:
- "Build a Navbar app to display Jira issues with filters."
- "Assess feasibility of real-time Slack notifications in Sidebar."
- "Compare Sidebar vs Navbar for an analytics dashboard."
- "What are performance implications of polling vs webhooks?"

**Ineffective Prompts**:
- "Make it better."
- "Add all the features."
- "Here is an API key: …"
- "Why doesn't my code work?" [massive dump without context]

### Transparency Notes

**Phase 5 Be Inaccurate**:
- Endpoint URLs and exact rate limits (subject to change)
- Specific error codes and latest best practices
- Deprecated or newly released features (post-cutoff)

**Consistent Strengths**:
- Conceptual architecture and trade-off analysis
- Starter code templates and rationale
- Identification of common anti-patterns
- Structuring technical plans

**Effective Usage**:
1. Use during DESIGN and PLANNING
2. Validate against official docs
3. Test snippets in a sandbox
4. Treat as informed starting point
5. Request clarifications for ambiguous areas
6. Cross-check security-critical details

### Comparison: AI Assistant vs Other Tools

```text
TOOL                TYPE                 STRENGTH                          WHEN TO USE AI ASSISTANT
────────────────────────────────────────────────────────────────────────────────────────────────────────
Stack Overflow      Community Q&A        Real user experiences             Initial research synthesis
Official Docs       Authoritative specs  Precise definitions               Verify suggestions and parameters
GitHub Copilot      IDE assistant        Inline code completion            After architecture is set
ChatGPT             Conversational LLM   General ideation/help             Similar planning use cases
Zendesk Support     Vendor support       Platform-specific help            Critical platform issues
AI Assistant (LLM)  Planning/analysis    Comprehensive planning            START HERE for architecture
```text
---

**This mathematical framework enables data-driven decisions about what to build in Zendesk AI Agent App Builder and how to optimize for success within its constraints.**
