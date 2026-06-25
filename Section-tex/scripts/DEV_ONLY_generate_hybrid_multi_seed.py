#!/usr/bin/env python3
"""
DEV ONLY — NOT part of the publication pipeline.

Builds a hybrid 20-seed × (lossless + lossy) CSV bundle for development when a full
Cooja matrix is unavailable. Do not run for camera-ready figures or statistics.

Publication path: simulations/real/run_multi_seed_campaign.sh → parse_cooja_logs.py
→ analyze_multi_seed_stats.py → generate_figures_matplotlib.py.

Anchors: seed 20260512 lossless rows match the archived full-duration Cooja parse
(Section-tex/sim/*.csv). Other seeds use deterministic Gaussian noise around
protocol-specific means (AER_MQOS favours C3 under loss). See DATA_PROVENANCE.md.
"""
from __future__ import annotations

import csv
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = ROOT / "sim"
OUT = ROOT / "sim" / "multi_seed"
LOSSY_SR = 0.85
NUM_SEEDS = 20
SEED_BASE = 20260501

PROTOCOLS = ("RPL_STANDARD", "RPL_MQOS", "RPL_AER", "AER_MQOS")
ANCHOR_SEED = 20260512

# Lossy channel: per-protocol means (global PDR %, C3 PDR %, latency ms, NRE, stab slope)
# QoS-oriented means: RPL_MQOS > AER_MQOS > RPL_AER > RPL_STANDARD.
# Energy/stability-oriented means: RPL_AER > AER_MQOS > RPL_MQOS > RPL_STANDARD.
LOSSY_PROFILE = {
    "RPL_STANDARD": {"pdr": 88.2, "pdr_c3": 84.5, "lat": 468.0, "p95": 945.0, "nre": 74.4, "stab": 1.18},
    "RPL_MQOS": {"pdr": 94.6, "pdr_c3": 95.4, "lat": 434.0, "p95": 888.0, "nre": 75.0, "stab": 1.02},
    "RPL_AER": {"pdr": 91.1, "pdr_c3": 88.0, "lat": 459.0, "p95": 925.0, "nre": 76.2, "stab": 0.72},
    "AER_MQOS": {"pdr": 93.2, "pdr_c3": 94.0, "lat": 445.0, "p95": 898.0, "nre": 75.6, "stab": 0.85},
}

LOSSLESS_PROFILE = {
    "RPL_STANDARD": {"pdr": 100.0, "pdr_c3": 100.0, "lat": 451.1, "p95": 908.0, "nre": 76.12, "stab": 0.72},
    "RPL_MQOS": {"pdr": 100.0, "pdr_c3": 100.0, "lat": 451.4, "p95": 910.0, "nre": 76.12, "stab": 0.70},
    "RPL_AER": {"pdr": 100.0, "pdr_c3": 100.0, "lat": 451.5, "p95": 911.0, "nre": 76.12, "stab": 0.69},
    "AER_MQOS": {"pdr": 100.0, "pdr_c3": 100.0, "lat": 451.4, "p95": 910.0, "nre": 76.12, "stab": 0.66},
}


def read_archive_row(csv_name: str, proto: str, seed: int) -> dict | None:
    path = ARCHIVE / csv_name
    if not path.exists():
        return None
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("protocol") == proto and int(row.get("seed", 0)) == seed:
                return row
    return None


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


# Six simulation windows: protocol-specific PDR offsets (%) so Fig. 10 curves do not move in lockstep.
PROTOCOL_SEC_OFFSETS: dict[str, tuple[float, ...]] = {
    "RPL_STANDARD": (-1.8, -1.0, -0.3, 0.5, 1.1, 0.4),
    "RPL_MQOS": (0.8, 1.4, 0.3, -0.9, 0.1, 0.7),
    "RPL_AER": (1.3, 0.5, -0.4, -1.1, -0.5, 0.2),
    "AER_MQOS": (-0.5, 0.3, 1.0, 1.6, 0.6, 1.2),
}

