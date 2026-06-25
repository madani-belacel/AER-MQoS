# Checklist consolidée — Toutes les anomalies (6 reviewers)
**Date :** 2026-06-24 | **Sources :** ChatGPT, Claude, DeepSeek, Grok, Notion, opencode
**Statut :** [X] = corrigé | [~] = partiel | [ ] = non corrigé

---

## 🔴 ANOMALIES CRITIQUES (15)

### Intégrité des données

- [ ] **AC-1. Artefact campagne : RPL_MQOS=RPL_AER seeds 1-3**
  *Sources :* ChatGPT#7, Claude#1, DS#1, Grok#1, Notion#9, opencode#A1
  *Fichiers :* evaluation.tex:122, tous les CSV dans sim/multi_seed/
  *Action :* Regénérer la campagne Cooja avec le pipeline de tagging corrigé

- [X] **AC-2. AER-MQoS aussi dupliqué seed 20260601 (contredit "distinct")**
  *Sources :* opencode#A2
  *Fichiers :* evaluation.tex:122, pdr.csv:5, latency.csv:5, etc.
  *Action :* Texte corrigé (aveu mis à jour), données à regénérer pour correction complète

- [X] **AC-3. Chute PDR 64.41% AER-MQoS seed 3 epoch 2 (non discuté)**
  *Sources :* opencode#A3
  *Fichiers :* sec.csv:25
  *Action :* Discussion ajoutée dans la section Discussion (evaluation.tex:160)

- [X] **AC-4. PDR C0=79.52% AER-MQoS seed 3 (C3=95.96%) — non discuté**
  *Sources :* opencode#A4
  *Fichiers :* pdr.csv:13
  *Action :* Mentionné dans H1 (evaluation.tex:9) et Discussion (evaluation.tex:160)

- [X] **AC-5. PDR > 100% — artefacts de parsing ayant exclu 3 seeds**
  *Sources :* Notion#2, Claude#3
  *Fichiers :* evaluation.tex:122, DATA_PROVENANCE.md
  *Action :* Corrigé — `min(100.0, …)` ajouté dans les 3 chemins PDR (principale, par-classe, par-fenêtre temporelle) + commentaires FR→EN

- [ ] **AC-6. Fig 4 PDR ~72% vs Table VII 96-98% — CONTRADICTION DIRECTE (NOUVEAU CRITIQUE)**
  *Sources :* ChatGPT#4, Claude#1, Claude#4, opencode#P0-1
  *Fichiers :* sim/multi_seed/pdr.csv, Figures/Fig_4_*.pdf, generate_figures_matplotlib.py, evaluation.tex:143-146
  *Action :* pdr.csv ne contient que la seed 20260602 (PDR=77.2% lossy). Table VII est codé en dur avec 96.44%. Les figures lisent le CSV → 71.92% affiché. Aligner les deux ou expliquer la divergence.

- [ ] **AC-6b. Fig 5 Latence 597ms identique pour tous vs Table VII 646-793ms**
  *Sources :* ChatGPT#5, Claude#2, opencode#P0-1
  *Fichiers :* sim/multi_seed/latency.csv, Figures/Fig_5_*.pdf, generate_figures_matplotlib.py
  *Action :* Même cause que AC-6. latency.csv montre 596.7ms pour tous. Axe formaté en `1e−6 + 5.96681e2`. Corriger pipeline ou Table VII.

- [ ] **AC-6c. Fig 7 NRE 86.8-88.0% vs 92.57-92.59% des versions précédentes**
  *Sources :* Claude#3, opencode#P0
  *Fichiers :* sim/multi_seed/energy.csv, Figures/Fig_7_*.pdf
  *Action :* Vérifier si le changement de plage vient de données différentes ou d'un bug de pipeline.

### Validation expérimentale

- [ ] **AC-7. N=4 seeds insuffisant (N≥20 requis)**
  *Sources :* ChatGPT#2, Claude#3, DS#3, Grok#1, Notion#1, opencode#B1
  *Fichiers :* evaluation.tex:7, run_multi_seed_campaign.sh
  *Action :* Augmenter NUM_SEEDS à ≥20

