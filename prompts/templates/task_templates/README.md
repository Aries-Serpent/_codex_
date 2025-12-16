# Task Templates

This directory contains structured templates for common agent tasks. Each YAML file must parse with `yaml.safe_load` and should include clear instructions on when to retrieve, which tools to call, and how to report verification states.

## Conventions
- Keep tasks minimal and action-oriented.
- Include acceptance criteria and evidence expectations.
- Mark unknowns explicitly and request needed retrieval/tool calls.
