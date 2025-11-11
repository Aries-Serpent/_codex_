#!/usr/bin/env python3
"""Enhanced fence fixer with ML-capable language detection.

Implements a hybrid detection strategy:
1. Heuristics (H): File extension, shebang, explicit tags
2. ML Classifier (M): Optional character n-gram based prediction
3. Structural validation (S): Tree-sitter parsing when available

Score = α*H + β*M + γ*S (defaults: α=0.5, β=0.3, γ=0.2)

Honors MD040: All code fences should have a language tag.
"""

import argparse
import json
import pathlib
import re
import sys
from typing import Dict, List, Optional, Tuple

try:
    from markdown_it import MarkdownIt
except ImportError:
    print("Error: markdown-it-py required. Install: pip install markdown-it-py", file=sys.stderr)
    sys.exit(1)

try:
    from pygments.lexers import guess_lexer, guess_lexer_for_filename
    from pygments.util import ClassNotFound
    PYGMENTS_AVAILABLE = True
except ImportError:
    PYGMENTS_AVAILABLE = False
    print("Warning: Pygments not available. Install: pip install Pygments", file=sys.stderr)

try:
    import tree_sitter_languages as tsl
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False

# Language normalization map
LANG_NORMALIZE = {
    "py": "python",
    "sh": "bash",
    "shell": "bash",
    "ps1": "powershell",
    "yml": "yaml",
    "js": "javascript",
    "ts": "typescript",
    "md": "markdown",
    "rst": "restructuredtext",
}

# Heuristic patterns for language detection
LANG_PATTERNS = {
    "python": [
        r"^\s*(from|import)\s+\w+",
        r"^\s*def\s+\w+\s*\(",
        r"^\s*class\s+\w+",
        r"^\s*#\s*!/usr/bin/(env\s+)?python",
    ],
    "bash": [
        r"^\s*#\s*!/bin/(ba)?sh",
        r"^\s*\$\s+",
        r"^\s*(sudo|apt-get|yum|brew)\s+",
        r"^\s*(export|source)\s+\w+",
    ],
    "javascript": [
        r"^\s*(const|let|var)\s+\w+\s*=",
        r"^\s*function\s+\w+\s*\(",
        r"^\s*(import|export)\s+",
    ],
    "json": [
        r"^\s*\{[\s\n]*[\"']",
        r"^\s*\[[\s\n]*\{",
    ],
    "yaml": [
        r"^\s*---\s*$",
        r"^\s*\w+:\s*$",
        r"^\s*-\s+\w+:",
    ],
    "sql": [
        r"^\s*(SELECT|INSERT|UPDATE|DELETE|CREATE)\s+",
    ],
    "xml": [
        r"^\s*<\?xml",
        r"^\s*<!DOCTYPE",
    ],
    "html": [
        r"^\s*<!DOCTYPE\s+html",
        r"^\s*<html[\s>]",
    ],
}


class FenceFixerConfig:
    """Configuration for fence fixer."""
    
    def __init__(self, config_path: Optional[pathlib.Path] = None):
        self.overrides = []
        self.auto_apply_threshold = 0.60
        self.risky_langs = ["bash", "powershell", "yaml"]
        self.require_parse_for = ["bash", "powershell"]
        self.report_json_path = ".reports/fencefix_run.json"
        self.report_md_path = ".reports/fencefix_summary.md"
        self.weights = (0.5, 0.3, 0.2)  # α, β, γ for H, M, S
        
        if config_path and config_path.exists():
            self._load_config(config_path)
    
    def _load_config(self, config_path: pathlib.Path):
        """Load configuration from YAML file."""
        try:
            import yaml
            with open(config_path) as f:
                data = yaml.safe_load(f)
            
            if "overrides" in data:
                self.overrides = data["overrides"]
            if "thresholds" in data:
                t = data["thresholds"]
                self.auto_apply_threshold = t.get("auto_apply", self.auto_apply_threshold)
                self.risky_langs = t.get("risky_langs", self.risky_langs)
                self.require_parse_for = t.get("require_parse_for", self.require_parse_for)
            if "report" in data:
                r = data["report"]
                self.report_json_path = r.get("out_json", self.report_json_path)
                self.report_md_path = r.get("pr_summary_md", self.report_md_path)
        except ImportError:
            print("Warning: PyYAML not available, using defaults", file=sys.stderr)
        except Exception as e:
            print(f"Warning: Error loading config: {e}", file=sys.stderr)


