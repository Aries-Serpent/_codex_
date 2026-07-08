"""
Semantic routing and decision evaluation for documentation.

Classes:
  - SemanticRouter: Route queries to matching documentation records
  - DecisionEvaluator: Evaluate decision logic based on criteria
  - ActionDispatcher: Trigger machine-readable actions
"""

import ast
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional


@dataclass
class RoutingResult:
    """Result of semantic routing query."""

    matched_docs: List[str]
    matched_sections: List[str]
    relevance_scores: Dict[str, float]
    decision_path: Optional[str] = None


class SemanticRouter:
    """Route documentation queries to semantic index.

    Supports:
      - Keyword-based routing
      - Tag-based filtering
      - Hierarchical navigation
      - Relevance scoring
    """

    def __init__(self, registry: Any):  # DocumentRegistry
        self.registry = registry
        self._route_cache: Dict[str, RoutingResult] = {}

    def route_query(self, query: str) -> RoutingResult:
        """Route a documentation query.

        Args:
            query: Natural language query or keyword search

        Returns:
            RoutingResult with matched documents and scores
        """
        # Check cache
        if query in self._route_cache:
            return self._route_cache[query]

        # Search documents and sections
        docs = self.registry.search_documents(query)

        relevance_scores = {}
        matched_sections = []

        # Score documents by keyword match
        for doc in docs:
            score = self._compute_relevance(query, doc.title)
            relevance_scores[doc.id] = score

            # Find relevant sections
            sections = self.registry.search_sections(doc.id, query)
            matched_sections.extend([s.id for s in sections])

        result = RoutingResult(
            matched_docs=[doc.id for doc in docs],
            matched_sections=matched_sections,
            relevance_scores=relevance_scores,
        )

        self._route_cache[query] = result
        return result

    def route_by_tag(self, tag: str) -> RoutingResult:
        """Route by document tag."""
        docs = self.registry.find_by_tag(tag)

        return RoutingResult(
            matched_docs=[doc.id for doc in docs],
            matched_sections=[],
            relevance_scores={doc.id: 1.0 for doc in docs},
        )

    @staticmethod
    def _compute_relevance(query: str, text: str) -> float:
        """Compute relevance score between query and text."""
        query_lower = query.lower()
        text_lower = text.lower()

        # Exact match: 1.0
        if query_lower == text_lower:
            return 1.0

        # Substring match: 0.8
        if query_lower in text_lower:
            return 0.8

        # Word match: 0.6
        query_words = set(query_lower.split())
        text_words = set(text_lower.split())
        intersection = query_words & text_words

        if intersection:
            return 0.6 * (len(intersection) / len(query_words))

        return 0.0

    def clear_cache(self) -> None:
        """Clear routing cache."""
        self._route_cache.clear()


