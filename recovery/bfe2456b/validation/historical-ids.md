# Historical identities: evidence and explicit unknowns

Prepared 2026-10-23 UTC from preserved evidence only. No tests, installs,
staging, commits or pushes were performed by this worker.

## Subsequent pinned observations

The coordinating execution later collected partial evidence at snapshot
`70798e17f0bb4463413684eddddd62358faa89d6` in a fresh isolated environment.
Of the separate 195 historical baseline-error modules, **164 have actual
printed node IDs, 28 still report `RecursionError`, and three have explicit
module skips**. The collection was interrupted, so these are observations,
not complete collection or execution results. See
`full/base-195-fresh-classification.json` and `test-comparison.md`.
This supersedes historical collection counts for current status but does not
recover any of the 295 missing historical identities below. The older evidence
and its provenance remain intentionally preserved.

## Provenance and interpretation

`collection-diff.md:39-75` records a reported historical population of 306
errors, with only 11 supplied dotted names. It explicitly says the complete
identity list never persisted; no complete historical artifact was supplied or
identified in the preserved recovery evidence. The original historical run date,
commit, exact pytest node IDs, classes and parameters are unavailable. This
document cannot identify the missing 295 entries or prove their resolution.

Parent handoff at **2026-10-23T03:57:34.525+00:00** reports that a cloud
session-store query resolved the original source task to session
`8b1c4b73-ebca-4c74-b3c9-54fcd95f7e23`, but repository/summary queries did
not find the recent recovery/full-comparison sessions. No additional historical
IDs were recovered. This is parent-supplied retrieval evidence, not an
independent or exhaustive search by this worker; the 295 identities remain unknown.

The 11 names below are the supplied identifiers, **not reconstructed pytest
node IDs**. Their old error → skip transitions and reasons are transcript
observations recorded in `collection-diff.md`, not independently verified old
results. No historical improvement is proven by their later collection alone.

The separate preserved baseline run began **2026-10-22T22:42:55.132784+00:00**
at `71613ee000808ab758cc2f8ddb07a05c5101f731`: 195 module collection errors,
all `RecursionError`, exit 2. These are not the historical 306 identities.
The required snapshot collection began
**2026-10-22T22:59:13.666228+00:00**, recording
`f507214f5d560762384eda29166d97b420d95948`, exit 0, no collection errors
and 44,053 collected items. Its metadata records concurrent dirty runtime
artifacts; this is not a clean isolated run.

The supplemental `logs/snapshot-nodeids-collection.log` contains **44,053
actual node-ID lines**, exit 0 in its companion `.exit`. Its command is reported
as `python -m pytest tests/ --collect-only -q -v` in `collection-diff.md:30-37`.
It has no independent invocation timestamp/commit record. The association with
the historical snapshot session is inherited, not proof of a fresh pinned run.
Both required logs and this supplemental log were published in
`d368aaba99618be8645108cd4ebc85607d6bea81`
(commit date **2026-10-22T23:26:39Z**). Publication is not execution time.

Below, “snapshot state” means those preserved collection observations, **not
current HEAD or fresh test execution**. A collected node is not a pass; an
absent node is neither a pass, proven skip, proven deletion nor proven error.
Environment-dependent ignore/skip rules can omit modules without error.

## Known supplied subset: 11 identifiers

Line references in the snapshot-state column are 1-based positions in
`logs/snapshot-nodeids-collection.log`. A module count is evidence for that
module's collection, not a reconstruction of the historical test identity.

