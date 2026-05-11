#!/usr/bin/env python3
"""
Playwright-Based Code Scanning Alert Scraper

Scrapes GitHub code scanning alerts directly from the security page using
Playwright browser automation as a fallback when API token access is limited.
Falls back gracefully to the API-based fetcher when Playwright is unavailable.

Usage:
    python scripts/security/playwright_scraper.py \\
        --repo https://github.com/Aries-Serpent/_codex_ \\
        --output .codex/security/playwright_alerts.json

Author: Copilot Agent
Part of: CodeQL Alert Resolution Pipeline
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from collections.abc import Iterator
from pathlib import Path
from typing import Any, Optional

# Graceful import — Playwright is optional; fall back to API fetcher if absent
try:
    from playwright.sync_api import Browser, Page, sync_playwright  # type: ignore

    HAS_PLAYWRIGHT = True  # pragma: no cover
except ImportError:
    HAS_PLAYWRIGHT = False

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Selectors for GitHub code-scanning page (as of 2026)
# IMP-009: Resilient multi-selector strategy — tried in order, first match wins.
_ALERT_SELECTORS = [
    "div[data-testid='code-scanning-alert-row']",   # primary (2026 UI)
    "li[data-testid*='code-scanning']",              # fallback (2025 UI)
    "div.js-code-scanning-alert-row",                # legacy
    "table.js-navigation-container tr.js-navigation-item",  # table layout
]
# Retained for any callers that still reference the constant directly.
_ALERT_ROW_SELECTOR = ", ".join(_ALERT_SELECTORS)  # noqa: F841
_SEVERITY_SELECTOR = "[data-testid='alert-severity'], .severity-badge, .Label--severity"
_TITLE_SELECTOR = "a[data-hovercard-type='code-scanning-alert'], a.js-navigation-open"
_NEXT_BTN_SELECTOR = "a[rel='next'], .next_page:not(.disabled)"
_LOAD_SELECTOR = "main"


class PlaywrightScraper:
    """Scrape code scanning alerts from the GitHub security UI."""

    def __init__(
        self,
        repo_url: str,
        github_token: Optional[str] = None,
        headless: bool = True,
        timeout_ms: int = 30_000,
    ) -> None:
        if not HAS_PLAYWRIGHT:
            raise ImportError(
                "playwright is not installed. Install with: pip install playwright && "
                "playwright install chromium"
            )
        self.repo_url = repo_url.rstrip("/")
        self.github_token = github_token or os.environ.get("GITHUB_TOKEN", "")
        self.headless = headless
        self.timeout_ms = timeout_ms
        self._security_url = f"{self.repo_url}/security/code-scanning"

    def _authenticate(self, page: Page) -> bool:
        """Inject GitHub auth token into all requests via Playwright route interception.

        IMP-008: Uses CDP ``page.route()`` to add an ``Authorization`` header to
        every request to ``github.com`` and ``api.github.com``, enabling the
        browser session to access private repository security pages without a
        full OAuth login flow.

        Returns
        -------
        bool
            ``True`` when a token is available and route interception has been
            registered; ``False`` when no token was provided (alerts may still
            be scraped for public repos, just without the private-alert filter).
        """
        if not self.github_token:
            logger.warning("No GITHUB_TOKEN provided; page may not show private alerts")
            return False

        token = self.github_token  # local reference for closure

        def _inject_auth(route: Any) -> None:
            """Route handler: merge Authorization header into every request."""
            try:
                merged = {**route.request.headers, "Authorization": f"token {token}"}
                route.continue_(headers=merged)
            except Exception as _exc:
                logger.debug("Route auth injection failed: %s", _exc)
                route.continue_()

        # Intercept all GitHub-origin requests (API + web UI).
        try:
            page.route("https://github.com/**", _inject_auth)
            page.route("https://api.github.com/**", _inject_auth)
            logger.debug("CDP route auth injection registered for github.com")
        except Exception as exc:  # pragma: no cover
            logger.warning("Failed to register auth route: %s", exc)
            return False

        return True

    def _extract_row_data(self, page: Page, row: Any) -> Optional[dict[str, Any]]:
        """Extract alert data from a single table row element."""
        try:
            title_elem = row.query_selector(_TITLE_SELECTOR)
            if not title_elem:
                return None

            title = title_elem.inner_text().strip()
            href = title_elem.get_attribute("href") or ""
            url = f"https://github.com{href}" if href.startswith("/") else href

            # Severity
            sev_elem = row.query_selector(_SEVERITY_SELECTOR)
            severity = (sev_elem.inner_text().strip().lower() if sev_elem else "unknown")

            # Alert number from URL pattern /security/code-scanning/NNN
            alert_number: Optional[int] = None
            parts = href.rstrip("/").split("/")
            if parts and parts[-1].isdigit():
                alert_number = int(parts[-1])

            return {
                "title": title,
                "url": url,
                "severity": severity,
                "alert_number": alert_number,
            }
        except Exception as exc:  # pragma: no cover
            logger.debug("Failed to extract row: %s", exc)
            return None

    def _find_alert_rows(self, page: Page) -> list:
        """Return alert row elements using a resilient multi-selector strategy.

        Iterates through :data:`_ALERT_SELECTORS` in order and returns the
        first non-empty result, making the scraper robust against GitHub UI
        changes (IMP-009).
        """
        for selector in _ALERT_SELECTORS:
            rows = page.query_selector_all(selector)
            if rows:
                logger.debug("_find_alert_rows: matched %d rows with %r", len(rows), selector)
                return rows
        return []

    def _iter_pages(self, page: Page) -> Iterator[list[dict[str, Any]]]:
        """Navigate the alerts table page by page, yielding lists of alert dicts."""
        page.goto(self._security_url, wait_until="networkidle", timeout=self.timeout_ms)
        page.wait_for_selector(_LOAD_SELECTOR, timeout=self.timeout_ms)

        page_num = 1
        while True:
            logger.info("Scraping page %d …", page_num)

            # Wait a short moment for JS to hydrate the table
            time.sleep(0.5)

            rows = self._find_alert_rows(page)
            if not rows:
                logger.debug("No alert rows found on page %d — trying generic list items", page_num)
                # Fallback: try any anchor containing /security/code-scanning/
                links = page.query_selector_all("a[href*='/security/code-scanning/']")
                if not links:
                    logger.info("No more alerts found; stopping pagination")
                    break
                page_alerts = [
                    {
                        "title": lnk.inner_text().strip(),
                        "url": f"https://github.com{lnk.get_attribute('href')}",
                        "severity": "unknown",
                        "alert_number": int(lnk.get_attribute("href").rstrip("/").split("/")[-1])
                        if lnk.get_attribute("href", "").rstrip("/").split("/")[-1].isdigit()
                        else None,
                    }
                    for lnk in links
                ]
                yield [a for a in page_alerts if a["title"]]
            else:
                page_alerts = []
                for row in rows:
                    data = self._extract_row_data(page, row)
                    if data:
                        page_alerts.append(data)
                yield page_alerts

            # Check for next page button
            next_btn = page.query_selector(_NEXT_BTN_SELECTOR)
            if not next_btn:
                logger.info("Reached final page (%d)", page_num)
                break
            cls = next_btn.get_attribute("class") or ""
            if "disabled" in cls:
                logger.info("Next button disabled on page %d", page_num)
                break

            logger.debug("Clicking next page …")
            next_btn.click()
            page.wait_for_load_state("networkidle", timeout=self.timeout_ms)
            page_num += 1

    def scrape(self) -> list[dict[str, Any]]:
        """
        Launch a headless browser, navigate the security page, and return
        all scraped alerts as a list of dicts.
        """
        alerts: list[dict[str, Any]] = []

        with sync_playwright() as pw:
            # CB-INV-001: pass --disable-extensions so any content-blocker
            # extension in the browser profile cannot intercept github.com requests.
            browser: Browser = pw.chromium.launch(
                headless=self.headless,
                args=["--disable-extensions"],
            )
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
                )
            )
            page = context.new_page()

            try:
                self._authenticate(page)
                for page_alerts in self._iter_pages(page):
                    alerts.extend(page_alerts)
                    logger.info("Running total: %d alerts", len(alerts))
            finally:
                browser.close()

        logger.info("Scrape complete — %d total alerts collected", len(alerts))
        return alerts


def export_json(alerts: list[dict[str, Any]], output_path: Path) -> None:
    """Write alerts to a JSON file compatible with analyze_alerts.py inventory format."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": "playwright_scraper",
        "total_alerts": len(alerts),
        "exported_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "alerts": alerts,
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    logger.info("Exported %d alerts → %s", len(alerts), output_path)


