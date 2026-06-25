# Campaign scripts (outline)

## `build_variant.sh`

Minimal shell script: prints **recommended** commands for each variant. Run without arguments to list the four profiles; with a profile, it prints the `cd` and `make` commands.

**MRHOF**, **RPLMQoS-style** and **AER-RPL-style** variants use different Makefiles than this repository — they point to other example directories. Only **AER-MQoS** compiles natively here.

Usage:

```bash
cd /path/to/code_source_AER_MQoS/simulations/scripts
chmod +x build_variant.sh   # once
./build_variant.sh
./build_variant.sh aer_mqos
```

## Cooja log export

After a simulation: **Simulation log** → save as `.log`; then:

```bash
grep '^METRIC,' run_001.log > metrics_run_001.csv
```

Or Python pipeline (to be completed): aggregate `METRIC,TX` / `METRIC,RX` by `(proto_tag, traffic_class, seed)` to produce the CSVs expected by `Section-tex/figures_manifest.csv`.

## Note

The canonical parser is `Section-tex/scripts/parse_cooja_logs.py`. The predecessor `parse_cooja_metrics.py` in this directory is **deprecated** and produces an incompatible CSV schema.