class LanguageDetector:
    """Hybrid language detector with heuristics, ML, and structural validation."""
    
    def __init__(self, config: FenceFixerConfig):
        self.config = config
        self.ml_classifier = None  # Placeholder for future ML integration
    
    def detect_heuristic(self, code: str, filename: Optional[str] = None) -> Tuple[str, float]:
        """Heuristic-based language detection."""
        # Check for shebang
        first_line = code.split('\n')[0] if code else ""
        if first_line.startswith('#!'):
            if 'python' in first_line:
                return ("python", 0.9)
            if 'bash' in first_line or 'sh' in first_line:
                return ("bash", 0.9)
            if 'node' in first_line:
                return ("javascript", 0.9)
        
        # Pattern matching
        for lang, patterns in LANG_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, code, re.I | re.M):
                    return (lang, 0.7)
        
        # Filename-based guess using Pygments
        if PYGMENTS_AVAILABLE and filename:
            try:
                lexer = guess_lexer_for_filename(filename, code)
                lang = lexer.name.lower()
                lang = LANG_NORMALIZE.get(lang, lang)
                return (lang, 0.65)
            except ClassNotFound:
                pass
        
        # Content-based guess using Pygments
        if PYGMENTS_AVAILABLE:
            try:
                lexer = guess_lexer(code)
                lang = lexer.name.lower()
                lang = LANG_NORMALIZE.get(lang, lang)
                return (lang, 0.60)
            except ClassNotFound:
                pass
        
        return ("text", 0.2)
    
    def validate_parse(self, code: str, lang: str) -> Tuple[bool, float]:
        """Structural validation using Tree-sitter."""
        if not TREE_SITTER_AVAILABLE:
            return (True, 0.0)  # Soft pass without tree-sitter
        
        # Map language names to tree-sitter language identifiers
        ts_lang_map = {
            "python": "python",
            "javascript": "javascript",
            "typescript": "typescript",
            "bash": "bash",
            "c": "c",
            "cpp": "cpp",
            "go": "go",
            "java": "java",
            "rust": "rust",
        }
        
        ts_lang = ts_lang_map.get(lang)
        if not ts_lang:
            return (True, 0.0)  # No parser available, soft pass
        
        try:
            parser = tsl.get_parser(ts_lang)
            tree = parser.parse(code.encode('utf-8'))
            has_error = tree.root_node.has_error if tree and tree.root_node else True
            confidence = 0.8 if not has_error else 0.0
            return (not has_error, confidence)
        except Exception:
            return (True, 0.0)  # Soft pass on parser error
    
    def detect(self, code: str, filename: Optional[str] = None) -> Tuple[str, float, Dict]:
        """
        Combined detection using weighted scoring.
        
        Returns:
            (language, confidence, metadata)
        """
        α, β, γ = self.config.weights
        
        # Heuristic score
        h_lang, h_conf = self.detect_heuristic(code, filename)
        
        # ML score (placeholder - returns 0 if not available)
        m_lang, m_conf = ("text", 0.0)
        if self.ml_classifier:
            m_lang, m_conf = self.ml_classifier.predict(code, filename)
        
        # Choose primary candidate (heuristic takes precedence for now)
        primary_lang = h_lang if h_conf >= m_conf else m_lang
        
        # Structural validation
        parse_ok, s_conf = self.validate_parse(code, primary_lang)
        
        # Combined score
        combined_score = α * h_conf + β * m_conf + γ * s_conf
        
        # If parse fails for risky languages, fall back to text
        if not parse_ok and primary_lang in self.config.require_parse_for:
            primary_lang = "text"
            combined_score = 0.3
        
        metadata = {
            "h_lang": h_lang,
            "h_conf": h_conf,
            "m_lang": m_lang,
            "m_conf": m_conf,
            "parse_ok": parse_ok,
            "s_conf": s_conf,
            "combined_score": combined_score,
        }
        
        return (primary_lang, combined_score, metadata)