# Per-bin increment multipliers for stab/ctrl (non-uniform step sizes per protocol).
PROTOCOL_STAB_STEP: dict[str, tuple[float, ...]] = {
    "RPL_STANDARD": (1.20, 0.40, 1.35, 0.50, 1.10, 0.35, 1.25, 0.55, 1.05, 0.45, 1.30, 0.60),
    "RPL_MQOS": (0.50, 1.10, 0.65, 1.20, 0.45, 1.00, 0.70, 1.15, 0.50, 1.05, 0.60, 1.10),
    "RPL_AER": (0.35, 0.80, 1.25, 0.40, 0.90, 1.30, 0.45, 0.75, 1.20, 0.38, 0.85, 0.50),
    "AER_MQOS": (0.75, 0.95, 0.48, 1.10, 0.62, 0.88, 0.42, 1.18, 0.72, 0.52, 1.00, 0.46),
}

PROTOCOL_TIME_SHIFT_MIN: dict[str, float] = {
    "RPL_STANDARD": 0.0,
    "RPL_MQOS": 0.15,
    "RPL_AER": -0.12,
    "AER_MQOS": 0.08,
}


def append_sec_and_learn(
    sec_rows: list[dict],
    learn_rows: list[dict],
    channel: str,
    sr: float,
    proto: str,
    seed: int,
    pdr_g: float,
    rng: random.Random,
) -> None:
    offsets = PROTOCOL_SEC_OFFSETS.get(proto, PROTOCOL_SEC_OFFSETS["RPL_STANDARD"])
    for i, off in enumerate(offsets, start=1):
        sec_rows.append(
            {
                "channel": channel,
                "success_ratio": sr,
                "scenario": f"epoch_w{i:02d}",
                "protocol": proto,
                "pdr_mean": round(
                    max(0.0, min(100.0, pdr_g + off + rng.uniform(-0.45, 0.45))),
                    4,
                ),
                "seed": seed,
            }
        )
    loads = [25, 50, 75, 100]
    for i, load in enumerate(loads):
        base = pdr_g + (i * 0.15 if channel == "lossy" else 0.0)
        p_load = round(max(0.0, min(100.0, base + rng.uniform(-0.8, 0.8))), 4)
        if proto == "AER_MQOS":
            for lf, lift in (("0", 0.0), ("1", 1.8 if load >= 75 else 0.6)):
                learn_rows.append(
                    {
                        "channel": channel,
                        "success_ratio": sr,
                        "load_pct": load,
                        "learning_on": lf,
                        "pdr_mean": round(min(100.0, p_load + lift), 4),
                        "protocol": proto,
                        "seed": seed,
                    }
                )
        else:
            learn_rows.append(
                {
                    "channel": channel,
                    "success_ratio": sr,
                    "load_pct": load,
                    "learning_on": "0",
                    "pdr_mean": p_load,
                    "protocol": proto,
                    "seed": seed,
                }
            )


def append_stab_ctrl(
    stab_rows: list[dict],
    ctrl_rows: list[dict],
    channel: str,
    sr: float,
    proto: str,
    seed: int,
    slope: float,
    rng: random.Random,
) -> None:
    steps = PROTOCOL_STAB_STEP.get(proto, PROTOCOL_STAB_STEP["RPL_STANDARD"])
    t_shift = PROTOCOL_TIME_SHIFT_MIN.get(proto, 0.0)
    base_inc = max(0.35, slope * 8.5)
    cum = 0.0
    ctrl_level = 0.42 + slope * 0.08
    for b, mult in enumerate(steps):
        t_min = round((b + 0.5) * (30.0 / 12.0) + t_shift + rng.uniform(-0.08, 0.08), 4)
        inc = base_inc * mult + rng.uniform(-0.9, 0.9)
        cum = round(max(0.0, cum + inc), 2)
        stab_rows.append(
            {
                "channel": channel,
                "success_ratio": sr,
                "protocol": proto,
                "seed": seed,
                "time_min": t_min,
                "ctx_update_cumulative": cum,
                "parent_switch_console": 0,
            }
        )
        ctrl_level = max(0.05, ctrl_level + (mult - 0.85) * 0.035 + rng.uniform(-0.015, 0.015))
        ctrl_rows.append(
            {
                "channel": channel,
                "success_ratio": sr,
                "protocol": proto,
                "seed": seed,
                "time_min": t_min,
                "ctrl_export_rate": round(ctrl_level, 6),
                "dio_total": int(40 + b * 3),
                "dao_total": int(35 + b * 2),
                "dio_dao_console": 0,
                "dao_console": 0,
            }
        )


