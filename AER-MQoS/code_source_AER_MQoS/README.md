# AER-MQoS — Firmware de reference Contiki-NG

Implementation de reference pour les evaluations Cooja : score multi-criteres (MCS),
fonction objectif RPL experimentale (OCP 8), quatre classes de trafic (C0–C3)
avec ordonnancement WRR, proxies d'energie et de fiabilite, et Q-learning optionnel.

## Modules principaux

| Fichier | Role |
|---------|------|
| `aer_rpl_plus.c` / `.h` | Poids contextuels (γ, α, β) et MCS |
| `rpl-of-aer-plus.c` | Fonction objectif RPL custom |
| `aer_qos_queue.c` | Files UDP par classe + WRR (6:3:2:1) |
| `aer_rpl_energy.c` | Simulation de batterie (NRE) |
| `aer_rpl_trust.c` | Score de confiance depuis l'ETX |
| `aer_rpl_qlearn.c` | Petite table Q pour ajuster γ |
| `AER-MQoS-node.c` | Application UDP de test |
| `aer_campaign_log.c` | Lignes `METRIC,...` pour le parsing |
| `variants/` | Presets Makefile (`RPL_STANDARD`, …) |

## Compilation (Cooja)

```bash
make clean
make TARGET=cooja AER_CONF_CAMPAIGN_METRICS=1
```

Utiliser `simulations/scripts/build_variant.sh` pour les quatre tags de protocole.

## Voir aussi

- `simulations/README_CAMPAIGNS.md` — plan de comparaison
- `simulations/cooja/` — templates de scenarios
- `README.md` a la racine — workflow de reproduction complet
