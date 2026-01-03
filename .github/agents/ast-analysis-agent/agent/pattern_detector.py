"""
AST Analysis Agent - Pattern Detector.

Detects code patterns using AST analysis and integrates
with Cognitive Brain for pattern learning.
"""
import ast
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Pattern:
    """Represents a detected code pattern.
    
    Attributes:
        name: Pattern identifier
        category: Pattern category (structural, behavioral, antipattern)
        description: Human-readable description
        locations: List of locations where pattern found
        confidence: Detection confidence [0, 1]
        metadata: Additional pattern metadata
    """
    name: str
    category: str  # structural, behavioral, antipattern
    description: str
    locations: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'locations': self.locations,
            'confidence': self.confidence,
            'metadata': self.metadata,
        }


class PatternDetector:
    """Detects code patterns in AST.
    
    Implements pattern detection for:
    - Structural patterns (singleton, factory, decorator)
    - Behavioral patterns (observer, strategy, command)
    - Anti-patterns (god class, long parameter list)
    
    Attributes:
        patterns: Registered pattern detectors
        detected: List of detected patterns
    """
    
    def __init__(self):
        """Initialize pattern detector."""
        self.patterns: Dict[str, callable] = {}
        self.detected: List[Pattern] = []
        self._register_default_patterns()
    
    def _register_default_patterns(self) -> None:
        """Register built-in pattern detectors."""
        self.patterns = {
            'singleton': self._detect_singleton,
            'factory': self._detect_factory,
            'god_class': self._detect_god_class,
            'long_parameter_list': self._detect_long_params,
            'decorator_pattern': self._detect_decorator_pattern,
        }
    
    def detect_patterns(
        self,
        source_code: str,
        file_path: str = "<unknown>",
    ) -> List[Pattern]:
        """Detect all patterns in source code.
        
        Args:
            source_code: Python source code
            file_path: Path to source file
            
        Returns:
            List of detected patterns
        """
        self.detected = []
        
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return []
        
        for pattern_name, detector in self.patterns.items():
            patterns = detector(tree, file_path)
            self.detected.extend(patterns)
        
        return self.detected
    
    def _detect_singleton(self, tree: ast.AST, file_path: str) -> List[Pattern]:
        """Detect singleton pattern."""
        patterns = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check for singleton indicators
                has_instance_attr = False
                has_get_instance = False
                
                for item in node.body:
                    # Check for _instance class attribute
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name) and target.id in ('_instance', 'instance'):
                                has_instance_attr = True
                    
                    # Check for get_instance method
                    if isinstance(item, ast.FunctionDef):
                        if item.name in ('get_instance', 'getInstance', 'instance'):
                            has_get_instance = True
                
                if has_instance_attr and has_get_instance:
                    patterns.append(Pattern(
                        name='singleton',
                        category='structural',
                        description=f"Singleton pattern detected in class '{node.name}'",
                        locations=[{
                            'file': file_path,
                            'line': node.lineno,
                            'class': node.name,
                        }],
                        confidence=0.85,
                    ))
        
        return patterns
    
    def _detect_factory(self, tree: ast.AST, file_path: str) -> List[Pattern]:
        """Detect factory pattern."""
        patterns = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for factory indicators
                if any(keyword in node.name.lower() for keyword in ['create', 'make', 'build', 'factory']):
                    # Check if function returns an object
                    for item in ast.walk(node):
                        if isinstance(item, ast.Return) and item.value:
                            if isinstance(item.value, ast.Call):
                                patterns.append(Pattern(
                                    name='factory',
                                    category='structural',
                                    description=f"Factory pattern detected in '{node.name}'",
                                    locations=[{
                                        'file': file_path,
                                        'line': node.lineno,
                                        'function': node.name,
                                    }],
                                    confidence=0.75,
                                ))
                                break
        
        return patterns
    
    def _detect_god_class(self, tree: ast.AST, file_path: str) -> List[Pattern]:
        """Detect god class anti-pattern."""
        patterns = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Count methods and attributes
                method_count = sum(1 for item in node.body if isinstance(item, ast.FunctionDef))
                attr_count = sum(1 for item in node.body if isinstance(item, ast.Assign))
                
                # Check for god class indicators
                if method_count > 20 or attr_count > 15:
                    patterns.append(Pattern(
                        name='god_class',
                        category='antipattern',
                        description=f"God class detected: '{node.name}' has {method_count} methods and {attr_count} attributes",
                        locations=[{
                            'file': file_path,
                            'line': node.lineno,
                            'class': node.name,
                        }],
                        confidence=0.8,
                        metadata={
                            'method_count': method_count,
                            'attribute_count': attr_count,
                        },
                    ))
        
        return patterns
    
    def _detect_long_params(self, tree: ast.AST, file_path: str) -> List[Pattern]:
        """Detect long parameter list anti-pattern."""
        patterns = []
        threshold = 5
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Count parameters (excluding self)
                param_count = len([
                    arg for arg in node.args.args 
                    if arg.arg != 'self'
                ])
                
                if param_count > threshold:
                    patterns.append(Pattern(
                        name='long_parameter_list',
                        category='antipattern',
                        description=f"Function '{node.name}' has {param_count} parameters (threshold: {threshold})",
                        locations=[{
                            'file': file_path,
                            'line': node.lineno,
                            'function': node.name,
                        }],
                        confidence=0.9,
                        metadata={
                            'parameter_count': param_count,
                            'threshold': threshold,
                        },
                    ))
        
        return patterns
    
    def _detect_decorator_pattern(self, tree: ast.AST, file_path: str) -> List[Pattern]:
        """Detect decorator pattern usage."""
        patterns = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.decorator_list:
                for decorator in node.decorator_list:
                    decorator_name = ""
                    if isinstance(decorator, ast.Name):
                        decorator_name = decorator.id
                    elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                        decorator_name = decorator.func.id
                    
                    if decorator_name:
                        patterns.append(Pattern(
                            name='decorator_pattern',
                            category='structural',
                            description=f"Decorator '{decorator_name}' used on '{node.name}'",
                            locations=[{
                                'file': file_path,
                                'line': node.lineno,
                                'function': node.name,
                                'decorator': decorator_name,
                            }],
                            confidence=1.0,
                        ))
        
        return patterns
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get detection statistics."""
        by_category = {}
        by_name = {}
        
        for pattern in self.detected:
            # Count by category
            if pattern.category not in by_category:
                by_category[pattern.category] = 0
            by_category[pattern.category] += 1
            
            # Count by name
            if pattern.name not in by_name:
                by_name[pattern.name] = 0
            by_name[pattern.name] += 1
        
        return {
            'total_patterns': len(self.detected),
            'by_category': by_category,
            'by_name': by_name,
        }
