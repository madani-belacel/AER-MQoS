# AER-MQoS — Adaptive Energy-aware Multi-Objective QoS Routing for RPL

Ce dépôt contient l'implémentation Contiki-NG, les scénarios Cooja et le pipeline d'évaluation reproductible du protocole **AER-MQoS**, présenté dans l'article soumis.

## Fonctionnalités principales
- Score Multi-Critères (MCS) adaptatif selon le contexte (énergie, QoS, fiabilité du lien)
- Fonction objectif RPL personnalisée (OCP 8)
- Files d'attente par classe de trafic (C0–C3) avec ordonnanceur WRR
- Modèle d'énergie résiduelle simulé + prédiction
- Score de confiance basé sur l'ETX
- Option Q-learning léger pour ajuster γ

## Structure
```
AER-MQoS/
├── code_source_AER_MQoS/          # Code firmware Contiki-NG
├── Section-tex/                   # Article + scripts d'analyse + figures
├── simulations/                   # Scénarios Cooja et campagnes
└── README.md
```

## Compilation rapide

```bash
cd code_source_AER_MQoS
make TARGET=cooja AER_CONF_CAMPAIGN_METRICS=1
```

Voir `simulations/README_CAMPAIGNS.md` pour les différentes variantes de protocole.

## Licence

MIT License (voir LICENSE).
