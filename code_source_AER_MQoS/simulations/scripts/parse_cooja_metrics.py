#!/usr/bin/env python3
"""
Parse Cooja / serial logs containing METRIC,... lines (see simulations/metrics/LOG_FORMAT.md).

Writes CSV files under --out-dir (default: ../results/) for the figure pipeline.
Currently aggregates:
  - pdr.csv  from METRIC,TX and METRIC,RX counts (global ratio, single run).

Extend with METRIC,LATENCY,... etc. when firmware logs them.
"""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


def parse_log(path: Path):
    tx = 0
    rx = 0
    tx_by_class: dict[int, int] = defaultdict(int)
    with path.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            if not line.startswith("METRIC,"):
                continue
            parts = line.strip().split(",")
            if len(parts) < 2:
                continue
            kind = parts[1]
            if kind == "TX" and len(parts) >= 7:
                try:
                    cls = int(parts[5])
                    tx_by_class[cls] += 1
                except ValueError:
                    pass
                tx += 1
            elif kind == "RX":
                rx += 1
    return tx, rx, tx_by_class


def write_pdr(out_dir: Path, protocol: str, seed: int, tx: int, rx: int):
    out_dir.mkdir(parents=True, exist_ok=True)
    pdr = 100.0 * rx / tx if tx > 0 else 0.0
    row = {"protocol": protocol, "seed": seed, "pdr_mean": round(pdr, 4), "pdr_std": 0.0}
    p = out_dir / "pdr.csv"
    append = p.exists()
    with p.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(row.keys()))
        if not append:
            w.writeheader()
        w.writerow(row)


def write_headers_only(out_dir: Path):
    """Create empty CSV shells so downstream tools see expected columns."""
    out_dir.mkdir(parents=True, exist_ok=True)
    specs = {
        "latency.csv": ["protocol", "seed", "latency_ms_mean", "latency_ms_p95"],
        "jitter.csv": ["protocol", "seed", "class", "jitter_ms_mean"],
        "energy.csv": ["protocol", "seed", "duty_cycle_pct"],
        "ctrl.csv": ["protocol", "seed", "time_min", "dio_dao_per_node_min"],
        "stab.csv": ["protocol", "seed", "time_min", "parent_changes_cumulative"],
        "sec.csv": ["scenario", "protocol", "pdr_mean"],
        "learn_or_load.csv": ["load_pct", "learning_on", "pdr_mean", "gamma_mean_x100"],
        "context.csv": ["class", "gamma_x100", "alpha_x100", "beta_x100"],
    }
    for name, fields in specs.items():
        p = out_dir / name
        if p.exists():
            continue
        with p.open("w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=fields).writeheader()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="in_path", type=Path, required=True, help="Cooja log export (text)")
    ap.add_argument(
        "--protocol",
        required=True,
        help="e.g. AER_MQOS, MRHOF, ... (older log spellings are normalized upstream)",
    )
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out-dir", type=Path, default=Path(__file__).resolve().parent.parent / "results")
    args = ap.parse_args()

    tx, rx, _by = parse_log(args.in_path)
    write_headers_only(args.out_dir)
    write_pdr(args.out_dir, args.protocol, args.seed, tx, rx)
    print(f"Parsed {args.in_path}: TX={tx} RX={rx} -> {args.out_dir / 'pdr.csv'}")


if __name__ == "__main__":
    main()
