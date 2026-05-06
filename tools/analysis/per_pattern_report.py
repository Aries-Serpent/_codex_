"""
Per-Pattern Accuracy Report

Groups scalability test results by scenario pattern and reports accuracy per pattern.
Used for STEP B investigation when scalability verification fails.

Usage:
    python tools/analysis/per_pattern_report.py <results_json> [--min-accuracy 0.95]

Example:
    python tools/analysis/per_pattern_report.py \
        audit_artifacts/results/phase4_scalability_raw.json
"""

import json
import sys


def load_results(path: str) -> dict:
    """Load scalability JSON results from disk."""
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def extract_pattern(audit_id: str) -> str:
    """Extract pattern letter from audit_id (e.g. 'COMPLEX-A-3' -> 'A')."""
    parts = audit_id.split("-")
    if len(parts) >= 2:
        return parts[1]
    return "UNKNOWN"


def compute_per_pattern_stats(
    per_seed_results: list[dict],
) -> dict[str, dict]:
    """
    Aggregate mismatch data across all seeds by scenario pattern.

    Returns a dict mapping pattern_letter -> {total, failures, accuracy, examples}.
    """
    pattern_failures: dict[str, list[dict]] = {}

    for seed_result in per_seed_results:
        seed = seed_result.get("seed", "?")
        mismatches = seed_result.get("mismatches", [])

        # We only have mismatch records, not all scenario IDs.
        # Estimate per-pattern totals proportionally from known distribution.
        for m in mismatches:
            pattern = extract_pattern(m.get("audit_id", ""))
            pattern_failures.setdefault(pattern, []).append({**m, "seed": seed})

    # We can only compute per-pattern failure counts from the mismatch data;
    # use the total scenario count and known pattern proportions as denominator.
    # Pattern proportions (from complex_scenarios.py generate_complex_scenarios):
    pattern_proportions = {
        "A": 0.15, "B": 0.15, "C": 0.15, "D": 0.15,
        "E": 0.15, "F": 0.15, "G": 0.10, "H": 0.10,
    }

    total_scenarios_all_seeds = sum(r.get("total_scenarios", 0) for r in per_seed_results)

    stats: dict[str, dict] = {}
    all_patterns = set(pattern_failures.keys()) | set(pattern_proportions.keys())
    for pattern in sorted(all_patterns):
        proportion = pattern_proportions.get(pattern, 0.0)
        estimated_total = int(total_scenarios_all_seeds * proportion)
        failures = pattern_failures.get(pattern, [])
        n_fail = len(failures)
        accuracy = 1.0 - (n_fail / max(1, estimated_total))
        stats[pattern] = {
            "estimated_total": estimated_total,
            "failures": n_fail,
            "accuracy": accuracy,
            "examples": failures[:5],
        }

    return stats


def print_report(stats: dict[str, dict], min_accuracy: float = 0.95) -> bool:
    """Print per-pattern accuracy report. Returns True if all patterns pass."""
    print("\n" + "=" * 70)
    print("Per-Pattern Accuracy Report")
    print("=" * 70)
    print(f"{'Pattern':<10} {'Est.Total':>10} {'Failures':>10} {'Accuracy':>12} {'Status':<8}")
    print("-" * 70)

    all_pass = True
    for pattern, data in sorted(stats.items()):
        acc = data["accuracy"]
        status = "✅" if acc >= min_accuracy else "❌"
        if acc < min_accuracy:
            all_pass = False
        print(
            f"  {pattern:<8} {data['estimated_total']:>10} {data['failures']:>10} "
            f"  {acc:.1%}     {status}"
        )

    print("=" * 70)

    failing = [(p, d) for p, d in stats.items() if d["accuracy"] < min_accuracy]
    if failing:
        print(f"\n⚠️  {len(failing)} pattern(s) below {min_accuracy:.0%} accuracy:")
        for pattern, data in failing:
            print(f"\n  Pattern {pattern}: {data['accuracy']:.1%} accuracy "
                  f"({data['failures']} failures / ~{data['estimated_total']} total)")
            for ex in data["examples"][:3]:
                print(f"    seed={ex.get('seed','?')} | {ex.get('audit_id','?')}")
                print(f"      Expected: {ex.get('expected','?')}  Got: {ex.get('predicted','?')}")
                print(
                    f"      score={ex.get('score', '?'):.3f}  "
                    f"risk={ex.get('risk','?')}  "
                    f"cost={ex.get('cost','?'):.0f}"
                )
    else:
        print(f"\n✅ All patterns at ≥{min_accuracy:.0%} accuracy")

    return all_pass


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 1

    results_path = args[0]
    min_accuracy = 0.95
    for i, arg in enumerate(args):
        if arg == "--min-accuracy" and i + 1 < len(args):
            try:
                min_accuracy = float(args[i + 1])
            except ValueError:  # ignore non-float --min-accuracy argument; keep default
                _ = None

    try:
        results = load_results(results_path)
    except FileNotFoundError:
        print(f"ERROR: Results file not found: {results_path}")
        return 1
    except json.JSONDecodeError as exc:
        print(f"ERROR: Failed to parse JSON: {exc}")
        return 1

    per_seed_results = results.get("per_seed_results", [])
    if not per_seed_results:
        print("ERROR: No per_seed_results found in JSON")
        return 1

    print(f"Loaded: {results_path}")
    print(f"Seeds: {results.get('seeds', '?')}")
    print(f"Scenarios/seed: {results.get('scenarios_per_seed', '?')}")
    print(f"Label mode: {results.get('label_mode', 'unknown')}")
    print(f"Overall min accuracy: {results.get('min_accuracy', '?'):.1%}")
    print(f"Max k₁: {results.get('max_k1', '?'):.4f}")

    stats = compute_per_pattern_stats(per_seed_results)
    all_pass = print_report(stats, min_accuracy=min_accuracy)
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
