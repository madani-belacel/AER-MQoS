# Gabarit Cooja AER-MQoS

Fichier : **`AER-MQoS-3nodes-template.csc`**.

- **Paramètres à ajuster à la main (ou par script)** : balise `<title>` (y noter `PROTO`, `SEED`, `TOPO`), `<randomseed>`, coordonnées `<x>/<y>` des motes, et éventuellement `transmitting_range` / `interference_range` pour densité « modérée » vs « stressée ».
- **`[CONTIKI_DIR]`** : Cooja le substitue par le répertoire Contiki-NG utilisé au lancement ; le chemin source pointe vers `examples/projet_madani/AER-MQoS/code_source_AER_MQoS/AER-MQoS-node.c`.
- **Compilation du mote** : la commande `$(MAKE) -j$(CPUS) AER-MQoS-node.cooja TARGET=cooja` s’exécute depuis le répertoire parent du fichier source (le dossier `code_source_AER_MQoS`), comme pour les exemples officiels.

Pour **dupliquer** le scénario vers d’autres tailles de réseau : dans Cooja, « Add motes » avec le même type, ou copier-coller les blocs `<mote>` en conservant des positions cohérentes avec la portée UDGM.

Pour les **autres protocoles** (MRHOF, RPLMQoS-style, AER-RPL-style), le `.csc` doit référencer **le fichier `.c` principal** et la **cible `make …cooja`** du projet correspondant ; voir `../README_CAMPAIGNS.md`.
