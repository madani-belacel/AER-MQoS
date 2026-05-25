# Smoke test report (2026-05-15)

**Command:** `NUM_SEEDS=3 LOSSY_RATIO=0.85 SIM_TIMEOUT_MS=90000 ./run_multi_seed_campaign.sh`

| Item | Result |
|------|--------|
| Duration | ~7 min |
| Batches launched | 8 (4 seeds × 2 channels) |
| Cooja failures | 0 |
| Bug found | `LOGDIR` export ignored by `run_campaigns.sh` → **fixed** (`LOGDIR="${LOGDIR:-...}"`) |
| Parse in `multi_seed/` | 0 rows (logs in `simulations/real/logs/` instead) |
| METRIC,TX per 90 s run | ~33–43 packets (vs 1325 @ 1800 s) |
| Protocol separation | None at 90 s |

**Conclusion:** automation and Cooja headless path are valid. Manuscript statistics use `../multi_seed/` ($N{=}20$, hybrid anchor + calibrated model) until `SIM_TIMEOUT_MS=1800000` full campaign completes.
