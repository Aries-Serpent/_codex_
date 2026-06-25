"""Image I/O helpers: load, save, and basic validation."""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

# Supported file extensions
_SUPPORTED = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}


def load_image(path: str | Path) -> np.ndarray:
    """Load an image and return a float32 RGB array in [0, 1].

    Parameters
    ----------
    path:
        Path to PNG, JPEG, TIFF, BMP, or WebP file.

    Returns
    -------
    np.ndarray
        Shape ``(H, W, 3)`` float32 in [0, 1].

    Raises
    ------
    FileNotFoundError
        When *path* does not exist.
    ValueError
        When the file extension is unsupported or the image cannot be decoded.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")
    if path.suffix.lower() not in _SUPPORTED:
        raise ValueError(f"Unsupported image format '{path.suffix}'. Use one of {_SUPPORTED}.")

    try:
        import imageio.v3 as iio

        img = iio.imread(str(path))
    except (IOError, OSError) as exc:
        raise ValueError(f"Cannot read image '{path}': {exc}") from exc

    img = _normalise(img)
    logger.debug("Loaded %s — shape %s dtype %s", path.name, img.shape, img.dtype)
    return img


def load_mask(path: str | Path) -> np.ndarray:
    """Load a binary mask (grayscale) and return a uint8 array.

    Non-zero pixels are treated as the region to inpaint.

    Returns
    -------
    np.ndarray
        Shape ``(H, W)`` uint8 with values 0 or 255.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Mask not found: {path}")

    import imageio.v3 as iio

    mask = iio.imread(str(path))
    if mask.ndim == 3:
        mask = mask[..., 0]
    return (mask > 0).astype(np.uint8) * 255


def save_image(image: np.ndarray, path: str | Path) -> Path:
    """Save a float32 [0,1] or uint8 image to *path*.

    Intermediate directories are created automatically.

    Returns
    -------
    Path
        Absolute path to the saved file.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if image.dtype != np.uint8:
        image = (np.clip(image, 0.0, 1.0) * 255).astype(np.uint8)

    import imageio.v3 as iio

    iio.imwrite(str(path), image)
    logger.info("Saved restored image → %s", path)
    return path.resolve()


# ── Internal helpers ──────────────────────────────────────────────────────────


def _normalise(img: np.ndarray) -> np.ndarray:
    """Convert any image array to float32 RGB [0, 1]."""
    if img.ndim == 2:
        # Grayscale → replicate to 3 channels
        img = np.stack([img, img, img], axis=-1)
    elif img.shape[2] == 4:
        # Drop alpha channel
        img = img[..., :3]
    elif img.shape[2] != 3:
        raise ValueError(f"Unexpected number of channels: {img.shape[2]}")

    if img.dtype == np.uint8:
        return img.astype(np.float32) / 255.0
    if img.dtype in (np.uint16, np.int32):
        return img.astype(np.float32) / 65535.0
    if img.dtype in (np.float32, np.float64):
        return img.astype(np.float32)

    raise ValueError(f"Unsupported array dtype: {img.dtype}")
