# Agent Prompts - ChatGPT 5.1 Agent Mode

This directory contains pre-defined prompts for AI Agents (ChatGPT 5.1 Agent Mode) to interact with the Codex repository effectively.

## Directory Structure

```
agents/prompts/
├── README.md                    # This file
├── audit/                       # Audit and improvement prompts
├── organization/                # Repository organization prompts
├── documentation/               # Documentation generation prompts
├── deployment/                  # Pre-release and deployment prompts
├── debugging/                   # Debugging and troubleshooting prompts
└── self-healing/               # Self-correction and feedback prompts
```

## Usage

### For AI Agents (ChatGPT 5.1 Agent Mode)

1. **Navigate to prompt category** based on your task
2. **Read the prompt template** for your specific task
3. **Execute the commands** provided in the prompt
4. **Follow the validation steps** to ensure success
5. **Report results** using the structured format

### Prompt Categories

#### 1. Audit (`audit/`)
- Run full audit pipeline
- Check for regressions
- Generate dashboards and visualizations
- Store and compare trends

#### 2. Organization (`organization/`)
- Analyze repository structure
- Archive old files
- Clean up root directory
- Generate organization reports

#### 3. Documentation (`documentation/`)
- Generate wiki pages
- Create documentation hubs
- Build API references
- Update AGENTS.md

#### 4. Deployment (`deployment/`)
- Prepare pre-release packages
- Run validation tests
- Generate release assets
- Deploy to GitHub

#### 5. Debugging (`debugging/`)
- Debug test failures systematically
- Resolve merge conflicts
- Optimize performance bottlenecks
- Remediate security vulnerabilities

#### 6. Self-Healing (`self-healing/`)
- Detect capability gaps
- Implement feedback loops
- Self-correct issues
- Iterative improvements

## Integration with AGENTS.md

All prompts are referenced in [AGENTS.md](../../AGENTS.md) for easy discovery.

## Adding New Prompts

When adding new prompts:

1. Create a new `.md` file in the appropriate category
2. Use the template format (see any existing prompt)
3. Include: Purpose, Prerequisites, Commands, Validation, Expected Output
4. Add reference to AGENTS.md
5. Test the prompt with an AI Agent

## Prompt Template Format

```markdown
# [Prompt Name]

## Purpose
Brief description of what this prompt helps accomplish.

## Prerequisites
- List required tools/dependencies
- Required environment setup
- Access permissions needed

## Commands
\```bash
# Step-by-step commands
\```

## Validation
How to verify the task completed successfully.

## Expected Output
Description of what should be produced.

## Troubleshooting
Common issues and solutions.
```

## Version History

- **v1.1.0** (Previous Cycle-12-11): Added debugging prompts for AI Agents
  - Test failure debugging
  - Merge conflict resolution
  - Performance optimization
  - Security vulnerability remediation
- **v1.0.0** (Previous Cycle-12-10): Initial prompt structure for ChatGPT 5.1 Agent Mode
