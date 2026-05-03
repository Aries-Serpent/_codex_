"""
Zendesk JSON Script Generator for AI Assistant Integration.

Provides template-based script generation with placeholder support
for ChatGPT, CustomGPT, and Zendesk AI Assistant.

All templates documented in openapi.yaml and swagger.html.
"""

from __future__ import annotations

import copy
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)

# Module-level constant for placeholder pattern: {{VARIABLE_NAME}}
# Matches uppercase variable names with underscores and digits
PLACEHOLDER_PATTERN = re.compile(r"\{\{([A-Z_][A-Z0-9_]*)\}\}")


@dataclass
class TemplateVariable:
    """Represents a variable placeholder in a template."""

    name: str
    description: str
    required: bool = True
    default: Any = None
    value_type: str = "string"  # string, number, boolean, array, object
    example: Any = None


@dataclass
class ScriptTemplate:
    """Represents a complete script template."""

    name: str
    description: str
    category: str
    template: dict[str, Any]
    variables: list[TemplateVariable] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


class ZendeskJSONGenerator:
    """
    Template-based JSON script generator for Zendesk API operations.

    Supports:
    - Variable placeholders using {{VARIABLE_NAME}} syntax
    - Multiple export formats (ChatGPT, CustomGPT, Zendesk AI)
    - Built-in template library
    - Custom template registration

    Example:
        >>> generator = ZendeskJSONGenerator()
        >>> script = generator.generate("create_ticket", {
        ...     "SUBJECT": "Help needed",
        ...     "DESCRIPTION": "I need help with my order"
        ... })
        >>> print(json.dumps(script, indent=2))
    """

    def __init__(self) -> None:
        """Initialize the generator with built-in templates."""
        self._templates: dict[str, ScriptTemplate] = {}
        self._register_builtin_templates()

    def _register_builtin_templates(self) -> None:
        """Register all built-in templates."""
        # Ticket templates
        self._register_ticket_templates()
        # User templates
        self._register_user_templates()
        # SLA Policy templates
        self._register_sla_templates()
        # Bulk operation templates
        self._register_bulk_templates()
        # Search templates
        self._register_search_templates()

    def _register_ticket_templates(self) -> None:
        """Register ticket-related templates."""
        self.register_template(
            ScriptTemplate(
                name="create_ticket",
                description="Create a new support ticket",
                category="tickets",
                template={
                    "ticket": {
                        "subject": "{{SUBJECT}}",
                        "description": "{{DESCRIPTION}}",
                        "priority": "{{PRIORITY}}",
                        "type": "{{TICKET_TYPE}}",
                        "requester": {"email": "{{REQUESTER_EMAIL}}"},
                        "tags": ["{{TAG1}}", "{{TAG2}}"],
                    }
                },
                variables=[
                    TemplateVariable(
                        name="SUBJECT",
                        description="Ticket subject line",
                        required=True,
                        example="Help with billing",
                    ),
                    TemplateVariable(
                        name="DESCRIPTION",
                        description="Detailed description of the issue",
                        required=True,
                        example="I have a question about my recent invoice",
                    ),
                    TemplateVariable(
                        name="PRIORITY",
                        description="Ticket priority (urgent, high, normal, low)",
                        required=False,
                        default="normal",
                        example="high",
                    ),
                    TemplateVariable(
                        name="TICKET_TYPE",
                        description="Ticket type (problem, incident, question, task)",
                        required=False,
                        default="question",
                        example="question",
                    ),
                    TemplateVariable(
                        name="REQUESTER_EMAIL",
                        description="Email of the requester",
                        required=True,
                        example="customer@example.com",
                    ),
                    TemplateVariable(
                        name="TAG1",
                        description="First tag",
                        required=False,
                        default="",
                        example="billing",
                    ),
                    TemplateVariable(
                        name="TAG2",
                        description="Second tag",
                        required=False,
                        default="",
                        example="priority",
                    ),
                ],
                tags=["ticket", "create", "support"],
            )
        )

        self.register_template(
            ScriptTemplate(
                name="update_ticket",
                description="Update an existing ticket",
                category="tickets",
                template={
                    "ticket": {
                        "status": "{{STATUS}}",
                        "priority": "{{PRIORITY}}",
                        "assignee_id": "{{ASSIGNEE_ID}}",
                        "comment": {
                            "body": "{{COMMENT}}",
                            "public": "{{IS_PUBLIC}}",
                        },
                    }
                },
                variables=[
                    TemplateVariable(
                        name="STATUS",
                        description="Ticket status (new, open, pending, hold, solved, closed)",
                        required=False,
                        example="pending",
                    ),
                    TemplateVariable(
                        name="PRIORITY",
                        description="Ticket priority",
                        required=False,
                        example="high",
                    ),
                    TemplateVariable(
                        name="ASSIGNEE_ID",
                        description="ID of the agent to assign",
                        required=False,
                        value_type="number",
                        example=12345,
                    ),
                    TemplateVariable(
                        name="COMMENT",
                        description="Comment to add to the ticket",
                        required=False,
                        example="Working on this issue",
                    ),
                    TemplateVariable(
                        name="IS_PUBLIC",
                        description="Whether the comment is public",
                        required=False,
                        value_type="boolean",
                        default=True,
                        example=True,
                    ),
                ],
                tags=["ticket", "update", "support"],
            )
        )

        self.register_template(
            ScriptTemplate(
                name="close_ticket",
                description="Close a ticket with resolution comment",
                category="tickets",
                template={
                    "ticket": {
                        "status": "solved",
                        "comment": {
                            "body": "{{RESOLUTION_COMMENT}}",
                            "public": True,
                        },
                    }
                },
                variables=[
                    TemplateVariable(
                        name="RESOLUTION_COMMENT",
                        description="Comment explaining the resolution",
                        required=True,
                        example="Issue resolved. The account has been credited.",
                    ),
                ],
                tags=["ticket", "close", "resolve"],
            )
        )

    def _register_user_templates(self) -> None:
        """Register user-related templates."""
        self.register_template(
            ScriptTemplate(
                name="create_user",
                description="Create a new user",
                category="users",
                template={
                    "user": {
                        "name": "{{NAME}}",
                        "email": "{{EMAIL}}",
                        "role": "{{ROLE}}",
                        "verified": "{{VERIFIED}}",
                    }
                },
                variables=[
                    TemplateVariable(
                        name="NAME",
                        description="User's full name",
                        required=True,
                        example="John Doe",
                    ),
                    TemplateVariable(
                        name="EMAIL",
                        description="User's email address",
                        required=True,
                        example="john.doe@example.com",
                    ),
                    TemplateVariable(
                        name="ROLE",
                        description="User role (end-user, agent, admin)",
                        required=False,
                        default="end-user",
                        example="end-user",
                    ),
                    TemplateVariable(
                        name="VERIFIED",
                        description="Whether the user is verified",
                        required=False,
                        value_type="boolean",
                        default=True,
                        example=True,
                    ),
                ],
                tags=["user", "create"],
            )
        )

    def _register_sla_templates(self) -> None:
        """Register SLA policy templates."""
        self.register_template(
            ScriptTemplate(
                name="create_sla_policy",
                description="Create a new SLA policy",
                category="sla_policies",
                template={
                    "sla_policy": {
                        "title": "{{TITLE}}",
                        "description": "{{DESCRIPTION}}",
                        "position": "{{POSITION}}",
                        "filter": {
                            "all": [
                                {
                                    "field": "priority",
                                    "operator": "is",
                                    "value": "{{PRIORITY_FILTER}}",
                                }
                            ]
                        },
                        "policy_metrics": [
                            {
                                "priority": "{{METRIC_PRIORITY}}",
                                "metric": "first_reply_time",
                                "target": "{{FIRST_REPLY_TARGET}}",
                                "business_hours": "{{USE_BUSINESS_HOURS}}",
                            }
                        ],
                    }
                },
                variables=[
                    TemplateVariable(
                        name="TITLE",
                        description="SLA policy title",
                        required=True,
                        example="Premium Support SLA",
                    ),
                    TemplateVariable(
                        name="DESCRIPTION",
                        description="Policy description",
                        required=False,
                        example="SLA for premium support customers",
                    ),
                    TemplateVariable(
                        name="POSITION",
                        description="Position in the policy list (lower = higher priority)",
                        required=False,
                        value_type="number",
                        default=1,
                        example=1,
                    ),
                    TemplateVariable(
                        name="PRIORITY_FILTER",
                        description="Priority level to match",
                        required=True,
                        example="urgent",
                    ),
                    TemplateVariable(
                        name="METRIC_PRIORITY",
                        description="Priority for the metric target",
                        required=True,
                        example="urgent",
                    ),
                    TemplateVariable(
                        name="FIRST_REPLY_TARGET",
                        description="First reply target in minutes",
                        required=True,
                        value_type="number",
                        example=60,
                    ),
                    TemplateVariable(
                        name="USE_BUSINESS_HOURS",
                        description="Whether to use business hours",
                        required=False,
                        value_type="boolean",
                        default=True,
                        example=True,
                    ),
                ],
                tags=["sla", "policy", "create"],
            )
        )

    def _register_bulk_templates(self) -> None:
        """Register bulk operation templates."""
        self.register_template(
            ScriptTemplate(
                name="bulk_update",
                description="Bulk update multiple tickets",
                category="tickets",
                template={
                    "ticket": {
                        "status": "{{STATUS}}",
                        "priority": "{{PRIORITY}}",
                        "assignee_id": "{{ASSIGNEE_ID}}",
                        "comment": {
                            "body": "{{COMMENT}}",
                            "public": False,
                        },
                    },
                    "_meta": {
                        "ids": "{{TICKET_IDS}}",
                        "description": "Comma-separated list of ticket IDs to update",
                    },
                },
                variables=[
                    TemplateVariable(
                        name="STATUS",
                        description="New status for all tickets",
                        required=False,
                        example="pending",
                    ),
                    TemplateVariable(
                        name="PRIORITY",
                        description="New priority for all tickets",
                        required=False,
                        example="high",
                    ),
                    TemplateVariable(
                        name="ASSIGNEE_ID",
                        description="Agent ID to assign all tickets to",
                        required=False,
                        value_type="number",
                        example=12345,
                    ),
                    TemplateVariable(
                        name="COMMENT",
                        description="Comment to add to all tickets",
                        required=False,
                        example="Bulk update: Assigned to support team",
                    ),
                    TemplateVariable(
                        name="TICKET_IDS",
                        description="Comma-separated list of ticket IDs",
                        required=True,
                        example="123,456,789",
                    ),
                ],
                tags=["bulk", "update", "tickets"],
            )
        )

    def _register_search_templates(self) -> None:
        """Register search templates."""
        self.register_template(
            ScriptTemplate(
                name="search_tickets",
                description="Search for tickets with specific criteria",
                category="search",
                template={
                    "query": "type:ticket {{QUERY}}",
                    "per_page": "{{PER_PAGE}}",
                },
                variables=[
                    TemplateVariable(
                        name="QUERY",
                        description="Search query (Zendesk search syntax)",
                        required=True,
                        example="status:open priority:urgent",
                    ),
                    TemplateVariable(
                        name="PER_PAGE",
                        description="Results per page (max 100)",
                        required=False,
                        value_type="number",
                        default=100,
                        example=50,
                    ),
                ],
                tags=["search", "tickets"],
            )
        )

    def register_template(self, template: ScriptTemplate) -> None:
        """
        Register a new template.

        Args:
            template: ScriptTemplate to register
        """
        self._templates[template.name] = template
        logger.debug(f"Registered template: {template.name}")

    def get_template(self, name: str) -> ScriptTemplate | None:
        """
        Get a template by name.

        Args:
            name: Template name

        Returns:
            ScriptTemplate or None if not found
        """
        return self._templates.get(name)

    def list_templates(
        self, category: str | None = None, tags: list[str] | None = None
    ) -> list[ScriptTemplate]:
        """
        List available templates, optionally filtered.

        Args:
            category: Filter by category
            tags: Filter by tags (any match)

        Returns:
            List of matching templates
        """
        templates = list(self._templates.values())

        if category:
            templates = [t for t in templates if t.category == category]

        if tags:
            templates = [t for t in templates if any(tag in t.tags for tag in tags)]

        return templates

    def _replace_placeholders(
        self, obj: Any, variables: dict[str, Any], strict: bool = False
    ) -> Any:
        """
        Recursively replace placeholders in an object.

        Args:
            obj: Object to process (dict, list, or str)
            variables: Variable values
            strict: If True, raise error for missing required variables

        Returns:
            Object with placeholders replaced
        """
        if isinstance(obj, str):
            # Check for complete replacement (entire string is a placeholder)
            match = PLACEHOLDER_PATTERN.fullmatch(obj)
            if match:
                var_name = match.group(1)
                if var_name in variables:
                    return variables[var_name]
                if strict:
                    raise ValueError(f"Missing required variable: {var_name}")
                return obj

            # Check for partial replacement (placeholder within string)
            def replace_match(m: re.Match) -> str:
                var_name = m.group(1)
                if var_name in variables:
                    return str(variables[var_name])
                if strict:
                    raise ValueError(f"Missing required variable: {var_name}")
                return m.group(0)

            return PLACEHOLDER_PATTERN.sub(replace_match, obj)

        if isinstance(obj, dict):
            return {k: self._replace_placeholders(v, variables, strict) for k, v in obj.items()}

        if isinstance(obj, list):
            return [self._replace_placeholders(item, variables, strict) for item in obj]

        return obj

    def generate(
        self,
        template_name: str,
        variables: dict[str, Any] | None = None,
        *,
        strict: bool = False,
        include_meta: bool = False,
    ) -> dict[str, Any]:
        """
        Generate a JSON script from a template.

        Args:
            template_name: Name of the template to use
            variables: Variable values to substitute
            strict: If True, raise error for missing required variables
            include_meta: If True, include metadata in output

        Returns:
            Generated JSON script

        Raises:
            ValueError: If template not found or required variable missing

        Example:
            >>> generator = ZendeskJSONGenerator()
            >>> script = generator.generate("create_ticket", {
            ...     "SUBJECT": "Help needed",
            ...     "DESCRIPTION": "I need assistance",
            ...     "REQUESTER_EMAIL": "user@example.com"
            ... })
        """
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template not found: {template_name}")

        variables = variables or {}

        # Apply defaults for missing variables
        for var in template.variables:
            if var.name not in variables and var.default is not None:
                variables[var.name] = var.default

        # Validate required variables
        if strict:
            for var in template.variables:
                if var.required and var.name not in variables:
                    raise ValueError(f"Missing required variable: {var.name}")

        # Generate script
        result = copy.deepcopy(template.template)
        result = self._replace_placeholders(result, variables, strict)

        # Add metadata if requested
        if include_meta:
            result["_generated"] = {
                "template": template_name,
                "timestamp": datetime.now(UTC).isoformat(),
                "variables_used": list(variables.keys()),
            }

        return result

    def export_for_chatgpt(
        self,
        template_name: str,
        variables: dict[str, Any] | None = None,
        *,
        include_instructions: bool = True,
    ) -> dict[str, Any]:
        """
        Export script in ChatGPT-compatible format.

        Args:
            template_name: Template to use
            variables: Variable values
            include_instructions: Include usage instructions

        Returns:
            ChatGPT-formatted output
        """
        script = self.generate(template_name, variables)
        template = self.get_template(template_name)

        result: dict[str, Any] = {
            "name": template_name,
            "description": template.description if template else "",
            "api_request": {
                "method": self._infer_http_method(template_name),
                "endpoint": self._infer_endpoint(template_name),
                "body": script,
            },
        }

        if include_instructions and template:
            result["instructions"] = self._generate_instructions(template)
            result["variables"] = [
                {
                    "name": var.name,
                    "description": var.description,
                    "required": var.required,
                    "example": var.example,
                }
                for var in template.variables
            ]

        return result

    def export_for_zendesk_ai_assistant(
        self,
        template_name: str,
        variables: dict[str, Any] | None = None,
        *,
        include_context: bool = True,
    ) -> dict[str, Any]:
        """
        Export script in Zendesk AI Assistant format.

        Args:
            template_name: Template to use
            variables: Variable values
            include_context: Include context information

        Returns:
            Zendesk AI Assistant formatted output
        """
        script = self.generate(template_name, variables)
        template = self.get_template(template_name)

        result: dict[str, Any] = {
            "action": template_name,
            "category": template.category if template else "unknown",
            "payload": script,
        }

        if include_context and template:
            result["context"] = {
                "description": template.description,
                "tags": template.tags,
                "variables": [
                    {"name": var.name, "type": var.value_type, "required": var.required}
                    for var in template.variables
                ],
            }

        return result

    def _infer_http_method(self, template_name: str) -> str:
        """Infer HTTP method from template name."""
        if template_name.startswith("create_") or template_name.startswith("search_"):
            return "POST"
        if template_name.startswith("update_") or template_name.startswith("bulk_"):
            return "PUT"
        if template_name.startswith("delete_"):
            return "DELETE"
        return "GET"

    def _infer_endpoint(self, template_name: str) -> str:
        """Infer API endpoint from template name."""
        endpoints = {
            "create_ticket": "/api/v2/tickets.json",
            "update_ticket": "/api/v2/tickets/{ticket_id}.json",
            "close_ticket": "/api/v2/tickets/{ticket_id}.json",
            "create_user": "/api/v2/users.json",
            "create_sla_policy": "/api/v2/slas/policies.json",
            "bulk_update": "/api/v2/tickets/update_many.json",
            "search_tickets": "/api/v2/search.json",
        }
        return endpoints.get(template_name, "/api/v2/unknown.json")

    def _generate_instructions(self, template: ScriptTemplate) -> str:
        """Generate usage instructions for a template."""
        lines = [
            f"## {template.name}",
            "",
            template.description,
            "",
            "### Variables:",
            "",
        ]

        for var in template.variables:
            req_str = "(required)" if var.required else "(optional)"
            default_str = f" [default: {var.default}]" if var.default is not None else ""
            example_str = f" Example: {var.example}" if var.example else ""
            lines.append(f"- **{var.name}** {req_str}: {var.description}{default_str}{example_str}")

        return "\n".join(lines)

    def to_json(self, template_name: str, variables: dict[str, Any] | None = None) -> str:
        """
        Generate and serialize to JSON string.

        Args:
            template_name: Template to use
            variables: Variable values

        Returns:
            JSON string
        """
        return json.dumps(self.generate(template_name, variables), indent=2)


__all__ = [
    "PLACEHOLDER_PATTERN",
    "ScriptTemplate",
    "TemplateVariable",
    "ZendeskJSONGenerator",
]
