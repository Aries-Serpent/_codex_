Azimuthal review: proposed formal notation
==========================================

Status and boundary
-------------------

This is a physics-inspired **proposed notation**, not physical law, measured
resilience, calibrated scoring, executable permission, or institutional
authority. See `architecture <azimuthal-reasoning-integrity.rst>`_ for its synthetic
illustrations (not measurements); this document intentionally contains no charts.
The companion source registry is
``src/codex/institutional/review-formulas.json``, schema
``codex.institutional.review-formulas.v1``. Stable identifiers RD4-F001 through
RD4-F058 cover every displayed equation, including the composite system.
Identifiers are never inherited from unrelated physics tables.

Source notation versus normalized typography
--------------------------------------------

The registry's ``source_preservation.source_expressions`` maps all 58 IDs to
the **parent-provided user transcription** received at integration. The same
strings are preserved in the source block at the end of this document.
The earlier lane shorthand is not labeled original and is not used as this
source. Provenance is the parent transcription, not an independently verified
upstream bytehash. ``formulas[].latex`` remains a separate normalized display
transcription for compatibility.

The source retains calligraphic families, exact operator spellings,
``D_n^{req}`` rather than normalized ``D_n^{\mathrm{required}}``,
``Fallback_n`` and the supplied boxed aligned composite. F008 and F027 each
have two supplied displays, recorded separately as well as together.
F038, F046 and F047 are explicitly **PROSE SOURCE**, not displayed user
equations. F056 and F057 are extracted from the supplied composite.
No set difference is invented.

Normalized differences are disclosed, not silently certified as corrections:
plain Latin families, ``operatorname``, expanded conditions/domains and
indicator notation differ from source. F038/F046/F047 turn prose into normalized
formulas. The normalized composite merges input/state lines, adds an explicit
dissent definition and expands source Next membership into cases; the supplied
composite is retained unchanged. In particular, source EligibleEvidence equality
is not silently repaired in the source block.
No semantic equivalence, calibration or numerical correctness is asserted.
Tests check exact source-to-document preservation separately from normalized
mapping and explicitly exercise these differences.

The lineage assertion
``75f7dab1dbff1521ab530dd32c5d7cf028f57669f24147676a5dbf917c9b69f6``
is **unverified**, supplied as lineage, and is **not an actual content digest**
of this document or any asset. Actual asset hashing is a separate evidence task.

Registry contract and implementation boundary
---------------------------------------------

Each formula has an ID, name, exact LaTeX, global symbol-table keys,
entry-specific conditions and a ``metadata_ref``. Resolve that reference in
``metadata`` for its computability, implementation, executable mapping,
assumptions/calibration, unknown/empty/zero-denominator behavior, tests,
provenance and package status. Conditions supplement rather than weaken the
shared metadata. This explicit shared-metadata bridge avoids pretending an
existing compatible registry was found.

All 58 equations are planned specifications, not implemented formula evaluators.
RD4-F054 alone is explicitly conceptual/noncomputable; other expressions are
conditional specifications, computable only if their domain requirements and
necessary services/calibration are actually supplied. There is no numerical
scoring implementation here. Existing ``core.canonical``, ``core.digest``,
``core.record`` and ``core.candidate`` are structural primitives for canonical
SHA-256, candidate envelopes and manifest binding, not implementations of
RD4-F005, RD4-F043 or the full transition system. Their existing
``test_fixed_clock_canonical_candidate`` is not formula proof. No runtime
mapping is asserted for any complete equation. Read-only inspection of
``src/codex/institutional/review.py`` establishes the bounded structural
correspondences below; no numeric formula evaluator is requested or implied.

* ``candidate_manifest`` hashes supplied file bytes/modes/context into a Draft
  manifest (RD4-F005/F043), without scanning or evaluating identity change.
* ``review_plan`` declares bearings, coverage and dissent (RD4-F008/F010/F011);
  ``lane_output`` validates supplied source/normalization/binding (F010/F011).
  Neither executes a reviewer or establishes calibrated independence.
* ``reconcile`` preserves findings/typed relations and returns missing-lane or
  conflict blockers with authorization ``none`` (F001/F003/F031/F033/F040/F045/
  F052/F053). Its initial/meta/final stages are not full reconciliation
  equations, assurance execution or closure.
* ``new_history``, ``append_event`` and ``fold_events`` supply bounded Draft
  history, copy-append, ordered UUIDv4 events, recomputed stage/blocker/pending
  state and cache source-event digest validation (F005/F007/F045/F056).
  They do not persist a tamperproof audit log, derive the full finding graph,
  evaluate evidence eligibility or implement arbitrary reopening/background
  monitoring. Cross-store event uniqueness remains coordinator-owned.
* ``resume`` checks current binding and exact supplied blocker clearances
  without skipping pending requirements (F050). Clearance strings are
  unverified assertions, not evidence/budget proof or the complete conjunction.
* ``remediation_adequacy`` checks finding-bound rotated follow-up evidence
  coverage (F026/F040), not Ready=PASS, truth, reproduction, audit or approval.
* ``attach_continuation`` returns a compatible Draft successor for the existing
  coordinator (F007/F058), not persistence, authorized application or closure.
  The coordinator must revalidate repository drift before writing.

The registry's ``review_sdk_mapping.bindings`` records all ten exact API names,
associated full RD4 IDs, implemented structural scope and explicit limitations.
Formula metadata remains planned: structural availability never implies that
the numerical, authorization or composite equations are implemented.

``test_review_formulas.py`` checks presence, exact document mapping, unique IDs,
symbol resolution, metadata and explicit edge conditions. Those tests are
neither mathematical proofs, calibration studies, runtime execution evidence,
nor evidence of authority. No dependency or packaging manifest is changed by
this lane. The parent's explicit declaration of ``review-formulas.json`` in
``codex.institutional`` package data is observed at ``pyproject.toml:722``;
external wheel verification remains pending.
At discovery ``pyproject.toml`` explicitly included only ``contracts.json`` for
that package. An explicit manifest declaration does not itself verify an
installed wheel: source availability, intended package inclusion and actual
external wheel checks are distinct evidence.

Bounded discovery and provenance
--------------------------------

Filename and content inspection covered ``src``, ``docs``, ``configs``,
``conf`` and relevant ``tests``. ``references`` did not exist.
``.github/agents`` was excluded entirely. This was not a remote, dependency-tree
or archive-wide search, nor proof that no registry exists anywhere.

