# Codebase Context Digest
**Generated:** 2026-01-07T15:24:53.546749
**Token Budget:** 100,000

## Summary
- **Total Files:** 1057
- **Code Files:** 994
- **Documentation:** 57
- **Configurations:** 6

## Code Structure

### `src/__init__.py`
- **Lines:** 15

### `src/agent/__init__.py`
- **Lines:** 7

### `src/agent/core.py`
- **Lines:** 307
- **Classes:** TaskStatus, AgentConfig, TaskResult, ToolCall, AgentCore

### `src/bridge_manager.py`
- **Lines:** 409
- **Classes:** BridgeMode, ContextMessage, BridgeLock, BridgeManager
- **Functions:** bridge_lock, share_context_with_copilot

### `src/bridge_types.py`
- **Lines:** 291
- **Classes:** MessageType, SourceType, BaseMessage, ContextUpdate, QueryMessage, ResponseMessage, StatusMessage, ErrorMessage, HeartbeatMessage
- **Functions:** create_context_update, create_query, create_response, create_status, create_error, create_heartbeat

### `src/cli.py`
- **Lines:** 269
- **Functions:** _ensure_real_torch, _resolve_callable, _section_to_dict, simple_synthetic_data, classification_accuracy, _instantiate_model, _instantiate_optimizer, _resolve_loss, _resolve_metric, _resolve_dataloaders

### `src/codex_harness/__init__.py`
- **Lines:** 14

### `src/codex_harness/golden_harness_status.py`
- **Lines:** 206
- **Classes:** HarnessSignal
- **Functions:** _utc_now, _normalize_status, _load_json_if_exists, _evaluate_ra_policy, _extract_gate_mapping, _evaluate_honesty, _evaluate_tool_trace, compute_golden_harness_status

### `src/codex_harness/honesty.py`
- **Lines:** 111
- **Classes:** HonestyStatement, HonestyMetadata, HonestyRecorder
- **Functions:** _utc_now

### `src/codex_harness/tool_trace.py`
- **Lines:** 174
- **Classes:** ToolInvocation, ToolTraceLogger
- **Functions:** _utc_now, _normalize_status

### `src/codex_init.py`
- **Lines:** 380
- **Classes:** ConfigLoader
- **Functions:** get_config_loader, load_config, reset_config_loader, detect_config_sprawl, generate_migration_report

### `src/context_management/__init__.py`
- **Lines:** 67

### `src/context_management/budget.py`
- **Lines:** 296
- **Classes:** ContentPriority, TokenBudget, ContentBlock, TokenBudgetEnforcer

### `src/context_management/clustering.py`
- **Lines:** 303
- **Classes:** ClusterMember, SemanticCluster, SemanticClusterer

### `src/context_management/context_cache.py`
- **Lines:** 399
- **Classes:** CacheEntry, CacheStats, ContextCache

### `src/context_management/deduplicator.py`
- **Lines:** 240
- **Classes:** DeduplicationResult, StatementEntry, SemanticDeduplicator

### `src/context_management/fingerprint.py`
- **Lines:** 256
- **Classes:** Fingerprint, StatementFingerprinter

### `src/context_management/guardrails.py`
- **Lines:** 272
- **Classes:** ActionRecord, GuardrailViolation, LoopGuardrail

### `src/context_management/hierarchical_memory.py`
- **Lines:** 454
- **Classes:** MemoryLayer, MemoryItem, MemoryStats, HierarchicalMemory

### `src/context_management/memory.py`
- **Lines:** 498
- **Classes:** MemoryChunk, RetrievalResult, ContextMemory

### `src/context_management/normalizer.py`
- **Lines:** 166
- **Classes:** ContextNormalizer

### `src/context_management/observability.py`
- **Lines:** 370
- **Classes:** MetricType, AlertSeverity, Metric, Alert, LogEntry, ContextObserver

### `src/context_management/priority_queue.py`
- **Lines:** 352
- **Classes:** Priority, PriorityItem, ContextPriorityQueue

### `src/context_management/pruning.py`
- **Lines:** 279
- **Classes:** PruneStrategy, PruneRule, PrunedBlock, PriorityPruner

### `src/context_management/sliding_window.py`
- **Lines:** 340
- **Classes:** WindowStrategy, WindowEntry, WindowState, SlidingWindowManager

### `src/logging_config.py`
- **Lines:** 18
- **Functions:** configure_logging

### `src/logging_utils.py`
- **Lines:** 384
- **Classes:** LoggingConfig, LoggingSession, LogHandles, FallbackMetricsWriter
- **Functions:** _create_tensorboard_writer, init_tensorboard, _start_mlflow_run, _create_fallback_writer, init_mlflow, setup_logging, log_scalar_tb, log_params_mlflow, log_metrics_mlflow, log_metrics

### `src/mcp/__init__.py`
- **Lines:** 31

### `src/mcp/auth.py`
- **Lines:** 93
- **Classes:** Principal, MCPAuthenticator, MCPAuthorizer
- **Functions:** hash_credential

### `src/mcp/config.py`
- **Lines:** 187
- **Classes:** ToolDefinition, MCPConfig
- **Functions:** compute_checksum

### `src/mcp/errors.py`
- **Lines:** 75
- **Classes:** MCPError, ToolNotFound, ValidationError, RateLimitExceeded, Unauthorized
- **Functions:** validate_error_response

