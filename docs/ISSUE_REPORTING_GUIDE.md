# Issue Reporting & Feature Request Guide
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Last Updated**: 2026-07-08 
**Version**: 1.0.0

This guide helps you report bugs effectively and request features thoughtfully.

## Table of Contents

1. [Before You Report](#before-you-report)
2. [Reporting Bugs](#reporting-bugs)
3. [Requesting Features](#requesting-features)
4. [Writing a Minimal Reproducible Example](#writing-a-minimal-reproducible-example)
5. [Following Up on Your Issue](#following-up-on-your-issue)

---

## Before You Report

### Is This Really a Bug?

Check if your issue might be:

1. **A usage question** → Use [GitHub Discussions](https://github.com/Aries-Serpent/_codex_/discussions) instead
2. **Already reported** → Search issues (may be fixed in next release)
3. **Expected behavior** → Check documentation or ask in discussions
4. **A feature request** → Use feature request template instead
5. **A security issue** → See SECURITY.md instead

### Quick Checklist

- [ ] I've read the documentation
- [ ] I've searched existing issues for similar reports
- [ ] I've checked the CHANGELOG to see if this is already fixed
- [ ] I can reproduce the issue consistently
- [ ] This is a bug, not a question or feature request

---

## Reporting Bugs

### Bug Report Template

**Use this template when opening an issue**:

```markdown
## Description
Brief description of what's not working.

## Expected Behavior
What should happen?

## Actual Behavior
What actually happens?

## Steps to Reproduce
1. ...
2. ...
3. ...

## Environment
- Python version: (run `python --version`)
- OS: (Windows/macOS/Linux)
- Installation: (pip/conda/from source)
- codex-ml version: (run `pip show codex-ml` or `python -c "from codex_ml import __version__; print(__version__)"`)

## Error Message
(full traceback, if applicable)

## Minimal Reproducible Example
(standalone code that shows the issue)

## Additional Context
(any other relevant information)
```

### Example Bug Report

```markdown
## Description
When loading a model with a config file path containing spaces, 
the loader crashes instead of handling the path correctly.

## Expected Behavior
Model should load successfully regardless of spaces in the path.

## Actual Behavior
ValueError is raised with message "Invalid path: /tmp/my config/model.yaml"

## Steps to Reproduce
1. Create a config file at `/tmp/my config/model.yaml`
2. Run:
 ```python
 from codex_ml import load_model
 model = load_model('/tmp/my config/model.yaml')
 ```
3. Observe error

## Environment
- Python version: 3.12.1
- OS: Ubuntu 22.04 LTS
- Installation: pip install codex-ml[full]
- codex-ml version: 0.1.0

## Error Message
```
Traceback (most recent call last):
 File "test.py", line 2, in <module>
 model = load_model('/tmp/my config/model.yaml')
 File "src/codex_ml/loader.py", line 45, in load_model
 validate_path(path)
 File "src/codex_ml/loader.py", line 78, in validate_path
 raise ValueError(f"Invalid path: {path}")
ValueError: Invalid path: /tmp/my config/model.yaml
```

## Minimal Reproducible Example
```python
from codex_ml import load_model
model = load_model('/tmp/my config/model.yaml')
```

## Additional Context
This works fine when the path has no spaces:
```python
model = load_model('/tmp/my_config/model.yaml') # Works 
```
```

### Bug Report Quality Tips

#### Good Bug Reports Include

- **Title**: Specific and descriptive
 - Good: "Model loading fails with spaces in path"
 - Bad: "Bug in loader"

- **Clear description**: What's broken?
 - Good: "When loading a model from a path with spaces, ValueError is raised"
 - Bad: "Something is broken"

- **Steps to reproduce**: Exact steps to see the bug
 - Good: 
 1. Create `/tmp/my config/config.yaml`
 2. Run `load_model('/tmp/my config/config.yaml')`
 - Bad: "Just use spaces in the path"

- **Expected vs actual**: What should happen vs. what happens
 - Good: "Should load the model; instead raises ValueError"
 - Bad: "It doesn't work"

- **Full error message**: The complete traceback
 - Good: Full traceback from Python
 - Bad: "Got an error"

- **Minimal example**: Standalone code to reproduce
 - Good: 5-10 lines of code
 - Bad: "Just load a model with spaces"

- **Environment details**: Python version, OS, etc.
 - Good: "Python 3.12.1, Ubuntu 22.04, codex-ml 0.1.0"
 - Bad: "Latest version"

#### Avoid

- Vague descriptions
- Multi-issue reports (one issue per report)
- Complaints instead of descriptions
- Information in code snippets only (summarize)
- Screenshots of code (paste the actual code)

---

## Requesting Features

### Feature Request Template

Use this when proposing new functionality:

```markdown
## Title
Clear, concise description of the feature.

## Motivation
Why is this feature needed? What problem does it solve?

## Proposed Solution
How should the feature work? Show example usage if possible.

## Alternatives Considered
What other approaches could work?

## Additional Context
Examples, use cases, related issues, etc.

## Impact
- [ ] Low impact (small feature, limited scope)
- [ ] Medium impact (useful to many, moderate complexity)
- [ ] High impact (breaks existing API, major change)
```

### Example Feature Request

```markdown
## Title
Support loading models directly from HuggingFace Hub

## Motivation
Currently, users must manually download models and store them locally.
This adds friction to workflow and makes reproducibility harder.

Many users want to load models directly from HuggingFace Hub, similar
to how other libraries work (e.g., `transformers`, `sentence-transformers`).

## Proposed Solution
Add optional `source` and `model_id` parameters to `load_model()`:

```python
# Load from local file (current)
model = load_model('path/to/config.yaml')

# Load from HuggingFace Hub (proposed)
model = load_model('gpt2', source='huggingface')
model = load_model('bert-base-uncased', source='huggingface')
```

Or use a URL pattern:
```python
model = load_model('huggingface://gpt2')
```

## Alternatives Considered
1. Manual download with `huggingface-hub` package
 - Pros: No changes needed
 - Cons: Extra steps, harder for new users

2. Environment variable for cache directory
 - Pros: Simple
 - Cons: Still requires manual download

3. Async loading with caching
 - Pros: Flexible
 - Cons: More complex API

## Additional Context
HuggingFace Hub hosts 10,000+ open models. This would:
- Lower barrier to entry
- Enable rapid experimentation
- Improve reproducibility
- Align with ecosystem patterns

Similar features in:
- `transformers.AutoModel.from_pretrained()`
- `sentence-transformers.SentenceTransformer()`
- PyTorch Hub

Related discussions:
- #123: User asked about HF Hub support
- #456: Reproducibility concerns
```

### Feature Request Quality Tips

#### Good Feature Requests

- **Clear title**: What feature is being requested?
- **Motivation**: Why is it needed? (not just "would be cool")
- **Use cases**: Real-world examples
- **API design**: How would users use this?
- **Examples**: Sample code showing the feature
- **Alternatives**: Other ways to solve the problem
- **Impact assessment**: How big is this change?

#### Avoid

- "I think this would be cool"
- Vague descriptions without motivation
- Demanding tone ("you need to add...")
- Complex features without breaking into steps
- Requests that conflict with project goals

---

## Writing a Minimal Reproducible Example

### Why Minimal Examples Matter

Good minimal examples:
- Help maintainers understand the issue
- Speed up debugging
- Can be added as test cases
- Make it easier to verify fixes
- Show you've done your homework

### Steps to Create MRE

1. **Start with your original code**
2. **Remove irrelevant parts** (keep only what's needed)
3. **Replace real data with dummy data** (no credentials!)
4. **Make it standalone** (shouldn't import your code)
5. **Run it to confirm it fails** (with the same error)
6. **Paste the code** in the issue

### Example MRE

** Too Complex** (unnecessary dependencies):
```python
from my_company.data import load_data
from my_company.model import MyModel
from my_company.utils import preprocess

# Load actual production data
data = load_data('s3://my-bucket/data.csv')
preprocessed = preprocess(data)

# Train my custom model
model = MyModel()
model.fit(preprocessed)

# This is where it fails
predictions = model.predict(preprocessed)
```

** Minimal** (shows only the issue):
```python
# This reproduces the issue without external dependencies
data = [
 {'value': 1},
 {'value': 'not a number'}, # This causes the issue
 {'value': 3},
]

for item in data:
 print(item['value'] + 1) # Fails on second item
```

### MRE Checklist

- [ ] Code is standalone (no imports of your code)
- [ ] Uses dummy/public data (no credentials, no large files)
- [ ] Runs without external dependencies (besides codex-ml)
- [ ] Shows the error (produces the same traceback)
- [ ] Is as short as possible while still showing the issue
- [ ] Has no comments explaining the code (it should be obvious)

---

## Following Up on Your Issue

### Providing Additional Information

If maintainers ask for more details:

1. **Respond in a comment** (don't edit original)
2. **Be specific**: Copy exact error messages, don't paraphrase
3. **Show your work**: Include output and commands
4. **Address all questions**: Don't skip any

### Checking for Updates

- **Set notifications**: Watch the issue for replies
- **Check regularly**: Don't let it get buried
- **Respond to requests**: If asked for more info, respond promptly
- **No bumping**: Don't post "any updates?" comments

### Getting Unstuck

If your issue isn't getting attention:

1. **After 1 week**: Make sure it's formatted well, add more details
2. **After 2 weeks**: Ask for feedback in discussions
3. **After 3 weeks**: Reach out to maintainers directly (if emails are public)
4. **Consider PR**: If you know how to fix it, submit a PR instead

### Closing Your Issue

If you find the solution yourself:

1. **Post the solution** in a comment
2. **Explain what was wrong** (helps others)
3. **Thank the community** (if someone helped)
4. **Close the issue** (or ask maintainer to close)

---

## Issue Labels & What They Mean

| Label | Meaning | What It Means for You |
|-------|---------|----------------------|
| `bug` | Something doesn't work | High priority, maintainers investigating |
| `feature-request` | Request for new feature | Under consideration, discussion welcome |
| `good-first-issue` | Great for new contributors | You can help! See CONTRIBUTING.md |
| `help-wanted` | Needs community input | Can be fixed by volunteers |
| `question` | Question, not a bug | For discussions, not issues |
| `documentation` | Docs need update | Help improve docs! |
| `blocked` | Waiting on something else | Can't fix yet |
| `duplicate` | Already reported | See linked issue for details |
| `wontfix` | Not something we'll fix | See comment for explanation |
| `P0` / `P1` / `P2` | Priority (high → low) | How urgently we're addressing it |

---

## Common Mistakes & How to Avoid Them

### Screenshot of Error Message

**Wrong**:
```
[Screenshot of Python error]
```

**Right**:
```
ValueError: invalid literal for int() with base 10: 'abc'
Traceback (most recent call last):
 File "test.py", line 5, in <module>
 x = int(my_string)
ValueError: invalid literal for int() with base 10: 'abc'
```

### Asking in Wrong Place

**Wrong**: Using issues for "how do I" questions

**Right**: Use GitHub Discussions for questions, Issues for bugs/features

### Missing Reproduction Steps

**Wrong**: "It doesn't work when I load models"

**Right**: 
1. Create config at `/tmp/test.yaml`
2. Run `load_model('/tmp/test.yaml')`
3. Observe ValueError

### Including Secrets

**Wrong**: Posting your API keys or credentials

**Right**: Use dummy values or scrub real ones

### Multiple Issues in One

**Wrong**: "Bug in loader AND feature request for streaming"

**Right**: Create separate issues for each

---

## Resources

- **[Contributing Guide](../CONTRIBUTING.md)** - How to get involved
- **[Community Guidelines](COMMUNITY_GUIDELINES.md)** - Communication norms
- **[Development Setup](DEVELOPMENT.md)** - Get your environment ready
- **[Code Review Guide](CODE_REVIEW_GUIDE.md)** - PR review process

---

## Still Have Questions?

- Check [docs/FAQ.md](FAQ.md)
- Ask in [GitHub Discussions](https://github.com/Aries-Serpent/_codex_/discussions)
- Read existing issues and PRs
- Look at the [Roadmap](ROADMAP.md)

Thank you for helping make Codex ML better! 
