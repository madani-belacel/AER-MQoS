Voici les anomalies identifiées dans cette version du manuscrit :

---

## 🔍 Anomalies identifiées dans AER-MQoS (main-ieee.pdf)

### 1. Artefact de campagne — données identiques pour RPL_MQoS et RPL_AER (seeds 1–3)

> *Section VII-H, Table VII*
> 

Les valeurs CSV de **RPL_MQoS et RPL_AER sont identiques pour les seeds 1–3** sur toutes les métriques. Cela invalide toute comparaison directe entre ces deux variantes. Seul le seed 4 est exploitable pour les distinguer. La Table VII en tient compte (note †), mais la figure 4 présente quand même les deux barres côte à côte, ce qui peut induire en erreur.

---

### 2. Exclusion de AER-MQoS seed 1 (artefact)

> *Section VII-H, Table VII*
> 

Le seed 1 de **AER-MQoS est exclu** (artefact de parsing). La moyenne de AER-MQoS dans Table VII est donc calculée sur seulement **3 seeds (2–4)**, tandis que RPL_STANDARD en utilise 4. Cela rend les comparaisons asymétriques.

---

### 3. Chute de PDR à 64,41% pour AER-MQoS sur le seed 20260603 (2ème époque)

> *Section VII-J*
> 

Sur ce même seed, AER-MQoS montre une dégradation sévère en deuxième moitié de simulation (**64.41% vs ~97% pour les baselines**). Cette sensibilité épisodique est un signal fort que le MCS composite peut introduire une instabilité sous certaines séquences d'états de liens — un problème fonctionnel non résolu, documenté comme nécessitant des campagnes d'ablation.

---

### 4. Anomalies aux extrémités du load dans `learn_or_load.csv`

> *Section VII-J, Appendice B*
> 

Le fichier `learn_or_load.csv` montre **0% PDR au quartile 25%** et **100% PDR au quartile maximum**. L'article attribue ces valeurs à des artefacts de binage sparse — mais ces points limites restent présents dans la figure 11, ce qui peut fausser l'interprétation visuelle si le lecteur n'a pas lu la note explicative.

---

### 5. Exclusion de 3 seeds supplémentaires (20260512, 20260605, 20260606)

> *Section VII-H*
> 

Trois seeds ont été **exclus pour artefacts de parsing** (logs dupliqués, PDR > 100%). L'échantillon final de N=4 seeds est donc issu d'une sélection post-hoc parmi 7 seeds initiaux — ce qui fragilise la représentativité statistique et n'est pas mentionné dans le résumé/abstract.

---

### 6. Inversion de classe sur seed 20260603 : MRHOF vs AER-MQoS

> *Section VII-J*
> 

Sur ce seed, **MRHOF favorise C0 (96.39%) au détriment de C3 (92.73%)**, alors qu'AER-MQoS fait l'inverse (C3 = 95.96%, C0 = 79.52%). Ce résultat est présenté comme une preuve de différenciation, mais la forte dégradation de C0 dans AER-MQoS sur ce même seed pourrait indiquer un effet secondaire indésirable de la pondération MCS, pas seulement une priorisation voulue.

---

### 7. Le nudge Q-learning n'est pas validé expérimentalement

> *Sections VI, VII-F, Appendice B*
> 

Le mécanisme Q-learning est **spécifié et implémenté mais jamais évalué comme levier de performance**. Il n'existe pas de build `NO_QL` pour comparaison. La figure 11 (Appendice B) est uniquement un test de cohérence de logging — ce point est correctement déclaré dans le texte, mais la présence du mécanisme dans le firmware sans ablation constitue une anomalie méthodologique à signaler aux reviewers.

---

### 8. Scalabilité de l'axe Y dans les figures 4 et 5

> *Figures 4, 5*
> 

L'axe Y de la figure 4 (PDR) est **zoomé entre ~70.5% et 73%**, et la figure 5 (latence) utilise une **échelle en 1e-6 + constante** (~596.681 ms). Ces choix de mise à l'échelle amplifient visuellement des différences très faibles (< 2 points de PDR, sub-milliseconde de latence), ce qui peut donner une impression de différenciation plus forte qu'elle ne l'est réellement.

---

**Résumé des priorités :**

| # | Anomalie | Sévérité |
| --- | --- | --- |
| 1 | RPL_MQoS = RPL_AER sur seeds 1–3 | 🔴 Haute |
| 3 | Chute PDR 64.41% seed 20260603 | 🔴 Haute |
| 5 | Exclusion de 3 seeds sur 7 | 🟠 Moyenne |
| 2 | AER-MQoS seed 1 exclu | 🟠 Moyenne |
| 6 | Inversion C0/C3 ambiguë | 🟠 Moyenne |
| 7 | Q-learning non ablationné | 🟡 Faible (bien déclaré) |
| 4 | Artefacts binage learn_or_load | 🟡 Faible |
| 8 | Mise à l'échelle trompeuse | 🟡 Faible |
