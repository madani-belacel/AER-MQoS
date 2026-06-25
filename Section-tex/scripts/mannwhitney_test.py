#!/usr/bin/env python3
"""Mann-Whitney U tests for AER-MQoS campaign results (AC-15).

Requires N >= 20 seeds per condition.

Usage:
  python3 mannwhitney_test.py --sim-dir Section-tex/sim/multi_seed --out-dir stats
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np
from scipy.stats import mannwhitneyu


def load_metric(csv_path: Path, metric_col: str, protocol_tag: str) -> list[float]:
    vals: list[float] = []
    if not csv_path.exists():
        return vals
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("protocol", "").strip() == protocol_tag:
                try:
                    vals.append(float(row.get(metric_col, "").strip()))
                except (ValueError, TypeError):
                    continue
    return vals


def compare_vs_baseline(sim_dir: Path, baseline_tag: str, target_tags: list[str],
                         metric_col: str, metric_label: str, out_dir: Path) -> None:
    baseline_vals = load_metric(sim_dir / "pdr.csv", metric_col, baseline_tag)
    if len(baseline_vals) < 2:
        print(f"  [skip] {metric_label}: baseline has {len(baseline_vals)} samples")
        return

    results: list[list[str]] = [["protocol", "baseline", "metric", "n_baseline",
                                 "n_target", "U_statistic", "p_value", "significant_005"]]
    for tag in target_tags:
        target_vals = load_metric(sim_dir / "pdr.csv", metric_col, tag)
        if len(target_vals) < 2:
            print(f"  [skip] {tag}: only {len(target_vals)} samples")
            continue
        try:
            u_stat, p_val = mannwhitneyu(baseline_vals, target_vals, alternative="two-sided")
        except ValueError as e:
            print(f"  [error] {tag} vs baseline: {e}")
            continue
        sig = "yes" if p_val < 0.05 else "no"
        results.append([tag, baseline_tag, metric_label,
                        str(len(baseline_vals)), str(len(target_vals)),
                        f"{u_stat:.2f}", f"{p_val:.4f}", sig])
        direction = "higher" if np.median(target_vals) > np.median(baseline_vals) else "lower"
        print(f"  {tag} vs {baseline_tag}: U={u_stat:.1f}, p={p_val:.4f} "
              f"({direction}, n={len(target_vals)}, significant={sig})")

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"mannwhitney_{metric_col.replace('/', '_')}.csv"
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(results)
    print(f"  Wrote {out_path}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sim-dir", required=True, type=Path)
    ap.add_argument("--out-dir", required=True, type=Path)
    args = ap.parse_args()

    baseline = "RPL_STANDARD"
    targets = ["RPL_MQOS", "RPL_AER", "AER_MQOS"]
    metrics = [("pdr_mean", "PDR (%)"), ("pdr_c3", "C3 PDR (%)")]

    print("=== Mann-Whitney U tests ===")
    print(f"Baseline: {baseline}")
    print(f"Targets: {targets}")
    print(f"Directory: {args.sim_dir}")
    print()

    for col, label in metrics:
        print(f"--- {label} ---")
        compare_vs_baseline(args.sim_dir, baseline, targets, col, label, args.out_dir)
        print()

    print("Done.")


if __name__ == "__main__":
    main()
