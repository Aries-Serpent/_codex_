"""
API Documentation Generator for Documentation Agent
Extracts docstrings and type hints to generate comprehensive API docs
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import ast
import random
import re

RANDOM_SEED = 48  # Documentation Agent seed

@dataclass
class FunctionDoc:
    """Documentation for a function"""
    name: str
    signature: str
    docstring: str
    parameters: List[Dict[str, str]]
    returns: Optional[str]
    examples: List[str]

class APIDocGenerator:
    """Generate API documentation from Python code"""
    
    def __init__(self, seed: int = RANDOM_SEED):
        self.seed = seed
        self._rng = random.Random(seed)
        self.documented_functions: List[FunctionDoc] = []
        self.initialized = True
    
    def extract_function_docs(self, source_code: str) -> List[FunctionDoc]:
        """Extract documentation from Python source code"""
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return []
        
        docs = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                doc = self._extract_function_info(node, source_code)
                if doc:
                    docs.append(doc)
                    self.documented_functions.append(doc)
        
        return docs
    
    def _extract_function_info(self, node: ast.FunctionDef, source: str) -> Optional[FunctionDoc]:
        """Extract information from a function AST node"""
        # Get function signature
        args = []
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            args.append(arg_str)
        
        signature = f"def {node.name}({', '.join(args)})"
        
        # Get return annotation
        returns = None
        if node.returns:
            returns = ast.unparse(node.returns)
            signature += f" -> {returns}"
        
        # Get docstring
        docstring = ast.get_docstring(node) or ""
        
        # Parse parameters from docstring
        parameters = self._parse_parameters(docstring)
        
        # Extract examples from docstring
        examples = self._extract_examples(docstring)
        
        return FunctionDoc(
            name=node.name,
            signature=signature,
            docstring=docstring,
            parameters=parameters,
            returns=returns,
            examples=examples
        )
    
    def _parse_parameters(self, docstring: str) -> List[Dict[str, str]]:
        """Parse parameter documentation from docstring"""
        params = []
        param_pattern = r'(?:Args?|Parameters?):\s*\n((?:\s+\w+.*\n?)+)'
        match = re.search(param_pattern, docstring, re.MULTILINE)
        
        if match:
            param_text = match.group(1)
            param_lines = param_text.strip().split('\n')
            for line in param_lines:
                param_match = re.match(r'\s+(\w+)(?:\s*\(([^)]+)\))?\s*:\s*(.+)', line)
                if param_match:
                    params.append({
                        "name": param_match.group(1),
                        "type": param_match.group(2) or "Any",
                        "description": param_match.group(3)
                    })
        
        return params
    
    def _extract_examples(self, docstring: str) -> List[str]:
        """Extract code examples from docstring"""
        examples = []
        example_pattern = r'(?:Examples?|Usage):\s*\n```python\n(.*?)\n```'
        matches = re.findall(example_pattern, docstring, re.DOTALL)
        examples.extend(matches)
        return examples
    
    def generate_markdown(self, function_docs: Optional[List[FunctionDoc]] = None) -> str:
        """Generate Markdown documentation"""
        if function_docs is None:
            function_docs = self.documented_functions
        
        if not function_docs:
            return "# API Documentation\n\nNo functions documented.\n"
        
        md = "# API Documentation\n\n"
        
        for func in function_docs:
            md += f"## `{func.name}`\n\n"
            md += f"```python\n{func.signature}\n```\n\n"
            
            if func.docstring:
                md += f"{func.docstring}\n\n"
            
            if func.parameters:
                md += "### Parameters\n\n"
                for param in func.parameters:
                    md += f"- **{param['name']}** (`{param['type']}`): {param['description']}\n"
                md += "\n"
            
            if func.returns:
                md += f"### Returns\n\n`{func.returns}`\n\n"
            
            if func.examples:
                md += "### Examples\n\n"
                for example in func.examples:
                    md += f"```python\n{example}\n```\n\n"
            
            md += "---\n\n"
        
        return md
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get generator metrics"""
        return {
            "seed": self.seed,
            "total_functions": len(self.documented_functions),
            "functions_with_docstrings": sum(1 for f in self.documented_functions if f.docstring),
            "functions_with_examples": sum(1 for f in self.documented_functions if f.examples),
            "initialized": self.initialized
        }


def create_generator(seed: int = RANDOM_SEED) -> APIDocGenerator:
    """Factory function to create API doc generator"""
    return APIDocGenerator(seed=seed)
