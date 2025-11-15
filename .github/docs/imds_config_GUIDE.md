# IMDS Config Guide
> Generated: 2025-11-14 23:14:07 UTC | Author: mbaetiong

## Purpose
Configure default behavior of `.github/scripts/imds_diagnostic.sh` via `.github/imds_config.yml` without changing CI or command-line flags.

## File Path
`.github/imds_config.yml`

## Supported Keys
| Key | Type | Default | Description |
|-----|------|---------|-------------|
| strict_approval | boolean | true | Require approval token for `--apply` |
| default_api_version | string | "2021-02-01" | IMDS API version used in HTTP calls |
| default_modes.json | boolean | false | Enable JSON output by default |
| default_modes.metrics | boolean | false | Enable metrics export by default |
| default_modes.html | boolean | false | Enable HTML report by default |
| issue_id | integer | 2226 | Issue reference used in audit JSONL and JSON summary |

## Example
