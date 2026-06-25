# OpenCode — Self-Identified Anomalies After All Fix Rounds

**Date :** 2026-06-24  
**Scope :** Post-correction audit after implementing all reviewer feedback from Grok, ChatGPT, Claude, DeepSeek, Notion.

---

## 🔴 P0 — Pipeline Data Integrity (CRITICAL: Contradiction Figures vs Table VII)

### 1. pdr.csv / latency.csv contain stale single-seed data

**Evidence :**
```
$ cat pdr.csv
lossy,RPL_STANDARD,20260602,77.2414
lossy,RPL_MQOS,20260602,77.2414    ← identical (artefact)
lossy,RPL_AER,20260602,77.2414     ← identical
lossy,AER_MQOS,20260602,77.2414    ← identical

$ cat latency.csv
lossy,RPL_STANDARD,20260602,596.681
lossy,RPL_MQOS,20260602,596.681   ← identical
lossy,RPL_AER,20260602,596.681    ← identical
lossy,AER_MQOS,20260602,596.681   ← identical
```

**Impact :**
- Fig 4 (PDR) → y-axis at **71.92%** for all variants
- Fig 5 (latency) → y-axis at **597 ms** + broken scientific notation (`1e−6 + 5.96681e2`)
- Table VII → hardcoded `96.44%` / `793 ms` etc. (does NOT read from CSV)
- **Result :** Table VII contradicts Figures 4 and 5 by ~25 percentage points / ~200 ms.
- **Rejection risk :** Immediate. Any reviewer will spot this.

**Root cause :** CSVs in `sim/multi_seed/` were generated from a quick smoke-test run (single seed 20260602), not from the full N=4 campaign. Table VII values were manually entered from a different (non-committed) dataset.

**Fix :**
- Either regenerate CSVs from the full campaign (N=4, corrected tagging), or
- Align Table VII with CSV data and adjust all text claims accordingly, or
- Replace figures with per-seed scatter plots that match the actual CSV data.

---

### 2. All protocols show identical CSV values (artefact contaminated also RPL_STANDARD?)

**Evidence :** Even `RPL_STANDARD` (lossy) shows 77.24% PDR in pdr.csv, while Table VII claims 96.44%. And `RPL_STANDARD` shows **exactly** the same as all other variants. This means either:
- The CSVs are from a corrupted run (bad tagging or script), or
- The CSVs are from a quick functional test, not the evaluation campaign.

**Documented in :** `evaluation.tex:122` (campaign artefact), but the artefact is worse than stated: it affects ALL rows, not just RPL_MQoS / RPL_AER.

---

## 🟠 P1 — Unresolvable Without Re-Simulation

| # | Anomaly | Sources | Action |
|---|---------|---------|--------|
| 3 | N=4 insufficient (N≥20 needed) | All 5 reviewers | Re-run with `NUM_SEEDS=20` |
| 4 | No ablations (A1 WRR-off, A2 learning-off, A3 trust-neutral) | All 5 reviewers | Build and run 3 ablation variants |
| 5 | No Energest energy traces | ChatGPT, Claude, Grok | Add `energest.h` logging to Cooja |
| 6 | Trust not validated under attack | ChatGPT, Claude, Grok, DS | Scripted Cooja attacks |
| 7 | PDR overlap (93.4-99.8%) → H1 unconfirmed | All reviewers | Higher traffic load needed |
| 8 | AER-MQoS PDR 97.68% < RPLMQoS 98.54% | ChatGPT #3 | Either demonstrate superiority or reposition |
| 9 | Fig 8/9 axis only 0-1 min of 30 min simulation | Claude #7-8 | Fix CSV logging to cover full duration |
| 10 | Topology 25 nodes insufficient | ChatGPT, Claude, Grok | Test 50/100 nodes |
| 11 | No SOTA comparison (OF-EC, DRL-RPL, Fuzzy-OF) | ChatGPT, Grok | Add benchmarks |

---

## 🟡 P2 — Documented Limitations (No Action Short of Re-Simulation)

| # | Anomaly | Status |
|---|---------|--------|
| 12 | No custom DIO/DAO TLVs (all signals local) | Documented in architecture.tex |
| 13 | WRR above UDP → no MAC blocking relief | Documented |
| 14 | No inferential statistics (Mann-Whitney pending) | Script exists, needs N≥20 |
| 15 | Energy is logical NRE proxy (not Energest) | Documented |
| 16 | Q-learning is specification only (no ablation) | Abstract/conclusion rephrased |
| 17 | Heavy self-citations to prior works [7][8][11][18] | Moderate (improved) |

---

## 🔵 P3 — Minor / Cosmetic

| # | Anomaly | Status |
|---|---------|--------|
| 18 | `AER_MQOS` (underscore) vs `AER-MQoS` (hyphen) in Fig 11 caption | CAPTIONS_EN.tex uses `\texttt{AER\_MQOS}` |
| 19 | Possible visual ambiguity `20260603` vs `20206003` at small font | Abstract/introduction use correct `20260603` |
| 20 | OCP 8 clarified as non-IANA | ✅ Done in architecture.tex:69 |
| 21 | Fig 3 caption improved (γ, α=γ, β=1-γ, mirror) | ✅ Done in CAPTIONS_EN.tex |
| 22 | Fig 8/9 axis labeled as "bootstrap window (0–1 min of 30)" | ✅ Done |
| 23 | Table VII footnotes added († ‡) | ✅ Done |
| 24 | Abstract/Conclusion Q-learning rephrased as future ablation | ✅ Done |
| 25 | Variant names uniform in PROTOCOL_ORDER | ✅ Done (`protocol_aliases.py`) |
| 26 | Fig 11 explanation strengthened | ✅ Done (evaluation.tex:161) |
| 27 | Section VII-G "n=4" should be "n=1/3/4" per variant | ❌ Not fixed |

---

## Summary

| Type | Count | 
|------|-------|
| 🔴 P0 — Pipeline contradiction (must fix before next compile) | 2 |
| 🟠 P1 — Requires re-simulation | 9 |
| 🟡 P2 — Documented limitation | 6 |
| 🔵 P3 — Minor remaining | 9 |
| **Total** | **26** |

**Key finding:** The CSV/Table VII contradiction (§VII-H vs Figs 4-5) is the single most critical issue. Fixing this alone eliminates ~70% of rejection risk according to ChatGPT's assessment. All other issues are either acknowledged limitations or require a full campaign re-run.

**Recommendation:** Before any further editing, align the CSVs with Table VII (or vice versa). The current state — where the figure generation pipeline outputs data that differ by 25 percentage points from the printed table — is incompatible with submission.
