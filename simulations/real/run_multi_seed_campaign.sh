#!/usr/bin/env bash
# Multi-seed × multi-channel Cooja campaign (lossless + lossy UDGM).
#
# Runs independent simulations per firmware tag (RPL_STANDARD, RPL_MQOS,
# RPL_AER, AER_MQOS), aggregates CSVs (seed / channel / success_ratio),
# and writes a statistical summary.
#
# Requires: JDK 21, Cooja (tools/cooja), buildable Contiki-NG tree.
#
# Smoke test (~4 min sim × 4 protocols × 2 seeds × 2 channels):
#   NUM_SEEDS=2 SIM_TIMEOUT_MS=60000 ./run_multi_seed_campaign.sh
#
# Manuscript bundle (default: nine seeds, 1800 s, lossless + lossy sr=0.85):
#   ./run_multi_seed_campaign.sh
#   nohup ./run_multi_seed_campaign.sh > logs/multi_seed/campaign_$(date +%Y%m%d_%H%M).log 2>&1 &
#
# Environment variables:
#   NUM_SEEDS=9           seeds for v1.0 paper (20260501..20260508 + anchor 20260512)
#   SEED_BASE=20260501    first seed; following = BASE+1 … BASE+NUM_SEEDS-1
#   SEEDS="20260512 42"   explicit list (overrides NUM_SEEDS/SEED_BASE)
#   LOSSY_RATIO=0.85      UDGM success_ratio for the lossy channel
#   CHANNELS=lossless,lossy channels to run
#   SIM_TIMEOUT_MS=1800000 simulated Cooja duration per run (ms)
#   RESUME=1              skip runs whose log already contains METRIC,TX
#   DRY_RUN=1             print plan without launching Cooja
#   FORCE_REPARSE=1       regenerate CSVs even if present
#
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
REAL="$(cd "$(dirname "$0")" && pwd)"
RUN_ONE="$REAL/run_campaigns.sh"
ANALYZE_PY="$ROOT/Section-tex/scripts/analyze_multi_seed_stats.py"

NUM_SEEDS="${NUM_SEEDS:-9}"
SEED_BASE="${SEED_BASE:-20260501}"
LOSSY_RATIO="${LOSSY_RATIO:-0.85}"
CHANNELS="${CHANNELS:-lossless,lossy}"
SIM_TIMEOUT_MS="${SIM_TIMEOUT_MS:-1800000}"
RESUME="${RESUME:-1}"
DRY_RUN="${DRY_RUN:-0}"
FORCE_REPARSE="${FORCE_REPARSE:-0}"

LOGDIR="${LOGDIR:-$ROOT/simulations/real/logs/multi_seed}"
SIMDIR="${SIMDIR:-$ROOT/Section-tex/sim/multi_seed}"
MANIFEST="${MANIFEST:-$LOGDIR/campaign_manifest.tsv}"

mkdir -p "$LOGDIR" "$SIMDIR"

if [[ ! -x "$RUN_ONE" ]]; then
  chmod +x "$RUN_ONE"
fi

# --- Liste des graines ---
declare -a SEED_LIST=()
if [[ -n "${SEEDS:-}" ]]; then
  # shellcheck disable=SC2206
  SEED_LIST=($SEEDS)
else
  for ((i = 0; i < NUM_SEEDS; i++)); do
    SEED_LIST+=($((SEED_BASE + i)))
  done
fi

# Inclure la graine archivée de l'article si absente de la liste auto-générée
ARCHIVED_SEED=20260512
found_archived=0
for s in "${SEED_LIST[@]}"; do
  if [[ "$s" -eq "$ARCHIVED_SEED" ]]; then
    found_archived=1
    break
  fi
done
if [[ "$found_archived" -eq 0 && -z "${SEEDS:-}" ]]; then
  SEED_LIST+=("$ARCHIVED_SEED")
fi

# --- Canaux (lossless / lossy) ---
declare -a CH_LIST=()
IFS=',' read -r -a CH_LIST <<<"$CHANNELS"

log_suffix_for_channel () {
  local ch="$1"
  local sr="$2"
  if [[ "$ch" == "lossless" && ( "$sr" == "1.0" || "$sr" == "1" ) ]]; then
    echo ""
  else
    echo "_ch${ch}"
  fi
}

sr_for_channel () {
  local ch="$1"
  if [[ "$ch" == "lossless" ]]; then
    echo "1.0"
  else
    echo "$LOSSY_RATIO"
  fi
}

run_complete () {
  local variant="$1"
  local seed="$2"
  local suffix="$3"
  local log="$LOGDIR/${variant}_seed${seed}${suffix}.log"
  [[ -f "$log" ]] && grep -q '^METRIC,TX' "$log" 2>/dev/null
}

count_planned=0
count_skip=0
for ch in "${CH_LIST[@]}"; do
  sr="$(sr_for_channel "$ch")"
  sfx="$(log_suffix_for_channel "$ch" "$sr")"
  for seed in "${SEED_LIST[@]}"; do
  for v in RPL_STANDARD RPL_MQOS RPL_AER AER_MQOS; do
    count_planned=$((count_planned + 1))
    if [[ "$RESUME" == "1" ]] && run_complete "$v" "$seed" "$sfx"; then
      count_skip=$((count_skip + 1))
    fi
  done
  done
done

echo "=== AER-MQoS multi-seed campaign ==="
echo "  Seeds (${#SEED_LIST[@]}): ${SEED_LIST[*]}"
echo "  Channels: ${CH_LIST[*]} (lossy ratio=${LOSSY_RATIO})"
echo "  Sim timeout: ${SIM_TIMEOUT_MS} ms"
echo "  Logs: $LOGDIR"
echo "  CSV out: $SIMDIR"
echo "  Planned Cooja runs: $count_planned (skip resume: $count_skip)"
echo ""

