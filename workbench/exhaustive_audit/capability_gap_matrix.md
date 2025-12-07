# Capability Gap Matrix (Autonomous, Self-Healing, Self-Managing ML System)

| Domain | Score (0-1) | Current Posture | Critical Gaps / Risks |
| --- | --- | --- | --- |
| Tokenization | 0.45 | Tokenizer CLI and registry present; legacy paths (`tokenization/`) coexist with `src/codex_ml/tokenization`. | No fast tokenizer parity tests; no vocab/version pinning or checksum validation; limited coverage of multilingual/streaming tokenizers; HF/SentencePiece drift detection absent. |
| Modeling | 0.40 | Registry-based model loading with PEFT hooks available. | No automated device/dtype matrix tests; no guardrails for quantization fallbacks; missing model card provenance capture; lacks auto-sharded checkpoint validation. |
| Training Engine | 0.40 | HF trainer wrapper exists with dataclass config. | Distributed (DDP/FSDP) not validated; gradient accumulation/mixed precision edge cases untested; resume logic lacks corruption auto-repair; no automated hyperparameter sweep runner. |
| Configuration | 0.50 | Hydra-style YAML plus dataclass config. | No schema enforcement for many configs; no drift detection against baselines; defaults not coverage-tested; missing config hashing for reproducibility. |
| Evaluation & Metrics | 0.45 | LM Eval and custom metrics registries present. | Metric determinism not enforced; NDJSON/CSV logging not schema-validated; regression suites sparse; offline eval data versioning absent. |
| Logging & Monitoring | 0.35 | JSON logging helpers and optional system metrics flags. | No centralized metrics sink; no alerting; no Prometheus/OTel exporters; log rotation/PII scrubbing missing. |
| Checkpointing & Resume | 0.35 | HF checkpoint manager emits manifests. | RNG/optimizer/scheduler state validation absent; checksum/hash verification missing; best-k retention not enforced; corruption auto-heal not implemented. |
| Data Handling | 0.40 | Basic dataset loaders and registry entries. | No schema validation/Great Expectations integration across pipelines; streaming and shuffling determinism untested; data leakage/imbalance checks absent. |
| Security & Safety | 0.45 | SECURITY.md and bandit config exist. | No secrets baseline enforcement in CI; dependency scanning not wired; prompt safety/sanitization not enforced; supply-chain SBOM/provenance missing. |
| Internal CI/Test | 0.35 | Pytest markers and nox sessions defined. | Coverage gate absent (`pytest -q` only); nox sessions not enforced pre-commit; integration/slow suites optional; deterministic seeding not universal. |
| Deployment | 0.30 | Dockerfiles and docker-compose present. | No reproducible build attestation; no health/readiness probes; no Helm/K8s manifests; no rollout/rollback automation. |
| Documentation | 0.45 | Extensive status docs and guides. | API docs missing; notebooks lack execution validation; README lacks quickstart for autonomy flows; design docs not linked to tests. |
| Experiment Tracking | 0.40 | MLflow hooks referenced. | No offline/airgapped mode tests; artifact retention/versioning gaps; run resumption not validated; cross-run comparison tools absent. |
| Extensibility | 0.45 | Entry-point registries for tokenizers/models/metrics/plugins. | No plugin sandboxing; no compatibility matrix; missing contract tests and ABI/version negotiation; discovery errors not self-healing. |
| Observability | 0.30 | Minimal logging toggles. | No metrics endpoints; no alerts/dashboards; no SLOs; no log-based anomaly detection. |
| Versioning & Releases | 0.35 | Changelogs and version placeholder. | No semantic release automation; release artifacts not signed; changelog generation manual; no compatibility policy. |
| Dependency Management | 0.40 | Segmented requirement files and nox evidence helpers. | No lockfiles enforced for ML extras; outdated dependencies risk CVEs; no automatic upgrade cadence; vendor purge not validated in CI. |
| Error Handling & Recovery | 0.35 | Some retries and CLI validations. | No uniform exception taxonomy; retries/circuit breakers missing; no dead-letter or fallback flows; lack of self-remediation scripts for failed runs. |
