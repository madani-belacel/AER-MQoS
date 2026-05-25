# AER-MQoS

Replication package for the manuscript *AER-MQoS: A Context-Aware Multi-Objective RPL Extension for QoS-Aware, Energy-Aware, and Link-Reliability-Informed Routing in Low-Power IoT Networks*.

## Overview

IPv6 RPL is the de facto routing core for many constrained IoT deployments, yet a single rank semantics rarely fits mixed traffic: urgent control flows, bulk telemetry, and long-lived maintenance packets impose different latency and energy pressures. **AER-MQoS** (Adaptive Energy-aware Multi-Objective QoS Routing) unifies class-aware rank shaping, residual-energy and link-reliability proxies, and UDP-edge weighted round-robin scheduling in one Contiki-NG firmware line built on stock `rpl-lite`. The evaluated builds use experimental Objective Code Point 8 and keep trust/energy/QoS terms as **local decision variables**â€”no project-specific DIO/DAO TLVs on the wire.

Release **v1.0** (May 2026) provides the IEEE camera-ready PDF, complete LaTeX sources, reference firmware, Cooja scenarios, parsing scripts, and the **nine-seed** measured campaign (`N = 9`, 1800 s per cell) behind Figures 3â€“11 and the evaluation tables.

## Author

**Madani Belacel**  
Abdelhamid Ibn Badis University of Mostaganem, Mostaganem, Algeria  
E-mail: madani.belacel@univ-mosta.dz  
ORCID: [0009-0003-2928-9565](https://orcid.org/0009-0003-2928-9565)

## How to cite this package

```bibtex
@misc{belacel2026aermqos,
  author       = {Belacel, Madani},
  title        = {{AER-MQoS}: A Context-Aware Multi-Objective {RPL} Extension for {QoS}-Aware, Energy-Aware, and Link-Reliability-Informed Routing in Low-Power {IoT} Networks --- Replication Package v1.0},
  year         = {2026},
  howpublished = {Software and manuscript sources},
  note         = {Abdelhamid Ibn Badis University of Mostaganem, Algeria}
}
```

Prior work on RPLMQoS and RPL-AER appears in `Section-tex/bib/references.bib`.

## Repository layout

| Path | Contents |
|------|----------|
| `main-ieee.pdf` | Camera-ready IEEE two-column manuscript (v1.0) |
| `Section-tex/` | LaTeX sources (`main-ieee.tex`, sections, preamble, `bib/references.bib`) |
| `Section-tex/Figures/` | Figure PDFs (Figs. 1â€“11) |
| `Section-tex/scripts/` | Figure generation and log parsing (`generate_figures_matplotlib.py`, `parse_cooja_logs.py`, â€¦) |
| `Section-tex/sim/multi_seed/` | Measured Cooja CSVs (nine seeds, four firmware tags) |
| `Section-tex/sim/DATA_PROVENANCE.md` | Data lineage for figures and tables |
| `code_source_AER_MQoS/` | Contiki-NG modules (`rpl-of-aer-plus.c`, `aer_rpl_plus.c`, `aer_qos_queue.c`, â€¦) |
| `simulations/` | Cooja `.csc` scenarios and `run_multi_seed_campaign.sh` |
| `INSTALL.md` | Toolchain setup, PDF build, figure and campaign reproduction |
| `LICENSE` | MIT license for this repository snapshot |

## Compile the paper

From `Section-tex/`:

```bash
pdflatex -interaction=nonstopmode main-ieee.tex
bibtex main-ieee
pdflatex -interaction=nonstopmode main-ieee.tex
pdflatex -interaction=nonstopmode main-ieee.tex
```

The root `main-ieee.pdf` is a copy of the output above. See **INSTALL.md** for dependencies and troubleshooting.

## Regenerate figures and replay Cooja

- **Figures 3â€“11:** `python3 scripts/generate_figures_matplotlib.py --from-csv sim/multi_seed` (run inside `Section-tex/`).
- **Full campaigns:** `simulations/real/run_multi_seed_campaign.sh` (JDK 21, Contiki-NG; expect long runtimes).

Committed CSVs under `Section-tex/sim/multi_seed/` match the statistics reported in `main-ieee.pdf`. Record your toolchain versions in `Section-tex/BUILD_NOTES.txt` when refreshing data.

## License

This snapshot is released under the **MIT License** (`LICENSE`). Firmware builds on **Contiki-NG** (BSD-style license). The bundled **IEEEtran** class files follow their own distribution terms.

