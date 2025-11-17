"""
Add this session snippet into existing noxfile.py.

@nox.session(name="security")
def security(session):
    session.install("pip-audit", "jsonschema")  # jsonschema used elsewhere; harmless here
    import json, subprocess, pathlib, datetime

    allowlist_path = pathlib.Path("security_allowlist.json")
    allowlist = {}
    if allowlist_path.exists():
        allowlist = json.loads(allowlist_path.read_text()).get("allowlisted_vulnerabilities", [])

    cmd = ["pip-audit", "-f", "json"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        session.error(f"pip-audit execution failed: {proc.stderr}")

    try:
        vulns = json.loads(proc.stdout)
    except Exception as e:
        session.error(f"Failed to parse pip-audit JSON: {e}")

    now = datetime.datetime.utcnow().date()
    allow_ids_active = {
        v["id"] for v in allowlist
        if datetime.date.fromisoformat(v["expiry_date"]) >= now
    }

    high_or_critical = []
    for pkg in vulns:
        for vuln in pkg.get("vulns", []):
            sev = vuln.get("severity", "").upper()
            vid = vuln.get("id")
            if vid in allow_ids_active:
                continue
            if sev in {"HIGH", "CRITICAL"}:
                high_or_critical.append((pkg.get("name"), vid, sev))

    artifacts_dir = pathlib.Path("artifacts")
    artifacts_dir.mkdir(exist_ok=True)
    (artifacts_dir / "security_report.json").write_text(json.dumps(vulns, indent=2))

    if high_or_critical:
        details = ", ".join(f"{name}:{vid}:{sev}" for name, vid, sev in high_or_critical)
        session.error(f"High/Critical vulnerabilities found (not allowlisted): {details}")

    session.log("Security scan complete: no high/critical vulnerabilities.")
"""
