#!/bin/sh
# Affiche les commandes de compilation Cooja pour les 4 variantes de l'article.
# Seul le dépôt AER-MQoS (ce Makefile) couvre la variante intégrée ; les autres profils = autres arborescences.

CONTIKI="${CONTIKI:-$(cd "$(dirname "$0")/../../../../../../" && pwd)}"
AER_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
BELACEL="${BELACEL:-$CONTIKI/examples/projet_madani/RPLMQoS_BELACEL}"
AER_MAIN="${AER_MAIN:-$CONTIKI/examples/projet_madani/RPL-AER-main}"
RPL_UDP="${RPL_UDP:-$CONTIKI/examples/autres/rpl-udp}"

usage() {
  echo "Usage: $0 [mrhof | mqos_style | aer_style | aer_mqos]"
  echo "CONTIKI=$CONTIKI"
  echo "BELACEL=$BELACEL"
  echo "AER_MAIN=$AER_MAIN"
  echo "RPL_UDP=$RPL_UDP"
  echo ""
  echo "Profiles:"
  echo "  mrhof       — RPL MRHOF stock : exemple udp-client / udp-server (Contiki-NG)."
  echo "  mqos_style  — Dépôt BELACEL : adapter Makefile/chemins (fork rpl_parent_t étendu)."
  echo "  aer_style   — Dépôt RPL-AER-main : udp-client + sink selon leur README."
  echo "  aer_mqos — Ce répertoire : AER-MQoS-node.c, OF OCP 8 (AER-MQoS)."
}

case "$1" in
  mrhof)
    echo "# --- RPL standard (MRHOF) + UDP ---"
    echo "cd \"$RPL_UDP\""
    echo "make clean && make udp-server.cooja TARGET=cooja && make udp-client.cooja TARGET=cooja"
    echo "# Cooja : motetype serveur = udp-server.c, clients = udp-client.c (cf. examples/autres/rpl-udp/rpl-udp-cooja.csc)"
    ;;
  mqos_style)
    echo "# --- RPLMQoS-style (BELACEL) ---"
    echo "cd \"$BELACEL\""
    echo "# Vérifier le Makefile / cible .cooja du projet (souvent rpl-mqos-example)."
    echo "make clean && make TARGET=cooja   # ou la cible documentée dans ce dépôt"
    ;;
  aer_style)
    echo "# --- AER-RPL-style (RPL-AER-main) ---"
    echo "cd \"$AER_MAIN\""
    echo "# Compiler udp-client + rpl-aer-sink selon instructions du dépôt (Cooja)."
    echo "make clean && make TARGET=cooja   # adapter si Makefile différent"
    ;;
  aer_mqos)
    echo "# --- AER-MQoS (intégration article) ---"
    echo "cd \"$AER_DIR\""
    echo "make clean && make TARGET=cooja"
    echo "# Logs METRIC optionnels :"
    echo "make AER_CONF_CAMPAIGN_METRICS=1 AER_CAMPAIGN_PROTO_TAG=AER_MQOS TARGET=cooja"
    ;;
  "")
    usage
    ;;
  *)
    usage
    exit 1
    ;;
esac
