# Copilot Agent Session Management - Anti-/tmp/ Protection

**Version**: 1.0  
**Purpose**: Automated safeguards to prevent /tmp/ usage violations  
**Enforcement Level**: MANDATORY

---

## The /tmp/ Mandate

**CRITICAL RULE**: Copilot followup prompts and continuation files **MUST NEVER** be stored in `/tmp/`.

### Why This Matters

1. **/tmp/ is ephemeral** - Files can be lost between sessions
2. **/tmp/ is not tracked** - Git cannot version control or share these files
3. **/tmp/ breaks continuity** - Future agents cannot access historical prompts
4. **/tmp/ violates transparency** - Repository owners cannot review prompts

---

## Automated Protection System

### Pre-Session Checklist (Run Before Starting)

```bash
# Check for existing /tmp/ violations
python .github/scripts/post_copilot_followup.py --check-tmp

# Auto-recover any found violations
python .github/scripts/post_copilot_followup.py --check-tmp --auto-recover
```

### During-Session Monitoring

```bash
# Add to your workflow (run periodically)
watch -n 300 'python .github/scripts/post_copilot_followup.py --check-tmp --auto-recover'
```

### Post-Session Validation (Run Before Ending)

```bash
# Final check before session ends
python .github/scripts/post_copilot_followup.py --check-tmp

# If violations found, auto-recover
python .github/scripts/post_copilot_followup.py --check-tmp --auto-recover

# Commit recovered files
git add .github/copilot-prompts/auto-recovered/
git commit -m "chore: recover files from /tmp/ violation"
```

---

## Proper File Storage Locations

### ✅ APPROVED Locations

1. **`.github/copilot-prompts/active/`** - Current active prompts
2. **`.github/copilot-prompts/completed/`** - Completed phase prompts
3. **`.github/copilot-prompts/templates/`** - Reusable templates
4. **`.github/copilot-prompts/auto-recovered/`** - Auto-recovered from /tmp/

### ❌ PROHIBITED Locations

