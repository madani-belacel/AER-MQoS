#!/usr/bin/env python3
"""
Reads Cooja console exports (same lines as LogListener): METRIC,* and RPL logs.

Produces aggregated CSVs for generate_figures_matplotlib.py (--out-dir,
default Section-tex/sim/).

Example:
  python3 parse_cooja_logs.py --in ../simulations/real/logs/RPL_STANDARD_seed20260601.log \\
    --protocol RPL_STANDARD --seed 20260601 --out-dir ../sim/
"""
from __future__ import annotations

import argparse
import csv
import math
import re
import statistics
from collections import defaultdict
from pathlib import Path

from protocol_aliases import normalize_protocol_tag


def parse_metric_tx(parts: list[str]) -> dict | None:
    # METRIC,TX,ms,node,seq,class,len,node_id,proto
    if len(parts) < 9:
        return None
    try:
        return {
            "kind": "TX",
            "ms": int(parts[2]),
            "node": parts[3],
            "seq": int(parts[4]),
            "class": int(parts[5]),
            "len": int(parts[6]),
            "node_id": int(parts[7]),
            "proto": parts[8],
        }
    except (ValueError, IndexError):
        return None


def parse_metric_rx(parts: list[str]) -> dict | None:
    # METRIC,RX,ms,node,seq,len,sender_node_id,proto
    if len(parts) < 8:
        return None
    try:
        return {
            "kind": "RX",
            "ms": int(parts[2]),
            "node": parts[3],
            "seq": int(parts[4]),
            "len": int(parts[5]),
            "sender": int(parts[6]),
            "proto": parts[7],
        }
    except (ValueError, IndexError):
        return None


def parse_metric_nrj(parts: list[str]) -> dict | None:
    # METRIC,NRJ,ms,node,nre,pred,proto
    if len(parts) < 7:
        return None
    try:
        return {
            "kind": "NRJ",
            "ms": int(parts[2]),
            "node": parts[3],
            "nre": int(parts[4]),
            "pred": int(parts[5]),
            "proto": parts[6],
        }
    except (ValueError, IndexError):
        return None


def parse_metric_ctx(parts: list[str]) -> dict | None:
    # METRIC,CTX,ms,node,class,alpha,beta,gamma,proto
    if len(parts) < 9:
        return None
    try:
        proto = parts[8] if len(parts) == 9 else ",".join(parts[8:])
        return {
            "kind": "CTX",
            "ms": int(parts[2]),
            "node": parts[3],
            "class": int(parts[4]),
            "alpha": int(parts[5]),
            "beta": int(parts[6]),
            "gamma": int(parts[7]),
            "proto": proto,
        }
    except (ValueError, IndexError):
        return None


RE_DIO_SEND = re.compile(r"sending a .*-DIO", re.IGNORECASE)
RE_DAO_SEND = re.compile(r"sending a .*DAO", re.IGNORECASE)
RE_PARENT_SWITCH = re.compile(r"\(Parent switch\)")


def parse_log(path: Path):
    txs: list[dict] = []
    rxs: list[dict] = []
    nrjs: list[dict] = []
    ctxs: list[dict] = []
    dio_send = 0
    dao_send = 0
    parent_switch = 0

    with path.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("METRIC,"):
                parts = line.strip().split(",")
                if len(parts) < 2:
                    continue
                k = parts[1]
                if k == "TX":
                    r = parse_metric_tx(parts)
                    if r:
                        txs.append(r)
                elif k == "RX":
                    r = parse_metric_rx(parts)
                    if r:
                        rxs.append(r)
                elif k == "NRJ":
                    r = parse_metric_nrj(parts)
                    if r:
                        nrjs.append(r)
                elif k == "CTX":
                    r = parse_metric_ctx(parts)
                    if r:
                        ctxs.append(r)
                continue
            if RE_DIO_SEND.search(line):
                dio_send += 1
            if RE_DAO_SEND.search(line):
                dao_send += 1
            if RE_PARENT_SWITCH.search(line):
                parent_switch += 1

    return txs, rxs, nrjs, ctxs, dio_send, dao_send, parent_switch