* ``src/tools/coverage_physics_toolkit.py`` defines ``CoverageStrategy`` with
  ``equation_id:int``, ``table:str``, ``strategy_type:str``, ``description:str``,
  ``expected_coverage_gain:float``, ``implementation_time_minutes:int`` and
  ``test_template:str``. The ten instantiated references are
  ``Table1_TimeConstraints:{1,49,56}``, ``Table2_ImportMonitoring:{1,6}``,
  ``Table3_MultiOrchestrator:{4,15}`` and ``Table4_CoverageUplift:{2,3,6}``.
  They are table-local integers, templates and heuristic coverage gains/times,
  not a complete equation implementation. Eq49 describes
  ``J = Coverage/Runtime``. No dedicated toolkit test was found in the bounded
  filename/symbol search; generated test templates are not execution evidence.
* Its prose sources are
  ``docs/plans/Physics_Equations_Time_Constraints_Plan_Prompts.md``,
  ``Physics_Equations_Monitor_Behavior_Plan_Prompts.md``,
  ``Physics_Equations_Multi_Orchestrator_Patterns.md`` and
  ``Physics_Equations_Coverage_Uplift_Paths.md`` in that same directory.
  The first uses numbered equations and ``PROMPT.Goal``, ``Inputs``,
  ``Actions_Minimal``, ``Checks_Fast_Invariants``, ``Decision`` and
  ``FollowUps_FutureEvolution``. Inspected entries include #1 Schrodinger,
  #2 Energy-Momentum, #3 Lorentz factor and #4 Continuity. Other tables contain
  corresponding prose/prompt mappings, not a compatible machine registry.
* ``docs/PHYSICS_TECHNICAL_REFERENCE.md`` uses named equations/method references,
  not stable formula IDs. Inspected calculations include logistic
  ``x_next=r*x*(1-x)`` and Reynolds ``Re=rho*v*L/mu``.
  ``src/agents/advanced_physics_calculators.py`` contains
  ``ChaoticAttractor._logistic_map`` and ``FluidChannel.reynolds_number``.
  ``tests/agents/test_advanced_physics_calculators.py`` contains calculator
  tests, including logistic iteration/chaos; those were inspected, not run here.
  Their physics domains and constants do not calibrate institutional review.
* ``docs/deep_research/2026_04_27/03_equation_variables_and_mermaid_maps.md``
  contains an unnumbered research formula stack and canonical variables:
  ``h=u+pv``, ``H_sa=C_a*Theta*Phi_context-muF+Omega_obs``,
  ``B*=eta*F_trust/kappa`` and context weights summing to one. No review
  evaluator, stable formula IDs or compatible unknown-value policy is supplied.
* ``docs/modeling/registry.md`` documents model-loader keys
  ``local_path/path/model_path``, ``pretrained_model_name_or_path`` and
  ``model_id``, with ``causal/mlm`` tasks. It is not a formula registry.

The JSON records those references and limits explicitly. No existing source
justifies importing its heuristic gains, physical constants, approval language
or denominator conventions into this model.

Global symbols and domains
--------------------------

The following table is global to every equation; the JSON contains the same
families as machine-readable descriptions. Subscripts distinguish overloads:
resource vector ``r_n`` differs from evidence recency ``r_e``; lineage label
``lambda`` differs from novelty coefficient vector ``bold lambda``; conflict
coefficient ``c_n(f,g)`` differs from bearing coverage ``c_{i,n}`` and checkpoint
``c``; proposed dispositions are not resilience dimension sets.

.. list-table::
   :header-rows: 1
   :widths: 28 72

   * - Symbol/family
     - Meaning/domain
   * - :math:`n,i,f,g,e,h,j,d`
     - Nonnegative iteration; bearing, finding, evidence, independence,
       assessment-component and resilience-dimension indices respectively.
   * - :math:`C_n,X_n,I_n`
     - Bound candidate manifest, review context, and input pair.
       Reviewed/current superscripts distinguish candidate snapshots.
   * - :math:`G_n,V_n,S_n`
     - Directed typed claim/finding multigraph, ordered append-only events,
       and input/graph/event state. Staged graphs have r0/r1/r2 superscripts.
   * - :math:`F_n,F_n^{\mathrm{crit}},R_n^{\mathrm{conf}},\operatorname{Changed}_n`
     - Findings, unresolved critical findings without authorized boundary,
       conflict edges and bound manifest differences.
   * - :math:`\Theta_n,b_i,\theta_i,w_{i,n},k_n`
     - Finite bearing tuples; identity, visualization angle, nonnegative
       active weight and active count. Parent/expiry/mode are explicit.
   * - :math:`P_n^{\mathrm{dispatch}},L_{i,n},L_n^{\mathrm{dissent}}`
     - Dispatch plan, lane outputs and dissent output, never assurance authority.
   * - :math:`\mathbf i_{i,n},K_i^{\mathrm{ind}},\alpha_h,\iota_{i,n}`
     - Eight independence dimensions in calibrated [0,1] or unknown,
       profile-critical subset, nonnegative normalized optional summary weights.
   * - :math:`\mu_{i,n},\mu_{f,n},\mathbf f_{i,n}`
     - Distinct nonnegative lane/finding magnitudes; visualization vector.
   * - :math:`T_n,c_n(f,g),T_{\max}`
     - Tension, conflict coefficient in [0,1], profile threshold.
   * - :math:`c_{i,n},\kappa_n,\kappa_n^{\mathrm{crit}},K_n^{\mathrm{bear}}`
     - Bearing coverage in [0,1] or unknown, weighted/critical summaries,
       nonempty critical bearing set.
   * - :math:`\pi_{i,n+1},\operatorname{Fallback}`
     - Nonnegative priority proposals; explicit preserve_prior/balanced policy.
   * - :math:`\mathbf u_{f,n}=(s_f,p_f,x_f,\nu_f)`
     - Severity, probability, exposure, uncertainty; primarily a risk vector.
   * - :math:`r_n,r_n^{\mathrm{used}},r_n^{\mathrm{limit}},B_n^{\mathrm{resource}}`
     - Resource context, usage, limits and operation-scoped resource blockers.
   * - :math:`e,\operatorname{EligibleEvidence}_n`
     - Evidence records and iteration-bound eligible set. Status, applicability,
       bindings and dispute predicates are explicit.
   * - :math:`\Lambda(e),M_{\lambda,n},M_\lambda^{\mathrm{cap}}`
     - Provenance lineage group, conditional capped memory aggregate and cap.
   * - :math:`\gamma_e,q_e,a_e,r_e,b_e`
     - Calibrated contribution, quality, applicability, recency and binding factors.
   * - :math:`h_j,J_{\mathrm{known}},J_{\mathrm{unknown}},J_{\mathrm{all}},\omega_j`
     - Known uncertainty components on an explicitly declared profile scale or
       unknown, partitioned index sets and nonnegative weights;
       known-uncertainty/unknown-fraction reports remain separate.
   * - :math:`\mathcal G_{f,\mathrm{stage}}^{\mathrm{required}},g`
     - Applicable required gates; PASS/FAIL/unknown/not_assessed values.
   * - :math:`\mathbf j_n,J_n,\boldsymbol\lambda`
     - Five novelty components, conditional normalized aggregate and profile weights.
   * - :math:`\mathbf z_n,Z_n,Z_n^{\mathrm{floor}},D_n^{\mathrm{required}},D_n^{\mathrm{crit}}`
     - Ordered 13-vector in ([0,1] union unknown)^13, conditional aggregate,
       critical floor, required and nonempty critical dimension sets.
   * - :math:`Q_n,D_n^{\mathrm{prop}},Y_n,\operatorname{Req}_n`
     - Explicit initial requirements/work queue, proposed dispositions, responses,
       second-reconciliation requirements.
   * - :math:`\Pi_n,A_n^{\mathrm{chg}},A_n^{\mathrm{disp}}`
     - Bound change set, separate change and disposition authorizations.
   * - :math:`P_n^{\mathrm{assure}},O_n^{\mathrm{tech}},O_n^{\mathrm{repro}},O_n^{\mathrm{audit}}`
     - Assurance DAG; distinct technical verification, reproduction and audit evidence.
   * - :math:`\operatorname{CloseReq}_n,\operatorname{Closure}_n,U_n^{\mathrm{assure}},U_n^{\mathrm{close}}`
     - Closure requirements, authorized review result, explicit unsatisfied requirements.
   * - :math:`\Delta_n^{\mathrm{id}},\Delta_{f,n}^{\mathrm{impact}},\operatorname{Dep}(f)`
     - Manifest identity/impact indicators and bound finding dependencies.
   * - :math:`B_n,\operatorname{Continue}_n,\operatorname{Next}_n`
     - Active operation-scoped blockers, assessed Boolean continuation,
       one of three proposed statuses; never approval.
   * - :math:`\epsilon_J,W_J,\Omega,\omega,\epsilon`
     - Novelty threshold, positive integer window, sensitivity domain,
       assessed weight/threshold parameter families.
   * - :math:`c,RD`
     - Checkpoint and recommendation-only reconciliation deliberation role.
   * - :math:`\mathcal R_0,\mathcal R_1,\mathcal R_2`
     - Proposed staged reconciliation operations, not physical dynamics.
   * - Other named operators
     - Typed operations/predicates named by the equations. ContextEvents and
       EventBatch are explicit context changes and ordered event batches.
       Qualitative resilience factors and institutional role names are concepts,
       not calibrated variables.

