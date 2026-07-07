# PHASE 13 TRACK 13.3: CVE SCANNING & DEPENDENCY AUDIT ARCHITECTURE

**Session**: phase-13-track-13-3-deployment  
**Date**: 2026-07-06T05:43:52Z  
**Mode**: ADVISORY (Design & Analysis)  
**Authority**: @mbaetiong (D-tier autonomous)  

---

## EXECUTIVE SUMMARY

This document designs the enterprise-grade CVE scanning and dependency audit system for Phase 13 Track 13.3. The system continuously monitors, classifies, and remediates dependency vulnerabilities across all Python, Rust, and Node.js dependencies.

**Key Design Decisions:**
- **Multi-Source Scanning**: pip-audit + safety + GitHub Advisory DB + Snyk API
- **CVSS-Based Prioritization**: Automated severity scoring with context
- **Intelligent Remediation**: Safe version bumps with compatibility validation
- **Zero-Break Guarantee**: Semantic versioning compliance + comprehensive testing

---

## 1. SYSTEM ARCHITECTURE

### 1.1 Component Overview

```
┌──────────────────────────────────────────────────────────────────┐
│        ENTERPRISE CVE SCANNING & DEPENDENCY AUDIT SYSTEM         │
│                                                                  │
│  ┌────────────────────┐  ┌──────────────────┐  ┌────────────┐   │
│  │ Vulnerability Scan │  │ CVE Scoring      │  │ Remediation│   │
│  │ ────────────────   │  │ & Prioritization │  │ Planning   │   │
│  │                    │  │ ─────────────────│  │ ──────────│   │
│  │ • pip-audit        │→→│ • CVSS scoring   │→→│ • Safe    │   │
│  │ • safety           │  │ • Exploitability │  │   bumps   │   │
│  │ • GitHub Advisory  │  │ • Affected count │  │ • Testing │   │
│  │ • Snyk API         │  │                  │  │ • PR gen  │   │
│  └────────────────────┘  └──────────────────┘  └────────────┘   │
│         ▲                         ▲                     ▼        │
│         │ Requirements            │ Classification     │        │
│         │ Lock files              │                    ▼        │
│         │ SBOMs                   │            ┌──────────────┐ │
│         └─────────────────────────┴────────────│ Verification │ │
│                                                │ & Deployment │ │
│                                                └──────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

### 1.2 Data Flow

```
DEPENDENCY SOURCES          SCANNING              SCORING            REMEDIATION
──────────────────          ────────              ──────             ───────────

requirements*.txt   ┐
pyproject.toml      ├─► [pip-audit]
Cargo.lock          ├─► [safety]       ┐
package-lock.json   ├─► [GitHub Adv.]  ├─► [CVSS Scorer] ──► [Remediation Service]
uv.lock             └─► [Snyk API]     │
                                       └─► [Context Analysis]
```

---

## 2. VULNERABILITY SCANNING LAYER

### 2.1 Multi-Source Scanning Strategy

#### 2.1.1 pip-audit (Python)

**Purpose**: Audit Python packages against known vulnerabilities

**Configuration**:
```toml
# pyproject.toml
[tool.pip-audit]
skip-editable = false
skip = []  # No skipped packages in production
cache-dir = ".cache/pip-audit"
db = "osv"  # Use Open Source Vulnerabilities database
```

**Usage**:
```bash
# Full audit
pip-audit --desc

# JSON output for parsing
pip-audit --format json > dependencies-audit.json

# With requirements mapping
pip-audit --skip-editable --format json
```

**Coverage**:
- PyPI package registry (500K+ packages)
- National Vulnerability Database (NVD)
- GitHub Advisory Database
- OSV (Open Source Vulnerabilities)

#### 2.1.2 safety (Python)

**Purpose**: Checks against Python Vulnerability Database

**Configuration**:
```yaml
# .safety-policy.json
{
  "security": [
    {
      "ignore-cvss-severity-below": 4.0,
      "ignore-cvss-unknown": false,
      "ignore-unpatchable": false,
      "ignore-vulnerable-spec": false
    }
  ]
}
```

**Usage**:
```bash
# Check with policy
safety check --policy .safety-policy.json --json

