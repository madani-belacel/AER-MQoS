# INSTALL.md

## AER-MQoS - Installation and Reproduction Guide

This document explains how to compile the firmware, run the simulations, and reproduce the figures.

### 1. Prerequisites

- Ubuntu / Linux (recommended)
- Contiki-NG (latest stable version)
- Cooja simulator (included in Contiki-NG)
- Python 3.8+
- JDK 21 (required for Cooja)
- LaTeX (Tex Live or MiKTeX) with `pdflatex` and `bibtex`

### 2. Firmware Compilation

```bash
cd code_source_AER_MQoS
make TARGET=cooja AER_PROTOCOL_VARIANT=RPL_STANDARD
make TARGET=cooja AER_PROTOCOL_VARIANT=RPL_MQoS
make TARGET=cooja AER_PROTOCOL_VARIANT=RPL_AER
make TARGET=cooja AER_PROTOCOL_VARIANT=AER_MQOS
```

### 3. Run Simulations (Measured Campaign)

```bash
cd simulations/real
./run_multi_seed_campaign.sh
```

This will run the 9 seeds used in the paper (SIM_TIMEOUT_MS=1800000).

### 4. Generate Figures

```bash
cd ../Section-tex
python3 scripts/generate_figures_matplotlib.py --from-csv sim/multi_seed
```

### 5. Compile the Paper (LaTeX)

```bash
cd Section-tex
pdflatex main-ieee.tex
bibtex main-ieee
pdflatex main-ieee.tex
pdflatex main-ieee.tex
```

### 6. Repository Structure Summary

- `code_source_AER_MQoS/` → Firmware source code
- `simulations/` → Cooja scenarios and campaign scripts
- `sim/multi_seed/` → Measured simulation results (N=9)
- `Section-tex/` → LaTeX sources (optional for reproduction)

### Note

The naming of some source files still uses legacy names (`aer_rpl_plus*`). See `NAMING.md` for details.

---
