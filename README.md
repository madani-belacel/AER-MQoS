# AER-MQoS — Adaptive Energy-aware Multi-Objective QoS Routing for RPL

**Replication package** pour l'article soumis :

> **AER-MQoS: A Context-Aware Multi-Objective RPL Extension for QoS-Aware, Energy-Aware, and Link-Reliability-Informed Routing in Low-Power IoT Networks**

## Version Officielle
**v1.0** — [Voir la Release](https://github.com/madani-belacel/AER-MQoS/releases/tag/v1.0)

## Contenu du dépôt
- Code source complet Contiki-NG (firmware AER-MQoS)
- Scénarios Cooja et scripts de campagnes multi-seed
- Sources LaTeX de l’article + figures
- Données mesurées (N=4 seeds)
- Pipeline complet de reproduction (parsing → figures)

## Fonctionnalités principales
- Score Multi-Critères (MCS) adaptatif (contexte γ, α, β)
- Fonction Objectif RPL expérimentale (OCP 8)
- Files d’attente par classe (C0–C3) avec ordonnanceur WRR
- Modèle d’énergie résiduelle simulé + prédiction
- Score de confiance basé sur l’ETX
- Q-learning léger (optionnel)

## Installation & Reproduction
Voir le fichier [`INSTALL.md`](INSTALL.md) pour :
- Compiler le firmware
- Lancer les campagnes Cooja
- Régénérer les figures
- Reproduire les résultats

## Citation
```bibtex
@misc{belacel2026aermqos,
  author       = {Belacel, Madani},
  title        = {{AER-MQoS} v1.0 --- Replication Package},
  year         = {2026},
  howpublished = {GitHub},
  url          = {https://github.com/madani-belacel/AER-MQoS}
}

Licence
MIT License — voir LICENSE