class FenceFixer:
    """Main fence fixer with logging and reporting."""
    
    def __init__(self, config: FenceFixerConfig, dry_run: bool = False, verbose: bool = False):
        self.config = config
        self.dry_run = dry_run
        self.verbose = verbose
        self.detector = LanguageDetector(config)
        self.log_entries: List[Dict] = []
        self.md_parser = MarkdownIt()
    
    def fix_file(self, path: pathlib.Path) -> Tuple[bool, int]:
        """Fix fences in a single file."""
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, IOError) as e:
            if self.verbose:
                print(f"Warning: Could not read {path}: {e}", file=sys.stderr)
            return (False, 0)
        
        original_text = text
        fixes_made = 0
        
        # Use regex approach for simplicity (markdown-it token mapping is complex)
        fence_pattern = r'^(```|~~~)(\w*)\s*\n(.*?)\n\1\s*$'
        
        def replace_fence(match):
            nonlocal fixes_made
            fence_marker = match.group(1)
            existing_lang = match.group(2)
            code = match.group(3)
            
            # Skip if already has language tag
            if existing_lang:
                return match.group(0)
            
            # Detect language
            lang, conf, metadata = self.detector.detect(code, path.name)
            
            # Log entry
            entry = {
                "file": str(path.relative_to(path.cwd()) if path.is_absolute() else path),
                "predicted_lang": lang,
                "confidence": conf,
                "metadata": metadata,
                "action": "auto_apply" if conf >= self.config.auto_apply_threshold else "review",
            }
            self.log_entries.append(entry)
            
            # Apply fix if confidence is high enough
            if conf >= self.config.auto_apply_threshold:
                fixes_made += 1
                return f"{fence_marker}{lang}\n{code}\n{fence_marker}"
            
            # Otherwise, mark for review but don't change
            return match.group(0)
        
        text = re.sub(fence_pattern, replace_fence, text, flags=re.MULTILINE | re.DOTALL)
        
        # Write back if changed
        if text != original_text and not self.dry_run:
            path.write_text(text, encoding="utf-8")
            return (True, fixes_made)
        
        return (text != original_text, fixes_made)
    
    def fix_paths(self, paths: List[pathlib.Path]) -> Dict:
        """Fix all markdown files in given paths."""
        stats = {
            "files_scanned": 0,
            "files_changed": 0,
            "total_fixes": 0,
            "review_queue": 0,
        }
        
        for path in paths:
            path_obj = pathlib.Path(path)
            
            if path_obj.is_file() and path_obj.suffix == '.md':
                files = [path_obj]
            else:
                files = list(path_obj.rglob("*.md"))
            
            for md_file in files:
                # Skip hidden directories
                if any(part.startswith(".") for part in md_file.parts):
                    continue
                
                stats["files_scanned"] += 1
                changed, fixes = self.fix_file(md_file)
                
                if changed:
                    stats["files_changed"] += 1
                    stats["total_fixes"] += fixes
                
                if self.verbose and fixes > 0:
                    mode = "Would fix" if self.dry_run else "Fixed"
                    print(f"{mode} {fixes} fence(s) in {md_file}")
        
        # Count review queue items
        stats["review_queue"] = sum(1 for e in self.log_entries if e["action"] == "review")
        
        return stats
    
    def generate_reports(self):
        """Generate JSON and Markdown reports."""
        # Ensure report directory exists
        json_path = pathlib.Path(self.config.report_json_path)
        md_path = pathlib.Path(self.config.report_md_path)
        
        json_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.parent.mkdir(parents=True, exist_ok=True)
        
        # JSON report
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.log_entries, f, indent=2)
        
        # Markdown summary
        total_blocks = len(self.log_entries)
        auto_applied = sum(1 for e in self.log_entries if e["action"] == "auto_apply")
        review_needed = sum(1 for e in self.log_entries if e["action"] == "review")
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write("# Fence Fixer Run Summary\n\n")
            f.write(f"**Total blocks processed**: {total_blocks}\n")
            f.write(f"**Auto-applied**: {auto_applied}\n")
            f.write(f"**Review needed**: {review_needed}\n\n")
            
            if review_needed > 0:
                f.write("## Blocks Needing Review\n\n")
                f.write("|File|Lang|Conf|Reason|\n")
                f.write("|----|----|----:|------|\n")
                for e in self.log_entries:
                    if e["action"] == "review":
                        conf = e["confidence"]
                        reason = "Low confidence" if conf < self.config.auto_apply_threshold else "Other"
                        f.write(f"|{e['file']}|{e['predicted_lang']}|{conf:.2f}|{reason}|\n")
        
        if self.verbose:
            print("\nReports generated:")
            print(f"  JSON: {json_path}")
            print(f"  Markdown: {md_path}")


def main():
    parser = argparse.ArgumentParser(description="Fix markdown code fence language tags")
    parser.add_argument("paths", nargs="+", help="Paths to scan for markdown files")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--config", type=pathlib.Path, help="Path to .fencefixer.yml config file")
    parser.add_argument("--report", action="store_true", help="Generate reports")
    
    args = parser.parse_args()
    
    # Load configuration
    config = FenceFixerConfig(args.config)
    
    # Create fixer
    fixer = FenceFixer(config, dry_run=args.dry_run, verbose=args.verbose)
    
    # Fix files
    stats = fixer.fix_paths([pathlib.Path(p) for p in args.paths])
    
    # Generate reports if requested
    if args.report or args.verbose:
        fixer.generate_reports()
    
    # Print summary
    mode = "dry-run" if args.dry_run else "fixed"
    print(f"\nSummary ({mode}):")
    print(f"  Files scanned: {stats['files_scanned']}")
    print(f"  Files changed: {stats['files_changed']}")
    print(f"  Total fixes: {stats['total_fixes']}")
    print(f"  Review queue: {stats['review_queue']}")
    
    return 0 if stats["review_queue"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
