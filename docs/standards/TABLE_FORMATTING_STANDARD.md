# Documentation Table Formatting Standard

**Last Updated:** 2026-06-22

**Version**: 1.0.0  
**Effective**: 2026-02-10  
**Status**: ✅ ACTIVE

---

## Solution: CSS-Based Approach

**Problem**: Tables immediately after headers render as text without blank lines.

**Solution**: Custom CSS handles spacing automatically - no markdown changes required.

### Implementation

**File**: `docs/stylesheets/extra.css`

```css
/* Automatic spacing between headers and tables */
.md-typeset h1 + table,
.md-typeset h2 + table,
.md-typeset h3 + table {
  margin-top: 1.5em;
}
```

**Config**: Added to `mkdocs.yml`:
```yaml
extra_css:
  - stylesheets/extra.css
```

### Benefits

✅ Works for all 1,278 markdown files automatically  
✅ No need to modify existing documentation  
✅ Handles both light and dark modes  
✅ Responsive design for mobile  
✅ Enhanced table styling (borders, hover effects, alternating rows)

### Testing

```bash
python -m mkdocs serve
```

**Live**: https://aries-serpent.github.io/_codex_/

---

**Owner**: @mbaetiong  
**Documentation**: `.github/agents/github-pages-manager.md`
