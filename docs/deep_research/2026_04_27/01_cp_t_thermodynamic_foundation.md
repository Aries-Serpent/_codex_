# Research Note 01 — $C_pT$ Thermodynamic Foundation

## NotebookLM Metadata

- **Source type:** Research collection note
- **Topic:** Specific heat at constant pressure, temperature, and specific enthalpy
- **Key equation:** $h \approx C_pT$ under simplified assumptions

## 1. Definition

$C_pT$ is the product of specific heat at constant pressure and absolute temperature.

| Symbol | Meaning | Typical Units |
|---|---|---|
| $C_p$ | specific heat at constant pressure | J/(kg·K), kJ/(kg·K), J/(mol·K) |
| $T$ | absolute temperature | K |
| $C_pT$ | temperature-scaled heat capacity | J/kg, kJ/kg, J/mol |

For a constant-$C_p$ ideal-gas approximation with an implicit zero reference:

```text
h ≈ C_pT
```

The more rigorous temperature-relative expression is:

```text
h(T) − h(T_ref) = ∫[T_ref to T] C_p(T)dT
```

If $C_p$ is approximately constant:

```text
Δh ≈ C_p(T − T_ref) = C_pΔT
```

## 2. Why It Relates to Enthalpy

Specific enthalpy is:

```text
h = u + pv
```

At constant pressure:

```text
C_p = (∂h/∂T)_p
```

Therefore:

```text
dh = C_p dT
Δh = ∫ C_p(T)dT
```

For an ideal gas, enthalpy depends primarily on temperature. For incompressible substances, a common approximation is:

```text
Δh ≈ C_pΔT + vΔp
```

When pressure change is small:

```text
Δh ≈ C_pΔT
```

## 3. Validity Table

| Case | Relationship | Reliability |
|---|---|---|
| Ideal gas, constant $C_p$ | $Δh = C_pΔT$ | good over moderate ranges |
| Ideal gas, variable $C_p(T)$ | $Δh = ∫C_p(T)dT$ | better for large temperature ranges |
| Incompressible liquid/solid | $Δh ≈ C_pΔT + vΔp$ | good when volume is nearly constant |
| Phase change | add latent heat | required when state changes |
| Chemical reaction | add reaction/formation enthalpy | required for reacting systems |

## 4. Dimensional Logic

```text
C_p [J/(kg·K)] × T [K] = J/kg
```

That matches specific enthalpy units.

| Expression | Unit | Meaning |
|---|---:|---|
| $C_pT$ | J/kg | specific energy approximation |
| $C_pΔT$ | J/kg | specific enthalpy change |
| $mC_pΔT$ | J | total heat/enthalpy change approximation |
| $\dot{m}C_pΔT$ | W | energy flow rate |

## 5. Sample Calculation

Dry air approximation:

```text
C_p = 1.005 kJ/(kg·K)
T = 300 K
h ≈ C_pT = 301.5 kJ/kg
```

Heating from 300 K to 500 K:

```text
Δh ≈ 1.005 × (500 − 300) = 201 kJ/kg
```

## 6. Condensed Foundation

$C_pT$ is most useful as a simplified enthalpy estimate. The safest engineering form is usually the difference form $Δh≈C_pΔT$, because enthalpy reference zeros are conventional.
