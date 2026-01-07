# Guide: Coverage Reporting for Status v1.2
> Generated: 2024-11-02 15:29:01 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Coverage Lead], [Secondary: Reviewer] ⚡ Energy: 5

Goals
- Capture overall and per-module coverage and reflect thresholds in the report.

Commands
- Run tests with coverage:
  - coverage run -m pytest -q
  - coverage json -o .coverage.json
- Extract per-module:
  - python tools/coverage_extract.py --coverage-json .coverage.json --out coverage_modules.json

Report Mapping
- snapshot.tests_gates.coverage_percent: totals.percent_covered
- snapshot.tests_gates.coverage_by_module: contents of coverage_modules.json
- snapshot.tests_gates.coverage_threshold: from .statusrc.json fail_under_coverage
