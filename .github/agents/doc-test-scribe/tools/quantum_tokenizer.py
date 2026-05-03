"""
Quantum-Inspired Tokenization for Doc-Test-Scribe

Leverages quantum physics principles from the cognitive brain for effective
tokenization of variables, values, and code structures.

Quantum Principles Applied:
1. **Superposition**: Variables exist in multiple semantic states simultaneously
2. **Entanglement**: Related variables/values are correlated
3. **Uncertainty**: Balance between precision and coverage
4. **Wave Function Collapse**: Resolve ambiguity to concrete meanings

Mathematical Foundation:
- State Vector: |ψ⟩ = Σᵢ αᵢ|token_i⟩
- Amplitude: αᵢ = semantic_weight(token_i)
- Probability: P(token_i) = |αᵢ|²
- Entanglement: C(token_i, token_j) = ⟨token_i|token_j⟩

Author: @copilot
Version: 1.0.0
Date: 2026-01-17
"""

import ast
import math
import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Set, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


@dataclass
class QuantumToken:
    """
    Represents a token in quantum superposition.

    A token can represent multiple semantic meanings simultaneously
    until "observed" (used in a specific context), at which point
    the wave function collapses to a concrete meaning.

    Attributes:
        value: The token string (variable name, literal, etc.)
        type: Token type (var, func, class, literal, keyword)
        amplitudes: Probability amplitudes for each semantic state
        semantic_states: Possible semantic meanings
        entangled_with: Set of tokens this is entangled with
        position: Location in source code (line, col)
        context: Surrounding code context
    """
    value: str
    type: str
    amplitudes: Dict[str, float] = field(default_factory=dict)
    semantic_states: List[str] = field(default_factory=list)
    entangled_with: Set[str] = field(default_factory=set)
    position: Tuple[int, int] = (0, 0)
    context: str = ""

    def __post_init__(self):
        """Initialize amplitudes with equal superposition."""
        if not self.amplitudes and self.semantic_states:
            n = len(self.semantic_states)
            amplitude = 1.0 / math.sqrt(n)
            self.amplitudes = {state: amplitude for state in self.semantic_states}

    @property
    def probabilities(self) -> Dict[str, float]:
        """Get probability distribution (|α|²)."""
        return {state: abs(amp)**2 for state, amp in self.amplitudes.items()}

    @property
    def dominant_state(self) -> str:
        """Get most probable semantic state (wave function collapse)."""
        if not self.probabilities:
            return "unknown"
        return max(self.probabilities.items(), key=lambda x: x[1])[0]

    def collapse(self, observed_state: str) -> None:
        """
        Collapse wave function to observed state.

        When a token is used in a specific context, its semantic
        ambiguity resolves to a concrete meaning.
        """
        self.amplitudes = {observed_state: 1.0}
        self.semantic_states = [observed_state]

    def measure_uncertainty(self) -> float:
        """
        Calculate Shannon entropy (uncertainty measure).

        Returns:
            Entropy in bits. Higher = more uncertain.
        """
        probs = list(self.probabilities.values())
        if not probs:
            return 0.0

        return -sum(p * math.log2(p) if p > 0 else 0 for p in probs)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'value': self.value,
            'type': self.type,
            'semantic_states': self.semantic_states,
            'probabilities': self.probabilities,
            'dominant_state': self.dominant_state,
            'uncertainty': self.measure_uncertainty(),
            'entangled_with': list(self.entangled_with),
            'position': self.position,
        }


@dataclass
class EntangledPair:
    """
    Represents entanglement between two tokens.

    Entangled tokens are semantically correlated - observing one
    provides information about the other.

    Examples:
    - Function name ↔ return type
    - Variable name ↔ variable type
    - Parameter name ↔ parameter usage
    """
    token1: str
    token2: str
    correlation: float  # Correlation coefficient (-1 to 1)
    relationship: str  # "defines", "uses", "returns", "param_of"
    confidence: float  # Confidence in entanglement (0 to 1)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'token1': self.token1,
            'token2': self.token2,
            'correlation': self.correlation,
            'relationship': self.relationship,
            'confidence': self.confidence,
        }


