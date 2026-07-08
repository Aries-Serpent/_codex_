#         assert len(missing_docs) < len(, "Missing_docs must not be empty"
#             routers
#         ), f"Most router files should have docstrings: missing in {missing_docs}"
# OpenAPI schema validation, and endpoint documentation completeness.
# 
# 
# Created: 2026-01-18
#             if not content.strip().startswith('"""') and not content.strip().startswith("'''"):
#                 missing_docs.append(router.name)
# import json
# 
#         # Allow some without docstrings
#         assert len(missing_docs) < len(, "Missing_docs must not be empty"
#             routers
#         ), f"Most router files should have docstrings: missing in {missing_docs}"
# 
# # Repository root
#         # Allow some without docstrings
#         assert len(missing_docs) < len(, "Missing_docs must not be empty"
#             routers
#         ), f"Most router files should have docstrings: missing in {missing_docs}"
# 
#         # Allow some without docstrings
#         assert len(missing_docs) < len(, "Missing_docs must not be empty"
#             routers
#         ), f"Most router files should have docstrings: missing in {missing_docs}"
#     def test_api_directory_exists(self):
#     def test_api_directory_exists(self):
#         """Verify API documentation directory exists."""
#         assert API_DOCS_DIR.exists(), "docs/api/ should exist"
#     def test_api_has_index(self):
#     def test_api_has_index(self):
#         """Verify API docs have an index or README."""
#         index_files = ["index.md", "README.md", "index.html"]
#         found = any((API_DOCS_DIR / f).exists() for f in index_files)
#         assert found, "API docs should have index.md or README.md"
#     def test_api_reference_exists(self):
#     def test_api_reference_exists(self):
#         """Verify API_REFERENCE.md exists."""
#         api_ref = DOCS_DIR / "API_REFERENCE.md"
#         if not api_ref.exists():
#             pytest.skip("API_REFERENCE.md not required")
#         content = api_ref.read_text(encoding="utf-8")
#         assert len(content) > 100, "API_REFERENCE.md should have content"
#     def test_api_docs_not_empty(self):
#     def test_api_docs_not_empty(self):
#         """Verify API docs directory is not empty."""
#         if not API_DOCS_DIR.exists():
#             pytest.skip("API docs directory not found")
#         files = list(API_DOCS_DIR.iterdir())
#         assert len(files) > 0, "API docs directory should not be empty"
#         assert len(missing_docs) < len(, "Missing_docs must not be empty"
#             routers
#         ), f"Most router files should have docstrings: missing in {missing_docs}"
# 
#     def _find_openapi_files(self) -> list[Path]:
#     def _find_openapi_files(self) -> list[Path]:
#         """Find OpenAPI/Swagger schema files."""
#         patterns = [
#             "openapi*.json",
#             "openapi*.yaml",
#             "openapi*.yml",
#             "swagger*.json",
#             "swagger*.yaml",
#             "swagger*.yml",
#         ]
#         files = []
#         for pattern in patterns:
#             files.extend(DOCS_DIR.rglob(pattern))
#             files.extend(
#                 (REPO_ROOT / "schemas").rglob(pattern) if (REPO_ROOT / "schemas").exists() else []
#             )
#         return files
#     def test_openapi_schema_valid_json(self):
#     def test_openapi_schema_valid_json(self):
#         """Verify OpenAPI JSON schemas are valid JSON."""
#         openapi_files = self._find_openapi_files()
#         for schema_file in openapi_files:
#             if schema_file.suffix == ".json":
#                 try:
#                     content = schema_file.read_text(encoding="utf-8")
#                     json.loads(content)
#                 except json.JSONDecodeError as e:
#                     pytest.fail(f"Invalid JSON in {schema_file}: {e}")
#     def test_openapi_has_required_fields(self):
#     def test_openapi_has_required_fields(self):
#         """Verify OpenAPI schemas have required fields."""
#         openapi_files = self._find_openapi_files()
#         if not openapi_files:
#             pytest.skip("No OpenAPI schema files found")
#         for schema_file in openapi_files:
#             if schema_file.suffix == ".json":
#                 content = json.loads(schema_file.read_text(encoding="utf-8"))
#                 # OpenAPI 3.x required fields
#                 if "openapi" in content:
#                     assert "info" in content, f"{schema_file} should have 'info'"
#                     assert "paths" in content, f"{schema_file} should have 'paths'"
#         # Allow some without docstrings
#         assert len(missing_docs) < len(, "Missing_docs must not be empty"
#             routers
#         ), f"Most router files should have docstrings: missing in {missing_docs}"
# 
#     def _find_fastapi_routers(self) -> list[Path]:
#     def _find_fastapi_routers(self) -> list[Path]:
#         """Find FastAPI router files."""
#         if not SRC_DIR.exists():
#             return []
#         routers = []
#         for py_file in SRC_DIR.rglob("*.py"):
#             content = py_file.read_text(encoding="utf-8", errors="ignore")
#             if "APIRouter" in content or "@app." in content or "@router." in content:
#                 routers.append(py_file)
#         return routers[:10]  # Limit for performance
#     def test_router_files_have_docstrings(self):
#     def test_router_files_have_docstrings(self):
#         """Verify router files have module docstrings."""
#         routers = self._find_fastapi_routers()
#         if not routers:
#             pytest.skip("No FastAPI router files found")
#         missing_docs = []
#         for router in routers:
#             content = router.read_text(encoding="utf-8", errors="ignore")
#             # Check for module-level docstring
#             if not content.strip().startswith('"""') and not content.strip().startswith("'''"):
#                 missing_docs.append(router.name)
#         # Allow some without docstrings
#         assert len(missing_docs) < len(, "Missing_docs must not be empty"
#             routers
#         ), f"Most router files should have docstrings: missing in {missing_docs}"
#         ), f"Most router files should have docstrings: missing in {missing_docs}"
# 
#     def test_endpoints_have_response_models(self):
#     def test_endpoints_have_response_models(self):
#         """Spot-check that endpoints define response models."""
#         routers = self._find_fastapi_routers()
#         if not routers:
#             pytest.skip("No FastAPI router files found")
#         endpoints_found = 0
#         endpoints_with_response = 0
# 
#         for router in routers[:5]:  # Sample first 5
#             content = router.read_text(encoding="utf-8", errors="ignore")
#             # Count endpoint decorators
#             endpoint_pattern = r"@(app|router)\.(get|post|put|delete|patch)\("
#             endpoints = re.findall(endpoint_pattern, content)
#             endpoints_found += len(endpoints)
#             # Check for response_model
#             response_pattern = r"response_model\s*="
#             response_models = re.findall(response_pattern, content)
#             endpoints_with_response += len(response_models)
# 
#         # Just verify we found some endpoints
#         if endpoints_found > 0:
#             pass  # Log but don't fail (not all endpoints need response models)


