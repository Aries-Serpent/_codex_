<!-- BEGIN: CODEX_DOCS_DYNAMICAL_SYSTEM -->
# Codex Dynamics: a quantum-operational model for single-shot repo runs

## Table of contents

1. State space and observables
2. Phase operators (P₁…P₆)
3. Quality gates as projectors
4. Patch algebra (creation/annihilation on files)
5. Canonicalization triad (merge/rename/delete)
6. Open-system dynamics (Hamiltonian + jump errors)
7. Action/optimal-control formulation
8. Measurement & run outcomes
9. Stability, invariants, and fixed points
10. Toy derivation on a duplicate-file family
11. Prompt adapter (how to use this in Codex specs)
12. Symbol legend

---

# 1) State space and observables

Let the run live in a composite Hilbert space

```text
𝓗 = 𝓗_files ⊗ 𝓗_tests ⊗ 𝓗_docs ⊗ 𝓗_tools .
```text
The repo’s instantaneous state is a vector |R_t⟩ or density matrix ρ_t on 𝓗.
File-family occupancies are number operators `{N_f}`; coverage, lint, type, etc. are Hermitian observables.

---

# 2) Phase operators (P₁…P₆)

Associate each execution phase with a (possibly time-dependent) operator:

```text
P₁: Preparation
P₂: Search & Mapping
P₃: Best-Effort Construction
P₄: Controlled Pruning
P₅: Error Capture
P₆: Finalization
```text
In the ideal, phase evolution is unitary `U_k = e^{-i H_k Δt}`; in practice we allow completely positive trace-preserving (CPTP) maps `𝓤_k` to model side-effects.

---

# 3) Quality gates as projectors

Define projectors (pass = 1, fail = 0):

```text
Π_lint, Π_type, Π_test, Π_cov(θ)
```text
with a coverage observable `Ĉ ∈ [0,100]` and threshold θ:

```text
Π_cov(θ) = Θ(Ĉ − θ)       (Θ is the Heaviside step function).
```text
The composite gate is

```text
G(θ) = Π_lint Π_type Π_test Π_cov(θ).
```text
A successful run postselects onto the +1 eigenspace of G(θ).

---

# 4) Patch algebra (creation/annihilation on files)

Model a unified patch to file f as a bosonic excitation with payload Δ:

```text
[a_f, a_g†] = δ_fg ,   [a_f, a_g] = 0 .
```text
Applying a patch is the action of `a_f†(Δ)`; reverting is `a_f(Δ)`.
Define a patch-cost operator (time-local)

```text
ℂ = ∑_f ∫ dΔ  c_f(Δ) a_f†(Δ) a_f(Δ),
```text
and a risk functional ℛ (see §7) that weights invasive edits.

Public-API (re)exports are encoded as commuting constraints `E_s = 1` for each expected symbol s in `__all__/index.ts/lib.rs`.

---

# 5) Canonicalization triad (merge/rename/delete)

For each duplicate family 𝔽 (e.g., `tokenizer.py0, .py1, .py00 → tokenizer.py`) define idempotent operators:

```text
𝕄_𝔽  (merge) ,   ℜ_𝔽  (rename) ,   𝔇_𝔽  (delete)
```text
with laws

```text
𝕄_𝔽² = 𝕄_𝔽 ,   ℜ_𝔽² = ℜ_𝔽 ,   𝔇_𝔽² = 𝔇_𝔽 ,
[𝕄_𝔽, ℜ_𝔽] = 0,   ℜ_𝔽 𝔇_𝔽 = 𝔇_𝔽 ℜ_𝔽 ,
N_suffix,𝔽 • (ℜ_𝔽 𝕄_𝔽) = 0   (no suffixed files remain).
```text
A successful canonicalization is the projector

```text
C_𝔽 = 𝔇_𝔽 ℜ_𝔽 𝕄_𝔽 .
```text
---

# 6) Open-system dynamics (Hamiltonian + jump errors)

Let the controlled Hamiltonian be

```text
H(t) = ∑_{k=1}^6 u_k(t) H_k  +  λ ℂ  +  μ ℛ ,
```text
where `u_k(t) ∈ {0,1}` toggles phases, λ, μ ≥ 0 tune cost/risk penalties.

Operationally the run is an open system evolving by a Lindblad master equation:

```text
ṙho = −i [H(t), ρ] + ∑_e γ_e ( J_e ρ J_e† − ½ {J_e† J_e, ρ} ),
```text
where each error mode e (lint fail, type fail, flaky test, IO error, etc.) has jump operator J_e.
Phase-5 logging corresponds to applying a documentation creation operator `D†` that appends a structured entry to `docs/reference/codex_questions.md` whenever any J_e fires.

---

# 7) Action/optimal-control formulation

Treat the run as an optimal-control problem minimizing the action

