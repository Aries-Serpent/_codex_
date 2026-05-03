#!/usr/bin/env python3
"""
Coverage HTML to PDF Converter

Generates a single ephemeral PDF from coverage function_index.html files.
Output is 72 DPI resolution, black and white only.

Usage:
    python tools/coverage_html_to_pdf.py [--input-dir <coverage_html_dir>] [--output <output.pdf>]

Requirements:
    - weasyprint (for HTML to PDF conversion)

Install:
    pip install weasyprint
"""
from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path
from typing import Optional

# Repository root
ROOT = Path(__file__).resolve().parents[1]

# Default locations to search for coverage HTML
DEFAULT_COVERAGE_DIRS = [
    "htmlcov",
    "artifacts/coverage",
    "coverage_html",
    ".coverage_html",
]

# Target DPI for PDF output
TARGET_DPI = 72

# Fallback PDF text rendering constants
FALLBACK_LINE_LENGTH = 100
FALLBACK_MAX_LINES = 50


def find_function_index_files(search_dirs: Optional[list[Path]] = None) -> list[Path]:
    """
    Find all function_index.html files in the specified directories.

    Args:
        search_dirs: List of directories to search. If None, uses defaults.

    Returns:
        List of paths to function_index.html files
    """
    if search_dirs is None:
        search_dirs = [ROOT / d for d in DEFAULT_COVERAGE_DIRS]

    found_files = []
    for search_dir in search_dirs:
        if not search_dir.exists():
            continue

        # Direct file
        direct_file = search_dir / "function_index.html"
        if direct_file.exists():
            found_files.append(direct_file)

        # Recursive search
        for f in search_dir.rglob("function_index.html"):
            if f not in found_files:
                found_files.append(f)

    return sorted(set(found_files))


def convert_html_to_grayscale_css() -> str:
    """
    Generate CSS for black and white (grayscale) conversion.

    Returns:
        CSS string to apply grayscale filter
    """
    return """
    /* Black and white / grayscale conversion */
    html, body {
        filter: grayscale(100%) !important;
        -webkit-filter: grayscale(100%) !important;
    }

    /* Ensure all colors are converted to grayscale */
    * {
        color: black !important;
        background-color: white !important;
        border-color: #666 !important;
    }

    /* Preserve table structure readability */
    table {
        border-collapse: collapse;
    }

    th, td {
        border: 1px solid #333 !important;
        padding: 4px 8px;
    }

    th {
        background-color: #ccc !important;
        font-weight: bold;
    }

    /* Links in black */
    a {
        color: black !important;
        text-decoration: underline;
    }

    /* Coverage percentage styling */
    .pc_cov {
        font-weight: bold;
    }

    @page {
        size: letter;
        margin: 0.5in;
    }

    @media print {
        html, body {
            filter: grayscale(100%) !important;
        }
    }
    """


def create_combined_html(html_files: list[Path], output_path: Path) -> None:
    """
    Create a combined HTML file from multiple function_index.html files.

    Args:
        html_files: List of HTML file paths to combine
        output_path: Output path for combined HTML
    """
    combined_content = []
    combined_content.append("<!DOCTYPE html>")
    combined_content.append("<html lang='en'>")
    combined_content.append("<head>")
    combined_content.append("<meta charset='utf-8'>")
    combined_content.append("<title>Coverage Function Index - Combined Report</title>")
    combined_content.append("<style>")
    combined_content.append(convert_html_to_grayscale_css())
    combined_content.append("</style>")
    combined_content.append("</head>")
    combined_content.append("<body>")

    for i, html_file in enumerate(html_files):
        try:
            content = html_file.read_text(encoding="utf-8")

            # Extract body content if present
            body_match = re.search(r"<body[^>]*>(.*)</body>", content, re.DOTALL | re.IGNORECASE)
            if body_match:
                body_content = body_match.group(1)
            else:
                body_content = content

            # Add source header
            combined_content.append(
                f"<h2>Source: {html_file.relative_to(ROOT) if html_file.is_relative_to(ROOT) else html_file}</h2>"
            )
            combined_content.append("<hr>")
            combined_content.append(body_content)

            # Add page break between files
            if i < len(html_files) - 1:
                combined_content.append("<div style='page-break-after: always;'></div>")
        except Exception as e:
            print(f"Warning: Failed to read {html_file}: {e}", file=sys.stderr)
            continue

    combined_content.append("</body>")
    combined_content.append("</html>")

    output_path.write_text("\n".join(combined_content), encoding="utf-8")


