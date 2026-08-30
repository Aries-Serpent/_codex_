from scripts.governance.rbac_engine import RBACEngine, OODAContext, Action, ResourceType
engine = RBACEngine()
ctx = OODAContext(decision_history=[], pattern_match="safe_pattern", risk_score=0.1, confidence=0.99)
print(engine._check_ooda_rules("alice", Action.APPROVE, ResourceType.AGENTS, ctx))
