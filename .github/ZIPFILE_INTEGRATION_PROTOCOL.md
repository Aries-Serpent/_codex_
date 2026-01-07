# ZIP File Integration Protocol for GitHub Copilot Agent

**Version:** 1.0  
**Date:** 2026-01-06  
**Purpose:** Standardized protocol for handling external ZIP files and resource integration

---

## Critical Learning: Check Before Claiming Limitations

### ❌ Don't Say:
> "I cannot directly download files from external URLs. The zip file needs to be present in the repository..."

### ✅ Do This Instead:
1. **FIRST**: Extract filename from the provided URL/link
2. **SECOND**: Search the repository for that filename
3. **THIRD**: Check common locations (misc/, docs/, tmp/, root)
4. **FOURTH**: Only if file is NOT found, then explain the limitation

**Example Workflow:**
```bash
# User provides: https://github.com/user/repo/releases/download/v1.0.0/cognitivecodex-main.zip
# Extract filename: cognitivecodex-main.zip

# Step 1: Search repository
find . -name "cognitivecodex-main.zip" -type f 2>/dev/null

# Step 2: Check common locations
ls -la misc/*.zip
ls -la docs/**/*.zip
ls -la *.zip

# Step 3: If found, proceed immediately
# Step 4: If not found, provide clear guidance
```

---

## Protocol for ZIP File Integration

### Phase 1: Discovery & Validation

#### 1.1 File Location Discovery
```bash
# When user mentions a ZIP file, immediately check:
FILENAME=$(basename "URL_PROVIDED_BY_USER")

# Search entire repository
find . -name "$FILENAME" -type f 2>/dev/null

# Common ZIP locations in _codex_ repository:
# - misc/ (miscellaneous resources)
# - docs/plans/ (implementation plans)
# - cognitive_app/ (app-specific resources)
# - Root directory (temporary or major resources)
```

#### 1.2 Extraction Strategy
```bash
# Create isolated extraction directory with timestamp
EXTRACTION_DIR="/tmp/extraction-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$EXTRACTION_DIR"
cd "$EXTRACTION_DIR"

# Extract and verify
unzip -q /path/to/zipfile.zip
ls -laR  # List all extracted contents

# Document structure
tree -L 3 > structure.txt
```

#### 1.3 Content Analysis
```bash
# Count files by type
find . -type f -name "*.ts" -o -name "*.tsx" | wc -l  # TypeScript
find . -type f -name "*.md" | wc -l                    # Documentation
find . -type f -name "*.json" | wc -l                  # Configuration

# Identify key directories
ls -ld src/ docs/ components/ lib/ 2>/dev/null

# Check for README or integration guide
cat README.md 2>/dev/null || cat INTEGRATION.md 2>/dev/null
```

### Phase 2: Integration Analysis

#### 2.1 Naming Convention Check
```bash
# Search for naming patterns that need alignment
grep -r "codex" . --include="*.ts" --include="*.tsx" | grep -v "_codex_" | head -20

# Common patterns to check:
# - API URLs: /api/codex → /api/_codex_
# - Component names: CodexAPI → Codex_API or keep as is
# - Import paths: from '@/codex/...' → from '@/_codex_/...'
# - Environment variables: VITE_CODEX → VITE_CODEX (usually OK as is)
```

#### 2.2 Conflict Detection
```bash
# Identify files that exist in both source and target
TARGET_DIR="/home/runner/work/_codex_/_codex_/cognitive_app"
SOURCE_DIR="$EXTRACTION_DIR/cognitivecodex-main"  # Use the variable from extraction step

# Compare directory structures
diff -rq "$SOURCE_DIR/src" "$TARGET_DIR/src" 2>/dev/null | grep "Only in"

# List duplicate filenames
find "$SOURCE_DIR" -name "*.tsx" -exec basename {} \; | sort > source_files.txt
find "$TARGET_DIR" -name "*.tsx" -exec basename {} \; | sort > target_files.txt
comm -12 source_files.txt target_files.txt  # Files in both
```

