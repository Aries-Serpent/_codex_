# Codex CRM Canonical Data Model

The canonical data model (CDM) lives in `config/cdm/*.csv` and defines the
entities and fields that drive every downstream scaffold and generator.

Each CSV row maps to a `FieldDef` structure, which captures:

- `name`: Display label presented to admins and agents.
- `key`: Stable identifier used for mappings across platforms.
- `type`: Semantic type (e.g. `integer`, `choice`, `lookup`).
- `required`: Boolean flag controlling validation requirements.
- `choices`: Optional pipe-delimited enumerations.
- `default`: Optional default value.

The loader utilities consume these CSVs and surface strongly typed data for the
CLI, generators, and conversion kernels.