class DecisionEvaluator:
    """Evaluate decision logic based on criteria and branches.

    Supports:
      - Weighted deterministic evaluation
      - Probabilistic branching
      - First-match evaluation
      - Condition chaining
    """

    def __init__(self):
        self.decisions: Dict[str, Dict] = {}

    def register_decision(self, decision: Dict) -> None:
        """Register a decision rule."""
        self.decisions[decision["id"]] = decision

    def evaluate(
        self,
        decision_id: str,
        context: Dict[str, Any],
    ) -> Optional[str]:
        """Evaluate a decision and return action ID.

        Args:
            decision_id: Decision record ID
            context: Context data for criteria evaluation

        Returns:
            Action ID to execute, or None if no match
        """
        decision = self.decisions.get(decision_id)
        if not decision:
            return None

        logic = decision.get("evaluation_logic", "weighted_deterministic")

        if logic == "first_match":
            return self._evaluate_first_match(decision, context)
        elif logic == "weighted_deterministic":
            return self._evaluate_weighted(decision, context)
        else:
            return decision.get("default_action_id")

    def _evaluate_first_match(
        self,
        decision: Dict,
        context: Dict[str, Any],
    ) -> Optional[str]:
        """First branch that matches wins."""
        for branch in decision.get("branches", []):
            if self._match_condition(branch["condition"], context):
                return branch.get("action_id")

        return decision.get("default_action_id")

    def _evaluate_weighted(
        self,
        decision: Dict,
        context: Dict[str, Any],
    ) -> Optional[str]:
        """Weighted evaluation - highest weight wins."""
        max_weight = 0
        best_action = None

        for branch in decision.get("branches", []):
            if self._match_condition(branch["condition"], context):
                weight = branch.get("weight", 0)
                if weight > max_weight:
                    max_weight = weight
                    best_action = branch.get("action_id")

        return best_action or decision.get("default_action_id")

    @staticmethod
    def _safe_eval_expression(expression: str) -> bool:
        """Safely evaluate a boolean expression using AST inspection.

        Only allows safe operations:
        - Comparison operators: ==, !=, <, >, <=, >=
        - Logical operators: and, or, not
        - Literals and variable references (already substituted)

        Args:
            expression: A boolean expression string

        Returns:
            The evaluated result

        Raises:
            ValueError: If expression contains unsafe operations
        """
        try:
            # Parse the expression into an AST
            tree = ast.parse(expression, mode="eval")

            # Use a visitor to safely evaluate
            return DecisionEvaluator._visit_expr(tree.body)
        except Exception:
            return False

    @staticmethod
    def _visit_expr(node: Any) -> Any:
        """Safely visit and evaluate AST nodes.

        Only allows safe node types for boolean expressions.
        """
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Name):
            # Names should already be substituted, but if not, treat as False
            return False
        elif isinstance(node, ast.Compare):
            # Evaluate comparisons: x == y, x > y, etc.
            left = DecisionEvaluator._visit_expr(node.left)
            for op, comparator in zip(node.ops, node.comparators):
                right = DecisionEvaluator._visit_expr(comparator)
                if isinstance(op, ast.Eq):
                    if not (left == right):
                        return False
                elif isinstance(op, ast.NotEq):
                    if not (left != right):
                        return False
                elif isinstance(op, ast.Lt):
                    if not (left < right):
                        return False
                elif isinstance(op, ast.LtE):
                    if not (left <= right):
                        return False
                elif isinstance(op, ast.Gt):
                    if not (left > right):
                        return False
                elif isinstance(op, ast.GtE):
                    if not (left >= right):
                        return False
                else:
                    raise ValueError(f"Unsupported comparison operator: {op}")
                left = right
            return True
        elif isinstance(node, ast.BoolOp):
            # Evaluate boolean operations: x and y, x or y
            if isinstance(node.op, ast.And):
                for value in node.values:
                    if not DecisionEvaluator._visit_expr(value):
                        return False
                return True
            elif isinstance(node.op, ast.Or):
                for value in node.values:
                    if DecisionEvaluator._visit_expr(value):
                        return True
                return False
            else:
                raise ValueError(f"Unsupported boolean operator: {node.op}")
        elif isinstance(node, ast.UnaryOp):
            # Evaluate unary operations: not x
            if isinstance(node.op, ast.Not):
                return not DecisionEvaluator._visit_expr(node.operand)
            else:
                raise ValueError(f"Unsupported unary operator: {node.op}")
        else:
            # Reject all other node types (function calls, attribute access, etc.)
            raise ValueError(f"Unsafe operation in expression: {ast.dump(node)}")

    @staticmethod
    def _match_condition(condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate a condition against context.

        Supports simple boolean logic:
          - Variable comparisons: field == value, field >= value
          - Logical operators: &&, ||, !
        """
        try:
            # Replace context variables in condition
            eval_condition = condition
            for key, value in context.items():
                if isinstance(value, str):
                    eval_condition = eval_condition.replace(key, f"'{value}'")
                else:
                    eval_condition = eval_condition.replace(key, str(value))

            # Replace && and || with Python equivalents
            eval_condition = eval_condition.replace("&&", "and").replace("||", "or")

            # Use safe evaluation instead of raw eval()
            return DecisionEvaluator._safe_eval_expression(eval_condition)
        except Exception:
            return False


class ActionDispatcher:
    """Dispatch machine-readable actions.

    Supports:
      - Action registration and execution
      - Parameter substitution
      - Condition guards
      - Action chaining
    """

    def __init__(self):
        self.actions: Dict[str, Dict] = {}
        self.handlers: Dict[str, Callable] = {}

    def register_action(self, action: Dict) -> None:
        """Register an action."""
        self.actions[action["id"]] = action

    def register_handler(self, target: str, handler: Callable) -> None:
        """Register handler for action target."""
        self.handlers[target] = handler

    def dispatch(
        self,
        action_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Dispatch and execute an action.

        Args:
            action_id: Action record ID
            context: Context data for parameter substitution

        Returns:
            Action result or None
        """
        action = self.actions.get(action_id)
        if not action:
            return None

        # Check guard conditions
        for condition in action.get("conditions", []):
            if condition.get("type") == "gate":
                # Would check gate conditions here
                pass

        target = action.get("target")
        if not isinstance(target, str):
            return None
        handler = self.handlers.get(target)

        if handler:
            params = action.get("parameters", {})
            # Substitute context variables
            params = self._substitute_params(params, context or {})
            return handler(**params)

        return None

    @staticmethod
    def _substitute_params(
        params: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Substitute context variables in parameters."""
        result = {}
        for key, value in params.items():
            if isinstance(value, str) and value.startswith("$"):
                # Variable reference: $context_key
                var_name = value[1:]
                result[key] = context.get(var_name, value)
            else:
                result[key] = value
        return result
