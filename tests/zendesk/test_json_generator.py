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

from zendesk.json_generator import (
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
        assert len(templates) >= 5, "Templates must not be empty"

    def test_create_ticket_template_exists(self, generator: ZendeskJSONGenerator) -> None:
        """Test that create_ticket template exists."""
        template = generator.get_template("create_ticket")
        assert template is not None, "template must be initialized"
        assert template.name == "create_ticket", "name is not valid"

    def test_bulk_update_template_exists(self, generator: ZendeskJSONGenerator) -> None:
        """Test that bulk_update template exists."""
        template = generator.get_template("bulk_update")
        assert template is not None, "template must be initialized"

    def test_create_sla_policy_template_exists(self, generator: ZendeskJSONGenerator) -> None:
        """Test that create_sla_policy template exists."""
        template = generator.get_template("create_sla_policy")
        assert template is not None, "template must be initialized"


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
        assert retrieved is not None, "retrieved must be initialized"
        assert retrieved.name == "custom_action", "name is not valid"
        assert retrieved.category == "custom", "category is not valid"

    def test_get_nonexistent_template_returns_none(self, generator: ZendeskJSONGenerator) -> None:
        """Test that getting a nonexistent template returns None."""
        template = generator.get_template("nonexistent_template")
        assert template is None, "template is not valid"


# ==============================================================================
# TEST TEMPLATE LISTING
# ==============================================================================


class TestTemplateListing:
    """Tests for template listing with filters."""

    def test_list_all_templates(self, generator: ZendeskJSONGenerator) -> None:
        """Test listing all templates."""
        templates = generator.list_templates()
        assert len(templates) >= 5, "Templates must not be empty"

    def test_list_templates_by_category(self, generator: ZendeskJSONGenerator) -> None:
        """Test listing templates by category."""
        ticket_templates = generator.list_templates(category="tickets")
        assert len(ticket_templates) >= 2, "Ticket_templates must not be empty"
        assert all(t.category == "tickets" for t in ticket_templates), "category is not valid"

    def test_list_templates_by_tags(self, generator: ZendeskJSONGenerator) -> None:
        """Test listing templates by tags."""
        create_templates = generator.list_templates(tags=["create"])
        assert len(create_templates) >= 2, "Create_templates must not be empty"
        assert all(
            any("create" in t.tags for t in create_templates) for t in create_templates
        ), "Condition must be true"

    def test_list_templates_with_combined_filters(self, generator: ZendeskJSONGenerator) -> None:
        """Test listing templates with both category and tags filters."""
        templates = generator.list_templates(category="tickets", tags=["create"])
        assert len(templates) >= 1, "Templates must not be empty"


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

        assert "ticket" in script, "Condition must be true"
        assert script["ticket"]["subject"] == "Test Subject", "Condition must be true"
        assert script["ticket"]["description"] == "Test Description", "Condition must be true"
        assert script["ticket"]["priority"] == "high", "Condition must be true"
        assert (
            script["ticket"]["requester"]["email"] == "test@example.com"
        ), "Condition must be true"

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

        assert script["ticket"]["priority"] == "normal", "Condition must be true"
        assert script["ticket"]["type"] == "question", "Condition must be true"

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

        assert "_generated" in script, "Condition must be true"
        assert script["_generated"]["template"] == "close_ticket", "Condition must be true"
        assert "timestamp" in script["_generated"], "Condition must be true"
        assert "variables_used" in script["_generated"], "Condition must be true"


# ==============================================================================
# TEST PLACEHOLDER REPLACEMENT
# ==============================================================================


class TestPlaceholderReplacement:
    """Tests for placeholder replacement."""

    def test_simple_placeholder_replacement(self, generator: ZendeskJSONGenerator) -> None:
        """Test simple placeholder replacement."""
        script = generator.generate("close_ticket", {"RESOLUTION_COMMENT": "All done!"})

        assert script["ticket"]["comment"]["body"] == "All done!", "Condition must be true"

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

        assert script["user"]["name"] == "John Doe", "Condition must be true"
        assert script["user"]["email"] == "john@example.com", "Condition must be true"

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

        assert script["field1"] == "value1", "Value must be initialized"
        assert script["field2"] == "{{VAR2}}", "Condition must be true"


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

        assert "name" in export, "Condition must be true"
        assert "description" in export, "Condition must be true"
        assert "api_request" in export, "Condition must be true"
        assert export["name"] == "create_ticket", "exp is not valid"
        assert export["api_request"]["method"] == "POST", "exp is not valid"
        assert export["api_request"]["endpoint"] == "/api/v2/tickets.json", "exp is not valid"

    def test_export_for_chatgpt_includes_instructions(
        self, generator: ZendeskJSONGenerator
    ) -> None:
        """Test that ChatGPT export includes instructions."""
        export = generator.export_for_chatgpt(
            "create_ticket",
            {},
            include_instructions=True,
        )

        assert "instructions" in export, "Condition must be true"
        assert "api_request" in export, "Condition must be true"
        assert "variables" in export, "Condition must be true"

    def test_export_for_chatgpt_without_instructions(self, generator: ZendeskJSONGenerator) -> None:
        """Test ChatGPT export without instructions."""
        export = generator.export_for_chatgpt(
            "create_ticket",
            {},
            include_instructions=False,
        )

        assert "instructions" not in export, "Condition must be true"

    def test_export_http_method_inference(self, generator: ZendeskJSONGenerator) -> None:
        """Test that HTTP methods are correctly inferred."""
        # POST for create_*
        create_export = generator.export_for_chatgpt("create_ticket", {})
        assert create_export["api_request"]["method"] == "POST", "create_exp is not valid"

        # POST for search_*
        search_export = generator.export_for_chatgpt("search_tickets", {"QUERY": "status:open"})
        assert search_export["api_request"]["method"] == "POST", "search_exp is not valid"

        # PUT for update_*
        update_export = generator.export_for_chatgpt("update_ticket", {})
        assert update_export["api_request"]["method"] == "PUT", "update_exp is not valid"

        # PUT for bulk_*
        bulk_export = generator.export_for_chatgpt("bulk_update", {})
        assert bulk_export["api_request"]["method"] == "PUT", "bulk_exp is not valid"


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

        assert "action" in export, "Condition must be true"
        assert "category" in export, "Condition must be true"
        assert "payload" in export, "Condition must be true"
        assert export["action"] == "create_ticket", "exp is not valid"
        assert export["category"] == "tickets", "exp is not valid"

    def test_export_for_zendesk_ai_includes_context(self, generator: ZendeskJSONGenerator) -> None:
        """Test that Zendesk AI export includes context."""
        export = generator.export_for_zendesk_ai_assistant(
            "create_ticket",
            {},
            include_context=True,
        )

        assert "context" in export, "Condition must be true"
        assert "description" in export["context"], "Condition must be true"
        assert "tags" in export["context"], "Condition must be true"
        assert "variables" in export["context"], "Condition must be true"

    def test_export_for_zendesk_ai_without_context(self, generator: ZendeskJSONGenerator) -> None:
        """Test Zendesk AI export without context."""
        export = generator.export_for_zendesk_ai_assistant(
            "create_ticket",
            {},
            include_context=False,
        )

        assert "context" not in export, "Condition must be true"


# ==============================================================================
# TEST JSON SERIALIZATION
# ==============================================================================


class TestJSONSerialization:
    """Tests for JSON serialization."""

    def test_to_json(self, generator: ZendeskJSONGenerator) -> None:
        """Test to_json method."""
        json_str = generator.to_json("close_ticket", {"RESOLUTION_COMMENT": "Issue resolved"})

        # Should be valid JSON
        parsed = json.loads(json_str)
        assert "ticket" in parsed, "Condition must be true"
        assert parsed["ticket"]["status"] == "solved", "Condition must be true"

    def test_to_json_is_pretty_printed(self, generator: ZendeskJSONGenerator) -> None:
        """Test that to_json output is pretty printed."""
        json_str = generator.to_json("close_ticket", {"RESOLUTION_COMMENT": "Done"})

        # Pretty printed JSON has newlines
        assert "\n" in json_str, "Condition must be true"
        assert "  " in json_str, "Condition must be true"


# ==============================================================================
# TEST TEMPLATE VARIABLES
# ==============================================================================


class TestTemplateVariables:
    """Tests for TemplateVariable dataclass."""

    def test_template_variable_defaults(self) -> None:
        """Test TemplateVariable default values."""
        var = TemplateVariable(name="TEST", description="A test variable")

        assert var.name == "TEST", "name is not valid"
        assert var.description == "A test variable", "description is not valid"
        assert var.required is True, "required is not valid"
        assert var.default is None, "default is not valid"
        assert var.value_type == "string", "Value must be initialized"
        assert var.example is None, "example is not valid"

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

        assert var.name == "COUNT", "Count must be greater than zero"
        assert var.required is False, "required is not valid"
        assert var.default == 10, "default is not valid"
        assert var.value_type == "number", "Value must be initialized"
        assert var.example == 50, "example is not valid"


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

        assert template.name == "test", "name is not valid"
        assert template.variables == [], "variables is not valid"
        assert template.tags == [], "tags is not valid"

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

        assert template.name == "full_test", "name is not valid"
        assert len(template.variables) == 1, "Collection must not be empty"
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

        assert "sla_policy" in script, "Condition must be true"
        assert script["sla_policy"]["title"] == "Premium Support", "Condition must be true"
        assert (
            script["sla_policy"]["filter"]["all"][0]["value"] == "urgent"
        ), "Value must be initialized"
        assert script["sla_policy"]["policy_metrics"][0]["target"] == 30, "Condition must be true"
