# Phase 7A Lane 3.2: Detailed Mutation Execution Schedule

**Campaign:** Production deployment readiness (7-day intensive)  
**Prepared:** 2026-06-19T08:30Z (Day 1)  
**Strategy:** Sequential module testing with parallel test enhancement

---

## PRIORITY 1 MODULE: agents/agent_memory.py

**Status:** Ready for mutation testing  
**Module Size:** 1,336 lines  
**Complexity:** HIGH (memory persistence, pattern matching)

### Test Inventory
- Main tests: 76 tests (test_agent_memory.py)
- Comprehensive tests: 60 tests (test_agent_memory_comprehensive.py)
- Mutation killers: 48 tests (test_agent_memory_mutation_killers.py)
- **Total Available:** 184 tests

### Estimated Mutations
- **Conservative Estimate:** 150-180 mutants
- **Aggressive Estimate:** 200-250 mutants
- **High-Value Mutations:**
  - Boundary conditions (>, >=, <, <=): ~30-40 mutants
  - Boolean logic (and/or, True/False): ~25-35 mutants
  - Return values (return x → return not x): ~20-30 mutants
  - Numeric operations (+,-,*,/): ~20-30 mutants
  - String/literal mutations: ~20-30 mutants

### Key Classes to Target
| Class | Methods | Complexity | Est. Mutations | Critical Methods |
|-------|---------|-----------|----------------|-----------------|
| AgentMemory | 17 | HIGH | 80-100 | store_memory, retrieve_memory, search_memories |
| AgentMemorySystem | 13 | HIGH | 40-50 | start_task, record_decision, record_lesson |
| PatternLibrary | 6 | MEDIUM | 20-30 | add_pattern, match_patterns |
| MemoryEntry | 2 | LOW | 10-15 | to_dict, from_dict |
| ContextFrame | 1 | LOW | 5-10 | to_dict |

### Execution Timeline

**Phase 1: Baseline Run** (2-3 hours)
- Generate all mutants for agent_memory.py
- Run full test suite against mutants
- Calculate baseline kill rate
- Identify surviving mutants

**Phase 2: Test Analysis** (1-2 hours)
- Group surviving mutants by mutation type
- Identify patterns in untested code paths

**Phase 3: Test Strengthening** (2-4 hours)
- Add boundary condition tests
- Add explicit branch tests
- Add exception handling tests

**Phase 4: Mutation Re-run** (2-3 hours)
- Re-run mutation tests
- Verify improvement

**Total Time: 8-12 hours**

### Expected Score Trajectory
- **Initial Baseline:** 60-65% kill rate
- **After Phase 4:** 70-75% kill rate
- **Target Improvement:** +10pp

---

## CRITICAL MUTATION PATTERNS

### Pattern 1: Boundary Mutations
```python
# Original: if count >= min_count:
# Mutant: if count > min_count:
# Test Strategy: Test exact boundary value
```

### Pattern 2: Return Value Mutations
```python
# Original: return is_valid
# Mutant: return not is_valid
# Test Strategy: Explicit equality assertions
```

### Pattern 3: Boolean Logic Mutations
```python
# Original: if condition_a and condition_b:
# Mutant: if condition_a or condition_b:
# Test Strategy: Test each condition separately
```

### Pattern 4: Exception Mutations
```python
# Original: if bad: raise ValueError()
# Mutant: if bad: pass
# Test Strategy: pytest.raises context manager
```

### Pattern 5: Numeric Mutations
```python
# Original: counter += 1
# Mutant: counter += 0
# Test Strategy: Explicit numeric assertions
```

---

## DAILY EXECUTION PLAN

### Day 2 (2026-06-20)
- **Morning (09:00-12:00Z):** Run baseline mutations on agent_memory.py
- **Afternoon (12:00-18:00Z):** Analyze surviving mutants, queue test improvements
- **Evening (18:00-21:00Z):** Implement new tests, verify kills
- **Target Score:** 64-65%

### Day 3 (2026-06-21)
- **Morning:** Complete agent_memory.py enhancements, finalize score
- **Afternoon:** Start mutations on mental_mapping.py
- **Evening:** Analyze mental_mapping results
- **Target Score:** 67-68%

### Day 4 (2026-06-22)
- **Morning-Afternoon:** Complete mental_mapping.py enhancements
- **Afternoon:** Start cognitive_adapter.py mutations
- **Evening:** Continue test strengthening
- **Target Score:** 69-70%

### Day 5 (2026-06-23)
- **Priority 2 Completion:** Finalize cognitive_adapter.py
- **Begin Priority 3:** Start on developer_orchestrator.py or workflow_navigator.py
- **Target Score:** 70-72%

### Days 6-7
- **Priority 3-4:** Finalize remaining modules
- **Final Validation:** Run comprehensive mutation suite
- **Documentation:** Generate final report
- **Target Score:** 75%+

---

## SUCCESS CRITERIA (Per Module)

### agent_memory.py (Days 1-2)
- [ ] 150+ mutations generated
- [ ] >100 mutations killed
- [ ] Surviving mutants documented
- [ ] >5 new tests added

### mental_mapping.py (Days 2-3)
- [ ] 120+ mutations generated
- [ ] >80 mutations killed
- [ ] Score improvement tracked

### cognitive_adapter.py (Days 3-4)
- [ ] 40+ mutations generated
- [ ] 30+ mutations killed
- [ ] Module integration verified

---

**Prepared by:** mutation-testing-agent  
**Authority:** @mbaetiong  
**Next Checkpoint:** Day 2 (09:00Z 2026-06-20)