# Database mode
safety check --db insecure.json
```

**Advantage**: Curated vulnerability DB, good for production packages

#### 2.1.3 GitHub Advisory Database

**Purpose**: Access GitHub's comprehensive vulnerability intelligence

**API Integration**:
```python
class GitHubAdvisoryScanner:
    def __init__(self, token: str):
        self.token = token
        self.api_url = "https://api.github.com/graphql"
    
    async def scan(self, package: str, version: str) -> list[dict]:
        """Query GitHub Advisory DB for vulnerabilities."""
        query = """
        query {
          securityVulnerabilities(
            ecosystem: PIP,
            package: "%s",
            versions: ["%s"],
            first: 100
          ) {
            nodes {
              advisory {
                cveId
                ghsaId
                summary
                description
                severity
                publishedAt
                updatedAt
              }
              vulnerableVersionRange
              firstPatchedVersion {
                identifier
              }
            }
          }
        }
        """ % (package, version)
        
        response = await self._query_api(query)
        return self._parse_vulnerabilities(response)
    
    async def _query_api(self, query: str) -> dict:
        """Execute GraphQL query against GitHub."""
        headers = {
            "Authorization": f"******",
            "Content-Type": "application/json"
        }
        # GraphQL request
        pass
```

#### 2.1.4 Snyk API (Optional)

**Purpose**: Unified vulnerability intelligence across all ecosystems

**Integration**:
```python
class SnykScanner:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.snyk.io/v1"
    
    async def scan_project(self, manifest_file: str) -> dict:
        """Scan project for vulnerabilities."""
        with open(manifest_file) as f:
            manifest_data = f.read()
        
        response = await self._post("/test", {
            "manifest": manifest_data,
            "manifestFileLocation": manifest_file,
            "org": self.org_id
        })
        
        return self._parse_snyk_results(response)
```

### 2.2 Scanning Orchestration

```python
class DependencyVulnerabilityScanner:
    """Orchestrates multi-source vulnerability scanning."""
    
    def __init__(self):
        self.pip_auditor = PipAuditScanner()
        self.safety_checker = SafetyScanner()
        self.github_scanner = GitHubAdvisoryScanner()
        self.snyk_scanner = SnykScanner(os.getenv("SNYK_API_KEY"))
    
    async def scan_all(self) -> dict:
        """Run all scanners and consolidate results."""
        # Run in parallel
        results = await asyncio.gather(
            self._scan_pip_audit(),
            self._scan_safety(),
            self._scan_github_advisory(),
            self._scan_snyk()
        )
        
        # Consolidate findings
        consolidated = self._consolidate_results(*results)
        
        # Deduplicate (same CVE from multiple sources)
        deduplicated = self._deduplicate(consolidated)
        
        return {
            "timestamp": datetime.now(),
            "vulnerabilities": deduplicated,
            "summary": self._generate_summary(deduplicated)
        }
    
    async def _scan_pip_audit(self) -> list[dict]:
        """Run pip-audit scanner."""
        # Implementation
        pass
    
    def _consolidate_results(self, *results) -> list[dict]:
        """Merge results from multiple sources."""
        consolidated = {}
        
        for scanner_results in results:
            for vuln in scanner_results:
                key = (vuln["package"], vuln["affected_version"])
                if key not in consolidated:
                    consolidated[key] = vuln
                else:
                    # Merge severity, sources
                    consolidated[key]["sources"].append(vuln["source"])
                    consolidated[key]["severity"] = max(
                        consolidated[key]["severity"],
                        vuln["severity"]
                    )
        
        return list(consolidated.values())
