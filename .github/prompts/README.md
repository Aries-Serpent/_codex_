# Quantum Orchestrator Autonomous Prompts

This directory contains a sequence of autonomous prompts for iterative development and enhancement of the Quantum-Relativistic-Dirac Orchestrator framework.

## Prompt Sequence

| #  | Prompt File | Objective | Status |
|----|-------------|-----------|--------|
| 00 | `00_foundation.prompt.md` | Verify foundation and imports | ✅ Complete |
| 01 | `01_extend_operators.prompt.md` | Add Klein-Gordon operator | ⏭️ Optional |
| 02 | `02_conservation.prompt.md` | Enhance conservation checking | 🎯 Recommended |
| 03 | `03_testing.prompt.md` | Expand test coverage | 🎯 Recommended |
| 04 | `04_optimization.prompt.md` | Performance optimization | ⏭️ Optional |
| 05 | `05_autonomous.prompt.md` | Self-improvement loop | 🎯 Recommended |

## Usage

### Sequential Execution

Execute prompts in order:

```bash
# Prompt 00: Foundation
cat .github/prompts/00_foundation.prompt.md

# Follow instructions in prompt
# Then proceed to next...

# Prompt 01: Operators
cat .github/prompts/01_extend_operators.prompt.md

# And so on...
```

### With Copilot

Use with GitHub Copilot:

```
@copilot Execute prompt .github/prompts/00_foundation.prompt.md
```

### Standalone

Each prompt is self-contained and includes:
- Objective
- Prerequisites
- Implementation details
- Testing instructions
- Verification commands
- Success criteria
- Next steps

## Current Implementation Status

✅ **Foundation (Prompt 00)**
- All core classes implemented
- Schrödinger dynamics working
- Dirac equation implemented
- 28/28 tests passing

✅ **Testing (Partial Prompt 03)**
- Physics validation tests complete
- Integration tests pending
- Performance benchmarks pending

⏳ **Conservation (Prompt 02)**
- Basic `verify_conservation()` implemented
- Leak detection pending
- Auto-repair pending

⏳ **Optimization (Prompt 04)**
- Baseline performance acceptable (~50 iter/sec for 100 tasks)
- Vectorization pending
- Spatial indexing pending

⏳ **Autonomous (Prompt 05)**
- Framework ready
- Monitoring system pending
- Auto-improvement loop pending

## Adding New Prompts

To add a new prompt in the sequence:

1. Create `06_your_feature.prompt.md`
2. Follow the template:

```markdown
# Feature Name

> **Prompt**: 06_your_feature.prompt.md  
> **Previous**: 05_autonomous.prompt.md  
> **Next**: 07_next_feature.prompt.md  
> **Prerequisites**: List prerequisites

---

## Objective

Clear objective statement

## Tasks

Detailed implementation tasks

## Testing

Test instructions

## Success Criteria

- [ ] Criterion 1
- [ ] Criterion 2

## Next Steps

Link to next prompt
```

3. Update this README
4. Update previous prompt's "Next" link

## Verification Commands

Quick verification of current state:

```bash
# Test imports
PYTHONPATH=src:$PYTHONPATH python3 -c "from codex.quantum_orchestrator import create_orchestrator; print('✓')"

# Run tests
PYTHONPATH=src:$PYTHONPATH pytest tests/quantum_orchestrator/ -v --no-cov

# Run demo
PYTHONPATH=src:$PYTHONPATH python3 examples/quantum_orchestrator_demo.py
```

## Development Workflow

1. **Read prompt** - Understand objective and tasks
2. **Implement** - Follow implementation details
3. **Test** - Run verification commands
4. **Validate** - Check success criteria
5. **Next** - Proceed to next prompt

## Notes

- Prompts marked ⏭️ Optional can be skipped
- Prompts marked 🎯 Recommended should be completed
- Each prompt builds on previous ones
- Tests must pass before proceeding
- Document any deviations in prompt file

## Support

For questions or issues:
- Review the main README: `docs/quantum_orchestrator_README.md`
- Check test results for clues
- Review implementation in `src/codex/quantum_orchestrator/`

---

**Status**: Prompt sequence established ✅  
**Next Action**: Execute Prompt 02 (Conservation enhancement)
