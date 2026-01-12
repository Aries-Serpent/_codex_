# Rust Error Handling Validator

Specialized agent for scanning Rust code to identify panic risks and suggest idiomatic error handling patterns with focus on PyO3 Python bindings.

## Mission
Scan Rust code for panic risks (`unwrap`, `expect`, `unreachable!`, `panic!`) and suggest idiomatic error handling patterns based on context.

## Quick Start
```bash
cd .github/agents/rust-error-validator
pip install -r requirements.txt
python scanner.py scan --dir ../../../rust_swarm/
```

## Output Example
```
File: rust_swarm/compression.rs:17
Severity: HIGH
Issue: unwrap() in python_facing_function can cause panic
Suggested fix: Return PyResult with .map_err()
```

See full documentation in repository.