```

---

## 3. CVE SCORING & PRIORITIZATION LAYER

### 3.1 CVSS-Based Severity Classification

**CVSS v3.1 Severity Ratings**:
```
Score      | Severity    | Action Required
-----------+-------------+------------------
9.0-10.0   | CRITICAL    | Immediate patching
7.0-8.9    | HIGH        | Urgent patching
4.0-6.9    | MEDIUM      | Regular patching
0.1-3.9    | LOW         | Monitor and patch
0.0        | NONE        | No action
```

**CVSS Calculation**:
```python
class CVSSCalculator:
    """Calculate CVSS scores and severity."""
    
    def calculate_severity(self, cve_data: dict) -> dict:
        """Determine severity from CVE data."""
        
        # Primary: CVSS score
        cvss_score = cve_data.get("cvss_score", 0)
        severity = self._score_to_severity(cvss_score)
        
        # Secondary: Exploitability context
        exploit_context = {
            "known_exploit": cve_data.get("known_exploit", False),
            "active_exploitation": cve_data.get("active_in_wild", False),
            "public_poc": cve_data.get("public_poc", False),
            "days_since_disclosure": self._days_since(cve_data.get("published_at"))
        }
        
        # Tertiary: Project context
        project_context = {
            "affected_count": cve_data.get("affected_count", 1),
            "transitive_dep": cve_data.get("is_transitive", False),
            "optional_dep": cve_data.get("is_optional", False)
        }
        
        return {
            "cvss_score": cvss_score,
            "severity": severity,
            "exploit_context": exploit_context,
            "project_context": project_context,
            "recommended_action": self._get_action(severity, exploit_context)
        }
    
    def _score_to_severity(self, score: float) -> str:
        """Map CVSS score to severity."""
        if score >= 9.0:
            return "CRITICAL"
        elif score >= 7.0:
            return "HIGH"
        elif score >= 4.0:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _get_action(self, severity: str, exploit_context: dict) -> str:
        """Recommend action based on severity and context."""
        if severity == "CRITICAL":
            return "IMMEDIATE_PATCH"
        elif severity == "HIGH" and exploit_context["active_exploitation"]:
            return "URGENT_PATCH"
        elif severity == "HIGH":
            return "SCHEDULE_PATCH"
        else:
            return "MONITOR"
```

### 3.2 Risk Prioritization Formula

```
priority_score = (cvss_weight × normalized_cvss +
                  exploit_weight × exploit_likelihood +
                  context_weight × context_severity) / 100

where:
  cvss_weight      = 50    # CVSS score is primary indicator
  exploit_weight   = 30    # Active exploitation increases priority
  context_weight   = 20    # Project context (spread, type)
  
  normalized_cvss: 0-100 (from CVSS 0-10)
  exploit_likelihood: 0-100 based on:
    - Known exploit: +40
    - Active in wild: +30
    - Public PoC: +20
    - Days since disclosure: -2 per day (capped)
  
  context_severity: 0-100 based on:
    - Affected count (packages using this dep): linear 1-100
    - Transitive dep: +5 (harder to fix)
    - Optional dep: -20 (can disable)
```

**Example Prioritization**:

| Package | CVSS | Exploit | Affected | Priority | Action |
|---------|------|---------|----------|----------|--------|
| cryptography | 9.8 | Active | 150 | 95/100 | PATCH NOW |
| jinja2 | 8.0 | PoC | 200 | 78/100 | PATCH THIS WEEK |
| requests | 6.5 | Known | 50 | 55/100 | PATCH NEXT SPRINT |
| idna | 3.2 | None | 10 | 25/100 | MONITOR |

### 3.3 Vulnerability Intelligence Sources

**Data Sources**:
- National Vulnerability Database (NVD): https://nvd.nist.gov
- GitHub Advisory Database: https://github.com/advisories
- OSV (Open Source Vulnerabilities): https://osv.dev
- Python Vulnerability Database: https://www.cvedetails.com
- Snyk Vulnerability Database: https://snyk.io/vuln

**Enrichment Tactics**:
```python
class VulnerabilityEnricher:
    """Enrich vulnerabilities with additional intelligence."""
    
    async def enrich(self, vuln: dict) -> dict:
        """Add exploitation data, patch availability, etc."""
        
        enriched = {
            **vuln,
            "has_fix": await self._check_fix_available(vuln),
            "fix_version": await self._find_fix_version(vuln),
            "known_exploit": await self._check_known_exploit(vuln),
            "real_world_impact": await self._assess_real_world_impact(vuln),
            "patch_difficulty": await self._assess_patch_difficulty(vuln),
            "affected_projects": await self._find_affected_projects(vuln)
        }
        
        return enriched
    
    async def _check_fix_available(self, vuln: dict) -> bool:
        """Check if patch/fix is available."""
        # Query patch repositories, GitHub issues, etc.
        pass
