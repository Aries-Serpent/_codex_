"""Command-line interface for the image restoration pipeline.

Usage examples::

    # Restore a single image
    python -m restore_pipeline.cli --input photo.jpg --output ./restored --verbose

    # Batch (folder)
    python -m restore_pipeline.cli --input ./raw_photos --output ./restored

    # With inpainting mask
    python -m restore_pipeline.cli --input photo.jpg --mask mask.png --output ./out

    # With deblurring + colorization
    python -m restore_pipeline.cli --input photo.jpg --deblur --colorize \\
        --colorize-model ./models/colorize.onnx --output ./out

    # Full options
    python -m restore_pipeline.cli --help
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

_SUPPORTED = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="restore_pipeline",
        description="CPU-only image restoration + vivid colour enhancement pipeline.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--input", "-i", required=True, help="Input image file or directory.")
    p.add_argument("--output", "-o", required=True, help="Output directory.")
    p.add_argument("--mask", help="Binary mask image (non-zero = inpaint region).")
    p.add_argument(
        "--reference",
        help="Reference image for metric computation (PSNR/SSIM) and optional Reinhard colour transfer.",  # noqa: E501
    )
    p.add_argument(
        "--algorithm",
        choices=["auto", "bm3d", "nl_means", "opencv"],
        default="auto",
        help="Denoising algorithm (default: auto).",
    )
    p.add_argument("--deblur", action="store_true", help="Enable Richardson–Lucy deblurring.")
    p.add_argument("--psf", help="PSF image path (used with --deblur).")
    p.add_argument("--colorize", action="store_true", help="Enable ONNX colorization (CPU).")
    p.add_argument(
        "--colorize-model",
        dest="colorize_model",
        help="Path to colorization ONNX model file.",
    )
    p.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging.")
    return p


def _collect_inputs(input_path: Path) -> list[Path]:
    if input_path.is_file():
        return [input_path]
    return sorted(f for f in input_path.rglob("*") if f.suffix.lower() in _SUPPORTED)


def run(argv: list[str] | None = None) -> int:
    """Entry point — returns exit code 0 on success."""
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s — %(message)s",
    )

    from restore_pipeline.config import PipelineConfig
    from restore_pipeline.io import load_image, load_mask, save_image
    from restore_pipeline.pipeline import process

    cfg = PipelineConfig(
        algorithm=args.algorithm,
        deblur=args.deblur,
        colorize=args.colorize,
        colorize_model_path=args.colorize_model or None,
    )

    input_path = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    files = _collect_inputs(input_path)
    if not files:
        logger.error("No supported images found in '%s'.", input_path)
        return 1

    mask = None
    if args.mask:
        mask = load_mask(args.mask)

    reference = None
    if args.reference:
        reference = load_image(args.reference)

    errors = 0
    for fp in files:
        try:
            img = load_image(fp)
            restored, metrics = process(img, mask=mask, reference=reference, config=cfg)
            out_path = output_dir / fp.name
            save_image(restored, out_path)

            if metrics:
                print(f"\n📊 Metrics — {fp.name}")
                for k, v in metrics.items():
                    print(f"   {k:<28} {v:+.4f}")
        except (IOError, OSError) as exc:
            logger.error("Failed to process '%s': %s", fp, exc)
            errors += 1

    print(f"\n✅ Processed {len(files) - errors}/{len(files)} image(s) → {output_dir}")
    return 1 if errors else 0


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
