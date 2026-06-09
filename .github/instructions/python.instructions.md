---
applyTo: "**/*.py"
---

- Format Python code with **Black**.
- Lint Python code with **Ruff**.
- Sort imports with **isort**.
- Ruff configuration selects only E, F, I checks; tests ignore E402 and F811.
- Run type checks with **mypy** when changing Python modules.
- Ensure compliance with Python >=3.12 requirements.
- Use `strftime("%Y-%m-%dT%H:%M:%SZ")` for UTC Z timestamps.
