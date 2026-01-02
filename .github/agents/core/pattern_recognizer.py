"""
Pattern Recognizer - Automated Pattern Detection and Learning
Detects code patterns, anti-patterns, and recurring issues across the codebase.

#AFTERMATH_PATTERN_IDENTIFIED: pattern_recognition_engine
Enables automatic learning from codebase patterns.
"""
import re
import ast
from typing import Any, Dict, List, Optional, Set
from pathlib import Path
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class Pattern:
    """Represents a detected pattern."""
    name: str
    pattern_type: str
    description: str
    locations: List[str]
    confidence: float
    metadata: Dict[str, Any]


class PatternMatcher(ABC):
    """Abstract base class for pattern matchers."""
    
    @abstractmethod
    def match(self, content: str, file_path: Path) -> List[Pattern]:
        """
        Match patterns in content.
        
        Args:
            content: File content to analyze
            file_path: Path to file being analyzed
        
        Returns:
            List of detected patterns
        """
        pass
    
    @abstractmethod
    def get_pattern_type(self) -> str:
        """Get the type of patterns this matcher detects."""
        pass


class ExceptionPatternMatcher(PatternMatcher):
    """Detects exception handling patterns and anti-patterns."""
    
    def __init__(self):
        self.patterns = {
            "broad_exception": r"except\s+Exception:",
            "bare_except": r"except\s*:",
            "empty_except": r"except[^:]*:\s*pass",
            "specific_exception": r"except\s+\w+Error:",
        }
    
    def match(self, content: str, file_path: Path) -> List[Pattern]:
        """Detect exception handling patterns."""
        detected = []
        
        for pattern_name, regex in self.patterns.items():
            matches = re.finditer(regex, content)
            for match in matches:
                # Calculate line number
                line_num = content[:match.start()].count('\n') + 1
                
                detected.append(Pattern(
                    name=pattern_name,
                    pattern_type="exception_handling",
                    description=f"Exception pattern: {pattern_name}",
                    locations=[f"{file_path}:{line_num}"],
                    confidence=0.9,
                    metadata={
                        "line": line_num,
                        "match": match.group(),
                        "file": str(file_path)
                    }
                ))
        
        return detected
    
    def get_pattern_type(self) -> str:
        return "exception_handling"


