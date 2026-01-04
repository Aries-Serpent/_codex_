#!/usr/bin/env python3
"""
External Repository Ingestion System for Cognitive Brain

This module provides comprehensive analysis and integration of external repositories
into the cognitive brain ecosystem. Supports C/C++, Python, and other languages.

Features:
- Repository structure analysis
- Code capability extraction
- Integration recommendation generation
- License compliance checking
- Dependency mapping
- Plugin adaptation strategies

Usage:
    python scripts/cognitive/ingest_external_repo.py --repo-url <url> --output cognitive/ingestion/
"""

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class RepoAnalysis:
    """Analysis results for an external repository"""
    repo_url: str
    repo_name: str
    clone_path: Path
    languages: Dict[str, int] = field(default_factory=dict)  # language -> line count
    total_files: int = 0
    total_lines: int = 0
    license_type: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    integration_strategy: str = ""
    plugin_adapter_needed: bool = False
    conversion_required: bool = False
    key_components: List[Dict[str, Any]] = field(default_factory=list)
    lessons_learned: List[str] = field(default_factory=list)
    meta_learning_applicable: bool = False


class ExternalRepoIngestor:
    """Ingests and analyzes external repositories for cognitive brain integration"""
    
    # Language file extensions
    LANGUAGE_EXTENSIONS = {
        "C/C++": [".c", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".hxx", ".mm"],
        "Python": [".py", ".pyx", ".pyd"],
        "JavaScript": [".js", ".jsx", ".ts", ".tsx"],
        "Java": [".java"],
        "C#": [".cs"],
        "Go": [".go"],
        "Rust": [".rs"],
        "Ruby": [".rb"],
        "PHP": [".php"],
        "Shell": [".sh", ".bash"],
    }
    
    # Capability detection patterns
    CAPABILITY_PATTERNS = {
        "screen_capture": [r"screen.*capture", r"capture.*screen", r"screenshot", r"grab"],
        "gif_encoding": [r"gif.*encod", r"write.*gif", r"create.*gif", r"gif.*frame"],
        "video_recording": [r"video.*record", r"record.*video", r"video.*capture"],
        "image_processing": [r"image.*process", r"bitmap", r"pixel", r"rgba", r"convert"],
        "ui_framework": [r"window", r"dialog", r"button", r"control", r"widget"],
        "file_io": [r"file.*read", r"file.*write", r"fopen", r"fclose", r"stream"],
        "networking": [r"http", r"socket", r"request", r"api", r"endpoint"],
        "database": [r"sql", r"database", r"query", r"table", r"insert"],
        "threading": [r"thread", r"mutex", r"lock", r"async", r"parallel"],
        "compression": [r"compress", r"decompress", r"zip", r"gzip", r"lzw"],
    }
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def clone_repository(self, repo_url: str, target_path: Path) -> bool:
        """Clone external repository to local path"""
        try:
            if target_path.exists():
                print(f"Repository already cloned at {target_path}")
                return True
                
            result = subprocess.run(
                ["git", "clone", repo_url, str(target_path)],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                print(f"✅ Successfully cloned {repo_url}")
                return True
            else:
                print(f"❌ Failed to clone: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error cloning repository: {e}")
            return False
    
    def analyze_languages(self, repo_path: Path) -> Dict[str, int]:
        """Analyze language distribution by counting lines of code"""
        lang_counts: Dict[str, int] = {}
        
        for lang, extensions in self.LANGUAGE_EXTENSIONS.items():
            line_count = 0
            for ext in extensions:
                for file_path in repo_path.rglob(f"*{ext}"):
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            line_count += sum(1 for _ in f)
                    except Exception:
                        # Skip files that can't be read
                        continue
            
            if line_count > 0:
                lang_counts[lang] = line_count
        
        return lang_counts
    
    def detect_license(self, repo_path: Path) -> Optional[str]:
        """Detect repository license type"""
        license_files = ["LICENSE", "LICENSE.txt", "LICENSE.md", "license.txt", "COPYING"]
        
        for license_file in license_files:
            license_path = repo_path / license_file
            if license_path.exists():
                try:
                    with open(license_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(500).lower()
                        
                    if "gpl" in content:
                        return "GPL (GNU General Public License)"
                    elif "mit" in content:
                        return "MIT License"
                    elif "apache" in content:
                        return "Apache License"
                    elif "bsd" in content:
                        return "BSD License"
                    else:
                        return "Custom/Other License"
                except Exception:
                    pass
        
        return None
    
    def detect_capabilities(self, repo_path: Path) -> List[str]:
        """Detect key capabilities from code content"""
        capabilities: Set[str] = set()
        
        # Search through source files for capability indicators
        for file_path in repo_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in ['.c', '.cpp', '.h', '.py', '.js']:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()
                        
                    for capability, patterns in self.CAPABILITY_PATTERNS.items():
                        for pattern in patterns:
                            if re.search(pattern, content, re.IGNORECASE):
                                capabilities.add(capability)
                                break
                                
                except Exception:
                    # Skip files that can't be processed
                    continue
        
        return sorted(list(capabilities))
    
    def extract_key_components(self, repo_path: Path, max_files: int = 10) -> List[Dict[str, Any]]:
        """Extract key source files and their metadata"""
        components = []
        
        # Find main source files
        main_patterns = ["main.*", "*_main.*", "*_ui.*", "*_core.*", "app.*"]
        for pattern in main_patterns:
            for file_path in repo_path.rglob(pattern):
                if file_path.is_file() and file_path.suffix in ['.c', '.cpp', '.py', '.js']:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            
                        # Extract classes, functions
                        classes = [l.strip() for l in lines if re.match(r'^\s*(class|struct)\s+\w+', l)]
                        functions = [l.strip() for l in lines if re.match(r'^\s*(void|int|bool|def|function)\s+\w+', l)]
                        
                        components.append({
                            "file": str(file_path.relative_to(repo_path)),
                            "lines": len(lines),
                            "classes": classes[:5],  # First 5
                            "functions": functions[:5]  # First 5
                        })
                        
                        if len(components) >= max_files:
                            break
                    except Exception:
                        # Skip files that can't be parsed
                        continue
        
        return components
    
    def generate_integration_strategy(self, analysis: RepoAnalysis) -> str:
        """Generate integration strategy based on analysis"""
        strategy_parts = []
        
        # Language-based strategy
        primary_lang = max(analysis.languages.items(), key=lambda x: x[1])[0] if analysis.languages else "Unknown"
        
        if primary_lang == "Python":
            strategy_parts.append("DIRECT_IMPORT: Python code can be directly imported into cognitive brain")
            analysis.conversion_required = False
        elif primary_lang in ["C/C++"]:
            strategy_parts.append("PYTHON_WRAPPER: Create Python bindings using ctypes, cffi, or pybind11")
            analysis.conversion_required = True
            analysis.plugin_adapter_needed = True
        elif primary_lang in ["JavaScript", "TypeScript"]:
            strategy_parts.append("NODE_BRIDGE: Interface via Node.js subprocess or PyExecJS")
            analysis.conversion_required = True
        else:
            strategy_parts.append("SUBPROCESS: Execute as external process with IPC")
            analysis.plugin_adapter_needed = True
        
        # Capability-based strategy
        if "screen_capture" in analysis.capabilities:
            strategy_parts.append("SCREEN_CAPTURE: Integrate as screenshot/recording tool for cognitive perception")
        
        if "gif_encoding" in analysis.capabilities:
            strategy_parts.append("GIF_EXPORT: Use for automated GIF generation in documentation and reports")
        
        if "ui_framework" in analysis.capabilities:
            strategy_parts.append("UI_COMPONENT: Potentially adapt UI components for cognitive dashboard")
        
        # License compliance
        if analysis.license_type and "GPL" in analysis.license_type:
            strategy_parts.append("⚠️ GPL_COMPLIANCE: Ensure GPL license compatibility with project")
        
        return " | ".join(strategy_parts)
    
    def generate_lessons_learned(self, analysis: RepoAnalysis) -> List[str]:
        """Extract lessons learned from ingestion process"""
        lessons = []
        
        # Language diversity
        if len(analysis.languages) > 1:
            lessons.append(f"Multi-language repository with {len(analysis.languages)} languages detected")
        
        # Conversion complexity
        if analysis.conversion_required:
            lessons.append("Code conversion/wrapping required - meta-learning should track conversion patterns")
        
        # Capability mapping
        if len(analysis.capabilities) > 3:
            lessons.append(f"Rich capability set ({len(analysis.capabilities)} capabilities) - suitable for plugin system")
        
        # Integration complexity
        if analysis.plugin_adapter_needed:
            lessons.append("Plugin adapter pattern needed - meta-learning can reuse adapter templates")
        
        # License awareness
        if analysis.license_type:
            lessons.append(f"License compliance check completed: {analysis.license_type}")
        
        return lessons
    
    def ingest_repository(self, repo_url: str, clone_dir: Path) -> RepoAnalysis:
        """Complete ingestion pipeline for external repository"""
        repo_name = repo_url.split("/")[-1].replace(".git", "")
        clone_path = clone_dir / repo_name
        
        print(f"🔄 Ingesting repository: {repo_name}")
        print(f"📦 Source: {repo_url}")
        
        # Step 1: Clone repository
        if not self.clone_repository(repo_url, clone_path):
            raise Exception("Failed to clone repository")
        
        # Step 2: Initialize analysis
        analysis = RepoAnalysis(
            repo_url=repo_url,
            repo_name=repo_name,
            clone_path=clone_path
        )
        
        # Step 3: Analyze languages
        print("🔍 Analyzing language distribution...")
        analysis.languages = self.analyze_languages(clone_path)
        analysis.total_lines = sum(analysis.languages.values())
        print(f"   Languages: {', '.join(f'{k}: {v} lines' for k, v in analysis.languages.items())}")
        
        # Step 4: Detect license
        print("📜 Detecting license...")
        analysis.license_type = self.detect_license(clone_path)
        print(f"   License: {analysis.license_type or 'Not detected'}")
        
        # Step 5: Detect capabilities
        print("🎯 Detecting capabilities...")
        analysis.capabilities = self.detect_capabilities(clone_path)
        print(f"   Capabilities: {', '.join(analysis.capabilities)}")
        
        # Step 6: Extract key components
        print("🔑 Extracting key components...")
        analysis.key_components = self.extract_key_components(clone_path)
        print(f"   Key components: {len(analysis.key_components)} files identified")
        
        # Step 7: Generate integration strategy
        print("🎯 Generating integration strategy...")
        analysis.integration_strategy = self.generate_integration_strategy(analysis)
        print(f"   Strategy: {analysis.integration_strategy}")
        
        # Step 8: Extract lessons learned
        print("📚 Extracting lessons learned...")
        analysis.lessons_learned = self.generate_lessons_learned(analysis)
        analysis.meta_learning_applicable = len(analysis.lessons_learned) > 0
        
        for i, lesson in enumerate(analysis.lessons_learned, 1):
            print(f"   Lesson {i}: {lesson}")
        
        return analysis
    
    def save_analysis(self, analysis: RepoAnalysis) -> Path:
        """Save analysis results to JSON file"""
        output_path = self.output_dir / f"{analysis.repo_name}_analysis.json"
        
        analysis_dict = {
            "repo_url": analysis.repo_url,
            "repo_name": analysis.repo_name,
            "timestamp": datetime.now().isoformat(),
            "languages": analysis.languages,
            "total_lines": analysis.total_lines,
            "license_type": analysis.license_type,
            "capabilities": analysis.capabilities,
            "integration_strategy": analysis.integration_strategy,
            "plugin_adapter_needed": analysis.plugin_adapter_needed,
            "conversion_required": analysis.conversion_required,
            "key_components": analysis.key_components,
            "lessons_learned": analysis.lessons_learned,
            "meta_learning_applicable": analysis.meta_learning_applicable
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_dict, f, indent=2)
        
        print(f"\n✅ Analysis saved to: {output_path}")
        return output_path


def main():
    parser = argparse.ArgumentParser(description="Ingest external repository into cognitive brain")
    parser.add_argument("--repo-url", required=True, help="Repository URL to ingest")
    parser.add_argument("--clone-dir", default="/tmp", help="Directory for cloning repositories")
    parser.add_argument("--output", default="cognitive/ingestion", help="Output directory for analysis")
    
    args = parser.parse_args()
    
    # Initialize ingestor
    output_dir = Path(args.output)
    ingestor = ExternalRepoIngestor(output_dir)
    
    # Ingest repository
    try:
        analysis = ingestor.ingest_repository(args.repo_url, Path(args.clone_dir))
        ingestor.save_analysis(analysis)
        
        print("\n" + "="*60)
        print("🎉 REPOSITORY INGESTION COMPLETE")
        print("="*60)
        print(f"Repository: {analysis.repo_name}")
        print(f"Capabilities: {len(analysis.capabilities)}")
        print(f"Integration Strategy: {analysis.integration_strategy.split('|')[0].strip()}")
        print(f"Meta-Learning Applicable: {'✅ YES' if analysis.meta_learning_applicable else '❌ NO'}")
        print(f"Lessons Learned: {len(analysis.lessons_learned)}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ INGESTION FAILED: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
