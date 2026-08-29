import re

with open('scripts/governance/rbac_engine.py', 'r') as f:
    content = f.read()

new_imports = """
import yaml
import os

class PolicyEnforcer:
    def __init__(self, rules_path=".codex/rbac_adaptive_rules.yaml"):
        self.rules = []
        if os.path.exists(rules_path):
            with open(rules_path, 'r') as f:
                data = yaml.safe_load(f)
                if data and 'adaptive_rules' in data:
                    self.rules = data['adaptive_rules']

    def evaluate(self, action_val: str, resource_val: str, ooda_context) -> str:
        ctx_vars = {
            'ooda_context': ooda_context,
            'action': action_val,
            'resource': resource_val,
            'incident_severity': getattr(ooda_context, 'incident_severity', 'LOW'),
            'None': None
        }
        
        def safe_eval(expr):
            expr = expr.replace("AND", "and").replace("OR", "or")
            try:
                return eval(expr, {"__builtins__": {}}, ctx_vars)
            except Exception:
                return False

        for rule in self.rules:
            cond = rule.get('condition', '')
            if safe_eval(cond):
                # Check rules
                rule_lines = rule.get('rule', [])
                all_passed = True
                for r in rule_lines:
                    if not safe_eval(r):
                        all_passed = False
                        break
                
                if all_passed:
                    return rule.get('action')
                else:
                    return f"DENY:{rule.get('name')}"
        return None
"""

content = content.replace("import time\n", "import time\n" + new_imports + "\n")

new_ooda_check = """    def _check_ooda_rules(
        self, principal_id: str, action: Action, resource: ResourceType, ooda_context: OODAContext
    ) -> bool:
        \"\"\"Check OODA-driven adaptive rules.\"\"\"
        if not hasattr(self, '_policy_enforcer'):
            self._policy_enforcer = PolicyEnforcer()
            
        result = self._policy_enforcer.evaluate(action.value, resource.value, ooda_context)
        
        if result and result.startswith("DENY"):
            logger.warning(f"OODA Policy denied action: {result}")
            return False
            
        if result == "grant_auto":
            return True
            
        if result in ("require_both", "require"):
            return True
            
        if action == Action.DELEGATE:
            if ooda_context.confidence < 0.95:
                return False
            if ooda_context.risk_score > 0.3:
                return False
            return True

        return False"""

content = re.sub(
    r'    def _check_ooda_rules\(.*?(?=    # ={72}\n    # Delegation)',
    new_ooda_check + '\n\n',
    content,
    flags=re.DOTALL | re.MULTILINE
)

with open('scripts/governance/rbac_engine.py', 'w') as f:
    f.write(content)

print("Patched successfully")