class QuantumTokenizer:
    """
    Quantum-inspired tokenizer for code analysis.

    Uses principles from cognitive_brain.quantum:
    - Superposition for ambiguous semantics
    - Entanglement for variable relationships
    - Uncertainty for coverage/precision tradeoffs

    Example:
        >>> tokenizer = QuantumTokenizer()
        >>> tokens = tokenizer.tokenize(source_code)
        >>> entanglements = tokenizer.find_entanglements(tokens)
        >>> semantic_map = tokenizer.build_semantic_map(tokens)
    """

    def __init__(
        self,
        uncertainty_threshold: float = 0.5,
        entanglement_threshold: float = 0.7
    ):
        """
        Initialize quantum tokenizer.

        Args:
            uncertainty_threshold: Max allowed entropy (bits)
            entanglement_threshold: Min correlation for entanglement
        """
        self.uncertainty_threshold = uncertainty_threshold
        self.entanglement_threshold = entanglement_threshold
        self.tfidf = TfidfVectorizer(ngram_range=(1, 2))
        self._fitted = False

    def tokenize(self, source_code: str) -> List[QuantumToken]:
        """
        Tokenize source code into quantum tokens.

        Process:
        1. Parse AST to extract structural tokens
        2. Assign semantic states to each token
        3. Initialize superposition (equal amplitudes)
        4. Extract context for each token

        Args:
            source_code: Python source code string

        Returns:
            List of quantum tokens in superposition
        """
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            # Fallback to regex-based tokenization
            return self._tokenize_fallback(source_code)

        tokens = []

        # Extract variables
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                token = self._create_variable_token(node, source_code)
                tokens.append(token)

            elif isinstance(node, ast.FunctionDef):
                token = self._create_function_token(node, source_code)
                tokens.append(token)

            elif isinstance(node, ast.ClassDef):
                token = self._create_class_token(node, source_code)
                tokens.append(token)

            elif isinstance(node, (ast.Constant, ast.Str, ast.Num)):
                token = self._create_literal_token(node, source_code)
                tokens.append(token)

        return tokens

    def _create_variable_token(
        self,
        node: ast.Name,
        source: str
    ) -> QuantumToken:
        """Create quantum token for variable."""
        var_name = node.id

        # Infer possible semantic states from naming
        semantic_states = self._infer_semantic_states_from_name(var_name)

        # Extract context
        context = self._extract_context(node, source)

        return QuantumToken(
            value=var_name,
            type='variable',
            semantic_states=semantic_states,
            position=(getattr(node, 'lineno', 0), getattr(node, 'col_offset', 0)),
            context=context
        )

    def _create_function_token(
        self,
        node: ast.FunctionDef,
        source: str
    ) -> QuantumToken:
        """Create quantum token for function."""
        func_name = node.name

        # Infer semantic states
        semantic_states = self._infer_semantic_states_from_name(func_name)
        semantic_states.append('callable')

        # Extract context (docstring, params, return)
        context = self._extract_function_context(node, source)

        return QuantumToken(
            value=func_name,
            type='function',
            semantic_states=semantic_states,
            position=(node.lineno, node.col_offset),
            context=context
        )

    def _create_class_token(
        self,
        node: ast.ClassDef,
        source: str
    ) -> QuantumToken:
        """Create quantum token for class."""
        class_name = node.name

        # Classes are types
        semantic_states = ['type', 'class', 'object']

        # Add specific semantics from name
        if class_name.endswith('Error') or class_name.endswith('Exception'):
            semantic_states.append('exception')
        elif class_name.endswith('Manager'):
            semantic_states.append('manager')
        elif class_name.endswith('Provider'):
            semantic_states.append('provider')

        context = self._extract_class_context(node, source)

        return QuantumToken(
            value=class_name,
            type='class',
            semantic_states=semantic_states,
            position=(node.lineno, node.col_offset),
            context=context
        )

    def _create_literal_token(
        self,
        node: ast.AST,
        source: str
    ) -> QuantumToken:
        """Create quantum token for literal value."""
        if isinstance(node, ast.Constant):
            value = str(node.value)
        elif isinstance(node, ast.Str):
            value = node.s
        elif isinstance(node, ast.Num):
            value = str(node.n)
        else:
            value = "unknown"

        # Infer semantic type
        semantic_states = []
        if isinstance(node, (ast.Str, ast.Constant)) and isinstance(node.value if hasattr(node, 'value') else None, str):
            semantic_states = ['string', 'text']
        elif isinstance(node, (ast.Num, ast.Constant)) and isinstance(node.value if hasattr(node, 'value') else None, (int, float)):
            semantic_states = ['number', 'numeric']

        return QuantumToken(
            value=value[:50],  # Truncate long literals
            type='literal',
            semantic_states=semantic_states or ['literal'],
            position=(getattr(node, 'lineno', 0), getattr(node, 'col_offset', 0)),
            context=""
        )

    def _infer_semantic_states_from_name(self, name: str) -> List[str]:
        """
        Infer semantic states from variable/function name.

        Uses naming patterns to create superposition of possible meanings.
        """
        states = []

        # Common prefixes
        if name.startswith('is_') or name.startswith('has_'):
            states.append('boolean')
        elif name.startswith('get_'):
            states.append('getter')
        elif name.startswith('set_'):
            states.append('setter')
        elif name.startswith('_'):
            states.append('private')
        elif name.startswith('__') and name.endswith('__'):
            states.append('magic')

        # Common suffixes
        if name.endswith('_count') or name.endswith('_size'):
            states.append('metric')
        elif name.endswith('_path') or name.endswith('_dir'):
            states.append('filesystem')
        elif name.endswith('_url') or name.endswith('_uri'):
            states.append('network')
        elif name.endswith('_id'):
            states.append('identifier')

        # Type hints from name
        if 'list' in name.lower():
            states.append('collection')
        elif 'dict' in name.lower() or 'map' in name.lower():
            states.append('mapping')
        elif 'set' in name.lower():
            states.append('set')

        # Default state if no inference
        if not states:
            states = ['generic']

        return states

    def _extract_context(self, node: ast.AST, source: str) -> str:
        """Extract surrounding context for a node."""
        try:
            lines = source.split('\n')
            lineno = getattr(node, 'lineno', 1) - 1

            # Get 3 lines of context
            start = max(0, lineno - 1)
            end = min(len(lines), lineno + 2)
            context_lines = lines[start:end]

            return '\n'.join(context_lines)
        except Exception:  # Catch all exceptions during context extraction
            return ""

    def _extract_function_context(self, node: ast.FunctionDef, source: str) -> str:
        """Extract function signature and docstring."""
        context_parts = []

        # Signature
        args = [arg.arg for arg in node.args.args]
        context_parts.append(f"def {node.name}({', '.join(args)})")

        # Docstring
        docstring = ast.get_docstring(node)
        if docstring:
            context_parts.append(docstring[:200])  # First 200 chars

        return '\n'.join(context_parts)

    def _extract_class_context(self, node: ast.ClassDef, source: str) -> str:
        """Extract class definition and docstring."""
        context_parts = []

        # Class signature
        bases = [base.id if isinstance(base, ast.Name) else 'object' for base in node.bases]
        context_parts.append(f"class {node.name}({', '.join(bases) if bases else ''})")

        # Docstring
        docstring = ast.get_docstring(node)
        if docstring:
            context_parts.append(docstring[:200])

        return '\n'.join(context_parts)

    def _tokenize_fallback(self, source_code: str) -> List[QuantumToken]:
        """Fallback tokenization using regex."""
        tokens = []

        # Find variable names
        for match in re.finditer(r'\b([a-z_][a-z0-9_]*)\b', source_code, re.IGNORECASE):
            var_name = match.group(1)
            if var_name not in {'if', 'else', 'for', 'while', 'def', 'class', 'return'}:
                semantic_states = self._infer_semantic_states_from_name(var_name)
                tokens.append(QuantumToken(
                    value=var_name,
                    type='variable',
                    semantic_states=semantic_states
                ))

        return tokens

    def find_entanglements(
        self,
        tokens: List[QuantumToken]
    ) -> List[EntangledPair]:
        """
        Find entangled token pairs.

        Tokens are entangled if they are semantically correlated:
        - Same line (likely related)
        - Same function scope
        - Assignment relationship
        - Parameter-usage relationship

        Args:
            tokens: List of quantum tokens

        Returns:
            List of entangled pairs
        """
        entanglements = []

        # Build position index
        by_line: Dict[int, List[QuantumToken]] = defaultdict(list)
        for token in tokens:
            by_line[token.position[0]].append(token)

        # Find correlations
        for line, line_tokens in by_line.items():
            if len(line_tokens) < 2:
                continue

            # All tokens on same line are potentially entangled
            for i, token1 in enumerate(line_tokens):
                for token2 in line_tokens[i+1:]:
                    correlation = self._calculate_correlation(token1, token2)

                    if correlation >= self.entanglement_threshold:
                        relationship = self._infer_relationship(token1, token2)
                        entanglements.append(EntangledPair(
                            token1=token1.value,
                            token2=token2.value,
                            correlation=correlation,
                            relationship=relationship,
                            confidence=correlation
                        ))

                        # Update tokens
                        token1.entangled_with.add(token2.value)
                        token2.entangled_with.add(token1.value)

        return entanglements

    def _calculate_correlation(
        self,
        token1: QuantumToken,
        token2: QuantumToken
    ) -> float:
        """
        Calculate correlation between two tokens.

        Uses semantic state overlap and context similarity.
        """
        # Semantic overlap
        states1 = set(token1.semantic_states)
        states2 = set(token2.semantic_states)

        if not states1 or not states2:
            semantic_overlap = 0.0
        else:
            semantic_overlap = len(states1 & states2) / len(states1 | states2)

        # Context similarity (TF-IDF)
        if token1.context and token2.context:
            try:
                if not self._fitted:
                    self.tfidf.fit([token1.context, token2.context])
                    self._fitted = True

                vectors = self.tfidf.transform([token1.context, token2.context])
                context_sim = (vectors[0] * vectors[1].T).toarray()[0, 0]
            except Exception:  # Catch sklearn/tfidf errors during context similarity calculation
                context_sim = 0.0
        else:
            context_sim = 0.0

        # Weighted average
        return 0.6 * semantic_overlap + 0.4 * context_sim


    def _infer_relationship(
        self,
        token1: QuantumToken,
        token2: QuantumToken
    ) -> str:
        """Infer relationship type between tokens."""
        # Function and its return value
        if token1.type == 'function' and token2.type == 'variable':
            return 'returns'

        # Variable and its type
        if token1.type == 'variable' and token2.type == 'class':
            return 'instance_of'

        # Assignment
        if 'setter' in token1.semantic_states and token2.type == 'variable':
            return 'assigns'

        # Usage
        if 'getter' in token1.semantic_states and token2.type == 'variable':
            return 'uses'

        return 'related'

    def build_semantic_map(
        self,
        tokens: List[QuantumToken],
        entanglements: List[EntangledPair]
    ) -> Dict[str, Any]:
        """
        Build semantic map of tokenized code.

        Creates a comprehensive view of:
        - Token superposition states
        - Entanglement network
        - Uncertainty distribution
        - Dominant patterns

        Args:
            tokens: List of quantum tokens
            entanglements: List of entangled pairs

        Returns:
            Semantic map dictionary
        """
        # Token statistics
        total_tokens = len(tokens)
        by_type = defaultdict(int)
        by_semantic = defaultdict(int)
        uncertainties = []

        for token in tokens:
            by_type[token.type] += 1
            for state in token.semantic_states:
                by_semantic[state] += 1
            uncertainties.append(token.measure_uncertainty())

        # Entanglement statistics
        entanglement_network = defaultdict(list)
        for pair in entanglements:
            entanglement_network[pair.token1].append(pair.token2)
            entanglement_network[pair.token2].append(pair.token1)

        # Build map
        return {
            'total_tokens': total_tokens,
            'token_types': dict(by_type),
            'semantic_distribution': dict(by_semantic),
            'average_uncertainty': np.mean(uncertainties) if uncertainties else 0.0,
            'max_uncertainty': max(uncertainties) if uncertainties else 0.0,
            'entanglement_count': len(entanglements),
            'entanglement_density': len(entanglements) / (total_tokens * (total_tokens - 1) / 2) if total_tokens > 1 else 0.0,
            'most_entangled': self._find_most_entangled(entanglement_network, k=5),
            'tokens': [token.to_dict() for token in tokens],
            'entanglements': [pair.to_dict() for pair in entanglements],
        }


    def _find_most_entangled(
        self,
        network: Dict[str, List[str]],
        k: int = 5
    ) -> List[Tuple[str, int]]:
        """Find tokens with most entanglements."""
        counts = [(token, len(partners)) for token, partners in network.items()]
        counts.sort(key=lambda x: x[1], reverse=True)
        return counts[:k]

    def collapse_ambiguity(
        self,
        tokens: List[QuantumToken],
        context_code: str
    ) -> List[QuantumToken]:
        """
        Collapse wave functions to resolve semantic ambiguity.

        Uses context to determine most likely semantic state for
        each token, collapsing superposition to concrete meaning.

        Args:
            tokens: Tokens in superposition
            context_code: Full code context for disambiguation

        Returns:
            Tokens with collapsed wave functions
        """
        # Parse context for type hints
        try:
            tree = ast.parse(context_code)
            type_annotations = self._extract_type_annotations(tree)
        except Exception:  # Catch AST parsing errors for malformed code context
            type_annotations = {}

        collapsed = []
        for token in tokens:
            if token.value in type_annotations:
                # Collapse to annotated type
                annotated_type = type_annotations[token.value]
                token.collapse(annotated_type)
            else:
                # Collapse to dominant state
                dominant = token.dominant_state
                token.collapse(dominant)

            collapsed.append(token)

        return collapsed

    def _extract_type_annotations(self, tree: ast.AST) -> Dict[str, str]:
        """Extract type annotations from AST."""
        annotations = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                var_name = node.target.id
                if isinstance(node.annotation, ast.Name):
                    type_name = node.annotation.id
                    annotations[var_name] = type_name

            elif isinstance(node, ast.FunctionDef):
                # Function arguments with annotations
                for arg in node.args.args:
                    if arg.annotation and isinstance(arg.annotation, ast.Name):
                        annotations[arg.arg] = arg.annotation.id

                # Return type
                if node.returns and isinstance(node.returns, ast.Name):
                    annotations[f"{node.name}_return"] = node.returns.id

        return annotations


