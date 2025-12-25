"""
Zendesk AI Package Curator.

Curates and packages Zendesk API integrations for various AI platforms:
- ChatGPT / Custom GPTs
- Zendesk AI Assistant
- General AI/LLM consumption

Provides tokenized patterns, intent handlers, and workflow templates.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class TargetPlatform(Enum):
    """Supported AI platforms for package export."""

    CHATGPT = "chatgpt"
    CUSTOM_GPT = "custom_gpt"
    ZENDESK_AI = "zendesk_ai"
    GENERIC = "generic"


@dataclass
class TokenizedPattern:
    """
    Represents a tokenized pattern for AI consumption.

    Patterns are reusable templates that AI systems can use to
    understand and execute Zendesk API operations.
    """

    name: str
    description: str
    category: str
    intent: str
    tokens: list[str]
    api_action: str
    api_endpoint: str
    http_method: str
    parameters: list[dict[str, Any]] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    response_template: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "intent": self.intent,
            "tokens": self.tokens,
            "api_action": self.api_action,
            "api_endpoint": self.api_endpoint,
            "http_method": self.http_method,
            "parameters": self.parameters,
            "examples": self.examples,
            "response_template": self.response_template,
        }


@dataclass
class WorkflowPattern:
    """
    Represents a multi-step workflow pattern.

    Workflows combine multiple API actions into a coherent sequence.
    """

    name: str
    description: str
    category: str
    steps: list[dict[str, Any]]
    triggers: list[str] = field(default_factory=list)
    conditions: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "steps": self.steps,
            "triggers": self.triggers,
            "conditions": self.conditions,
        }


class ZendeskPackageCurator:
    """
    Curates and packages Zendesk API integrations for AI platforms.

    Provides:
    - Tokenized pattern library
    - Intent handlers
    - Workflow templates
    - Multi-platform export

    Example:
        >>> curator = ZendeskPackageCurator()
        >>> package = curator.curate_chatgpt_package()
        >>> curator.export_package(package, "zendesk-chatgpt.json")
    """

    def __init__(self) -> None:
        """Initialize the curator with pattern library."""
        self._patterns: dict[str, TokenizedPattern] = {}
        self._workflows: dict[str, WorkflowPattern] = {}
        self._intents: dict[str, list[str]] = {}
        self._register_builtin_patterns()
        self._register_builtin_workflows()
        self._register_builtin_intents()

    def _register_builtin_patterns(self) -> None:
        """Register all built-in patterns."""
        # Ticket patterns
        self._register_ticket_patterns()
        # User patterns
        self._register_user_patterns()
        # SLA patterns
        self._register_sla_patterns()
        # Search patterns
        self._register_search_patterns()

    def _register_ticket_patterns(self) -> None:
        """Register ticket-related patterns."""
        self.register_pattern(
            TokenizedPattern(
                name="create_ticket",
                description="Create a new support ticket",
                category="tickets",
                intent="create_support_ticket",
                tokens=["create", "new", "ticket", "support", "request", "issue", "help"],
                api_action="create_ticket",
                api_endpoint="/api/v2/tickets.json",
                http_method="POST",
                parameters=[
                    {
                        "name": "subject",
                        "type": "string",
                        "required": True,
                        "description": "Ticket subject line",
                    },
                    {
                        "name": "description",
                        "type": "string",
                        "required": True,
                        "description": "Detailed issue description",
                    },
                    {
                        "name": "priority",
                        "type": "enum",
                        "values": ["low", "normal", "high", "urgent"],
                        "required": False,
                        "default": "normal",
                    },
                    {
                        "name": "requester_email",
                        "type": "email",
                        "required": True,
                        "description": "Customer email address",
                    },
                ],
                examples=[
                    "Create a ticket for billing issue",
                    "I need to submit a support request",
                    "Open a new ticket for login problem",
                ],
                response_template={
                    "success_message": "Ticket #{ticket_id} created successfully",
                    "fields_to_display": ["id", "subject", "status"],
                },
            )
        )

        self.register_pattern(
            TokenizedPattern(
                name="update_ticket_status",
                description="Update the status of an existing ticket",
                category="tickets",
                intent="update_ticket",
                tokens=["update", "change", "status", "ticket", "mark", "set"],
                api_action="update_ticket",
                api_endpoint="/api/v2/tickets/{ticket_id}.json",
                http_method="PUT",
                parameters=[
                    {
                        "name": "ticket_id",
                        "type": "integer",
                        "required": True,
                        "description": "The ticket ID to update",
                    },
                    {
                        "name": "status",
                        "type": "enum",
                        "values": ["open", "pending", "hold", "solved", "closed"],
                        "required": True,
                    },
                ],
                examples=[
                    "Mark ticket 12345 as solved",
                    "Change ticket status to pending",
                    "Close ticket #6789",
                ],
            )
        )

        self.register_pattern(
            TokenizedPattern(
                name="get_ticket",
                description="Retrieve details of a specific ticket",
                category="tickets",
                intent="view_ticket",
                tokens=["get", "show", "view", "find", "ticket", "details", "lookup"],
                api_action="get_ticket",
                api_endpoint="/api/v2/tickets/{ticket_id}.json",
                http_method="GET",
                parameters=[
                    {
                        "name": "ticket_id",
                        "type": "integer",
                        "required": True,
                        "description": "The ticket ID to retrieve",
                    },
                ],
                examples=[
                    "Show ticket 12345",
                    "Get details for ticket #9999",
                    "What's the status of ticket 5555?",
                ],
            )
        )

        self.register_pattern(
            TokenizedPattern(
                name="list_open_tickets",
                description="List all open tickets",
                category="tickets",
                intent="list_tickets",
                tokens=["list", "show", "all", "open", "tickets", "active", "pending"],
                api_action="list_tickets",
                api_endpoint="/api/v2/tickets.json",
                http_method="GET",
                parameters=[
                    {
                        "name": "status",
                        "type": "enum",
                        "values": ["open", "pending", "new"],
                        "required": False,
                    },
                    {
                        "name": "per_page",
                        "type": "integer",
                        "required": False,
                        "default": 25,
                    },
                ],
                examples=[
                    "Show all open tickets",
                    "List pending support requests",
                    "What tickets are waiting for response?",
                ],
            )
        )

    def _register_user_patterns(self) -> None:
        """Register user-related patterns."""
        self.register_pattern(
            TokenizedPattern(
                name="create_user",
                description="Create a new user account",
                category="users",
                intent="create_user",
                tokens=["create", "new", "user", "account", "add", "register"],
                api_action="create_user",
                api_endpoint="/api/v2/users.json",
                http_method="POST",
                parameters=[
                    {"name": "name", "type": "string", "required": True},
                    {"name": "email", "type": "email", "required": True},
                    {
                        "name": "role",
                        "type": "enum",
                        "values": ["end-user", "agent", "admin"],
                        "required": False,
                        "default": "end-user",
                    },
                ],
                examples=[
                    "Create a new user account",
                    "Add a customer to the system",
                    "Register new end-user",
                ],
            )
        )

        self.register_pattern(
            TokenizedPattern(
                name="lookup_user",
                description="Find a user by email or ID",
                category="users",
                intent="find_user",
                tokens=["find", "lookup", "search", "user", "customer", "email"],
                api_action="get_user",
                api_endpoint="/api/v2/users/{user_id}.json",
                http_method="GET",
                parameters=[
                    {"name": "user_id", "type": "integer", "required": True},
                ],
                examples=[
                    "Find user with email john@example.com",
                    "Look up customer account",
                    "Who is user 12345?",
                ],
            )
        )

    def _register_sla_patterns(self) -> None:
        """Register SLA-related patterns."""
        self.register_pattern(
            TokenizedPattern(
                name="check_sla_status",
                description="Check SLA compliance for a ticket",
                category="sla",
                intent="check_sla",
                tokens=["sla", "service", "level", "agreement", "compliance", "breach", "time"],
                api_action="get_sla_policy",
                api_endpoint="/api/v2/slas/policies.json",
                http_method="GET",
                parameters=[],
                examples=[
                    "Is ticket 12345 within SLA?",
                    "Check SLA status",
                    "Are we meeting our service levels?",
                ],
            )
        )

    def _register_search_patterns(self) -> None:
        """Register search-related patterns."""
        self.register_pattern(
            TokenizedPattern(
                name="search_tickets",
                description="Search for tickets with specific criteria",
                category="search",
                intent="search",
                tokens=["search", "find", "query", "filter", "tickets", "matching"],
                api_action="search",
                api_endpoint="/api/v2/search.json",
                http_method="GET",
                parameters=[
                    {"name": "query", "type": "string", "required": True},
                    {"name": "type", "type": "string", "required": False, "default": "ticket"},
                ],
                examples=[
                    "Search for urgent tickets",
                    "Find tickets about billing",
                    "Show me VIP customer tickets",
                ],
            )
        )

    def _register_builtin_workflows(self) -> None:
        """Register built-in workflow patterns."""
        self.register_workflow(
            WorkflowPattern(
                name="escalation_workflow",
                description="Escalate a ticket to higher support tier",
                category="support",
                steps=[
                    {
                        "action": "get_ticket",
                        "description": "Retrieve ticket details",
                    },
                    {
                        "action": "update_ticket",
                        "changes": {"priority": "urgent", "status": "open"},
                        "description": "Set priority to urgent",
                    },
                    {
                        "action": "add_comment",
                        "comment": "Escalating to Tier 2 support",
                        "internal": True,
                        "description": "Add escalation note",
                    },
                    {
                        "action": "assign_ticket",
                        "group": "tier2_support",
                        "description": "Assign to Tier 2 group",
                    },
                ],
                triggers=["escalate", "urgent", "priority", "tier 2"],
            )
        )

        self.register_workflow(
            WorkflowPattern(
                name="ticket_resolution_workflow",
                description="Close a ticket with customer satisfaction survey",
                category="support",
                steps=[
                    {
                        "action": "update_ticket",
                        "changes": {"status": "solved"},
                        "description": "Mark ticket as solved",
                    },
                    {
                        "action": "add_comment",
                        "comment": "Issue has been resolved. Please let us know if you need further assistance.",
                        "public": True,
                        "description": "Add resolution comment",
                    },
                    {
                        "action": "send_satisfaction_survey",
                        "description": "Trigger CSAT survey",
                    },
                ],
                triggers=["resolve", "close", "solved", "completed"],
            )
        )

        self.register_workflow(
            WorkflowPattern(
                name="new_customer_onboarding",
                description="Set up a new customer in Zendesk",
                category="customers",
                steps=[
                    {
                        "action": "create_user",
                        "description": "Create user account",
                    },
                    {
                        "action": "create_organization",
                        "description": "Create organization if needed",
                    },
                    {
                        "action": "assign_user_to_org",
                        "description": "Link user to organization",
                    },
                    {
                        "action": "send_welcome_email",
                        "description": "Send onboarding email",
                    },
                ],
                triggers=["new customer", "onboard", "setup", "register"],
            )
        )

    def _register_builtin_intents(self) -> None:
        """Register intent mappings."""
        self._intents = {
            "create_support_ticket": [
                "I need help with",
                "Create a ticket for",
                "Submit a support request",
                "Report an issue",
                "I have a problem with",
            ],
            "update_ticket": [
                "Update ticket",
                "Change the status of",
                "Mark as",
                "Set priority to",
                "Assign ticket to",
            ],
            "view_ticket": [
                "Show me ticket",
                "Get details for",
                "What's the status of",
                "Look up ticket",
                "Find ticket",
            ],
            "list_tickets": [
                "Show all tickets",
                "List open tickets",
                "What tickets are pending",
                "Display my tickets",
            ],
            "search": [
                "Search for",
                "Find tickets about",
                "Look for",
                "Query tickets",
            ],
            "create_user": [
                "Create a new user",
                "Add a customer",
                "Register a new account",
            ],
            "check_sla": [
                "Check SLA status",
                "Are we within SLA",
                "SLA compliance",
            ],
        }

    def register_pattern(self, pattern: TokenizedPattern) -> None:
        """Register a new pattern."""
        self._patterns[pattern.name] = pattern
        logger.debug(f"Registered pattern: {pattern.name}")

    def register_workflow(self, workflow: WorkflowPattern) -> None:
        """Register a new workflow."""
        self._workflows[workflow.name] = workflow
        logger.debug(f"Registered workflow: {workflow.name}")

    def get_pattern(self, name: str) -> TokenizedPattern | None:
        """Get a pattern by name."""
        return self._patterns.get(name)

    def get_workflow(self, name: str) -> WorkflowPattern | None:
        """Get a workflow by name."""
        return self._workflows.get(name)

    def list_patterns(self, category: str | None = None) -> list[TokenizedPattern]:
        """List patterns, optionally filtered by category."""
        patterns = list(self._patterns.values())
        if category:
            patterns = [p for p in patterns if p.category == category]
        return patterns

    def list_workflows(self, category: str | None = None) -> list[WorkflowPattern]:
        """List workflows, optionally filtered by category."""
        workflows = list(self._workflows.values())
        if category:
            workflows = [w for w in workflows if w.category == category]
        return workflows

    def curate_chatgpt_package(
        self,
        *,
        include_workflows: bool = True,
        include_examples: bool = True,
    ) -> dict[str, Any]:
        """
        Curate a package for ChatGPT / Custom GPT.

        Args:
            include_workflows: Include workflow patterns
            include_examples: Include example utterances

        Returns:
            Package dictionary ready for ChatGPT consumption
        """
        package: dict[str, Any] = {
            "name": "Zendesk Support Integration",
            "description": "AI-powered Zendesk Support API integration for ticket management, user operations, and SLA policies.",
            "version": "1.0.0",
            "platform": "chatgpt",
            "generated_at": datetime.utcnow().isoformat(),
            "capabilities": {
                "tickets": [
                    "Create tickets",
                    "Update ticket status",
                    "Search tickets",
                    "List tickets",
                    "Merge tickets",
                ],
                "users": ["Create users", "Look up users", "List users"],
                "sla": ["Check SLA compliance", "List SLA policies"],
                "search": ["Advanced search across all objects"],
            },
            "actions": [],
            "intents": self._intents,
        }

        # Add patterns as actions
        for pattern in self._patterns.values():
            action = {
                "name": pattern.name,
                "description": pattern.description,
                "api": {
                    "method": pattern.http_method,
                    "endpoint": pattern.api_endpoint,
                },
                "parameters": pattern.parameters,
            }
            if include_examples:
                action["examples"] = pattern.examples
            package["actions"].append(action)

        # Add workflows if requested
        if include_workflows:
            package["workflows"] = [w.to_dict() for w in self._workflows.values()]

        return package

    def curate_zendesk_ai_package(
        self,
        *,
        include_intents: bool = True,
    ) -> dict[str, Any]:
        """
        Curate a package for Zendesk AI Assistant.

        Args:
            include_intents: Include intent mappings

        Returns:
            Package dictionary for Zendesk AI
        """
        package: dict[str, Any] = {
            "integration": "zendesk_ai_assistant",
            "version": "1.0.0",
            "generated_at": datetime.utcnow().isoformat(),
            "patterns": [],
            "workflows": [],
        }

        # Add patterns
        for pattern in self._patterns.values():
            package["patterns"].append(
                {
                    "id": pattern.name,
                    "intent": pattern.intent,
                    "tokens": pattern.tokens,
                    "action": {
                        "type": pattern.api_action,
                        "endpoint": pattern.api_endpoint,
                        "method": pattern.http_method,
                    },
                    "parameters": pattern.parameters,
                }
            )

        # Add workflows
        for workflow in self._workflows.values():
            package["workflows"].append(
                {
                    "id": workflow.name,
                    "description": workflow.description,
                    "triggers": workflow.triggers,
                    "steps": workflow.steps,
                }
            )

        # Add intents if requested
        if include_intents:
            package["intents"] = self._intents

        return package

    def curate_generic_package(self) -> dict[str, Any]:
        """
        Curate a generic package for any AI/LLM consumption.

        Returns:
            Generic package dictionary
        """
        return {
            "name": "Zendesk API Integration",
            "version": "1.0.0",
            "generated_at": datetime.utcnow().isoformat(),
            "patterns": [p.to_dict() for p in self._patterns.values()],
            "workflows": [w.to_dict() for w in self._workflows.values()],
            "intents": self._intents,
            "documentation_url": "https://developer.zendesk.com/api-reference",
        }

    def export_package(
        self,
        package: dict[str, Any],
        output_path: str | Path,
        *,
        pretty: bool = True,
    ) -> Path:
        """
        Export a package to a JSON file.

        Args:
            package: Package dictionary to export
            output_path: Path to write the package
            pretty: Pretty print the JSON

        Returns:
            Path to the exported file
        """
        path = Path(output_path)
        indent = 2 if pretty else None

        with open(path, "w", encoding="utf-8") as f:
            json.dump(package, f, indent=indent)

        logger.info(f"Exported package to {path}")
        return path

    def match_intent(self, user_input: str) -> list[tuple[str, float]]:
        """
        Match user input to intents based on token overlap.

        Args:
            user_input: User's natural language input

        Returns:
            List of (intent, score) tuples, sorted by score
        """
        user_tokens = set(user_input.lower().split())
        matches = []

        for pattern in self._patterns.values():
            pattern_tokens = set(t.lower() for t in pattern.tokens)
            overlap = len(user_tokens & pattern_tokens)
            if overlap > 0:
                score = overlap / max(len(user_tokens), len(pattern_tokens))
                matches.append((pattern.intent, score))

        # Sort by score descending
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches

    def get_pattern_for_intent(self, intent: str) -> TokenizedPattern | None:
        """Get the best matching pattern for an intent."""
        for pattern in self._patterns.values():
            if pattern.intent == intent:
                return pattern
        return None


def main() -> None:
    """CLI entry point for package curation."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Zendesk AI Package Curator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--platform",
        choices=["chatgpt", "zendesk", "generic"],
        default="chatgpt",
        help="Target platform for the package",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="zendesk-package.json",
        help="Output file path",
    )
    parser.add_argument(
        "--no-workflows",
        action="store_true",
        help="Exclude workflows from package",
    )
    parser.add_argument(
        "--no-examples",
        action="store_true",
        help="Exclude examples from package",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print package to stdout instead of saving",
    )

    args = parser.parse_args()

    curator = ZendeskPackageCurator()

    # Generate package based on platform
    if args.platform == "chatgpt":
        package = curator.curate_chatgpt_package(
            include_workflows=not args.no_workflows,
            include_examples=not args.no_examples,
        )
    elif args.platform == "zendesk":
        package = curator.curate_zendesk_ai_package()
    else:
        package = curator.curate_generic_package()

    if args.dry_run:
        print(json.dumps(package, indent=2))
    else:
        curator.export_package(package, args.output)
        print(f"Package exported to {args.output}")


if __name__ == "__main__":
    main()


__all__ = [
    "ZendeskPackageCurator",
    "TokenizedPattern",
    "WorkflowPattern",
    "TargetPlatform",
]
