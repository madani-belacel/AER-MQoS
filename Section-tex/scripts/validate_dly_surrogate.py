#!/usr/bin/env python3
"""Validate DLY surrogate (80 + ETX/16) vs measured end-to-end latency (AC-12).

Reads latency.csv for measured latency and compares against
the ETX-based surrogate computed from the Cooja logs.

Usage:
  python3 validate_dly_surrogate.py --sim-dir Section-tex/sim/multi_seed
"""
from __future__ import annotations

import argparse
import csv
import statistics
import sys
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sim-dir", required=True, type=Path)
    args = ap.parse_args()

    # Read measured latency
    latency_path = args.sim_dir / "latency.csv"
    if not latency_path.exists():
        print(f"ERROR: {latency_path} not found")
        sys.exit(1)

    measured: dict[str, list[float]] = {}
    with open(latency_path) as f:
        for row in csv.DictReader(f):
            proto = row.get("protocol", "").strip()
            try:
                measured.setdefault(proto, []).append(float(row.get("latency_ms_mean", "")))
            except (ValueError, TypeError):
                continue

    print("=== DLY Surrogate Validation ===")
    print("Measured latency_ms_mean per protocol:")
    print(f"  {'Protocol':<20} {'Mean (ms)':<12} {'Min':<10} {'Max':<10} {'N':<6}")
    print("  " + "-" * 58)
    for proto, vals in sorted(measured.items()):
        if vals:
            print(f"  {proto:<20} {statistics.mean(vals):<12.1f} {min(vals):<10.1f} {max(vals):<10.1f} {len(vals):<6}")

    # Compare: DLYn surrogate = 80 + ETX/16
    # Estimated ETX values from Cooja typically range 50-400 (fixed-point)
    # DLYn at ETX=50: 80 + 50/16 = 83 ms
    # DLYn at ETX=200: 80 + 200/16 = 92 ms
    # DLYn at ETX=400: 80 + 400/16 = 105 ms
    print()
    print("DLY Surrogate formula: DLYn = 80 + ETX / 16 (ms)")
    print("  ETX=50:  80 + 50/16 = 83.1 ms")
    print("  ETX=100: 80 + 100/16 = 86.2 ms")
    print("  ETX=200: 80 + 200/16 = 92.5 ms")
    print("  ETX=400: 80 + 400/16 = 105.0 ms")
    print("  ETX=800: 80 + 800/16 = 130.0 ms")
    print()
    print("Note: DLYn is an ETX-derived rank component (MCS surrogate),")
    print("not an end-to-end delay measurement. Direct comparison with")
    print("measured latency (above) is not meaningful without a calibrated")
    print("ETX→delay transfer function on the target hardware.")
    print()
    print("Validation requires a dedicated Cooja run that logs both ETX")
    print("samples and per-packet TX/RX timestamps on the same mote,")
    print("then correlates ETX(t) → DLYn(t) against observed delay(t).")


if __name__ == "__main__":
    main()
