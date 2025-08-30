<!-- BEGIN: CODEX_DOCS_DYNAMICAL_SYSTEM -->
# Codex as a Dynamical System

The Codex single-shot run can be interpreted through the lens of a quantum-style dynamical system. Repository states evolve through discrete phases, patches act as quanta, and quality gates serve as projectors.

## 1. System Overview

Let $|\Psi_t\rangle$ denote the repository process state at time $t$. The run progresses through phases $\{\mathsf{Prep},\mathsf{Map},\mathsf{Build},\mathsf{Prune},\mathsf{Error},\mathsf{Finalize}\}$ with tunable weights $\vec\kappa$.

## 2. State Space & Operators

- Basis $\{|r\rangle\}$ spans repo configurations.
- Patch creation/rollback operators: $a^\dagger$ creates a patch, $a$ reverts it, with $[a,a^\dagger]=\mathbf{1}$.
- Quality debt operator $D\ge0$ accumulates lint, type, test, coverage, and doc violations.
- $G$ is the GitHub Actions activation operator; feasible states satisfy $G|\Psi_t\rangle=0$.
- Phase generators $\mathcal{H}_\phi$ drive each phase $\phi$.

## 3. Dynamics

A phase-weighted Hamiltonian combines phase generators:

$$H = \alpha\mathcal{H}_{\text{prep}} + \beta\mathcal{H}_{\text{map}} + \gamma\mathcal{H}_{\text{build}} + \delta\mathcal{H}_{\text{prune}} + \varepsilon\mathcal{H}_{\text{error}} + \zeta\mathcal{H}_{\text{final}}.$$

An illustrative build generator:

$$\mathcal{H}_{\text{build}} = \eta_1 a^\dagger + \eta_2 a D + \eta_3 D^2.$$

Evolution follows a Schrödinger-like equation $i\hbar\partial_t|\Psi_t\rangle = H|\Psi_t\rangle$.

## 4. Constraints & Projectors

Quality gates are projectors $\Pi_\text{lint},\Pi_\text{type},\Pi_\text{test},\Pi_{\text{cov}(\ge c)},\Pi_\text{docs},\Pi_\text{noGH}$. The hard constraint $\Pi_\text{noGH}|\Psi\rangle=|\Psi\rangle$ keeps GitHub Actions off. Soft penalties use $1-\langle\Psi|\Pi_j|\Psi\rangle$.

## 5. Measurements & Error Capture

Failure probability is $P_{\text{err}}(t) = \langle\Psi_t|\Pi_{\text{err}}|\Psi_t\rangle$. On error, a logging superoperator appends diagnostic entries while preserving state evolution.

## 6. Objective: Free-Energy Minimization

We minimize run energy

$$\mathbb{E}[E] = \langle\Psi|H|\Psi\rangle + \sum_j\lambda_j\mathcal{C}_j(\Psi)$$

subject to $G|\Psi\rangle=0$. Temperature $T$ tunes exploration via $\beta=1/(k_B T)$.

## 7. Stationary Conditions

Variational calculus yields

$$(i\hbar\partial_t - H)|\Psi_t\rangle = \left(\lambda_G G + \sum_j \lambda_j \nabla_\Psi \mathcal{C}_j\right)|\Psi_t\rangle,$$

interpreted algorithmically: propose a patch with $a^\dagger$ that decreases quality debt; accept if it lowers $\mathbb{E}[E]$, otherwise revert with $a$.

## 8. Discrete Algorithmic Analog

With discrete steps $k$, $|\Psi_{k+1}\rangle = M_{\text{gates}} U_\Delta(\vec\kappa) |\Psi_k\rangle$, where $U_\Delta \approx I - i\Delta H$. Acceptance follows a Metropolis rule

$$p_{\text{accept}} = \min\left(1, e^{-\beta(\mathbb{E}[E]_{k+1}-\mathbb{E}[E]_k)}\right).$$

## 9. Summary Equation

$$\boxed{\min_{|\Psi\rangle:G|\Psi\rangle=0}\left\{\langle\Psi|H|\Psi\rangle + \sum_j\lambda_j\left(1-\langle\Psi|\Pi_j|\Psi\rangle\right)\right\};\ |\Psi_{k+1}\rangle \leftarrow M_{\text{gates}} U_\Delta(\vec\kappa) |\Psi_k\rangle.}$$

This formulation explains how Codex converges to high-quality, constraint-satisfying patches while ensuring GitHub Actions remain inactive.
<!-- END: CODEX_DOCS_DYNAMICAL_SYSTEM -->
