# spectral.py
# PSD estimation with robust fallback:
# 1) Prefer Welch (scipy.signal.welch) for evenly-sampled series
# 2) If timestamps are uneven or Welch fails, prefer Astropy LombScargle
# 3) If Astropy is unavailable, fallback to SciPy's lombscargle
# Saves a PNG under ARTIFACTS_DIR and returns a small dict of summary stats.
#
# References:
# - Welch PSD: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.welch.html
# - Astropy LombScargle: https://docs.astropy.org/en/latest/timeseries/lombscargle.html
# - SciPy lombscargle: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.lombscargle.html

from __future__ import annotations

import datetime as dt
import json
import os
import warnings
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional, Tuple

import numpy as np


def _is_evenly_sampled(t: np.ndarray, rtol: float = 1e-2) -> bool:
    if t.size < 3:
        return True
    dt = np.diff(t)
    m = np.median(dt)
    return bool(np.allclose(dt, m, rtol=rtol, atol=0))


@dataclass
class PSDSummary:
    method: str
    n: int
    fmin: float
    fmax: float
    f_peak: float
    power_peak: float
    slope_lowfreq: Optional[float] = None  # tilt analog


def _welch_psd(y: np.ndarray, fs: float = 1.0):
    from scipy.signal import welch  # type: ignore

    f, pxx = welch(y, fs=fs, nperseg=min(256, y.size))
    return f, pxx


def _astropy_ls(t: np.ndarray, y: np.ndarray):
    from astropy.timeseries import LombScargle  # type: ignore

    # Let astropy choose a sensible grid
    freq, power = LombScargle(t, y).autopower()
    return freq, power


def _scipy_ls(t: np.ndarray, y: np.ndarray):
    # SciPy's lombscargle needs an explicit angular frequency grid
    from scipy.signal import lombscargle  # type: ignore

    # Build a simple grid from 0..Nyquist-like range
    tspan = t.max() - t.min() if t.size > 1 else 1.0
    # cycles per unit time; convert to angular frequency for SciPy
    f = np.linspace(1.0 / (tspan * 10), 0.5 * np.median(1 / np.diff(t)) if t.size > 2 else 1.0, 256)
    w = 2 * np.pi * f
    p = lombscargle(t - t.min(), y - np.mean(y), w)
    return f, p


def compute_psd(
    times: Optional[np.ndarray], values: np.ndarray, fs: Optional[float] = None
) -> Tuple[np.ndarray, np.ndarray, PSDSummary]:
    """Compute PSD with automatic fallback.
    - If times is None or evenly sampled and fs is provided -> Welch
    - Else try Astropy LombScargle, then SciPy lombscargle
    Returns (freq, power, summary)
    """

    values = np.asarray(values, dtype=float)
    if times is None:
        if fs is None:
            fs = 1.0
        f, p = _welch_psd(values, fs=fs)
        summary = PSDSummary(
            method="welch",
            n=values.size,
            fmin=float(f.min()),
            fmax=float(f.max()),
            f_peak=float(f[np.argmax(p)]),
            power_peak=float(np.max(p)),
        )
        return f, p, summary

    t = np.asarray(times, dtype=float)
    if _is_evenly_sampled(t) and fs is not None:
        try:
            f, p = _welch_psd(values, fs=fs)
            summary = PSDSummary(
                method="welch",
                n=values.size,
                fmin=float(f.min()),
                fmax=float(f.max()),
                f_peak=float(f[np.argmax(p)]),
                power_peak=float(np.max(p)),
            )
            return f, p, summary
        except Exception as e:
            warnings.warn(f"Welch failed: {e}; falling back to Lomb-Scargle")

    # Lomb-Scargle branch (Astropy preferred)
    try:
        f, p = _astropy_ls(t, values)
        method = "astropy_lombscargle"
    except Exception as e_astropy:
        warnings.warn(
            f"Astropy LombScargle unavailable/failed: {e_astropy}; trying SciPy lombscargle"
        )
        f, p = _scipy_ls(t, values)
        method = "scipy_lombscargle"

    # compute a crude low-frequency slope (spectral tilt analog) over the first decade of f
    try:
        # pick lowest 20% of nonzero frequencies
        idx = np.where(f > 0)[0]
        if idx.size > 10:
            k = max(10, idx.size // 5)
            fx = f[idx[:k]]
            px = p[idx[:k]]
            slope = np.polyfit(np.log(fx), np.log(np.maximum(px, 1e-12)), 1)[0]
        else:
            slope = None
    except Exception:
        slope = None

    summary = PSDSummary(
        method=method,
        n=values.size,
        fmin=float(np.min(f)),
        fmax=float(np.max(f)),
        f_peak=float(f[np.argmax(p)]),
        power_peak=float(np.max(p)),
        slope_lowfreq=slope,
    )
    return f, p, summary


def save_psd_plot(freq: np.ndarray, power: np.ndarray, out_path: Path, title: str = "PSD"):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.figure()
    plt.loglog(freq[freq > 0], np.maximum(power[freq > 0], 1e-12))
    plt.xlabel("Frequency")
    plt.ylabel("Power")
    plt.title(title)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()


def run_cli():
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--values",
        type=Path,
        required=True,
        help="Path to a newline-separated series of numeric values",
    )
    ap.add_argument(
        "--times",
        type=Path,
        help="Optional path to newline-separated timestamps (float)",
    )
    ap.add_argument(
        "--fs",
        type=float,
        default=None,
        help="Sampling frequency for evenly sampled series",
    )
    ap.add_argument(
        "--artifacts",
        type=Path,
        default=Path(os.getenv("ARTIFACTS_DIR", "artifacts")),
    )
    ap.add_argument(
        "--session-id",
        type=str,
        default=os.getenv("CODEX_SESSION_ID", "local"),
    )
    args = ap.parse_args()

    values = np.loadtxt(args.values, dtype=float)
    times = np.loadtxt(args.times, dtype=float) if args.times and args.times.exists() else None

    f, p, s = compute_psd(times, values, fs=args.fs)
    ts = int(dt.datetime.utcnow().timestamp())
    out_img = args.artifacts / f"psd_{args.session_id}_{ts}.png"
    out_json = args.artifacts / f"psd_{args.session_id}_{ts}.json"
    save_psd_plot(f, p, out_img, title=f"PSD ({s.method})")

    out_json.parent.mkdir(parents=True, exist_ok=True)
    with out_json.open("w", encoding="utf-8") as fh:
        json.dump(asdict(s), fh, indent=2)

    print(json.dumps({"ok": True, "img": str(out_img), "summary": asdict(s)}))


if __name__ == "__main__":
    run_cli()