```

---

## 4. REMEDIATION PLANNING LAYER

### 4.1 Safe Version Bump Strategy

**Semantic Versioning Rules**:
```python
class VersionBumpPlanner:
    """Plan safe version bumps for vulnerable packages."""
    
    def plan_fix(self, package: dict, vuln: dict) -> dict:
        """Generate remediation plan for vulnerable dependency."""
        
        current_version = package["version"]
        patch_available = vuln.get("first_patched_version")
        
        if not patch_available:
            return {
                "status": "no_fix",
                "action": "MANUAL_REVIEW",
                "reason": "No patch available yet"
            }
        
        # Check semver compatibility
        target_version = patch_available
        is_major_bump = self._is_major_bump(current_version, target_version)
        is_safe = not is_major_bump or self._is_safe_major_bump(package)
        
        if not is_safe:
            return {
                "status": "incompatible",
                "action": "MANUAL_REVIEW",
                "reason": f"Major version bump required: {current_version} → {target_version}",
                "requires_testing": True,
                "estimated_effort": "HIGH"
            }
        
        return {
            "status": "safe_fix",
            "action": "AUTO_PATCH",
            "current_version": current_version,
            "target_version": target_version,
            "bump_type": self._get_bump_type(current_version, target_version),
            "requires_testing": is_major_bump,
            "estimated_effort": "LOW" if not is_major_bump else "MEDIUM",
            "pr_ready": True
        }
    
    def _is_major_bump(self, current: str, target: str) -> bool:
        """Check if this is a major version bump."""
        from packaging import version
        return version.parse(target).major > version.parse(current).major
    
    def _is_safe_major_bump(self, package: dict) -> bool:
        """Check if package is safe for major version bump."""
        # Consider: API stability, test coverage, usage patterns
        return package.get("has_good_tests", False)
```

### 4.2 Compatibility & Impact Analysis

```python
class CompatibilityAnalyzer:
    """Analyze package compatibility and impact."""
    
    async def analyze_impact(self, package: str, old_version: str, new_version: str) -> dict:
        """Determine if upgrade is compatible."""
        
        analysis = {
            "package": package,
            "upgrade": f"{old_version} → {new_version}",
            "api_changes": await self._detect_api_changes(package, old_version, new_version),
            "breaking_changes": await self._detect_breaking_changes(package, new_version),
            "dependency_conflicts": await self._check_dependency_conflicts(package, new_version),
            "test_coverage": await self._assess_test_coverage(package, new_version),
            "risk_assessment": "LOW" if all([
                not self._has_breaking_changes(breaking_changes),
                not self._has_conflicts(dependency_conflicts),
                self._has_good_coverage(test_coverage)
            ]) else "HIGH"
        }
        
        return analysis
    
    async def _detect_api_changes(self, package: str, old_v: str, new_v: str) -> list[str]:
        """Detect API changes between versions."""
        # Compare package signatures, deprecated functions, etc.
        pass
```

### 4.3 Automated Patch Generation

```python
class PatchGenerator:
    """Generate pull requests with vulnerability fixes."""
    
    async def generate_patch_pr(self, findings: list[dict]) -> dict:
        """Generate PR with all safe patches."""
        
        # Group findings by severity
        critical = [f for f in findings if f["severity"] == "CRITICAL"]
        high = [f for f in findings if f["severity"] == "HIGH"]
        
        # Plan fixes
        fixes = []
        for finding in critical + high:
            plan = await self._plan_fix(finding)
            if plan["action"] == "AUTO_PATCH":
                fixes.append(plan)
        
        if not fixes:
            return {"status": "no_auto_fixes"}
        
        # Generate PR
        pr_body = self._generate_pr_description(fixes)
        updated_reqs = self._update_requirements(fixes)
        
        return {
            "status": "pr_generated",
            "pr_title": f"Security: Fix {len(fixes)} vulnerabilities",
            "pr_body": pr_body,
            "changes": updated_reqs,
            "auto_merge": len(critical) == 0  # Only auto-merge if no critical
        }
    
    def _generate_pr_description(self, fixes: list[dict]) -> str:
        """Generate PR description with vulnerability details."""
        body = "## Security Patches\n\n"
        
        for fix in fixes:
            body += f"### {fix['package']}\n"
            body += f"- **Vulnerability**: {fix['cve_id']}\n"
            body += f"- **Severity**: {fix['severity']}\n"
            body += f"- **CVSS Score**: {fix['cvss_score']}\n"
            body += f"- **Fix**: {fix['current_version']} → {fix['target_version']}\n"
            body += f"- **Status**: {fix['status']}\n\n"
        
        body += "Closes #[vulnerability-tracking-issue]\n"
        return body
