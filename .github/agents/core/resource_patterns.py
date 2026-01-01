"""
Resource Pattern Matcher for Cognitive Brain Framework.

Detects resource management issues: memory leaks, unclosed files, connection leaks.

#AFTERMATH_PATTERN_IDENTIFIED: resource_management_analysis
#AFTERMATH_METRIC: resource_issues_detected

PDA Loop Integration:
- PERCEIVE: Analyze code for resource management issues
- DECIDE: Classify severity and leak risk
- ACT: Generate resource cleanup recommendations
- AFTERMATH: Record patterns for learning
"""

import ast
import re
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from pathlib import Path


@dataclass
class ResourcePattern:
    """Resource management issue or leak risk."""
    
    name: str
    pattern_type: str  # "memory_leak", "file_leak", "connection_leak", "resource_exhaustion"
    description: str
    locations: List[str]
    confidence: float  # 0.0 to 1.0
    severity: str  # "critical", "high", "medium", "low"
    leak_risk: str  # Description of leak risk
    fix: str  # Suggested fix
    metadata: Dict[str, Any]


class ResourcePatternMatcher:
    """
    Detects resource management issues and potential leaks.
    
    #AFTERMATH_PATTERN_IDENTIFIED: resource_pattern_detection
    
    PDA Loop:
    - PERCEIVE: Multi-layer resource analysis (AST + regex)
    - DECIDE: Leak-risk based severity classification
    - ACT: Pattern detection with cleanup strategies
    - AFTERMATH: Metrics + cognitive brain learning
    """
    
    def __init__(self):
        """Initialize resource pattern matcher."""
        self.detected_patterns: List[ResourcePattern] = []
        #AFTERMATH_METRIC: resource_matcher_initialized
    
    def analyze_file(self, file_path: Path, content: Optional[str] = None) -> List[ResourcePattern]:
        """
        Analyze a file for resource management issues.
        
        #AFTERMATH_PATTERN_IDENTIFIED: file_resource_analysis
        
        Args:
            file_path: Path to file to analyze
            content: Optional file content (will read if not provided)
            
        Returns:
            List of detected resource patterns
        """
        if content is None:
            try:
                content = file_path.read_text()
            except (IOError, UnicodeDecodeError):
                return []
        
        detected: List[ResourcePattern] = []
        
        # PERCEIVE: Multi-layer resource scanning
        if file_path.suffix == ".py":
            # Python-specific analysis using AST
            try:
                tree = ast.parse(content)
                detected.extend(self._detect_unclosed_files(tree, file_path))
                detected.extend(self._detect_connection_leaks(tree, file_path))
                detected.extend(self._detect_memory_leaks(tree, file_path))
                detected.extend(self._detect_resource_exhaustion(tree, file_path))
                #AFTERMATH_PATTERN_IDENTIFIED: ast_resource_analysis
            except SyntaxError:
                # Intentionally skip files with syntax errors
                # Resource analysis requires valid AST
                pass
        
        # General regex-based detection (all file types)
        detected.extend(self._detect_regex_patterns(content, file_path))
        
        # AFTERMATH: Record metrics
        #AFTERMATH_METRIC: resource_issues_count = len(detected)
        
        return detected
    
    def _detect_unclosed_files(self, tree: ast.AST, file_path: Path) -> List[ResourcePattern]:
        """
        Detect unclosed file handles.
        
        #AFTERMATH_PATTERN_IDENTIFIED: file_leak_detection
        """
        detected = []
        
        # Look for open() calls without context manager
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = self._get_call_name(node)
                
                # Check for open() not in 'with' statement
                if func_name in ['open', 'file']:
                    # Check if this is inside a 'with' statement
                    if not self._is_in_context_manager(tree, node):
                        detected.append(ResourcePattern(
                            name="unclosed_file",
                            pattern_type="file_leak",
                            description=f"File opened without context manager: {func_name}()",
                            locations=[f"{file_path}:{node.lineno}"],
                            confidence=0.85,
                            severity="high",
                            leak_risk="File handle not guaranteed to be closed, may cause resource exhaustion",
                            fix="Use 'with open(...) as f:' to ensure file is closed",
                            metadata={
                                "file": str(file_path),
                                "line": node.lineno,
                                "function": func_name
                            }
                        ))
                
                # tempfile without cleanup
                if 'tempfile' in func_name.lower() or 'mktemp' in func_name.lower():
                    detected.append(ResourcePattern(
                        name="unclosed_tempfile",
                        pattern_type="file_leak",
                        description="Temporary file created without cleanup",
                        locations=[f"{file_path}:{node.lineno}"],
                        confidence=0.75,
                        severity="medium",
                        leak_risk="Temporary files may accumulate and fill disk",
                        fix="Use tempfile.TemporaryFile or ensure explicit cleanup",
                        metadata={
                            "file": str(file_path),
                            "line": node.lineno
                        }
                    ))
        
        return detected
    
    def _detect_connection_leaks(self, tree: ast.AST, file_path: Path) -> List[ResourcePattern]:
        """
        Detect unclosed database/network connections.
        
        #AFTERMATH_PATTERN_IDENTIFIED: connection_leak_detection
        """
        detected = []
        
        connection_patterns = [
            'connect', 'connection', 'cursor', 'session',
            'socket', 'urlopen', 'request', 'client'
        ]
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = self._get_call_name(node)
                
                # Check for connection creation without context manager
                if any(pattern in func_name.lower() for pattern in connection_patterns):
                    if not self._is_in_context_manager(tree, node):
                        detected.append(ResourcePattern(
                            name="unclosed_connection",
                            pattern_type="connection_leak",
                            description=f"Connection opened without context manager: {func_name}()",
                            locations=[f"{file_path}:{node.lineno}"],
                            confidence=0.8,
                            severity="high",
                            leak_risk="Connection not guaranteed to be closed, may exhaust connection pool",
                            fix="Use context manager or ensure .close() in finally block",
                            metadata={
                                "file": str(file_path),
                                "line": node.lineno,
                                "function": func_name
                            }
                        ))
        
        return detected
    
    def _detect_memory_leaks(self, tree: ast.AST, file_path: Path) -> List[ResourcePattern]:
        """
        Detect potential memory leaks.
        
        #AFTERMATH_PATTERN_IDENTIFIED: memory_leak_detection
        """
        detected = []
        
        # Global collections that grow indefinitely
        for node in ast.walk(tree):
            if isinstance(node, ast.Global):
                # Check if these globals are modified (append, extend, etc.)
                for inner in ast.walk(tree):
                    if isinstance(inner, ast.Call):
                        func_name = self._get_call_name(inner)
                        if any(method in func_name for method in ['.append', '.extend', '.add', '.update']):
                            # Check if target is a global
                            if isinstance(inner.func, ast.Attribute):
                                if isinstance(inner.func.value, ast.Name):
                                    if inner.func.value.id in node.names:
                                        detected.append(ResourcePattern(
                                            name="unbounded_collection_growth",
                                            pattern_type="memory_leak",
                                            description=f"Global collection {inner.func.value.id} grows without bounds",
                                            locations=[f"{file_path}:{inner.lineno}"],
                                            confidence=0.7,
                                            severity="medium",
                                            leak_risk="Memory usage grows over time without limit",
                                            fix="Implement size limits, use LRU cache, or periodic cleanup",
                                            metadata={
                                                "file": str(file_path),
                                                "line": inner.lineno,
                                                "collection": inner.func.value.id
                                            }
                                        ))
            
            # Circular references with __del__
            if isinstance(node, ast.ClassDef):
                has_del = any(isinstance(n, ast.FunctionDef) and n.name == '__del__' 
                             for n in node.body)
                if has_del:
                    detected.append(ResourcePattern(
                        name="circular_reference_with_del",
                        pattern_type="memory_leak",
                        description=f"Class {node.name} has __del__ which may prevent garbage collection",
                        locations=[f"{file_path}:{node.lineno}"],
                        confidence=0.6,
                        severity="low",
                        leak_risk="Circular references with __del__ may not be collected",
                        fix="Avoid __del__ or use weakref to break cycles",
                        metadata={
                            "file": str(file_path),
                            "line": node.lineno,
                            "class": node.name
                        }
                    ))
        
        return detected
    
    def _detect_resource_exhaustion(self, tree: ast.AST, file_path: Path) -> List[ResourcePattern]:
        """
        Detect patterns that may exhaust system resources.
        
        #AFTERMATH_PATTERN_IDENTIFIED: resource_exhaustion_detection
        """
        detected = []
        
        # Unbounded thread/process creation
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                for inner in ast.walk(node):
                    if isinstance(inner, ast.Call):
                        func_name = self._get_call_name(inner)
                        
                        # Thread creation in loop
                        if 'Thread' in func_name or 'Process' in func_name:
                            detected.append(ResourcePattern(
                                name="unbounded_thread_creation",
                                pattern_type="resource_exhaustion",
                                description=f"Thread/Process created in loop: {func_name}",
                                locations=[f"{file_path}:{inner.lineno}"],
                                confidence=0.85,
                                severity="critical",
                                leak_risk="May create thousands of threads/processes, exhausting system resources",
                                fix="Use ThreadPoolExecutor or ProcessPoolExecutor with limited workers",
                                metadata={
                                    "file": str(file_path),
                                    "line": inner.lineno,
                                    "function": func_name
                                }
                            ))
                        
                        # Socket creation in loop
                        if 'socket' in func_name.lower() or 'connect' in func_name.lower():
                            detected.append(ResourcePattern(
                                name="unbounded_socket_creation",
                                pattern_type="resource_exhaustion",
                                description="Socket/connection created in loop without pooling",
                                locations=[f"{file_path}:{inner.lineno}"],
                                confidence=0.75,
                                severity="high",
                                leak_risk="May exhaust file descriptors or connection limits",
                                fix="Use connection pooling or limit concurrent connections",
                                metadata={
                                    "file": str(file_path),
                                    "line": inner.lineno
                                }
                            ))
        
        # Recursive function without base case or limit
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if function calls itself
                for inner in ast.walk(node):
                    if isinstance(inner, ast.Call):
                        func_name = self._get_call_name(inner)
                        if func_name == node.name:
                            # Recursive call found - check for base case
                            has_return = any(isinstance(n, ast.Return) for n in ast.walk(node))
                            if not has_return:
                                detected.append(ResourcePattern(
                                    name="unbounded_recursion",
                                    pattern_type="resource_exhaustion",
                                    description=f"Recursive function {node.name} may lack base case",
                                    locations=[f"{file_path}:{node.lineno}"],
                                    confidence=0.65,
                                    severity="high",
                                    leak_risk="May cause stack overflow and crash",
                                    fix="Ensure proper base case or convert to iteration",
                                    metadata={
                                        "file": str(file_path),
                                        "line": node.lineno,
                                        "function": node.name
                                    }
                                ))
        
        return detected
    
    def _detect_regex_patterns(self, content: str, file_path: Path) -> List[ResourcePattern]:
        """
        Detect resource issues using regex patterns.
        
        #AFTERMATH_PATTERN_IDENTIFIED: regex_resource_detection
        """
        detected = []
        
        # File operations without close
        if re.search(r'(?<!with\s)\b(?:open|file)\s*\(', content):
            # This is a heuristic - may have false positives
            detected.append(ResourcePattern(
                name="potential_unclosed_file",
                pattern_type="file_leak",
                description="File operation detected - verify proper closure",
                locations=[str(file_path)],
                confidence=0.5,
                severity="medium",
                leak_risk="File may not be closed in all code paths",
                fix="Use context manager: with open(...) as f:",
                metadata={"file": str(file_path)}
            ))
        
        return detected
    
    def _is_in_context_manager(self, tree: ast.AST, target: ast.AST) -> bool:
        """Check if target node is inside a 'with' statement."""
        for node in ast.walk(tree):
            if isinstance(node, ast.With):
                for inner in ast.walk(node):
                    if inner is target:
                        return True
        return False
    
    def _get_call_name(self, node: ast.Call) -> str:
        """Extract function name from Call node."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            parts = []
            current = node.func
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            return '.'.join(reversed(parts))
        return "unknown"
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Generate summary of detected resource issues.
        
        #AFTERMATH_METRIC: resource_summary_generated
        
        Returns:
            Dictionary with resource management metrics
        """
        summary = {
            "total_issues": len(self.detected_patterns),
            "by_type": {},
            "by_severity": {},
            "leak_risks": len([p for p in self.detected_patterns if p.severity in ["high", "critical"]])
        }
        
        for pattern in self.detected_patterns:
            summary["by_type"][pattern.pattern_type] = summary["by_type"].get(pattern.pattern_type, 0) + 1
            summary["by_severity"][pattern.severity] = summary["by_severity"].get(pattern.severity, 0) + 1
        
        #AFTERMATH_LESSON_LEARNED: resource_patterns_summarized
        return summary
