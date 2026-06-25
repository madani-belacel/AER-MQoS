# Cooja campaigns — four protocols (paper methodology)

This document defines a **concrete plan** for comparing **RPL-MRHOF**, **RPL-MQoS-style**, **RPL-AER-style** and **AER-MQoS** under Cooja, with CSV exports feeding the eleven PDF figures of the manuscript.

## Fairness principle

- **Same** radio model (UDGM), **same** `transmitting_range` / `interference_range`, **same** mote placement (or grid generated with the same seed), **same** simulation duration and **same** application traffic types (UDP, similar sizes, identical periods) where possible.
- **Seeds** `<randomseed>` are distinct for statistical reproducibility; record `seed` in each exported `.log` filename.
- Each campaign is identified by a logical **triplet**: `(variant, topology_id, seed)`.

## Where to compile what

| Variant | Source directory (under `examples/AER-MQoS/`) | Notes |
|----------|------------------------------------------------|-------|
| **RPL-MRHOF** | `autres/rpl-udp/` (`udp-server.c`, `udp-client.c`) — requires sibling repo | Baseline RPL + MRHOF without AER/MQoS extensions. |
| **RPL-MQoS-style** | sibling repo `RPLMQoS_BELACEL/` | Per-class composite metric; **fork** with extended `rpl_parent_t` (delay, jitter, queue) — not drop-in on stock `rpl-lite`. |
| **RPL-AER-style** | sibling repo `RPL-AER-main/` | Floating-point MCS, multi-component trust, LSTM/harvest in **stub**; WRR queues not identical to AER-MQoS. |
| **AER-MQoS** | `AER-MQoS/code_source_AER_MQoS/` | Integer MCS, OCP 8, ETX trust, NRE + lightweight prediction, Q-learning on $\gamma$, **application-layer WRR**. |

The `scripts/build_variant.sh` script recalls typical `make` commands for each profile (paths overridable via `CONTIKI`, `BELACEL`, `AER_MAIN`, `RPL_UDP` environment variables).

## `.csc` template

- **Grid + jitter campaign (25–49 nodes)**: generate with  
  `simulations/scripts/generate_campaign_csc.py --nodes 30 --out cooja/aer-campaign-grid-30.csc`  
  (example already produced: `cooja/aer-campaign-grid-30.csc`). Simulated duration (1800–3600 s) is set in Cooja after opening the `.csc`.
- **Short reference file** for **AER-MQoS**: `cooja/AER-MQoS-3nodes-template.csc` (three motes, single firmware type).
- For **other variants**: duplicate the campaign `.csc` in Cooja, then replace **`<source>`** and **`<commands>`** of the `motetype` block with those of the target project (as in `autres/rpl-udp/rpl-udp-cooja.csc`).
- Name the exported file as: `log_<VARIANT>_<TOPO>_<SEED>.log`.

## Structured `METRIC,...` logs

See `metrics/LOG_FORMAT.md`. For AER-MQoS, enable at build:

```bash
make AER_CONF_CAMPAIGN_METRICS=1 AER_CAMPAIGN_PROTO_TAG=AER_MQOS TARGET=cooja
```

For **other repositories**, add equivalent `printf` calls (`METRIC,TX,...` / `METRIC,RX,...`) in their `udp-client.c` / sink to produce the **same column schema** on the parser side.

## Data → figures pipeline

1. Export Cooja logs per run.
2. `grep '^METRIC,'` → intermediate files per run (optional).
3. **`Section-tex/scripts/parse_cooja_logs.py`**: canonical parser (writes to `Section-tex/sim/`). The predecessor in `simulations/scripts/parse_cooja_metrics.py` is **deprecated**.
4. Generate PDFs: `python3 Section-tex/scripts/generate_figures_matplotlib.py` (figures 4–11 only if CSVs contain data; no fictive values). Schematics only: `--schematics-only` (Fig. 1–2).

## Assumed limitations

The four stacks are **not** a single binary with flags: the comparison remains **methodologically** controlled (Cooja, same topology, same load), with **honest distinction** in the paper between "MQoS-style" behaviour (BELACEL repository) and AER-MQoS (WRR + unified MCS on current Contiki-NG tree).
