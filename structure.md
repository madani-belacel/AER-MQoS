# Abstract

This paper presents AER-MQoS, a context-aware multi-objective extension of RPL for low-power IoT networks. The protocol unifies QoS differentiation, energy awareness, and link-reliability-informed routing through a Multi-Criteria Score (MCS) driven by a context coefficient gamma balancing QoS (alpha) and energy (beta) weights. Weighted round-robin queues provide class-based scheduling at the UDP layer. A bounded Q-learning nudge on gamma is specified for future ablation. The implementation on Contiki-NG is evaluated through reproducible Cooja simulations (N=4 seeds, 1800 s, 25-node topology) across four firmware variants. All variants achieve >93% PDR under lossy UDGM (success_ratio=0.85); per-class PDR on seed 20260603 provides preliminary evidence of traffic-class differentiation (AER-MQoS C3 =95.96% vs C0 =79.52%), alongside episodic sensitivity that motivates larger-scale campaigns. Contributions include: the (alpha,beta,gamma) contextual model, the MCS with MRHOF-compatible hysteresis, application-layer WRR queuing, and an open-source implementation with reproducible CSV-to-figure provenance.

# Index Terms

RPL, IoT, low-power networks, QoS, energy-aware routing, link-reliability routing, network simulation.

# I. Introduction

*Article organization* (unnumbered)

# II. Related Work

- A. RPL foundations and objective functions
- B. Traffic differentiation and composite routing metrics
- C. Energy-aware routing and harvesting context
- D. Trust, anomalies, and internal threats
- E. Simulation methodology
- F. Comparative positioning
- G. Positioning of AER-MQoS

## Table I -- Positioning vs. representative RPL extensions (2023--2025 publication dates). "On-wire" = custom DIO/DAO TLVs in evaluated artifacts.

# III. Architecture of AER-MQoS

*(Notation table appears here in the flow)*

## Table II -- Principal notation.

## Figure 1 -- Conceptual schematic---not simulation output. Reference architecture of AER-MQoS: QoS plane, trust/energy context plane, MCS, and experimental OCP 8 objective function. Module boundaries match the Cooja firmware tree.

- A. Design principles
- B. Functional planes on each node
- C. Path levels and traffic-class mapping

## Figure 2 -- Conceptual schematic---not simulation output. Illustrative RPL DODAG (not the 25-node Cooja layout): DIO (down), DAO (up), preferred parent path to the sink/LBR. Class-to-level mapping C3->1, ..., C0->4.

- D. Context fusion and the (alpha,beta,gamma) model

## Figure 3 -- Context coefficient gamma (and derived weights alpha=gamma, beta=100-gamma in hundredths) per traffic class C0--C3 for AER-MQoS from context.csv (measured Cooja campaign). The two curves are mirror images since alpha+beta=1. This figure shares data with Table VII and is provided as a complementary visual reference.

- E. Multi-Criteria Score (MCS)
- F. Objective function interface
- G. Application-layer weighted round-robin queues
- H. DIO extensions and interoperability

## Table III -- AER-MQoS signals vs. DIO/DAO carriage (rpl-of-aer-plus.c builds). Values are local to the node unless noted; no project-specific TLV is serialized in the evaluated firmware. W.=on-wire; St.=local state.

  - (Paragraph) Code path (rank computation)
  - (Paragraph) Design trajectory (future TLV roadmap)
- I. Interoperability summary
- J. Summary

# IV. Security and Trust Indicators

- A. Threat model and scope
- B. Trust signal derived from link statistics
- C. Trust term in the MCS partial score
- D. Positioning relative to trust-centric RPL extensions
- E. Future attack-injection studies (out of scope here)
- F. Summary

# V. Energy Context and Prediction

- A. Normalized residual energy (NRE)
- B. Prediction as a short-horizon moving average
- C. Cooja-only evolution of the residual state
- D. Interaction with context fusion (alpha,beta,gamma)
- E. Relation to analytical energy models in the literature
- F. Summary

# VI. Bounded Table-Driven Nudge on the Context Coefficient (Design Specification)

- A. Relation to tabular Q-learning
- B. State space
- C. Action space and effect on gamma
- D. Reward signal
- E. Update rule and fixed learning parameters
- F. What is not evaluated in this submission
- G. Summary

# VII. Performance Evaluation

- A. Goals and hypotheses
  - 1. H1 (QoS under heterogeneity)
  - 2. H2 (Energy)
  - 3. H3 (Stability)
- B. Experimental environment
- C. Protocol configurations (four-way comparison)

## Table IV -- Cooja link footprint per firmware tag (TARGET=cooja, campaign metrics enabled). Project-specific objects sum to approx. 8.6 KiB .text for shared modules; full image includes Contiki-NG + rpl-lite.

- D. Metrics
  - (Paragraph) Latency measurement
- E. Protocol--metric comparison matrix

