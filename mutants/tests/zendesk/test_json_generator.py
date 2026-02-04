"""
Test suite for Zendesk JSON Generator.

Tests cover:
- Template registration and retrieval
- Placeholder substitution
- Export formats (ChatGPT, Zendesk AI)
- All built-in templates
"""

from __future__ import annotations

import json

import pytest

from src.zendesk.json_generator import (
    ScriptTemplate,
    TemplateVariable,
    ZendeskJSONGenerator,
)


# ==============================================================================
# FIXTURES
# ==============================================================================


@pytest.fixture
def generator() -> ZendeskJSONGenerator:
    """Create a test generator instance."""
    return ZendeskJSONGenerator()


# ==============================================================================
# TEST INITIALIZATION
# ==============================================================================


class TestGeneratorInitialization:
    """Tests for generator initialization."""

    def test_generator_loads_builtin_templates(self, generator: ZendeskJSONGenerator) -> None:
        """Test that built-in templates are loaded."""
        templates = generator.list_templates()
        assert len(templates) >= 5  # At least 5 built-in templates

    def test_create_ticket_template_exists(self, generator: ZendeskJSONGenerator) -> None:
        """Test that create_ticket template exists."""
        template = generator.get_template("create_ticket")
        assert template is not None
        assert template.name == "create_ticket"

    def test_bulk_update_template_exists(self, generator: ZendeskJSONGenerator) -> None:
        """Test that bulk_update template exists."""
        template = generator.get_template("bulk_update")
        assert template is not None

    def test_create_sla_policy_template_exists(self, generator: ZendeskJSONGenerator) -> None:
        """Test that create_sla_policy template exists."""
        template = generator.get_template("create_sla_policy")
        assert template is not None


# ==============================================================================
# TEST TEMPLATE REGISTRATION
# ==============================================================================


class TestTemplateRegistration:
    """Tests for template registration."""

    def test_register_custom_template(self, generator: ZendeskJSONGenerator) -> None:
        """Test registering a custom template."""
        custom_template = ScriptTemplate(
            name="custom_action",
            description="A custom action template",
            category="custom",
            template={"action": "{{ACTION_TYPE}}", "data": "{{DATA}}"},
            variables=[
                TemplateVariable(name="ACTION_TYPE", description="Type of action", required=True),
                TemplateVariable(name="DATA", description="Action data", required=True),
            ],
            tags=["custom"],
        )

        generator.register_template(custom_template)

        retrieved = generator.get_template("custom_action")
        assert retrieved is not None
        assert retrieved.name == "custom_action"
        assert retrieved.category == "custom"

    def test_get_nonexistent_template_returns_none(
        self, generator: ZendeskJSONGenerator
    ) -> None:
        """Test that getting a nonexistent template returns None."""
        template = generator.get_template("nonexistent_template")
        assert template is None


# ==============================================================================
# TEST TEMPLATE LISTING
# ==============================================================================


class TestTemplateListing:
    """Tests for template listing with filters."""

    def test_list_all_templates(self, generator: ZendeskJSONGenerator) -> None:
        """Test listing all templates."""
        templates = generator.list_templates()
        assert len(templates) >= 5

    def test_list_templates_by_category(self, generator: ZendeskJSONGenerator) -> None:
        """Test listing templates by category."""
        ticket_templates = generator.list_templates(category="tickets")
        assert len(ticket_templates) >= 2
        assert all(t.category == "tickets" for t in ticket_templates)

    def test_list_templates_by_tags(self, generator: ZendeskJSONGenerator) -> None:
        """Test listing templates by tags."""
        create_templates = generator.list_templates(tags=["create"])
        assert len(create_templates) >= 2
        assert all(any("create" in t.tags for t in create_templates) for t in create_templates)

    def test_list_templates_with_combined_filters(
        self, generator: ZendeskJSONGenerator
    ) -> None:
        """Test listing templates with both category and tags filters."""
        templates = generator.list_templates(category="tickets", tags=["create"])
        assert len(templates) >= 1


