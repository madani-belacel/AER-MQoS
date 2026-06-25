# AER-MQoS

**Adaptive Energy-aware Multi-Objective QoS Routing for RPL in Low-Power IoT Networks**

**Version officielle : v1.0**  
[📦 Télécharger la Release](https://github.com/madani-belacel/AER-MQoS/releases/tag/v1.0)

---

## À propos du projet

Ce dépôt contient le **package de reproduction** complet de l'article :

> **AER-MQoS: A Context-Aware Multi-Objective RPL Extension for QoS-Aware, Energy-Aware, and Link-Reliability-Informed Routing in Low-Power IoT Networks**

## Fonctionnalités principales

- Score Multi-Critères adaptatif (MCS) combinant QoS, Énergie et Confiance
- Fonction Objectif RPL personnalisée (OCP 8)
- Ordonnancement WRR par classe de trafic (C0 à C3)
- Modèle d’énergie résiduelle (NRE) avec prédiction
- Mécanisme léger de Q-learning pour l’adaptation contextuelle
- Scripts complets de campagnes Cooja multi-seed

## Structure du dépôt
AER-MQoS/
├── code_source_AER_MQoS/     # Code source Contiki-NG
├── simulations/              # Scénarios Cooja + scripts
├── Section-tex/              # Sources LaTeX + figures
├── scripts/                  # Scripts de build et analyse
├── INSTALL.md                # Instructions de reproduction
├── README.md                 # (ce fichier)
└── LICENSE
text## Comment reproduire les résultats

Consultez le fichier [`INSTALL.md`](INSTALL.md) pour les instructions détaillées :
- Compilation du firmware
- Lancement des campagnes de simulation
- Génération des figures et tableaux
- Analyse statistique

## Citation

```bibtex
@misc{belacel2026aermqos,
  author       = {Belacel, Madani},
  title        = {AER-MQoS v1.0: Replication Package},
  year         = {2026},
  publisher    = {GitHub},
  url          = {https://github.com/madani-belacel/AER-MQoS}
}
Licence
Ce projet est distribué sous licence MIT — voir le fichier LICENSE.
