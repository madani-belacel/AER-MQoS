#!/usr/bin/env python3
"""
DEPRECATED — use Section-tex/scripts/parse_cooja_logs.py instead.

This script is a predecessor that produces CSV files with an incompatible
schema (missing channel, success_ratio, and per-column metrics). It writes
to code_source_AER_MQoS/simulations/results/ rather than Section-tex/sim/.

Kept for reference only. The canonical parser is at:
  Section-tex/scripts/parse_cooja_logs.py

Parse Cooja / serial logs containing METRIC,... lines (see simulations/metrics/LOG_FORMAT.md).

Writes CSV files under --out-dir (default: ../results/) for the figure pipeline.
Currently aggregates:
  - pdr.csv  from METRIC,TX and METRIC,RX counts (global ratio, single run).

Extend with METRIC,LATENCY,... etc. when firmware logs them.
"""
