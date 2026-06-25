# AER-MQoS

**Adaptive Energy-aware Multi-Objective QoS Routing for RPL in Low-Power IoT Networks**

**Official Release: v1.0**  
[📦 Download Release v1.0](https://github.com/madani-belacel/AER-MQoS/releases/tag/v1.0)

---

## About the Project

This repository contains the **full replication package** for the paper:

> **AER-MQoS: A Context-Aware Multi-Objective RPL Extension for QoS-Aware, Energy-Aware, and Link-Reliability-Informed Routing in Low-Power IoT Networks**

## Key Features

- Adaptive Multi-Criteria Score (MCS) combining QoS, Energy, and Trust
- Custom RPL Objective Function (OCP 8)
- Per-traffic-class Weighted Round Robin (WRR) queuing (C0–C3)
- Residual Energy (NRE) model with moving-average prediction
- Lightweight Q-learning for context adaptation
- Complete Cooja simulation campaigns (multi-seed)

## Repository Structure
AER-MQoS/
├── code_source_AER_MQoS/     # Contiki-NG firmware source
├── simulations/              # Cooja scenarios and campaign scripts
├── Section-tex/              # LaTeX sources and figures
├── scripts/                  # Build and analysis scripts
├── INSTALL.md                # Full reproduction instructions
├── README.md                 # (this file)
└── LICENSE
text## How to Reproduce

Please refer to [`INSTALL.md`](INSTALL.md) for detailed instructions:
- Firmware compilation
- Running multi-seed Cooja campaigns
- Generating figures and tables
- Statistical analysis

## Citation

```bibtex
@misc{belacel2026aermqos,
  author       = {Belacel, Madani},
  title        = {AER-MQoS v1.0: Replication Package},
  year         = {2026},
  publisher    = {GitHub},
  url          = {https://github.com/madani-belacel/AER-MQoS}
}
License
This project is licensed under the MIT License — see the LICENSE file for details.
