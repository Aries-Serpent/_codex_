"""Optional TensorBoard logger (offline-friendly).

Provides a context-managed SummaryWriter that gracefully degrades when
TensorBoard is unavailable or disabled.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator


@contextmanager
def get_tb_writer(
    log_dir: str | Path | None = None,
    *,
    enabled: bool | None = None
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
    if log_dir is None:
        log_dir = Path("artifacts/tb_runs")
    else:
        log_dir = Path(log_dir)
    
    # Try to import TensorBoard
    writer = None
    try:
        # Try torch.utils.tensorboard first (comes with PyTorch)
        try:
            from torch.utils.tensorboard import SummaryWriter
        except ImportError:
            # Fallback to standalone tensorboard
            from tensorboardX import SummaryWriter
        
        # Create log directory
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create writer
        writer = SummaryWriter(str(log_dir))
        
        yield writer
        
    except ImportError:
        # TensorBoard not available - gracefully degrade
        yield None
        
    except Exception:
        # Any other error - gracefully degrade
        yield None
        
    finally:
        # Close writer if created
        if writer is not None:
            try:
                writer.close()
            except Exception:
                # Silently ignore close errors to ensure cleanup doesn't fail
                # the entire context. Common errors include already-closed writers
                # or filesystem issues during flush.
                pass


def is_tensorboard_available() -> bool:
    """Check if TensorBoard is available.
    
    Returns
    -------
    bool
        True if TensorBoard can be imported
    """
    try:
        try:
            from torch.utils.tensorboard import SummaryWriter  # noqa: F401
            return True
        except ImportError:
            from tensorboardX import SummaryWriter  # noqa: F401
            return True
    except ImportError:
        return False
