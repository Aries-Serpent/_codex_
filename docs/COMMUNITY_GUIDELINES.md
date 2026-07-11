# Community Guidelines & Getting Help
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Last Updated**: 2026-07-08  
**Version**: 1.0.0

Welcome to the Codex ML community! This guide outlines how to participate constructively, get help when you need it, and build relationships with fellow contributors.

## Table of Contents

1. [Community Values](#community-values)
2. [Getting Help](#getting-help)
3. [Asking Good Questions](#asking-good-questions)
4. [Reporting Issues](#reporting-issues)
5. [Discussions & Conversations](#discussions--conversations)
6. [Code Review Etiquette](#code-review-etiquette)
7. [Conflict Resolution](#conflict-resolution)
8. [Contributor Recognition](#contributor-recognition)
9. [Anti-patterns to Avoid](#anti-patterns-to-avoid)

---

## Community Values

We believe in:

### **Respect**
- Treat all community members with dignity and respect
- Value diverse perspectives and backgrounds
- Assume good intentions

### **Inclusivity**
- Welcome contributors of all skill levels
- Create space for questions and learning
- Support underrepresented groups in tech

### **Collaboration**
- Work together toward common goals
- Share knowledge freely
- Help others succeed

### **Transparency**
- Be honest about limitations and challenges
- Document decisions and reasoning
- Share progress and updates

### **Quality**
- Strive for excellent code and documentation
- Embrace constructive criticism
- Continuous improvement mindset

---

## Getting Help

### When You're Stuck

**Step 1: Search existing resources**
- Check [docs/](docs/) - Most questions are answered there
- Search [GitHub Issues](https://github.com/Aries-Serpent/_codex_/issues?q=is%3Aissue) - Your question might be answered
- Check [GitHub Discussions](https://github.com/Aries-Serpent/_codex_/discussions) - For community Q&A
- Search error messages online (Stack Overflow, etc.)

**Step 2: Ask in the right place**

| Question Type | Best Location |
|--|--|
| "How do I...?" | GitHub Discussions |
| "Is this a bug?" | GitHub Issues (with reproduction) |
| "Should we add...?" | GitHub Discussions or Issues |
| "Code review help?" | Pull Request comments |
| "General chat?" | Discussions |

**Step 3: Post your question**
- Be specific and include relevant details
- Show what you've already tried
- Include error messages/output
- Share minimal reproducible example

### Support Channels

#### GitHub Discussions
**Best for**: Questions, ideas, general chat  
**How to use**:
1. Click "Discussions" tab on the repo
2. Search existing discussions
3. Click "New discussion"
4. Choose a category (Q&A, Ideas, etc.)
5. Write your question with details

#### GitHub Issues
**Best for**: Bugs, feature requests, confirmed problems  
**Use these labels**:
- `bug` - Something doesn't work
- `feature-request` - New capability wanted
- `good-first-issue` - Great for newcomers
- `help-wanted` - Needs community input
- `question` - Request for information

#### Pull Request Comments
**Best for**: Questions about specific code changes  
**How it works**:
1. Comment on the PR
2. Mention relevant people: `@username`
3. Reference line numbers: "Line 42"
4. Ask specific questions about the code

### Response Time Expectations

- **Urgent (security)**: Response within 24 hours
- **Bugs/PRs**: Response within 3-7 days
- **Discussions/Questions**: Response within 1-2 weeks
- **Feature requests**: Feedback within 2-4 weeks

*Note: These are targets, not guarantees. Maintainers are volunteers!*

---

## Asking Good Questions

### Question Checklist

Before posting, make sure your question:

- [ ] Is specific and focused (not too broad)
- [ ] Includes context about your goal
- [ ] Shows what you've already tried
- [ ] Includes error messages/output
- [ ] Has a minimal reproducible example
- [ ] Uses clear title/subject line
- [ ] Has proper formatting (code blocks, etc.)

### Template for Questions

```markdown
## Summary
Brief description of what you're trying to do.

## What I've Tried
- Checked documentation at...
- Searched issues for...
- Attempted solution...

## Minimal Example
<!-- Code that demonstrates the issue -->
```python
from codex_ml import load_model
model = load_model('path/to/config.yaml')
```

## Error Message
<!-- Full error output here -->
```
Traceback (most recent call last):
  File "test.py", line 1, in <module>
    model = load_model('path/to/config.yaml')
ValueError: Config file not found: path/to/config.yaml
```

## Environment
- Python version: 3.12.1
- OS: Ubuntu 22.04
- Installation: `pip install codex-ml[full]`

## Expected Behavior
What should happen...

## Actual Behavior
What actually happens...
```

### Examples of Good Questions

**Good **:
> "I'm trying to load a model from a config file with spaces in the path. When I run `load_model('/my path/model.yaml')` I get `ValueError: Invalid path`. How can I escape spaces or handle this?"

**Less Good **:
> "How do I load models?"

**Good **:
> "I want to add authentication to the API endpoint. Should I use JWT tokens or session cookies? What are the tradeoffs?"

**Less Good **:
> "How do authentication?"

---

## Reporting Issues

### Reporting a Bug

Use the bug report template on GitHub Issues. Include:

1. **Title**: Descriptive and concise
2. **Description**: What's the problem?
3. **Steps to Reproduce**: How to recreate it
4. **Expected vs. Actual**: What should happen vs. what happens
5. **Environment**: Python version, OS, installation method
6. **Error Message**: Full traceback
7. **Screenshots**: If applicable

### Bug Report Example

```markdown
## Title
Model loading fails with ValueError when config path contains spaces

## Description
When loading a model with a config file path that contains spaces,
the loader raises a ValueError instead of handling the path correctly.

## Steps to Reproduce
1. Create a config file at `/tmp/my config/model.yaml`
2. Run: `model = load_model('/tmp/my config/model.yaml')`
3. Observe error

## Expected Behavior
Model should load successfully regardless of spaces in path

## Actual Behavior
ValueError: Invalid path: /tmp/my config/model.yaml

## Environment
- Python: 3.12.1
- OS: Ubuntu 22.04
- Installation: `pip install codex-ml[full]`

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
```

### Requesting a Feature

Use the feature request template. Include:

1. **Title**: Clear description of feature
2. **Motivation**: Why is this needed?
3. **Proposed Solution**: How should it work?
4. **Alternatives**: Other approaches considered
5. **Context**: Use cases and examples

### Feature Request Example

```markdown
## Title
Support loading models directly from HuggingFace Hub

## Motivation
Currently models must be downloaded and stored locally. Many users
want to load models directly from HuggingFace Hub without manual
download. This is especially useful for rapid prototyping.

## Proposed Solution
Add optional `source` parameter:
```python
model = load_model('gpt2', source='huggingface')
```

## Alternatives Considered
- Manual download with huggingface-hub package first (current approach)
- Environment variable for default source (could add later)

## Additional Context
HuggingFace Hub has 10k+ public models. This would enable:
- Faster experimentation
- Easier model sharing and collaboration
- Better reproducibility
```

---

## Discussions & Conversations

### Healthy Discussions

**Do**:
-  Ask clarifying questions
-  Share relevant experience
-  Provide concrete examples
-  Acknowledge good points
-  Link to relevant resources
-  Stay on topic

**Don't**:
-  Go off-topic
-  Post the same question multiple times
-  Ignore answers and repeat questions
-  Use discussions for bugs/issues (use Issues instead)
-  Cross-post to many places (spam)
-  Post promotional/advertising content

### Following Conversations

GitHub Discussions can be long. To follow along:

1. **Watch the discussion**: Click "Subscribe" to get updates
2. **Sort by newest**: See most recent comments first
3. **Use search**: Ctrl/Cmd+F to find your topic
4. **Read before posting**: Check if your point is already made

### Resolving Discussions

If your question is answered:
1. Mark the answer: Click ✓ button (if discussion template allows)
2. Thank the responder
3. If still unclear, follow up with specific remaining questions
4. Close discussion when fully resolved

---

## Code Review Etiquette

### As a Reviewer

**Be Constructive**:
```markdown
 Bad:
"This code is wrong."

 Good:
"This approach causes a race condition when multiple threads access
the cache simultaneously. Consider using a lock, like in PR #123."
```

**Be Specific**:
```markdown
 Bad:
"Fix the code."

 Good:
"Line 42: The variable `count` might be None here. Add a null check
before using it on line 43, or initialize it in line 35."
```

**Be Humble**:
```markdown
 Bad:
"Why would anyone do this?"

 Good:
"I'm not sure I understand the approach here. Can you explain the
reasoning? I might be missing something."
```

**Be Appreciative**:
```markdown
 Good:
"Nice refactoring! This makes the code much clearer. One small thing:
could you also update the docstring to match?"
```

**Review Checklist**:
- [ ] Tests pass and coverage maintained
- [ ] Code follows style guidelines
- [ ] Functionality is correct
- [ ] Documentation is clear
- [ ] No obvious performance issues
- [ ] Security considerations addressed

### As a Contributor

**Receive Feedback Gracefully**:
- Read comments carefully
- Ask for clarification if needed
- Don't take it personally
- Make requested changes
- Thank reviewers for their time

**Respond to Comments**:
```markdown
 Good:
"Good catch! I fixed that on line 45. Would you like me to add a
test case for this edge case as well?"

 Dismissive:
"That's fine, it works."
```

**Request Re-Review**:
```markdown
"I've addressed all the comments. Ready for re-review!"
```

---

## Conflict Resolution

### If You Have a Disagreement

**Before escalating**:
1. **Read carefully**: Make sure you understand the other person's point
2. **Assume good intentions**: They're probably trying to help
3. **Think before responding**: Don't reply in anger
4. **Take it offline**: Complex discussions work better in real-time

**How to handle disagreement**:
```markdown
I see your point about [issue]. I was thinking about [alternative].
Let me explain my reasoning: [explanation]. What do you think about [specific aspect]?
```

### Reporting Violations

If someone violates the Code of Conduct:

1. **Do not escalate publicly**: Avoid calling them out in comments
2. **Report privately**: Email conduct@aries-serpent.dev
3. **Include details**: What happened, when, links to evidence
4. **Be specific**: Quote relevant messages
5. **Remain calm**: Let maintainers handle it

**Maintainers will**:
- Investigate promptly and fairly
- Keep reporter's privacy
- Take appropriate action
- Follow enforcement guidelines (see CODE_OF_CONDUCT.md)

---

## Contributor Recognition

### Ways We Recognize Contributors

1. **Credits in Changelog**: Listed in CHANGELOG.md for each release
2. **Commit History**: Your name on all your commits
3. **GitHub Stats**: Visible as contributor on GitHub
4. **Blog Posts**: Feature articles about significant contributions
5. **Release Notes**: Mentioned for major features
6. **Community Discussions**: Recognition from the community

### Adding Yourself to Credits

If you want credit for your contribution:
1. Ensure your git `user.name` and `user.email` are set correctly
2. Commit with those credentials
3. Your name will appear in our contributor list automatically

**Set git credentials**:
```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

---

## Anti-Patterns to Avoid

###  Spamming

Don't:
- Post the same question in multiple places
- Cross-post issues to every channel
- Bump discussions without new information
- Promote products/services

###  Arguing About Preferences

Don't:
- Bikeshed on code style (we use Black, case closed)
- Argue about tab vs. spaces (we use spaces, 4 indent)
- Debate language choice (we use Python, already decided)
- Fight about frameworks (we use specific frameworks for reasons)

**Instead**: Focus on functionality and correctness.

###  Inactivity

Don't:
- Open issues/PRs and abandon them
- Not respond to feedback for weeks
- Ignore questions about your changes

**Instead**: If you can't work on something, let maintainers know.

###  Demanding/Entitled Tone

Don't:
- "You need to fix this NOW"
- "This should already work"
- "Why haven't you done X?"

**Instead**: "Would it be possible to...?" or "I'd be happy to help with..."

###  Hijacking Discussions

Don't:
- Take over someone else's issue/PR with different topic
- Use discussions to promote competing products
- Derail conversations with off-topic comments

**Instead**: Open a new discussion/issue for your topic.

###  Passive Aggression

Don't:
- "As you might know..." (condescending)
- "Obviously..." (implies stupidity)
- "I shouldn't have to explain..." (dismissive)

**Instead**: Be direct and respectful.

---

## Quick Reference

### Common Scenarios

**"I found a bug!"**
→ Open an issue with the bug template

**"I want to suggest a feature"**
→ Start a discussion or open a feature-request issue

**"I'm interested in contributing"**
→ Read CONTRIBUTING.md, check good-first-issue labels

**"I disagree with a decision"**
→ Ask about the reasoning in discussions, respectfully

**"Someone was rude to me"**
→ Report to conduct@aries-serpent.dev, or reach out privately

**"My PR is stuck"**
→ Ask for feedback in a comment, don't bump repeatedly

**"I want to know more about the roadmap"**
→ Check ROADMAP.md or ask in discussions

---

## Thank You!

We appreciate every contribution, question, and piece of feedback. The community makes this project better! 🎉

**Questions about this guide?** Open a discussion or reach out to maintainers.

---

**Related Documents**:
- [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md) - Community standards and enforcement
- [CONTRIBUTING.md](../CONTRIBUTING.md) - How to contribute code
- [DEVELOPMENT.md](DEVELOPMENT.md) - Setting up your environment
