# Code Review Guidelines

**Last Updated**: 2026-07-08  
**Version**: 1.0.0

Code reviews are critical for maintaining code quality, sharing knowledge, and fostering collaboration. This guide helps reviewers and contributors make the code review process smooth and productive.

## Table of Contents

1. [Code Review Principles](#code-review-principles)
2. [For Reviewers](#for-reviewers)
3. [For Contributors](#for-contributors)
4. [Review Checklist](#review-checklist)
5. [Common Issues & How to Phrase Feedback](#common-issues--how-to-phrase-feedback)
6. [Tools & Automation](#tools--automation)

---

## Code Review Principles

### Goals of Code Review

1. **Catch bugs**: Find issues before they reach users
2. **Share knowledge**: Help the whole team learn
3. **Maintain standards**: Ensure code quality and consistency
4. **Build relationships**: Connect team members through collaboration
5. **Improve code**: Make code clearer and more maintainable

### Core Values

- **Respectful**: Focus on code, not the person
- **Constructive**: Suggest improvements, don't just criticize
- **Collaborative**: Work together to solve problems
- **Timely**: Review promptly so contributors aren't blocked
- **Thorough**: Don't skip important checks
- **Humble**: Assume good intentions and learn from others

---

## For Reviewers

### Review Workflow

1. **Receive notification**: Get PR in your inbox/notification
2. **Prioritize**: High-priority PRs should be reviewed within 1-2 days
3. **Review thoroughly**: Check functionality, style, tests, docs
4. **Leave clear feedback**: Explain the "why" behind suggestions
5. **Request changes or approve**: Use GitHub review features
6. **Follow up**: Respond promptly to contributor questions

### Starting a Review

**Before diving in**:
- [ ] Read the PR title and description
- [ ] Check the related issue/discussion
- [ ] Look at the changed files list
- [ ] Run tests locally (optional but helpful)

**Structure your review**:
1. First pass: Understand the overall approach
2. Second pass: Check logic and correctness
3. Third pass: Look at style and standards
4. Final pass: Consider edge cases and performance

### Types of Feedback

**Critical Issues** (Must fix before merge):
- Security vulnerabilities
- Bugs that break functionality
- Major performance issues
- Breaking changes without discussion

**Important Issues** (Should fix):
- Coverage regressions
- Type errors
- Style violations
- Missing tests or documentation

**Suggestions** (Nice to have):
- Refactoring for clarity
- Performance optimizations
- Better naming
- Additional edge cases

**Compliments** (Always appreciated):
- Good code structure
- Clear variable names
- Excellent test coverage
- Great documentation

### Effective Feedback Examples

#### ❌ Don't:
```markdown
This code is terrible. Fix it.
```

#### ✅ Do:
```markdown
This function has high complexity and is hard to follow. Consider
breaking it into smaller functions, or adding more inline comments
to explain the logic. For example, the loop on lines 42-67 could be
its own function that validates the batch.
```

#### ❌ Don't:
```markdown
Why would anyone do it this way?
```

#### ✅ Do:
```markdown
I'm not immediately clear on why you're using a list instead of
a set here. Sets have O(1) lookup. Is there a reason you need to
preserve order? If so, consider using `collections.OrderedDict` or
adding a comment explaining the requirement.
```

#### ❌ Don't:
```markdown
Add tests.
```

#### ✅ Do:
```markdown
The new `validate_config()` function isn't covered by tests. Could
you add tests for:
- Valid config inputs
- Missing required keys
- Invalid types (e.g., string instead of int)

See `tests/test_config.py` for the testing pattern we use.
```

### Handling Disagreements

If you disagree with an approach:

**Don't**:
- Block the PR without good reason
- Demand your way
- Be condescending

**Do**:
- Explain your perspective
- Ask clarifying questions
- Suggest alternatives
- Defer to maintainers if stuck

**Example**:
```markdown
I had a different approach in mind here. Rather than calling the
validation function before saving, we could validate on load to
reduce startup time. However, I see your approach is more strict and
catches errors earlier. Both are valid - what's the reasoning for
choosing this path?
```

### When to Request Changes vs. Comment

**Request Changes** (blocks PR):
- Critical bugs that break functionality
- Security vulnerabilities
- Missing tests for new code
- Type errors
- Breaking API changes

**Comment** (doesn't block):
- Style suggestions
- Performance ideas
- Refactoring suggestions
- Praise and thanks

### Review Shortcuts

**For small PRs** (< 100 lines):
- 1-5 minutes review
- Check tests, types, style
- Look for obvious bugs

**For medium PRs** (100-500 lines):
- 5-15 minutes review
- Understand overall approach
- Check tests and coverage
- Review critical paths

**For large PRs** (500+ lines):
- 15-60+ minutes review
- Might span multiple sittings
- Request description of approach
- Focus on critical sections first
- Consider asking for smaller chunks

---

## For Contributors

### Before Requesting Review

**Your PR should have**:
- [ ] Clear title and description
- [ ] Tests passing locally
- [ ] Coverage maintained (>90%)
- [ ] Type checks passing (`mypy`)
- [ ] Code formatted (`black`)
- [ ] Linting passes (`ruff`)
- [ ] All commits squashed (clean history)

**Check using**:
```bash
# Run all local checks
pytest
pytest --cov=src --cov-fail-under=90
mypy src/
black --check src/
ruff check src/
pre-commit run --all-files
```

### PR Description Template

Use this when creating your PR:

```markdown
## Description
Clear, concise description of what this PR does and why.

## Type of Change
- [ ] Bug fix (non-breaking)
- [ ] New feature (non-breaking)
- [ ] Breaking change (causes existing functionality to change)
- [ ] Documentation update
- [ ] Performance improvement

## Related Issues
Closes #ISSUE_NUMBER

## Testing
- [ ] Added tests for new functionality
- [ ] All tests pass locally
- [ ] Coverage maintained above 90%
- [ ] Manual testing (if applicable)

## Checklist
- [ ] Code follows project style guidelines
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Ready for review
```

### Receiving Feedback

**Do**:
- ✅ Read all feedback carefully
- ✅ Ask clarifying questions
- ✅ Respond to all comments (even if just saying "Done")
- ✅ Make requested changes
- ✅ Acknowledge good suggestions
- ✅ Push fixes and re-request review

**Don't**:
- ❌ Ignore feedback
- ❌ Dismiss suggestions without explanation
- ❌ Argue about subjective preferences
- ❌ Make excuses
- ❌ Push new features while being reviewed

### Responding to Feedback

**To disagreement**:
```markdown
✅ Good:
I see your point about using a set here. I was thinking about the
order requirement - we need to preserve insertion order. Would it be
better to use `collections.OrderedDict` instead and update the comment?

❌ Dismissive:
It works fine as is.
```

**To suggestions**:
```markdown
✅ Good:
Great idea! I implemented that suggestion on line 42. Let me know
if it addresses your concern.

❌ Dismissive:
Already thought of that.
```

**When you disagree**:
```markdown
✅ Good:
I understand your point. However, the current approach handles [case]
better because [reason]. Would you be okay with this approach if I add
a comment explaining this trade-off?

❌ Dismissive:
My way is better.
```

**When something is unclear**:
```markdown
✅ Good:
Can you clarify what you mean by "simplify"? Are you suggesting I
extract this into a helper function, or refactor the algorithm?

❌ Dismissive:
I don't understand.
```

### Handling Review Stalls

If your PR is stuck (not reviewed in several days):

1. **First**: Check if review is requested (you should have seen notification)
2. **After 3 days**: Leave a friendly comment
   ```markdown
   Friendly ping! Would appreciate feedback when available. 😊
   ```
3. **After 1 week**: Ask in discussions or mention a maintainer
4. **Never**: Get angry or demanding

---

## Review Checklist

### Functionality

- [ ] Code does what the PR description says
- [ ] No obvious bugs
- [ ] Handles error cases
- [ ] No infinite loops or deadlocks
- [ ] Correct types/ranges for values
- [ ] No race conditions
- [ ] Performance is acceptable

### Testing

- [ ] Tests pass (CI green ✅)
- [ ] Coverage doesn't decrease
- [ ] New code has tests
- [ ] Edge cases covered
- [ ] Tests are clear and well-named
- [ ] Tests actually test the code (not just coverage farming)

### Code Quality

- [ ] Code is readable
- [ ] Follows style guide (Black, Ruff, etc.)
- [ ] Variable/function names are clear
- [ ] Complex logic has comments
- [ ] DRY principle (no duplication)
- [ ] No debug code or comments

### Type Safety

- [ ] Type hints present
- [ ] `mypy --strict` passes
- [ ] Types are correct (no `Any` unless needed)
- [ ] Union types are specific

### Security

- [ ] No hardcoded secrets
- [ ] Input validation
- [ ] No SQL/command injection
- [ ] Safe deserialization (no pickle)
- [ ] No unsafe crypto

### Documentation

- [ ] Docstrings updated
- [ ] README updated if applicable
- [ ] API docs updated
- [ ] Examples provided for new features
- [ ] Breaking changes noted

### Performance

- [ ] No obvious performance regression
- [ ] Efficient algorithms
- [ ] No unnecessary copies
- [ ] Memory usage reasonable
- [ ] Network calls minimized

---

## Common Issues & How to Phrase Feedback

### Missing Tests

**❌ Don't**:
```markdown
Add tests.
```

**✅ Do**:
```markdown
This new function isn't covered by tests. Could you add tests for:
1. Valid inputs (happy path)
2. Missing required parameters
3. Invalid types (e.g., string instead of int)
4. Edge cases (empty list, very large numbers, etc.)

See `tests/test_module.py` for our testing patterns.
```

### Poor Variable Names

**❌ Don't**:
```markdown
Bad variable names.
```

**✅ Do**:
```markdown
The variable `x` on line 42 could have a more descriptive name.
Based on the context, something like `token_count` or `validated_items`
would be clearer. What does it represent?
```

### Missing Documentation

**❌ Don't**:
```markdown
Add docs.
```

**✅ Do**:
```markdown
Could you add a docstring to this function? Include:
- What it does
- Parameter descriptions
- Return value
- Example usage
- Any exceptions it might raise

Here's our docstring style:
```python
def process_data(items: list[dict], batch_size: int = 32) -> Iterator[list]:
    \"\"\"Process items in batches.
    
    Args:
        items: List of data items to process
        batch_size: Number of items per batch (default: 32)
    
    Returns:
        Iterator of batches
    
    Raises:
        ValueError: If batch_size is not positive
    
    Example:
        >>> data = [{'id': 1}, {'id': 2}]
        >>> for batch in process_data(data, batch_size=1):
        ...     print(batch)
    \"\"\"
```

### Style Violations

**❌ Don't**:
```markdown
Fix your style.
```

**✅ Do**:
```markdown
This line is 125 characters long (our limit is 100). Could you break
it into multiple lines?

Also, the space before the colon on line 52 violates our style guide
(should be no space). I can run Black to fix this if you'd like:
\`\`\`bash
black file.py
\`\`\`
```

### Logic Issues

**❌ Don't**:
```markdown
This logic is wrong.
```

**✅ Do**:
```markdown
I think there might be an issue here. If `user_id` is None (which can
happen on line 35), then line 42 will raise an AttributeError instead
of the intended ValueError.

Could you add a check like:
\`\`\`python
if user_id is None:
    raise ValueError("user_id is required")
\`\`\`

Or if None is acceptable, what should happen?
```

### Performance Concerns

**❌ Don't**:
```markdown
This is inefficient.
```

**✅ Do**:
```markdown
This O(n²) loop might be slow for large datasets. Consider using a set
for lookups instead:

\`\`\`python
# Current approach (O(n²)):
for item in items:
    if item in other_list:  # O(n) search

# Faster approach (O(n)):
other_set = set(other_list)
for item in items:
    if item in other_set:  # O(1) lookup
\`\`\`

If performance isn't a concern here, feel free to leave as-is.
```

---

## Tools & Automation

### GitHub Review Features

**Request Changes**:
- Blocks PR from merging
- Use for critical issues
- Contributor must respond

**Approve**:
- Indicates approval
- PR can merge (if all checks pass)
- Use when satisfied

**Comment**:
- No blocking
- For suggestions and questions
- Great for discussions

### Automated Tools

These run automatically on every PR:

1. **Tests** (`pytest`) - Ensures code works
2. **Coverage** - Checks test coverage meets minimum
3. **Type Checking** (`mypy`) - Catches type errors
4. **Formatting** (`black`) - Ensures consistent style
5. **Linting** (`ruff`) - Catches bugs and style issues
6. **Pre-commit hooks** - Local quality gates

### Requesting Manual Checks

Some things still need humans:

- [ ] Architecture review
- [ ] Security review
- [ ] Performance profiling
- [ ] UX/design feedback
- [ ] API stability concerns
- [ ] Documentation clarity

---

## Helpful Resources

- **[CONTRIBUTING.md](../CONTRIBUTING.md)** - How to contribute
- **[CODE_STYLE_GUIDE.md](dev/CODE_STYLE_GUIDE.md)** - Style standards
- **[testing.md](dev/testing.md)** - Testing practices
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Setup guide

---

## Questions?

- **"How strict should I be?"** → Focus on critical issues, suggest others
- **"How long should reviews take?"** → 5-30 min for most PRs
- **"What if I disagree?"** → Discuss respectfully, don't block without reason
- **"How do I handle criticism?"** → View it as opportunity to learn
- **"What if someone is rude?"** → Report to conduct@aries-serpent.dev

Happy reviewing! 🔍
