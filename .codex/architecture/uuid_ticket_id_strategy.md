# ADR: UUID-to-Integer Ticket ID Conversion Strategy

**Status**: Accepted  
**Date**: 2026-01-10  
**Deciders**: Engineering Team, Security Team  
**Related**: PS-05 Enhancement (Scope Validation Integration)

## Context

The quantum orchestrator system (`src.quantum.orchestrator.ThermodynamicOrchestrator`) uses integer-based task IDs for tracking thermodynamic tasks. The Zendesk integration module needs to create tickets with globally unique identifiers that work across distributed systems without coordination, while maintaining compatibility with the integer-based orchestrator API.

## Decision

We have decided to use UUID v4 for ticket ID generation and convert them to 128-bit integers for compatibility with the quantum orchestrator.

### Implementation

```python
# Generate UUID and convert to 128-bit integer
ticket_uuid = uuid.uuid4()
ticket_id = ticket_uuid.int  # Returns 128-bit integer (0 to 2^128-1)
```

The conversion is implemented in `src/codex/zendesk/quantum/orchestrator.py` in the `create_ticket_with_scope_check()` method.

## Rationale

### Advantages

1. **Global Uniqueness**: UUIDs provide collision-free identifiers across distributed systems
2. **No Coordination Required**: Can generate IDs offline without database access
3. **Cryptographic Randomness**: UUID v4 uses secure random number generation
4. **Preserves Uniqueness**: 128-bit integer conversion maintains UUID's uniqueness guarantee
5. **API Compatibility**: Integer format works with existing orchestrator methods

### Trade-offs

1. **Large Integer Size**: 128-bit integers may exceed limits of:
   - 64-bit database integer columns
   - JSON number precision in some parsers
   - Display in fixed-width UI fields
   
2. **Human Readability**: 128-bit integers are not human-friendly in logs/UIs
   - Example: `123456789012345678901234567890123456`
   
3. **Sorting Semantics**: Unlike sequential IDs, UUIDs provide no temporal ordering

## Alternatives Considered

### Alternative 1: Sequential Integer IDs

**Rejected** - Requires database coordination for uniqueness, doesn't scale across distributed systems

```python
# Anti-pattern: Coordination required
ticket_id = database.get_next_ticket_id()  # Single point of failure
```

### Alternative 2: 64-bit Hash of UUID

**Rejected** - Introduces collision risk, defeats UUID's uniqueness guarantee

```python
# Anti-pattern: Potential collisions
ticket_id = hash(uuid.uuid4()) & 0xFFFFFFFFFFFFFFFF  # Only 64 bits
```

### Alternative 3: String UUIDs Throughout

**Rejected** - Requires changing the quantum orchestrator's API, broader refactoring

```python
# Would require API changes
orchestrator.submit_task(task_id="550e8400-e29b-41d4-a716-446655440000")
```

## Migration Strategy

For systems that cannot handle 128-bit integers:

### Option A: Mapping Layer (Recommended)

Maintain a bidirectional mapping between UUIDs and sequential IDs:

```python
class TicketIDMapper:
    """Maps between UUID and sequential ID for system compatibility."""
    
    def uuid_to_display_id(self, ticket_uuid: uuid.UUID) -> int:
        """Get or create sequential ID for display."""
        # Store mapping in database
        return self.db.get_or_create_sequential_id(ticket_uuid)
    
    def display_id_to_uuid(self, display_id: int) -> uuid.UUID:
        """Resolve display ID to original UUID."""
        return self.db.lookup_uuid(display_id)
```

### Option B: Truncated Display IDs

Show shortened versions in UI while storing full UUID:

```python
def format_ticket_id_for_display(ticket_id: int) -> str:
    """Format ticket ID for human-readable display."""
    # Show last 8 hex digits with prefix
    return f"TKT-{ticket_id & 0xFFFFFFFF:08X}"
    # Example output: TKT-A7B3C9D1
```

### Option C: Database Schema Update

Store both UUID and integer representations:

```sql
CREATE TABLE tickets (
    ticket_uuid UUID PRIMARY KEY,
    ticket_int_id NUMERIC(39, 0),  -- 128-bit integer
    ticket_display_id BIGINT GENERATED ALWAYS AS IDENTITY,
    -- other columns...
);
```

## Consequences

### Positive

- ✅ Globally unique IDs without coordination
- ✅ Compatible with existing integer-based APIs
- ✅ Suitable for distributed/microservices architecture
- ✅ No database locking for ID generation
- ✅ Cryptographically secure randomness

### Negative

- ❌ Requires migration strategy for 64-bit systems
- ❌ Less human-readable than sequential IDs
- ❌ No temporal ordering from ID alone
- ❌ Increased storage size (128-bit vs 64-bit)

### Neutral

- ⚠️ Need to document ID format expectations in API contracts
- ⚠️ UI/UX team needs guidance on ID display formatting
- ⚠️ Consider adding created_at timestamp for temporal queries

## Implementation Checklist

- [x] Implement UUID-to-integer conversion in quantum orchestrator adapter
- [x] Document design decision in module docstring
- [x] Create this ADR document for reference
- [ ] Add display formatting utility for UI rendering
- [ ] Update API documentation with ID format specification
- [ ] Consider creating TicketIDMapper if 64-bit systems needed
- [ ] Add monitoring for ID collision detection (should never occur)

## References

- RFC 4122: A Universally Unique IDentifier (UUID) URN Namespace
- Python uuid module: https://docs.python.org/3/library/uuid.html
- Integer conversion: `uuid.UUID.int` property documentation
- Related module: `src/codex/zendesk/quantum/orchestrator.py`

## Review History

- 2026-01-10: Initial ADR created during code review feedback resolution
- Next Review: After 6 pre-commit cycles or when migrating to production at scale

---

**Maintainers**: @engineering-team @security-team  
**Last Updated**: 2026-01-10  
**Commit SHA**: (to be added upon commit)