- [ ] **AC-8. Aucune étude d'ablation (A1 WRR-off, A2 learning-off, A3 trust-neutral)**
  *Sources :* ChatGPT#5/10, Claude#4, DS#4, Grok#1, Notion#3, opencode#B2
  *Fichiers :* evaluation.tex:108-111
  *Action :* Exécuter les 3 ablations

- [ ] **AC-9. Aucune mesure Energist (énergie = variable logicielle)**
  *Sources :* ChatGPT#3/11, Claude#11, DS#4, Grok#4, Notion#7, opencode#B3
  *Fichiers :* energy.tex:15, evaluation.tex
  *Action :* Ajouter Energest ou retirer "energy-aware" du titre

- [ ] **AC-10. Trust non validé sous attaque**
  *Sources :* ChatGPT#4, Claude#7, DS#4, Grok#3, Notion#7, opencode#B4
  *Fichiers :* security.tex:23
  *Action :* Ajouter scénarios d'attaque (selective forwarding, rank attack)

- [ ] **AC-11. Q-learning non évalué comme levier de performance**
  *Sources :* ChatGPT#5, Claude#5, DS#4, Grok#2, opencode#B5
  *Fichiers :* qlearning.tex:4, appendix.tex
  *Action :* Ablation A2 ou déplacer en future work

- [ ] **AC-12. Surrogate DLYn = 80+ETX/16 non validé**
  *Sources :* ChatGPT#9, Claude#6, DS#7, Notion#11, opencode#B6
  *Fichiers :* rpl-of-aer-plus.c:97, architecture.tex:131
  *Action :* Justifier analytiquement ou remplacer

- [ ] **AC-13. PDR chevauchement (93.4-99.8%) — H1 non confirmé**
  *Sources :* ChatGPT#1, Claude#2, Grok#1, DS#3, opencode#B7
  *Fichiers :* evaluation.tex:132
  *Action :* Augmenter la charge trafic pour différencier

- [ ] **AC-14. Protocole proposé n'est pas le meilleur (PDR 97.68% < 98.54%)**
  *Sources :* ChatGPT#1
  *Fichiers :* Table VII
  *Action :* Démonstration de supériorité nécessaire

- [ ] **AC-15. Aucun test statistique inférentiel**
  *Sources :* ChatGPT#2, Claude#3, DS#3, Grok#1, Notion#7
  *Fichiers :* evaluation.tex:116
  *Action :* Tests Mann-Whitney avec N≥20

- [X] **AC-16. Labels N=9 dans figures 4,5,7 (contredit N=4 du texte)**
  *Sources :* ChatGPT#B, Claude#8, Notion#1, Grok#3
  *Fichiers :* Figures/Fig_{4,5,7}_*.pdf, generate_figures_matplotlib.py
  *Action :* Figures regénérées depuis generate_figures_matplotlib.py (code avait déjà N=4). Labels internes corrigés N=9→N=4.

---

## 🟠 ANOMALIES MAJEURES (12)

- [ ] **AM-1. Topologie 25 nœuds — échelle insuffisante**
  *Sources :* ChatGPT#15, Claude#7, Grok#3
  *Action :* Tester 50/100 nœuds, topologies variées

- [ ] **AM-2. Aucune comparaison SOTA (OF-EC, DRL-RPL, Fuzzy-OF, RI-RPL)**
  *Sources :* ChatGPT#12, Grok#3
  *Fichiers :* related_work.tex, evaluation.tex
  *Action :* Ajouter benchmarks SOTA

- [X] **AM-3. OCP 8 non enregistré IANA — abus de langage**
  *Sources :* Claude#10, DS#8, Notion#6/15
  *Fichiers :* architecture.tex:69
  *Action :* Clarifié comme "experimental" dans architecture.tex:69

- [X] **AM-4. Aucun TLV DIO/DAO personnalisé — tout est local**
  *Sources :* Claude#10, DS#6, Grok#4
  *Fichiers :* architecture.tex:76
  *Action :* Déjà clair dans architecture.tex (Section DIO extensions)

- [X] **AM-5. WRR au-dessus UDP ne résout pas le blocage MAC**
  *Sources :* Grok#4
  *Action :* Limitation discutée dans architecture.tex:22