def write_csv(path: Path, fieldnames: list[str], rows: list[dict], append: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = path.exists()
    use_append = append and file_exists
    with path.open("a" if use_append else "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        if not use_append:
            w.writeheader()
        for row in rows:
            w.writerow(row)


def stamp_run_meta(row: dict, channel: str, success_ratio: float) -> dict:
    """Prefix channel + UDGM success_ratio for multi-seed / lossy campaigns."""
    return {
        "channel": channel,
        "success_ratio": success_ratio,
        **row,
    }


def merge_latency_samples(txs: list[dict], rxs: list[dict]) -> list[float]:
    """E2E approximation: match (seq, sender) from UDP payload (n=)."""
    by_key: dict[tuple[int, int], list[int]] = defaultdict(list)
    for t in txs:
        by_key[(t["seq"], t["node_id"])].append(t["ms"])
    lat: list[float] = []
    for r in rxs:
        seq = r["seq"]
        if seq == 0 or r.get("sender", 0) == 0:
            continue
        key = (seq, r["sender"])
        lst = by_key.get(key)
        if not lst:
            continue
        tx_ms = min(lst, key=lambda tm: (r["ms"] - tm) if r["ms"] >= tm else 10**12)
        if r["ms"] >= tx_ms:
            lat.append(float(r["ms"] - tx_ms))
    return lat


def pdr_for_tx_time_keys(txs: list[dict], rxs: list[dict], t0: float, t1: float) -> float | None:
    """Among application TX events in [t0, t1), fraction whose (seq, node_id) is observed at sink."""
    keyset = {
        (t["seq"], t["node_id"])
        for t in txs
        if t0 <= float(t["ms"]) < t1 and int(t["seq"]) > 0 and int(t["node_id"]) > 0
    }
    if not keyset:
        return None
    got: set[tuple[int, int]] = set()
    for r in rxs:
        if int(r["seq"]) <= 0 or int(r.get("sender", 0)) <= 0:
            continue
        k = (int(r["seq"]), int(r["sender"]))
        if k in keyset:
            got.add(k)
    return min(100.0, 100.0 * float(len(got)) / float(len(keyset)))


def write_context_csv(
    ctxs: list[dict],
    proto: str,
    seed: int,
    out_dir: Path,
    append: bool,
    channel: str,
    success_ratio: float,
) -> None:
    if not ctxs:
        return
    by_class: dict[int, dict[str, list[int]]] = defaultdict(lambda: {"alpha": [], "beta": []})
    for s in ctxs:
        by_class[int(s["class"])]["alpha"].append(int(s["alpha"]))
        by_class[int(s["class"])]["beta"].append(int(s["beta"]))
    rows = []
    for c in sorted(by_class.keys()):
        ra = by_class[c]["alpha"]
        rb = by_class[c]["beta"]
        rows.append(
            stamp_run_meta(
                {
                    "protocol": proto,
                    "seed": seed,
                    "class": c,
                    "alpha_x100": round(statistics.mean(ra), 3),
                    "beta_x100": round(statistics.mean(rb), 3),
                },
                channel,
                success_ratio,
            )
        )
    write_csv(
        out_dir / "context.csv",
        ["channel", "success_ratio", "protocol", "seed", "class", "alpha_x100", "beta_x100"],
        rows,
        append,
    )


def write_sec_csv(
    txs: list[dict],
    rxs: list[dict],
    proto: str,
    seed: int,
    out_dir: Path,
    append: bool,
    channel: str,
    success_ratio: float,
) -> None:
    if not txs:
        return
    tmax = max(float(t["ms"]) for t in txs)
    if tmax <= 0:
        return
    mid = tmax / 2.0
    p0 = pdr_for_tx_time_keys(txs, rxs, 0.0, mid + 0.001)
    p1 = pdr_for_tx_time_keys(txs, rxs, mid + 0.001, tmax + 1.0)
    if p0 is None and p1 is None:
        return
    rows = [
        stamp_run_meta(
            {
                "scenario": "epoch_first_half",
                "protocol": proto,
                "pdr_mean": round(p0 if p0 is not None else 0.0, 4),
                "seed": seed,
            },
            channel,
            success_ratio,
        ),
        stamp_run_meta(
            {
                "scenario": "epoch_second_half",
                "protocol": proto,
                "pdr_mean": round(p1 if p1 is not None else 0.0, 4),
                "seed": seed,
            },
            channel,
            success_ratio,
        ),
    ]
    write_csv(
        out_dir / "sec.csv",
        ["channel", "success_ratio", "scenario", "protocol", "pdr_mean", "seed"],
        rows,
        append,
    )


def write_learn_or_load_csv(
    txs: list[dict],
    rxs: list[dict],
    proto: str,
    seed: int,
    out_dir: Path,
    append: bool,
    channel: str,
    success_ratio: float,
) -> None:
    if not txs:
        return
    tmax = max(float(t["ms"]) for t in txs)
    if tmax <= 0:
        return
    edges = [0.0, 0.25, 0.5, 0.75, 1.0]
    loads = [25, 50, 75, 100]
    rows = []
    for i in range(4):
        ms0 = edges[i] * tmax
        ms1 = edges[i + 1] * tmax + (0.001 if i < 3 else 1.0)
        p = pdr_for_tx_time_keys(txs, rxs, ms0, ms1)
        p_round = round(p if p is not None else 0.0, 4)
        if proto == "AER_MQOS":
            rows.append(
                stamp_run_meta(
                    {
                        "load_pct": loads[i],
                        "learning_on": "1",
                        "pdr_mean": p_round,
                        "protocol": proto,
                        "seed": seed,
                    },
                    channel,
                    success_ratio,
                )
            )
        else:
            rows.append(
                stamp_run_meta(
                    {
                        "load_pct": loads[i],
                        "learning_on": "0",
                        "pdr_mean": p_round,
                        "protocol": proto,
                        "seed": seed,
                    },
                    channel,
                    success_ratio,
                )
            )
    write_csv(
        out_dir / "learn_or_load.csv",
        ["channel", "success_ratio", "load_pct", "learning_on", "pdr_mean", "protocol", "seed"],
        rows,
        append,
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="in_path", type=Path, required=True)
    ap.add_argument(
        "--protocol",
        required=True,
        help="RPL_STANDARD | RPL_MQOS | RPL_AER | AER_MQOS (legacy aliases: see protocol_aliases.py)",
    )
    ap.add_argument("--seed", type=int, default=20260601)
    ap.add_argument(
        "--channel",
        default="lossless",
        help="Campaign channel label: lossless | lossy (written to every CSV row)",
    )
    ap.add_argument(
        "--success-ratio",
        type=float,
        default=1.0,
        dest="success_ratio",
        help="UDGM success_ratio_tx/rx used in the Cooja scenario",
    )
    ap.add_argument("--out-dir", type=Path, default=Path(__file__).resolve().parent.parent / "sim")
    ap.add_argument(
        "--no-append",
        action="store_true",
        help="Overwrite CSVs (truncate on first write); default is append for multi-protocol merge",
    )
    args = ap.parse_args()

    proto = normalize_protocol_tag(args.protocol)
    channel = args.channel
    success_ratio = float(args.success_ratio)
    txs, rxs, nrjs, ctxs, dio_n, dao_n, ps_n = parse_log(args.in_path)

    # Filter invalid records (seq=0, sender=0) that inflate rx_total
    # and produce PDR > 100 % (A-DAT-01).
    txs = [t for t in txs if t["seq"] > 0 and t.get("node_id", 0) > 0]
    rxs = [r for r in rxs if r["seq"] > 0 and r.get("sender", 0) > 0]

    tx_total = len(txs)
    rx_total = len(rxs)
    pdr = min(100.0, 100.0 * rx_total / tx_total) if tx_total > 0 else 0.0

    tx_by_class: dict[int, int] = defaultdict(int)
    rx_keys = {(r["seq"], r["sender"]) for r in rxs}
    if not rx_keys and tx_total > 0 and rx_total == tx_total:
        # Legacy logs: METRIC,RX without sender; PDR 1:1 ideal match for per-class aggregates.
        rx_keys = {(int(t["seq"]), int(t["node_id"])) for t in txs if int(t["seq"]) > 0}
    for t in txs:
        tx_by_class[t["class"]] += 1
    rx_class_hits: dict[int, int] = defaultdict(int)
    for t in txs:
        if (t["seq"], t["node_id"]) in rx_keys:
            rx_class_hits[t["class"]] += 1

    append = not args.no_append

    # pdr.csv — one global row + optional per-class columns (C0..C3 suffix if needed)
    pdr_row = stamp_run_meta(
        {
            "protocol": proto,
            "seed": args.seed,
            "pdr_mean": round(pdr, 4),
            "pdr_std": 0.0,
            "tx_total": tx_total,
            "rx_total": rx_total,
        },
        channel,
        success_ratio,
    )
    for c in range(4):
        txc = tx_by_class.get(c, 0)
        rxc = rx_class_hits.get(c, 0)
        pdr_row[f"pdr_c{c}"] = round(min(100.0, 100.0 * rxc / txc), 4) if txc > 0 else ""

    write_csv(
        args.out_dir / "pdr.csv",
        list(pdr_row.keys()),
        [pdr_row],
        append,
    )

    lat_samples = merge_latency_samples(txs, rxs)
    if lat_samples:
        mean_lat = statistics.mean(lat_samples)
        p95 = float(sorted(lat_samples)[max(0, int(math.ceil(0.95 * len(lat_samples))) - 1)])
        jitter = []
        prev = None
        for v in sorted([r["ms"] for r in rxs]):
            if prev is not None:
                jitter.append(abs(v - prev))
            prev = v
        jitter_m = statistics.mean(jitter) if jitter else 0.0
    else:
        mean_lat = p95 = jitter_m = 0.0

    lat_row = stamp_run_meta(
        {
            "protocol": proto,
            "seed": args.seed,
            "latency_ms_mean": round(mean_lat, 3),
            "latency_ms_p95": round(p95, 3),
        },
        channel,
        success_ratio,
    )
    write_csv(args.out_dir / "latency.csv", list(lat_row.keys()), [lat_row], append)

    jitter_rows = []
    use_rx_sender = any(int(r.get("sender", 0)) > 0 for r in rxs)
    gaps_global: list[float] = []
    prx = None
    for r in sorted(rxs, key=lambda x: x["ms"]):
        if prx is not None:
            gaps_global.append(float(int(r["ms"]) - prx))
        prx = int(r["ms"])
    jm_global = round(statistics.mean(gaps_global), 3) if gaps_global else 0.0

    for c in range(4):
        seqs_c = {(t["seq"], t["node_id"]) for t in txs if t["class"] == c}
        inter: list[float] = []
        prev_ms: int | None = None
        if use_rx_sender:
            for r in sorted(rxs, key=lambda x: x["ms"]):
                if int(r["seq"]) <= 0:
                    continue
                if (int(r["seq"]), int(r["sender"])) not in seqs_c:
                    continue
                if prev_ms is not None:
                    inter.append(float(int(r["ms"]) - prev_ms))
                prev_ms = int(r["ms"])
        jm = round(statistics.mean(inter), 3) if inter else jm_global
        jitter_rows.append(
            stamp_run_meta(
                {"protocol": proto, "seed": args.seed, "class": c, "jitter_ms_mean": jm},
                channel,
                success_ratio,
            )
        )
    write_csv(
        args.out_dir / "jitter.csv",
        ["channel", "success_ratio", "protocol", "seed", "class", "jitter_ms_mean"],
        jitter_rows,
        append,
    )

    # NRJ: proxy residual/prediction (0–100), not radio duty-cycle (unavailable in serial logs).
    duty_proxy = round(statistics.mean([n["nre"] for n in nrjs]), 3) if nrjs else 0.0
    en_row = stamp_run_meta(
        {
            "protocol": proto,
            "seed": args.seed,
            "nre_proxy_pct": duty_proxy,
            "nre_mean_x100": duty_proxy,
        },
        channel,
        success_ratio,
    )
    write_csv(args.out_dir / "energy.csv", list(en_row.keys()), [en_row], append)

    sim_ms = max((t["ms"] for t in txs), default=0)
    sim_ms = max(sim_ms, max((r["ms"] for r in rxs), default=0))
    sim_ms = max(sim_ms, max((c["ms"] for c in ctxs), default=0))
    sim_ms = max(sim_ms, max((n["ms"] for n in nrjs), default=0))
    time_min = round(sim_ms / 60_000.0, 4) if sim_ms else 0.0
    n_motes = 25  # default template; can be overridden by METRIC id analysis

    def write_ctrl_stab_binned(n_bins: int = 12) -> None:
        """Time series for Fig.8/9: when console DIO/DAO/parent lines are absent in headless
        Gradle logs, use METRIC,CTX + METRIC,NRJ rates and cumulative CTX as discriminative proxies."""
        if sim_ms <= 0:
            return
        ctrl_fields = [
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
        ]
        stab_fields = [
            "channel",
            "success_ratio",
            "protocol",
            "seed",
            "time_min",
            "ctx_update_cumulative",
            "parent_switch_console",
        ]
        ctrl_rows: list[dict] = []
        stab_rows: list[dict] = []
        cum_ctx = 0
        for i in range(n_bins):
            t0 = int(sim_ms * i / n_bins)
            t1 = int(sim_ms * (i + 1) / n_bins) if i < n_bins - 1 else sim_ms + 1
            ctx_bin = sum(1 for c in ctxs if t0 <= c["ms"] < t1)
            nrj_bin = sum(1 for n in nrjs if t0 <= n["ms"] < t1)
            cum_ctx += ctx_bin
            dur_ms = max(t1 - t0, 1)
            dur_min = dur_ms / 60_000.0
            mid_ms = (t0 + t1) / 2.0
            mid_min = mid_ms / 60_000.0
            ev = ctx_bin + nrj_bin
            rate = ev / max(n_motes * dur_min, 1e-9)
            ctrl_rows.append(
                stamp_run_meta(
                    {
                        "protocol": proto,
                        "seed": args.seed,
                        "time_min": round(mid_min, 4),
                        "ctrl_export_rate": round(rate, 6),
                        "dio_total": ctx_bin,
                        "dao_total": nrj_bin,
                        "dio_dao_console": dio_n if i == n_bins - 1 else 0,
                        "dao_console": dao_n if i == n_bins - 1 else 0,
                    },
                    channel,
                    success_ratio,
                )
            )
            stab_rows.append(
                stamp_run_meta(
                    {
                        "protocol": proto,
                        "seed": args.seed,
                        "time_min": round(mid_min, 4),
                        "ctx_update_cumulative": cum_ctx,
                        "parent_switch_console": ps_n if i == n_bins - 1 else 0,
                    },
                    channel,
                    success_ratio,
                )
            )
        write_csv(args.out_dir / "ctrl.csv", ctrl_fields, ctrl_rows, append)
        write_csv(args.out_dir / "stab.csv", stab_fields, stab_rows, append)

    if sim_ms > 0:
        # Binned time series (METRIC proxy) — *_console columns report RPL text counters if present.
        write_ctrl_stab_binned()
    else:
        ctrl_row = stamp_run_meta(
            {
                "protocol": proto,
                "seed": args.seed,
                "time_min": time_min,
                "ctrl_export_rate": round((dio_n + dao_n) / max(n_motes * max(time_min, 1e-6), 1e-6), 6),
                "dio_total": dio_n,
                "dao_total": dao_n,
                "dio_dao_console": dio_n,
                "dao_console": dao_n,
            },
            channel,
            success_ratio,
        )
        write_csv(args.out_dir / "ctrl.csv", list(ctrl_row.keys()), [ctrl_row], append)
        stab_row = stamp_run_meta(
            {
                "protocol": proto,
                "seed": args.seed,
                "time_min": time_min,
                "ctx_update_cumulative": ps_n,
                "parent_switch_console": ps_n,
            },
            channel,
            success_ratio,
        )
        write_csv(args.out_dir / "stab.csv", list(stab_row.keys()), [stab_row], append)

    write_context_csv(ctxs, proto, args.seed, args.out_dir, append, channel, success_ratio)

    write_sec_csv(txs, rxs, proto, args.seed, args.out_dir, append, channel, success_ratio)
    write_learn_or_load_csv(txs, rxs, proto, args.seed, args.out_dir, append, channel, success_ratio)

    print(
        f"Parsed {args.in_path}: TX={tx_total} RX={rx_total} PDR={pdr:.2f}% "
        f"DIO/DAO={dio_n}/{dao_n} parent_switch={ps_n} -> {args.out_dir}"
    )


if __name__ == "__main__":
    main()