class ImportPatternMatcher(PatternMatcher):
    """Detects import patterns and issues."""
    
    def __init__(self):
        self.patterns = {
            "unused_import": None,  # Requires AST analysis
            "wildcard_import": r"from\s+\S+\s+import\s+\*",
            "conditional_import": r"^\s*if\s+.*:\s*import",
            "duplicate_import": None,  # Requires tracking
        }
    
    def match(self, content: str, file_path: Path) -> List[Pattern]:
        """Detect import patterns."""
        detected = []
        
        # Detect wildcard imports
        for match in re.finditer(self.patterns["wildcard_import"], content, re.MULTILINE):
            line_num = content[:match.start()].count('\n') + 1
            detected.append(Pattern(
                name="wildcard_import",
                pattern_type="import",
                description="Wildcard import detected (may hide unused imports)",
                locations=[f"{file_path}:{line_num}"],
                confidence=1.0,
                metadata={
                    "line": line_num,
                    "match": match.group(),
                    "file": str(file_path)
                }
            ))
        
        # Detect conditional imports
        for match in re.finditer(self.patterns["conditional_import"], content, re.MULTILINE):
            line_num = content[:match.start()].count('\n') + 1
            detected.append(Pattern(
                name="conditional_import",
                pattern_type="import",
                description="Conditional import (may indicate optional dependency)",
                locations=[f"{file_path}:{line_num}"],
                confidence=0.9,
                metadata={
                    "line": line_num,
                    "match": match.group(),
                    "file": str(file_path)
                }
            ))
        
        # AST-based analysis for unused imports
        try:
            tree = ast.parse(content)
            imports = self._extract_imports(tree)
            used_names = self._extract_used_names(tree)
            
            for imp in imports:
                if imp["name"] not in used_names:
                    detected.append(Pattern(
                        name="unused_import",
                        pattern_type="import",
                        description=f"Unused import: {imp['name']}",
                        locations=[f"{file_path}:{imp['line']}"],
                        confidence=0.8,
                        metadata={
                            "line": imp["line"],
                            "import_name": imp["name"],
                            "file": str(file_path)
                        }
                    ))
        except SyntaxError:
            # Skip files with syntax errors
            pass
        
        return detected
    
    def _extract_imports(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract all imports from AST."""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        "name": alias.asname if alias.asname else alias.name.split('.')[0],
                        "line": node.lineno,
                        "type": "import"
                    })
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imports.append({
                        "name": alias.asname if alias.asname else alias.name,
                        "line": node.lineno,
                        "type": "from_import"
                    })
        return imports
    
    def _extract_used_names(self, tree: ast.AST) -> Set[str]:
        """Extract all used names from AST."""
        used = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used.add(node.id)
            elif isinstance(node, ast.Attribute):
                # Get the root name
                root = node
                while isinstance(root, ast.Attribute):
                    root = root.value
                if isinstance(root, ast.Name):
                    used.add(root.id)
        return used
    
    def get_pattern_type(self) -> str:
        return "import"


class TestPatternMatcher(PatternMatcher):
    """Detects test patterns and anti-patterns."""
    
    def __init__(self):
        self.patterns = {
            "test_function": r"def\s+test_\w+\s*\(",
            "fixture": r"@pytest\.fixture",
            "parametrize": r"@pytest\.mark\.parametrize",
            "skip": r"@pytest\.mark\.skip",
            "xfail": r"@pytest\.mark\.xfail",
            "empty_test": r"def\s+test_\w+\s*\([^)]*\):\s*pass",
            "missing_assert": r"def\s+test_\w+\s*\([^)]*\):(?:(?!assert).)*$",
        }
    
    def match(self, content: str, file_path: Path) -> List[Pattern]:
        """Detect test patterns."""
        detected = []
        
        # Only analyze test files
        if not (file_path.name.startswith('test_') or '/tests/' in str(file_path)):
            return detected
        
        for pattern_name, regex in self.patterns.items():
            matches = re.finditer(regex, content, re.MULTILINE | re.DOTALL)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                
                detected.append(Pattern(
                    name=pattern_name,
                    pattern_type="test",
                    description=f"Test pattern: {pattern_name}",
                    locations=[f"{file_path}:{line_num}"],
                    confidence=0.85,
                    metadata={
                        "line": line_num,
                        "match": match.group()[:50],  # First 50 chars
                        "file": str(file_path)
                    }
                ))
        
        return detected
    
    def get_pattern_type(self) -> str:
        return "test"


class DocstringPatternMatcher(PatternMatcher):
    """Detects docstring patterns and issues."""
    
    def match(self, content: str, file_path: Path) -> List[Pattern]:
        """Detect docstring patterns."""
        detected = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    docstring = ast.get_docstring(node)
                    
                    if docstring is None:
                        detected.append(Pattern(
                            name="missing_docstring",
                            pattern_type="documentation",
                            description=f"Missing docstring for {node.name}",
                            locations=[f"{file_path}:{node.lineno}"],
                            confidence=1.0,
                            metadata={
                                "line": node.lineno,
                                "name": node.name,
                                "type": type(node).__name__,
                                "file": str(file_path)
                            }
                        ))
                    elif len(docstring) < 10:
                        detected.append(Pattern(
                            name="minimal_docstring",
                            pattern_type="documentation",
                            description=f"Very short docstring for {node.name}",
                            locations=[f"{file_path}:{node.lineno}"],
                            confidence=0.7,
                            metadata={
                                "line": node.lineno,
                                "name": node.name,
                                "length": len(docstring),
                                "file": str(file_path)
                            }
                        ))
        except SyntaxError as exc:
            # Ignore files with syntax errors; docstring analysis only applies to
            # successfully parsed Python code. Record as pattern for diagnostics.
            detected.append(Pattern(
                name="syntax_error",
                pattern_type="documentation",
                description=f"Could not parse file {file_path.name} due to syntax error",
                locations=[str(file_path)],
                confidence=0.3,
                metadata={"file": str(file_path), "error": str(exc)}
            ))
        
        return detected
    
    def get_pattern_type(self) -> str:
        return "documentation"


class PatternRecognizer:
    """
    Main pattern recognition engine.
    
    Coordinates multiple pattern matchers and aggregates results.
    """
    
    def __init__(self):
        self.matchers: List[PatternMatcher] = [
            ExceptionPatternMatcher(),
            ImportPatternMatcher(),
            TestPatternMatcher(),
            DocstringPatternMatcher(),
        ]
    
    def analyze_file(self, file_path: Path) -> List[Pattern]:
        """
        Analyze a single file for patterns.
        
        Args:
            file_path: Path to file to analyze
        
        Returns:
            List of detected patterns
        """
        if not file_path.exists() or not file_path.is_file():
            return []
        
        # Only analyze Python files
        if file_path.suffix != '.py':
            return []
        
        try:
            content = file_path.read_text(encoding='utf-8')
        except (IOError, UnicodeDecodeError):
            return []
        
        all_patterns = []
        for matcher in self.matchers:
            patterns = matcher.match(content, file_path)
            all_patterns.extend(patterns)
        
        return all_patterns
    
    def analyze_directory(
        self, 
        directory: Path, 
        recursive: bool = True,
        exclude_patterns: Optional[List[str]] = None
    ) -> Dict[str, List[Pattern]]:
        """
        Analyze all Python files in a directory.
        
        Args:
            directory: Directory to analyze
            recursive: Whether to recurse into subdirectories
            exclude_patterns: List of glob patterns to exclude
        
        Returns:
            Dictionary mapping file paths to detected patterns
        """
        if exclude_patterns is None:
            exclude_patterns = [
                "*/venv/*", "*/virtualenv/*", "*/.venv/*",
                "*/node_modules/*", "*/__pycache__/*",
                "*/.git/*", "*/.pytest_cache/*",
                "*/.hypothesis/*", "*/build/*", "*/dist/*"
            ]
        
        results = {}
        
        pattern_glob = "**/*.py" if recursive else "*.py"
        for file_path in directory.glob(pattern_glob):
            # Check exclusions
            excluded = False
            for exclude in exclude_patterns:
                if file_path.match(exclude):
                    excluded = True
                    break
            
            if excluded:
                continue
            
            patterns = self.analyze_file(file_path)
            if patterns:
                results[str(file_path)] = patterns
        
        return results
    
    def get_pattern_summary(
        self, 
        results: Dict[str, List[Pattern]]
    ) -> Dict[str, Any]:
        """
        Generate summary statistics from pattern analysis.
        
        Args:
            results: Results from analyze_directory
        
        Returns:
            Summary dictionary with counts and top patterns
        
        #AFTERMATH_METRIC: pattern_analysis_summary
        """
        pattern_counts = {}
        pattern_types = {}
        
        for patterns in results.values():
            for pattern in patterns:
                # Count by name
                pattern_counts[pattern.name] = pattern_counts.get(pattern.name, 0) + 1
                
                # Count by type
                pattern_types[pattern.pattern_type] = pattern_types.get(pattern.pattern_type, 0) + 1
        
        # Sort by count
        top_patterns = sorted(
            pattern_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        return {
            "total_files": len(results),
            "total_patterns": sum(len(p) for p in results.values()),
            "unique_patterns": len(pattern_counts),
            "pattern_types": pattern_types,
            "top_patterns": [{"name": name, "count": count} for name, count in top_patterns],
            "files_with_patterns": len([f for f, p in results.items() if p])
        }
    
    def add_matcher(self, matcher: PatternMatcher):
        """
        Add a custom pattern matcher.
        
        Args:
            matcher: PatternMatcher instance
        """
        self.matchers.append(matcher)
    
    def remove_matcher(self, pattern_type: str):
        """
        Remove pattern matcher by type.
        
        Args:
            pattern_type: Type of matcher to remove
        """
        self.matchers = [m for m in self.matchers if m.get_pattern_type() != pattern_type]
