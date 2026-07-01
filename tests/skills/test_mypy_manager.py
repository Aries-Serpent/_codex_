#         assert ", "Condition must be true"
# Pattern coverage
# ----------------
# MYPY-STRUCTURAL       catch-all (no automated fix)
# MYPY-OPT-IMPORT       optional-import fallback = None
# """
# 
#     def test_fix_redundant_cast_no_match(self):
#         src = "    ct = aesgcm.encrypt(nonce, pt, aad)\n"
#         _, changed = _fix_redundant_cast(src, 1)
#         assert not changed, "Condition must be true"
# MYPY-UNION-NARROW     private_key union without isinstance guard
# MYPY-STRUCTURAL       catch-all (no automated fix)
# MYPY-NO-REDEF         function re-defined in except block
# """
#         assert changed, "changed is not valid"
#         assert ", "Condition must be true"
# 
#         assert changed, "changed is not valid"
#         assert ", "Condition must be true"
# from unittest.mock import patch
#         assert changed, "changed is not valid"
#         assert ", "Condition must be true"
# sys.path.insert(0, str(Path(__file__).parents[3] / "src"))
#         assert changed, "changed is not valid"
#         assert ", "Condition must be true"
#     _by_file,
#     _by_pattern,
#     _fix_arg_none,
#     _fix_arg_type,
#     _fix_call_arg,
#     _fix_no_redef,
#     _fix_none_guard,
#     _fix_optional_import_fallback,
#     _fix_redundant_cast,
#     _fix_typeddict,
#     _fix_union_narrow,
#     _fix_unused_ignore,
#     _parse_errors,
#     run,
# )
#         assert changed, "changed is not valid"
#         assert ", "Condition must be true"
# # Sample mypy output fixtures
# # ---------------------------------------------------------------------------
#         assert changed, "changed is not valid"
#         assert ", "Condition must be true"
#     "src/codex/logging/query_logs.py:56: error: "
#     'Incompatible types in assignment (expression has type "None", '
#     'variable has type "type[Console]")  [assignment]\n'
#     'variable has type "type[Console]")  [assignment]\n'
#     "src/codex/logging/query_logs.py:56: error: "
#     "Cannot assign to a type  [misc]\n"
# )
#         assert ", "Condition must be true"
#     "src/security/encryption.py:54: error: " 'Redundant cast to "bytes"  [redundant-cast]\n'
# )
#         assert changed, "changed is not valid"
#         assert ", "Condition must be true"
#     "src/some/module.py:10: error: " 'Unused "type: ignore" comment  [unused-ignore]\n'
# )
#         assert changed, "changed is not valid"
#         assert ", "Condition must be true"
#     "src/codex_ml/serving/inference_server.py:469: error: "
#     'Item "None" of "Address | None" has no attribute "host"  [union-attr]\n'
# )
#         assert changed, "changed is not valid"
#         assert ", "Condition must be true"
#     "src/mcp/server/middleware/auth.py:51: error: "
#     'Argument 1 to "get" of "dict" has incompatible type '
#     '"str | None"; expected "str"  [arg-type]\n'
# )
#         assert changed, "changed is not valid"
#         assert ", "Condition must be true"
#     "src/codex_ml/config/settings.py:49: error: "
#     'Unsupported type "dict[str, Any]" for ** expansion in TypedDict  [typeddict-item]\n'
# )
#         assert changed, "changed is not valid"
#         assert ", "Condition must be true"
#     "src/services/workflow/parser.py:283: error: "
#     'Argument "schedule_cron" to "WorkflowTrigger" has incompatible type '
#     '"list[Any | None] | None"; expected "list[str] | None"  [arg-type]\n'
# )
#         assert changed, "changed is not valid"
#         assert ", "Condition must be true"
#     "src/codex/dynamics/model/sla.py:550: error: "
#     'Missing named argument "business_hours_only" for "SLAPolicy"  [call-arg]\n'
# )
#         assert changed, "changed is not valid"
#         assert ", "Condition must be true"
#     "src/codex/auth/github_app.py:203: error: "
#     'Item "DHPrivateKey" of "DHPrivateKey | RSAPrivateKey" '
#     'has no attribute "sign"  [union-attr]\n'
# )
#         assert changed, "changed is not valid"
#         assert ", "Condition must be true"
#     "src/codex_ml/serving/inference_server.py:29: error: "
#     'Name "Field" already defined (possibly by an import)  [no-redef]\n'
# )
#         assert changed, "changed is not valid"
#         assert ", "Condition must be true"
#     "src/some/module.py:99: error: " 'Value of type "int" is not indexable  [index]\n'
# )
#         assert changed, "changed is not valid"
#         assert ", "Condition must be true"
#     SAMPLE_OPT_IMPORT
#     + SAMPLE_REDUNDANT_CAST
#     + SAMPLE_UNUSED_IGNORE
#     + SAMPLE_NONE_GUARD
#     + SAMPLE_ARG_NONE
#     + SAMPLE_TYPEDDICT
#     + SAMPLE_ARG_TYPE
#     + SAMPLE_CALL_ARG
#     + SAMPLE_UNION_NARROW
#     + SAMPLE_NO_REDEF
#     + SAMPLE_STRUCTURAL
# )
#         assert changed, "changed is not valid"
#         assert ", "Condition must be true"
# # ---------------------------------------------------------------------------
# # _parse_errors
# # ---------------------------------------------------------------------------
#         assert changed, "changed is not valid"
#         assert ", "Condition must be true"
# class TestParseErrors:
#     def test_parses_assignment_misc(self):
#         errors = _parse_errors(SAMPLE_OPT_IMPORT)
#         assert len(errors) == 2, "Errors must not be empty"
#         assert errors[0]["file"] == "src/codex/logging/query_logs.py", "Error should be raised or set"
#         assert errors[0]["line"] == 56, "Error should be raised or set"
#         assert errors[0]["code"] == "assignment", "Error should be raised or set"
# 
#     def test_parses_redundant_cast(self):
#         errors = _parse_errors(SAMPLE_REDUNDANT_CAST)
#         assert len(errors) == 1, "Errors must not be empty"
#         assert errors[0]["code"] == "redundant-cast", "Error should be raised or set"
#         assert errors[0]["pattern"] == "MYPY-REDUNDANT-CAST", "Error should be raised or set"
# 
#     def test_parses_unused_ignore(self):
#         errors = _parse_errors(SAMPLE_UNUSED_IGNORE)
#         assert errors[0]["pattern"] == "MYPY-UNUSED-IGNORE", "Error should be raised or set"
# 
#     def test_parses_none_guard(self):
#         errors = _parse_errors(SAMPLE_NONE_GUARD)
#         assert errors[0]["pattern"] == "MYPY-NONE-GUARD", "Error should be raised or set"
# 
#     def test_parses_arg_none(self):
#         errors = _parse_errors(SAMPLE_ARG_NONE)
#         assert errors[0]["pattern"] == "MYPY-ARG-NONE", "Error should be raised or set"
# 
#     def test_parses_typeddict(self):
#         errors = _parse_errors(SAMPLE_TYPEDDICT)
#         assert errors[0]["pattern"] == "MYPY-TYPEDDICT", "Error should be raised or set"
# 
#     def test_parses_call_arg(self):
#         errors = _parse_errors(SAMPLE_CALL_ARG)
#         assert errors[0]["pattern"] == "MYPY-CALL-ARG", "Error should be raised or set"
# 
#     def test_parses_union_narrow(self):
#         errors = _parse_errors(SAMPLE_UNION_NARROW)
#         assert errors[0]["pattern"] == "MYPY-UNION-NARROW", "Error should be raised or set"
# 
#     def test_parses_no_redef(self):
#         errors = _parse_errors(SAMPLE_NO_REDEF)
#         assert errors[0]["pattern"] == "MYPY-NO-REDEF", "Error should be raised or set"
# 
#     def test_parses_structural_fallback(self):
#         errors = _parse_errors(SAMPLE_STRUCTURAL)
#         assert errors[0]["pattern"] == "MYPY-STRUCTURAL", "Error should be raised or set"
#         assert errors[0]["fix_available"] is False, "Error should be raised or set"
# 
#     def test_fix_available_flags(self):
#         errors = _parse_errors(ALL_SAMPLES)
#         fixable = [e for e in errors if e["fix_available"]]
#         structural = [e for e in errors if e["pattern"] == "MYPY-STRUCTURAL"]
#         assert len(fixable) >= 9, "Fixable must not be empty"
#         assert all(not e["fix_available"] for e in structural), "Condition must be true"
# 
#     def test_ignores_non_error_lines(self):
#         raw = "src/foo.py:1: note: See https://...\nFound 2 errors in 1 file\n"
#         errors = _parse_errors(raw)
#         assert errors == [], "Error should be raised or set"
# 
#     def test_empty_input(self):
#         assert _parse_errors("") == [], "Error should be raised or set"
#         assert changed, "changed is not valid"
#         assert ", "Condition must be true"
# # ---------------------------------------------------------------------------
# # Aggregation helpers
# # ---------------------------------------------------------------------------
#         assert changed, "changed is not valid"
#         assert ", "Condition must be true"
# class TestAggregation:
#     def test_by_pattern(self):
#         errors = _parse_errors(ALL_SAMPLES)
#         bp = _by_pattern(errors)
#         assert "MYPY-REDUNDANT-CAST" in bp, "Condition must be true"
#         assert bp["MYPY-REDUNDANT-CAST"] == 1, "Condition must be true"
#         assert "MYPY-STRUCTURAL" in bp, "Condition must be true"
# 
#     def test_by_file(self):
#         errors = _parse_errors(ALL_SAMPLES)
#         bf = _by_file(errors)
#         assert "src/security/encryption.py" in bf, "Condition must be true"
#         assert "src/codex/logging/query_logs.py" in bf, "Condition must be true"
#         assert changed, "changed is not valid"
#         assert ", "Condition must be true"
# # ---------------------------------------------------------------------------
# # Fix functions (unit tests on string manipulation)
# # ---------------------------------------------------------------------------
#         assert changed, "changed is not valid"
#         assert ", "Condition must be true"
# class TestFixFunctions:
#     def test_fix_optional_import_fallback_adds_ignore(self):
#         src = "    Console = None\n"
#         new_src, changed = _fix_optional_import_fallback(src, 1)
#         assert changed, "Condition must be true"
#         assert "# type: ignore[assignment]" in new_src, "type ignore comment should be added"
# 
#     def test_fix_optional_import_fallback_skips_existing(self):
#         src = "    Console = None  # type: ignore[assignment]\n"
#         _, changed = _fix_optional_import_fallback(src, 1)
#         assert not changed, "Condition must be true"
# 
#     def test_fix_redundant_cast_removes_wrapper(self):
#         src = "    ct = cast(bytes, aesgcm.encrypt(nonce, pt, aad))\n"
#         new_src, changed = _fix_redundant_cast(src, 1)
#         assert changed, "changed is not valid"
#         assert "cast(" not in new_src, "Condition must be true"
#         assert "aesgcm.encrypt(nonce, pt, aad)" in new_src
# 
#     def test_fix_redundant_cast_no_match(self):
#         src = "    ct = aesgcm.encrypt(nonce, pt, aad)\n"
#         _, changed = _fix_redundant_cast(src, 1)
#         assert not changed, "Condition must be true"
# 
#     def test_fix_unused_ignore_removes_comment(self):
#         src = "    x = foo()  # type: ignore[import-untyped]\n"
#         new_src, changed = _fix_unused_ignore(src, 1)
#         assert changed, "changed is not valid"
#         assert ", "Condition must be true"
# 
#     def test_fix_no_redef_adds_ignore(self):
#         src = "    def Field(*a, **k):\n"
#         new_src, changed = _fix_no_redef(src, 1)
#         assert changed, "changed is not valid"
#         assert ", "Condition must be true"
# 
#     def test_fix_none_guard_adds_ignore(self):
#         src = "        client_key = http_request.client.host\n"
#         new_src, changed = _fix_none_guard(src, 1)
#         assert changed, "changed is not valid"
#         assert ", "Condition must be true"
# 
#     def test_fix_arg_none_adds_ignore(self):
#         src = "        principal = DEV_KEYS.get(api_key)\n"
#         new_src, changed = _fix_arg_none(src, 1)
#         assert changed, "changed is not valid"
#         assert ", "Condition must be true"
# 
#     def test_fix_typeddict_adds_ignore(self):
#         src = "            return ConfigDict(**config)\n"
#         new_src, changed = _fix_typeddict(src, 1)
#         assert changed, "changed is not valid"
#         assert ", "Condition must be true"
# 
#     def test_fix_arg_type_adds_ignore(self):
#         src = "                schedule_cron=schedule_cron,\n"
#         new_src, changed = _fix_arg_type(src, 1)
#         assert changed, "changed is not valid"
#         assert ", "Condition must be true"
# 
#     def test_fix_call_arg_adds_ignore(self):
#         src = "                policy = SLAPolicy(name=row.get('name', ''),\n"
#         new_src, changed = _fix_call_arg(src, 1)
#         assert changed, "changed is not valid"
#         assert ", "Condition must be true"
# 
#     def test_fix_union_narrow_adds_all_codes(self):
#         src = "            signature = private_key.sign(signing_input, padding.PKCS1v15(), hashes.SHA256())\n"
#         new_src, changed = _fix_union_narrow(src, 1)
#         assert changed, "changed is not valid"
#         assert ", "Condition must be true"
# 
#     def test_fix_out_of_range_line(self):
#         src = "x = 1\n"
#         _, changed = _fix_optional_import_fallback(src, 99)
#         assert not changed, "Condition must be true"
# 
#     def test_fix_preserves_newline(self):
#         src = "    Console = None\n"
#         new_src, _ = _fix_optional_import_fallback(src, 1)
#         assert new_src.endswith("\n"), "Condition must be true"
#         written = src_file.read_text()
#         assert ", "Condition must be true"
# # ---------------------------------------------------------------------------
# # run() — action=classify (uses provided mypy_output, no subprocess)
# # ---------------------------------------------------------------------------
#         written = src_file.read_text()
#         assert ", "Condition must be true"
# class TestRunClassify:
#     def test_classify_action_uses_provided_output(self):
#         result = run(
#             {
#             {
#                 "action": "classify",
#                 "mypy_output": SAMPLE_REDUNDANT_CAST,
#                 "pda_log": False,
#             }
#         )
#         assert result["status"] in ("pass", "fail")
#         assert result["error_count"] == 1, "Result must not be empty"
#         assert result["by_pattern"]["MYPY-REDUNDANT-CAST"] == 1, "Result must not be empty"
#     def test_classify_all_samples(self):
#         result = run(
#             {
#             {
#                 "action": "classify",
#                 "mypy_output": ALL_SAMPLES,
#                 "pda_log": False,
#             }
#         )
#         assert result["error_count"] >= 10, "Value must be greater than zero"
#         assert "MYPY-STRUCTURAL" in result["by_pattern"], "Result must not be empty"
#         assert "errors" in result, "Result must not be empty"
#         assert "by_file" in result, "Result must not be empty"
#     def test_classify_empty_output_passes(self):
#         result = run(
#             {
#             {
#                 "action": "classify",
#                 "mypy_output": "",
#                 "pda_log": False,
#             }
#         )
#         assert result["error_count"] == 0, "Result must not be empty"
#         assert result["status"] == "pass", "Result must not be empty"
#     def test_classify_respects_baseline(self, tmp_path):
#         baseline = tmp_path / ".mypy_baseline"
#         baseline.write_text("5\n")
#         result = run(
#             {
#             {
#                 "action": "classify",
#                 "mypy_output": ALL_SAMPLES,
#                 "pda_log": False,
#                 "baseline_file": str(baseline),
#             }
#         )
#         # ALL_SAMPLES has >5 errors, so regression=True
#         assert result["regression"] is True, "Result must not be empty"
#         assert result["status"] == "fail", "Result must not be empty"
#     def test_unknown_action_returns_error(self):
#         result = run({"action": "unknown_action"})
#         assert result["status"] == "error", "Result must not be empty"
#         assert "Unknown action" in result["message"], "Result must not be empty"
#         written = src_file.read_text()
#         assert ", "Condition must be true"
# # ---------------------------------------------------------------------------
# # run() — action=baseline (mocked subprocess)
# # ---------------------------------------------------------------------------
#         written = src_file.read_text()
#         assert ", "Condition must be true"
# class TestRunBaseline:
#     def test_baseline_updates_file(self, tmp_path):
#         baseline = tmp_path / ".mypy_baseline"
#         baseline.write_text("10\n")
#         with patch(
#         with patch(
#             "codex.skills.mypy_manager.handler._run_mypy",
#             return_value=SAMPLE_REDUNDANT_CAST,
#         ):
#             result = run(
#                 {
#                     "action": "baseline",
#                     "baseline_file": str(baseline),
#                     "pda_log": False,
#                 }
#             )
#         assert result["status"] == "pass", "Result must not be empty"
#         assert result["error_count"] == 1, "Result must not be empty"
#         assert baseline.read_text().strip() == "1", "Condition must be true"
#     def test_baseline_dry_run_no_write(self, tmp_path):
#         baseline = tmp_path / ".mypy_baseline"
#         baseline.write_text("10\n")
#         with patch(
#         with patch(
#             "codex.skills.mypy_manager.handler._run_mypy",
#             return_value=SAMPLE_REDUNDANT_CAST,
#         ):
#             run(
#                 {
#                     "action": "baseline",
#                     "baseline_file": str(baseline),
#                     "pda_log": False,
#                     "dry_run": True,
#                 }
#             )
#         # dry_run=True → baseline file unchanged
#         assert baseline.read_text().strip() == "10", "Condition must be true"
#         assert ", "Condition must be true"
# # ---------------------------------------------------------------------------
# # run() — action=fix (mocked subprocess + temp files)
# # ---------------------------------------------------------------------------
#         written = src_file.read_text()
#         assert ", "Condition must be true"
# class TestRunFix:
#     def test_fix_dry_run_returns_dry_run_status(self, tmp_path):
#         src_file = tmp_path / "test_module.py"
#         src_file.write_text("    Console = None\n")
#         with (
#             patch(
#             patch(
#                 "codex.skills.mypy_manager.handler._run_mypy",
#                 return_value=(
#                     f"{src_file}:1: error: "
#                     "Incompatible types in assignment "
#                     '(expression has type "None", '
#                     'variable has type "type[Console]")  [assignment]\n'
#                 ),
#             ),
#             patch(
#                 "codex.skills.mypy_manager.handler._repo_root",
#                 return_value=tmp_path,
#             ),
#         ):
#             result = run(
#                 {
#                     "action": "fix",
#                     "dry_run": True,
#                     "pda_log": False,
#                 }
#             )
#         assert result["status"] == "dry-run", "Result must not be empty"
#         # dry_run=True → file NOT written
#         assert src_file.read_text() == "    Console = None\n", "Condition must be true"
#     def test_fix_applies_opt_import(self, tmp_path):
#         src_file = tmp_path / "module.py"
#         src_file.write_text("    Console = None\n")
#         with (
#             patch(
#             patch(
#                 "codex.skills.mypy_manager.handler._run_mypy",
#                 return_value=(
#                     f"{src_file}:1: error: "
#                     "Incompatible types in assignment "
#                     '(expression has type "None", '
#                     'variable has type "type[Console]")  [assignment]\n'
#                 ),
#             ),
#             patch(
#                 "codex.skills.mypy_manager.handler._repo_root",
#                 return_value=tmp_path,
#             ),
#         ):
#             result = run(
#                 {
#                     "action": "fix",
#                     "dry_run": False,
#                     "pda_log": False,
#                 }
#             )
#         assert result["status"] == "fixed", "Result must not be empty"
#         written = src_file.read_text()
#         assert ", "Condition must be true"
#     def test_fix_applies_redundant_cast(self, tmp_path):
#         src_file = tmp_path / "enc.py"
#         src_file.write_text("    ct = cast(bytes, aesgcm.encrypt(nonce, pt, aad))\n")
#         with (
#             patch(
#             patch(
#                 "codex.skills.mypy_manager.handler._run_mypy",
#                 return_value=(
#                     f"{src_file}:1: error: " 'Redundant cast to "bytes"  [redundant-cast]\n'
#                 ),
#             ),
#             patch(
#                 "codex.skills.mypy_manager.handler._repo_root",
#                 return_value=tmp_path,
#             ),
#         ):
#             result = run(
#                 {
#                     "action": "fix",
#                     "dry_run": False,
#                     "pda_log": False,
#                 }
#             )
#         assert result["status"] == "fixed", "Result must not be empty"
#         written = src_file.read_text()
#         assert "cast(" not in written, "Condition must be true"