#### 2.3 Dependency Analysis
```bash
# Extract dependencies from source package.json
jq '.dependencies, .devDependencies' "$SOURCE_DIR/package.json" > source_deps.json

# Compare with existing dependencies
jq '.dependencies, .devDependencies' "$TARGET_DIR/package.json" > target_deps.json

# Identify new dependencies needed
jq -s '.[0] * .[1]' source_deps.json target_deps.json
```

### Phase 3: Selective Integration Strategy

#### 3.1 Prioritization Matrix

**Priority 1 - Safe to Merge (No Conflicts):**
- New UI components not in target
- New utility functions
- New documentation
- New test files for new components

**Priority 2 - Requires Review (Potential Conflicts):**
- Components with same name but different implementation
- Configuration files (merge carefully)
- Shared utilities (compare implementation)

**Priority 3 - Critical Protection (Never Override):**
- Files with 100% test pass rate (e.g., CodeGenerator.tsx)
- Core API clients with tests
- Existing test infrastructure
- Production configuration with secrets

#### 3.2 Merge Strategy Per File Type

**UI Components (*.tsx in src/components/):**
```bash
# For new components: Copy directly
cp "$SOURCE_DIR/src/components/ui/new-component.tsx" \
   "$TARGET_DIR/src/components/ui/"

# For conflicting components: Rename or review
# Example: If both have Button.tsx
# - Keep existing if it's tested and working
# - Add new as Button.v2.tsx or merge manually
# - Document differences in integration report
```

**Configuration Files:**
```bash
# Never direct copy - always merge
# 1. tailwind.config.js: Merge theme extensions
# 2. vite.config.ts: Merge plugins and aliases
# 3. package.json: Merge dependencies (with version conflict resolution)

# Use JSON merge for package.json
jq -s '.[0] * .[1]' target_package.json source_package.json > merged_package.json
```

**Documentation:**
```bash
# Copy non-conflicting docs to docs/ or reports/
cp "$SOURCE_DIR/INTEGRATION_GUIDE.md" \
   "$TARGET_DIR/docs/cognitive_brain_integration.md"

# For README: Create separate section or new file
cat "$SOURCE_DIR/README.md" >> "$TARGET_DIR/docs/COGNITIVE_CODEX_README.md"
```

### Phase 4: Validation & Testing

#### 4.1 Post-Merge Validation Checklist

```bash
# Run after each significant merge step

# 1. TypeScript Compilation
cd "$TARGET_DIR"
npm run type-check  # Should complete without errors

# 2. Unit Tests
npm test  # Should maintain 100% pass rate (14/14)

# 3. Build Process
npm run build  # Should complete without errors

# 4. Lint Checks
npm run lint  # Should pass or show only new file issues

# 5. Import Resolution
# Check for broken imports in merged files
grep -r "from.*components/ui/" src/ --include="*.tsx" | grep -v "node_modules"
```

#### 4.2 Integration Report Template

Create a report after each major integration step:

```markdown
# Integration Report: [Component/Feature Name]

**Date:** YYYY-MM-DD  
**Source:** cognitivecodex-main.zip  
**Phase:** [Phase Number]  

## Files Added
- List of new files with line counts

## Files Modified
- List of modified files with change summary

## Dependencies Added
- Package name: version (purpose)

## Tests Status
- Unit Tests: X/Y passing
- Build: Pass/Fail
- TypeScript: Pass/Fail

## Conflicts Resolved
- Description of any conflicts and resolution

## Next Steps
- List remaining integration tasks
```

### Phase 5: Documentation & Handoff

#### 5.1 Update Integration Analysis

```bash
# Append to existing integration analysis report
cat >> reports/cognitivecodex_integration_analysis_2026-01-06.md <<EOF

## Integration Progress Update

**Completed:** $(date)

### Phase [X] Complete:
- [Summary of what was integrated]
- Files added: [count]
- Tests passing: [X/Y]
- Build status: [Pass/Fail]

### Remaining Work:
- [List of remaining tasks]

EOF
```