def html_to_pdf(html_path: Path, pdf_path: Path, dpi: int = 72) -> bool:
    """
    Convert HTML file to PDF at specified DPI in grayscale.

    Args:
        html_path: Path to input HTML file
        pdf_path: Path to output PDF file
        dpi: Target DPI resolution (default: 72)

    Returns:
        True if successful, False otherwise
    """
    try:
        # Try weasyprint first (best quality)
        from weasyprint import CSS, HTML

        grayscale_css = CSS(string=convert_html_to_grayscale_css())

        html_doc = HTML(filename=str(html_path))
        html_doc.write_pdf(
            str(pdf_path),
            stylesheets=[grayscale_css],
            # WeasyPrint uses 96 DPI by default, scale accordingly
            zoom=dpi / 96.0,
        )
        return True
    except ImportError:
        pass

    # Fallback: Try pdfkit (requires wkhtmltopdf)
    try:
        import pdfkit

        options = {
            "grayscale": "",
            "dpi": str(dpi),
            "page-size": "Letter",
            "margin-top": "0.5in",
            "margin-right": "0.5in",
            "margin-bottom": "0.5in",
            "margin-left": "0.5in",
            "encoding": "UTF-8",
        }

        pdfkit.from_file(str(html_path), str(pdf_path), options=options)
        return True
    except ImportError:
        pass
    except Exception as e:
        print(f"pdfkit failed: {e}", file=sys.stderr)

    # Last resort: Create a simple text-based PDF
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        from reportlab.pdfgen import canvas

        # Read HTML and extract text content
        html_content = html_path.read_text(encoding="utf-8")

        # Strip HTML tags for simple text extraction
        text_content = re.sub(r"<[^>]+>", " ", html_content)
        text_content = re.sub(r"\s+", " ", text_content).strip()

        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        width, height = letter

        c.setFont("Helvetica", 10)

        # Simple text wrapping using configurable constants
        y = height - inch
        lines = [
            text_content[i : i + FALLBACK_LINE_LENGTH]
            for i in range(0, len(text_content), FALLBACK_LINE_LENGTH)
        ]

        for line in lines[:FALLBACK_MAX_LINES]:
            if y < inch:
                c.showPage()
                y = height - inch
                c.setFont("Helvetica", 10)
            c.drawString(inch, y, line)
            y -= 12

        c.save()
        return True
    except ImportError:
        pass

    print("Error: No PDF conversion library available.", file=sys.stderr)
    print("Install one of: weasyprint, pdfkit (with wkhtmltopdf), or reportlab", file=sys.stderr)
    return False


def main(argv: Optional[list[str]] = None) -> int:
    """
    Main entry point for coverage HTML to PDF conversion.

    Args:
        argv: Command line arguments (uses sys.argv if None)

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    parser = argparse.ArgumentParser(
        description="Convert coverage function_index.html files to a single PDF"
    )
    parser.add_argument(
        "--input-dir",
        "-i",
        type=Path,
        action="append",
        help="Directory containing coverage HTML (can be specified multiple times)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("coverage_functions.pdf"),
        help="Output PDF file path (default: coverage_functions.pdf)",
    )
    parser.add_argument(
        "--dpi", type=int, default=TARGET_DPI, help=f"PDF resolution in DPI (default: {TARGET_DPI})"
    )
    parser.add_argument(
        "--persistent",
        action="store_true",
        help="Mark PDF as persistent (default: ephemeral/temporary)",
    )

    args = parser.parse_args(argv)

    # Find function_index.html files
    search_dirs = args.input_dir if args.input_dir else None
    html_files = find_function_index_files(search_dirs)

    if not html_files:
        print("No function_index.html files found.", file=sys.stderr)
        print(
            f"Searched in: {search_dirs or [ROOT / d for d in DEFAULT_COVERAGE_DIRS]}",
            file=sys.stderr,
        )
        return 1

    print(f"Found {len(html_files)} function_index.html file(s):")
    for f in html_files:
        print(f"  - {f}")

    # Create combined HTML in temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        combined_html = Path(tmpdir) / "combined_coverage.html"
        create_combined_html(html_files, combined_html)

        # Convert to PDF
        output_path = args.output
        output_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"\nGenerating PDF at {args.dpi} DPI (black & white)...")

        if html_to_pdf(combined_html, output_path, dpi=args.dpi):
            print(f"[OK] PDF generated: {output_path}")
            if not args.persistent:
                print("     (ephemeral - can be cleaned up after use)")
            return 0
        print("[FAIL] PDF generation failed", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
