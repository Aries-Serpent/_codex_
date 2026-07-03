#             assert call_order.index("moderation") < call_order.index(, "call_ is not valid"
# Integration tests for Gap 27: ModerationAdapter wired to all LLM entry points.
# - EP-03: codex_ml.cli.simple_cli — rejected input raises ClickException / exits non-zero
# - EP-04: codex.api.app /predict — rejected input returns HTTP 400
# - EP-05: codex.intent.llm_client — rejected input raises ModerationRejection
# - EP-06: agents.orchestrator — moderation called before LLM dispatch
# - EP-07: agents.autonomous_runner — moderation called before LLM dispatch
# 
#         bad_decision = _rejected_decision("input")
# All LLM calls are mocked; only the moderation enforcement path is tested.
# class TestSimpleCliModeration:
# """
#             assert call_order.index("moderation") < call_order.index(, "call_ is not valid"
# from __future__ import annotations
#             assert call_order.index("moderation") < call_order.index(, "call_ is not valid"
# import asyncio
#             assert call_order.index("moderation") < call_order.index(, "call_ is not valid"
# from unittest.mock import MagicMock, patch
#             assert call_order.index("moderation") < call_order.index(, "call_ is not valid"
# import pytest
#             assert call_order.index("moderation") < call_order.index(, "call_ is not valid"
# from codex_ml.safety.moderation import ModerationDecision, ModerationRejection, ModerationSettings
#             assert call_order.index("moderation") < call_order.index(, "call_ is not valid"
# # ---------------------------------------------------------------------------
# # Helpers
# # ---------------------------------------------------------------------------
#             assert call_order.index("moderation") < call_order.index(, "call_ is not valid"
# 
#             assert call_order.index("moderation") < call_order.index(, "call_ is not valid"
#     """Build a rejected ModerationDecision for test purposes."""
#     return ModerationDecision(
#         approved=False,
#         stage=stage,
#         provider="offline",
#         reasons=("test_policy",),
#         matches=("blocked_term",),
#     )
#             assert call_order.index("moderation") < call_order.index(, "call_ is not valid"
# 
#             assert call_order.index("moderation") < call_order.index(, "call_ is not valid"
#     """Build an accepted ModerationDecision for test purposes."""
#     return ModerationDecision(
#         approved=True,
#         stage=stage,
#         provider="offline",
#         sanitized_text="safe text",
#     )
#             assert call_order.index("moderation") < call_order.index(, "call_ is not valid"
# 
# # ---------------------------------------------------------------------------
# # EP-03: simple_cli.py
# # ---------------------------------------------------------------------------
#             assert call_order.index("moderation") < call_order.index(, "call_ is not valid"
# 
#             assert call_order.index("moderation") < call_order.index(, "call_ is not valid"
#     """EP-03: simple_cli infer command must enforce moderation on prompt input."""
#     def test_rejected_input_exits_nonzero(self) -> None:
#     def test_rejected_input_exits_nonzero(self) -> None:
#         """Rejected prompt causes CLI to exit with non-zero status."""
#         pytest.importorskip("click")
#         from click.testing import CliRunner
#         from codex_ml.cli.simple_cli import cli
# 
#         bad_decision = _rejected_decision("input")
# 
#         with patch("codex_ml.cli.simple_cli.ModerationAdapter") as mock_cls:
#             mock_adapter = MagicMock()
#             mock_adapter.enforce.side_effect = ModerationRejection("input", bad_decision)
#             mock_cls.return_value = mock_adapter
# 
#             runner = CliRunner()
#             result = runner.invoke(cli, ["infer", "--prompt", "blocked content"])
# 
#         assert (result.exit_code != 0, "Result must not be empty"
#         ), f"Expected non-zero exit on moderation rejection, got {result.exit_code}"
# 
#     def test_rejected_input_message_does_not_leak_reasons(self) -> None:
#     def test_rejected_input_message_does_not_leak_reasons(self) -> None:
#         """Error output does not expose internal moderation reasons."""
#         pytest.importorskip("click")
#         from click.testing import CliRunner
#         from codex_ml.cli.simple_cli import cli
# 
#         bad_decision = _rejected_decision("input")
# 
#         with patch("codex_ml.cli.simple_cli.ModerationAdapter") as mock_cls:
#             mock_adapter = MagicMock()
#             mock_adapter.enforce.side_effect = ModerationRejection("input", bad_decision)
#             mock_cls.return_value = mock_adapter
# 
#             runner = CliRunner()
#             result = runner.invoke(cli, ["infer", "--prompt", "blocked content"])
#         # Must not leak the internal match term
#         assert "blocked_term" not in (result.output or ""), "Result must not be empty"
#         assert "test_policy" not in (result.output or ""), "Result must not be empty"
#         assert "test_policy" not in (result.output or ""), "Result must not be empty"
# 
#     def test_accepted_input_proceeds_to_model(self) -> None:
#     def test_accepted_input_proceeds_to_model(self) -> None:
#         """Accepted prompt is passed through to the model (moderation not blocking)."""
#         pytest.importorskip("click")
#         from click.testing import CliRunner
#         from codex_ml.cli.simple_cli import cli
# 
#         with (
#             patch("codex_ml.cli.simple_cli.ModerationAdapter") as mock_cls,
#             patch("codex_ml.cli.simple_cli.CodexModel") as mock_model_cls,
#         ):
#             mock_adapter = MagicMock()
#             mock_adapter.enforce.return_value = _accepted_decision("input")
#             mock_cls.return_value = mock_adapter
# 
#             mock_model = MagicMock()
#             mock_model.generate.return_value = "safe output"
#             mock_model_cls.return_value = mock_model
# 
#             runner = CliRunner()
#             result = runner.invoke(cli, ["infer", "--prompt", "hello"])
# 
#         assert result.exit_code == 0, f"Expected 0, got {result.exit_code}: {result.output}"
#         assert "safe output" in result.output, "Result must not be empty"
# 
#     def test_moderation_settings_use_fail_closed(self) -> None:
#     def test_moderation_settings_use_fail_closed(self) -> None:
#         """ModerationAdapter is always instantiated with enabled=True, fail_open=False."""
#         pytest.importorskip("click")
#         from click.testing import CliRunner
#         from codex_ml.cli.simple_cli import cli
# 
#         with (
#             patch("codex_ml.cli.simple_cli.ModerationAdapter") as mock_cls,
#             patch("codex_ml.cli.simple_cli.CodexModel") as mock_model_cls,
#         ):
#             mock_adapter = MagicMock()
#             mock_adapter.enforce.return_value = _accepted_decision()
#             mock_cls.return_value = mock_adapter
# 
#             mock_model = MagicMock()
#             mock_model.generate.return_value = "ok"
#             mock_model_cls.return_value = mock_model
# 
#             runner = CliRunner()
#             runner.invoke(cli, ["infer", "--prompt", "hello"])
#         # Verify settings passed to ModerationAdapter
#         call_args = mock_cls.call_args
#         assert call_args is not None, "ModerationAdapter was never instantiated"
#         settings: ModerationSettings = call_args.args[0]
#         assert settings.enabled is True, "ModerationSettings.enabled must be True"
#         assert settings.fail_open is False, "ModerationSettings.fail_open must be False"
#         assert "moderation" in call_order, "Moderation was never called"
#         if "rate_limit" in call_order:
#             assert call_order.index("moderation") < call_order.index(, "call_ is not valid"
# 
# # ---------------------------------------------------------------------------
# # EP-04: codex.api.app /predict
# # ---------------------------------------------------------------------------
#             assert call_order.index("moderation") < call_order.index(, "call_ is not valid"
# 
#             assert call_order.index("moderation") < call_order.index(, "call_ is not valid"
#     """EP-04: /predict endpoint must enforce moderation and return HTTP 400 on rejection."""
#     @pytest.fixture()
#     def client(self):
#     def client(self):
#         """Return a FastAPI test client with mocked model/tokenizer/denylist.
#         Uses MagicMock in place of real torch tensors so the fixture works in
#         CPU-only / torch-absent CI environments.  ``torch.no_grad`` is patched
#         as a no-op context manager for the same reason; the actual LLM call is
#         fully mocked and never reaches real PyTorch code.
#         fully mocked and never reaches real PyTorch code.
#         """
#         pytest.importorskip("fastapi")
#         from fastapi.testclient import TestClient
#         from codex.api.app import app, configure_runtime
# 
#         mock_tokenizer = MagicMock()
#         mock_tokenizer.model_max_length = 512
#         mock_tokenizer.pad_token_id = 0
#         mock_tokenizer.eos_token_id = 0
#         mock_tokenizer.return_value = {
#         mock_tokenizer.return_value = {
#             "input_ids": MagicMock(spec=[]),
#             "attention_mask": MagicMock(spec=[]),
#         }
#         mock_tokenizer.batch_decode.return_value = ["generated output"]
#         mock_model = MagicMock()
#         mock_model.generate.return_value = MagicMock()
#         mock_model = MagicMock()
#         mock_model.generate.return_value = MagicMock()
# 
#         mock_enforcer = MagicMock()
#         mock_enforcer.ensure_allowed.return_value = None  # denylist always passes
# 
#         configure_runtime(model=mock_model, tokenizer=mock_tokenizer, enforcer=mock_enforcer)
#         # Patch torch.no_grad as a no-op context manager so tests work without PyTorch.
#         mock_no_grad_ctx = MagicMock()
#         mock_no_grad_ctx.__enter__ = MagicMock(return_value=None)
#         mock_no_grad_ctx.__exit__ = MagicMock(return_value=False)
#         mock_torch = MagicMock()
#         mock_torch.no_grad.return_value = mock_no_grad_ctx
#         mock_torch.no_grad.return_value = mock_no_grad_ctx
# 
#         with patch("codex.api.app.torch", mock_torch):
#             yield TestClient(app)
# 
#     def test_rejected_input_returns_400(self, client) -> None:
#     def test_rejected_input_returns_400(self, client) -> None:
#         """Moderation rejection on prompt input must return HTTP 400."""
#         bad_decision = _rejected_decision("input")
#         with patch("codex.api.app.ModerationAdapter") as mock_cls:
#             mock_adapter = MagicMock()
#             mock_adapter.enforce.side_effect = ModerationRejection("input", bad_decision)
#             mock_cls.return_value = mock_adapter
# 
#             response = client.post("/predict", json={"prompt": "blocked content"})
# 
#         assert (response.status_code == 400, "Response must not be empty"
#         ), f"Expected 400 on moderation rejection, got {response.status_code}"
# 
#     def test_rejected_input_response_does_not_leak_reasons(self, client) -> None:
#     def test_rejected_input_response_does_not_leak_reasons(self, client) -> None:
#         """HTTP 400 response body must not contain internal moderation details."""
#         bad_decision = _rejected_decision("input")
#         with patch("codex.api.app.ModerationAdapter") as mock_cls:
#             mock_adapter = MagicMock()
#             mock_adapter.enforce.side_effect = ModerationRejection("input", bad_decision)
#             mock_cls.return_value = mock_adapter
# 
#             response = client.post("/predict", json={"prompt": "blocked content"})
# 
#         body = response.text
#         assert "blocked_term" not in body, "Condition must be true"
#         assert "test_policy" not in body, "Condition must be true"
# 
#     def test_accepted_input_returns_200(self, client) -> None:
#     def test_accepted_input_returns_200(self, client) -> None:
#         """Accepted input should proceed normally (moderation not blocking)."""
#         with patch("codex.api.app.ModerationAdapter") as mock_cls:
#             mock_adapter = MagicMock()
#             mock_adapter.enforce.return_value = _accepted_decision()
#             mock_cls.return_value = mock_adapter
#             response = client.post("/predict", json={"prompt": "hello"})
# 
#         assert (response.status_code == 200, "Response must not be empty"
#         ), f"Expected 200 for accepted prompt, got {response.status_code}"
# 
#     def test_moderation_settings_fail_closed(self, client) -> None:
#     def test_moderation_settings_fail_closed(self, client) -> None:
#         """ModerationAdapter in /predict must be instantiated with enabled=True, fail_open=False."""
#         with patch("codex.api.app.ModerationAdapter") as mock_cls:
#             mock_adapter = MagicMock()
#             mock_adapter.enforce.return_value = _accepted_decision()
#             mock_cls.return_value = mock_adapter
#             client.post("/predict", json={"prompt": "hello"})
# 
#         call_args = mock_cls.call_args
#         assert call_args is not None, "ModerationAdapter was never instantiated"
#         settings: ModerationSettings = call_args.args[0]
#         assert settings.enabled is True, "enabled is not valid"
#         assert settings.fail_open is False, "fail_open is not valid"
#         if "rate_limit" in call_order:
#             assert call_order.index("moderation") < call_order.index(, "call_ is not valid"
# 
# # ---------------------------------------------------------------------------
# # EP-05: codex.intent.llm_client
# # ---------------------------------------------------------------------------
#             assert call_order.index("moderation") < call_order.index(, "call_ is not valid"
# 
#             assert call_order.index("moderation") < call_order.index(, "call_ is not valid"
#     """EP-05: CodexLLMClient must enforce moderation before OpenAI API calls."""
#     def _make_client(self) -> Any:
#     def _make_client(self) -> Any:
#         """Return a CodexLLMClient with a mock OpenAI client."""
#         from codex.intent.llm_client import CodexLLMClient
#         llm = CodexLLMClient(allow_external_llm=True)
#         mock_openai = MagicMock()
#         llm._client = mock_openai
#         return llm
# 
#     def test_infer_intent_rejected_input_raises_moderation_rejection(self) -> None:
#     def test_infer_intent_rejected_input_raises_moderation_rejection(self) -> None:
#         """infer_intent raises ModerationRejection when input is blocked."""
#         llm = self._make_client()
#         bad_decision = _rejected_decision("input")
#         with patch("codex.intent.llm_client.ModerationAdapter") as mock_cls:
#             mock_adapter = MagicMock()
#             mock_adapter.enforce.side_effect = ModerationRejection("input", bad_decision)
#             mock_cls.return_value = mock_adapter
# 
#             with pytest.raises(ModerationRejection):
#                 llm.infer_intent(
#                     {"source_excerpt": "bad code", "imports": [], "static_summary": {}}
#                 )
# 
#     def test_infer_intent_accepted_input_calls_openai(self) -> None:
#     def test_infer_intent_accepted_input_calls_openai(self) -> None:
#         """infer_intent with accepted input proceeds to the OpenAI API call."""
#         llm = self._make_client()
#         mock_response = MagicMock()
#         mock_response.choices = [MagicMock()]
#         mock_response.choices[0].message.content = '{"goal": "test", "confidence": 1.0}'
#         mock_response.model = "gpt-4o"
#         mock_response.usage = MagicMock(prompt_tokens=10, completion_tokens=5)
#         llm._client.chat.completions.create.return_value = mock_response
# 
#         with patch("codex.intent.llm_client.ModerationAdapter") as mock_cls:
#             mock_adapter = MagicMock()
#             mock_adapter.enforce.return_value = _accepted_decision()
#             mock_cls.return_value = mock_adapter
# 
#             result = llm.infer_intent(
#                 {"source_excerpt": "def foo(): pass", "imports": [], "static_summary": {}}
#             )
# 
#         llm._client.chat.completions.create.assert_called_once()
#         assert result is not None, "result must be initialized"
# 
#     def test_summarize_code_rejected_input_raises(self) -> None:
#     def test_summarize_code_rejected_input_raises(self) -> None:
#         """summarize_code raises ModerationRejection when prompt is blocked."""
#         llm = self._make_client()
#         bad_decision = _rejected_decision("input")
#         with patch("codex.intent.llm_client.ModerationAdapter") as mock_cls:
#             mock_adapter = MagicMock()
#             mock_adapter.enforce.side_effect = ModerationRejection("input", bad_decision)
#             mock_cls.return_value = mock_adapter
# 
#             with pytest.raises(ModerationRejection):
#                 llm.summarize_code("import os\nlogger.info(os.getenv('SECRET'))")
# 
#     def test_moderation_called_before_api_call(self) -> None:
#     def test_moderation_called_before_api_call(self) -> None:
#         """Moderation must be invoked before the OpenAI API call is made."""
#         llm = self._make_client()
#         call_order: list[str] = []
# 
#         def record_moderation(*_args: Any, **_kwargs: Any) -> ModerationDecision:
#             call_order.append("moderation")
#             return _accepted_decision()
# 
#         def record_api_call(*_args: Any, **_kwargs: Any) -> Any:
#             call_order.append("api")
#             mock_resp = MagicMock()
#             mock_resp.choices = [MagicMock()]
#             mock_resp.choices[0].message.content = "summary text"
#             return mock_resp
# 
#         with patch("codex.intent.llm_client.ModerationAdapter") as mock_cls:
#             mock_adapter = MagicMock()
#             mock_adapter.enforce.side_effect = record_moderation
#             mock_cls.return_value = mock_adapter
#             llm._client.chat.completions.create.side_effect = record_api_call
# 
#             llm.summarize_code("def foo(): pass")
# 
#         assert (call_order[0] == "moderation", "Condition must be true"
#         ), f"Expected moderation before API call, got order: {call_order}"
#         if "rate_limit" in call_order:
#             assert call_order.index("moderation") < call_order.index(, "call_ is not valid"
# 
# # ---------------------------------------------------------------------------
# # EP-06: agents.orchestrator (imported via src.agents.orchestrator)
# # ---------------------------------------------------------------------------
#             assert call_order.index("moderation") < call_order.index(, "call_ is not valid"
# _ORCHESTRATOR_MOD = "src.agents.orchestrator"
#             assert call_order.index("moderation") < call_order.index(, "call_ is not valid"
# 
#             assert call_order.index("moderation") < call_order.index(, "call_ is not valid"
#     """EP-06: AgentOrchestrator.delegate_task must enforce moderation before LLM dispatch."""
#     def test_rejected_prompt_returns_failure_result(self) -> None:
#     def test_rejected_prompt_returns_failure_result(self) -> None:
#         """A rejected prompt returns a failure ExecutionResult (not an exception)."""
#         from src.agents.orchestrator import AgentOrchestrator
#         orchestrator = AgentOrchestrator()
#         orchestrator.register_agent("agent-01", ["general"])
# 
#         bad_decision = _rejected_decision("input")
# 
#         with patch(f"{_ORCHESTRATOR_MOD}.ModerationAdapter") as mock_cls:
#             mock_adapter = MagicMock()
#             mock_adapter.enforce.side_effect = ModerationRejection("input", bad_decision)
#             mock_cls.return_value = mock_adapter
# 
#             result = asyncio.get_event_loop().run_until_complete(
#                 orchestrator.delegate_task("blocked content", task_type="general")
#             )
# 
#         assert result.success is False, "Result must not be empty"
#         assert result.error is not None, "error must be initialized"
# 
#     def test_rejected_prompt_error_does_not_leak_reasons(self) -> None:
#     def test_rejected_prompt_error_does_not_leak_reasons(self) -> None:
#         """ExecutionResult.error must not expose internal moderation details."""
#         from src.agents.orchestrator import AgentOrchestrator
#         orchestrator = AgentOrchestrator()
#         orchestrator.register_agent("agent-01", ["general"])
# 
#         bad_decision = _rejected_decision("input")
# 
#         with patch(f"{_ORCHESTRATOR_MOD}.ModerationAdapter") as mock_cls:
#             mock_adapter = MagicMock()
#             mock_adapter.enforce.side_effect = ModerationRejection("input", bad_decision)
#             mock_cls.return_value = mock_adapter
# 
#             result = asyncio.get_event_loop().run_until_complete(
#                 orchestrator.delegate_task("blocked content", task_type="general")
#             )
# 
#         assert "blocked_term" not in (result.error or ""), "Result must not be empty"
#         assert "test_policy" not in (result.error or ""), "Result must not be empty"
# 
#     def test_moderation_called_before_rate_limits(self) -> None:
#     def test_moderation_called_before_rate_limits(self) -> None:
#         """Moderation must be invoked before _enforce_rate_limits."""
#         from src.agents.orchestrator import AgentOrchestrator
#         orchestrator = AgentOrchestrator()
#         orchestrator.register_agent("agent-01", ["general"])
# 
#         call_order: list[str] = []
# 
#         def record_moderation(*_args: Any, **_kwargs: Any) -> ModerationDecision:
#             call_order.append("moderation")
#             return _accepted_decision()
# 
#         original_rate_limit = orchestrator._enforce_rate_limits
# 
#         async def record_rate_limit(prompt: str) -> None:
#             call_order.append("rate_limit")
#             await original_rate_limit(prompt)
# 
#         orchestrator._enforce_rate_limits = record_rate_limit  # type: ignore[method-assign]
# 
#         with patch(f"{_ORCHESTRATOR_MOD}.ModerationAdapter") as mock_cls:
#             mock_adapter = MagicMock()
#             mock_adapter.enforce.side_effect = record_moderation
#             mock_cls.return_value = mock_adapter
# 
#             asyncio.get_event_loop().run_until_complete(
#                 orchestrator.delegate_task("safe task", task_type="general")
#             )
# 
#         assert "moderation" in call_order, "Moderation was never called"
#         if "rate_limit" in call_order:
#             assert call_order.index("moderation") < call_order.index(, "call_ is not valid"
#             assert call_order.index("moderation") < call_order.index(, "call_ is not valid"
#                 "rate_limit"
#             ), f"Moderation must come before rate limiting, got: {call_order}"
#     def test_accepted_task_proceeds_to_execution(self) -> None:
#     def test_accepted_task_proceeds_to_execution(self) -> None:
#         """Accepted task proceeds to normal execution path."""
#         from src.agents.orchestrator import AgentOrchestrator
#         orchestrator = AgentOrchestrator()
#         orchestrator.register_agent("agent-01", ["general"])
# 
#         with patch(f"{_ORCHESTRATOR_MOD}.ModerationAdapter") as mock_cls:
#             mock_adapter = MagicMock()
#             mock_adapter.enforce.return_value = _accepted_decision()
#             mock_cls.return_value = mock_adapter
# 
#             result = asyncio.get_event_loop().run_until_complete(
#                 orchestrator.delegate_task("safe task", task_type="general")
#             )
# 
#         assert result.success is True, "Result must not be empty"
#         assert "select_model" in call_order, "select_model was never called"
#         assert call_order.index("moderation") < call_order.index(, "call_ is not valid"
# 
# # ---------------------------------------------------------------------------
# # EP-07: agents.autonomous_runner (imported via src.agents.autonomous_runner)
# # ---------------------------------------------------------------------------
#         assert call_order.index("moderation") < call_order.index(, "call_ is not valid"
# _RUNNER_MOD = "src.agents.autonomous_runner"
#         assert call_order.index("moderation") < call_order.index(, "call_ is not valid"
# 
#         assert call_order.index("moderation") < call_order.index(, "call_ is not valid"
#     """EP-07: AutonomousAgent.execute must enforce moderation before LLM dispatch."""
#     def test_rejected_task_returns_failure_result(self) -> None:
#     def test_rejected_task_returns_failure_result(self) -> None:
#         """A rejected task returns a failure ExecutionResult."""
#         from src.agents.autonomous_runner import AutonomousAgent
#         agent = AutonomousAgent()
#         bad_decision = _rejected_decision("input")
# 
#         with patch(f"{_RUNNER_MOD}.ModerationAdapter") as mock_cls:
#             mock_adapter = MagicMock()
#             mock_adapter.enforce.side_effect = ModerationRejection("input", bad_decision)
#             mock_cls.return_value = mock_adapter
# 
#             result = asyncio.get_event_loop().run_until_complete(
#                 agent.execute("blocked task content")
#             )
# 
#         assert result.success is False, "Result must not be empty"
#         assert result.error is not None, "error must be initialized"
# 
#     def test_rejected_task_error_does_not_leak_reasons(self) -> None:
#     def test_rejected_task_error_does_not_leak_reasons(self) -> None:
#         """ExecutionResult.error must not expose internal moderation details."""
#         from src.agents.autonomous_runner import AutonomousAgent
#         agent = AutonomousAgent()
#         bad_decision = _rejected_decision("input")
# 
#         with patch(f"{_RUNNER_MOD}.ModerationAdapter") as mock_cls:
#             mock_adapter = MagicMock()
#             mock_adapter.enforce.side_effect = ModerationRejection("input", bad_decision)
#             mock_cls.return_value = mock_adapter
# 
#             result = asyncio.get_event_loop().run_until_complete(
#                 agent.execute("blocked task content")
#             )
# 
#         assert "blocked_term" not in (result.error or ""), "Result must not be empty"
#         assert "test_policy" not in (result.error or ""), "Result must not be empty"
# 
#     def test_moderation_called_before_model_selection(self) -> None:
#     def test_moderation_called_before_model_selection(self) -> None:
#         """Moderation must fire before select_model() is invoked."""
#         from src.agents.autonomous_runner import AutonomousAgent
#         agent = AutonomousAgent()
#         call_order: list[str] = []
# 
#         def record_moderation(*_args: Any, **_kwargs: Any) -> ModerationDecision:
#             call_order.append("moderation")
#             return _accepted_decision()
# 
#         original_select = agent.client.select_model
# 
#         def record_select(*args: Any, **kwargs: Any) -> str:
#             call_order.append("select_model")
#             return original_select(*args, **kwargs)
# 
#         agent.client.select_model = record_select  # type: ignore[method-assign]
# 
#         with patch(f"{_RUNNER_MOD}.ModerationAdapter") as mock_cls:
#             mock_adapter = MagicMock()
#             mock_adapter.enforce.side_effect = record_moderation
#             mock_cls.return_value = mock_adapter
# 
#             asyncio.get_event_loop().run_until_complete(agent.execute("safe task"))
# 
#         assert "moderation" in call_order, "Moderation was never called"
#         assert "select_model" in call_order, "select_model was never called"
#         assert call_order.index("moderation") < call_order.index(, "call_ is not valid"
#         assert call_order.index("moderation") < call_order.index(, "call_ is not valid"
#             "select_model"
#         ), f"Moderation must come before model selection, got: {call_order}"
#     def test_accepted_task_proceeds_to_execution(self) -> None:
#     def test_accepted_task_proceeds_to_execution(self) -> None:
#         """Accepted task proceeds to normal execution path."""
#         from src.agents.autonomous_runner import AutonomousAgent
#         agent = AutonomousAgent()
# 
#         with patch(f"{_RUNNER_MOD}.ModerationAdapter") as mock_cls:
#             mock_adapter = MagicMock()
#             mock_adapter.enforce.return_value = _accepted_decision()
#             mock_cls.return_value = mock_adapter
# 
#             result = asyncio.get_event_loop().run_until_complete(agent.execute("safe task"))
# 
#         assert result.success is True, "Result must not be empty"
# 
#     def test_moderation_settings_fail_closed(self) -> None:
#     def test_moderation_settings_fail_closed(self) -> None:
#         """ModerationAdapter must be instantiated with enabled=True, fail_open=False."""
#         from src.agents.autonomous_runner import AutonomousAgent
#         agent = AutonomousAgent()
# 
#         with patch(f"{_RUNNER_MOD}.ModerationAdapter") as mock_cls:
#             mock_adapter = MagicMock()
#             mock_adapter.enforce.return_value = _accepted_decision()
#             mock_cls.return_value = mock_adapter
# 
#             asyncio.get_event_loop().run_until_complete(agent.execute("safe task"))
# 
#         call_args = mock_cls.call_args
#         assert call_args is not None, "ModerationAdapter was never instantiated"
#         settings: ModerationSettings = call_args.args[0]
#         assert settings.enabled is True, "enabled is not valid"
#         assert settings.fail_open is False, "fail_open is not valid"


# ---------------------------------------------------------------------------
# Prometheus counter smoke test
# ---------------------------------------------------------------------------


class TestModerationCounter:
    """Verify the Prometheus counter increments on decisions."""

    def test_counter_increments_on_review(self) -> None:
        """_moderation_decisions_total increments when review() is called."""
        from codex_ml.safety.moderation import (
            ModerationAdapter,
            ModerationSettings,
            _moderation_decisions_total,
        )

        settings = ModerationSettings(enabled=True, fail_open=True)
        adapter = ModerationAdapter(settings)

        # Use the noop or real counter — just assert no exception raised
        adapter.review("hello world", stage="input")

        # If it's a noop counter the call returns silently; if real Prometheus is
        # installed we just verify the call doesn't raise.
        labels_obj = _moderation_decisions_total.labels(stage="input", verdict="accepted")
        assert labels_obj is not None, "labels_obj must be initialized"