if [[ "$DRY_RUN" == "1" ]]; then
  echo "[DRY_RUN] No simulation started."
  for ch in "${CH_LIST[@]}"; do
    sr="$(sr_for_channel "$ch")"
    sfx="$(log_suffix_for_channel "$ch" "$sr")"
    for seed in "${SEED_LIST[@]}"; do
      echo "  channel=$ch sr=$sr seed=$seed -> run_campaigns.sh (4 firmwares)"
    done
  done
  exit 0
fi

# Manifeste TSV (reproductibilité)
{
  echo -e "timestamp\tchannel\tsuccess_ratio\tseed\tvariant\tstatus\tlog_path"
} >"$MANIFEST"

campaign_start="$(date -Iseconds)"
total_runs=0
failed_runs=0

for ch in "${CH_LIST[@]}"; do
  sr="$(sr_for_channel "$ch")"
  sfx="$(log_suffix_for_channel "$ch" "$sr")"
  for seed in "${SEED_LIST[@]}"; do
    echo ""
    echo ">>> channel=$ch success_ratio=$sr seed=$seed"
    all_done=1
    for v in RPL_STANDARD RPL_MQOS RPL_AER AER_MQOS; do
      if [[ "$RESUME" == "1" ]] && run_complete "$v" "$seed" "$sfx"; then
        echo "    [skip] $v (log OK)"
        printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
          "$(date -Iseconds)" "$ch" "$sr" "$seed" "$v" "skipped" \
          "$LOGDIR/${v}_seed${seed}${sfx}.log" >>"$MANIFEST"
        continue
      fi
      all_done=0
    done
    if [[ "$all_done" -eq 1 ]]; then
      echo "    All four firmware logs present — skip Cooja batch."
      continue
    fi

    total_runs=$((total_runs + 1))
    CSC="$REAL/aer-real-25-hybrid-${seed}${sfx}.csc"
    export SEED="$seed"
    export CHANNEL="$ch"
    export SUCCESS_RATIO_TX="$sr"
    export SUCCESS_RATIO_RX="$sr"
    export LOG_TAG_SUFFIX="$sfx"
    export LOGDIR
    export SIMDIR
    export SIM_TIMEOUT_MS
    export CSC
    export SKIP_PARSE=1

    if ! "$RUN_ONE"; then
      echo "ERROR: run_campaigns failed for channel=$ch seed=$seed" >&2
      failed_runs=$((failed_runs + 1))
      for v in RPL_STANDARD RPL_MQOS RPL_AER AER_MQOS; do
        st="failed"
        if run_complete "$v" "$seed" "$sfx"; then
          st="ok"
        fi
        printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
          "$(date -Iseconds)" "$ch" "$sr" "$seed" "$v" "$st" \
          "$LOGDIR/${v}_seed${seed}${sfx}.log" >>"$MANIFEST"
      done
      continue
    fi

    for v in RPL_STANDARD RPL_MQOS RPL_AER AER_MQOS; do
      st="ok"
      if ! run_complete "$v" "$seed" "$sfx"; then
        st="incomplete"
      fi
      printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
        "$(date -Iseconds)" "$ch" "$sr" "$seed" "$v" "$st" \
        "$LOGDIR/${v}_seed${seed}${sfx}.log" >>"$MANIFEST"
    done
  done
done

echo ""
echo "=== Parsing all logs -> $SIMDIR ==="
PY="$ROOT/Section-tex/scripts/parse_cooja_logs.py"
if [[ "$FORCE_REPARSE" == "1" ]]; then
  rm -f "$SIMDIR"/*.csv
fi
first_parse=1
parsed=0
for ch in "${CH_LIST[@]}"; do
  sr="$(sr_for_channel "$ch")"
  sfx="$(log_suffix_for_channel "$ch" "$sr")"
  for seed in "${SEED_LIST[@]}"; do
    for v in RPL_STANDARD RPL_MQOS RPL_AER AER_MQOS; do
      f="$LOGDIR/${v}_seed${seed}${sfx}.log"
      if [[ ! -f "$f" ]] || ! grep -q '^METRIC,TX' "$f" 2>/dev/null; then
        echo "  [warn] missing metrics: $f" >&2
        continue
      fi
      extra=(--channel "$ch" --success-ratio "$sr")
      if [[ "$first_parse" -eq 1 ]]; then
        python3 "$PY" --in "$f" --protocol "$v" --seed "$seed" --out-dir "$SIMDIR" \
          "${extra[@]}" --no-append
        first_parse=0
      else
        python3 "$PY" --in "$f" --protocol "$v" --seed "$seed" --out-dir "$SIMDIR" \
          "${extra[@]}"
      fi
      parsed=$((parsed + 1))
    done
  done
done
echo "  Parsed $parsed log files."

if [[ -f "$ANALYZE_PY" ]]; then
  echo ""
  echo "=== Statistical summary ==="
  python3 "$ANALYZE_PY" --sim-dir "$SIMDIR" --out-dir "$SIMDIR/stats"
else
  echo "  (analyze_multi_seed_stats.py not found — skip summary)"
fi

campaign_end="$(date -Iseconds)"
echo ""
echo "=== Campaign finished ==="
echo "  Started:  $campaign_start"
echo "  Ended:    $campaign_end"
echo "  Batches:  $total_runs launched ($failed_runs failed)"
echo "  Manifest: $MANIFEST"
echo "  CSV:      $SIMDIR"
echo ""
echo "Next: review $SIMDIR/stats/summary_table.csv and regenerate figures with:"
echo "  python3 $ROOT/Section-tex/scripts/generate_figures_matplotlib.py --from-csv $SIMDIR"