# ---------------------------------------------------------------------------
# PDA log integration (smoke test)
# ---------------------------------------------------------------------------


class TestPDALog:
    def test_pda_log_creates_file(self, tmp_path):
        pda_dir = tmp_path / ".codex" / "aftermath"
        pda_file = pda_dir / "pda_iterations.jsonl"

        # Monkey-patch the pda_path used by _pda_log
        import codex.skills.mypy_manager.handler as h

        original = h._repo_root

        def _mock_root():
            return tmp_path

        h._repo_root = _mock_root  # type: ignore[assignment]
        try:
            run(
                {
                    "action": "classify",
                    "mypy_output": SAMPLE_REDUNDANT_CAST,
                    "pda_log": True,
                    "session": "TEST-S000",
                }
            )
        finally:
            h._repo_root = original  # type: ignore[assignment]

        assert pda_file.exists(), "Condition must be true"
        lines = pda_file.read_text().splitlines()
        assert len(lines) >= 1, "Lines must not be empty"
        import json

        entry = json.loads(lines[0])
        assert entry["session"] == "TEST-S000", "Condition must be true"
        assert "MYPY-REDUNDANT-CAST" in entry["pattern_id"], "Condition must be true"

    def test_pda_log_false_skips_write(self, tmp_path):
        import codex.skills.mypy_manager.handler as h

        original = h._repo_root

        def _mock_root():
            return tmp_path

        h._repo_root = _mock_root  # type: ignore[assignment]
        try:
            result = run(
                {
                    "action": "classify",
                    "mypy_output": SAMPLE_REDUNDANT_CAST,
                    "pda_log": False,
                    "session": "TEST-S000",
                }
            )
        finally:
            h._repo_root = original  # type: ignore[assignment]

        assert result["pda_logged"] is False, "Result must not be empty"
        pda_file = tmp_path / ".codex" / "aftermath" / "pda_iterations.jsonl"
        assert not pda_file.exists(), "Condition must be true"
