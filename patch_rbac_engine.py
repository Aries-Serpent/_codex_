import sys
import yaml

content = open('scripts/governance/rbac_engine.py').read()

new_imports = """
import yaml
import os
import re

class PolicyEnforcer:
    def __init__(self, rules_path=".codex/rbac_adaptive_rules.yaml"):
        self.rules = []
        if os.path.exists(rules_path):
            with open(rules_path, 'r') as f:
                data = yaml.safe_load(f)
                if data and 'adaptive_rules' in data:
                    self.rules = data['adaptive_rules']

    def evaluate(self, action_val: str, resource_val: str, ooda_context) -> str:
        # Returns 'require_both', 'require', 'grant_auto', or None
        
        ctx_vars = {
            'ooda_context.confidence': ooda_context.confidence,
            'ooda_context.risk_score': ooda_context.risk_score,
            'ooda_context.incident_id': ooda_context.incident_id,
            'incident_severity': getattr(ooda_context, 'incident_severity', 'LOW'),
            'ooda_context.pattern_match': ooda_context.pattern_match,
            'action': action_val,
            'resource': resource_val,
            'None': None
        }
        
        def eval_condition(cond_str):
            # very naive evaluator for the specific rules we have
            c = cond_str.replace("==", "==").replace("=", "==").replace("AND", "and").replace("OR", "or")
            try:
                return eval(c, {}, ctx_vars)
            except Exception as e:
                return False
                
        def eval_rule_lines(rules_list):
            for r in rules_list:
                try:
                    res = eval(r, {}, ctx_vars)
                    if not res: return False
                except Exception as e:
                    return False
            return True

        for rule in self.rules:
            cond = rule.get('condition', '')
            if eval_condition(cond):
                if eval_rule_lines(rule.get('rule', [])):
                    return rule.get('action')
                else:
                    return f"DENY:{rule.get('name')}"
        return None
"""

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
            # These rules act as a gate; if they pass, we fall back to normal RBAC
            return True
            
        # Example hardcoded rules as fallback if enforcer didn't match
        if action == Action.DELEGATE:
            if ooda_context.confidence < 0.95:
                return False
            if ooda_context.risk_score > 0.3:
                return False
            return True

        return False"""

# Add imports
content = content.replace("import time", "import time\n" + new_imports)

# Replace _check_ooda_rules
import re
content = re.sub(
    r'    def _check_ooda_rules\(.*?(?=    # ={72})',
    new_ooda_check + '\n\n',
    content,
    flags=re.DOTALL | re.MULTILINE
)

open('scripts/governance/rbac_engine.py', 'w').read()
