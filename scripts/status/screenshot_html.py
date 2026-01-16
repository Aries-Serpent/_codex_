#!/usr/bin/env python3
"""
Screenshot Html

Purpose:
    Command-line utility (see argument parser for details)

Usage:
    python scripts/status/screenshot_html.py [options]
    
    Examples:
    $ python scripts/status/screenshot_html.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""


from __future__ import annotations

import argparse
from pathlib import Path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Capture a screenshot (PNG) of an HTML file using Playwright"
    )
    ap.add_argument("--html", required=True, help="Path to HTML file")
    ap.add_argument("--out", required=True, help="Path to output PNG")
    ap.add_argument("--viewport-width", type=int, default=1280)
    ap.add_argument("--viewport-height", type=int, default=800)
    args = ap.parse_args(argv)

    from playwright.sync_api import sync_playwright  # type: ignore

    html_path = Path(args.html).resolve()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": args.viewport_width, "height": args.viewport_height}
        )
        page.goto(f"file://{html_path}")
        page.screenshot(path=str(out_path), full_page=True)
        browser.close()
    print(f"[OK] Wrote screenshot {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