# ==============================================================================
# TEST SCRIPT GENERATION
# ==============================================================================


class TestScriptGeneration:
    """Tests for script generation."""

    def test_generate_create_ticket(self, generator: ZendeskJSONGenerator) -> None:
        """Test generating a create_ticket script."""
        script = generator.generate(
            "create_ticket",
            {
                "SUBJECT": "Test Subject",
                "DESCRIPTION": "Test Description",
                "PRIORITY": "high",
                "TICKET_TYPE": "incident",
                "REQUESTER_EMAIL": "test@example.com",
                "TAG1": "urgent",
                "TAG2": "billing",
            },
        )

        assert "ticket" in script
        assert script["ticket"]["subject"] == "Test Subject"
        assert script["ticket"]["description"] == "Test Description"
        assert script["ticket"]["priority"] == "high"
        assert script["ticket"]["requester"]["email"] == "test@example.com"

    def test_generate_with_defaults(self, generator: ZendeskJSONGenerator) -> None:
        """Test that defaults are applied for missing optional variables."""
        script = generator.generate(
            "create_ticket",
            {
                "SUBJECT": "Test Subject",
                "DESCRIPTION": "Test Description",
                "REQUESTER_EMAIL": "test@example.com",
            },
        )

        assert script["ticket"]["priority"] == "normal"
        assert script["ticket"]["type"] == "question"

    def test_generate_with_strict_mode(self, generator: ZendeskJSONGenerator) -> None:
        """Test strict mode raises error for missing required variables."""
        with pytest.raises(ValueError, match="Missing required variable"):
            generator.generate(
                "create_ticket",
                {"SUBJECT": "Test"},  # Missing DESCRIPTION and REQUESTER_EMAIL
                strict=True,
            )

    def test_generate_nonexistent_template_raises_error(
        self, generator: ZendeskJSONGenerator
    ) -> None:
        """Test that generating from nonexistent template raises error."""
        with pytest.raises(ValueError, match="Template not found"):
            generator.generate("nonexistent_template", {})

    def test_generate_with_metadata(self, generator: ZendeskJSONGenerator) -> None:
        """Test generation with metadata included."""
        script = generator.generate(
            "close_ticket",
            {"RESOLUTION_COMMENT": "Issue resolved"},
            include_meta=True,
        )

        assert "_generated" in script
        assert script["_generated"]["template"] == "close_ticket"
        assert "timestamp" in script["_generated"]
        assert "variables_used" in script["_generated"]


# ==============================================================================
# TEST PLACEHOLDER REPLACEMENT
# ==============================================================================


class TestPlaceholderReplacement:
    """Tests for placeholder replacement."""

    def test_simple_placeholder_replacement(self, generator: ZendeskJSONGenerator) -> None:
        """Test simple placeholder replacement."""
        script = generator.generate(
            "close_ticket", {"RESOLUTION_COMMENT": "All done!"}
        )

        assert script["ticket"]["comment"]["body"] == "All done!"

    def test_placeholder_in_nested_structure(self, generator: ZendeskJSONGenerator) -> None:
        """Test placeholder replacement in nested structures."""
        script = generator.generate(
            "create_user",
            {
                "NAME": "John Doe",
                "EMAIL": "john@example.com",
                "ROLE": "agent",
                "VERIFIED": True,
            },
        )

        assert script["user"]["name"] == "John Doe"
        assert script["user"]["email"] == "john@example.com"

    def test_placeholder_preserves_unreplaced_when_not_strict(
        self, generator: ZendeskJSONGenerator
    ) -> None:
        """Test that unreplaced placeholders are preserved in non-strict mode."""
        # Register a simple test template
        generator.register_template(
            ScriptTemplate(
                name="test_template",
                description="Test",
                category="test",
                template={"field1": "{{VAR1}}", "field2": "{{VAR2}}"},
                variables=[
                    TemplateVariable(name="VAR1", description="Var 1", required=False),
                    TemplateVariable(name="VAR2", description="Var 2", required=False),
                ],
            )
        )

        script = generator.generate("test_template", {"VAR1": "value1"})

        assert script["field1"] == "value1"
        assert script["field2"] == "{{VAR2}}"  # Unreplaced placeholder preserved


