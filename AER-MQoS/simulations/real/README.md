# Simulations réelles Cooja (AER-MQoS)

Ce répertoire regroupe les **scénarios .csc** utilisés pour l’article (données exclusivement issues de Cooja/Contiki-NG).

## Gabarit 25 nœuds hybride

- Fichier généré : `aer-real-25-hybrid-20260601.csc`
- Générateur : `gen_csc_hybrid25.py` (graine **20260601**, reproductible)
- Topologie : **racine centrale** (mote id 1), **anneau** de voisins proches, **grille partielle** avec jitter, puis **dispersion pseudo-aléatoire** contrôlée (distance minimale entre paires de nœuds)
- Radio : UDGM 55 m / 110 m (aligné sur les campagnes existantes du dépôt)
- **Durée simulée** : non figée dans le XML Cooja classique ; régler **1800–3600 s** dans le plugin *Simulation control* avant lancement (recommandation article)

## Trafic applicatif C0–C3

Le firmware `AER-MQoS-node.c` applique un **profil par `node_id`** (reste % 4) : période d’émission différente et **biais de classe** (répartition non uniforme entre C0…C3), sans valeurs inventées dans les logs : tout est produit par la pile et l’application en simulation.

## Logs METRIC

Compiler depuis `code_source_AER_MQoS/` :

```text
make clean && make AER_CONF_CAMPAIGN_METRICS=1 AER_CAMPAIGN_PROTO_TAG=RPL_STD TARGET=cooja
```

Remplacer `RPL_STD` par l’étiquette de campagne (ex. `MQoS`, `AER`, `AER_MQOS`) selon la variante, puis ouvrir le `.csc` dans Cooja, lancer la simulation et exporter la console / *Log listener* vers `logs/<tag>_seed20260601.txt`.

## Régénérer le .csc

```text
python3 gen_csc_hybrid25.py --out aer-real-25-hybrid-20260601.csc
```

Options : `--seed`, `--nodes` (défaut 25 ; 26–49 possibles pour étendre le même script).