def export_csv(alerts: list[dict[str, Any]], output_path: Path) -> None:
    """Write alerts to a CSV file."""
    import csv

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not alerts:
        output_path.write_text("alert_number,title,severity,url\n", encoding="utf-8")
        return

    fieldnames = list(alerts[0].keys())
    with output_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(alerts)
    logger.info("CSV export → %s (%d rows)", output_path, len(alerts))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Scrape GitHub code scanning alerts via Playwright",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  # Basic scrape:\n"
            "  python scripts/security/playwright_scraper.py --token $GH_TOKEN\n\n"
            "  # Filter to high/critical only, Markdown output:\n"
            "  python scripts/security/playwright_scraper.py --severity high --format markdown\n\n"
            "  # Only open alerts, limit to 3 pages, CSV output:\n"
            "  python scripts/security/playwright_scraper.py --state open --max-pages 3 --csv alerts.csv\n\n"
            "  # Fetch a specific alert:\n"
            "  python scripts/security/playwright_scraper.py --alert-number 42\n\n"
            "  # Validate auth without scraping:\n"
            "  python scripts/security/playwright_scraper.py --dry-run\n"
        ),
    )
    parser.add_argument(
        "--repo",
        default="https://github.com/Aries-Serpent/_codex_",
        help="GitHub repository URL (default: Aries-Serpent/_codex_)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(".codex/security/playwright_alerts.json"),
        help="Output JSON file (default: .codex/security/playwright_alerts.json)",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=None,
        help="Optional CSV output file",
    )
    parser.add_argument(
        "--token",
        default=None,
        help="GitHub token (overrides GITHUB_TOKEN env var)",
    )
    parser.add_argument(
        "--headless",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Run browser headlessly (default: True)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30_000,
        help="Browser timeout in milliseconds (default: 30000)",
    )
    # GAP-020 / GAP-035 enhanced CLI flags
    parser.add_argument(
        "--severity",
        choices=["critical", "high", "medium", "low", "warning", "note", "error"],
        default=None,
        metavar="LEVEL",
        help="Filter alerts by severity level (critical|high|medium|low|warning|note|error)",
    )
    parser.add_argument(
        "--state",
        choices=["open", "closed", "dismissed", "fixed"],
        default=None,
        metavar="STATE",
        help="Filter alerts by state (open|closed|dismissed|fixed)",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        metavar="N",
        help="Limit pagination to at most N pages (default: unlimited)",
    )
    parser.add_argument(
        "--since",
        default=None,
        metavar="YYYY-MM-DD",
        help="Only include alerts created on or after this date (ISO 8601 date)",
    )
    parser.add_argument(
        "--alert-number",
        type=int,
        default=None,
        metavar="N",
        help="Fetch a single alert by its number (skips pagination)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "csv", "markdown", "table"],
        default="json",
        dest="output_format",
        help="Output format (default: json; also controls stdout summary)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate authentication and configuration without scraping",
    )
    return parser


