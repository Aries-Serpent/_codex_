# Zendesk API Reference Summary

This guide condenses the key configuration resources exposed by Zendesk's Support platform and related services. It focuses on the objects `_codex_` manages through snapshot, diff, plan, and apply workflows so that engineers can quickly locate the canonical endpoints and concepts for each resource family.

## Overview

The Zendesk Support API (also referred to as the Ticketing API) enables authenticated administrators to manage tickets, users, organizations, and business rules programmatically. Every request requires an API token or OAuth credential, respects rate limits, and supports pagination, filtering, and incremental exports where available.[^support-overview]

The sections below summarize common configuration resources together with representative endpoints and noteworthy behaviors. Follow the cited Zendesk documentation for exhaustive attribute definitions, request bodies, response schemas, and language-specific examples.

## Ticket Fields

Ticket fields capture structured metadata that agents and end users populate on tickets. Custom fields can be created, updated, reordered, or deleted; system fields expose limited mutability. Field definitions include identifiers, types, option lists, position, and localization details.[^ticket-fields]

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/v2/ticket_fields` | List fields with pagination and optional locale filters. |
| POST | `/api/v2/ticket_fields` | Create a custom field (e.g., `type`, `title`, and `custom_field_options`). |
| GET | `/api/v2/ticket_fields/{id}` | Retrieve a single field definition. |
| PUT | `/api/v2/ticket_fields/{id}` | Update field metadata or options. |
| DELETE | `/api/v2/ticket_fields/{id}` | Delete an eligible custom field. |
| PUT | `/api/v2/ticket_fields/reorder` | Reorder the displayed sequence of fields. |

## Ticket Forms

Ticket forms define which fields appear for a given workflow. Administrators can show different forms to agents and end users, control conditions, and reorder forms to adjust defaults.[^ticket-forms]

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/v2/ticket_forms` | List all forms with pagination. |
| GET | `/api/v2/ticket_forms/{id}` | Retrieve a single form. |
| GET | `/api/v2/ticket_forms/show_many?ids={ids}` | Fetch multiple forms by ID. |
| POST | `/api/v2/ticket_forms` | Create a new form and assign field IDs. |
| PUT | `/api/v2/ticket_forms/{id}` | Update form attributes such as visibility and conditions. |
| DELETE | `/api/v2/ticket_forms/{id}` | Delete a form. |
| PUT | `/api/v2/ticket_forms/reorder` | Reorder forms. |

## Groups

Groups bundle agents together for assignment and permissions. Zendesk enforces that each ticket has an owning group, and groups cannot be deleted while tickets reference them.[^groups]

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/v2/groups` | List groups, optionally limited to assignable groups. |
| GET | `/api/v2/groups/count` | Return a count of groups. |
| GET | `/api/v2/groups/{id}` | Retrieve group details. |
| POST | `/api/v2/groups` | Create a group. |
| PUT | `/api/v2/groups/{id}` | Update a group. |
| DELETE | `/api/v2/groups/{id}` | Delete a group (subject to constraints). |

## Triggers

Triggers evaluate ticket conditions immediately after creation or updates and run ordered actions such as notifications, assignments, or tag changes.[^triggers]

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/v2/triggers` | List triggers with pagination. |
| GET | `/api/v2/triggers/{id}` | Retrieve a trigger definition. |
| POST | `/api/v2/triggers` | Create a trigger. |
| PUT | `/api/v2/triggers/{id}` | Update a trigger. |
| PUT | `/api/v2/triggers/reorder` | Reorder trigger execution. |
| DELETE | `/api/v2/triggers/{id}` | Delete a trigger. |

## Macros

Macros encapsulate reusable ticket updates that agents can apply manually. Filters allow administrators to scope macros to groups, categories, or visibility levels.[^macros]

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/v2/macros` | List macros with filter parameters (e.g., `access`, `group_id`). |
| GET | `/api/v2/macros/{id}` | Retrieve macro details. |
| POST | `/api/v2/macros` | Create a macro. |
| PUT | `/api/v2/macros/{id}` | Update macro actions or metadata. |
| PUT | `/api/v2/macros/reorder` | Reorder macros. |
| DELETE | `/api/v2/macros/{id}` | Delete a macro. |

## Views

Views define how tickets are filtered, sorted, and displayed in agent queues. The API exposes endpoints to list, show, preview, update, reorder, and delete views, as well as to execute a view to fetch matching tickets.[^views]

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/v2/views` | List views. |
| GET | `/api/v2/views/{id}` | Retrieve a view. |
| PUT | `/api/v2/views/{id}` | Update filters, columns, and sorting. |
| POST | `/api/v2/views` | Create a view. |
| DELETE | `/api/v2/views/{id}` | Delete a view. |
| PUT | `/api/v2/views/reorder` | Reorder views. |
| GET | `/api/v2/views/{id}/execute` | Execute a view to retrieve tickets. |

## Webhooks

