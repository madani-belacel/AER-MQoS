# Dossier `sim/` — CSV attendus après campagnes Cooja

Les noms de fichiers correspondent à `figures_manifest.csv`. Les CSV attendus sont décrits dans **`../sim/README.md`** (gabarit `sim/pdr.csv.template`). Chaque CSV devrait inclure une colonne **`protocol`** (`MRHOF`, `MQOS`, `AER`, `AER_MQOS`) et **`seed`** (entier).

## Colonnes suggérées

- **`pdr.csv`** : `protocol`, `seed`, `pdr_mean`, `pdr_std` (ou PDR par classe : `pdr_c0` … `pdr_c3`).
- **`latency.csv`** : `protocol`, `seed`, `latency_ms_mean`, `latency_ms_p95`.
- **`jitter.csv`** : `protocol`, `class`, `jitter_ms_mean`.
- **`energy.csv`** : `protocol`, `seed`, `duty_cycle_pct` (ou proxy équivalent).
- **`ctrl.csv`** : `protocol`, `time_min`, `dio_dao_per_node_min`.
- **`stab.csv`** : `protocol`, `time_min`, `parent_changes_cumulative`.
- **`sec.csv`** : `scenario`, `protocol`, `pdr_mean` (baseline vs attack).
- **`learn_or_load.csv`** : `load_pct`, `learning_on`, `pdr_mean`, `gamma_mean_x100`.
- **`context.csv`** : `class`, `gamma_x100`, `alpha_x100`, `beta_x100` (pour Fig.~3).

Après remplissage : étendre `generate_figures_matplotlib.py` ou **`plot_from_csv.py`** (esquisse) pour lire ces CSV puis régénérer les PDF sous `Figures/` sans renommer les fichiers.
