# Figure generation (Matplotlib)

Main script: `generate_figures_matplotlib.py`  
Post-campaign sketch: `plot_from_csv.py` (complete when `sim/*.csv` exist).

Output: `../Figures/*.pdf` (eleven files, names aligned with `figures_manifest.csv`).

## Dependencies

If `python3-matplotlib` is not installed system-wide, install in a local directory:

```bash
cd /path/to/contiki-ng/examples/AER-MQoS/Section-tex
mkdir -p .pydeps
pip install matplotlib numpy --target=.pydeps --break-system-packages
PYTHONPATH=.pydeps python3 scripts/generate_figures_matplotlib.py
```

Style: white background, black axes, light grey dotted grid, sober palette (close to the `Modele_figure.png` model). Figures 4–11 use measured CSV values from `sim/multi_seed/`.
