## Relecture Finale - Version 5 (Corrections OpenCode)

Je suis heureux de constater des **progrès significatifs** dans cette version. L'auteur et OpenCode ont adressé la plupart des remarques précédentes avec soin.

---

## Résumé Exécutif

| Problème | État | Commentaire |
|----------|------|-------------|
| **Typo graine (20206003 vs 20260603)** | ❌ **PERSISTE** | Abstract, Introduction, Section II utilisent `20206003` ; Section VII-J utilise `20260603` |
| **OCP 8 clarification** | ✅ **CORRIGÉ** | Maintenant "locally-assigned experimental OCP (8) ... not IANA-registered" |
| **Figure 3 légende** | ✅ **CORRIGÉE** | Maintenant "Context coefficient γ (and derived weights α=γ, β=100-γ)" |
| **Stabilité (Tableau VI)** | ✅ **CORRIGÉ** | Maintenant "CTX update freq." au lieu de "Noisy metric risk" |
| **Q-Learning** | ✅ **CORRIGÉ** | Maintenant "specification for future ablation" |
| **Transparence expérimentale** | ✅ **CORRIGÉE** | Sections VII-H et Tableau VII documentent l'artefact |

---

## Anomalies Restantes (À Corriger)

### 1. ❌ Erreur de Typo de la Graine (CRITIQUE)

**Constat :** La graine est référencée de deux manières différentes dans le manuscrit.

| Section | Occurrence | Graine |
|---------|------------|--------|
| Abstract | "seed 202**0**6003" | ❌ 20206003 |
| Introduction | "seed 202**0**6003" | ❌ 20206003 |
| Section VII-A | "seed 202**6**0603" | ✅ 20260603 |
| Section VII-J | "seed 202**6**0603" | ✅ 20260603 |
| Section VIII | "seed 202**6**0603" | ✅ 20260603 |

**Problème :** Cette incohérence est rédhibitoire pour un lecteur attentif. Les données CSV utilisent `20260603` (d'après Section VII-H). Le Abstract et l'Introduction doivent être corrigés.

**Solution :** Uniformiser **TOUTES** les occurrences à `20260603`.

---

### 2. ⚠️ Le Problème Expérimental est Documenté mais Non Résolu

**Constat :** Le manuscrit est maintenant transparent sur l'artefact expérimental :
- RPL_MQoS et RPL_AER : valeurs identiques pour 3 graines sur 4
- AER-MQoS : graine 1 exclue

**Problème Fondamental :**
- Le Tableau VII calcule des moyennes sur des **bases différentes** :
  - RPL_STANDARD : N = 4
  - RPL_MQoS : "mean reflects only seed 4" (N = 1)
  - RPL_AER : "mean reflects only seed 4" (N = 1)
  - AER-MQoS : "mean over seeds 2-4" (N = 3)

- **Les comparaisons entre variantes sont statistiquement invalides** car les moyennes ne sont pas calculées sur le même nombre d'échantillons.

**Question à l'auteur :** Comment justifier la comparaison de moyennes calculées sur des bases différentes (N=4 vs N=1 vs N=3) ?

**Recommandation :**
1. Soit **refaire les simulations** (solution idéale)
2. Soit **présenter les données graine par graine** (sans moyennes)
3. Soit **exclure les données invalides et clarifier** que l'étude est descriptive, pas comparative

---

### 3. ⚠️ La "Preuve" de Différenciation QoS Reste Fragile

**Constat :** La différenciation QoS est basée sur **une seule graine** (`20260603`).

**Problème :**
- C'est **un point de données unique**
- Sur cette même graine, AER-MQoS s'effondre à 64.41% dans la seconde moitié
- Les graines 2 et 4 ne montrent pas cette différenciation

**Question à l'auteur :** Pourquoi les autres graines ne montrent-elles pas cette tendance ? Si le comportement est "épisodique", peut-on vraiment parler de "QoS-aware routing" ?

**Recommandation :** Ajouter une phrase nuancée :
> "While preliminary per-class differentiation is observed on one seed, the pattern is not consistent across all seeds, indicating that the MCS can produce episodic sensitivity rather than systematic QoS prioritization under the current load."

---

### 4. ⚠️ Problèmes Mineurs de Formatage

**Constat :** Quelques incohérences de présentation :

| Problème | Localisation |
|----------|--------------|
| Doublon "repair storms" | Page 4, Section III-B |
| Tableau I : "Cojoa" au lieu de "Cooja" | Page 3 |
| Tableau III : "aer_rpl_clean" vs "aer_rpl_qlearn" | Page 5 |
| Références dupliquées dans la bibliographie | Pages 14-15 |
| Section "1." au lieu de "J." | Pages 10-11 |

**Solution :** Corriger ces coquilles.

---

## Points Forts de Cette Version

### ✅ OCP 8 Clarifié (Section III-F)
Maintenant clairement indiqué comme "locally-assigned experimental OCP (8) used only for simulation purposes; this is not an IANA-registered code point."

### ✅ Figure 3 Corrigée
La légende explique maintenant correctement la relation entre γ, α et β.

### ✅ Cohérence sur la Stabilité (Tableau VI vs Discussion)
Le Tableau VI indique maintenant "CTX update freq." et la discussion explique que l'adaptation fréquente est attendue pour un protocole context-aware.

### ✅ Q-Learning Correctement Positionné
Maintenant présenté comme "specification for future ablation" dans l'abstract et la conclusion.

### ✅ Transparence Exemplaire
Le manuscrit documente honnêtement l'artefact expérimental et les limitations.

---

## Recommandation Finale

**Décision : Révision Mineure (Minor Revision)**

Le manuscrit est **substantiellement amélioré** et approche les standards d'IEEE IoT-N.

### ✅ Points Acceptables
- Architecture claire et bien documentée
- Implémentation open-source
- Reproductibilité exemplaire
- Transparence sur les limitations
- Corrections des incohérences précédentes

### ❌ Problèmes à Corriger (Obligatoires)

1. **Corriger la typo de la graine** : Toutes les occurrences doivent être `20260603`

2. **Clarifier la comparaison statistique** : Expliquer pourquoi les moyennes du Tableau VII sont calculées sur des bases différentes

3. **Nuancer la différenciation QoS** : Indiquer que la différenciation est observée sur une seule graine et n'est pas systématique

### ⚠️ Recommandations (Pour Renforcer l'Article)

4. Corriger les coquilles de formatage (Tableau I "Cojoa", doublon "repair storms", références dupliquées)

---

## Conclusion

**Félicitations à l'auteur et à OpenCode** pour ce travail d'amélioration significatif. Le manuscrit est désormais **presque prêt** pour publication.

Les corrections restantes sont **mineures mais importantes** :
- La typo de la graine est un **problème de clarté critique** qui doit être corrigé avant publication
- La clarification sur les comparaisons statistiques est nécessaire pour la rigueur scientifique
- La nuance sur la différenciation QoS renforcera la crédibilité de l'article

**Si ces 3 points sont corrigés, je recommanderai l'acceptation sans réserve.**