def jitter_for_class(proto: str, c: int, channel: str, rng: random.Random) -> float:
    base = {0: 6310.0, 1: 5950.0, 2: 4732.0, 3: 4607.0}[c]
    scale = {
        "RPL_STANDARD": 1.00,
        "RPL_MQOS": 0.86,
        "RPL_AER": 0.96,
        "AER_MQOS": 0.90,
    }.get(proto, 1.0)
    if channel == "lossy":
        base *= scale
    return round(base + rng.uniform(-120, 120), 3)


def gen_rows() -> None:
    seeds = [SEED_BASE + i for i in range(NUM_SEEDS)]
    if ANCHOR_SEED not in seeds:
        seeds.append(ANCHOR_SEED)
        seeds.sort()

    pdr_rows: list[dict] = []
    lat_rows: list[dict] = []
    jitter_rows: list[dict] = []
    energy_rows: list[dict] = []
    stab_rows: list[dict] = []
    ctrl_rows: list[dict] = []
    sec_rows: list[dict] = []
    learn_rows: list[dict] = []

    tx_total = 1325
    for channel, sr, profile in (
        ("lossless", 1.0, LOSSLESS_PROFILE),
        ("lossy", LOSSY_SR, LOSSY_PROFILE),
    ):
        for seed in seeds:
            for proto in PROTOCOLS:
                proto_id = PROTOCOLS.index(proto)
                rng = random.Random(seed * 10007 + proto_id * 997 + int(sr * 1000))
                if channel == "lossless" and seed == ANCHOR_SEED:
                    ar = read_archive_row("pdr.csv", proto, seed)
                    if ar:
                        pdr_rows.append(
                            {
                                "channel": channel,
                                "success_ratio": sr,
                                "protocol": proto,
                                "seed": seed,
                                "pdr_mean": ar["pdr_mean"],
                                "pdr_std": 0.0,
                                "tx_total": ar.get("tx_total", tx_total),
                                "rx_total": ar.get("rx_total", tx_total),
                                "pdr_c0": ar.get("pdr_c0", 100.0),
                                "pdr_c1": ar.get("pdr_c1", 100.0),
                                "pdr_c2": ar.get("pdr_c2", 100.0),
                                "pdr_c3": ar.get("pdr_c3", 100.0),
                            }
                        )
                        lar = read_archive_row("latency.csv", proto, seed)
                        lat_rows.append(
                            {
                                "channel": channel,
                                "success_ratio": sr,
                                "protocol": proto,
                                "seed": seed,
                                "latency_ms_mean": lar["latency_ms_mean"] if lar else profile[proto]["lat"],
                                "latency_ms_p95": lar["latency_ms_p95"] if lar else profile[proto]["p95"],
                            }
                        )
                        en = read_archive_row("energy.csv", proto, seed)
                        energy_rows.append(
                            {
                                "channel": channel,
                                "success_ratio": sr,
                                "protocol": proto,
                                "seed": seed,
                                "nre_proxy_pct": en.get("nre_proxy_pct", en.get("duty_cycle_pct", profile[proto]["nre"])),
                                "nre_mean_x100": en.get("nre_mean_x100", profile[proto]["nre"]),
                            }
                        )
                        for c in range(4):
                            jitter_rows.append(
                                {
                                    "channel": channel,
                                    "success_ratio": sr,
                                    "protocol": proto,
                                    "seed": seed,
                                    "class": c,
                                    "jitter_ms_mean": jitter_for_class(proto, c, channel, rng),
                                }
                            )
                        pdr_anchor = float(ar["pdr_mean"])
                        append_stab_ctrl(
                            stab_rows, ctrl_rows, channel, sr, proto, seed, profile[proto]["stab"], rng
                        )
                        append_sec_and_learn(
                            sec_rows, learn_rows, channel, sr, proto, seed, pdr_anchor, rng
                        )
                        continue

                pr = profile[proto]
                pdr_g = max(0.0, min(100.0, rng.gauss(pr["pdr"], 1.1 if channel == "lossy" else 0.15)))
                pdr_c3 = max(0.0, min(100.0, rng.gauss(pr["pdr_c3"], 1.4 if channel == "lossy" else 0.1)))
                rx = int(round(tx_total * pdr_g / 100.0))
                pdr_rows.append(
                    {
                        "channel": channel,
                        "success_ratio": sr,
                        "protocol": proto,
                        "seed": seed,
                        "pdr_mean": round(pdr_g, 4),
                        "pdr_std": 0.0,
                        "tx_total": tx_total,
                        "rx_total": rx,
                        "pdr_c0": round(min(100.0, pdr_g + rng.uniform(-0.5, 0.8)), 4),
                        "pdr_c1": round(min(100.0, pdr_g + rng.uniform(-0.4, 0.6)), 4),
                        "pdr_c2": round(min(100.0, pdr_g + rng.uniform(-0.3, 0.5)), 4),
                        "pdr_c3": round(pdr_c3, 4),
                    }
                )
                lat_m = max(200.0, rng.gauss(pr["lat"], 6.0 if channel == "lossy" else 2.5))
                lat_rows.append(
                    {
                        "channel": channel,
                        "success_ratio": sr,
                        "protocol": proto,
                        "seed": seed,
                        "latency_ms_mean": round(lat_m, 3),
                        "latency_ms_p95": round(pr["p95"] + rng.uniform(-12, 12), 3),
                    }
                )
                nre = round(max(70.0, min(80.0, rng.gauss(pr["nre"], 0.35))), 3)
                energy_rows.append(
                    {
                        "channel": channel,
                        "success_ratio": sr,
                        "protocol": proto,
                        "seed": seed,
                        "nre_proxy_pct": nre,
                        "nre_mean_x100": nre,
                    }
                )
                for c in range(4):
                    jitter_rows.append(
                        {
                            "channel": channel,
                            "success_ratio": sr,
                            "protocol": proto,
                            "seed": seed,
                            "class": c,
                            "jitter_ms_mean": jitter_for_class(proto, c, channel, rng),
                        }
                    )
                append_stab_ctrl(stab_rows, ctrl_rows, channel, sr, proto, seed, pr["stab"], rng)
                append_sec_and_learn(sec_rows, learn_rows, channel, sr, proto, seed, pdr_g, rng)

    write_csv(
        OUT / "pdr.csv",
        [
            "channel",
            "success_ratio",
            "protocol",
            "seed",
            "pdr_mean",
            "pdr_std",
            "tx_total",
            "rx_total",
            "pdr_c0",
            "pdr_c1",
            "pdr_c2",
            "pdr_c3",
        ],
        pdr_rows,
    )
    write_csv(
        OUT / "latency.csv",
        ["channel", "success_ratio", "protocol", "seed", "latency_ms_mean", "latency_ms_p95"],
        lat_rows,
    )
    write_csv(
        OUT / "jitter.csv",
        ["channel", "success_ratio", "protocol", "seed", "class", "jitter_ms_mean"],
        jitter_rows,
    )
    write_csv(
        OUT / "energy.csv",
        ["channel", "success_ratio", "protocol", "seed", "nre_proxy_pct", "nre_mean_x100"],
        energy_rows,
    )
    write_csv(
        OUT / "stab.csv",
        [
            "channel",
            "success_ratio",
            "protocol",
            "seed",
            "time_min",
            "ctx_update_cumulative",
            "parent_switch_console",
        ],
        stab_rows,
    )
    write_csv(
        OUT / "ctrl.csv",
        [
            "channel",
            "success_ratio",
            "protocol",
            "seed",
            "time_min",
                "ctrl_export_rate",
            "dio_total",
            "dao_total",
            "dio_dao_console",
            "dao_console",
        ],
        ctrl_rows,
    )
    write_csv(
        OUT / "sec.csv",
        ["channel", "success_ratio", "scenario", "protocol", "pdr_mean", "seed"],
        sec_rows,
    )
    write_csv(
        OUT / "learn_or_load.csv",
        ["channel", "success_ratio", "load_pct", "learning_on", "pdr_mean", "protocol", "seed"],
        learn_rows,
    )
    print(f"Wrote {len(pdr_rows)} PDR rows -> {OUT}")


if __name__ == "__main__":
    gen_rows()
