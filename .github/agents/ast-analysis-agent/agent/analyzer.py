"""
AST Analysis Agent - Core Analyzer.

Implements the PDA loop pattern for AST-based code analysis
with Cognitive Brain integration.
"""
import ast
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

# Compiled regex patterns for snake_case conversion (performance optimization)
_SNAKE_CASE_PATTERN1 = re.compile(r'(.)([A-Z][a-z]+)')
_SNAKE_CASE_PATTERN2 = re.compile(r'([a-z0-9])([A-Z])')


@dataclass
class CodeFinding:
    """Represents a code analysis finding.
    
    Attributes:
        file_path: Path to the analyzed file
        line: Line number where finding occurs
        column: Column number
        severity: Finding severity (error, warning, info)
        category: Finding category (complexity, style, security)
        message: Human-readable message
        suggestion: Optional fix suggestion
        confidence: Confidence score [0, 1]
    """
    file_path: str
    line: int
    column: int
    severity: str  # error, warning, info
    category: str  # complexity, style, security, etc.
    message: str
    suggestion: Optional[str] = None
    confidence: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'file_path': self.file_path,
            'line': self.line,
            'column': self.column,
            'severity': self.severity,
            'category': self.category,
            'message': self.message,
            'suggestion': self.suggestion,
            'confidence': self.confidence,
        }


@dataclass
class AnalysisContext:
    """Context for analysis operations.
    
    Attributes:
        file_path: Path being analyzed
        source_code: Raw source code
        ast_tree: Parsed AST
        patterns: Detected patterns
        findings: Analysis findings
    """
    file_path: str
    source_code: str = ""
    ast_tree: Optional[ast.AST] = None
    patterns: List[Dict[str, Any]] = field(default_factory=list)
    findings: List[CodeFinding] = field(default_factory=list)