Profile and edge semantics
--------------------------

The profile chooses weights, thresholds, critical sets, :math:`T_{\max}`,
:math:`\epsilon_J`, :math:`W_J`, :math:`\Omega`, memory caps, required gates
and fallback policy. There are **no numeric defaults or measured calibration**.
Ordinal scales permit ordering only. Arithmetic needs justified interval/ratio
calibration; multiplicative risk/evidence factors need calibrated ratio scales.
Unknowns propagate rather than disappearing from denominators or minima.
Unknown nonrequired dimensions remain visible.

Empty/zero-denominator aggregates are undefined/not_assessed, never silently
zero or approval, except explicitly specified conditional cases below.
Required unknown predicates add applicable missing-evidence/calibration
requirements and cannot imply convergence. State folds events, and caches
require their source-event digest.

Findings, state and review bearings
-----------------------------------

RD4-F001 — findings

.. math::

   F_n=\operatorname{Findings}(G_n)

RD4-F002 — unresolved critical findings

.. math::

   F_n^{\mathrm{crit}}=\{f\in F_n:\operatorname{Critical}(f)\land\operatorname{Open}(f)\land\neg\operatorname{AuthorizedBoundary}(f)\}

RD4-F003 — conflicts

.. math::

   R_n^{\mathrm{conf}}=\operatorname{ConflictEdges}(G_n)

RD4-F004 — bound differences

.. math::

   \operatorname{Changed}_n=\operatorname{Diff}(C_n^{\mathrm{reviewed}},C_n^{\mathrm{current}})

RD4-F005 — input/state

.. math::

   I_n=(C_n,X_n),\qquad S_n=(I_n,G_n,V_n)

RD4-F006 — context advance

.. math::

   X_{n+1}=\operatorname{AdvanceContext}(X_n,\operatorname{ContextEvents}_n)

RD4-F007 — append-only events

.. math::

   V_{n+1}=\operatorname{AppendEvents}(V_n,\operatorname{EventBatch}_n)

Preserve source findings, dissent, graph multiplicity and event order. Missing
manifest bindings or boundary predicates are unknown, not authorization.
Context changes require explicit applicable context events.

RD4-F008 — finite active bearing set

.. math::

   \Theta_n=\{(b_i,\theta_i,w_{i,n},\operatorname{parent}_i,\operatorname{expiry}_i,\operatorname{mode}_i)\}_{i=1}^{k_n},\quad\operatorname{mode}_i\in\{\mathrm{replace},\mathrm{supplement}\}

RD4-F009 — admission

.. math::

   \operatorname{Admit}(b)=\operatorname{Trigger}(b)\land\operatorname{BoundedScope}(b)\land\operatorname{Budgeted}(b)\land\operatorname{OutputDefined}(b)\land\neg\operatorname{Duplicate}(b)

RD4-F010 — review lane

.. math::

   L_{i,n}=\operatorname{Review}_{b_i}(I_n,P_n^{\mathrm{dispatch}})

RD4-F011 — dissent lane

.. math::

   L_n^{\mathrm{dissent}}=\operatorname{DissentReview}(I_n,\{L_{i,n}\})

Admission requires all predicates assessed. Parent lineage, expiry and mode are
explicit; replacement never erases history. Dispatch is not assurance.

Independence, visualization, tension and coverage
-------------------------------------------------

RD4-F012 — eight-dimensional independence

.. math::

   \mathbf i_{i,n}=(i_{\mathrm{actor}},i_{\mathrm{model}},i_{\mathrm{prompt}},i_{\mathrm{evidence}},i_{\mathrm{environment}},i_{\mathrm{procedure}},i_{\mathrm{organization}},i_{\mathrm{custody}})

RD4-F013 — critical independence floor

.. math::

   i_{i,n}^{\mathrm{floor}}=\min_{h\in K_i^{\mathrm{ind}}}i_h

