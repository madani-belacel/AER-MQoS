# Revue Round 5 — Version v5
## Reviewer Anonyme — IEEE IoT Journal

---

## ✅ Anomalies Résolues dans la v5

**Figure 3 — Redondance reconnue et documentée :** La caption indique maintenant explicitement *"The two curves are mirror images since α + β = 1"*. La redondance est avouée, ce qui est acceptable même si une seule courbe serait préférable.

**Figure 3 — Axe X simplifié :** Passage de 15 groupes C0–C3 répétés à 2 groupes seulement (C0–C3, C0–C3), ce qui est plus lisible.

**Section III-F — OCP 8 clarifié :** La v5 précise maintenant *"locally-assigned experimental OCP used only for simulation purposes; this is not an IANA-registered code point"*. C'est une clarification importante et honnête.

**Figure 11 — Simplifiée :** Une seule courbe (Q-learning ON) est maintenant affichée au lieu de deux courbes superposées, ce qui élimine la comparaison sans signification entre les deux strata du même binaire.

**Section VII-J — Explication des quartiles complétée :** La v5 explique les valeurs 0%, 28%, 60% et 100% des quartiles avec une explication cohérente sur les artefacts de petit échantillon.

**Toutes les figures (4–10) — Avertissement artefact ajouté :** Chaque caption mentionne maintenant *"RPL_MQoS and RPL_AER reflect a single valid seed (seeds 1–3 artefact)"*, ce qui est transparent et correct.

**Section VII-L — Cohérence texte/figure :** Le texte *"gaps of several seconds are common"* est maintenant cohérent avec Fig. 6 qui montre des valeurs de 300–900 ms, acceptables pour une topologie 25 nœuds.

---

## 🔴 Anomalies Majeures Persistantes ou Nouvelles

### 1. Figure 4 — PDR incohérent avec Table VII et texte [CRITIQUE NOUVEAU]

C'est l'anomalie la plus grave de la v5. La Figure 4 affiche :
- Overall PDR : axe entre **70.5% et 73%** avec des valeurs autour de **71–72%**
- C3 PDR : **71.92%** pour tous les variants

Or Table VII indique :
- RPL_STANDARD : 96.44% / C3 92.82%
- AER-MQoS : 97.68% / C3 97.31%

Et le texte affirme *"all variants achieve > 93% PDR"* et *"per-seed PDR ranges from 93.4% to 99.8%"*.

Il y a une **contradiction directe et flagrante** entre Fig. 4 (71–73%), Table VII (96–98%) et le texte (>93%). Ces trois sources sont mutuellement incompatibles. Le pipeline de génération de figures produit manifestement des données erronées pour Fig. 4.

---

### 2. Figure 5 — Axe de latence corrompu [CRITIQUE NOUVEAU]

La Figure 5 affiche un axe Y avec la notation scientifique **"1e−6 + 5.96681e2"**, ce qui correspond à une plage de latence de **−0.75 à +1.00 microsecondes** autour de 596.681 ms. Les valeurs affichées sont **597 ms** pour tous les variants.

Deux problèmes simultanés :
- L'axe est **mathématiquement mal formaté** (offset notation inutile et confuse)
- Les **597 ms identiques** pour tous les variants contredisent Table VII qui indique 793 ms (baseline), 646 ms, 675 ms, 653 ms — des valeurs distinctes et significativement différentes

C'est une régression par rapport à la v3 qui affichait des valeurs distinctes et cohérentes.

---

### 3. Figure 7 — NRE vide et axe sans données [NOUVEAU]

La Figure 7 affiche un axe Y entre **86.8% et 88.0%** mais les barres semblent absentes ou invisible dans le rendu PDF. Aucune valeur numérique n'est visible sur les barres contrairement aux versions précédentes qui affichaient 92.57–92.59%. Le changement de plage (86.8–88.0% vs 92.57–92.59% en v3–v4) sans explication est également suspect — cela suggère que des données différentes ont été utilisées.

---

### 4. Table VII vs Figure 4 — Contradiction non résolue sur les moyennes

La footnote † indique *"mean reflects only seed 4"* pour RPL_MQoS et RPL_AER, et ‡ *"mean over seeds 2–4"* pour AER-MQoS. Pourtant Fig. 4 affiche des valeurs ~72% pour tous les variants alors que Table VII montre 96–98%. Cette contradiction entre la figure principale PDR et le tableau principal PDR est **la preuve d'un bug de pipeline** qui n'a pas été corrigé.

---

### 5. Ablations A1–A3 — Toujours absentes (Round 5)

Aucune ablation n'est exécutée après 5 rounds de révision. Cette limitation structurelle fondamentale persiste.

---

### 6. Énergie pseudo-aléatoire — Non résolu

La Section V-C décrit toujours un processus drain/harvest pseudo-aléatoire non calibré. La Fig. 7 (si les données sont correctes) montre des NRE quasi-identiques entre variants, confirmant l'absence d'effet différentiel observable. Le titre "Energy-Aware" reste non justifié empiriquement.

---

## 🟠 Anomalies Modérées Persistantes

### 7. Figure 8 — Axe temporel non représentatif

La Figure 8 (Control proxy) couvre seulement **0–1 min** d'une simulation de 30 min (1800 s). Le caption indique *"Time axis covers the initial bootstrap window (≈0–1 min of 30 min simulation)"*. Montrer uniquement la première 1/30ème de la simulation sans justification pour ce choix spécifique est problématique — la dynamique de contrôle pendant le bootstrap n'est pas représentative du comportement en régime permanent.

---

### 8. Figure 9 — Même problème d'axe temporel