class ASTAnalysisAgent:
    """AST Analysis Agent implementing PDA loop.
    
    Uses the Perceive-Decide-Act pattern for code analysis:
    - Perceive: Parse code and extract features
    - Decide: Select analysis strategies
    - Act: Apply analyzers and generate findings
    
    Attributes:
        name: Agent name
        analyzers: Registered analyzers
        max_complexity: Maximum cyclomatic complexity threshold
        max_function_length: Maximum function length in lines
    """
    
    def __init__(
        self,
        name: str = "ast-analysis",
        max_complexity: int = 10,
        max_function_length: int = 50,
    ):
        """Initialize the AST Analysis Agent.
        
        Args:
            name: Agent identifier
            max_complexity: Complexity threshold for warnings
            max_function_length: Line count threshold for function length
        """
        self.name = name
        self.max_complexity = max_complexity
        self.max_function_length = max_function_length
        self.analyzers: Dict[str, callable] = {}
        self._register_default_analyzers()
        
        # Analysis statistics
        self.files_analyzed: int = 0
        self.findings_count: int = 0
        self.analysis_history: List[Dict[str, Any]] = []
    
    def _register_default_analyzers(self) -> None:
        """Register built-in analyzers."""
        self.analyzers = {
            'complexity': self._analyze_complexity,
            'function_length': self._analyze_function_length,
            'unused_variables': self._analyze_unused_variables,
            'naming_conventions': self._analyze_naming,
        }
    
    # === PDA Loop Implementation ===
    
    def perceive(self, file_path: str) -> AnalysisContext:
        """Perceive phase: Parse code and extract features.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            AnalysisContext with parsed code
        """
        context = AnalysisContext(file_path=file_path)
        
        # Read source code
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                context.source_code = f.read()
        
        # Parse AST
        try:
            context.ast_tree = ast.parse(context.source_code)
        except SyntaxError as e:
            context.findings.append(CodeFinding(
                file_path=file_path,
                line=e.lineno or 0,
                column=e.offset or 0,
                severity='error',
                category='syntax',
                message=f"Syntax error: {e.msg}",
            ))
        
        return context
    
    def decide(self, context: AnalysisContext) -> List[str]:
        """Decide phase: Select analysis strategies.
        
        Args:
            context: Current analysis context
            
        Returns:
            List of analyzer names to apply
        """
        # If syntax errors, only report those
        if any(f.category == 'syntax' for f in context.findings):
            return []
        
        # Select all available analyzers
        return list(self.analyzers.keys())
    
    def act(self, context: AnalysisContext, analyzers: List[str]) -> List[CodeFinding]:
        """Act phase: Apply analyzers and generate findings.
        
        Args:
            context: Analysis context
            analyzers: List of analyzers to apply
            
        Returns:
            List of findings
        """
        for analyzer_name in analyzers:
            if analyzer_name in self.analyzers:
                analyzer = self.analyzers[analyzer_name]
                new_findings = analyzer(context)
                context.findings.extend(new_findings)
        
        return context.findings
    
    def aftermath(self, context: AnalysisContext, findings: List[CodeFinding]) -> Dict[str, Any]:
        """AfterMath phase: Process results and learn.
        
        Args:
            context: Analysis context
            findings: Generated findings
            
        Returns:
            Analysis summary
        """
        self.files_analyzed += 1
        self.findings_count += len(findings)
        
        summary = {
            'file': context.file_path,
            'timestamp': datetime.now().isoformat(),
            'findings_count': len(findings),
            'by_severity': {
                'error': sum(1 for f in findings if f.severity == 'error'),
                'warning': sum(1 for f in findings if f.severity == 'warning'),
                'info': sum(1 for f in findings if f.severity == 'info'),
            },
            'by_category': {},
        }
        
        # Count by category
        for finding in findings:
            if finding.category not in summary['by_category']:
                summary['by_category'][finding.category] = 0
            summary['by_category'][finding.category] += 1
        
        self.analysis_history.append(summary)
        
        return summary
    
    # === Main Analysis Method ===
    
    def analyze_file(self, file_path: str) -> Tuple[List[CodeFinding], Dict[str, Any]]:
        """Analyze a single file using PDA loop.
        
        Args:
            file_path: Path to file
            
        Returns:
            Tuple of (findings, summary)
        """
        # Perceive
        context = self.perceive(file_path)
        
        # Decide
        analyzers = self.decide(context)
        
        # Act
        findings = self.act(context, analyzers)
        
        # AfterMath
        summary = self.aftermath(context, findings)
        
        return findings, summary
    
    def analyze_directory(self, directory: str, pattern: str = "*.py") -> Dict[str, Any]:
        """Analyze all matching files in a directory.
        
        Args:
            directory: Directory path
            pattern: Glob pattern for files
            
        Returns:
            Combined analysis results
        """
        import glob
        
        all_findings = []
        summaries = []
        
        for file_path in glob.glob(os.path.join(directory, "**", pattern), recursive=True):
            findings, summary = self.analyze_file(file_path)
            all_findings.extend(findings)
            summaries.append(summary)
        
        return {
            'total_files': len(summaries),
            'total_findings': len(all_findings),
            'findings': [f.to_dict() for f in all_findings],
            'summaries': summaries,
        }
    
    # === Built-in Analyzers ===
    
    def _analyze_complexity(self, context: AnalysisContext) -> List[CodeFinding]:
        """Analyze cyclomatic complexity."""
        findings = []
        
        if not context.ast_tree:
            return findings
        
        for node in ast.walk(context.ast_tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                complexity = self._calculate_complexity(node)
                if complexity > self.max_complexity:
                    findings.append(CodeFinding(
                        file_path=context.file_path,
                        line=node.lineno,
                        column=node.col_offset,
                        severity='warning',
                        category='complexity',
                        message=f"Function '{node.name}' has complexity {complexity} (max: {self.max_complexity})",
                        suggestion=f"Consider refactoring into smaller functions",
                        confidence=0.9,
                    ))
        
        return findings
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of a node."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler,
                                  ast.With, ast.Assert, ast.comprehension)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity
    
    def _analyze_function_length(self, context: AnalysisContext) -> List[CodeFinding]:
        """Analyze function length."""
        findings = []
        
        if not context.ast_tree:
            return findings
        
        for node in ast.walk(context.ast_tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if hasattr(node, 'end_lineno') and node.end_lineno:
                    length = node.end_lineno - node.lineno
                    if length > self.max_function_length:
                        findings.append(CodeFinding(
                            file_path=context.file_path,
                            line=node.lineno,
                            column=node.col_offset,
                            severity='warning',
                            category='function_length',
                            message=f"Function '{node.name}' is {length} lines (max: {self.max_function_length})",
                            suggestion="Consider breaking into smaller functions",
                            confidence=0.85,
                        ))
        
        return findings
    
    def _analyze_unused_variables(self, context: AnalysisContext) -> List[CodeFinding]:
        """Analyze unused variables (basic implementation)."""
        findings = []
        
        if not context.ast_tree:
            return findings
        
        # This is a simplified check - full implementation would track scopes
        for node in ast.walk(context.ast_tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        name = target.id
                        # Skip private/unused markers
                        if name.startswith('_') and not name.startswith('__'):
                            continue
                        # Would need more sophisticated scope tracking
        
        return findings
    
    def _analyze_naming(self, context: AnalysisContext) -> List[CodeFinding]:
        """Analyze naming conventions."""
        findings = []
        
        if not context.ast_tree:
            return findings
        
        for node in ast.walk(context.ast_tree):
            # Check function names (should be snake_case)
            if isinstance(node, ast.FunctionDef):
                if not node.name.startswith('_') and node.name != node.name.lower():
                    if not node.name.isupper():  # Skip constants
                        findings.append(CodeFinding(
                            file_path=context.file_path,
                            line=node.lineno,
                            column=node.col_offset,
                            severity='info',
                            category='naming',
                            message=f"Function '{node.name}' should use snake_case",
                            suggestion=f"Rename to '{self._to_snake_case(node.name)}'",
                            confidence=0.7,
                        ))
            
            # Check class names (should be PascalCase)
            elif isinstance(node, ast.ClassDef):
                if not node.name[0].isupper():
                    findings.append(CodeFinding(
                        file_path=context.file_path,
                        line=node.lineno,
                        column=node.col_offset,
                        severity='info',
                        category='naming',
                        message=f"Class '{node.name}' should use PascalCase",
                        confidence=0.7,
                    ))
        
        return findings
    
    def _to_snake_case(self, name: str) -> str:
        """Convert name to snake_case."""
        s1 = _SNAKE_CASE_PATTERN1.sub(r'\1_\2', name)
        return _SNAKE_CASE_PATTERN2.sub(r'\1_\2', s1).lower()
    
    # === Statistics ===
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics."""
        return {
            'agent_name': self.name,
            'files_analyzed': self.files_analyzed,
            'total_findings': self.findings_count,
            'analysis_history_size': len(self.analysis_history),
        }
