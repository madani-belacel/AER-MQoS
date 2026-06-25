#!/usr/bin/env python3
"""
Aggregates multi-seed CSVs (Section-tex/sim/multi_seed/):
mean ± std, 95% CI (Student t), pairwise significance tests.

Usage:
  python3 analyze_multi_seed_stats.py --sim-dir ../sim/multi_seed --out-dir ../sim/multi_seed/stats
"""
from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path

try:
    from scipy import stats as scipy_stats
except ImportError:
    scipy_stats = None


METRICS = [
    ("pdr.csv", "pdr_mean", "PDR (%)"),
    ("latency.csv", "latency_ms_mean", "Latency mean (ms)"),
    ("latency.csv", "latency_ms_p95", "Latency p95 (ms)"),
    ("energy.csv", "nre_proxy_pct", "NRE proxy"),
]

CLASS_PDR_SUFFIXES = [f"pdr_c{i}" for i in range(4)]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def ci95_t(values: list[float]) -> tuple[float, float, float]:
    """Return (mean, std, half-width of 95% CI)."""
    n = len(values)
    if n == 0:
        return float("nan"), float("nan"), float("nan")
    mean = sum(values) / n
    if n == 1:
        return mean, 0.0, 0.0
    var = sum((x - mean) ** 2 for x in values) / (n - 1)
    std = math.sqrt(var)
    if scipy_stats is not None:
        hw = scipy_stats.t.ppf(0.975, n - 1) * std / math.sqrt(n)
    else:
        hw = 1.96 * std / math.sqrt(n)  # fallback normal approx
    return mean, std, hw


def _mann_whitney_p_pure(a: list[float], b: list[float]) -> float | None:
    """Normal-approximation Mann--Whitney U (two-sided); used when scipy is absent."""
    if len(a) < 2 or len(b) < 2:
        return None
    tagged = [(v, 0) for v in a] + [(v, 1) for v in b]
    tagged.sort(key=lambda t: t[0])
    vals = [t[0] for t in tagged]
    groups = [t[1] for t in tagged]
    n1, n2 = len(a), len(b)
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    ranks = [0.0] * len(vals)
    i = 0
    while i < len(vals):
        j = i
        while j < len(vals) and vals[order[j]] == vals[order[i]]:
            j += 1
        avg = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[order[k]] = avg
        i = j
    r1 = sum(ranks[i] for i, g in enumerate(groups) if g == 0)
    u1 = r1 - n1 * (n1 + 1) / 2.0
    u = min(u1, n1 * n2 - u1)
    mu = n1 * n2 / 2.0
    sigma = math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12.0)
    if sigma == 0:
        return None
    z = (u - mu) / sigma
    return 2.0 * (1.0 - 0.5 * (1.0 + math.erf(abs(z) / math.sqrt(2.0))))


def mann_whitney_p(a: list[float], b: list[float]) -> float | None:
    if len(a) < 2 or len(b) < 2:
        return None
    if scipy_stats is not None:
        try:
            _, p = scipy_stats.mannwhitneyu(a, b, alternative="two-sided")
            return float(p)
        except ValueError:
            return None
    return _mann_whitney_p_pure(a, b)


def aggregate_metric(
    rows: list[dict[str, str]],
    value_key: str,
    group_keys: tuple[str, ...] = ("channel", "protocol"),
) -> dict[tuple, list[float]]:
    buckets: dict[tuple, list[float]] = defaultdict(list)
    for row in rows:
        try:
            val = float(row.get(value_key, "") or "")
        except ValueError:
            continue
        key = tuple(row.get(k, "") for k in group_keys)
        buckets[key].append(val)
    return buckets


def write_summary_table(out_path: Path, summaries: list[dict]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if not summaries:
        return
    fields = list(summaries[0].keys())
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(summaries)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sim-dir", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, default=None)
    ap.add_argument(
        "--reference",
        default="RPL_STANDARD",
        help="Baseline protocol for pairwise significance vs others",
    )
    args = ap.parse_args()
    sim_dir = args.sim_dir
    out_dir = args.out_dir or (sim_dir / "stats")
    out_dir.mkdir(parents=True, exist_ok=True)

    summaries: list[dict] = []
    pdr_rows = read_csv(sim_dir / "pdr.csv")

    for csv_name, col, label in METRICS:
        rows = read_csv(sim_dir / csv_name)
        buckets = aggregate_metric(rows, col)
        for (channel, protocol), vals in sorted(buckets.items()):
            mean, std, ci_hw = ci95_t(vals)
            summaries.append(
                {
                    "metric": label,
                    "column": col,
                    "channel": channel,
                    "protocol": protocol,
                    "n": len(vals),
                    "mean": round(mean, 4),
                    "std": round(std, 4),
                    "ci95_half_width": round(ci_hw, 4),
                    "mean_minus_ci": round(mean - ci_hw, 4),
                    "mean_plus_ci": round(mean + ci_hw, 4),
                }
            )

    for c in CLASS_PDR_SUFFIXES:
        buckets = aggregate_metric(pdr_rows, c)
        for (channel, protocol), vals in sorted(buckets.items()):
            if not vals:
                continue
            mean, std, ci_hw = ci95_t(vals)
            summaries.append(
                {
                    "metric": f"PDR class {c}",
                    "column": c,
                    "channel": channel,
                    "protocol": protocol,
                    "n": len(vals),
                    "mean": round(mean, 4),
                    "std": round(std, 4),
                    "ci95_half_width": round(ci_hw, 4),
                    "mean_minus_ci": round(mean - ci_hw, 4),
                    "mean_plus_ci": round(mean + ci_hw, 4),
                }
            )

    write_summary_table(out_dir / "summary_table.csv", summaries)

    # Pairwise vs reference (Mann-Whitney) on global PDR per channel
    ref = args.reference
    sig_rows: list[dict] = []
    by_ch_proto: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in pdr_rows:
        ch = row.get("channel", "lossless")
        proto = row.get("protocol", "")
        try:
            by_ch_proto[(ch, proto)].append(float(row.get("pdr_mean", "") or 0))
        except ValueError:
            continue
    for ch in sorted({k[0] for k in by_ch_proto}):
        ref_vals = by_ch_proto.get((ch, ref), [])
        if len(ref_vals) < 2:
            continue
        for proto in sorted({k[1] for k in by_ch_proto if k[0] == ch}):
            if proto == ref:
                continue
            other = by_ch_proto.get((ch, proto), [])
            p = mann_whitney_p(ref_vals, other)
            sig_rows.append(
                {
                    "channel": ch,
                    "reference": ref,
                    "protocol": proto,
                    "n_ref": len(ref_vals),
                    "n_other": len(other),
                    "mann_whitney_p": "" if p is None else round(p, 6),
                    "significant_0.05": "" if p is None else ("yes" if p < 0.05 else "no"),
                }
            )
    write_summary_table(out_dir / "significance_vs_reference.csv", sig_rows)

    print(f"Wrote {out_dir / 'summary_table.csv'} ({len(summaries)} rows)")
    print(f"Wrote {out_dir / 'significance_vs_reference.csv'} ({len(sig_rows)} pairwise tests)")
    if scipy_stats is None:
        print("Note: scipy not installed; used pure-Python Mann-Whitney and Student-t CI fallback")


if __name__ == "__main__":
    main()
