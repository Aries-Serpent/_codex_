#!/usr/bin/env python3
import json
import sys


def badge(n):
    try:
        n = int(n)
    except Exception:
        return f"`{n}`"
    return f"`{n}`" if 1 <= n <= 5 else f"`{n}`"


def main():
    if len(sys.argv) < 3:
        print("usage: render_md.py <status.json> <out.md>", file=sys.stderr)
        return 2
    with open(sys.argv[1], encoding="utf-8") as f:
        data = json.loads(f.read())
    lines = [f"# {data['metadata']['title']}", ""]
    lines += ["## Repo Map", "```", data["snapshot"]["repo_map"], "```", ""]
    lines += [
        "## Capabilities",
        "",
        "| Name | Category | Status | Sev | Conf | Artifacts |",
        "|---|---|---|---:|---:|---|",
    ]
    for c in data["snapshot"]["capabilities"]:
        lines += [
            f"| {c['name']} | {c.get('category','')} | {c['status']} | {badge(c.get('severity',3))} | {badge(c.get('confidence',3))} | {c.get('artifacts','')} |"
        ]
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(sys.argv[2])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
