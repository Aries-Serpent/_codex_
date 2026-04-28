# Research Note 05 — Edge Cases, Failure Modes, and Worked Samples

## NotebookLM Metadata

- **Source type:** Research collection note
- **Topic:** Iterated edge cases for $C_pT$, enthalpy, and security/access counter-balance modeling

## 1. Thermodynamic Edge Cases

| Edge Case | Why $C_pT$ Can Fail | Better Model |
|---|---|---|
| Variable heat capacity | $C_p$ changes with temperature | $Δh = ∫C_p(T)dT$ |
| Phase transition | latent heat dominates | include fusion/vaporization enthalpy |
| Chemical reaction | bond energy changes matter | include formation/reaction enthalpy |
| Near critical point | properties shift sharply | use real-fluid tables/equation of state |
| Very high temperature | dissociation/ionization can occur | species and plasma models |
| High-pressure liquid | pressure contribution can matter | $Δh ≈ C_pΔT + vΔp$ |
| Non-equilibrium flow | one temperature may not describe state | transport/CFD model |

## 2. Security/Access Edge Cases

| Edge Case | Why Simple Balance Fails | Better Counter-Balance |
|---|---|---|
| Emergency incident | normal friction is too slow | break-glass with intense audit |
| Insider threat | identity confidence is misleading | behavior/resource anomaly weighting |
| Compromised device | valid user still unsafe | entangle identity with device posture |
| MFA fatigue | prompts stop adding security | risk-based prompts/passkeys/device binding |
| Privilege sprawl | entropy grows silently | periodic least-privilege projection |
| Machine identities | automation scales faster than review | short-lived tokens and attestation |
| Low observability | risky actions are invisible | deny or instrument before access |
| High reversibility | mistakes can be undone | allow more autonomy with audit |
| Low reversibility | damage is permanent | strict gates and scoping |

## 3. Worked Sample — Break-Glass Access

```text
C_a = 0.75
Θ = 0.95
Φ = 0.80
μ = 0.60
F = 0.90
Ω = 0.60
Γ_r = 0.70
Ξ_b = 0.80
```

```text
H_sa = 0.75×0.95×0.80 − 0.60×0.90 + 0.60 = 0.630
Blast penalty = Ξ_b(1 − Γ_r) = 0.80×0.30 = 0.240
H_adjusted = 0.390
```

Decision: allow through break-glass with time box, recording, audit, and automatic privilege removal.

## 4. Worked Sample — MFA Fatigue

```text
C_a = 0.50
Θ = 0.50
Φ = 0.85
μ = 0.90
F = 0.90
Ω = 0.10
H_sa = 0.50×0.50×0.85 − 0.90×0.90 + 0.10 = -0.4975
```

Decision: repeated prompts produce negative value. Replace with passkeys, device binding, and anomaly-triggered step-up.

## 5. Worked Sample — High Observability, Low Friction

```text
C_a = 0.85
Θ = 0.40
Φ = 0.95
μ = 0.20
F = 0.20
Ω = 0.50
H_sa = 0.85×0.40×0.95 − 0.20×0.20 + 0.50 = 0.783
```

Decision: allow. Strong scoping and observability make low-friction access safe.

## 6. Worked Sample — Broad Admin Role Request

```text
C_a = 0.35
Θ = 0.75
Φ = 0.60
μ = 0.30
F = 0.30
Ω = 0.10
Σ_s = 0.70
Ξ_b = 0.90
Γ_r = 0.20
```

```text
H_sa = 0.35×0.75×0.60 − 0.30×0.30 + 0.10 = 0.1675
Penalty = Σ_s + Ξ_b(1 − Γ_r) = 0.70 + 0.90×0.80 = 1.42
H_adjusted = -1.2525
```

Decision: do not grant broad permanent admin. Project into scoped JIT access.

## 7. Iteration Checklist

1. Define threat temperature $Θ$.
2. Define access capacity $C_a$.
3. Define context multiplier $Φ_context$.
4. Compute friction $μF$.
5. Credit observability $Ω_obs$.
6. Check uncertainty $κ$, $Λ_q$, and $Σ_s$.
7. Check blast radius $Ξ_b$.
8. Check reversibility $Γ_r$.
9. Apply least-privilege projection $Π_l$.
10. Select allow, step-up, scope, deny, quarantine, or redesign.

## 8. Failure Mode Table

| Failure Mode | CpT Analogy | Security/Access Symptom | Fix |
|---|---|---|---|
| Thermal runaway | heat accumulates faster than dissipation | permissions expand faster than audits | automated access review |
| Freezing | too little energy for useful work | approvals block delivery | remove low-efficiency controls |
| Shock | abrupt temperature change | sudden policy rollout breaks workflows | staged rollout and simulation |
| Hidden heat | unmeasured energy | shadow access paths | discovery and telemetry |
| Phase change | qualitative state shift | incident changes operating mode | break-glass regime |
| Critical point | tiny changes cause huge effects | fragile production systems | reduce coupling and blast radius |
