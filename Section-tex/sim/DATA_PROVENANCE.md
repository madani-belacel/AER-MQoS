# Data Provenance — AER-MQoS

## Measured Campaign

| Attribute | Value |
|-----------|-------|
| Seeds | `20260601`, `20260602`, `20260603`, `20260604` |
| Firmware tags | `RPL_STANDARD`, `RPL_MQOS`, `RPL_AER`, `AER_MQOS` |
| Topology | 25 nodes, hybrid grid + random placement |
| Radio | UDGM lossy (`success_ratio_tx = 0.85`, `success_ratio_rx = 0.85`) |
| Duration | 1800 s simulated per run |
| Simulator | Cooja (Contiki-NG), headless via Gradle |
| Parser | `Section-tex/scripts/parse_cooja_logs.py` → CSV per metric |

## Excluded Seeds

| Seed | Reason |
|------|--------|
| `20260512` | Parsing artefact: duplicate logs across all protocols |
| `20260605` | PDR > 100% (malformed METRIC,RX entries) |
| `20260606` | PDR > 100% (malformed METRIC,RX entries) |

## Output CSVs (under `Section-tex/sim/multi_seed/`)

Only lossy UDGM (`sr=0.85`) CSVs are committed. To reproduce lossless (`sr=1.0`) runs, set `CHANNELS=lossless` in `run_multi_seed_campaign.sh`.

- `pdr.csv` — per-seed PDR (global + per-class C0–C3)
- `latency.csv` — mean and P95 latency
- `jitter.csv` — inter-arrival jitter per class
- `energy.csv` — NRE duty-cycle proxy
- `ctrl.csv` — DIO/DAO rates (binned)
- `stab.csv` — parent change cumulative proxy
- `sec.csv` — PDR per epoch (first/second half)
- `context.csv` — alpha/beta MCS weights per class
- `learn_or_load.csv` — PDR per traffic load quartile