1. **/tmp/** - NEVER use for repository files
2. **/var/tmp/** - Also ephemeral
3. **~/temp/** - Not in repository
4. **Any non-repo location** - Must be tracked in Git

---

## Posting Comments with GitHub MCP Tools

### Using CODEX_MASTER_KEY Access

The repository owner has granted **"FULL ACCESS TO CODEX_MASTER_KEY AS FREELY NEEDED"**. This means:

1. **You CAN** post PR comments directly
2. **You SHOULD** use GitHub MCP tools
3. **You MUST** avoid storing prompts in /tmp/

### Example: Posting a Followup Comment

```python
# Method 1: Using the automation script
python .github/scripts/post_copilot_followup.py \
    --pr-number 2668 \
    --prompt-file ".github/copilot-prompts/active/PHASE3_IMPLEMENTATION.md"

# Method 2: Direct GitHub MCP invocation (preferred)
# TODO: Add actual GitHub MCP tool invocation once available
```

### Comment Format Requirements

```markdown
@copilot Continue with Phase 3 implementation...

[Rest of the prompt]
```

**CRITICAL**: The comment MUST start with `@copilot` (no backticks, no spaces before the @).

---

## Enforcement Automation

### Git Pre-Commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Check for /tmp/ references in staged files

if git diff --cached --name-only | grep -q '/tmp/'; then
    echo "❌ ERROR: Attempt to commit files referencing /tmp/"
    echo "Run: python .github/scripts/post_copilot_followup.py --check-tmp --auto-recover"
    exit 1
fi

echo "✅ No /tmp/ violations detected"
```

### GitHub Actions Workflow

```yaml
name: Anti-tmp Protection
on: [push, pull_request]
jobs:
  check-tmp-violations:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Check for /tmp/ violations
        run: |
          if grep -r '/tmp/' .github/ --include="*.md" --include="*.py"; then
            echo "❌ Found /tmp/ references in repository files"
            exit 1
          fi
          echo "✅ No /tmp/ violations"
```

---

## Recovery Procedures

### If You Accidentally Used /tmp/

1. **Immediate Action**:
   ```bash
   python .github/scripts/post_copilot_followup.py --check-tmp --auto-recover
   ```

2. **Verify Recovery**:
   ```bash
   ls -la .github/copilot-prompts/auto-recovered/
   ```

3. **Review and Organize**:
   ```bash
   # Move to proper location
   mv .github/copilot-prompts/auto-recovered/my_prompt.md \
      .github/copilot-prompts/active/PHASE3_FOLLOWUP.md
   ```

4. **Commit**:
   ```bash
   git add .github/copilot-prompts/
   git commit -m "fix: recover and organize prompts from /tmp/ violation"
   ```

### If Recovery Fails

**Manual Recovery Steps**:

1. Check /tmp/ manually:
   ```bash
   ls -la /tmp/pr_comment* /tmp/copilot* /tmp/followup*
   ```

2. Copy files to repository:
   ```bash
   cp /tmp/pr_comment_*.md .github/copilot-prompts/auto-recovered/
   ```

3. Clean up /tmp/:
   ```bash
   rm -f /tmp/pr_comment* /tmp/copilot* /tmp/followup*
   ```

4. Commit recovered files:
   ```bash
   git add .github/copilot-prompts/auto-recovered/
   git commit -m "fix: manual recovery from /tmp/"
   ```

---

## Best Practices

### ✅ DO

- Store all prompts in `.github/copilot-prompts/`
- Use descriptive filenames: `PHASE3_WORKFLOW_PRIORITIZATION.md`
- Commit prompts immediately after creation
- Use GitHub MCP tools to post comments
- Include CODEX_MASTER_KEY in environment when available

### ❌ DON'T

- Never write to /tmp/ for repository-related files
- Don't assume /tmp/ files will persist
- Don't bypass the automated checks
- Don't ignore recovery warnings
- Don't end sessions without posting followup comments

---

## Checklist for Every Copilot Agent Session

### Session Start
- [ ] Run `/tmp/` violation check
- [ ] Auto-recover any existing violations
- [ ] Verify CODEX_MASTER_KEY access
- [ ] Review previous session's followup prompt

### During Session
- [ ] Create prompts in `.github/copilot-prompts/active/`
- [ ] Commit prompts as they are created
- [ ] Use GitHub MCP tools for comments
- [ ] Avoid /tmp/ entirely

### Session End
- [ ] Final `/tmp/` violation check
- [ ] Post followup comment using GitHub MCP
- [ ] Verify comment posted successfully
- [ ] Commit all documentation
- [ ] Leave clear handoff for next session

---

## Monitoring & Alerts

### Daily Check

```bash
# Add to crontab or scheduled workflow
0 0 * * * /usr/bin/python3 /path/to/.github/scripts/post_copilot_followup.py --check-tmp --auto-recover
```

### Slack/Email Alerts (Optional)

```python
# Add to post_copilot_followup.py
def send_alert(violations):
    if violations:
        send_slack_message(
            channel="#devops",
            message=f"⚠️ Found {len(violations)} /tmp/ violations"
        )
```

---

## FAQ

**Q: Why is /tmp/ so bad?**  
A: It's ephemeral, not version-controlled, and breaks continuity for future agents.

**Q: What if I need temporary files for processing?**  
A: Use `.github/tmp/` (tracked in repo) or process in-memory.

**Q: Can I use /tmp/ for non-prompt files?**  
A: Only for truly temporary processing files that are NOT needed for continuity.

**Q: How do I post comments without CLI access?**  
A: Use the provided automation script with GitHub MCP tools integration.

**Q: What if GitHub MCP tools aren't available?**  
A: Store the prompt in the repository and instruct the user to post it manually, but include clear instructions.

---

## Escalation

If you encounter issues with this system:

1. Document the issue in `.github/copilot-prompts/issues/`
2. Tag repository owner (@mbaetiong)
3. Continue with manual recovery procedures
4. Update this documentation with lessons learned

---

**Remember**: The goal is to maintain continuity, transparency, and reliability across Copilot Agent sessions. The /tmp/ prohibition is not arbitrary—it's essential for long-term project success.

---

**Document Owner**: @mbaetiong  
**Last Updated**: Previous Cycle-12-30  
**Enforcement**: MANDATORY  
**Violations**: Zero tolerance