No critical dimensions means independence ``not_assessed``. The floor is defined
only with nonempty critical dimensions, known values and justified scales.
Unknown critical values are not omitted and cannot imply a passing floor.

RD4-F014 — optional summary

.. math::

   \iota_{i,n}=\sum_h\alpha_hi_h,\qquad\alpha_h\geq0,\quad\sum_h\alpha_h=1

Optional arithmetic requires calibrated scales and does not replace the vector.

RD4-F015 — visualization only

.. math::

   \mathbf f_{i,n}=\mu_{i,n}\begin{bmatrix}\cos\theta_i\\\sin\theta_i\end{bmatrix}

Cancellation never erases source findings or dissent.

RD4-F016 — tension

.. math::

   T_n=\frac{\sum_{(f,g)\in R_n^{\mathrm{conf}}}\mu_{f,n}\mu_{g,n}c_n(f,g)}{\sum_{f\in F_n}\mu_{f,n}},\qquad c_n(f,g)\in[0,1]

No assessed findings means ``not_applicable``. A zero denominator is undefined,
not zero. Unknown coefficients propagate; magnitudes need calibrated scales.

RD4-F017 — weighted bearing coverage

.. math::

   \kappa_n=\frac{\sum_iw_{i,n}c_{i,n}}{\sum_iw_{i,n}}

RD4-F018 — critical coverage

.. math::

   \kappa_n^{\mathrm{crit}}=\min_{i\in K_n^{\mathrm{bear}}}c_{i,n}

Positive active weights and a positive denominator are required. Critical
bearing sets are nonempty; unknown critical coverage precludes a known passing
floor. No active bearings is ``not_assessed``.

RD4-F019 — explicit fallback policy

.. math::

   w_{i,n+1}=\begin{cases}\pi_{i,n+1}/\sum_j\pi_{j,n+1}&\sum_j\pi_{j,n+1}>0,\\w_{i,n}&\sum_j\pi_{j,n+1}=0\land\operatorname{Fallback}=\mathrm{preserve\_prior},\\1/k_n&\sum_j\pi_{j,n+1}=0\land\operatorname{Fallback}=\mathrm{balanced}.\end{cases}

Require nonnegative priorities, :math:`k_n>0` and compatible active membership.
Changed membership requires explicit redistribution; absent fallback is
undefined. Zero priority is not permission to reuse incompatible old weights.

Risk, resources, evidence, uncertainty and adequacy
---------------------------------------------------

RD4-F020 — risk primarily as a vector

.. math::

   \mathbf u_{f,n}=(s_f,p_f,x_f,\nu_f)

Products are permitted only on calibrated ratio scales, not ordinal labels.

RD4-F021 — scoped resource blockers

.. math::

   B_n^{\mathrm{resource}}=\operatorname{ResourceBlockers}(r_n^{\mathrm{used}},r_n^{\mathrm{limit}})

RD4-F022 — eligible evidence

.. math::

   \operatorname{EligibleEvidence}(e)=[\operatorname{Status}(e)=\mathrm{ACTIVE}]\land\operatorname{Applicable}(e)\land\operatorname{BindingsCurrent}(e)\land\neg\operatorname{Disputed}(e)

Unknown usage is not restored budget. Unknown eligibility does not qualify;
expired/revoked/disputed evidence is ineligible.

RD4-F023 — conditional lineage-group memory

.. math::

   M_{\lambda,n}=\min\left(M_\lambda^{\mathrm{cap}},\sum_{e:\Lambda(e)=\lambda\land\operatorname{EligibleEvidence}(e)}\gamma_eq_ea_er_eb_e\right)

Calibrate contribution scales and provenance-lineage grouping first; otherwise
the ordered evidence ledger is authoritative and no aggregate is computed.
Empty evidence does not justify inventing a measured zero.

RD4-F024 — known uncertainty (Uncertainty and Adequacy)

.. math::

   H_n^{\mathrm{known}}=\frac{\sum_{j\in J_{\mathrm{known}}}\omega_jh_j}{\sum_{j\in J_{\mathrm{known}}}\omega_j}

No known positive weight means unknown, not zero.

RD4-F025 — explicit unknown-weight fraction

.. math::

   \eta_n^{\mathrm{unknown}}=\frac{\sum_{j\in J_{\mathrm{unknown}}}\omega_j}{\sum_{j\in J_{\mathrm{all}}}\omega_j}

Empty/zero total means undefined/not_assessed, not zero. Use a full partition,
valid nonnegative weights and explicitly calibrated uncertainty scales; report
both summaries. No health interpretation or unprovided uncertainty domain is
inferred. The legacy registry name ``known_health`` and symbol key ``health``
are compatibility aliases only, not the meaning of the expression.

RD4-F026 — stage readiness

.. math::

   \operatorname{Ready}(f,\mathrm{stage})=\bigwedge_{g\in\mathcal G_{f,\mathrm{stage}}^{\mathrm{required}}}(g=\mathrm{PASS})

An empty gate set does not grant approval. Unknown is not PASS; applicability
and authorization remain separate.

Novelty and the complete 13-dimensional resilience vector
---------------------------------------------------------

RD4-F027 — novelty components and conditional aggregate

.. math::

   \mathbf j_n=(j_{\mathrm{new}},j_{\mathrm{conflict}},j_{\mathrm{assumption}},j_{\mathrm{reopen}},j_{\mathrm{evidence}}),\qquad J_n=\boldsymbol\lambda^\top\mathbf j_n

Normalization and arithmetic need explicit profile calibration. Missing
components/history remain unknown.

RD4-F028 — fixed vector ordering

.. math::

   \mathbf z_n=(z_{\mathrm{logical}},z_{\mathrm{adversarial}},z_{\mathrm{institutional}},z_{\mathrm{operational}},z_{\mathrm{historical}},z_{\mathrm{portability}},z_{\mathrm{epistemic}},z_{\mathrm{ecological}},z_{\mathrm{resource}},z_{\mathrm{governance}},z_{\mathrm{architectural}},z_{\mathrm{evidentiary}},z_{\mathrm{temporal}})^\top\in([0,1]\cup\{\mathrm{unknown}\})^{13}

RD4-F029 — conditional geometric aggregate

.. math::

   Z_n=\begin{cases}0&\exists d\in D_n^{\mathrm{required}}:z_{d,n}=0,\\\exp\!\left(\dfrac{\sum_{d\in D_n^{\mathrm{required}}}\omega_d\ln z_{d,n}}{\sum_{d\in D_n^{\mathrm{required}}}\omega_d}\right)&\text{otherwise}.\end{cases}