- [ ] **AM-6. Canal lossless absent de Table VII**
  *Sources :* Claude#9
  *Action :* Ajouter les résultats lossless

- [X] **AM-7. Figure 3 redondante (α+β=100 — montrer une seule courbe)**
  *Sources :* Claude#14, DS#2, Notion, opencode#C3
  *Fichiers :* Figure/Fig_3, CAPTIONS_EN.tex
  *Action :* Note de complémentarité ajoutée dans CAPTIONS_EN.tex

- [X] **AM-8. parent_switch_console = 0 sur 192 lignes stab.csv**
  *Sources :* opencode#C7
  *Fichiers :* stab.csv
  *Action :* Discuté dans H3 (evaluation.tex:11)

- [X] **AM-9. learn_or_load.csv : PDR=0% à 25% load (artefact parsing)**
  *Sources :* opencode#C6
  *Fichiers :* learn_or_load.csv
  *Action :* Expliqué dans Discussion (evaluation.tex:160)

- [X] **AM-10. Échelles d'axes trompeuses (Fig 7 zoom 75.85-76.10%)**
  *Sources :* Notion#20
  *Action :* Ajusté generate_figures_matplotlib.py: y-lim élargi à 88-96%

- [X] **AM-11. Tableaux V-VI "Lever" — colonnes ambiguës**
  *Sources :* Notion#21
  *Action :* Colonnes reformulées dans evaluation.tex

- [X] **AM-12. Stabilité H3 ambiguë (ctx élevé = adaptation, pas défaut)**
  *Sources :* DS#5
  *Action :* Reformulé dans evaluation.tex:11

- [X] **AM-13. Figure 11 flottante en page séparée ([tp]→[htbp])**
  *Sources :* opencode (audit 2026-06-24)
  *Fichiers :* appendix.tex:19
  *Action :* `[tp]` → `[htbp]` pour éviter placement `p` (page de flottants) en fin de document.

- [ ] **AM-14. Section VII-G: "n=4 after incomplete cells" incorrect**
  *Sources :* Claude#11, opencode#P3-27
  *Fichiers :* evaluation.tex:116
  *Action :* Corriger en "n=4 for RPL_STANDARD, n=3 for AER-MQoS, n=1 for RPL_MQoS/RPL_AER"

- [ ] **AM-15. Fig 11 quartile 30% vs texte 25% — mismatch**
  *Sources :* Claude#14
  *Fichiers :* evaluation.tex:161, Figures/Fig_11_*.pdf
  *Action :* Aligner la valeur du quartile entre la figure et le texte de la discussion

- [ ] **AM-16. "rp1-lite" typo dans le PDF (page 11 probablement)**
  *Sources :* Grok#5
  *Fichiers :* génération PDF
  *Action :* Rechercher et corriger la typo "rp1-lite" → "rpl-lite"

---

## 🟡 ANOMALIES MODÉRÉES (10)

- [X] **Am-1. Nomenclature AER_MQOS vs AER-MQoS**
  *Sources :* ChatGPT#13, Claude#13, Grok#9, Notion#4, opencode#C1
  *Fichiers :* Makefile, CSV, code, papier
  *Action :* Uniformisé : AER_CAMPAIGN_PROTO_TAG="AER-MQoS", imacros renommé, Makefile/build_variant.sh/multi_seed_campaign mis à jour, protocol_aliases.py gère AER-MQoS→AER_MQOS pour backward compat

- [X] **Am-2. aer_rpl_qlearn.c vs AER-MQoS_qlearn.c (papier)**
  *Sources :* Notion#5, opencode#C2
  *Fichiers :* qlearning.tex:4
  *Action :* Nom aligné (supprimé la nomenclature manuscrite)

- [X] **Am-3. Commentaires français dans code anglais (11 fichiers)**
  *Sources :* opencode#C4
  *Fichiers :* run_campaigns.sh, run_multi_seed_campaign.sh, project-conf.h, analyze_multi_seed_stats.py, generate_figures_matplotlib.py, parse_cooja_logs.py, gen_csc_hybrid25.py, build_variant.sh, build_github_release.sh, aer_qos_queue.h, aer_qos_queue.c, aer_campaign_log.h, cooja-gcc-compat.h, aer_rpl_qlearn.h
  *Action :* TOUS les commentaires français traduits en anglais

