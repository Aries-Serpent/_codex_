#         assert not (, "Condition must be true"
#             validation_rules["score"]["min"]
#             <= invalid_record["score"]
#             <= validation_rules["score"]["max"]
#         )
# Template Version: 1.0.0
# Template Version: 1.0.0
# Created: 2026-01-18 (Phase 14.0)
#         """Test handling of nested JSON structures."""
#         nested_file = tmp_path / "nested.jsonl"
#         nested_file.write_text('{"data": {"nested": {"value": 42}}}\n')
#         records = [json.loads(ln) for ln in nested_file.read_text().splitlines() if ln]
#         assert records[0]["data"]["nested"]["value"] == 42, "Data must not be empty"
