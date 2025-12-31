# Resolving Merge Conflicts

This prompt guides AI Agents through resolving merge conflicts systematically.

## Context

Use this prompt when git merge conflicts occur during PR merges or branch updates.

## Prompt Template

```
I need help resolving merge conflicts in the Codex repository.

**Conflict Information:**
- Branch: [feature-branch]
- Target branch: [main/develop]
- Conflicting files: [list files]
- Conflict type: [content / binary / rename]

**Steps to Resolve:**

1. **Understand the Conflict**
   ```bash
   # Check conflict status
   git status
   
   # See conflict markers
   git diff
   
   # View both versions
   git show :1:path/to/file  # common ancestor
   git show :2:path/to/file  # current branch (HEAD)
   git show :3:path/to/file  # incoming branch
   ```

2. **Analyze Changes**
   - Check what changes were made in your branch
   - Check what changes were made in target branch
   - Identify if changes are compatible or conflicting
   - Look for logical conflicts (not just textual)

3. **Resolution Strategy**

   **For Code Conflicts:**
   - Preserve both changes if they're independent
   - Choose one if they conflict logically
   - Merge logic if both needed
   - Test thoroughly after resolution

   **For Configuration Conflicts:**
   - Verify both configurations are valid
   - Merge settings intelligently
   - Preserve environment-specific settings

   **For Documentation Conflicts:**
   - Merge content from both sides
   - Remove duplicate information
   - Ensure consistency in style

4. **Resolve the Conflict**

   **Manual Resolution:**
   ```bash
   # Edit file to resolve conflicts
   # Remove conflict markers: <<<<<<<, =======, >>>>>>>
   # Keep desired changes
   # Save file
   
   # Mark as resolved
   git add path/to/file
   
   # Continue merge/rebase
   git commit  # for merge
   git rebase --continue  # for rebase
   ```

   **Using Git Tools:**
   ```bash
   # Use mergetool
   git mergetool path/to/file
   
   # Choose version (with caution)
   git checkout --ours path/to/file    # keep your version
   git checkout --theirs path/to/file  # take their version
   ```

5. **Verify Resolution**
   ```bash
   # Run linters
   ruff check path/to/file
   
   # Run affected tests
   pytest path/to/related/tests -v
   
   # Check syntax
   python -m py_compile path/to/file
   
   # View final result
   git diff --cached path/to/file
   ```

6. **Common Conflict Patterns**

   **Import Conflicts:**
   ```python
   # Both branches added imports - merge both
   <<<<<<< HEAD
   from module_a import ClassA
   =======
   from module_b import ClassB
   >>>>>>> feature
   
   # Resolution: include both
   from module_a import ClassA
   from module_b import ClassB
   ```

   **Function Conflicts:**
   ```python
   # Both branches modified function - merge logic
   <<<<<<< HEAD
   def process(data):
       validate(data)
       return transform(data)
   =======
   def process(data):
       validate(data)
       return enhance(transform(data))
   >>>>>>> feature
   
   # Resolution: combine both enhancements
   def process(data):
       validate(data)
       return enhance(transform(data))
   ```

   **Configuration Conflicts:**
   ```yaml
   # Both branches added settings - merge both
   <<<<<<< HEAD
   settings:
     feature_a: true
   =======
   settings:
     feature_b: true
   >>>>>>> feature
   
   # Resolution: include both
   settings:
     feature_a: true
     feature_b: true
   ```

7. **Final Checks**
   ```bash
   # Ensure all conflicts resolved
   git status | grep -i conflict
   
   # Run full test suite
   pytest tests/ -v
   
   # Check for unintended changes
   git diff main..HEAD --stat
   ```

**Useful Commands:**
```bash
# Abort merge if needed
git merge --abort
git rebase --abort

# List conflicted files
git diff --name-only --diff-filter=U

# Show conflict summary
git ls-files -u

# Re-resolve using recorded resolution (if available)
git rerere
```

**Repository-Specific Notes:**

For Codex repository:
- Check AGENTS.md for code style conventions
- Verify tests pass after resolution
- Update documentation if API changed
- Run audit pipeline if capabilities affected

**Prevention:**
- Keep branches up to date with main
- Make smaller, focused PRs
- Communicate about overlapping work
- Use feature flags for long-running features
```

## Examples

### Example 1: Import Conflict

```
File: src/codex_ml/training.py
Conflict: Both branches added different imports

Resolution:
- Merge both import lists
- Sort imports alphabetically
- Remove duplicates
- Run isort to format
```

### Example 2: Function Modification

```
File: scripts/audit_runner.py
Conflict: Both branches modified same function

Resolution:
- Understand intent of both changes
- Merge logic if compatible
- Keep both features if possible
- Test thoroughly to ensure correctness
```

### Example 3: Configuration Update

```
File: pyproject.toml
Conflict: Both branches updated dependencies

Resolution:
- Merge dependency lists
- Use newer versions if compatible
- Check for conflicts between dependencies
- Run tests to verify compatibility
```

## Best Practices

1. **Test After Every Resolution**
   - Run affected tests immediately
   - Don't accumulate untested resolutions

2. **Understand Both Changes**
   - Read commit messages
   - Check PR descriptions
   - Ask author if unclear

3. **Document Complex Resolutions**
   - Add comments explaining why
   - Update PR description
   - Mention in commit message

4. **Seek Help When Needed**
   - Ask original authors
   - Escalate if business logic unclear
   - Don't guess on critical code

## Related Prompts

- [Test Failure Debugging](./test-failure-debugging.md)


## Automation

Future: Add merge conflict resolution to workflow navigator

```python
from agents.workflow_navigator import WorkflowNavigator

navigator = WorkflowNavigator()
navigator.execute('RESOLVE_CONFLICT')  # Future feature
```

## References

- [Git merge documentation](https://git-scm.com/docs/git-merge)
- [Git conflict resolution](https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging#_basic_merge_conflicts)
- [Codex contribution guidelines](../../../CONTRIBUTING.md)
