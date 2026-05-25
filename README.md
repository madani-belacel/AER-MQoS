# AER-MQoS

**Source Code & Measured Data**

This repository contains the Contiki-NG implementation of the AER-MQoS routing protocol and the measured simulation data used in the associated research paper.

## Repository Content

- `code_source_AER_MQoS/` — Firmware source code (Contiki-NG)
- `simulations/` — Cooja simulation scenarios and scripts
- `sim/` — Measured simulation results (N=9 independent seeds)
- `INSTALL.md` — Setup and reproduction instructions
- `NAMING.md` — Explanation of file naming convention

## License

This project is released under the **MIT License**.

---

### 2. Vérification détaillée des dossiers uploadés

D’après ce que je vois sur ton repository, voici l’état actuel :

**Bien présents :**
- `code_source_AER_MQoS/` → OK (contient les fichiers .c, .h, Makefile…)
- `sim/` → OK (contient `multi_seed/`, `DATA_PROVENANCE.md`, etc.)
- `simulations/` → OK (contient `real/`, scénarios Cooja…)
- `INSTALL.md`
- `NAMING.md`
- `LICENSE`

**Points à améliorer :**
- Il y a encore des doublons (ex: `sim/multi_seed/` et `code_source_AER_MQoS/simulations/...`)
- Le README n’est pas encore mis à jour avec la nouvelle version ci-dessus.

**Recommandation :**  
Après avoir mis le nouveau README, tu peux supprimer les dossiers redondants si tu veux (ex: garder uniquement `sim/` pour les données).

---

### 3. Version finale de `INSTALL.md`

```markdown
# INSTALL.md - AER-MQoS

## Installation and Reproduction Guide

### 1. Prerequisites

- Linux (Ubuntu recommended)
- Contiki-NG
- Cooja simulator
- Python 3
- JDK 21 (for Cooja)
- LaTeX distribution (pdflatex + bibtex)

### 2. Compile the Firmware

```bash
cd code_source_AER_MQoS
make TARGET=cooja
3. Run the Simulations (N=9 seeds)
Bashcd simulations/real
./run_multi_seed_campaign.sh
4. Generate Figures
Bashcd ../../sim  # or Section-tex if you have it
python3 scripts/generate_figures_matplotlib.py --from-csv multi_seed
5. Reproduce the Paper (optional)
Bashcd Section-tex
pdflatex main-ieee.tex
bibtex main-ieee
pdflatex main-ieee.tex
pdflatex main-ieee.tex
Note
Some source files still use legacy names (aer_rpl_plus*). See NAMING.md for details.
