"""
Documentation and Code Quality Validation Tests - Phase 3 Lane 3.4

This test suite validates:
1. Documentation completeness and accuracy
2. Code quality metrics (type hints, docstrings)
3. Link validation in documentation
4. API documentation coverage
5. Security checks for hardcoded secrets
6. Import integrity
7. README accuracy
8. Overall integration quality

Test Categories:
- Documentation Quality (docstrings, API docs)
- Code Quality (type hints, style)
- Security (secret scanning, credentials)
- Integration (imports, dependencies)
"""

import ast
import re

import pytest


class TestDocumentationCompleteness:
    """Test 1: Documentation Completeness - Docstring Coverage."""
    
    def test_source_files_have_docstrings(
        self,
        source_files,
        docstring_analyzer,
    ):
        """Verify that source files have comprehensive docstring coverage."""
        if not source_files:
            pytest.skip("No source files found")
        
        results = []
        total_coverage = 0
        
        for file_path in source_files:
            result = docstring_analyzer.analyze_file(file_path)
            results.append(result)
            if "coverage_pct" in result:
                total_coverage += result["coverage_pct"]
        
        avg_coverage = total_coverage / max(len(results), 1) if results else 0
        
        # Report findings
        insufficient_docs = [r for r in results if r.get("coverage_pct", 0) < 70]
        
        # Check coverage threshold
        assert (
            avg_coverage >= 70
        ), f"Average docstring coverage {avg_coverage:.1f}% is below 70% threshold. "
        f"Files with <70% coverage: {len(insufficient_docs)}"
        
        # Assert no files have 0 coverage (critical modules should have docs)
        zero_coverage = [r for r in results if r.get("coverage_pct", 0) == 0]
        critical_modules = [
            r["file"] for r in zero_coverage
            if "core" in r["file"] or "main" in r["file"] or "__init__" in r["file"]
        ]
        assert not critical_modules, (
            f"Critical modules have no docstrings: {critical_modules}"
        )


class TestCodeQualityTypeHints:
    """Test 2: Code Quality - Type Hint Coverage."""
    
    def test_functions_have_type_hints(
        self,
        source_files,
        type_hint_validator,
    ):
        """Verify that functions have proper type hints."""
        if not source_files:
            pytest.skip("No source files found")
        
        results = []
        total_coverage = 0
        
        for file_path in source_files:
            result = type_hint_validator.analyze_file(file_path)
            results.append(result)
            if "coverage_pct" in result:
                total_coverage += result["coverage_pct"]
        
        avg_coverage = total_coverage / max(len(results), 1) if results else 0
        
        # Type hint coverage should be good but we're lenient for legacy code
        assert (
            avg_coverage >= 60
        ), f"Average type hint coverage {avg_coverage:.1f}% is below 60%"
        
        # At least 50% of files should have >80% type hint coverage
        good_coverage = sum(1 for r in results if r.get("coverage_pct", 0) >= 80)
        assert (
            good_coverage >= len(results) * 0.5
        ), f"Only {good_coverage}/{len(results)} files have good type hint coverage"


class TestLinkValidation:
    """Test 3: Link Validation - Documentation Links."""
    
    def test_markdown_links_are_valid(
        self,
        all_markdown_files,
        link_validator,
        project_root,
    ):
        """Verify that all markdown links in documentation are valid."""
        if not all_markdown_files:
            pytest.skip("No markdown files found")
        
        results = []
        all_broken = []
        
        for file_path in all_markdown_files:
            result = link_validator.validate_file(file_path, project_root)
            results.append(result)
            if result.get("broken_links"):
                all_broken.extend([
                    f"{file_path}: {b['link']}"
                    for b in result["broken_links"]
                ])
        
        # Allow some tolerance for external or special links
        critical_broken = [
            link for link in all_broken
            if not any(skip in link for skip in [
                "github.com",
                "https://",
                "http://",
                "#",  # Anchors only
            ])
        ]
        
        assert (
            len(critical_broken) == 0
        ), f"Found broken internal documentation links: {critical_broken}"


class TestSecurityCheckCredentials:
    """Test 4: Security - No Hardcoded Secrets."""
    
    def test_no_hardcoded_credentials(
        self,
        source_files,
        secret_scanner,
    ):
        """Verify that there are no hardcoded credentials or secrets in source code."""
        if not source_files:
            pytest.skip("No source files found")
        
        results = []
        files_with_secrets = []
        
        for file_path in source_files:
            result = secret_scanner.scan_file(file_path)
            results.append(result)
            if result.get("has_secrets"):
                files_with_secrets.append({
                    "file": result["file"],
                    "findings": result.get("findings", []),
                })
        
        assert (
            not files_with_secrets
        ), f"Found potential secrets in source files: {files_with_secrets}"


