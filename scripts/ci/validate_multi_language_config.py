#!/usr/bin/env python3
"""
Multi-Language Configuration Validator

Expands the Rust Cargo.toml validation pattern to other language ecosystems:
- Python: pyproject.toml extras_require
- Node.js: package.json optionalDependencies
- Go: build tags
- C/C++: preprocessor directives

Based on learnings from January 19, 2026 Rust incident.
"""

import json
import re
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None


class Language(Enum):
    """Supported language ecosystems."""
    RUST = "rust"
    PYTHON = "python"
    NODEJS = "nodejs"
    GO = "go"
    CPP = "cpp"


@dataclass
class ConfigIssue:
    """Represents a configuration validation issue."""
    feature_name: str
    issue_type: str
    location: str
    severity: str
    description: str
    fix_suggestion: Optional[str] = None


class MultiLanguageValidator:
    """Validates configuration features across multiple language ecosystems."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.issues: List[ConfigIssue] = []

    def validate_all(self) -> Tuple[bool, List[ConfigIssue]]:
        """Validate all detected language configurations."""
        validators = {
            Language.RUST: self._validate_rust,
            Language.PYTHON: self._validate_python,
            Language.NODEJS: self._validate_nodejs,
            Language.GO: self._validate_go,
            Language.CPP: self._validate_cpp,
        }

        for lang, validator in validators.items():
            if self._language_detected(lang):
                print(f"🔍 Validating {lang.value} configuration...")
                validator()

        return len(self.issues) == 0, self.issues

    def _language_detected(self, lang: Language) -> bool:
        """Check if a language is used in the repository."""
        detection_files = {
            Language.RUST: "Cargo.toml",
            Language.PYTHON: "pyproject.toml",
            Language.NODEJS: "package.json",
            Language.GO: "go.mod",
            Language.CPP: ["CMakeLists.txt", "Makefile"],
        }

        files = detection_files[lang]
        if isinstance(files, str):
            files = [files]

        return any((self.repo_root / f).exists() for f in files)

    def _validate_rust(self):
        """Validate Rust Cargo.toml features (existing implementation)."""
        cargo_toml = self.repo_root / "Cargo.toml"
        if not cargo_toml.exists():
            return

        # Use existing validation logic from same directory
        # Note: Import here to avoid issues if validate_cargo_features not available
        try:
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent))
            from validate_cargo_features import validate_cargo_features
            is_valid, errors = validate_cargo_features(cargo_toml)
        except ImportError:
            print("⚠️  validate_cargo_features module not available, skipping Rust validation")
            return

        if not is_valid:
            for error in errors:
                self.issues.append(ConfigIssue(
                    feature_name="rust_feature",
                    issue_type="validation_error",
                    location="Cargo.toml",
                    severity="high",
                    description=error
                ))

    def _validate_python(self):
        """Validate Python pyproject.toml extras_require."""
        pyproject = self.repo_root / "pyproject.toml"
        if not pyproject.exists():
            return

        if not tomllib:
            print("⚠️  TOML parser not available for Python validation")
            return

        with open(pyproject, 'rb') as f:
            data = tomllib.load(f)

        # Check extras_require
        extras = data.get('project', {}).get('optional-dependencies', {})

        # Find Python files that use extras
        python_files = list(self.repo_root.glob('**/*.py'))
        used_extras = set()

        for py_file in python_files:
            try:
                content = py_file.read_text()
                # Look for setuptools extras_require usage or import guards
                extras_matches = re.findall(r'extras_require\s*=\s*\[[\'"]([\w-]+)[\'"]\]', content)
                used_extras.update(extras_matches)
            except Exception:
                continue

        # Check for undeclared extras
        for extra in used_extras:
            if extra not in extras:
                self.issues.append(ConfigIssue(
                    feature_name=extra,
                    issue_type="missing_extra",
                    location="pyproject.toml",
                    severity="high",
                    description=f"Extra '{extra}' used in code but not declared in pyproject.toml",
                    fix_suggestion=f"Add '[project.optional-dependencies]' section with '{extra} = [...]'"
                ))

        print(f"   ✓ Found {len(extras)} declared extras")
        if used_extras:
            print(f"   ✓ Found {len(used_extras)} used extras: {', '.join(used_extras)}")

    def _validate_nodejs(self):
        """Validate Node.js package.json optionalDependencies."""
        package_json = self.repo_root / "package.json"
        if not package_json.exists():
            return

        with open(package_json) as f:
            data = json.load(f)

        optional_deps = data.get('optionalDependencies', {})

        # Find JavaScript/TypeScript files that conditionally require packages
        js_files = list(self.repo_root.glob('**/*.js')) + list(self.repo_root.glob('**/*.ts'))
        used_optional = set()

        for js_file in js_files:
            try:
                content = js_file.read_text()
                # Look for optional require() or import
                for pkg in optional_deps:
                    if f"require('{pkg}')" in content or f'require("{pkg}")' in content:
                        used_optional.add(pkg)
                    if f"from '{pkg}'" in content or f'from "{pkg}"' in content:
                        used_optional.add(pkg)
            except Exception:
                continue

        # Check for unused optional dependencies
        unused = set(optional_deps.keys()) - used_optional
        if unused:
            for pkg in unused:
                self.issues.append(ConfigIssue(
                    feature_name=pkg,
                    issue_type="orphaned_dependency",
                    location="package.json",
                    severity="low",
                    description=f"Optional dependency '{pkg}' declared but not used",
                    fix_suggestion="Remove from optionalDependencies or use in code"
                ))

        print(f"   ✓ Found {len(optional_deps)} optional dependencies")
        print(f"   ✓ {len(used_optional)} are actively used")

    def _validate_go(self):
        """Validate Go build tags."""
        go_files = list(self.repo_root.glob('**/*.go'))
        if not go_files:
            return

        used_tags = set()

        # Find declared build tags in files
        for go_file in go_files:
            try:
                content = go_file.read_text()
                # Look for //go:build directives
                build_tags = re.findall(r'//go:build\s+([\w\s&|!()]+)', content)
                for tag_expr in build_tags:
                    # Extract individual tags
                    tags = re.findall(r'\b(\w+)\b', tag_expr)
                    used_tags.update(tags)
            except Exception:
                continue

        # Check for common Go build tags that should be documented
        common_tags = {'linux', 'darwin', 'windows', 'amd64', 'arm64', 'cgo', 'debug', 'release'}
        undocumented = used_tags & common_tags

        if undocumented:
            print(f"   ✓ Found {len(used_tags)} build tags")
            print(f"   ℹ️  Consider documenting tags: {', '.join(undocumented)}")

    def _validate_cpp(self):
        """Validate C/C++ preprocessor directives."""
        cpp_files = (list(self.repo_root.glob('**/*.cpp')) +
                     list(self.repo_root.glob('**/*.h')) +
                     list(self.repo_root.glob('**/*.cc')))

        if not cpp_files:
            return

        defined_macros = set()
        used_macros = set()

        for cpp_file in cpp_files:
            try:
                content = cpp_file.read_text()
                # Find #define directives
                defines = re.findall(r'#define\s+(\w+)', content)
                defined_macros.update(defines)

                # Find #ifdef, #ifndef, #if defined usage
                ifdefs = re.findall(r'#ifn?def\s+(\w+)', content)
                if_defined = re.findall(r'#if\s+defined\((\w+)\)', content)
                used_macros.update(ifdefs)
                used_macros.update(if_defined)
            except Exception:
                continue

        # Check for undefined macros
        undefined = used_macros - defined_macros
        common_macros = {'DEBUG', 'NDEBUG', 'WIN32', 'LINUX', '__cplusplus'}
        undefined = undefined - common_macros

        if undefined:
            for macro in undefined:
                self.issues.append(ConfigIssue(
                    feature_name=macro,
                    issue_type="undefined_macro",
                    location="C/C++ source files",
                    severity="medium",
                    description=f"Macro '{macro}' used in #ifdef but not #defined",
                    fix_suggestion=f"Add #define {macro} or define in build system"
                ))

        print(f"   ✓ Found {len(defined_macros)} defined macros")
        print(f"   ✓ Found {len(used_macros)} used macros")


def main():
    """Main validation function."""
    repo_root = Path(__file__).parent.parent.parent

    print("🔍 Multi-Language Configuration Validator")
    print(f"   Repository: {repo_root}")
    print()

    validator = MultiLanguageValidator(repo_root)
    is_valid, issues = validator.validate_all()

    print()
    if is_valid:
        print("✅ All language configurations validated successfully!")
        return 0
    print(f"❌ Found {len(issues)} configuration issues:")
    print()

    for issue in issues:
        severity_emoji = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🔵',
        }.get(issue.severity, '⚪')

        print(f"{severity_emoji} [{issue.severity.upper()}] {issue.issue_type}")
        print(f"   Feature: {issue.feature_name}")
        print(f"   Location: {issue.location}")
        print(f"   Issue: {issue.description}")
        if issue.fix_suggestion:
            print(f"   Fix: {issue.fix_suggestion}")
        print()

    return 1


if __name__ == '__main__':
    sys.exit(main())