| Supplied historical identifier | Old state/reason from collection-diff.md | Preserved snapshot state |
|---|---|---|
| `tests.codex_ml.test_cli_train_config_bridge` | error → skip: mlflow absent | No actual node ID for `tests/codex_ml/test_cli_train_config_bridge.py`; baseline summary line 240507 reports `RecursionError`. Snapshot outcome unknown, not pass. |
| `tests.config.test_override_propagation` | error → skip: Hydra `--override-file` path unavailable with Typer | No actual node ID for `tests/config/test_override_propagation.py`; baseline summary line 240547 reports `RecursionError`. Snapshot outcome unknown, not pass. |
| `tests.monitoring.test_logging_bootstrap_real` | error → skip: mlflow | No actual node ID for `tests/monitoring/test_logging_bootstrap_real.py`; no snapshot outcome established. |
| `tests.peft.test_peft_smoke` | error → skip: PEFT registry unavailable | No actual node ID for `tests/peft/test_peft_smoke.py`; no snapshot outcome established. |
| `tests.phase_5_coverage_cli.utils_modules.test_seed_manager` | error → skip: module not importable | No actual node ID for `tests/phase_5_coverage_cli/utils_modules/test_seed_manager.py`; no snapshot outcome established. |
| `tests.space_traversal.test_peft_comprehensive.test_run_functional_training_resume` | error → skip: numpy | Exact dotted module-path match `tests/space_traversal/test_peft_comprehensive/test_run_functional_training_resume.py`: 3 actual nodes, first at line 16002. This is a module path, not an invented class/function conversion. |
| `tests.test_checkpoint_restore_rng_torch` | error → skip: numpy | `tests/test_checkpoint_restore_rng_torch.py`: 1 actual node, line 20165: `tests/test_checkpoint_restore_rng_torch.py::test_rng_restoration_roundtrip`. |
| `tests.test_checkpoint_roundtrip` | error → skip: numpy | `tests/test_checkpoint_roundtrip.py`: 2 actual nodes, first line 20407: `tests/test_checkpoint_roundtrip.py::test_checkpoint_roundtrip_restores_states[True]`. |
| `tests.test_monitoring_cli` | error → skip: mlflow | No actual node ID for `tests/test_monitoring_cli.py`; do not substitute the distinct `tests/cli/test_monitoring_cli.py`. No snapshot outcome established. |
| `tests.test_peft_adapter` | error → skip: torch stub | `tests/test_peft_adapter.py`: 3 actual nodes, first line 13623: `tests/test_peft_adapter.py::test_apply_lora_task_type_and_control_keys`. |
| `tests.test_peft_integration` | error → skip: peft absent | `tests/test_peft_integration.py`: 1 actual node, line 22512: `tests/test_peft_integration.py::test_peft_apply_lora`. |

Thus 5 supplied names map to modules with actual preserved snapshot nodes;
6 have no matching nodes and remain unknown. No test outcomes or exact
historical parametrizations follow from either count.

## Unknown historical entries: 295 placeholders

**Every label below is a bookkeeping placeholder, NOT an actual test ID.**
Ordering is arbitrary and conveys no association with any test/module/class.
Every row's reason is that the identity list never persisted. No classes,
functions, parameters, deletion claims, skip reasons or passing outcomes are
fabricated for these rows. Their old and current individual states are unknown.