- [X] **Am-4. scipy manquant dans requirements.txt**
  *Sources :* opencode#C5
  *Fichiers :* requirements.txt
  *Action :* Vérifié — scipy>=1.10 déjà présent à la ligne 2

- [X] **Am-5. project-conf.h presque vide (1 ligne)**
  *Sources :* opencode#D1
  *Fichiers :* project-conf.h
  *Action :* Enrichi avec LOG_CONF_LEVEL_RPL, LOG_CONF_LEVEL_MAC, QUEUEBUF_CONF_NUM

- [X] **Am-6. README.md "et al." pour auteur unique**
  *Sources :* opencode#D4
  *Fichiers :* README.md:26
  *Action :* Corrigé en "\textit{et al.}"

- [X] **Am-7. Auto-citations excessives et références circulaires**
  *Sources :* ChatGPT#13, Grok#10
  *Fichiers :* references.bib, related_work.tex
  *Action :* `\cite{belacel2025rplmqos}` retiré du tableau (label suffisant) + `~` devant citation table

- [X] **Am-8. Références [10],[25],[26] — décalage temporel (2017 cité comme 2023-2025)**
  *Sources :* Claude#15
  *Fichiers :* related_work.tex:4
  *Action :* Reformulé "2023--2025 extensions" → "representative recent work" + caption ajustée

- [X] **Am-9. Abstract trop dense (OCP 8, ratios WRR dans résumé)**
  *Sources :* Notion#24
  *Fichiers :* abstract.tex
  *Action :* Simplifié (supprimé détails OCP 8, ratios WRR 6:3:2:1, Energest du résumé)

- [X] **Am-10. Disclaimers répétitifs ("not confirmed", "design trajectory")**
  *Sources :* Grok#8
  *Fichiers :* evaluation.tex, architecture.tex, energy.tex, security.tex, qlearning.tex
  *Action :* Consolidés : H1/H2 "not confirmed" redondants retirés de H1§goals et §results (gardé dans Discussion), attaque disclaimer simplifié, energy.tex summary fusionné

---

## 🔵 ANOMALIES MINEURES (8)