```

---

## 5. DEPLOYMENT & MONITORING

### 5.1 Continuous Scanning Schedule

```yaml
# .github/workflows/cve-scanning.yml
name: CVE Scanning & Remediation

on:
  schedule:
    # Scan hourly for critical vulnerabilities
    - cron: "0 * * * *"
  
  # Manual trigger
  workflow_dispatch:

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run CVE scan
        run: |
          python scripts/ci/cve_scanner.py \
            --all-ecosystems \
            --output json > cve-report.json
      
      - name: Generate patches
        run: |
          python scripts/ci/generate_patches.py \
            --report cve-report.json \
            --auto-patch-safe
      
      - name: Submit PRs for fixes
        if: success()
        run: |
          python scripts/ci/submit_security_prs.py \
            --report cve-report.json
```

### 5.2 Vulnerability Tracking

**Vulnerability Tracking Issue**:
```yaml
# Issue template: .github/ISSUE_TEMPLATE/vulnerability.md
---
name: Vulnerability Tracking
about: Track discovered vulnerabilities
title: "VULN: [Package] - [CVE-ID]"
labels: security, cve
---

## Vulnerability Details
- **Package**: 
- **CVE ID**: 
- **CVSS Score**: 
- **Severity**: 
- **Description**: 

## Status
- [ ] Detection confirmed
- [ ] Fix available
- [ ] Patch generated
- [ ] PR submitted
- [ ] Tests passing
- [ ] Deployed to staging
- [ ] Deployed to production
```

### 5.3 Metrics & Reporting

```python
class DependencyMetrics:
    """Track vulnerability metrics over time."""
    
    def generate_dashboard(self) -> dict:
        """Generate vulnerability dashboard."""
        return {
            "date": datetime.now(),
            "total_dependencies": 250,
            "outdated_dependencies": 45,
            "vulnerable_dependencies": 12,
            "critical_vulns": 0,
            "high_vulns": 2,
            "medium_vulns": 8,
            "low_vulns": 15,
            "avg_patch_lag_days": 3.2,
            "patch_success_rate": 98.5,
            "trending": {
                "new_vulns_this_week": 2,
                "patched_this_week": 4,
                "avg_patch_time_days": 2.1
            }
        }
```

---

## 6. INTEGRATION POINTS

### 6.1 Integration with SBOM Generation (Track 13.3)

The CVE scanner feeds vulnerability data to the SBOM generator:

```python
# SBOM enrichment with vulnerability data
for component in sbom.components:
    vulns = cve_scanner.find_vulnerabilities(
        component.name,
        component.version
    )
    component.vulnerabilities = vulns
```

### 6.2 Integration with Compliance Audit (Track 13.3)

CVE status feeds compliance reporting:

```
Compliance Check: "0 unpatched critical/high vulnerabilities"
├─ PASS: 0 critical vulnerabilities
├─ PASS: 0 high vulnerabilities remaining
└─ Status: COMPLIANT with security policy
```

---

## 7. SUCCESS CRITERIA

**For Advisory Phase**:
- ✅ Multi-source scanning architecture designed
- ✅ CVSS scoring formula documented
- ✅ Remediation strategy finalized
- ✅ Integration points mapped

**For Full Execution (Days 5-9)**:
- ✅ 0 unpatched critical vulnerabilities
- ✅ <7 day patch lag for high vulnerabilities
- ✅ 100% safe auto-patch success rate
- ✅ All ecosystem types covered (Python, Rust, Node)
- ✅ Compliance reporting operational

---

## DOCUMENT CONTROL

**Status**: ✅ ADVISORY PHASE COMPLETE  
**Date**: 2026-07-06T05:43:52Z  
**Next Phase**: Full Execution (Days 5-9, pending Track 12.3 clearance)  
**Authority**: @mbaetiong (D-tier autonomous, APPROVED)