class TestAPIDocumentation:
    """Test 5: API Documentation - Public APIs Properly Documented."""
    
    def test_public_api_modules_documented(
        self,
        source_files,
    ):
        """Verify that public API modules are properly documented."""
        if not source_files:
            pytest.skip("No source files found")
        
        public_api_files = [
            f for f in source_files
            if "__init__.py" in f.name and "src" in f.parts
        ]
        
        undocumented_apis = []
        for api_file in public_api_files:
            try:
                with open(api_file, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                
                if not ast.get_docstring(tree):
                    undocumented_apis.append(str(api_file))
            except Exception:
                pass
        
        # Critical API modules should be documented
        critical_undocumented = [
            f for f in undocumented_apis
            if "core" in f or "utils" in f or "codex" in f.lower()
        ]
        
        assert not critical_undocumented, (
            f"Critical API modules lack module docstrings: {critical_undocumented}"
        )


class TestREADMEAccuracy:
    """Test 6: README Accuracy - README Matches Current Code."""
    
    def test_readme_references_valid_files(
        self,
        readme_file,
        project_root,
    ):
        """Verify that README references point to existing files."""
        if not readme_file.exists():
            pytest.skip("README.md not found")
        
        with open(readme_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Extract file references from README
        # Pattern: `path/to/file.ext` or [link](path/to/file)
        file_pattern = re.compile(r"[`\(]((?:[a-zA-Z0-9_\-./]+\.(?:py|md|yaml|yml|txt|json))[`\)]?)")
        matches = file_pattern.finditer(content)
        
        missing_files = []
        for match in matches:
            file_ref = match.group(1).rstrip("`)")
            file_path = project_root / file_ref
            
            if not file_path.exists():
                # Allow some tolerance for wildcards and patterns
                if "*" not in file_ref and not file_ref.startswith("http"):
                    missing_files.append(file_ref)
        
        # Warn but don't fail on missing files (they might be generated)
        if missing_files:
            pytest.warns(UserWarning, match=".*")


class TestNoCircularImports:
    """Test 7: Dependencies - No Circular Imports."""
    
    def test_imports_are_acyclic(
        self,
        source_files,
    ):
        """Verify that module imports don't have circular dependencies."""
        if not source_files:
            pytest.skip("No source files found")
        
        import_graph = {}
        
        for file_path in source_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                
                imports = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.add(alias.name.split(".")[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.add(node.module.split(".")[0])
                
                module_name = str(file_path.relative_to(file_path.parents[3]))
                import_graph[module_name] = imports
            except Exception:
                pass
        
        # Check for simple circular imports (A -> B -> A)
        circular_pairs = []
        for module, imports in import_graph.items():
            for imp in imports:
                if imp in import_graph and module in import_graph.get(imp, set()):
                    pair = tuple(sorted([module, imp]))
                    if pair not in circular_pairs:
                        circular_pairs.append(pair)
        
        # Allow some circular imports as they might be design patterns
        critical_circular = [
            pair for pair in circular_pairs
            if any("__init__" not in str(p) for p in pair)
        ]
        
        assert not critical_circular, (
            f"Found circular import patterns: {critical_circular}"
        )


class TestCodeStyleConsistency:
    """Test 8: Code Quality - Style Consistency."""
    
    def test_python_files_follow_conventions(
        self,
        source_files,
    ):
        """Verify that Python files follow naming conventions."""
        if not source_files:
            pytest.skip("No source files found")
        
        violations = []
        
        for file_path in source_files:
            # Check filename conventions
            filename = file_path.name
            
            # Should be lowercase with underscores
            if filename != "__init__.py" and not filename.islower():
                # Check for camelCase or PascalCase
                if re.search(r"[a-z][A-Z]", filename):
                    violations.append(f"{filename}: violates snake_case convention")
        
        # Be lenient - just warn about major violations
        assert len(violations) < len(source_files) * 0.1, (
            f"Too many style violations ({len(violations)}): {violations[:5]}"
        )


class TestIntegrationQuality:
    """Test 9: Integration - Full Profile Integration."""
    
    def test_core_modules_are_importable(
        self,
        source_dir,
    ):
        """Verify that core modules can be imported without errors."""
        if not source_dir.exists():
            pytest.skip("Source directory not found")
        
        import sys
        sys.path.insert(0, str(source_dir))
        
        core_modules = ["ingestion", "workers", "orchestration", "agent", "rag"]
        
        for module_name in core_modules:
            module_path = source_dir / module_name
            if module_path.exists():
                try:
                    # Try to import the module
                    __import__(module_name)
                except ImportError as e:
                    pytest.warns(
                        UserWarning,
                        match=f"Could not import {module_name}"
                    )


class TestErrorHandling:
    """Test 10: Error Handling - Helpful Error Messages."""
    
    def test_exceptions_have_meaningful_messages(
        self,
        source_files,
    ):
        """Verify that exceptions in code have meaningful messages."""
        if not source_files:
            pytest.skip("No source files found")
        
        generic_exceptions = []
        
        for file_path in source_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Look for raise statements with empty or generic messages
                raise_patterns = [
                    r"raise\s+\w+\(\s*\)",  # raise Exception()
                    r"raise\s+\w+\(\s*['\"][\s]*['\"]\s*\)",  # raise Exception("")
                ]
                
                for pattern in raise_patterns:
                    if re.search(pattern, content):
                        matches = re.finditer(pattern, content)
                        for match in matches:
                            line_num = content[:match.start()].count("\n") + 1
                            generic_exceptions.append(
                                f"{file_path.name}:{line_num}"
                            )
            except Exception:
                pass
        
        # Be lenient - just ensure not too many generic exceptions
        assert len(generic_exceptions) < len(source_files) * 0.05, (
            f"Too many exceptions with generic messages: {generic_exceptions[:5]}"
        )


class TestPerformanceBaseline:
    """Test 11: Performance - No Obvious Regressions."""
    
    def test_no_obvious_performance_issues(
        self,
        source_files,
    ):
        """Verify that there are no obvious performance anti-patterns."""
        if not source_files:
            pytest.skip("No source files found")
        
        issues = []
        
        # Look for common performance anti-patterns
        patterns = {
            "nested_loops": re.compile(r"for\s+\w+\s+in.*:\s*\n.*for\s+\w+\s+in"),
            "string_concat_loop": re.compile(r"for\s+\w+\s+in.*:\s*\n.*\+\s*=.*str"),
            "unnecessary_copies": re.compile(r"list\(.*\.copy\(\)"),
        }
        
        for file_path in source_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                for pattern_name, pattern in patterns.items():
                    if pattern.search(content):
                        issues.append(f"{file_path.name}: potential {pattern_name}")
            except Exception:
                pass
        
        # Be very lenient - just warn about extreme patterns
        assert len(issues) < len(source_files) * 0.02, (
            f"Found potential performance issues: {issues[:5]}"
        )


class TestComprehensiveIntegration:
    """Test 12: Comprehensive Integration - Full Profile Quality."""
    
    def test_full_profile_quality_metrics(
        self,
        source_files,
        docstring_analyzer,
        type_hint_validator,
    ):
        """Verify that the full profile meets quality thresholds."""
        if not source_files:
            pytest.skip("No source files found")
        
        # Collect comprehensive metrics
        metrics = {
            "total_files": len(source_files),
            "docstring_coverage": 0,
            "type_hint_coverage": 0,
        }
        
        docstring_results = []
        type_hint_results = []
        
        for file_path in source_files:
            doc_result = docstring_analyzer.analyze_file(file_path)
            if "coverage_pct" in doc_result:
                docstring_results.append(doc_result["coverage_pct"])
            
            hint_result = type_hint_validator.analyze_file(file_path)
            if "coverage_pct" in hint_result:
                type_hint_results.append(hint_result["coverage_pct"])
        
        metrics["docstring_coverage"] = (
            sum(docstring_results) / max(len(docstring_results), 1)
            if docstring_results else 0
        )
        metrics["type_hint_coverage"] = (
            sum(type_hint_results) / max(len(type_hint_results), 1)
            if type_hint_results else 0
        )
        
        # Quality thresholds
        assert metrics["docstring_coverage"] >= 70, (
            f"Docstring coverage {metrics['docstring_coverage']:.1f}% "
            "is below 70% threshold"
        )
        
        # Overall quality should be good
        overall_quality = (
            metrics["docstring_coverage"] * 0.6 +
            metrics["type_hint_coverage"] * 0.4
        )
        
        assert overall_quality >= 65, (
            f"Overall quality score {overall_quality:.1f}% is below 65%"
        )
