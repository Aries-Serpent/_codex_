from __future__ import annotations

from pathlib import Path
from typing import Any

from .data_report import build_data_drift


def run_data_drift_gate(
    reference_csv: Path,
    current_csv: Path,
    out_html: Path,
    out_json: Path,
    thresholds: dict[str, float],
    abort_on_critical: bool,
    tracked_columns: list[str] | None = None,
) -> dict[str, Any]:
    """Run data drift report and raise if thresholds exceeded when configured."""

    summary = build_data_drift(reference_csv, current_csv, out_html, out_json, tracked_columns)

    drift_share = float(summary.get("drift_share", 0.0))
    p_mean = float(summary.get("p_value_mean", 1.0))

    crit_share = float(thresholds.get("drift_share_critical", 0.5))
    crit_p = float(thresholds.get("p_value_critical", 0.05))

    gate_failed = drift_share >= crit_share or p_mean < crit_p
    summary["gate"] = {
        "fail": bool(gate_failed),
        "criteria": {"drift_share": crit_share, "p_value": crit_p},
    }

    if gate_failed and abort_on_critical:
        raise RuntimeError(
            "Data drift critical: "
            f"drift_share={drift_share:.3f} (>= {crit_share}), "
            f"p_mean={p_mean:.3f} (< {crit_p}). See {out_html} / {out_json}"
        )

    return summary
