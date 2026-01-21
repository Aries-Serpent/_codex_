# Mutation Testing Configuration for Phase 15.2
# 
# This file configures mutmut for mutation testing.
# Run with: mutmut run --paths-to-mutate=src/
#
# Created: 2026-01-18
# Phase: 15.2 - Mutation Testing

def init():
    """Initialize mutation testing configuration."""
    pass


# Paths to mutate
paths_to_mutate = "src/"

# Paths to backup (not mutated)
backup = True

# Test runner
runner = "python -m pytest tests/ -x -q --tb=no"

# Disable mutations in these files
dict_synonyms = ["config", "settings", "defaults"]

# Files to skip
def pre_mutation(context):
    """Called before each mutation."""
    # Skip test files
    if context.filename.startswith("tests/"):
        context.skip = True
    
    # Skip __init__.py files
    if context.filename.endswith("__init__.py"):
        context.skip = True
    
    # Skip type stubs
    if context.filename.endswith(".pyi"):
        context.skip = True
    
    # Skip generated files
    if "generated" in context.filename:
        context.skip = True


def pre_mutation_ast(context):
    """Called before AST-based mutations."""
    # Skip docstrings
    if context.current_source_line.strip().startswith('"""'):
        context.skip = True
    if context.current_source_line.strip().startswith("'''"):
        context.skip = True
    
    # Skip comments
    if context.current_source_line.strip().startswith("#"):
        context.skip = True