Webhooks send outbound HTTP requests when invoked by triggers, automations, or custom schedules. Administrators can test webhooks, rotate secrets, and manage subscriptions via the API.[^webhooks]

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/v2/webhooks` | List webhooks and subscriptions. |
| POST | `/api/v2/webhooks` | Create a webhook. |
| GET | `/api/v2/webhooks/{id}` | Retrieve webhook configuration. |
| PUT | `/api/v2/webhooks/{id}` | Update webhook details. |
| DELETE | `/api/v2/webhooks/{id}` | Delete a webhook. |
| POST | `/api/v2/webhooks/{id}/test` | Send a test payload. |

## Talk and IVR

Zendesk Talk offers voice support with configurable numbers, greetings, and IVR menus. The Talk Admin API covers greetings, IVR menus, agent availability, lines, and call routing rules.[^talk]

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/v2/talk/ivr_menus` | List IVR menus. |
| POST | `/api/v2/talk/ivr_menus` | Create an IVR menu. |
| PUT | `/api/v2/talk/ivr_menus/{id}` | Update an IVR menu. |
| GET | `/api/v2/talk/greetings` | List greetings. |
| POST | `/api/v2/talk/greetings` | Create a greeting. |
| PUT | `/api/v2/talk/greetings/{id}` | Update a greeting. |

## Skills-Based Routing

The Routing API enables skills-based routing policies that assign tickets to agents with matching skills and capacities. Resources include attributes (skill categories), values, agent assignments, and routing policies.[^routing]

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/v2/routing/attributes` | List skill attributes. |
| POST | `/api/v2/routing/attributes` | Create an attribute. |
| GET | `/api/v2/routing/attributes/{id}` | Retrieve an attribute. |
| PUT | `/api/v2/routing/attributes/{id}` | Update an attribute. |
| DELETE | `/api/v2/routing/attributes/{id}` | Delete an attribute. |
| GET | `/api/v2/routing/attributes/{id}/values` | List values for an attribute. |
| POST | `/api/v2/routing/policies` | Create or update routing policies. |

## Widgets

Zendesk offers both the Classic Web Widget and Messaging Web Widget for embedding support experiences. Configuration is driven by JSON settings, channel toggles, and branding options exposed through the widget APIs.[^widgets]

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/v2/widget/settings` | Retrieve widget settings. |
| PUT | `/api/v2/widget/settings` | Update widget configuration JSON. |
| POST | `/api/v2/widget/channels` | Enable or configure channels (e.g., chat, contact forms). |

## Apps

The Apps API allows administrators to upload and manage Zendesk App Framework (ZAF) packages, including private apps used internally.[^apps]

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/v2/apps/installations` | List installed apps. |
| POST | `/api/v2/apps/uploads` | Upload a packaged app (ZIP). |
| POST | `/api/v2/apps/installations` | Install an app from an upload. |
| PUT | `/api/v2/apps/installations/{id}` | Update an app installation. |
| DELETE | `/api/v2/apps/installations/{id}` | Uninstall an app. |

## Guide / Help Center

Guide powers the customer-facing help center. APIs cover themes, assets, and template modifications so that teams can version and deploy Guide customizations.[^guide]

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/v2/guide/themes` | List installed themes. |
| POST | `/api/v2/guide/themes` | Upload a theme package. |
| PUT | `/api/v2/guide/themes/{id}` | Update or publish a theme. |
| GET | `/api/v2/guide/themes/{id}/assets` | List theme assets. |
| PUT | `/api/v2/guide/themes/{id}/assets/{path}` | Update an asset or template file. |

## Additional References

* **Support API introduction** – conceptual overview and categories.[^support-intro]
* **Developer documentation home** – canonical hub for API specs, SDKs, and authentication guidance.[^dev-home]

[^support-overview]: https://developer.zendesk.com/api-reference/ticketing/introduction/
[^ticket-fields]: https://developer.zendesk.com/api-reference/ticketing/ticket-fields/ticket-fields/
[^ticket-forms]: https://developer.zendesk.com/api-reference/ticketing/ticket-forms/ticket-forms/
[^groups]: https://developer.zendesk.com/api-reference/ticketing/groups/groups/
[^triggers]: https://developer.zendesk.com/api-reference/ticketing/business-rules/triggers/
[^macros]: https://developer.zendesk.com/api-reference/ticketing/business-rules/macros/
[^views]: https://developer.zendesk.com/api-reference/ticketing/business-rules/views/
[^webhooks]: https://developer.zendesk.com/api-reference/ticketing/webhooks/webhooks/
[^talk]: https://developer.zendesk.com/api-reference/talk-api/talk-api/
[^routing]: https://developer.zendesk.com/api-reference/routing/introduction/
[^widgets]: https://developer.zendesk.com/api-reference/widget/introduction/
[^apps]: https://developer.zendesk.com/api-reference/apps/apps-api/apps/
[^guide]: https://developer.zendesk.com/api-reference/help_center/help-center-api/themes/
[^support-intro]: https://developer.zendesk.com/documentation/ticketing/reference-introduction/
[^dev-home]: https://developer.zendesk.com/api-reference/