# ==============================================================================
# TEST CHATGPT EXPORT
# ==============================================================================


class TestChatGPTExport:
    """Tests for ChatGPT export format."""

    def test_export_for_chatgpt_basic(self, generator: ZendeskJSONGenerator) -> None:
        """Test basic ChatGPT export."""
        export = generator.export_for_chatgpt(
            "create_ticket",
            {
                "SUBJECT": "Help needed",
                "DESCRIPTION": "I need help",
                "REQUESTER_EMAIL": "user@example.com",
            },
        )

        assert "name" in export
        assert "description" in export
        assert "api_request" in export
        assert export["name"] == "create_ticket"
        assert export["api_request"]["method"] == "POST"
        assert export["api_request"]["endpoint"] == "/api/v2/tickets.json"

    def test_export_for_chatgpt_includes_instructions(
        self, generator: ZendeskJSONGenerator
    ) -> None:
        """Test that ChatGPT export includes instructions."""
        export = generator.export_for_chatgpt(
            "create_ticket",
            {},
            include_instructions=True,
        )

        assert "instructions" in export
        assert "## create_ticket" in export["instructions"]
        assert "variables" in export

    def test_export_for_chatgpt_without_instructions(
        self, generator: ZendeskJSONGenerator
    ) -> None:
        """Test ChatGPT export without instructions."""
        export = generator.export_for_chatgpt(
            "create_ticket",
            {},
            include_instructions=False,
        )

        assert "instructions" not in export

    def test_export_http_method_inference(self, generator: ZendeskJSONGenerator) -> None:
        """Test that HTTP methods are correctly inferred."""
        # POST for create_*
        create_export = generator.export_for_chatgpt("create_ticket", {})
        assert create_export["api_request"]["method"] == "POST"

        # POST for search_*
        search_export = generator.export_for_chatgpt("search_tickets", {"QUERY": "status:open"})
        assert search_export["api_request"]["method"] == "POST"

        # PUT for update_*
        update_export = generator.export_for_chatgpt("update_ticket", {})
        assert update_export["api_request"]["method"] == "PUT"

        # PUT for bulk_*
        bulk_export = generator.export_for_chatgpt("bulk_update", {})
        assert bulk_export["api_request"]["method"] == "PUT"


# ==============================================================================
# TEST ZENDESK AI EXPORT
# ==============================================================================


class TestZendeskAIExport:
    """Tests for Zendesk AI Assistant export format."""

    def test_export_for_zendesk_ai_basic(self, generator: ZendeskJSONGenerator) -> None:
        """Test basic Zendesk AI export."""
        export = generator.export_for_zendesk_ai_assistant(
            "create_ticket",
            {
                "SUBJECT": "Help needed",
                "DESCRIPTION": "I need help",
                "REQUESTER_EMAIL": "user@example.com",
            },
        )

        assert "action" in export
        assert "category" in export
        assert "payload" in export
        assert export["action"] == "create_ticket"
        assert export["category"] == "tickets"

    def test_export_for_zendesk_ai_includes_context(
        self, generator: ZendeskJSONGenerator
    ) -> None:
        """Test that Zendesk AI export includes context."""
        export = generator.export_for_zendesk_ai_assistant(
            "create_ticket",
            {},
            include_context=True,
        )

        assert "context" in export
        assert "description" in export["context"]
        assert "tags" in export["context"]
        assert "variables" in export["context"]

    def test_export_for_zendesk_ai_without_context(
        self, generator: ZendeskJSONGenerator
    ) -> None:
        """Test Zendesk AI export without context."""
        export = generator.export_for_zendesk_ai_assistant(
            "create_ticket",
            {},
            include_context=False,
        )

        assert "context" not in export