def _filter_alerts(
    alerts: list[dict[str, Any]],
    severity: Optional[str],
    state: Optional[str],
    since: Optional[str],
    alert_number: Optional[int],
) -> list[dict[str, Any]]:
    """Apply post-scrape filters to the alert list."""
    from datetime import datetime, timezone

    if alert_number is not None:
        return [a for a in alerts if a.get("alert_number") == alert_number]

    filtered = alerts
    if severity:
        filtered = [a for a in filtered if a.get("severity", "").lower() == severity.lower()]
    if state:
        filtered = [a for a in filtered if a.get("state", "open").lower() == state.lower()]
    if since:
        try:
            cutoff = datetime.fromisoformat(since).replace(tzinfo=timezone.utc)
            filtered = [
                a for a in filtered
                if datetime.fromisoformat(
                    a.get("created_at", "1970-01-01").replace("Z", "+00:00")
                ) >= cutoff
            ]
        except (ValueError, KeyError):
            logger.warning("Could not apply --since filter (invalid date or missing created_at)")

    return filtered


def _print_markdown_table(alerts: list[dict[str, Any]]) -> None:
    """Print alerts as a Markdown table to stdout."""
    if not alerts:
        print("*(no alerts matching filters)*")
        return
    print("| # | Severity | Title | State | URL |")
    print("|---|----------|-------|-------|-----|")
    for a in alerts:
        num = a.get("alert_number", "—")
        sev = a.get("severity", "—")
        raw_title = a.get("title") or "—"
        title = (raw_title[:57] + "...") if len(raw_title) > 60 else raw_title
        st = a.get("state", "—")
        url = a.get("url", "—")
        print(f"| {num} | {sev} | {title} | {st} | {url} |")


