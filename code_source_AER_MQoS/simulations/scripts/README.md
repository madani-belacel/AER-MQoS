# Scripts de campagne (esquisse)

## `build_variant.sh`

Script shell minimal : affiche les commandes **recommandées** pour chaque variante. L’exécuter sans argument liste les quatre profils ; avec un profil, il imprime le `cd` et le `make` correspondant.

Les variantes **MRHOF**, **RPLMQoS-style** et **AER-RPL-style** ne partagent pas toutes le même `Makefile` que ce dépôt : elles pointent vers d’autres répertoires d’exemple sous `examples/projet_madani/`. Seule **AER-MQoS** se compile nativement ici.

Usage :

```bash
cd /path/to/code_source_AER_MQoS/simulations/scripts
chmod +x build_variant.sh   # une fois
./build_variant.sh
./build_variant.sh aer_mqos
```

## Export des logs Cooja

Après une simulation : **Simulation log** → sauvegarder en `.log` ; puis :

```bash
grep '^METRIC,' run_001.log > metrics_run_001.csv
```

Ou pipeline Python (à compléter) : agréger `METRIC,TX` / `METRIC,RX` par `(proto_tag, traffic_class, seed)` pour produire les CSV attendus par `Section-tex/figures_manifest.csv`.
