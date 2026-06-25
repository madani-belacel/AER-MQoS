Après lecture attentive de cette **nouvelle version**, je constate que le manuscrit est beaucoup plus cohérent qu'auparavant. Les incohérences N=9, les confusions sur les TLV, les métriques de contrôle et plusieurs problèmes rédactionnels ont été corrigés.

Cependant, si je suis **Reviewer #2 pour IEEE Internet of Things Journal**, il reste encore plusieurs anomalies importantes.

# 1. Problème majeur : l'artefact expérimental est toujours présent

La section VII-H indique explicitement :

> "Due to a campaign artefact, RPL_MQoS and RPL_AER CSV values are identical for seeds 1–3 across all metrics" 

et :

> "Comparisons between RPL_MQoS and RPL_AER are therefore invalid" 

Puis Table VII continue à publier leurs résultats. 

### Conséquence

Pour IEEE :

> les données de deux protocoles sont reconnues comme invalides par les auteurs eux-mêmes.

Tant que cette phrase existe, le papier reste vulnérable à un rejet.

---

# 2. Les moyennes ne sont plus statistiquement comparables

Table VII précise :

> RPL_MQoS and RPL_AER values are identical for seeds 1–3; mean reflects only seed 4. 

et

> AER-MQoS seed 1 is excluded. 

Donc :

| Protocole    | Nombre réel de seeds |
| ------------ | -------------------- |
| RPL_STANDARD | 4                    |
| AER-MQoS     | 3                    |
| RPL_MQoS     | 1                    |
| RPL_AER      | 1                    |

Le tableau compare donc des moyennes calculées sur des tailles d'échantillon différentes.

C'est méthodologiquement fragile.

---

# 3. Le protocole proposé n'est toujours pas supérieur

Table VII :

| Variant      | PDR   |
| ------------ | ----- |
| RPL_STANDARD | 96.44 |
| RPL_MQoS     | 98.54 |
| RPL_AER      | 98.49 |
| AER-MQoS     | 97.68 |



Le protocole proposé reste inférieur aux deux variantes dont il combine les mécanismes.

Le reviewer demandera :

> What is the quantitative advantage of integration?

Aujourd'hui la réponse n'est pas démontrée.

---

# 4. Contradiction dans Figure 4

Dans le texte :

> Overall PDR means lie within ≈2.10 percentage points across tags. 

Mais la Figure 4 affiche environ :

> 71.92 % pour tous les protocoles. 

Cette figure paraît incohérente avec Table VII.

Cela ressemble à un problème de génération graphique ou de normalisation.

Je vérifierais immédiatement le script Python.

---

# 5. Figure 5 semble incorrecte

Figure 5 affiche :

> 597 ms 597 ms 597 ms 597 ms 

alors que Table VII donne :

| Variant | Latency |
| ------- | ------- |
| 793     |         |
| 646     |         |
| 675     |         |
| 653     |         |



La figure et le tableau semblent incompatibles.

Très probablement un bug dans l'affichage matplotlib.

---

# 6. Figure 7 n'apporte pratiquement aucune preuve scientifique

La section V reconnaît :

> internal NRE traces (instrumentation check) 

La Figure 7 montre :

≈87–88 % pour tous les protocoles. 

Donc :

* aucune différenciation visible ;
* aucune mesure énergétique réelle ;
* aucun Energest ;
* aucun mJ.

Cette figure risque d'être considérée comme du bruit expérimental.

---

# 7. H2 n'est toujours pas validée

La section VII-A indique :

> Energest-calibrated confirmation ... reserved for future instrumentation. 

Autrement dit :

l'hypothèse énergie n'est pas démontrée.

---

# 8. H3 repose toujours sur un proxy

Vous écrivez :

> proxy captures only MCS recomputation events, not parent changes. 

Donc la stabilité RPL réelle n'est pas mesurée.

Le reviewer peut considérer H3 comme non démontrée.

---

# 9. Trop de limitations dans le corps principal

On retrouve encore :

* simulation-only 
* not experimentally validated 
* future work 
* planned campaigns 

Le papier est honnête, mais il se dévalorise lui-même.

Pour IEEE, il faut déplacer une partie de ces réserves dans la section Limitations.

---

# 10. Référence [11] toujours fragile

La bibliographie indique :

> early access; no DOI at time of writing. 

Si votre article RPL-AER possède maintenant un DOI, cette référence doit être mise à jour.

---

# 11. Taille expérimentale toujours faible

Vous écrivez :

> N=4 measured seeds. 

et :

> N≥20 recommended before confirmatory tests. 

Donc vous reconnaissez vous-même que l'étude est exploratoire.

Pour IEEE IoT Journal, c'est encore une faiblesse majeure.

---

# 12. Contribution scientifique encore difficile à isoler

Vous reconnaissez explicitement que les ablations :

* WRR-off
* learning-off
* trust-neutral

sont futures. 

Sans ces expériences, il est impossible de savoir :

* ce que WRR apporte réellement ;
* ce que γ apporte ;
* ce que Trust apporte ;
* ce que Q-learning apporte.

---

# Verdict final (version actuelle)

### Rédaction

**9/10**

### Architecture

**8/10**

### Reproductibilité

**9/10**

### Validation expérimentale

**5/10**

### Risque de rejet IEEE IoT

Le papier n'est plus proche du rejet pour des raisons rédactionnelles.

Le risque principal est désormais **scientifique et expérimental** :

1. Artefact des seeds toujours présent.
2. Figures 4 et 5 potentiellement incohérentes avec Table VII.
3. N=4 seulement.
4. Absence d'ablations.
5. Absence de validation énergétique réelle.
6. Le protocole proposé n'est pas meilleur que RPL_MQoS.

Si vous corrigez uniquement l'artefact expérimental et les incohérences Figures 4–5/Table VII, vous éliminerez probablement plus de 70 % des objections restantes d'un reviewer IEEE IoT Journal.

