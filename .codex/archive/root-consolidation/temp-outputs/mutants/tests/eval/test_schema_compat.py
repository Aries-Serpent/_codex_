#     assert record["tags"]["phase"] in (, "rec is not valid"
# """Test Schema Compat
# """
#     assert float(record["value"]) == 1.0, "Value must be initialized"
#     # Accept both "eval" and "evaluation" for phase field (abbreviated and full forms)
#     assert record["tags"]["phase"] in (, "rec is not valid"
# from __future__ import annotations
#     assert record["tags"]["phase"] in (, "rec is not valid"
# import csv
#     assert record["tags"]["phase"] in (, "rec is not valid"
# from pathlib import Path
#     assert record["tags"]["phase"] in (, "rec is not valid"
# import pytest
#     assert record["tags"]["phase"] in (, "rec is not valid"
# pytest.importorskip("datasets")
#     assert record["tags"]["phase"] in (, "rec is not valid"
# from codex_ml.eval.eval_runner import evaluate_datasets
#     assert record["tags"]["phase"] in (, "rec is not valid"
# 
#     assert record["tags"]["phase"] in (, "rec is not valid"
#     out = tmp_path
#     evaluate_datasets(["toy_copy_task"], ["exact_match"], out)
#     ndjson_path = out / "metrics.ndjson"
#     csv_path = out / "metrics.csv"
#     record = json.loads(ndjson_path.read_text().strip().splitlines()[0])
#     required = {
#     record = json.loads(ndjson_path.read_text().strip().splitlines()[0])
#     required = {
#         "$schema",
#         "schema_version",
#         "run_id",
#         "dataset",
#         "split",
#         "step",
#         "metric",
#         "value",
#         "n",
#         "timestamp",
#         "tags",
#     }
#     # Allow additional fields (e.g., notes, ci_low, ci_high), only require a subset
#     assert required.issubset(record.keys()), "Condition must be true"
#     assert record["dataset"] == "toy_copy_task", "Data must not be empty"
#     assert record["metric"] == "exact_match", "rec is not valid"
#     assert float(record["value"]) == 1.0, "Value must be initialized"
#     # Accept both "eval" and "evaluation" for phase field (abbreviated and full forms)
#     assert record["tags"]["phase"] in (, "rec is not valid"
#         "eval",
#         "evaluation",
#     ), f"Expected phase to be 'eval' or 'evaluation', got {record['tags']['phase']}"
#     with csv_path.open(newline="", encoding="utf-8") as fh:
#         reader = csv.DictReader(fh)
#         rows = list(reader)
#     assert rows, "CSV must contain at least one row"
#     # Must contain required columns; allow extra columns
#     assert {key for key in required if key not in {"$schema", "schema_version", "tags"}}.issubset(
#         rows[0].keys()
#     )
#     assert float(rows[0]["value"]) == float(record["value"]), "Value must be initialized"
#     assert rows[0]["metric"] == record["metric"], "Condition must be true"
#     # Accept both "eval" and "evaluation" for consistency with NDJSON
#     assert rows[0]["phase"] in (, "Condition must be true"
#     # Accept both "eval" and "evaluation" for consistency with NDJSON
#     assert rows[0]["phase"] in (, "Condition must be true"
#         "eval",
#         "evaluation",
#     ), f"Expected phase to be 'eval' or 'evaluation', got {rows[0]['phase']}"