# ==============================================================================
# TEST JSON SERIALIZATION
# ==============================================================================


class TestJSONSerialization:
    """Tests for JSON serialization."""

    def test_to_json(self, generator: ZendeskJSONGenerator) -> None:
        """Test to_json method."""
        json_str = generator.to_json(
            "close_ticket", {"RESOLUTION_COMMENT": "Issue resolved"}
        )

        # Should be valid JSON
        parsed = json.loads(json_str)
        assert "ticket" in parsed
        assert parsed["ticket"]["status"] == "solved"

    def test_to_json_is_pretty_printed(self, generator: ZendeskJSONGenerator) -> None:
        """Test that to_json output is pretty printed."""
        json_str = generator.to_json(
            "close_ticket", {"RESOLUTION_COMMENT": "Done"}
        )

        # Pretty printed JSON has newlines
        assert "\n" in json_str
        assert "  " in json_str  # Indentation


# ==============================================================================
# TEST TEMPLATE VARIABLES
# ==============================================================================


class TestTemplateVariables:
    """Tests for TemplateVariable dataclass."""

    def test_template_variable_defaults(self) -> None:
        """Test TemplateVariable default values."""
        var = TemplateVariable(name="TEST", description="A test variable")

        assert var.name == "TEST"
        assert var.description == "A test variable"
        assert var.required is True
        assert var.default is None
        assert var.value_type == "string"
        assert var.example is None

    def test_template_variable_full_specification(self) -> None:
        """Test TemplateVariable with all fields specified."""
        var = TemplateVariable(
            name="COUNT",
            description="Number of items",
            required=False,
            default=10,
            value_type="number",
            example=50,
        )

        assert var.name == "COUNT"
        assert var.required is False
        assert var.default == 10
        assert var.value_type == "number"
        assert var.example == 50


# ==============================================================================
# TEST SCRIPT TEMPLATE
# ==============================================================================


class TestScriptTemplate:
    """Tests for ScriptTemplate dataclass."""

    def test_script_template_defaults(self) -> None:
        """Test ScriptTemplate default values."""
        template = ScriptTemplate(
            name="test",
            description="A test template",
            category="testing",
            template={"key": "value"},
        )

        assert template.name == "test"
        assert template.variables == []
        assert template.tags == []

    def test_script_template_full_specification(self) -> None:
        """Test ScriptTemplate with all fields specified."""
        variables = [TemplateVariable(name="VAR", description="A var")]
        template = ScriptTemplate(
            name="full_test",
            description="A fully specified template",
            category="testing",
            template={"data": "{{VAR}}"},
            variables=variables,
            tags=["test", "example"],
        )

        assert template.name == "full_test"
        assert len(template.variables) == 1
        assert template.tags == ["test", "example"]


# ==============================================================================
# TEST SLA POLICY TEMPLATE
# ==============================================================================


class TestSLAPolicyTemplate:
    """Tests for SLA policy template."""

    def test_generate_sla_policy(self, generator: ZendeskJSONGenerator) -> None:
        """Test generating an SLA policy script."""
        script = generator.generate(
            "create_sla_policy",
            {
                "TITLE": "Premium Support",
                "DESCRIPTION": "For premium customers",
                "POSITION": 1,
                "PRIORITY_FILTER": "urgent",
                "METRIC_PRIORITY": "urgent",
                "FIRST_REPLY_TARGET": 30,
                "USE_BUSINESS_HOURS": True,
            },
        )

        assert "sla_policy" in script
        assert script["sla_policy"]["title"] == "Premium Support"
        assert script["sla_policy"]["filter"]["all"][0]["value"] == "urgent"
        assert script["sla_policy"]["policy_metrics"][0]["target"] == 30
