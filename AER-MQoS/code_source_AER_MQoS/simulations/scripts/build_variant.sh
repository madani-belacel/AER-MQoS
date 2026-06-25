#!/bin/sh
# Prints Cooja build commands for the 4 paper variants.
# Only the AER-MQoS repository (this Makefile) covers the integrated variant; other profiles = other trees.

CONTIKI="${CONTIKI:-$(cd "$(dirname "$0")/../../../../../../" && pwd)}"
AER_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
BELACEL="${BELACEL:-$CONTIKI/examples/AER-MQoS/AER-MQoS}"
AER_MAIN="${AER_MAIN:-$CONTIKI/examples/AER-MQoS/AER-MQoS}"
RPL_UDP="${RPL_UDP:-$CONTIKI/examples/AER-MQoS/AER-MQoS}"

usage() {
  echo "Usage: $0 [mrhof | mqos_style | aer_style | aer_mqos]"
  echo "CONTIKI=$CONTIKI"
  echo "BELACEL=$BELACEL"
  echo "AER_MAIN=$AER_MAIN"
  echo "RPL_UDP=$RPL_UDP"
  echo ""
  echo "Profiles:"
  echo "  mrhof       — Stock RPL MRHOF: udp-client / udp-server example (Contiki-NG)."
  echo "  mqos_style  — BELACEL repository: adapt Makefile/paths (extended rpl_parent_t fork)."
  echo "  aer_style   — RPL-AER-main repository: udp-client + sink per their README."
  echo "  aer_mqos — This directory: AER-MQoS-node.c, OF OCP 8 (AER-MQoS)."
}

case "$1" in
  mrhof)
    echo "# --- Standard RPL (MRHOF) + UDP ---"
    echo "cd \"$RPL_UDP\""
    echo "make clean && make udp-server.cooja TARGET=cooja && make udp-client.cooja TARGET=cooja"
    echo "# Cooja : motetype serveur = udp-server.c, clients = udp-client.c (cf. examples/autres/rpl-udp/rpl-udp-cooja.csc)"
    ;;
  mqos_style)
    echo "# --- RPLMQoS-style (BELACEL) ---"
    echo "cd \"$BELACEL\""
    echo "# Check the project Makefile/.cooja target (often rpl-mqos-example)."
    echo "make clean && make TARGET=cooja   # or the target documented in this repository"
    ;;
  aer_style)
    echo "# --- AER-RPL-style (RPL-AER-main) ---"
    echo "cd \"$AER_MAIN\""
    echo "# Build udp-client + rpl-aer-sink per repository instructions (Cooja)."
    echo "make clean && make TARGET=cooja   # adapt if Makefile differs"
    ;;
  aer_mqos)
    echo "# --- AER-MQoS (paper integration) ---"
    echo "cd \"$AER_DIR\""
    echo "make clean && make TARGET=cooja"
    echo "# Optional METRIC logs:"
    echo "make AER_CONF_CAMPAIGN_METRICS=1 AER_CAMPAIGN_PROTO_TAG=AER-MQoS TARGET=cooja"
    ;;
  "")
    usage
    ;;
  *)
    usage
    exit 1
    ;;
esac
