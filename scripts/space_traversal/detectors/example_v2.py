def detect_v2(file_index: dict) -> dict:
    """
    Example detector v2 that returns evidence with ranges and confidence.
    This is a minimal illustrative detector — real detectors should inspect file contents.
    """
    files = [f["path"] for f in file_index.get("files", []) if f.get("path", "").endswith(".py")]
    evidence = []
    for p in files:
        if "serve" in p.lower() or "checkpoint" in p.lower():
            evidence.append({
                "path": p,
                "sha": None,
                "ranges": [{"start_line": 1, "end_line": 40}],
                "confidence": 0.9,
                "excerpt": None
            })
    return {
        "id": "example-evidence-v2",
        "evidence": evidence,
        "found_patterns": ["serve", "checkpoint"],
        "required_patterns": ["serve"],
        "meta": {"detector_version": "v2", "source": "example_v2"}
    }