## Table V -- Protocol variants vs. core QoS/energy observables (same topology and traffic within a campaign). Expected trends vs. RPL_STANDARD are stated in words in each cell under mixed C0--C3 traffic unless noted.

## Table VI -- Protocol variants vs. control, stability, and security-facing observables (continuation of Table V).

- F. Planned extensions (not in submitted results)
- G. Statistical methodology
- H. Data provenance (measured Cooja bundle)
- I. Empirical results (multi-seed Cooja)

## Table VII -- Descriptive performance metrics under lossy UDGM channel (success_ratio=0.85, N=4 seeds).

- J. Discussion
- K. Figures (measurement panels bound to CSV pipeline)

## Figure 4 -- Overall and C3 PDR (%) on the lossy UDGM channel (success_ratio=0.85): per-seed boxplots and descriptive means from pdr.csv. Campaign descriptive means (Table VII); per-seed variance unavailable from committed CSVs (see Section H). RPL_MQoS and RPL_AER reflect a single valid seed (seeds 1--3 artefact). AER-MQoS mean over seeds 2--4. Visual scaling applied for readability.

## Figure 5 -- Measured application-layer end-to-end latency (ms) on the lossy channel (TX/RX pairing; not the ETX-derived MCS surrogate). Descriptive means from latency.csv. Campaign descriptive means (Table VII); per-seed variance unavailable from committed CSVs (see Section H). RPL_MQoS and RPL_AER reflect a single valid seed (seeds 1--3 artefact). AER-MQoS mean over seeds 2--4. Visual scaling applied for readability.

- L. Inter-arrival gap metric

## Figure 6 -- Mean inter-arrival gap (ms) per class C0--C3 from jitter.csv (not RFC 3393 IPDV; C3 ring-highlighted). Large gaps reflect sparse Poisson arrivals over long runs. Campaign descriptive means (Table VII); per-seed variance unavailable from committed CSVs (see Section H). RPL_MQoS and RPL_AER reflect a single valid seed (seeds 1--3 artefact). AER-MQoS mean over seeds 2--4. Visual scaling applied for readability.

## Figure 7 -- Internal NRE (instrumentation) per firmware tag from energy.csv (nre_proxy_pct); not Energest duty-cycle or joules. Campaign descriptive means (Table VII); per-seed variance unavailable from committed CSVs (see Section H). RPL_MQoS and RPL_AER reflect a single valid seed (seeds 1--3 artefact). AER-MQoS mean over seeds 2--4. Visual scaling applied for readability.

## Figure 8 -- Control-plane export proxy: ctrl_export_rate from ctrl.csv (METRIC/context export rate per node per minute). Time axis covers the initial bootstrap window (approx. 0--1 min of 30 min simulation). Campaign descriptive means (Table VII); per-seed variance unavailable from committed CSVs (see Section H). RPL_MQoS and RPL_AER reflect a single valid seed (seeds 1--3 artefact). AER-MQoS mean over seeds 2--4. Visual scaling applied for readability.

## Figure 9 -- Route-adaptation proxy: cumulative ctx_update_cumulative from stab.csv versus simulated time (METRIC/CTX proxy). Time axis covers the initial bootstrap window (approx. 0--1 min of 30 min simulation). Campaign descriptive means (Table VII); per-seed variance unavailable from committed CSVs (see Section H). RPL_MQoS and RPL_AER reflect a single valid seed (seeds 1--3 artefact). AER-MQoS mean over seeds 2--4. Visual scaling applied for readability.

## Figure 10 -- Temporal PDR stratification over epochs epoch_first_half and epoch_second_half from sec.csv (four firmware tags; not an attack scenario). Campaign descriptive means (Table VII); per-seed variance unavailable from committed CSVs (see Section H). RPL_MQoS and RPL_AER reflect a single valid seed (seeds 1--3 artefact). AER-MQoS mean over seeds 2--4. Visual scaling applied for readability.

- M. Reproducibility checklist

# VIII. Conclusion and Future Work

- Limitations (unnumbered)
- Future work (unnumbered)

# Data Availability

The source code, Cooja simulation scenarios, and measured datasets (N=4 independent seeds) used in this study are publicly available in the following GitHub repository: https://github.com/madani-belacel/AER-MQoS

# Author Contributions

The author conceived the integrated protocol design, implemented the Contiki-NG firmware and evaluation scripts, coordinated the Cooja campaigns, and wrote the manuscript.

# Appendix: Supplementary Instrumentation Panels

- A. Repository-only statistics (not cited)
- B. Learning-stratification sanity check

## Figure 11 -- Logging sanity check: PDR vs. offered-load quartiles for learning_on strata in learn_or_load.csv (same AER-MQoS binary; not a learning ablation). Campaign descriptive means (Table VII); per-seed variance unavailable from committed CSVs (see Section VII-H). RPL_MQoS and RPL_AER reflect a single valid seed (seeds 1--3 artefact). AER-MQoS mean over seeds 2--4. Visual scaling applied for readability.

# References

