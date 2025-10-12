# Zendesk API Catalog

This document enumerates the Zendesk API endpoints leveraged by the
`_codex_` Zendesk adapters. It captures method, path, authentication
requirements, rate limits, and any special notes. Refer to this
catalog when extending adapters or adding new resource types.

| Family | Method | Path | Auth/Scope | Notes |
|-------|--------|------|-----------|------|
| Triggers | GET/POST/PUT | `/api/v2/triggers` | API token or OAuth with `triggers:write` | Manage triggers (create/update/reorder) |
| Ticket Fields | GET/POST/PUT | `/api/v2/ticket_fields` | `ticket_fields:write` | Manage ticket fields |
| Ticket Forms | GET/POST/PUT | `/api/v2/ticket_forms` | `ticket_forms:write` | Manage forms and field assignments |
| Groups | GET/POST/PUT | `/api/v2/groups` | `groups:write` | Manage groups |
| Webhooks | GET/POST/PUT | `/api/v2/webhooks` | `webhooks:write` | Create/update webhooks and subscriptions |
| Talk IVR | GET/POST/PUT | `/api/v2/talk/ivr_menus` | `talk:write` | Manage IVR menus and routes |
| Routing | GET/POST/PUT | `/api/v2/routing/attributes` | `routing:write` | Manage attributes, skills, agent assignments |
| Widget | GET/POST/PUT | (dynamic via JSON) | API token | Manage widget snippets and settings |
| Apps | POST | `/api/v2/apps/private` | `apps:write` | Upload/update private apps |
| Guide Themes | GET/POST/PUT | `/api/v2/guide/themes` | `themes:write` | Manage themes and publications |

Additional endpoints (e.g., incremental exports) may be added later.
