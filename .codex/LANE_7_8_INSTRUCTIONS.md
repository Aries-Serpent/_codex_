# Lanes 7-8 Instructions — Build/Deployment + Design Validation

**Trigger**: After Lanes 1-6 report completion

---

## Lane 7: Design & Theme Polish

Execute after Lanes 1-2 (emoji + links) are complete, as those affect rendering.

### 7.1 Navigation Structure Validation
```bash
# Validate mkdocs.yml nav structure
cd /home/runner/work/_codex_/_codex_
python3 << 'PYTHON'
import yaml
with open('mkdocs.yml', 'r') as f:
    config = yaml.safe_load(f)
    nav = config.get('nav', [])
    depth = 0
    for section in nav:
        if isinstance(section, dict):
            for key, value in section.items():
                if isinstance(value, list):
                    print(f"Section: {key} ({len(value)} items)")
                else:
                    print(f"  - {key}")
PYTHON
```

### 7.2 Verify Theme Features
- Search functionality works
- Dark/light mode toggle operational
- Code copy buttons visible
- Breadcrumb navigation working
- Back-to-top button present
- Logo and favicon loading

### 7.3 Consistency Checks
- Heading hierarchy (H1→H6) consistent
- Code block syntax highlighting works
- Table formatting consistent
- Admonition styling (Note, Warning, etc.)

### 7.4 Deliverable
File: `.codex/reports/DESIGN_THEME_REPORT_v0.2.0.md`

---

## Lane 8: Build & Deployment Validation

Execute AFTER Lanes 1-6 complete (depends on all fixes).

### 8.1 Local Build Testing

```bash
cd /home/runner/work/_codex_/_codex_

# Install MkDocs and plugins if not present
pip install mkdocs mkdocs-material pymdown-extensions mermaid2

# Run strict build
mkdocs build --strict

# Check output
ls -lah site/
```

**Expected Results**:
- Zero build errors
- site/ directory created
- All files copied correctly
- No 404 in build log

### 8.2 Build Output Validation

```bash
# Check for broken references in built HTML
cd site/
find . -name "*.html" -exec grep -l "404\|error\|undefined" {} \;

# Check file integrity
find . -type f -name "*.html" | wc -l
find . -type f -name "*.css" | wc -l
find . -type f -name "*.js" | wc -l
```

### 8.3 HTML Quality Checks

```bash
# Sample check of key pages
curl -s file:///home/runner/work/_codex_/_codex_/site/index.html | head -50
```

### 8.4 CI/CD Workflow Validation

**Workflows to validate**:
1. pages-mkdocs.yml (main build)
2. pages-health-guard.yml (health checks)
3. pages-pre-merge-validation.yml (PR checks)

**Checklist**:
- [ ] All workflows have correct permissions
- [ ] All workflows use approved action versions (@v5, @v8, @v6)
- [ ] MkDocs build runs without timeout (60m limit)
- [ ] Artifact upload configured
- [ ] Pages deployment configured

### 8.5 Production Readiness

**Dry-run deployment**:
1. Verify build artifacts generate
2. Check file sizes (should be < 500MB total)
3. Verify no sensitive files in output
4. Performance: page load time estimates

### 8.6 Deliverable
File: `.codex/reports/BUILD_DEPLOYMENT_REPORT_v0.2.0.md`

Include:
- Build success/failure status
- Build time
- Output size
- Warnings/errors encountered
- CI workflow validation results
- Recommended next steps

---

## Lane 9: Final QA Gate (After Lane 8)

### 9.1 Release Readiness Checklist

| # | Component | Target | Pass/Fail |
|----|-----------|--------|-----------|
| 1 | Links | 100% valid | ☐ |
| 2 | Mermaid | 703 render | ☐ |
| 3 | Cognitive App | Functional | ☐ |
| 4 | Reporting Console | Accurate | ☐ |
| 5 | Content | v0.2.0 aligned | ☐ |
| 6 | Theme | Material perfect | ☐ |
| 7 | Build | Zero errors | ☐ |
| 8 | Performance | < 3s load | ☐ |

### 9.2 Production Go/No-Go Decision

**GO DECISION** requires:
- All 8 criteria = PASS
- Zero critical issues
- All reports filed
- Rollback procedure ready

**NO-GO Decision** requires:
- Document blockers
- Create issues for each
- Propose remediation timeline

### 9.3 Final Deliverable
File: `.codex/reports/FINAL_QA_REPORT_v0.2.0.md`

---

## File Storage Requirement

**ALL reports must be stored in**: `/home/runner/work/_codex_/_codex_/.codex/reports/`

**Never use /tmp/** — reports must be preserved in repository.

---

## Timeline

- Lane 7 starts: When Lane 1-2 complete
- Lane 8 starts: When Lane 1-6 complete
- Lane 9 starts: When Lane 8 complete
- Estimated total: 24-36 hours