```text
S[path] = ∫_0^T [ L_base(ρ,u) + λ ⟨ℂ⟩_ρ + μ ⟨ℛ⟩_ρ
                 + α (1 − ⟨Π_test⟩_ρ) + β (θ − ⟨Ĉ⟩_ρ)_+ ] dt
```text
subject to boundary constraints:

```text
Π_noGH |R_t⟩ = |R_t⟩     (superselection: no GitHub Actions),
G(θ) |R_T⟩ = |R_T⟩       (all gates pass at final time),
C_𝔽 |R_T⟩ = |R_T⟩       (all canonicalizations applied),
E_s |R_T⟩ = |R_T⟩       (public exports present).
```text
Here `(x)_+ = max(x,0)`, and `Π_noGH` forbids any `.github/workflows/*` activation.

The partition function over all admissible patch paths is

```text
Z(β) = ∑_{paths} exp(−β S[path]),
```text
useful for reasoning about alternative diffs/branch strategies.

---

# 8) Measurement & run outcomes

At T, perform the projective measurement `{G(θ), 1−G(θ)}`.
Success probability:

```text
p_succ = Tr[ G(θ) ρ_T ] .
```text
Conditioning on success collapses onto the “green build” manifold; otherwise the state is fed back through P₅ (error capture) with updated controls.

---

# 9) Stability, invariants, and fixed points

**Invariants.**

* No-Actions invariant: `[H(t), Π_noGH] = 0` ⇒ forbidden files cannot be created/activated.
* Canonicalization decreases a Lyapunov potential `Φ = ∑_𝔽 N_suffix,𝔽`, and

```text
Φ_{t+} ≤ Φ_{t},   Φ_T = 0  (at a fixed point).
```text
**Fixed points.**
A fixed point `ρ*` satisfies

```text
[H(·), ρ*] = 0 ,   J_e ρ* = 0 ∀e ,   G(θ) ρ* = ρ* .
```text
Interpretation: no pending edits, no error channels active, all gates passing.

---

# 10) Toy derivation on a duplicate-file family

Consider one family 𝔽 = {`x.py0`, `x.py1`} with target `x.py`.
Occupancies `(n0, n1, n)` are eigenvalues of `{N_0, N_1, N}`.

Start with `|ψ₀⟩ = |1,1,0⟩`. Apply merge→rename→delete:

```text
|ψ₁⟩ = 𝕄_𝔽 |1,1,0⟩ = |0,0,1⟩         (content union landed in canonical)
|ψ₂⟩ = ℜ_𝔽 |0,0,1⟩ = |0,0,1⟩         (idempotent if already canonical)
|ψ₃⟩ = 𝔇_𝔽 |0,0,1⟩ = |0,0,1⟩         (no residual suffixed files)
```text
Quality gate projector `G(θ)` then acts only on tests/coverage; `Π_cov(θ)=1` if `Ĉ ≥ θ`.

---

# 11) Prompt adapter (drop-in snippet for your Codex specs)

```text
—[Quantum-Operational Constraints]—
1) Treat phases as control fields u_k(t) ∈ {0,1} multiplying H_k.
2) Minimize S[path] in §7; respect superselection Π_noGH and terminal constraints G(θ)=1, C_𝔽=1.
3) Implement canonicalization via the commuting, idempotent triad (𝕄, ℜ, 𝔇) per family.
4) Encode patches with creation ops a_f†; prefer low ℂ, low ℛ; keep exports E_s satisfied.
5) On any failure channel J_e, emit a Phase-5 log entry (exact template), then continue with adjusted controls.
6) Stop only when at a fixed point ρ* with Φ=0 and G(θ)=1.
```text
---

# 12) Symbol legend (quick reference)

* `|R_t⟩, ρ_t` — repo state (vector/density).
* `P₁…P₆` — phase operators (prep, map, build, prune, errors, finalize).
* `G(θ)` — composite quality gate with coverage threshold θ.
* `Π_noGH` — “no GitHub Actions” projector (hard constraint).
* `a_f†(Δ), a_f(Δ)` — patch create/revert on file f with delta Δ.
* `ℂ` — patch-cost operator; `ℛ` — risk functional.
* `𝕄, ℜ, 𝔇` — merge/rename/delete canonicalization ops (idempotent, commuting).
* `J_e` — error jump operator; `γ_e` — its rate.
* `H(t)` — controlled Hamiltonian; `u_k(t)` — phase control fields.
* `S[path]` — action to minimize; `Z(β)` — run partition function.
* `Φ` — duplicate-suffix potential; `ρ*` — fixed point (green build).

---

### One-line mnemonic

```text
“Drive ρ_t with U_phases while damping by J_errors,
create minimal a†-patches, annihilate duplicates with (𝕄,ℜ,𝔇),
postselect on G(θ)=1 under Π_noGH — and you’re done.”
```text
<!-- END: CODEX_DOCS_DYNAMICAL_SYSTEM -->