Both branches require all required values known, a nonempty required set,
valid nonnegative weights and positive required total. The logarithmic branch
requires positive values. Required unknowns preclude computation even if another
required value is zero. Unknown nonrequired dimensions remain visible.

RD4-F030 — critical resilience floor

.. math::

   Z_n^{\mathrm{floor}}=\min_{d\in D_n^{\mathrm{crit}}}z_{d,n}

The critical set is nonempty; unknown critical dimensions cannot imply a known
passing floor. No metric closes findings or grants authority.

Sequential reconciliation and separately authorized routes
----------------------------------------------------------

RD4-F031 — initial reconciliation

.. math::

   (G_n^{r0},Q_n,D_n^{\mathrm{prop}},\Theta_{n+1})=\mathcal R_0(S_n,\{L_{i,n}\},L_n^{\mathrm{dissent}})

Here :math:`Q_n` is the explicit initial-reconciliation requirements/work queue.

RD4-F032 — proposals only

.. math::

   Y_n=\operatorname{ProposeResponses}(G_n^{r0},D_n^{\mathrm{prop}})

RD4-F033 — response reconciliation

.. math::

   (G_n^{r1},\operatorname{Req}_n)=\mathcal R_1(S_n,G_n^{r0},Y_n)

RD4-F034 — disposition routes

.. math::

   \operatorname{Route}(f)=\begin{cases}\mathrm{mutating}&\operatorname{Disposition}(f)=\mathrm{FIXED},\\\mathrm{nonmutating}&\operatorname{Disposition}(f)\in\{\mathrm{ACCEPTED\_RISK},\mathrm{NOT\_APPLICABLE},\mathrm{REJECTED\_WITH\_EVIDENCE},\mathrm{SUPERSEDED},\mathrm{DEFERRED},\mathrm{OUT\_OF\_SCOPE\_TRANSFER}\}.\end{cases}

FIXED names a proposed mutating route, not proof of implementation or closure.
Unknown/invalid dispositions block the affected route.

RD4-F035 — materialization

.. math::

   \Pi_n=\operatorname{MaterializeChangeSet}(Y_n,G_n^{r1})

RD4-F036 — change authorization

.. math::

   A_n^{\mathrm{chg}}=\operatorname{AuthorizeChange}(\Pi_n,C_n)

RD4-F037 — bound authorized application

.. math::

   C_{n+1}=\operatorname{Apply}(C_n,\Pi_n,A_n^{\mathrm{chg}})

RD4-F038 — nonmutating identity

.. math::

   C_{n+1}=C_n\quad\text{for a nonmutating route unless another authorized change applies}

A proposal cannot authorize itself. Change authority is external,
operation-specific and binding-current. Nonmutating dispositions still require
their own disposition authority and evidence.

RD4-F039 — assurance DAG

.. math::

   P_n^{\mathrm{assure}}=\operatorname{PlanAssurance}(G_n^{r1},C_{n+1})

RD4-F040 — assurance reconciliation

.. math::

   (G_n^{r2},\operatorname{CloseReq}_n)=\mathcal R_2(G_n^{r1},C_{n+1},O_n^{\mathrm{tech}},O_n^{\mathrm{repro}},O_n^{\mathrm{audit}})

RD4-F041 — disposition authorization

.. math::

   A_n^{\mathrm{disp}}=\operatorname{AuthorizeDisposition}(G_n^{r2},\operatorname{CloseReq}_n)

RD4-F042 — authorized closure review

.. math::

   \operatorname{Closure}_n=\operatorname{ReviewClosure}(G_n^{r2},A_n^{\mathrm{disp}})

Planning is not execution. Verification is not reproduction or audit.
Missing/disputed/stale evidence remains a requirement. An authorized service,
not deliberation or a score, persists accepted closure.

Impact, blockers, continuation and sensitivity
-----------------------------------------------

RD4-F043 — identity change

.. math::

   \Delta_n^{\mathrm{id}}=\mathbf1[\operatorname{digest}(C_n^{\mathrm{reviewed}})\ne\operatorname{digest}(C_n^{\mathrm{current}})]

RD4-F044 — dependency impact

.. math::

   \Delta_{f,n}^{\mathrm{impact}}=\mathbf1[\operatorname{Dep}(f)\cap\operatorname{Changed}_n\ne\varnothing]

Missing manifests/dependencies are unknown, not evidence of no impact.

RD4-F045 — active blockers

.. math::

   B_n=\{b:\operatorname{active}(b,n)\}

RD4-F046 — explicit unsatisfied requirements

.. math::

   U_n^{\mathrm{assure}}=\{q\in\operatorname{AssuranceRequirements}_n:\neg\operatorname{Satisfied}(q)\},\quad U_n^{\mathrm{close}}=\{q\in\operatorname{CloseReq}_n:\neg\operatorname{Satisfied}(q)\}

Unknown satisfaction remains unsatisfied for convergence. Blockers retain
reason, owner, affected operations and resume target; they do not globally halt
safe unrelated development.

RD4-F047 — novelty window

.. math::

   \operatorname{WindowSatisfied}_n=\bigwedge_{t=n-W_J+1}^{n}(J_t^{\mathrm{normalized}}<\epsilon_J)

Use the configured positive window and threshold; enough consecutive assessed
history and calibrated normalization are required. Empty/missing history is
unknown, not stable.

RD4-F048 — continuation predicate

.. math::

   \operatorname{Continue}_n=\mathbf1[F_n^{\mathrm{crit}}\ne\varnothing\lor T_n>T_{\max}\lor\kappa_n^{\mathrm{crit}}<1\lor\Delta_n^{\mathrm{id}}=1\lor U_n^{\mathrm{assure}}\ne\varnothing\lor U_n^{\mathrm{close}}\ne\varnothing\lor\neg\operatorname{WindowSatisfied}_n\lor\neg\operatorname{SensitivityStable}_n]

Required unknown predicates cannot imply convergence: add an applicable
missing-evidence/calibration requirement. Do not compare uncalibrated scores.

RD4-F049 — three statuses, not three authorities

.. math::

   \operatorname{Next}_n=\begin{cases}\mathrm{STOP\_SAFELY}&B_n\ne\varnothing,\\\mathrm{ROTATE\_AND\_CONTINUE}&B_n=\varnothing\land\operatorname{Continue}_n=1,\\\mathrm{CONVERGED\_FOR\_AUTHORIZED\_DECISION}&B_n=\varnothing\land\operatorname{Continue}_n=0.\end{cases}

STOP_SAFELY scopes affected operations; convergence is never approval.

RD4-F050 — explicit checkpoint resumption

