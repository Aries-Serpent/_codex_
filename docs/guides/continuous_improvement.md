# Continuous Improvement

This project includes maintenance utilities for pruning logs and keeping the repository tidy. The `tools/codex_maintenance.py` script is meant to run on a regular schedule so that artefacts do not accumulate.

## Local scheduling with cron

Use `cron` to run the maintenance script at an interval of your choice. The example below runs it every day at midnight:

```cron
0 0 * * * /usr/bin/env python /path/to/repo/tools/codex_maintenance.py >> /path/to/repo/.codex/maintenance.log 2>&1
```
Replace `/path/to/repo` with the absolute path on your machine. The script's output is appended to a local log file so you can review past runs.

## Local scheduling with a runner script

If you prefer not to modify your system's `cron` table, create a lightweight runner that you invoke manually or from another scheduling tool:

```bash
#!/usr/bin/env bash
python /path/to/repo/tools/codex_maintenance.py
```
Invoke this runner from `launchd`, `systemd`, or any other local scheduler you control. All resources remain on your machine; **do not** enable or rely on GitHub Actions or other hosted services.

## Rationale

Keeping the maintenance workflow local avoids exposing repository data to external services and keeps automation simple. Run the job on a workstation or server you manage, and adjust the interval to match your cleanup requirements.
