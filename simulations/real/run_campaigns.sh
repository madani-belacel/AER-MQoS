#!/usr/bin/env bash
# Compile les 4 variantes (même binaire applicatif, OF / MRHOF selon Makefile) puis lance Cooja
# en mode headless sur le gabarit .csc (ScriptRunner TIMEOUT = durée simulée en ms).
#
# Usage :
#   ./run_campaigns.sh                    # 1800 s sim / protocole, logs dans ./logs/
#   SIM_TIMEOUT_MS=60000 ./run_campaigns.sh   # campagne courte (60 s sim)
#
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
CODE="$ROOT/code_source_AER_MQoS"
LOGDIR="${LOGDIR:-$ROOT/simulations/real/logs}"
CSC="${CSC:-$ROOT/simulations/real/aer-real-25-hybrid-20260512.csc}"
CONTIKI="${CONTIKI:-$ROOT/../../..}"
COOJA_DIR="${COOJA_DIR:-$CONTIKI/tools/cooja}"
JAVA_HOME="${JAVA_HOME:-/usr/lib/jvm/java-21-openjdk-amd64}"
export JAVA_HOME

SIM_TIMEOUT_MS="${SIM_TIMEOUT_MS:-1800000}"
SEED="${SEED:-20260512}"
SUCCESS_RATIO_TX="${SUCCESS_RATIO_TX:-1.0}"
SUCCESS_RATIO_RX="${SUCCESS_RATIO_RX:-$SUCCESS_RATIO_TX}"
# lossless | lossy — suffixe des logs et colonne CSV (multi-seed)
CHANNEL="${CHANNEL:-lossless}"
if [[ "$SUCCESS_RATIO_TX" != "1.0" && "$SUCCESS_RATIO_TX" != "1" && "$CHANNEL" == "lossless" ]]; then
  CHANNEL="lossy"
fi
if [[ -z "${LOG_TAG_SUFFIX+x}" ]]; then
  if [[ "$CHANNEL" == "lossless" && ( "$SUCCESS_RATIO_TX" == "1.0" || "$SUCCESS_RATIO_TX" == "1" ) ]]; then
    LOG_TAG_SUFFIX=""
  else
    LOG_TAG_SUFFIX="_ch${CHANNEL}"
  fi
fi
SIMDIR="${SIMDIR:-$ROOT/Section-tex/sim}"
SKIP_PARSE="${SKIP_PARSE:-0}"

mkdir -p "$LOGDIR"

# Aligner le TIMEOUT ScriptRunner du .csc sur SIM_TIMEOUT_MS (ms de temps simulé).
GEN_PY="$ROOT/simulations/real/gen_csc_hybrid25.py"
if [[ -f "$GEN_PY" ]]; then
  python3 "$GEN_PY" --out "$CSC" --sim-timeout-ms "$SIM_TIMEOUT_MS" --seed "$SEED" \
    --success-ratio-tx "$SUCCESS_RATIO_TX" --success-ratio-rx "$SUCCESS_RATIO_RX" || {
    echo "Failed to regenerate CSC with timeout ${SIM_TIMEOUT_MS} ms" >&2
    exit 1
  }
fi

if [[ ! -f "$CSC" ]]; then
  echo "Missing CSC: $CSC" >&2
  exit 1
fi

build_variant () {
  local variant="$1"
  local tag="$2"
  echo "=== build $variant (METRIC tag=$tag) ==="
  ( cd "$CODE" && make clean >/dev/null && \
    make -j"$(nproc)" \
      AER_PROTOCOL_VARIANT="$variant" \
      AER_CONF_CAMPAIGN_METRICS=1 \
      AER_CAMPAIGN_PROTO_TAG="$tag" \
      TARGET=cooja )
}

# En --no-gui, Cooja ne démarre pas les VisPlugin (dont LogListener). Les printf sont
# toutefois visibles dans LogScriptEngine : on enregistre METRIC,* via log.append() dans le ScriptRunner (gen_csc_hybrid25.py).
patch_metrics_placeholder () {
  local tmpcsc="$1"
  local metrics_file="$2"
  python3 - "$tmpcsc" "$metrics_file" <<'PY'
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
metrics = pathlib.Path(sys.argv[2])
raw = path.read_text(encoding="utf-8")
ap = str(metrics.resolve()).replace("\\", "\\\\").replace("'", "\\'")
if "@@METRICS_PATH@@" not in raw:
    print("run_campaigns: @@METRICS_PATH@@ absent du .csc (régénérer avec gen_csc_hybrid25.py)", file=sys.stderr)
    sys.exit(1)
path.write_text(raw.replace("@@METRICS_PATH@@", ap, 1), encoding="utf-8")
PY
}