.. math::

   \operatorname{Resume}(c)=\operatorname{Rebind}(c)\land\operatorname{BlockersCleared}(c)\land\operatorname{EvidenceRevalidated}(c)\land\operatorname{BudgetRestored}(c)\land\operatorname{TransitionValid}(c)

Resume at ``pending_requirement`` or ``blocked_from_state``, never guessed
success. Expiry/revocation appends reopening events through an authorized
service and reevaluates closure/activation. No background monitor is implemented.

RD4-F051 — sensitivity stability

.. math::

   \operatorname{SensitivityStable}_n=\mathbf1[\operatorname{Next}_n(\omega,\epsilon)=\operatorname{Next}_n(\omega',\epsilon')\ \text{for every assessed pair in }\Omega]

Proposed assessment methods are finite enumeration, interval proof, symbolic
analysis and bounded sampling. Sampling covers assessed samples only, not a
continuous-domain proof. Empty assessment is not stable. Evaluate comparisons
on fixed base predicate snapshots, without recursively evaluating sensitivity
inside itself; unassessed requirements stay explicit.

Deliberation boundary and qualitative interpretation
----------------------------------------------------

RD4-F052 — no delegated authority

.. math::

   \operatorname{Authority}(RD)=\operatorname{Mutation}(RD)=\operatorname{Execution}(RD)=\operatorname{Reproduction}(RD)=\operatorname{Audit}(RD)=\operatorname{Approval}(RD)=0

RD4-F053 — recommendation role

.. math::

   \operatorname{Reconcile}(RD)=\operatorname{RecommendBearing}(RD)=\operatorname{ReopenFinding}(RD)=\operatorname{PreserveUncertainty}(RD)=\operatorname{RecommendContinuation}(RD)=1

Zero/one denote role boundaries, not measured scores. Reopening is a
recommendation persisted by an authorized service, not direct graph mutation.

RD4-F054 — conceptual, noncomputable relation

.. math::

   \operatorname{ResilienceEvidence}\underset{\mathrm{conceptual}}{\propto}\operatorname{AnalyticalDiversity}\times\operatorname{SequentialReconciliation}\times\operatorname{EvidenceBinding}\times\operatorname{ReversibleHistory}\times\operatorname{RotatedRetesting}

There is no calibrated multiplication, causal law or numerical inference here.

RD4-F055 — institutional separation

.. math::

   \operatorname{Orchestration}\ne\operatorname{Reconciliation}\ne\operatorname{Implementation}\ne\operatorname{Verification}\ne\operatorname{Reproduction}\ne\operatorname{Audit}\ne\operatorname{Approval}\ne\operatorname{Authority}

All named institutional roles are distinct, not merely adjacent inequalities.
Separation does not itself establish independence.

RD4-F056 — event-derived graph

.. math::

   G_{n+1}=\operatorname{DeriveGraph}(V_{n+1},\operatorname{EligibleEvidence}_n)

Caches require source-event digests. Evidence is iteration-bound and eligibility
is reevaluated on expiry/revocation before reuse.

RD4-F057 — reassessment, not invented scoring

.. math::

   \mathbf z_{n+1}=\operatorname{AssessResilience}(C_{n+1},X_{n+1},G_{n+1})

Preserve all thirteen dimensions and explicit unknowns.

Complete proposed transition system
------------------------------------

RD4-F058 — composite transition

.. math::

   \boxed{\begin{aligned}I_n&=(C_n,X_n),\quad S_n=(I_n,G_n,V_n),\\L_{i,n}&=\operatorname{Review}_{b_i}(I_n,P_n^{\mathrm{dispatch}}),\\L_n^{\mathrm{dissent}}&=\operatorname{DissentReview}(I_n,\{L_{i,n}\}),\\(G_n^{r0},Q_n,D_n^{\mathrm{prop}},\Theta_{n+1})&=\mathcal R_0(S_n,\{L_{i,n}\},L_n^{\mathrm{dissent}}),\\Y_n&=\operatorname{ProposeResponses}(G_n^{r0},D_n^{\mathrm{prop}}),\\(G_n^{r1},\operatorname{Req}_n)&=\mathcal R_1(S_n,G_n^{r0},Y_n),\\C_{n+1}&=\operatorname{ApplyAuthorizedRoutes}(C_n,G_n^{r1},Y_n),\\P_n^{\mathrm{assure}}&=\operatorname{PlanAssurance}(G_n^{r1},C_{n+1}),\\(G_n^{r2},\operatorname{CloseReq}_n)&=\mathcal R_2(G_n^{r1},C_{n+1},O_n^{\mathrm{tech}},O_n^{\mathrm{repro}},O_n^{\mathrm{audit}}),\\\operatorname{Closure}_n&=\operatorname{ReviewAuthorizedClosure}(G_n^{r2},\operatorname{CloseReq}_n),\\X_{n+1}&=\operatorname{AdvanceContext}(X_n,\operatorname{ContextEvents}_n),\\V_{n+1}&=\operatorname{AppendEvents}(V_n,\operatorname{EventBatch}_n),\\G_{n+1}&=\operatorname{DeriveGraph}(V_{n+1},\operatorname{EligibleEvidence}_n),\\\mathbf z_{n+1}&=\operatorname{AssessResilience}(C_{n+1},X_{n+1},G_{n+1}),\\\operatorname{Next}_n&=\begin{cases}\mathrm{STOP\_SAFELY}&B_n\ne\varnothing,\\\mathrm{ROTATE\_AND\_CONTINUE}&B_n=\varnothing\land\operatorname{Continue}_n=1,\\\mathrm{CONVERGED\_FOR\_AUTHORIZED\_DECISION}&B_n=\varnothing\land\operatorname{Continue}_n=0.\end{cases}\end{aligned}}

``ApplyAuthorizedRoutes`` expands RD4-F034–F038: materialization and separate
change authorization for mutating routes, identity for nonmutating routes
unless another authorized change applies. ``ReviewAuthorizedClosure`` expands
RD4-F041–F042: distinct disposition authorization and closure review.
Both are proposed service boundaries, not implemented shortcuts.
Required unknowns preclude convergence; sensitivity uses fixed noncircular
predicate snapshots. None of this notation implements a scheduler, performs
mutation, executes assurance, approves a disposition or activates a candidate.

Parent-transcribed source expressions
-------------------------------------

Provenance: parent-provided user transcription, received
``2026-10-25T00:31:12.400+00:00``. The literal source below is separate from all
normalized displays above. F008/F027 retain the supplied separate-display
annotation; their individual displays are also in registry metadata.
F038/F046/F047 are prose. F056/F057 are expressions extracted from the supplied
composite. No upstream content-hash verification or mathematical proof is claimed.

