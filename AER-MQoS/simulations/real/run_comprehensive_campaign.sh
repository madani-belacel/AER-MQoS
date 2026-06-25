#!/usr/bin/env bash
# Comprehensive AER-MQoS campaign: runs ALL 12 sim-required experiments.
#
# Usage:
#   nohup ./run_comprehensive_campaign.sh > campaign_$(date +%Y%m%d_%H%M).log 2>&1 &
#
# Experiments:
#   1.  baseline+lossless  (N=20 seeds, fixed artefact, lossy+lossless)
#   2.  ablations          (A1 WRR-off, A2 learning-off, A3 trust-neutral)
#   3.  energest           (same as baseline + Energest traces)
#   4.  attack             (selective forwarding + rank anomaly)
#   5.  stress             (higher traffic load)
#   6.  topology           (50 + 100 nodes)
#
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
REAL="$(cd "$(dirname "$0")" && pwd)"
CODE="$ROOT/code_source_AER_MQoS"
MULTI="$REAL/run_multi_seed_campaign.sh"
ANALYZE="$ROOT/Section-tex/scripts/analyze_multi_seed_stats.py"
PARSE="$ROOT/Section-tex/scripts/parse_cooja_logs.py"

START_TS="$(date -Iseconds)"
echo "=== AER-MQoS Comprehensive Campaign ==="
echo "Started: $START_TS"
echo ""

# --- Config ---
NUM_SEEDS=20
export RESUME=1
export SIM_TIMEOUT_MS=1800000
export SKIP_PARSE=1  # defer parsing to end

# ============================================================
# 1. BASELINE + LOSSLESS (AC-1, AC-7, AM-6)
# ============================================================
echo "=========================================="
echo "1. BASELINE CAMPAIGN (N=${NUM_SEEDS}, lossy + lossless)"
echo "=========================================="

export LOSSY_RATIO=0.85
export CHANNELS=lossless,lossy
export NUM_SEEDS
export LOGDIR="$REAL/logs/comprehensive/baseline"
export SIMDIR="$ROOT/Section-tex/sim/comprehensive/baseline"
mkdir -p "$LOGDIR" "$SIMDIR"
bash "$MULTI" 2>&1 | tee "$LOGDIR/baseline_campaign.log"

# ============================================================
# 2. ABLATIONS A1-A3 (AC-8)
# ============================================================
echo "=========================================="
echo "2. ABLATIONS (lossy only)"
echo "=========================================="

export CHANNELS=lossy
export LOSSY_RATIO=0.85
export NUM_SEEDS

run_ablation() {
  local name="$1"
  local extra_cflags="$2"
  echo "--- Ablation: $name ---"
  export LOGDIR="$REAL/logs/comprehensive/ablation_${name}"
  export SIMDIR="$ROOT/Section-tex/sim/comprehensive/ablation_${name}"
  mkdir -p "$LOGDIR" "$SIMDIR"
  (cd "$CODE" && make clean >/dev/null)
  export AER_EXTRA_CFLAGS="$extra_cflags"
  bash "$MULTI" 2>&1 | tee "$LOGDIR/campaign.log"
  unset AER_EXTRA_CFLAGS
}

run_ablation "A1_wrroff" "-DAER_CONF_WRR_ENABLED=0"
run_ablation "A2_learnoff" "-DAER_CONF_QLEARN_ENABLED=0"
run_ablation "A3_trustneutral" "-DAER_CONF_TRUST_ENABLED=0 -DAER_CONF_TRUST_WEIGHT_NEUTRAL=1"

# ============================================================
# 3. ENERGET (AC-9)
# ============================================================
echo "=========================================="
echo "3. ENERGET TRACES"
echo "=========================================="
export LOGDIR="$REAL/logs/comprehensive/energest"
export SIMDIR="$ROOT/Section-tex/sim/comprehensive/energest"
mkdir -p "$LOGDIR" "$SIMDIR"
export CHANNELS=lossy
export LOSSY_RATIO=0.85
export NUM_SEEDS
(cd "$CODE" && make clean >/dev/null)
export AER_EXTRA_CFLAGS="-DAER_CONF_ENERGEST_ENABLED=1 -DCONTIKIMAC_CONF_ENABLED=1"
bash "$MULTI" 2>&1 | tee "$LOGDIR/campaign.log"
unset AER_EXTRA_CFLAGS

# ============================================================
# 4. ATTACK SCENARIOS (AC-10)
# ============================================================
echo "=========================================="
echo "4. ATTACK INJECTIONS"
echo "=========================================="
export CHANNELS=lossy
export LOSSY_RATIO=0.85
export NUM_SEEDS

