# AER-MQoS Cooja template

File: **`AER-MQoS-3nodes-template.csc`**.

- **Parameters to adjust manually (or via script)**: `<title>` tag (note `PROTO`, `SEED`, `TOPO`), `<randomseed>`, mote coordinates `<x>`/`<y>`, and optionally `transmitting_range` / `interference_range` for "moderate" vs "stressed" density.
- **`[CONTIKI_DIR]`**: Cooja substitutes this with the Contiki-NG directory used at launch; the source path points to `examples/AER-MQoS/AER-MQoS/code_source_AER_MQoS/AER-MQoS-node.c`.
- **Mote compilation**: the command `$(MAKE) -j$(CPUS) AER-MQoS-node.cooja TARGET=cooja` runs from the parent directory of the source file (`code_source_AER_MQoS`), as in official examples.

**Duplicating** the scenario to other network sizes: in Cooja, "Add motes" with the same type, or copy-paste `<mote>` blocks keeping positions consistent with UDGM range.

For **other protocols** (MRHOF, RPLMQoS-style, AER-RPL-style), the `.csc` must reference **the main `.c` file** and the **`make …cooja` target** of the corresponding project; see `../README_CAMPAIGNS.md`.

## Note on duplication

The actual campaign scenarios (31 files) reside under `AER-MQoS/simulations/real/`. This directory contains only the 3-node template for quick experiments. Both locations use the same `.csc` format; the template is a minimal subset.