.. code-block:: text

   SOURCE RD4-F001: \mathcal F_n=Findings(\mathcal G_n)
   SOURCE RD4-F002: \mathcal F_n^{crit}=\{f\in\mathcal F_n:Critical(f)\land Open(f)\land\neg AuthorizedBoundary(f)\}
   SOURCE RD4-F003: \mathcal R_n^{conf}=ConflictEdges(\mathcal G_n)
   SOURCE RD4-F004: Changed_n=Diff(\mathcal C_n^{reviewed},\mathcal C_n^{current})
   SOURCE RD4-F005: \mathcal I_n=(\mathcal C_n,\mathcal X_n),\qquad\mathcal S_n=(\mathcal I_n,\mathcal G_n,\mathcal V_n)
   SOURCE RD4-F006: \mathcal X_{n+1}=AdvanceContext(\mathcal X_n,ContextEvents_n)
   SOURCE RD4-F007: \mathcal V_{n+1}=AppendEvents(\mathcal V_n,EventBatch_n)
   SOURCE RD4-F008: \Theta_n=\{(b_i,\theta_i,w_{i,n},parent_i,expiry_i,mode_i)\}_{i=1}^{k_n}; separate supplied display mode_i\in\{replace,supplement\}
   SOURCE RD4-F009: Admit(b)=Trigger(b)\land BoundedScope(b)\land Budgeted(b)\land OutputDefined(b)\land\neg Duplicate(b)
   SOURCE RD4-F010: \mathcal L_{i,n}=Review_{b_i}(\mathcal I_n,\mathcal P_n^{dispatch})
   SOURCE RD4-F011: \mathcal L_n^{dissent}=DissentReview(\mathcal I_n,\{\mathcal L_{i,n}\})
   SOURCE RD4-F012: \mathbf i_{i,n}=(i_{actor},i_{model},i_{prompt},i_{evidence},i_{environment},i_{procedure},i_{organization},i_{custody})
   SOURCE RD4-F013: i_{i,n}^{floor}=\min_{h\in K_i^{ind}}i_h
   SOURCE RD4-F014: \iota_{i,n}=\sum_h\alpha_hi_h,\qquad \alpha_h\ge0,\qquad \sum_h\alpha_h=1
   SOURCE RD4-F015: \mathbf f_{i,n}=\mu_{i,n}\begin{bmatrix}\cos\theta_i\\\sin\theta_i\end{bmatrix}
   SOURCE RD4-F016: \mathcal T_n=\frac{\sum_{(f,g)\in\mathcal R_n^{conf}}\mu_{f,n}\mu_{g,n}c_n(f,g)}{\sum_{f\in\mathcal F_n}\mu_{f,n}},\qquad c_n(f,g)\in[0,1]
   SOURCE RD4-F017: \kappa_n=\frac{\sum_iw_{i,n}c_{i,n}}{\sum_iw_{i,n}},\qquad \sum_iw_{i,n}>0
   SOURCE RD4-F018: \kappa_n^{crit}=\min_{i\in K_n^{bear}}c_{i,n}
   SOURCE RD4-F019: w_{i,n+1}=\begin{cases}\pi_{i,n+1}/\sum_j\pi_{j,n+1},&\sum_j\pi_{j,n+1}>0\\w_{i,n},&\sum_j\pi_{j,n+1}=0\land Fallback_n=preserve\_prior\\1/k_n,&\sum_j\pi_{j,n+1}=0\land Fallback_n=balanced\end{cases}
   SOURCE RD4-F020: \mathbf u_{f,n}=(s_f,p_f,x_f,\nu_f)
   SOURCE RD4-F021: \mathcal B_n^{resource}=ResourceBlockers(\mathbf r_n^{used},\mathbf r_n^{limit})
   SOURCE RD4-F022: EligibleEvidence(e)=Status(e)=ACTIVE\land Applicable(e)\land BindingsCurrent(e)\land\neg Disputed(e)
   SOURCE RD4-F023: M_{\lambda,n}=\min\left(M_{\lambda}^{cap},\sum_{e:\Lambda(e)=\lambda\land EligibleEvidence(e)}\gamma_eq_ea_er_eb_e\right)
   SOURCE RD4-F024: \mathcal H_n^{known}=\frac{\sum_{j\in J_{known}}\omega_jh_j}{\sum_{j\in J_{known}}\omega_j}
   SOURCE RD4-F025: \eta_n^{unknown}=\frac{\sum_{j\in J_{unknown}}\omega_j}{\sum_{j\in J_{all}}\omega_j}
   SOURCE RD4-F026: Ready(f,stage)=\bigwedge_{g\in G_{f,stage}^{required}}(g=PASS)
   SOURCE RD4-F027: \mathbf j_n=(j_{new},j_{conflict},j_{assumption},j_{reopen},j_{evidence}); separate display \mathcal J_n=\boldsymbol\lambda^T\mathbf j_n
   SOURCE RD4-F028: \mathbf z_n=(z_{logical},z_{adversarial},z_{institutional},z_{operational},z_{historical},z_{portability},z_{epistemic},z_{ecological},z_{resource},z_{governance},z_{architectural},z_{evidentiary},z_{temporal})^T
   SOURCE RD4-F029: Z_n=\begin{cases}0,&\exists d\in D_n^{req}:z_{d,n}=0\\\exp\left(\frac{\sum_{d\in D_n^{req}}\omega_d\ln z_{d,n}}{\sum_{d\in D_n^{req}}\omega_d}\right),&otherwise\end{cases}
   SOURCE RD4-F030: Z_n^{floor}=\min_{d\in D_n^{crit}}z_{d,n}
   SOURCE RD4-F031: (\mathcal G_n^{r0},\mathcal Q_n,\mathcal D_n^{prop},\Theta_{n+1})=\mathscr R_0(\mathcal S_n,\{\mathcal L_{i,n}\},\mathcal L_n^{dissent})
   SOURCE RD4-F032: \mathcal Y_n=ProposeResponses(\mathcal G_n^{r0},\mathcal D_n^{prop})
   SOURCE RD4-F033: (\mathcal G_n^{r1},\mathcal Req_n)=\mathscr R_1(\mathcal S_n,\mathcal G_n^{r0},\mathcal Y_n)
   SOURCE RD4-F034: Route(f)=\begin{cases}mutating,&Disposition(f)=FIXED\\nonmutating,&Disposition(f)\in\{ACCEPTED\_RISK,NOT\_APPLICABLE,REJECTED\_WITH\_EVIDENCE,SUPERSEDED,DEFERRED,OUT\_OF\_SCOPE\_TRANSFER\}\end{cases}
   SOURCE RD4-F035: \Pi_n=MaterializeChangeSet(\mathcal Y_n,\mathcal G_n^{r1})
   SOURCE RD4-F036: \mathcal A_n^{chg}=AuthorizeChange(\Pi_n,\mathcal C_n)
   SOURCE RD4-F037: \mathcal C_{n+1}=Apply(\mathcal C_n,\Pi_n,\mathcal A_n^{chg})
   SOURCE RD4-F038: PROSE SOURCE: Nonmutating routes retain \(\mathcal C_{n+1}=\mathcal C_n\), unless another authorized change exists.
   SOURCE RD4-F039: \mathcal P_n^{assure}=PlanAssurance(\mathcal G_n^{r1},\mathcal C_{n+1})
   SOURCE RD4-F040: (\mathcal G_n^{r2},\mathcal CloseReq_n)=\mathscr R_2(\mathcal G_n^{r1},\mathcal C_{n+1},\mathcal O_n^{tech},\mathcal O_n^{repro},\mathcal O_n^{audit})
   SOURCE RD4-F041: \mathcal A_n^{disp}=AuthorizeDisposition(\mathcal G_n^{r2},\mathcal CloseReq_n)
   SOURCE RD4-F042: Closure_n=ReviewClosure(\mathcal G_n^{r2},\mathcal A_n^{disp})
   SOURCE RD4-F043: \Delta_n^{id}=\mathbb1[digest(\mathcal C_n^{reviewed})\ne digest(\mathcal C_n^{current})]
   SOURCE RD4-F044: \Delta_{f,n}^{impact}=\mathbb1[Dep(f)\cap Changed_n\ne\varnothing]
   SOURCE RD4-F045: \mathcal B_n=\{b:active(b,n)\}
   SOURCE RD4-F046: PROSE SOURCE: Unsatisfied assurance and closure requirements remain explicit as \(\mathcal U_n^{assure}\) and \(\mathcal U_n^{close}\).
   SOURCE RD4-F047: PROSE SOURCE: `WindowSatisfied` means the normalized information-return summary remains below the configured threshold for the configured window.
   SOURCE RD4-F048: Continue_n=\mathbb1[\mathcal F_n^{crit}\ne\varnothing\lor\mathcal T_n>T_{max}\lor\kappa_n^{crit}<1\lor\Delta_n^{id}=1\lor\mathcal U_n^{assure}\ne\varnothing\lor\mathcal U_n^{close}\ne\varnothing\lor\neg WindowSatisfied_n\lor\neg SensitivityStable_n]
   SOURCE RD4-F049: Next_n=\begin{cases}STOP\_SAFELY,&\mathcal B_n\ne\varnothing\\ROTATE\_AND\_CONTINUE,&\mathcal B_n=\varnothing\land Continue_n=1\\CONVERGED\_FOR\_AUTHORIZED\_DECISION,&\mathcal B_n=\varnothing\land Continue_n=0\end{cases}
   SOURCE RD4-F050: Resume(c)=Rebind(c)\land BlockersCleared(c)\land EvidenceRevalidated(c)\land BudgetRestored(c)\land TransitionValid(c)
   SOURCE RD4-F051: SensitivityStable_n=\mathbb1[Next_n(\omega,\epsilon)=Next_n(\omega',\epsilon')\text{ for every assessed pair in }\Omega]
   SOURCE RD4-F052: Authority(RD)=Mutation(RD)=Execution(RD)=Reproduction(RD)=Audit(RD)=Approval(RD)=0
   SOURCE RD4-F053: Reconcile(RD)=RecommendBearing(RD)=ReopenFinding(RD)=PreserveUncertainty(RD)=RecommendContinuation(RD)=1
   SOURCE RD4-F054: ResilienceEvidence\propto_{conceptual}AnalyticalDiversity\times SequentialReconciliation\times EvidenceBinding\times ReversibleHistory\times RotatedRetesting
   SOURCE RD4-F055: Orchestration\ne Reconciliation\ne Implementation\ne Verification\ne Reproduction\ne Audit\ne Approval\ne Authority
   SOURCE RD4-F056: \mathcal G_{n+1}=DeriveGraph(\mathcal V_{n+1},EligibleEvidence_n)
   SOURCE RD4-F057: \mathbf z_{n+1}=AssessResilience(\mathcal C_{n+1},\mathcal X_{n+1},\mathcal G_{n+1})
   SOURCE RD4-F058: \boxed{\begin{aligned}\mathcal I_n&=(\mathcal C_n,\mathcal X_n)\\\mathcal S_n&=(\mathcal I_n,\mathcal G_n,\mathcal V_n)\\\mathcal L_{i,n}&=Review_{b_i}(\mathcal I_n,\mathcal P_n^{dispatch})\\(\mathcal G_n^{r0},\mathcal Q_n,\mathcal D_n^{prop},\Theta_{n+1})&=\mathscr R_0(\mathcal S_n,\{\mathcal L_{i,n}\},\mathcal L_n^{dissent})\\\mathcal Y_n&=ProposeResponses(\mathcal G_n^{r0},\mathcal D_n^{prop})\\(\mathcal G_n^{r1},\mathcal Req_n)&=\mathscr R_1(\mathcal S_n,\mathcal G_n^{r0},\mathcal Y_n)\\\mathcal C_{n+1}&=ApplyAuthorizedRoutes(\mathcal C_n,\mathcal G_n^{r1},\mathcal Y_n)\\\mathcal P_n^{assure}&=PlanAssurance(\mathcal G_n^{r1},\mathcal C_{n+1})\\(\mathcal G_n^{r2},\mathcal CloseReq_n)&=\mathscr R_2(\mathcal G_n^{r1},\mathcal C_{n+1},\mathcal O_n^{tech},\mathcal O_n^{repro},\mathcal O_n^{audit})\\Closure_n&=ReviewAuthorizedClosure(\mathcal G_n^{r2},\mathcal CloseReq_n)\\\mathcal X_{n+1}&=AdvanceContext(\mathcal X_n,ContextEvents_n)\\\mathcal V_{n+1}&=AppendEvents(\mathcal V_n,EventBatch_n)\\\mathcal G_{n+1}&=DeriveGraph(\mathcal V_{n+1},EligibleEvidence_n)\\\mathbf z_{n+1}&=AssessResilience(\mathcal C_{n+1},\mathcal X_{n+1},\mathcal G_{n+1})\\Next_n&\in\{STOP\_SAFELY,ROTATE\_AND\_CONTINUE,CONVERGED\_FOR\_AUTHORIZED\_DECISION\}\end{aligned}}