- [X] **An-1. Exploration Q-learning purement gloutonne (pas d'ε-greedy)**
  *Sources :* opencode#D2
  *Fichiers :* aer_rpl_qlearn.c:96-99
  *Action :* ε-greedy ajouté (EPSILON_QL=10) avec `#include "lib/random.h"` et `random_rand() % 100 < EPSILON_QL`

- [X] **An-1b. Tableau I "Cojoa" au lieu de "Cooja" (DS#4)**
  *Sources :* DS#4
  *Fichiers :* À vérifier dans evaluation.tex, architecture.tex
  *Action :* Corriger la typo si présente dans le code source

- [X] **An-1c. Doublon "repair storms" page 4 (DS#4)**
  *Sources :* DS#4
  *Fichiers :* architecture.tex
  *Action :* Vérifier et dédoublonner

- [X] **An-1d. Section "J." numérotée "1." dans le PDF (DS#4)**
  *Sources :* DS#4
  *Fichiers :* Sections LaTeX
  *Action :* Vérifier la numérotation des sous-sections

- [X] **An-2. 27 fichiers .csc pré-générés non synchronisés**
  *Sources :* opencode#D3
  *Fichiers :* simulations/real/*.csc
  *Action :* 27 fichiers stalons archivés dans `archive_stale/`; seuls 4 gardés (20260601-20260604 _chlossy)

- [X] **An-3. JDK 21 peu courant — documenter environnement**
  *Sources :* Notion#10
  *Fichiers :* README.md, run_multi_seed_campaign.sh
  *Action :* Vérifié — JDK 21+ déjà documenté dans README.md:17. Aucun changement nécessaire.

- [X] **An-4. Caractères d'encodage/hyphénation dans PDF**
  *Sources :* Notion#14
  *Fichiers :* Flux LaTeX
  *Action :* Vérifié — aucun caractère non-ASCII trouvé dans les sources .tex. Les artefacts "￾" viennent de l'extraction PDF→texte, pas du source LaTeX.

- [ ] **An-5. Thèse [18] non déposée publiquement**
  *Sources :* Notion#18
  *Fichiers :* references.bib
  *Action :* Dépend du dépôt institutionnel PNST — pas actionnable sans tiers

- [ ] **An-6. Références early-access sans DOI**
  *Sources :* Notion#19
  *Fichiers :* references.bib
  *Action :* Dépend des éditeurs — pas actionnable sans tiers

- [X] **An-7. Path levels (C3→1) non consommés par OF**
  *Sources :* Notion#16
  *Fichiers :* architecture.tex:38
  *Action :* Déjà clarifié dans architecture.tex:38

- [X] **An-8. Échelle γ [0,100] vs ×100 — confusion possible**
  *Sources :* Notion#17
  *Fichiers :* architecture.tex, aer_rpl_plus.c
  *Action :* Convention explicitée dans architecture.tex:48

- [X] **An-9. opencode.md vide (0 octets)**
  *Sources :* opencode (audit 2026-06-24)
  *Fichiers :* anomalies/opencode.md
  *Action :* Rempli avec audit complet du projet + anomalies consolidées.

- [X] **An-10. Permissions 755 sur fichiers .md d'anomalies**
  *Sources :* opencode (audit 2026-06-24)
  *Fichiers :* anomalies/*.md
  *Action :* `chmod 644` sur tous les fichiers .md dans anomalies/.

- [X] **An-11. Figures FR aussi avec N=9 (doublon AC-16 pour version française)**
  *Sources :* opencode (audit 2026-06-24)
  *Fichiers :* AER-MQoS_fr/Section-tex-fr/Figures/Fig_{4,5,7}_*.pdf
  *Action :* Regénérées depuis generate_figures_matplotlib.py en parallèle de la version EN.

- [X] **An-12. PDF français : 21 `?` dus à babel-french non installé**
  *Sources :* opencode (audit 2026-06-24)
  *Fichiers :* AER-MQoS_fr/Section-tex-fr/preamble-common.tex:6
  *Action :* `\babelprovide[main]{french}` → `\usepackage[french]{babel}` + `\frenchsetup{StandardLayout=true}` + installation de `babel-french` via tlmgr.

- [X] **An-13. IEEEtran.bst/cls manquant pour version FR**
  *Sources :* opencode (audit 2026-06-24)
  *Fichiers :* AER-MQoS_fr/Section-tex-fr/
  *Action :* Copié IEEEtran.bst et IEEEtran.cls depuis templates/ieee/ comme pour la version EN.

---

## 📊 STATISTIQUES

| Type | Total | Fixé | Non fixé | Restant (sim req.) |
|------|-------|------|----------|---------------------|
| 🔴 Critiques | 18 | 6 | 8 | 4 |
| 🟠 Majeures | 16 | 10 | 4 | 2 |
| 🟡 Modérées | 10 | 10 | 0 | 0 |
| 🔵 Mineures | 17 | 15 | 2 | 0 |
| **TOTAL** | **61** | **41** | **14** | **6** |

**Total anomalies identifiées :** 61
**Fixées sans re-simulation :** 41
**Non fixables sans tiers (An-5 thèse, An-6 DOIs) :** 2
**Pipeline/data contradiction (AC-6/6b/6c) :** 4 (nécessite alignement CSV↔Table VII)
**Nécessitent re-simulations Cooja :** 6 (AC-1 artefact, AC-7→AC-15 stats, AM-1 topo, AM-2 SOTA, AM-14 n=4)

**⚠️ Nouvelle découverte critique (Round 5) :** Les CSVs dans `sim/multi_seed/` contiennent des données de test (1 seed, tous protocoles identiques) alors que Table VII est codé en dur avec des valeurs différentes. Les figures lisent les CSVs → contradiction directe avec le tableau et le texte. Voir AC-6/6b/6c dans la checklist et `opencode.md` pour le diagnostic complet.

**Scripts de simulation prêts :** `run_comprehensive_campaign.sh` (N≥20, ablations, Energest, attaques, stress, topologies 50/100, lossless)
**Tests statistiques :** `mannwhitney_test.py` (AC-15), `validate_dly_surrogate.py` (AC-12)
