#!/usr/bin/env python3
"""
Cognitive Brain - Code Ingestion Module
Part of Perception Layer - ingests and analyzes new code submissions
"""
import argparse
import json
import hashlib
import ast
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


def analyze_python_code(code_content: str) -> Dict[str, Any]:
    """
    Analyze Python code structure using AST.
    
    Args:
        code_content: Python source code
    
    Returns:
        Analysis results
    """
    analysis = {
        "classes": [],
        "functions": [],
        "imports": [],
        "docstrings": [],
        "complexity_score": 0,
        "lines_of_code": len(code_content.split('\n'))
    }
    
    try:
        tree = ast.parse(code_content)
        
        for node in ast.walk(tree):
            # Extract classes
            if isinstance(node, ast.ClassDef):
                class_info = {
                    "name": node.name,
                    "methods": [m.name for m in node.body if isinstance(m, ast.FunctionDef)],
                    "bases": [base.id for base in node.bases if isinstance(base, ast.Name)],
                    "docstring": ast.get_docstring(node)
                }
                analysis["classes"].append(class_info)
                analysis["complexity_score"] += len(class_info["methods"])
            
            # Extract functions
            elif isinstance(node, ast.FunctionDef):
                func_info = {
                    "name": node.name,
                    "args": [arg.arg for arg in node.args.args],
                    "docstring": ast.get_docstring(node)
                }
                analysis["functions"].append(func_info)
                analysis["complexity_score"] += 1
            
            # Extract imports
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    analysis["imports"].append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    analysis["imports"].append(f"{module}.{alias.name}")
        
        # Extract docstrings
        if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Constant):
            module_doc = tree.body[0].value.value
            if isinstance(module_doc, str):
                analysis["docstrings"].append({"type": "module", "content": module_doc})
        
    except SyntaxError as e:
        analysis["error"] = f"Syntax error: {e}"
    except Exception as e:
        analysis["error"] = f"Analysis error: {e}"
    
    return analysis


def ingest_code(code_path: str, output_path: str, project_name: str = "unknown") -> Dict[str, Any]:
    """
    Ingest and analyze a Python code file.
    
    Args:
        code_path: Path to Python file
        output_path: Path to save ingestion results
        project_name: Name of the project/component
    
    Returns:
        Ingestion report
    """
    code_file = Path(code_path)
    
    if not code_file.exists():
        return {"error": f"File not found: {code_path}"}
    
    # Read code
    with open(code_file, 'r', encoding='utf-8') as f:
        code_content = f.read()
    
    # Generate fingerprint
    code_hash = hashlib.sha256(code_content.encode()).hexdigest()
    
    # Analyze code
    analysis = analyze_python_code(code_content)
    
    # Create ingestion report
    report = {
        "ingestion_timestamp": datetime.now().isoformat(),
        "source_file": str(code_file),
        "project_name": project_name,
        "file_size_bytes": len(code_content),
        "code_hash": code_hash,
        "analysis": analysis,
        "quality_metrics": {}
    }
    
    # Calculate quality metrics
    report["quality_metrics"] = {
        "has_docstrings": len(analysis.get("docstrings", [])) > 0,
        "class_count": len(analysis.get("classes", [])),
        "function_count": len(analysis.get("functions", [])),
        "import_count": len(set(analysis.get("imports", []))),
        "complexity_score": analysis.get("complexity_score", 0),
        "lines_of_code": analysis.get("lines_of_code", 0),
        "estimated_maintainability": "high" if analysis.get("complexity_score", 0) < 20 else "medium" if analysis.get("complexity_score", 0) < 50 else "low"
    }
    
    # Integration recommendations
    report["integration_recommendations"] = []
    
    if "PyQt6" in str(analysis.get("imports", [])):
        report["integration_recommendations"].append({
            "type": "ui_component",
            "recommendation": "Integrate as UI module in cognitive dashboard",
            "priority": "medium"
        })
    
    if analysis.get("classes"):
        report["integration_recommendations"].append({
            "type": "class_based",
            "recommendation": "Import classes into cognitive brain module system",
            "priority": "high"
        })
    
    # Knowledge extraction
    report["knowledge_extracted"] = {
        "design_patterns": [],
        "technologies": [],
        "capabilities": []
    }
    
    # Identify design patterns
    for cls in analysis.get("classes", []):
        if "Worker" in cls["name"]:
            report["knowledge_extracted"]["design_patterns"].append("Worker pattern (threading)")
        if "QObject" in cls.get("bases", []):
            report["knowledge_extracted"]["technologies"].append("PyQt6/Qt framework")
    
    # Identify capabilities
    for func in analysis.get("functions", []):
        if "encode" in func["name"].lower():
            report["knowledge_extracted"]["capabilities"].append("Base64 encoding")
        if "decode" in func["name"].lower():
            report["knowledge_extracted"]["capabilities"].append("Base64 decoding")
        if "theme" in func["name"].lower():
            report["knowledge_extracted"]["capabilities"].append("Theme management")
    
    # Save report
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"✅ Code ingestion complete")
    print(f"   File: {code_file.name}")
    print(f"   Size: {report['file_size_bytes']} bytes")
    print(f"   Classes: {report['quality_metrics']['class_count']}")
    print(f"   Functions: {report['quality_metrics']['function_count']}")
    print(f"   Complexity: {report['quality_metrics']['complexity_score']}")
    print(f"   Maintainability: {report['quality_metrics']['estimated_maintainability']}")
    print(f"   Recommendations: {len(report['integration_recommendations'])}")
    print(f"   Saved to: {output_path}")
    
    return report


def main():
    parser = argparse.ArgumentParser(description="Ingest and analyze Python code")
    parser.add_argument("--code", required=True, help="Path to Python file")
    parser.add_argument("--output", required=True, help="Output JSON path")
    parser.add_argument("--project", default="unknown", help="Project name")
    args = parser.parse_args()
    
    ingest_code(args.code, args.output, args.project)


if __name__ == "__main__":
    main()
