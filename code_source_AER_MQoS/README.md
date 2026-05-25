# AER-MQoS — Contiki-NG reference firmware

Reference implementation for Cooja evaluation: multi-criteria score (MCS), experimental RPL objective function (OCP 8), four traffic classes (C0–C3) with WRR queuing, link-reliability and energy proxies, and optional bounded Q-learning on context weights.

**Release note (May 2026):** this tree was consolidated for the v1.0 replication package together with the measured nine-seed Cooja campaign (`Section-tex/sim/multi_seed/`).

## Main modules

| File | Role |
|------|------|
| `aer_rpl_plus.c` / `.h` | Context weights (γ, α, β) and MCS |
| `rpl-of-aer-plus.c` | Custom RPL objective function |
| `aer_qos_queue.c` | Per-class UDP queues + WRR (4:3:2:1) |
| `aer_rpl_energy.c` | Simulated NRE register |
| `aer_rpl_trust.c` | Link-reliability score from ETX |
| `aer_rpl_qlearn.c` | Small Q-table nudging γ |
| `AER-MQoS-node.c` | UDP test application |
| `aer_campaign_log.c` | `METRIC,...` lines for log parsing |
| `variants/` | Makefile tag presets (`RPL_STANDARD`, …) |

## Build (Cooja)

From this directory (with `CONTIKI` set to your Contiki-NG tree):

```bash
make clean
make TARGET=cooja AER_CONF_CAMPAIGN_METRICS=1 AER_CAMPAIGN_PROTO_TAG=RPL_STD
```

Use `simulations/scripts/build_variant.sh` for the four protocol tags. Enable campaign metrics with `AER_CONF_CAMPAIGN_METRICS=1`.

## Related documentation

- `simulations/README_CAMPAIGNS.md` — four-way comparison plan
- `simulations/cooja/` — scenario templates
- Repository root `INSTALL.md` — full reproduction workflow