### `src/mcp/lifecycle.py`
- **Lines:** 320
- **Classes:** ServerState, InvalidStateTransition, HealthStatus, LifecycleConfig, LifecycleManager
- **Functions:** get_lifecycle_manager, reset_lifecycle_manager

### `src/mcp/observability.py`
- **Lines:** 478
- **Classes:** MetricValue, TraceSpan, MetricsRegistry, Tracer, MCPMetrics
- **Functions:** traced, get_metrics_registry, get_tracer, get_mcp_metrics, reset_observability

### `src/mcp/rate_limit.py`
- **Lines:** 76
- **Classes:** _Bucket, MCPRateLimiter

### `src/mcp/registry.py`
- **Lines:** 106
- **Classes:** ToolDefinition, MCPToolRegistry
- **Functions:** compute_tool_checksum

### `src/mcp/retries.py`
- **Lines:** 35
- **Functions:** retry_on_exception

### `src/mcp/versioning.py`
- **Lines:** 194
- **Functions:** _validate_version_string, _sanitize_version_list, negotiate_version, supports_feature, validate_version

### `src/metrics.py`
- **Lines:** 44
- **Functions:** accuracy, write_ndjson, append_ndjson

### `src/modeling.py`
- **Lines:** 405
- **Classes:** LoraSettings, ModelInitConfig
- **Functions:** _needs_bf16, _assert_bf16_capability, _ensure_torch, _normalise_mapping, _resolve_value, _resolve_dtype, _resolve_device, _coerce_config, load_tokenizer, _is_bf16_dtype

### `src/models/__init__.py`
- **Lines:** 6

### `src/models/chat_model.py`
- **Lines:** 156
- **Classes:** ChatModelConfig, ChatModel
- **Functions:** _resolve_device, _dtype_map, _encoding_to_inputs

### `src/models/peft_utils.py`
- **Lines:** 39
- **Functions:** summarize_peft

### `src/utils/checkpoint.py`
- **Lines:** 397
- **Functions:** _ensure_torch_available, _torch_supports_weights_only, _torch_rng_get_state, _torch_rng_set_state, _legacy_capture_rng_state, _legacy_restore_rng_state, _capture_rng, _restore_rng, _torch_load, save_checkpoint

### `src/utils/error_logging.py`
- **Lines:** 60
- **Functions:** append_error

### `src/utils/log_sanitizer.py`
- **Lines:** 96
- **Functions:** sanitize_log_input, sanitize_dict_for_log

### `src/utils/logging_factory.py`
- **Lines:** 48
- **Functions:** init_logging

### `src/utils/sanitize.py`
- **Lines:** 31
- **Functions:** sanitize_prompt

### `src/utils/sensitive_data.py`
- **Lines:** 172
- **Functions:** mask_token, mask_email, mask_password, hash_for_logging, mask_sensitive_dict

### `src/utils/trackers.py`
- **Lines:** 36
- **Functions:** init_wandb_offline, init_mlflow_local

### `src/workflow_refactor.py`
- **Lines:** 394
- **Classes:** WorkflowRefactorer
- **Functions:** refactor_workflows

... and 944 more code files

## Key Documentation

- `src/README.md`
- `src/cli/README.md`
- `src/codex/README.md`
- `src/codex_plans/Tasks_PR_2459.md`
- `src/codex_plans/batchsetpatchset_segments/batchsetpatchset_part04.txt`
- `src/codex_plans/batchsetpatchset_segments/batchsetpatchset_part06.txt`
- `src/codex_plans/batchsetpatchset_segments/batchsetpatchset_part17.txt`
- `src/codex_plans/batchsetpatchset_segments/batchsetpatchset_part18.txt`
- `src/codex_plans/batchsetpatchset_segments/batchsetpatchset_part23.txt`
- `src/codex_plans/batchsetpatchset_segments/batchsetpatchset_part24.txt`
- `src/codex_plans/track_A.md`
- `src/codex_plans/track_B.md`
- `src/codex_plans/track_C.md`
- `src/codex_plans/track_D.md`
- `src/codex_plans/track_E.md`
- `src/codex_plans/track_F.md`
- `src/codex_plans/track_G.md`
- `src/ingestion/README.md`
- `src/mcp/AGENTS.md`
- `src/mcp/server/README.md`
- ... and 37 more docs

## Configuration Files

- `agents/codex_client/pyproject.toml`
- `agents/config/workflow_config.yaml`
- `src/codex/ingest/sample-manifest.yaml`
- `src/codex/transform/refactor-rules.yaml`
- `src/codex_ml/configs/training/functional_base.yaml`
- `src/codex_ml/safety/default_policy.yaml`

## Module Map

```
src/
├── cognitive_brain/    # Cognitive architecture ABCs
├── bridge_manager.py   # Secure IPC bridge
├── bridge_types.py     # Typed message formats
├── codex_init.py       # Configuration loader
└── workflow_refactor.py # CI/CD utilities

agents/
├── cognitive_adapter.py # Legacy agent adapter
├── agent_memory.py     # Agent memory system
└── [35+ agent modules]

cognitive_app/
└── src/orchestrator.py # OODA Loop orchestrator
```

**Digest Size:** 8715 chars
**Estimated Tokens:** ~2178
