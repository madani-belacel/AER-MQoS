#!/usr/bin/env bash
# Build the 4 firmware variants (same application binary, OF/MRHOF per Makefile) then launch Cooja
# headless on the .csc template (ScriptRunner TIMEOUT = simulated duration in ms).
#
# Usage :
#   ./run_campaigns.sh                    # 1800 s sim / protocol, logs in ./logs/
#   SIM_TIMEOUT_MS=60000 ./run_campaigns.sh   # short campaign (60 s sim)
#
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PROJECT_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
CODE="$ROOT/code_source_AER_MQoS"
LOGDIR="${LOGDIR:-$ROOT/simulations/real/logs}"
CSC="${CSC:-$ROOT/simulations/real/aer-real-25-hybrid-20260601.csc}"
CONTIKI="${CONTIKI:-$(cd "$PROJECT_ROOT/../.." && pwd)}"
COOJA_DIR="${COOJA_DIR:-$CONTIKI/tools/cooja}"
if ! command -v java &>/dev/null; then
  echo "Java not found. Install JDK 21+ or set JAVA_HOME." >&2
  exit 1
fi
if [ -z "${JAVA_HOME:-}" ]; then
  JAVA_HOME="$(java -XshowSettings:java -version 2>&1 | awk -F'=' '/java\.home/{gsub(/[ \t]/, "", $2); print $2}')" || true
  JAVA_HOME="${JAVA_HOME:-/usr/lib/jvm/java-21-openjdk-amd64}"
fi
export JAVA_HOME

SIM_TIMEOUT_MS="${SIM_TIMEOUT_MS:-1800000}"
SEED="${SEED:-20260601}"
SUCCESS_RATIO_TX="${SUCCESS_RATIO_TX:-1.0}"
SUCCESS_RATIO_RX="${SUCCESS_RATIO_RX:-$SUCCESS_RATIO_TX}"
TX_RANGE="${TX_RANGE:-35.0}"
RX_RANGE="${RX_RANGE:-70.0}"
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
SIMDIR="${SIMDIR:-$PROJECT_ROOT/Section-tex/sim}"
SKIP_PARSE="${SKIP_PARSE:-0}"

mkdir -p "$LOGDIR"

# Align ScriptRunner TIMEOUT of .csc with SIM_TIMEOUT_MS (ms of simulated time).
GEN_PY="$ROOT/simulations/real/gen_csc_hybrid25.py"
if [[ -f "$GEN_PY" ]]; then
  python3 "$GEN_PY" --out "$CSC" --sim-timeout-ms "$SIM_TIMEOUT_MS" --seed "$SEED" \
    --success-ratio-tx "$SUCCESS_RATIO_TX" --success-ratio-rx "$SUCCESS_RATIO_RX" \
    --tx-range "$TX_RANGE" --rx-range "$RX_RANGE" || {
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
      ${AER_EXTRA_CFLAGS:+AER_EXTRA_CFLAGS="$AER_EXTRA_CFLAGS"} \
      TARGET=cooja )
}

  # In --no-gui mode, Cooja does not start VisPlugin (LogListener included). However, printf
  # remains visible in LogScriptEngine: we record METRIC,* via log.append() in ScriptRunner (gen_csc_hybrid25.py).
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
    print("run_campaigns: @@METRICS_PATH@@ missing from .csc (regenerate with gen_csc_hybrid25.py)", file=sys.stderr)
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
  # Cooja re-invokes make: inject the same variant/METRIC tag as the preceding build.
  local aer_extra="${AER_EXTRA_CFLAGS:+ AER_EXTRA_CFLAGS=}${AER_EXTRA_CFLAGS:-}"
  sed "s|\$(MAKE) -j\$(CPUS) AER-MQoS-node.cooja|\$(MAKE) -j\$(CPUS) AER_PROTOCOL_VARIANT=${variant} AER_CONF_CAMPAIGN_METRICS=1 AER_CAMPAIGN_PROTO_TAG=${tag}${aer_extra} AER-MQoS-node.cooja|" \
    "$CSC" >"$tmpcsc"
  patch_metrics_placeholder "$tmpcsc" "$metrics"
  # Resolve relative paths before cd into COOJA_DIR
  local abs_logdir; abs_logdir="$(cd "$LOGDIR" && pwd)"
  local abs_tmpcsc; abs_tmpcsc="$(cd "$(dirname "$tmpcsc")" && pwd)/$(basename "$tmpcsc")"
  local abs_metrics; abs_metrics="$(cd "$(dirname "$metrics")" && pwd)/$(basename "$metrics")"
  ( cd "$COOJA_DIR" && ./gradlew -q run --args="--no-gui --autostart --logdir=$abs_logdir --contiki=$CONTIKI $abs_tmpcsc --random-seed=$SEED" ) >"$log" 2>&1 || {
    echo "Cooja run failed for $variant (see $log)" >&2
    return 1
  }
  merge_metrics_to_gradle_log "$log" "$abs_metrics"
}

# Paper order: baseline MRHOF, RPLMQoS-style, AER-RPL-style, AER-MQoS
build_variant RPL_STANDARD RPL_STANDARD
run_cooja RPL_STANDARD RPL_STANDARD

build_variant RPL_MQOS RPL_MQOS
run_cooja RPL_MQOS RPL_MQOS

build_variant RPL_AER RPL_AER
run_cooja RPL_AER RPL_AER

build_variant AER-MQoS AER-MQoS
run_cooja AER-MQoS AER-MQoS

echo "Done. Logs under $LOGDIR"

if [[ "$SKIP_PARSE" != "1" ]]; then
  PY="$ROOT/Section-tex/scripts/parse_cooja_logs.py"
  first=1
  for v in RPL_STANDARD RPL_MQOS RPL_AER AER-MQoS; do
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