def demonstrate_quantum_tokenization():
    """Demonstrate quantum tokenizer capabilities."""
    sample_code = '''
def calculate_embedding(text: str, provider: EmbeddingProvider) -> np.ndarray:
    """Calculate embedding for text using provider.

    Args:
        text: Input text string
        provider: Embedding provider instance

    Returns:
        Embedding vector as numpy array
    """
    tokens = tokenize(text)
    embedding = provider.encode(tokens)
    return embedding

class TfidfEmbeddingProvider:
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.vectorizer = TfidfVectorizer()
    '''

    print("=== Quantum Tokenization Demo ===\n")

    # Initialize tokenizer
    tokenizer = QuantumTokenizer()

    # Tokenize
    print("1. Tokenizing code...")
    tokens = tokenizer.tokenize(sample_code)
    print(f"   Found {len(tokens)} tokens\n")

    # Show some tokens in superposition
    print("2. Tokens in superposition:")
    for token in tokens[:5]:
        print(f"   {token.value} ({token.type})")
        print(f"      States: {token.semantic_states}")
        print(f"      Uncertainty: {token.measure_uncertainty():.3f} bits")
        print()

    # Find entanglements
    print("3. Finding entanglements...")
    entanglements = tokenizer.find_entanglements(tokens)
    print(f"   Found {len(entanglements)} entangled pairs\n")

    # Show entanglements
    print("4. Entangled pairs:")
    for pair in entanglements[:3]:
        print(f"   {pair.token1} ↔ {pair.token2}")
        print(f"      Correlation: {pair.correlation:.3f}")
        print(f"      Relationship: {pair.relationship}")
        print()

    # Build semantic map
    print("5. Building semantic map...")
    semantic_map = tokenizer.build_semantic_map(tokens, entanglements)
    print(f"   Average uncertainty: {semantic_map['average_uncertainty']:.3f} bits")
    print(f"   Entanglement density: {semantic_map['entanglement_density']:.3f}")
    print(f"   Most entangled: {semantic_map['most_entangled'][:3]}\n")

    # Collapse wave functions
    print("6. Collapsing wave functions...")
    collapsed = tokenizer.collapse_ambiguity(tokens, sample_code)
    print(f"   Resolved {len(collapsed)} tokens to concrete meanings\n")

    print("=== Demo Complete ===")


if __name__ == "__main__":
    demonstrate_quantum_tokenization()
