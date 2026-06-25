#!/usr/bin/env python3
"""
Future hook: read CSV files under ../sim/ and regenerate Figures/*.pdf.

For now, run ../scripts/generate_figures_matplotlib.py for illustrative plots.
When sim/pdr.csv (etc.) are populated, extend this script to call matplotlib
with measured means/std per protocol.
"""
from pathlib import Path

SIM = Path(__file__).resolve().parent.parent / "sim"


def main():
    pdr = SIM / "pdr.csv"
    if not pdr.exists():
        print("No", pdr, "— fill sim/*.csv after Cooja campaigns, then implement plotting here.")
        return 1
    print("Found", pdr, "— implement parse and call shared plot helpers.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