for attack_type in selective_forwarding rank_anomaly mixed; do
  echo "--- Attack type: $attack_type ---"
  LOGDIR="$REAL/logs/comprehensive/attack/${attack_type}"
  SIMDIR="$ROOT/Section-tex/sim/comprehensive/attack/${attack_type}"
  mkdir -p "$LOGDIR" "$SIMDIR"
  for seed in $(seq 20260601 $((20260600 + NUM_SEEDS - 1))); do
    CSC="$REAL/csc_attack/aer-attack-25-${attack_type}.csc"
    # gen per-seed CSC with correct random seed
    python3 "$REAL/gen_csc_attack.py" --attack "$attack_type" \
      --seed "$seed" --out "/tmp/aer_attack_${attack_type}_${seed}.csc"
    SEED="$seed" CSC="/tmp/aer_attack_${attack_type}_${seed}.csc" \
      LOGDIR="$LOGDIR" SIMDIR="$SIMDIR" \
      bash "$REAL/run_campaigns.sh" 2>&1 | \
      tee -a "$LOGDIR/attack_${attack_type}_seed${seed}.log"
    rm -f "/tmp/aer_attack_${attack_type}_${seed}.csc"
  done
done

# ============================================================
# 5. STRESS / HIGHER TRAFFIC LOAD (AC-13)
# ============================================================
echo "=========================================="
echo "5. STRESS TEST (higher traffic load)"
echo "=========================================="
export CHANNELS=lossy
export LOSSY_RATIO=0.85
export NUM_SEEDS

for load_pct in 200 400; do
  echo "--- Traffic load: ${load_pct}% ---"
  LOGDIR="$REAL/logs/comprehensive/stress/load${load_pct}"
  SIMDIR="$ROOT/Section-tex/sim/comprehensive/stress/load${load_pct}"
  mkdir -p "$LOGDIR" "$SIMDIR"
  (cd "$CODE" && make clean >/dev/null)
  export AER_EXTRA_CFLAGS="-DAER_CONF_TRAFFIC_LOAD_PCT=${load_pct}"
  bash "$MULTI" 2>&1 | tee "$LOGDIR/campaign.log"
done
unset AER_EXTRA_CFLAGS

# ============================================================
# 6. TOPOLOGY SCALE (50 + 100 nodes) (AM-1)
# ============================================================
echo "=========================================="
echo "6. TOPOLOGY SCALE (50 + 100 nodes)"
echo "=========================================="
export CHANNELS=lossy
export LOSSY_RATIO=0.85
export NUM_SEEDS

for size in 50 100; do
  echo "--- Topology: ${size} nodes ---"
  LOGDIR="$REAL/logs/comprehensive/topology/${size}"
  SIMDIR="$ROOT/Section-tex/sim/comprehensive/topology/${size}"
  mkdir -p "$LOGDIR" "$SIMDIR"
  for seed in $(seq 20260601 $((20260600 + NUM_SEEDS - 1))); do
    python3 "$REAL/gen_csc_topology.py" --n-motes "$size" \
      --seed "$seed" --out "/tmp/aer_topology_${size}_${seed}.csc"
    SEED="$seed" CSC="/tmp/aer_topology_${size}_${seed}.csc" \
      LOGDIR="$LOGDIR" SIMDIR="$SIMDIR" \
      bash "$REAL/run_campaigns.sh" 2>&1 | \
      tee -a "$LOGDIR/topology${size}_seed${seed}.log"
    rm -f "/tmp/aer_topology_${size}_${seed}.csc"
  done
done

# ============================================================
# PARSE ALL LOGS
# ============================================================
echo "=========================================="
echo "PARSING ALL LOGS"
echo "=========================================="
for simdir in "$ROOT/Section-tex/sim/comprehensive"/*/; do
  echo "--- Parsing: $simdir ---"
  find "$simdir" -name '*.log' -path '*/logs/*' | while read -r logfile; do
    if grep -q '^METRIC,TX' "$logfile" 2>/dev/null; then
      python3 "$PARSE" --in "$logfile" \
        --protocol "$(basename "$logfile" | cut -d_ -f1)" \
        --seed "$(echo "$logfile" | grep -oP 'seed\d+' | grep -oP '\d+')" \
        --out-dir "$simdir" 2>/dev/null || true
    fi
  done
done

# ============================================================
# STATISTICAL TESTS
# ============================================================
echo "=========================================="
echo "MANN-WHITNEY TESTS"
echo "=========================================="
for simdir in "$ROOT/Section-tex/sim/comprehensive"/*/; do
  if [[ -f "$simdir/pdr.csv" ]]; then
    python3 "$ROOT/Section-tex/scripts/mannwhitney_test.py" \
      --sim-dir "$simdir" --out-dir "$simdir/stats" 2>/dev/null || true
  fi
done

# ============================================================
# SUMMARY
# ============================================================
echo ""
echo "=========================================="
echo "CAMPAIGN COMPLETE"
echo "=========================================="
echo "Started: $START_TS"
echo "Ended:   $(date -Iseconds)"
echo ""
echo "Figure regeneration:"
echo "  python3 $ROOT/Section-tex/scripts/generate_figures_matplotlib.py --from-csv $ROOT/Section-tex/sim/comprehensive/baseline"