| Placeholder (NOT an actual test ID) | Reason identity/outcome cannot be established |
|---|---|
| Unknown historical ID0001 | identity list never persisted |
| Unknown historical ID0002 | identity list never persisted |
| Unknown historical ID0003 | identity list never persisted |
| Unknown historical ID0004 | identity list never persisted |
| Unknown historical ID0005 | identity list never persisted |
| Unknown historical ID0006 | identity list never persisted |
| Unknown historical ID0007 | identity list never persisted |
| Unknown historical ID0008 | identity list never persisted |
| Unknown historical ID0009 | identity list never persisted |
| Unknown historical ID0010 | identity list never persisted |
| Unknown historical ID0011 | identity list never persisted |
| Unknown historical ID0012 | identity list never persisted |
| Unknown historical ID0013 | identity list never persisted |
| Unknown historical ID0014 | identity list never persisted |
| Unknown historical ID0015 | identity list never persisted |
| Unknown historical ID0016 | identity list never persisted |
| Unknown historical ID0017 | identity list never persisted |
| Unknown historical ID0018 | identity list never persisted |
| Unknown historical ID0019 | identity list never persisted |
| Unknown historical ID0020 | identity list never persisted |
| Unknown historical ID0021 | identity list never persisted |
| Unknown historical ID0022 | identity list never persisted |
| Unknown historical ID0023 | identity list never persisted |
| Unknown historical ID0024 | identity list never persisted |
| Unknown historical ID0025 | identity list never persisted |
| Unknown historical ID0026 | identity list never persisted |
| Unknown historical ID0027 | identity list never persisted |
| Unknown historical ID0028 | identity list never persisted |
| Unknown historical ID0029 | identity list never persisted |
| Unknown historical ID0030 | identity list never persisted |
| Unknown historical ID0031 | identity list never persisted |
| Unknown historical ID0032 | identity list never persisted |
| Unknown historical ID0033 | identity list never persisted |
| Unknown historical ID0034 | identity list never persisted |
| Unknown historical ID0035 | identity list never persisted |
| Unknown historical ID0036 | identity list never persisted |
| Unknown historical ID0037 | identity list never persisted |
| Unknown historical ID0038 | identity list never persisted |
| Unknown historical ID0039 | identity list never persisted |
| Unknown historical ID0040 | identity list never persisted |
| Unknown historical ID0041 | identity list never persisted |
| Unknown historical ID0042 | identity list never persisted |
| Unknown historical ID0043 | identity list never persisted |
| Unknown historical ID0044 | identity list never persisted |
| Unknown historical ID0045 | identity list never persisted |
| Unknown historical ID0046 | identity list never persisted |
| Unknown historical ID0047 | identity list never persisted |
| Unknown historical ID0048 | identity list never persisted |
| Unknown historical ID0049 | identity list never persisted |
| Unknown historical ID0050 | identity list never persisted |
| Unknown historical ID0051 | identity list never persisted |
| Unknown historical ID0052 | identity list never persisted |
| Unknown historical ID0053 | identity list never persisted |
| Unknown historical ID0054 | identity list never persisted |
| Unknown historical ID0055 | identity list never persisted |
| Unknown historical ID0056 | identity list never persisted |
| Unknown historical ID0057 | identity list never persisted |
| Unknown historical ID0058 | identity list never persisted |
| Unknown historical ID0059 | identity list never persisted |
| Unknown historical ID0060 | identity list never persisted |
| Unknown historical ID0061 | identity list never persisted |
| Unknown historical ID0062 | identity list never persisted |
| Unknown historical ID0063 | identity list never persisted |
| Unknown historical ID0064 | identity list never persisted |
| Unknown historical ID0065 | identity list never persisted |
| Unknown historical ID0066 | identity list never persisted |
| Unknown historical ID0067 | identity list never persisted |
| Unknown historical ID0068 | identity list never persisted |
| Unknown historical ID0069 | identity list never persisted |
| Unknown historical ID0070 | identity list never persisted |
| Unknown historical ID0071 | identity list never persisted |
| Unknown historical ID0072 | identity list never persisted |
| Unknown historical ID0073 | identity list never persisted |
| Unknown historical ID0074 | identity list never persisted |
| Unknown historical ID0075 | identity list never persisted |
| Unknown historical ID0076 | identity list never persisted |
| Unknown historical ID0077 | identity list never persisted |
| Unknown historical ID0078 | identity list never persisted |
| Unknown historical ID0079 | identity list never persisted |
| Unknown historical ID0080 | identity list never persisted |
| Unknown historical ID0081 | identity list never persisted |
| Unknown historical ID0082 | identity list never persisted |
| Unknown historical ID0083 | identity list never persisted |
| Unknown historical ID0084 | identity list never persisted |
| Unknown historical ID0085 | identity list never persisted |
| Unknown historical ID0086 | identity list never persisted |
| Unknown historical ID0087 | identity list never persisted |
| Unknown historical ID0088 | identity list never persisted |
| Unknown historical ID0089 | identity list never persisted |
| Unknown historical ID0090 | identity list never persisted |
| Unknown historical ID0091 | identity list never persisted |
| Unknown historical ID0092 | identity list never persisted |
| Unknown historical ID0093 | identity list never persisted |
| Unknown historical ID0094 | identity list never persisted |
| Unknown historical ID0095 | identity list never persisted |
| Unknown historical ID0096 | identity list never persisted |
| Unknown historical ID0097 | identity list never persisted |
| Unknown historical ID0098 | identity list never persisted |
| Unknown historical ID0099 | identity list never persisted |
| Unknown historical ID0100 | identity list never persisted |
| Unknown historical ID0101 | identity list never persisted |
| Unknown historical ID0102 | identity list never persisted |
| Unknown historical ID0103 | identity list never persisted |
| Unknown historical ID0104 | identity list never persisted |
| Unknown historical ID0105 | identity list never persisted |
| Unknown historical ID0106 | identity list never persisted |
| Unknown historical ID0107 | identity list never persisted |
| Unknown historical ID0108 | identity list never persisted |
| Unknown historical ID0109 | identity list never persisted |
| Unknown historical ID0110 | identity list never persisted |
| Unknown historical ID0111 | identity list never persisted |
| Unknown historical ID0112 | identity list never persisted |
| Unknown historical ID0113 | identity list never persisted |
| Unknown historical ID0114 | identity list never persisted |
| Unknown historical ID0115 | identity list never persisted |
| Unknown historical ID0116 | identity list never persisted |
| Unknown historical ID0117 | identity list never persisted |
| Unknown historical ID0118 | identity list never persisted |
| Unknown historical ID0119 | identity list never persisted |
| Unknown historical ID0120 | identity list never persisted |
| Unknown historical ID0121 | identity list never persisted |
| Unknown historical ID0122 | identity list never persisted |
| Unknown historical ID0123 | identity list never persisted |
| Unknown historical ID0124 | identity list never persisted |
| Unknown historical ID0125 | identity list never persisted |
| Unknown historical ID0126 | identity list never persisted |
| Unknown historical ID0127 | identity list never persisted |
| Unknown historical ID0128 | identity list never persisted |
| Unknown historical ID0129 | identity list never persisted |
| Unknown historical ID0130 | identity list never persisted |
| Unknown historical ID0131 | identity list never persisted |
| Unknown historical ID0132 | identity list never persisted |
| Unknown historical ID0133 | identity list never persisted |
| Unknown historical ID0134 | identity list never persisted |
| Unknown historical ID0135 | identity list never persisted |
| Unknown historical ID0136 | identity list never persisted |
| Unknown historical ID0137 | identity list never persisted |
| Unknown historical ID0138 | identity list never persisted |
| Unknown historical ID0139 | identity list never persisted |
| Unknown historical ID0140 | identity list never persisted |
| Unknown historical ID0141 | identity list never persisted |
| Unknown historical ID0142 | identity list never persisted |
| Unknown historical ID0143 | identity list never persisted |
| Unknown historical ID0144 | identity list never persisted |
| Unknown historical ID0145 | identity list never persisted |
| Unknown historical ID0146 | identity list never persisted |
| Unknown historical ID0147 | identity list never persisted |
| Unknown historical ID0148 | identity list never persisted |
| Unknown historical ID0149 | identity list never persisted |
| Unknown historical ID0150 | identity list never persisted |
| Unknown historical ID0151 | identity list never persisted |
| Unknown historical ID0152 | identity list never persisted |
| Unknown historical ID0153 | identity list never persisted |
| Unknown historical ID0154 | identity list never persisted |
| Unknown historical ID0155 | identity list never persisted |
| Unknown historical ID0156 | identity list never persisted |
| Unknown historical ID0157 | identity list never persisted |
| Unknown historical ID0158 | identity list never persisted |
| Unknown historical ID0159 | identity list never persisted |
| Unknown historical ID0160 | identity list never persisted |
| Unknown historical ID0161 | identity list never persisted |
| Unknown historical ID0162 | identity list never persisted |
| Unknown historical ID0163 | identity list never persisted |
| Unknown historical ID0164 | identity list never persisted |
| Unknown historical ID0165 | identity list never persisted |
| Unknown historical ID0166 | identity list never persisted |
| Unknown historical ID0167 | identity list never persisted |
| Unknown historical ID0168 | identity list never persisted |
| Unknown historical ID0169 | identity list never persisted |
| Unknown historical ID0170 | identity list never persisted |
| Unknown historical ID0171 | identity list never persisted |
| Unknown historical ID0172 | identity list never persisted |
| Unknown historical ID0173 | identity list never persisted |
| Unknown historical ID0174 | identity list never persisted |
| Unknown historical ID0175 | identity list never persisted |
| Unknown historical ID0176 | identity list never persisted |
| Unknown historical ID0177 | identity list never persisted |
| Unknown historical ID0178 | identity list never persisted |
| Unknown historical ID0179 | identity list never persisted |
| Unknown historical ID0180 | identity list never persisted |
| Unknown historical ID0181 | identity list never persisted |
| Unknown historical ID0182 | identity list never persisted |
| Unknown historical ID0183 | identity list never persisted |
| Unknown historical ID0184 | identity list never persisted |
| Unknown historical ID0185 | identity list never persisted |
| Unknown historical ID0186 | identity list never persisted |
| Unknown historical ID0187 | identity list never persisted |
| Unknown historical ID0188 | identity list never persisted |
| Unknown historical ID0189 | identity list never persisted |
| Unknown historical ID0190 | identity list never persisted |
| Unknown historical ID0191 | identity list never persisted |
| Unknown historical ID0192 | identity list never persisted |
| Unknown historical ID0193 | identity list never persisted |
| Unknown historical ID0194 | identity list never persisted |
| Unknown historical ID0195 | identity list never persisted |
| Unknown historical ID0196 | identity list never persisted |
| Unknown historical ID0197 | identity list never persisted |
| Unknown historical ID0198 | identity list never persisted |
| Unknown historical ID0199 | identity list never persisted |
| Unknown historical ID0200 | identity list never persisted |
| Unknown historical ID0201 | identity list never persisted |
| Unknown historical ID0202 | identity list never persisted |
| Unknown historical ID0203 | identity list never persisted |
| Unknown historical ID0204 | identity list never persisted |
| Unknown historical ID0205 | identity list never persisted |
| Unknown historical ID0206 | identity list never persisted |
| Unknown historical ID0207 | identity list never persisted |
| Unknown historical ID0208 | identity list never persisted |
| Unknown historical ID0209 | identity list never persisted |
| Unknown historical ID0210 | identity list never persisted |
| Unknown historical ID0211 | identity list never persisted |
| Unknown historical ID0212 | identity list never persisted |
| Unknown historical ID0213 | identity list never persisted |
| Unknown historical ID0214 | identity list never persisted |
| Unknown historical ID0215 | identity list never persisted |
| Unknown historical ID0216 | identity list never persisted |
| Unknown historical ID0217 | identity list never persisted |
| Unknown historical ID0218 | identity list never persisted |
| Unknown historical ID0219 | identity list never persisted |
| Unknown historical ID0220 | identity list never persisted |
| Unknown historical ID0221 | identity list never persisted |
| Unknown historical ID0222 | identity list never persisted |
| Unknown historical ID0223 | identity list never persisted |
| Unknown historical ID0224 | identity list never persisted |
| Unknown historical ID0225 | identity list never persisted |
| Unknown historical ID0226 | identity list never persisted |
| Unknown historical ID0227 | identity list never persisted |
| Unknown historical ID0228 | identity list never persisted |
| Unknown historical ID0229 | identity list never persisted |
| Unknown historical ID0230 | identity list never persisted |
| Unknown historical ID0231 | identity list never persisted |
| Unknown historical ID0232 | identity list never persisted |
| Unknown historical ID0233 | identity list never persisted |
| Unknown historical ID0234 | identity list never persisted |
| Unknown historical ID0235 | identity list never persisted |
| Unknown historical ID0236 | identity list never persisted |
| Unknown historical ID0237 | identity list never persisted |
| Unknown historical ID0238 | identity list never persisted |
| Unknown historical ID0239 | identity list never persisted |
| Unknown historical ID0240 | identity list never persisted |
| Unknown historical ID0241 | identity list never persisted |
| Unknown historical ID0242 | identity list never persisted |
| Unknown historical ID0243 | identity list never persisted |
| Unknown historical ID0244 | identity list never persisted |
| Unknown historical ID0245 | identity list never persisted |
| Unknown historical ID0246 | identity list never persisted |
| Unknown historical ID0247 | identity list never persisted |
| Unknown historical ID0248 | identity list never persisted |
| Unknown historical ID0249 | identity list never persisted |
| Unknown historical ID0250 | identity list never persisted |
| Unknown historical ID0251 | identity list never persisted |
| Unknown historical ID0252 | identity list never persisted |
| Unknown historical ID0253 | identity list never persisted |
| Unknown historical ID0254 | identity list never persisted |
| Unknown historical ID0255 | identity list never persisted |
| Unknown historical ID0256 | identity list never persisted |
| Unknown historical ID0257 | identity list never persisted |
| Unknown historical ID0258 | identity list never persisted |
| Unknown historical ID0259 | identity list never persisted |
| Unknown historical ID0260 | identity list never persisted |
| Unknown historical ID0261 | identity list never persisted |
| Unknown historical ID0262 | identity list never persisted |
| Unknown historical ID0263 | identity list never persisted |
| Unknown historical ID0264 | identity list never persisted |
| Unknown historical ID0265 | identity list never persisted |
| Unknown historical ID0266 | identity list never persisted |
| Unknown historical ID0267 | identity list never persisted |
| Unknown historical ID0268 | identity list never persisted |
| Unknown historical ID0269 | identity list never persisted |
| Unknown historical ID0270 | identity list never persisted |
| Unknown historical ID0271 | identity list never persisted |
| Unknown historical ID0272 | identity list never persisted |
| Unknown historical ID0273 | identity list never persisted |
| Unknown historical ID0274 | identity list never persisted |
| Unknown historical ID0275 | identity list never persisted |
| Unknown historical ID0276 | identity list never persisted |
| Unknown historical ID0277 | identity list never persisted |
| Unknown historical ID0278 | identity list never persisted |
| Unknown historical ID0279 | identity list never persisted |
| Unknown historical ID0280 | identity list never persisted |
| Unknown historical ID0281 | identity list never persisted |
| Unknown historical ID0282 | identity list never persisted |
| Unknown historical ID0283 | identity list never persisted |
| Unknown historical ID0284 | identity list never persisted |
| Unknown historical ID0285 | identity list never persisted |
| Unknown historical ID0286 | identity list never persisted |
| Unknown historical ID0287 | identity list never persisted |
| Unknown historical ID0288 | identity list never persisted |
| Unknown historical ID0289 | identity list never persisted |
| Unknown historical ID0290 | identity list never persisted |
| Unknown historical ID0291 | identity list never persisted |
| Unknown historical ID0292 | identity list never persisted |
| Unknown historical ID0293 | identity list never persisted |
| Unknown historical ID0294 | identity list never persisted |
| Unknown historical ID0295 | identity list never persisted |

## Separate baseline classification and remaining work

`full/base-collection-classification.json` accounts for all **195** baseline
error modules with their raw-log lines and error types: **192 collect on the
historical snapshot**, **0 have deletion/move commit proof**, **0 have observed
snapshot collection errors**, and **3 are unresolved/not reported**. The last
category is intentionally unknown, not a claim that those errors persist or
resolved. The three paths still exist in the recorded snapshot tree; existing
skip/import guards are only possible explanations, not observed skip evidence.

The root parent owns fresh pinned collection, remaining execution shards and
the final report. These historical artifacts do not complete those gates,
establish suite coverage, or validate current HEAD. Recovering an actual old
identity artifact is required to replace the 295 placeholders; without it,
individual identity and disposition remain unknowable from these sources.