#### 5.2 Create Continuation Prompt

```markdown
# Continuation Prompt for Next Session

## Current Status
- Phase [X] complete: [summary]
- Tests: [X/Y passing]
- Integration: [X%] complete

## Next Actions
1. [Specific next step with file paths]
2. [Validation command to run]
3. [Expected outcome]

## Context for Next Agent
- Source extracted: $EXTRACTION_DIR (use the actual path from extraction)
- Integration analysis: reports/cognitivecodex_integration_analysis_2026-01-06.md
- Protected files: [list files that must not be modified]
```

---

## Quick Reference Commands

### File Discovery
```bash
# Find ZIP files
find . -name "*.zip" -type f 2>/dev/null

# Find by pattern in URL
FILENAME=$(echo "URL" | grep -o '[^/]*\.zip$')
find . -name "$FILENAME" -type f
```

### Extraction & Analysis
```bash
# Safe extraction
mkdir -p /tmp/extract-$(date +%s)
unzip -q /path/to/file.zip -d /tmp/extract-TIMESTAMP
tree -L 3 /tmp/extract-TIMESTAMP
```

### Integration Safety
```bash
# Before modifying any file, check test status
cd cognitive_app && npm test

# After each change, validate
npm run type-check && npm test && npm run build
```

### Conflict Detection
```bash
# Find duplicate filenames
comm -12 <(find source/ -name "*.tsx" | sort) \
         <(find target/ -name "*.tsx" | sort)
```

---

## Best Practices

### ✅ DO:
1. **Always check repository first** before stating limitations
2. **Extract filename from URLs** and search for it
3. **Create integration reports** for each phase
4. **Validate tests** after each merge step
5. **Document conflicts** and resolutions
6. **Use temporary directories** for extraction
7. **Commit incrementally** with descriptive messages

### ❌ DON'T:
1. **Don't immediately say "I cannot"** - investigate first
2. **Don't override tested code** without explicit approval
3. **Don't merge configuration files blindly** - review first
4. **Don't skip validation steps**
5. **Don't commit unvalidated changes**
6. **Don't ignore naming convention conflicts**
7. **Don't extract to repository directories** - use /tmp/

---

## Troubleshooting

### Issue: ZIP file not found
```bash
# Check all possible locations
find . -name "*.zip" -type f 2>/dev/null
ls -la misc/*.zip docs/**/*.zip *.zip 2>/dev/null

# Check if it needs to be downloaded/pushed first
echo "File may need to be added to repository by user"
```

### Issue: Extraction fails
```bash
# Check ZIP file integrity
unzip -t /path/to/file.zip

# Try different extraction method
python3 -m zipfile -e /path/to/file.zip /tmp/extract/
```

### Issue: Conflicts during merge
```bash
# For each conflict, create comparison
diff -u existing_file.tsx new_file.tsx > conflict_analysis.diff

# Document decision in integration report
# Options: Keep existing, use new, manual merge, rename
```

---

## Template Responses

### When ZIP file found in repository:
```
✅ ZIP file located at: [path]

Proceeding with extraction and integration:
1. Extracting to: /tmp/extraction-[timestamp]
2. Analyzing structure: [X] files, [Y] directories
3. Integration phase: [current phase]
4. Next steps: [specific actions]
```

### When ZIP file not found:
```
🔍 Searched for "[filename]" in:
- Repository root: ❌
- misc/ directory: ❌
- docs/ directory: ❌
- Other locations: ❌

To proceed, please:
1. Add the ZIP file to the repository (recommended: misc/[filename])
2. Push the changes to this branch
3. I'll then extract and integrate immediately

Alternative: Extract locally and push extracted contents to a temp directory.
```

---

## Conclusion

This protocol ensures efficient, safe, and thorough integration of external resources while maintaining code quality, test coverage, and system stability. Always check the repository first, validate incrementally, and document thoroughly.

**Key Principle:** Investigate before limitation, validate before integration, document throughout process.
