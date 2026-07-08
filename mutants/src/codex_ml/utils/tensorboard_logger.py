"""Optional TensorBoard logger (offline-friendly).

Provides a context-managed SummaryWriter that gracefully degrades when
TensorBoard is unavailable or disabled.
"""

from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator

logger = logging.getLogger(__name__)


@contextmanager
def get_tb_writer(
    log_dir: str | Path | None = None, *, enabled: bool | None = None
) -> Generator[Any | None, None, None]:
    """Get TensorBoard SummaryWriter with graceful degradation.

    Parameters
    ----------
    log_dir : str | Path | None
        Directory for TensorBoard logs (default: artifacts/tb_runs)
    enabled : bool | None
        Override enablement (default: check CODEX_ENABLE_TENSORBOARD)

    Yields
    ------
    SummaryWriter | None
        Writer instance if enabled and available, None otherwise

    Examples
    --------
    >>> with get_tb_writer("runs/exp1") as writer:
    ...     if writer:
    ...         writer.add_scalar("loss", 0.5, step=0)
    """
    # Check if enabled
    if enabled is None:
        enabled = os.getenv("CODEX_ENABLE_TENSORBOARD") == "1"

    if not enabled:
        yield None
        return

    # Set default log directory
    log_dir = Path("artifacts/tb_runs") if log_dir is None else Path(log_dir)

    # Try to import TensorBoard
    writer = None
    try:
        # Try torch.utils.tensorboard first (comes with PyTorch)
        try:
            from torch.utils.tensorboard import SummaryWriter
        except ImportError as e:
            type(e).__name__
            logger.debug("ImportError: <ERROR_TYPE>")
            logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
            # Fallback to standalone tensorboard
            from tensorboardX import SummaryWriter  # type: ignore[no-redef]

        # Create log directory
        log_dir.mkdir(parents=True, exist_ok=True)

        # Create writer
        writer = SummaryWriter(str(log_dir))

        yield writer

    except ImportError as e:
        type(e).__name__
        logger.debug("ImportError: <ERROR_TYPE>")
        logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
        # TensorBoard not available - gracefully degrade
        yield None

    except (IOError, OSError):
        logger.warning("Exception occurred", exc_info=True)
        # Any other error - gracefully degrade
        yield None

    finally:
        # Close writer if created
        if writer is not None:
            try:
                writer.close()
            except (IOError, OSError):
                logger.warning("Exception occurred", exc_info=True)
                # Silently ignore close errors to ensure cleanup doesn't fail
                # the entire context. Common errors include already-closed writers
                # or filesystem issues during flush.


def is_tensorboard_available() -> bool:
    """Check if TensorBoard is available.

    Returns
    -------
    bool
        True if TensorBoard can be imported
    """
    try:
        try:
            from torch.utils.tensorboard import SummaryWriter as SummaryWriter

            return True
        except ImportError as e:
            type(e).__name__
            logger.debug("ImportError: <ERROR_TYPE>")
            logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
            from tensorboardX import SummaryWriter as SummaryWriter  # type: ignore[no-redef]

            return True
    except ImportError as e:
        type(e).__name__
        logger.debug("ImportError: <ERROR_TYPE>")
        logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
        return False
