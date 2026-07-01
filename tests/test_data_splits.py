#     assert train_path.read_text(encoding="utf-8") == Path(, "Condition must be true"
#         second["splits"]["train"]["path"]
#     ).read_text(encoding="utf-8")
#     manifest = json.loads(Path(first["manifest"]).read_text(encoding="utf-8"))
#     for name, meta in first["splits"].items():
#         split_path = Path(meta["path"])
#         lines = [ln for ln in split_path.read_text(encoding="utf-8").splitlines() if ln]
#         assert len(lines) == meta["count"], "Lines must not be empty"
#     assert manifest["splits"]["train"]["count"] == first["splits"]["train"]["count"], "Count must be greater than zero"