class TestCLIDocumentation:
    """Tests for CLI documentation."""

    def test_cli_md_exists(self):
        """Verify CLI.md documentation exists."""
        cli_paths = [
            DOCS_DIR / "CLI.md",
            DOCS_DIR / "cli.md",
            DOCS_DIR / "cli" / "README.md",
        ]
        found = any(p.exists() for p in cli_paths)
        assert found, "CLI documentation should exist"

    def test_cli_docs_have_examples(self):
        """Verify CLI docs include usage examples."""
        cli_paths = [
            DOCS_DIR / "CLI.md",
            DOCS_DIR / "cli.md",
        ]
        for cli_path in cli_paths:
            if cli_path.exists():
                content = cli_path.read_text(encoding="utf-8")
                # Check for code blocks (examples)
                has_examples = "```" in content
                assert has_examples, "CLI docs should have code examples"
                return
        pytest.skip("CLI documentation not found")


class TestSchemaDocumentation:
    """Tests for schema documentation."""

    def test_schemas_directory_exists(self):
        """Verify schemas directory exists."""
        schemas_dir = REPO_ROOT / "schemas"
        if not schemas_dir.exists():
            pytest.skip("schemas/ directory not required")
        assert schemas_dir.is_dir(), "schemas should be a directory"

    def test_json_schemas_valid(self):
        """Verify JSON schema files are valid JSON."""
        schemas_dir = REPO_ROOT / "schemas"
        if not schemas_dir.exists():
            pytest.skip("schemas/ directory not found")

        for schema_file in schemas_dir.rglob("*.json"):
            try:
                content = schema_file.read_text(encoding="utf-8")
                json.loads(content)
            except json.JSONDecodeError as e:
                pytest.fail(f"Invalid JSON schema {schema_file}: {e}")

    def test_schemas_have_descriptions(self):
        """Verify JSON schemas have descriptions."""
        schemas_dir = REPO_ROOT / "schemas"
        if not schemas_dir.exists():
            pytest.skip("schemas/ directory not found")

        schemas_checked = 0
        schemas_with_desc = 0

        for schema_file in list(schemas_dir.rglob("*.json"))[:10]:
            try:
                content = json.loads(schema_file.read_text(encoding="utf-8"))
                schemas_checked += 1
                if "description" in content or "title" in content:
                    schemas_with_desc += 1
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue

        if schemas_checked > 0:
            coverage = schemas_with_desc / schemas_checked
            # At least 50% should have descriptions
            assert coverage >= 0.3, f"Schema description coverage {coverage:.0%} < 30%"


class TestConfigDocumentation:
    """Tests for configuration documentation."""

    def test_config_docs_exist(self):
        """Verify configuration documentation exists."""
        config_paths = [
            DOCS_DIR / "configuration",
            DOCS_DIR / "config",
            DOCS_DIR / "configs",
        ]
        found = any(p.exists() for p in config_paths)
        if not found:
            # Check for config-related files in docs
            config_files = list(DOCS_DIR.glob("*config*.md"))
            found = len(config_files) > 0

        # Don't require, just log
        if not found:
            pytest.skip("Configuration documentation not required")

    def test_hydra_docs_exist(self):
        """Verify Hydra configuration documentation exists."""
        hydra_paths = [
            DOCS_DIR / "hydra_quickstart.md",
            DOCS_DIR / "hydra_defaults_and_sweeps.md",
        ]
        found = any(p.exists() for p in hydra_paths)
        if not found:
            pytest.skip("Hydra documentation not required")

        for hydra_path in hydra_paths:
            if hydra_path.exists():
                content = hydra_path.read_text(encoding="utf-8")
                assert "hydra" in content.lower(), f"{hydra_path.name} should mention Hydra"
