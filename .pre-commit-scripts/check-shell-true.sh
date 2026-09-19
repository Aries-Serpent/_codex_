#!/bin/bash
# Check for subprocess shell=True (command injection risk)
# This script prevents command injection vulnerabilities by detecting shell=True usage

files=$(find . \( \
    -path "./.git" \
    -o -path "./tests" \
    -o -path "./scripts" \
    -o -path "./security/fix" \
    -o -path "./security/validate" \
    -o -path "./.github" \
    -o -path "./.codex" \
    -o -path "./.venv_ci" \
    -o -path "./.venv_validation" \
    -o -path "./.venv_agent" \
    -o -path "./.venv_test" \
    -o -path "./venv_test" \
    -o -path "./tools" \
  \) -prune -o -name "*.py" -print | xargs grep -n "shell=True" 2>/dev/null | grep -E -v '(# nosec|raise.*Error.*".*shell=True|^[[:space:]]*#)' || true)

if [ -n "$files" ]; then
  echo "$files"
  echo "ERROR: Found shell=True in production code. Use shlex.split() and shell=False instead."
  exit 1
else
  exit 0
fi
