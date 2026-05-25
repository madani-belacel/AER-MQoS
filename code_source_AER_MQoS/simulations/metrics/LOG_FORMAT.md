# Format de log structuré `METRIC,...` (campagnes Cooja)

Objectif : lignes **une par événement**, préfixe commun **`METRIC`**, champs séparés par des **virgules**, faciles à `grep` et à ingérer en CSV (sans espaces superflus dans les champs).

## Préfixe

Toute ligne de métrique commence par :

```text
METRIC,<TYPE>,...
```

## Types définis (AER-MQoS dans ce dépôt)

| TYPE | Champs (ordre) | Description |
|------|----------------|-------------|
| `TX` | `TX,<time_ms>,<node_id2hex>,<app_seq>,<traffic_class>,<payload_len>,<node_id>,<proto_tag>` | Émission UDP applicative (après envoi effectif : file QoS ou direct). |
| `RX` | `RX,<time_ms>,<node_id2hex>,<app_seq>,<payload_len>,<sender_node_id>,<proto_tag>` | Réception ; `app_seq` et `sender_node_id` extraits du payload (`t=… n=…`) même si d’autres champs (`c=`, `p=`, …) sont intercalés. |
| `NRJ` | `NRJ,<time_ms>,<node_id2hex>,<nre_x100>,<pred_x100>,<proto_tag>` | Proxy énergie (NRE + prédiction normalisés 0–100). |
| `CTX` | `CTX,<time_ms>,<node_id2hex>,<class>,<alpha_x100>,<beta_x100>,<gamma_x100>,<proto_tag>` | Poids de contexte au moment de l’émission (classe applicative courante). |

- **`time_ms`** : temps simulé approximatif en millisecondes (`clock_time()`).
- **`node_id2hex`** : deux derniers octets de `linkaddr_node_addr` en hex concaténés (identifiant compact par mote).
- **`traffic_class`** : entier 0–3 aligné sur `aer_traffic_class_t`.
- **`proto_tag`** : chaîne C, par défaut `AER_MQOS` ; surcharger au build avec `make AER_CAMPAIGN_PROTO_TAG=RPL_MRHOF …` si besoin d’homogénéiser les exports multi-dépôts.

## Activation (ce dépôt)

```bash
make clean
make AER_CONF_CAMPAIGN_METRICS=1 AER_CAMPAIGN_PROTO_TAG=AER_MQOS TARGET=cooja
```

Les lignes `METRIC,...` apparaissent sur la sortie série Cooja (onglet **Log** / export simulation). En mode headless, le gabarit Cooja du dépôt enregistre aussi les `METRIC` via `log.append` dans le ScriptRunner (voir `simulations/real/gen_csc_hybrid25.py`).

## Extensions recommandées

- **`METRIC,RADIO`** : duty cycle ou temps radio (si instrumentation `energest` activée).
- **`METRIC,RPL`** : compteurs DIO/DAO agrégés sur fenêtre (via hooks LOG ou compteurs custom).

Le parseur `Section-tex/scripts/parse_cooja_logs.py` agrège `TX`/`RX`/`NRJ`/`CTX` vers les CSV sous `Section-tex/sim/`.