merge_metrics_to_gradle_log () {
  local log="$1"
  local metrics="$2"
  if [[ ! -f "$metrics" ]] || [[ ! -s "$metrics" ]]; then
    return 0
  fi
  {
    echo ""
    echo "===== ScriptRunner METRICS (merged for parse_cooja_logs) ====="
    cat "$metrics"
  } >>"$log"
}

run_cooja () {
  local variant="$1"
  local tag="$2"
  local log="$LOGDIR/${variant}_seed${SEED}${LOG_TAG_SUFFIX}.log"
  local tmpcsc="$LOGDIR/_run_${variant}_${SEED}${LOG_TAG_SUFFIX}.csc"
  local metrics="$LOGDIR/metrics_${variant}_seed${SEED}${LOG_TAG_SUFFIX}.log"
  echo "=== Cooja $variant -> $log (timeout ${SIM_TIMEOUT_MS} ms sim) ==="
  if [[ ! -d "$COOJA_DIR" ]]; then
    echo "Cooja not found at $COOJA_DIR" >&2
    exit 1
  fi
  : >"$metrics"
  # Cooja relance make : injecter la même variante / METRIC tag que le build précédent.
  sed "s|\$(MAKE) -j\$(CPUS) AER-MQoS-node.cooja|\$(MAKE) -j\$(CPUS) AER_PROTOCOL_VARIANT=${variant} AER_CONF_CAMPAIGN_METRICS=1 AER_CAMPAIGN_PROTO_TAG=${tag} AER-MQoS-node.cooja|" \
    "$CSC" >"$tmpcsc"
  patch_metrics_placeholder "$tmpcsc" "$metrics"
  ( cd "$COOJA_DIR" && ./gradlew -q run --args="--no-gui --autostart --logdir=$LOGDIR --contiki=$CONTIKI \"$tmpcsc\",random-seed=$SEED" ) >"$log" 2>&1 || {
    echo "Cooja run failed for $variant (see $log)" >&2
    return 1
  }
  merge_metrics_to_gradle_log "$log" "$metrics"
}

# Ordre article : baseline MRHOF, RPLMQoS-style, AER-RPL-style, AER-MQoS
build_variant RPL_STANDARD RPL_STANDARD
run_cooja RPL_STANDARD RPL_STANDARD

build_variant RPL_MQOS RPL_MQOS
run_cooja RPL_MQOS RPL_MQOS

build_variant RPL_AER RPL_AER
run_cooja RPL_AER RPL_AER

build_variant AER_MQOS AER_MQOS
run_cooja AER_MQOS AER_MQOS

echo "Done. Logs under $LOGDIR"

if [[ "$SKIP_PARSE" != "1" ]]; then
  PY="$ROOT/Section-tex/scripts/parse_cooja_logs.py"
  first=1
  for v in RPL_STANDARD RPL_MQOS RPL_AER AER_MQOS; do
    f="$LOGDIR/${v}_seed${SEED}${LOG_TAG_SUFFIX}.log"
    if [[ -f "$f" ]] && [[ -s "$f" ]] && grep -q '^METRIC,TX' "$f" 2>/dev/null; then
      parse_extra=(--channel "$CHANNEL" --success-ratio "$SUCCESS_RATIO_TX")
      if [[ "$first" -eq 1 ]]; then
        python3 "$PY" --in "$f" --protocol "$v" --seed "$SEED" --out-dir "$SIMDIR" \
          "${parse_extra[@]}" --no-append
        first=0
      else
        python3 "$PY" --in "$f" --protocol "$v" --seed "$SEED" --out-dir "$SIMDIR" \
          "${parse_extra[@]}"
      fi
    else
      echo "Skip parse: missing or empty $f" >&2
    fi
  done
fi
