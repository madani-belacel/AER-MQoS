# Campagnes Cooja — quatre protocoles (méthodo article)

Ce document fixe un **plan concret** pour comparer **RPL-MRHOF**, **RPL-MQoS-style**, **RPL-AER-style** et **AER-MQoS** sous Cooja, avec export vers CSV puis les onze figures PDF du manuscrit.

## Principe d’équité

- **Même** modèle radio (UDGM), **mêmes** portées `transmitting_range` / `interference_range`, **même** placement des motes (ou grille générée avec la même graine), **même** durée de simulation et **mêmes** types de trafic applicatif (UDP, tailles proches, périodes identiques) dans la mesure du possible.
- **Graines** `<randomseed>` distinctes pour la répétabilité statistique ; noter `seed` dans le nom du fichier `.log` exporté.
- Chaque campagne est identifiée par un **triplet** logique : `(variante, topologie_id, seed)`.

## Où compiler quoi

| Variante | Répertoire source (sous `examples/projet_madani/` ou `autres/`) | Remarque |
|----------|-------------------------------------------------------------------|----------|
| **RPL-MRHOF** | `autres/rpl-udp/` (`udp-server.c`, `udp-client.c`) | Baseline RPL + MRHOF sans extensions AER/MQoS. |
| **RPL-MQoS-style** | `RPLMQoS_BELACEL/` | Métrique composite par classe ; **fork** avec `rpl_parent_t` étendu (délai, gigue, file) — pas drop-in sur `rpl-lite` stock. |
| **RPL-AER-style** | `RPL-AER-main/` | MCS flottant, confiance multi-composantes, LSTM/harvest en **stub** selon fichiers ; pas de files WRR identiques à AER-MQoS. |
| **AER-MQoS** | `AER-MQoS/code_source_AER_MQoS/` | MCS entier, OCP 8, confiance ETX, NRE + prédiction légère, Q-learning sur $\gamma$, **WRR applicatif**. |

Le script `scripts/build_variant.sh` rappelle les commandes `make` typiques pour chaque profil (chemins surchargés par variables d’environnement `CONTIKI`, `BELACEL`, `AER_MAIN`, `RPL_UDP` si besoin).

## Gabarit `.csc`

- **Campagne grille + jitter (25–49 nœuds)** : générer avec  
  `simulations/scripts/generate_campaign_csc.py --nodes 30 --out cooja/aer-campaign-grid-30.csc`  
  (exemple déjà produit : `cooja/aer-campaign-grid-30.csc`). La durée simulée (1800–3600 s) se règle dans Cooja après ouverture du `.csc`.
- Fichier de référence **court** pour **AER-MQoS** : `cooja/AER-MQoS-3nodes-template.csc` (trois motes, un seul type firmware).
- Pour les **autres variantes** : dupliquer le `.csc` de campagne dans Cooja, puis remplacer **`<source>`** et **`<commands>`** du `motetype` par ceux du projet cible (comme dans `autres/rpl-udp/rpl-udp-cooja.csc`).
- Renommer le fichier exporté du style : `log_<VARIANT>_<TOPO>_<SEED>.log`.

## Logs structurés `METRIC,...`

Voir `metrics/LOG_FORMAT.md`. Pour AER-MQoS, activer au build :

```bash
make AER_CONF_CAMPAIGN_METRICS=1 AER_CAMPAIGN_PROTO_TAG=AER_MQOS TARGET=cooja
```

Pour les **autres dépôts**, ajouter des `printf` équivalents (`METRIC,TX,...` / `METRIC,RX,...`) dans leurs `udp-client.c` / sink afin d’obtenir le **même schéma de colonnes** côté parseur.

## Pipeline données → figures

1. Exporter les logs Cooja par run.
2. `grep '^METRIC,'` → fichiers intermédiaires par run (optionnel).
3. **`simulations/scripts/parse_cooja_metrics.py`** : agrège au minimum `METRIC,TX` / `METRIC,RX` vers `simulations/results/pdr.csv` (puis copier ou fusionner vers `Section-tex/sim/pdr.csv` pour les figures). Étendre le firmware avec d’autres lignes `METRIC,...` pour remplir `latency.csv`, `jitter.csv`, etc.
4. Écrire ou compléter les CSV attendus par `Section-tex/scripts/generate_figures_matplotlib.py` sous `Section-tex/sim/` (voir en-têtes dans `parse_cooja_metrics.py` pour les colonnes).
5. Générer les PDF : `python3 Section-tex/scripts/generate_figures_matplotlib.py` (figures 4–11 uniquement si les CSV contiennent des données ; pas de valeurs fictives). Schémas seuls : `--schematics-only` (Fig. 1–2).

## Limitations assumées

Les quatre piles ne sont **pas** un seul binaire à flags : la comparaison reste **méthodologiquement** contrôlée (Cooja, même topologie, même charge), avec **distinction honnête** dans l’article entre comportement « style MQoS » (dépôt BELACEL) et AER-MQoS (fichiers WRR + MCS unifié sur Contiki-NG courant).