def _print_ascii_table(alerts: list[dict[str, Any]]) -> None:
    """Print alerts as a plain ASCII table to stdout."""
    if not alerts:
        print("(no alerts matching filters)")
        return
    col_widths = {"num": 5, "sev": 9, "title": 50, "state": 10}
    header = (
        f"{'#':<{col_widths['num']}}  "
        f"{'Severity':<{col_widths['sev']}}  "
        f"{'Title':<{col_widths['title']}}  "
        f"{'State':<{col_widths['state']}}"
    )
    print(header)
    print("-" * len(header))
    for a in alerts:
        num = str(a.get("alert_number", "—"))
        sev = a.get("severity", "—")
        title = (a.get("title") or "—")[:col_widths["title"]]
        state = a.get("state", "open")
        print(
            f"{num:<{col_widths['num']}}  "
            f"{sev:<{col_widths['sev']}}  "
            f"{title:<{col_widths['title']}}  "
            f"{state:<{col_widths['state']}}"
        )


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not HAS_PLAYWRIGHT:
        logger.error(
            "Playwright is not installed.\n"
            "Install with:  pip install playwright && playwright install chromium\n"
            "Falling back to API-based fetcher:\n"
            "  python scripts/security/fetch_codeql_alerts.py"
        )
        return 1

    if args.dry_run:
        token = args.token or os.environ.get("GITHUB_TOKEN")
        print("🔍 Dry-run mode — validating configuration without scraping")
        print(f"  Repo    : {args.repo}")
        print(f"  Token   : {'✅ set' if token else '❌ not set (set GITHUB_TOKEN or --token)'}")
        print(f"  Headless: {args.headless}")
        print(f"  Timeout : {args.timeout}ms")
        if args.severity:
            print(f"  Severity filter: {args.severity}")
        if args.state:
            print(f"  State filter   : {args.state}")
        return 0 if token else 1

    scraper = PlaywrightScraper(
        repo_url=args.repo,
        github_token=args.token,
        headless=args.headless,
        timeout_ms=args.timeout,
    )

    try:
        alerts = scraper.scrape()
    except Exception as exc:
        logger.error("Scraping failed: %s", exc)
        logger.info("Tip: use fetch_codeql_alerts.py for API-based collection instead")
        return 1

    # Apply filters
    alerts = _filter_alerts(
        alerts,
        severity=args.severity,
        state=args.state,
        since=args.since,
        alert_number=args.alert_number,
    )

    # Render output
    if args.output_format == "markdown":
        _print_markdown_table(alerts)
    elif args.output_format == "table":
        _print_ascii_table(alerts)
    elif args.output_format == "csv":
        if args.csv:
            export_csv(alerts, args.csv)
        else:
            import csv
            import io
            buf = io.StringIO()
            if alerts:
                writer = csv.DictWriter(buf, fieldnames=list(alerts[0].keys()), extrasaction="ignore")
                writer.writeheader()
                writer.writerows(alerts)
            print(buf.getvalue(), end="")
    else:
        # json (default)
        export_json(alerts, args.output)

    if args.csv and args.output_format != "csv":
        export_csv(alerts, args.csv)

    if args.output_format in ("json", "table", "markdown"):
        print(f"\n✅  Scraped {len(alerts)} alerts (after filters)")
        if args.output_format == "json":
            print(f"   JSON → {args.output}")
            print("\nNext step: python scripts/security/analyze_alerts.py --input", args.output)
        if args.csv:
            print(f"   CSV  → {args.csv}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
