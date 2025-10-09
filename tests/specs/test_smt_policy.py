from __future__ import annotations

import pytest

try:
    import z3  # type: ignore
except Exception:  # pragma: no cover
    z3 = None  # type: ignore


@pytest.mark.skipif(z3 is None, reason="z3-solver not installed")
def test_policy_scenarios():
    s = z3.Solver()
    online, host = z3.Bool("online_allowlist"), z3.Bool("host_allowlisted")
    admin_perms = z3.Bool("admin_perms")
    ro, adm = z3.Bool("action_readonly"), z3.Bool("action_admin")
    admissible = z3.And(online, host, z3.Or(ro, z3.And(adm, admin_perms)))

    # Read-only path OK
    s.push()
    s.add(online, host, ro, z3.Not(adm))
    assert s.check() == z3.sat
    s.pop()

    # Admin without perms should require admissible=false to be sat
    s.push()
    s.add(online, host, adm, z3.Not(admin_perms), z3.Not(ro), z3.Not(admissible))
    assert s.check() == z3.sat
    s.pop()

    # Admin with perms and admissible true
    s.push()
    s.add(online, host, adm, admin_perms, admissible)
    assert s.check() == z3.sat
    s.pop()