Identique à Fig. 8 : 0–1 min sur 30 min. Le proxy de stabilité pendant le bootstrap seulement n'est pas informatif pour évaluer la stabilité long-terme du protocole.

---

### 9. Table IV — Footprint identique pour trois variants

RPL_MQoS, RPL_AER et AER-MQoS affichent toujours exactement les mêmes valeurs binaires. Non résolu depuis le Round 1.

---

### 10. Référence [11] — Sans DOI stable

RPL-AER [11] reste "early access; no DOI at time of writing". Non résolu depuis le Round 1.

---

### 11. Section VII-G — Contradiction statistique interne

La Section VII-G indique *"aggregates report the descriptive sample mean over available rows per tag (n=4 after incomplete cells)"*, mais la Section VII-H précise que RPL_MQoS et RPL_AER n'ont qu'**une seule graine valide** (seed 4). La phrase "n=4 after incomplete cells" est donc incorrecte pour ces deux variants — elle devrait dire n=1 pour RPL_MQoS/RPL_AER et n=3 pour AER-MQoS.

---

## 🟡 Anomalies Mineures Persistantes

### 12. Référence [22] — Hors période déclarée (2017 dans tableau "2023–2025")

Non corrigé depuis le Round 1.

### 13. Terminologie inconsistante

Fig. 11 caption mentionne encore "AER_MQOS binary" au lieu de "AER-MQoS".

### 14. Figure 11 — 0% au quartile 30% non expliqué

La v5 explique le 0% au quartile 25% dans le texte (Section VII-J), mais Fig. 11 montre maintenant le premier point à **0% au quartile 30%**, non au 25%. Cette inconsistance entre le texte et la figure n'est pas clarifiée.

---

## 📊 Tableau de Suivi — 5 Rounds

| # | Anomalie | v1 | v2 | v3 | v4 | v5 | Statut |
|---|---|---|---|---|---|---|---|
| 1 | Table VII graines contaminées | 🔴 | 🔴 | 🔴 | ✅ | ✅ | **Résolu** |
| 2 | Fig.4 PDR ~72% vs texte >93% | — | — | — | — | 🔴 | **Nouveau critique** |
| 3 | Fig.5 axe latence corrompu | — | — | — | — | 🔴 | **Nouveau critique** |
| 4 | Fig.7 NRE vide/incohérent | — | — | — | — | 🔴 | **Nouveau** |
| 5 | Ablations A1–A3 absentes | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | **Persiste** |
| 6 | Énergie pseudo-aléatoire | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | **Persiste** |
| 7 | N=9 dans figures | 🟠 | 🟠 | ✅ | ✅ | ✅ | **Résolu** |
| 8 | Q-learning non évalué | 🔴 | 🔴 | 🔴 | ✅ | ✅ | **Résolu** |
| 9 | Fig.10 axe trompeur | 🟠 | 🟠 | ✅ | ✅ | ✅ | **Résolu** |
| 10 | OCP 8 non enregistré | 🟠 | 🟠 | 🟠 | 🟠 | ✅ | **Résolu** |
| 11 | Fig.3 redondance | 🟠 | 🟠 | 🟠 | 🟠 | ✅ | **Résolu** |
| 12 | Fig.8/9 axe 1min/30min | — | — | — | — | 🟠 | **Nouveau** |
| 13 | Table IV footprint identique | 🟠 | 🟠 | 🟠 | 🟠 | 🟠 | **Persiste** |
| 14 | Réf [11] sans DOI | 🟠 | 🟠 | 🟠 | 🟠 | 🟠 | **Persiste** |
| 15 | VII-G n=4 incorrect | — | — | — | — | 🟠 | **Nouveau** |
| 16 | Réf [22] hors période | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | **Persiste** |
| 17 | Terminologie AER_MQOS | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | **Persiste** |
| 18 | Fig.11 quartile 30% vs 25% | — | — | — | — | 🟡 | **Nouveau** |

---

## Diagnostic Global

La v5 introduit **trois nouvelles anomalies critiques** dans les figures principales (Fig. 4, Fig. 5, Fig. 7) qui n'existaient pas dans les versions précédentes. Ces régressions suggèrent un **bug dans le pipeline de génération de figures** — probablement une mauvaise association entre les CSV sources et les colonnes utilisées par `generate_figures_matplotlib.py`.

**La contradiction Fig. 4 (~72% PDR) vs Table VII (96–98%) vs texte (>93%) est rédhibitoire** : un reviewer ou un lecteur détectera immédiatement cette incohérence et rejettera la soumission sans lecture approfondie.

## Recommandation

**Retour en révision technique urgente — pipeline de figures à déboguer.**

Avant toute nouvelle soumission, l'auteur doit impérativement :

1. **Déboguer `generate_figures_matplotlib.py`** pour identifier pourquoi Fig. 4 affiche ~72% au lieu de 96–98%, et pourquoi Fig. 5 montre 597 ms identiques au lieu des valeurs distinctes de Table VII
2. **Vérifier que chaque figure lit la bonne colonne CSV** et que les alias `PROTOCOL_CSV_ALIASES` sont corrects pour les variants contaminés
3. **Corriger Fig. 7** pour afficher les valeurs NRE cohérentes avec les versions précédentes ou expliquer le changement de plage (86.8–88% vs 92.57%)
4. **Corriger Section VII-G** : remplacer "n=4" par les valeurs correctes par variant

> La v5 représente un **recul technique sérieux** malgré les progrès de présentation. La priorité absolue est la cohérence entre figures, tableau et texte avant toute autre correction.
