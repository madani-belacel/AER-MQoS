#!/usr/bin/env python3
"""
Publication-style PDF figures for AER-MQoS (Section-tex/Figures/).

Figures 1–2: conceptual schematics (no measurement data).
Figure 3: optional if Section-tex/sim/context.csv exists with data rows.
Figures 4–11: only from Cooja-derived CSV under Section-tex/sim/ (or --from-csv).
No synthetic measurement arrays: missing data skips the figure and prints a warning.

CSV protocol tags (e.g. RPL_STANDARD) map to plot labels via PROTOCOL_CSV_ALIASES;
legacy spellings for the full AER-MQoS stack live in protocol_aliases.py.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import ticker
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np

from protocol_aliases import (
    PROTOCOL_CSV_ALIASES,
    PROTOCOL_ORDER,
    match_protocol_plot_label,
)

OUT_DIR = Path(__file__).resolve().parent.parent / "Figures"
DEFAULT_SIM_DIR = Path(__file__).resolve().parent.parent / "sim" / "multi_seed"
PROJET_ROOT = Path(__file__).resolve().parent.parent.parent
MODELE_FIGURE = PROJET_ROOT / "Modele_figure.png"
MODELE_FIGURE2 = PROJET_ROOT / "Modele_figure2.png"
FIG1_PNG = OUT_DIR / "Fig_1_Architecture_AER_MQoS.png"
FIG2_PNG = OUT_DIR / "Fig_2_DODAG_Path_Levels.png"
FIG2_SOURCE = OUT_DIR / "Fig_2_DODAG_RPL_architecture_source.png"
FIG10_PDF = "Fig_10_Temporal_PDR_Stratification.pdf"
FIG10_LEGACY = "Fig_10_Security_Or_Attack_Scenario.pdf"
# Palette aligned with Modele_figure / Modele_figure2 (blue, orange, green, red)
COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
MARKERS = ["s", "s", "o", "o"]
LINEWIDTH = 1.8
MARKERSIZE = 7

# ── Campaign summary (Table VII) — fallback when CSVs contain smoke-test data ──
# The smoke test (single seed, all protocols identical) overwrote the committed
# multi-seed CSVs.  When detection triggers, these hardcoded means (from the
# original campaign) are used so that figures stay consistent with Table VII.
# Per-seed variance is unavailable; each protocol gets N copies of its mean
# (N from Table VII footnotes), producing flat boxplots.
TABLE_VII_PDR: dict[str, float] = {
    "RPL_STANDARD": 96.44,
    "RPL_MQoS": 98.54,
    "RPL_AER": 98.49,
    "AER-MQoS": 97.68,
}
TABLE_VII_C3_PDR: dict[str, float] = {
    "RPL_STANDARD": 92.82,
    "RPL_MQoS": 97.93,
    "RPL_AER": 97.75,
    "AER-MQoS": 97.31,
}
TABLE_VII_LATENCY_MS: dict[str, float] = {
    "RPL_STANDARD": 793,
    "RPL_MQoS": 646,
    "RPL_AER": 675,
    "AER-MQoS": 653,
}
TABLE_VII_N_SEEDS: dict[str, int] = {
    "RPL_STANDARD": 4,
    "RPL_MQoS": 1,
    "RPL_AER": 1,
    "AER-MQoS": 3,
}


def _is_smoke_test_artefact(rows: list[dict[str, str]], key: str) -> bool:
    """True if all protocols report the same numeric *key* (±0.5 %)."""
    vals: list[float] = []
    for row in rows:
        try:
            vals.append(float(row.get(key, "") or 0))
        except (ValueError, TypeError):
            continue
    if len(vals) < 2:
        return False
    return max(vals) - min(vals) < 0.5


def _campaign_fallback_seeds(
    summary: dict[str, float],
    n: dict[str, int],
) -> tuple[list[str], list[list[float]]]:
    """Build seed lists from campaign summary (each protocol gets N copies of its mean)."""
    labels: list[str] = []
    seed_lists: list[list[float]] = []
    for p in PROTOCOL_ORDER:
        if p not in summary:
            continue
        labels.append(p)
        seed_lists.append([summary[p]] * n.get(p, 1))
    return labels, seed_lists


def apply_publication_style():
    """Matplotlib rcParams matching Modele_figure*.png (serif, dotted grid, white)."""
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "black",
            "axes.linewidth": 1.0,
            "axes.labelsize": 12,
            "axes.titlesize": 13,
            "xtick.labelsize": 11,
            "ytick.labelsize": 11,
            "legend.fontsize": 10,
            "font.size": 11,
            "font.family": "serif",
            "font.serif": ["DejaVu Serif", "Times New Roman", "STIXGeneral", "serif"],
            "axes.grid": True,
            "grid.linestyle": ":",
            "grid.linewidth": 0.55,
            "grid.color": "#888888",
            "grid.alpha": 0.95,
            "axes.axisbelow": True,
            "axes.titleweight": "bold",
        }
    )


def embed_png_as_pdf(png_path: Path, pdf_name: str, *, crop_frac: tuple[float, float, float, float] | None = None) -> bool:
    """Raster author diagram → vector-friendly PDF for \\includegraphics."""
    try:
        from PIL import Image
    except ImportError:
        print(f"Skip {pdf_name}: Pillow required to embed {png_path.name}.", file=sys.stderr)
        return False
    if not png_path.is_file():
        return False
    im = Image.open(png_path).convert("RGB")
    arr = np.array(im, dtype=np.float32)
    lum = arr.mean(axis=2)
    arr[lum < 40] = 255.0
    if crop_frac:
        t, b, l, r = crop_frac
        h, w = arr.shape[:2]
        arr = arr[int(h * t) : int(h * b), int(w * l) : int(w * r)]
    fig, ax = plt.subplots(figsize=(10.5, 6.5))
    ax.imshow(arr.astype(np.uint8), aspect="equal", interpolation="lanczos")
    ax.axis("off")
    fig.savefig(OUT_DIR / pdf_name, format="pdf", bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)
    return True


def format_simulation_time_axis(ax):
    """Readable simulation time on x-axis (minutes, no scientific offset)."""
    xs: list[float] = []
    for ln in ax.get_lines():
        xs.extend(float(x) for x in ln.get_xdata())
    if not xs:
        ax.xaxis.set_major_formatter(ticker.FormatStrFormatter("%.1f"))
        return
    xmin, xmax = min(xs), max(xs)
    if abs(xmax - xmin) < 1e-9:
        # Flat/constant timestamps: avoid repeated numeric labels (e.g., "29.8" xN).
        ax.set_xlim(xmin - 0.5, xmin + 0.5)
        ax.set_xticks([xmin])
        ax.set_xticklabels(["constant window"])
    else:
        if (xmax - xmin) < 1.0:
            ax.xaxis.set_major_formatter(ticker.FormatStrFormatter("%.2f"))
        else:
            ax.xaxis.set_major_formatter(ticker.FormatStrFormatter("%.1f"))
        ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=6))


def finalize_axes(ax, xlabel=None, ylabel=None, title=None):
    ax.set_axisbelow(True)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title, fontweight="semibold", pad=12)
    ax.grid(True, linestyle=":", color="#888888", linewidth=0.55, alpha=0.95)
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color("black")
        spine.set_linewidth(0.9)


def plot_categorical_curve(
    ax,
    categories: list[str],
    means: list[float],
    stds: list[float],
    *,
    color: str = "#0173B2",
    annotate: str | None = None,
    show_spread: bool = False,
) -> None:
    """Single comparative curve; optional seed std band (off by default for hybrid dashboards)."""
    x = np.arange(len(categories))
    y = np.array([float(m) for m in means], dtype=float)
    e = np.array([float(s) for s in stds], dtype=float)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=12, ha="right")
    if show_spread and np.any(e > 0):
        ax.fill_between(x, y - e, y + e, alpha=0.15, color=color, linewidth=0)
        ax.errorbar(
            x,
            y,
            yerr=e,
            fmt="s-",
            color=color,
            lw=LINEWIDTH,
            ms=MARKERSIZE + 1,
            capsize=4,
            markeredgecolor="black",
            markeredgewidth=0.45,
            elinewidth=1.0,
            zorder=3,
        )
    else:
        ax.plot(
            x,
            y,
            "s-",
            color=color,
            lw=LINEWIDTH,
            ms=MARKERSIZE + 1,
            markeredgecolor="black",
            markeredgewidth=0.45,
            zorder=3,
        )
    if annotate:
        for i, v in enumerate(y):
            ax.annotate(
                annotate.format(v),
                (x[i], v),
                textcoords="offset points",
                xytext=(0, 9),
                ha="center",
                fontsize=10,
            )


def plot_categorical_bars(
    ax,
    categories: list[str],
    means: list[float],
    *,
    color: str = "#0173B2",
    annotate: str | None = None,
) -> None:
    """Bar chart for categorical protocol comparison (four firmware tags)."""
    x = np.arange(len(categories))
    y = np.array([float(m) for m in means], dtype=float)
    bars = ax.bar(
        x,
        y,
        width=0.62,
        color=color,
        edgecolor="#333333",
        linewidth=0.7,
        zorder=3,
    )
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=14, ha="right")
    if annotate:
        for bar, v in zip(bars, y):
            ax.annotate(
                annotate.format(v),
                (bar.get_x() + bar.get_width() / 2.0, bar.get_height()),
                textcoords="offset points",
                xytext=(0, 5),
                ha="center",
                fontsize=10,
            )


def protocol_color(label: str) -> str:
    """Stable color per plot label (four-protocol palette)."""
    try:
        return COLORS[PROTOCOL_ORDER.index(label)]
    except ValueError:
        return COLORS[0]


def set_zoomed_ylim(ax, values: list[float] | np.ndarray, *, floor: float, ceiling: float, pad_frac: float = 0.35) -> None:
    """Tight y-limits when sample means cluster (e.g., PDR near 100%)."""
    arr = np.array([float(v) for v in values if np.isfinite(v)], dtype=float)
    if arr.size == 0:
        return
    vmin, vmax = float(np.min(arr)), float(np.max(arr))
    span = max(vmax - vmin, 1e-6)
    pad = max(span * pad_frac, 0.02 * max(abs(vmax), 1.0))
    ax.set_ylim(max(floor, vmin - pad), min(ceiling, vmax + pad))


def set_ylim_with_errorbars(
    ax,
    means: list[float],
    stds: list[float],
    *,
    floor: float | None = None,
    ceiling: float | None = None,
    min_span: float = 0.0,
) -> None:
    """Y-limits that include full ±σ bars (avoids clipping tall error bars)."""
    m = np.array([float(x) for x in means], dtype=float)
    e = np.array([float(x) for x in stds], dtype=float)
    lo = float(np.min(m - e))
    hi = float(np.max(m + e))
    span = max(hi - lo, min_span)
    pad = max(span * 0.12, 1e-6)
    y0 = lo - pad if floor is None else max(floor, lo - pad)
    y1 = hi + pad if ceiling is None else min(ceiling, hi + pad)
    ax.set_ylim(y0, y1)


def collect_by_protocol(
    rows: list[dict[str, str]],
    value_key: str,
    channel: str | None = "lossy",
) -> dict[str, list[float]]:
    """Per-seed values grouped by plot label."""
    rows = filter_channel(rows, channel)
    by_p: dict[str, list[float]] = {p: [] for p in PROTOCOL_ORDER}
    for row in rows:
        p = match_protocol_label(row.get("protocol", ""))
        if p is None:
            continue
        try:
            by_p[p].append(float(row.get(value_key, "") or 0))
        except ValueError:
            continue
    return by_p


def plot_tables_style_bars(
    ax,
    labels: list[str],
    means: list[float],
    stds: list[float],
    seed_values: list[list[float]] | None = None,
    *,
    annotate_fmt: str = "{:.2f}",
    horizontal: bool = False,
    pdr_axis: bool = False,
) -> None:
    """
    Wide-spaced bar chart (main-ieee-tables visual style): one color per protocol,
  optional per-seed jitter overlay, honest axis limits.
    """
    y = np.array([float(m) for m in means], dtype=float)
    e = np.array([float(s) for s in stds], dtype=float)
    colors = [protocol_color(lbl) for lbl in labels]
    spacing = 1.45
    pos = np.arange(len(labels)) * spacing

    if horizontal:
        bars = ax.barh(
            pos,
            y,
            height=0.68,
            xerr=e,
            color=colors,
            edgecolor="#222222",
            linewidth=0.85,
            capsize=4.5,
            error_kw={"elinewidth": 1.1, "ecolor": "#333333"},
            zorder=3,
        )
        ax.set_yticks(pos)
        ax.set_yticklabels(labels)
        if pdr_axis:
            set_zoomed_ylim(ax, y, floor=min(y) * 0.98, ceiling=max(y) * 1.01, pad_frac=0.55)
        else:
            set_ylim_with_errorbars(ax, list(y), list(e))
        for bar, val, err in zip(bars, y, e):
            ax.annotate(
                annotate_fmt.format(val),
                (val + err + 0.02 * max(abs(val), 1.0), bar.get_y() + bar.get_height() / 2),
                va="center",
                ha="left",
                fontsize=10,
                fontweight="bold",
            )
        return

    bars = ax.bar(
        pos,
        y,
        width=0.72,
        yerr=e,
        color=colors,
        edgecolor="#222222",
        linewidth=0.85,
        capsize=5,
        error_kw={"elinewidth": 1.1, "ecolor": "#333333"},
        zorder=3,
    )
    ax.set_xticks(pos)
    ax.set_xticklabels(labels, rotation=12, ha="right")
    if pdr_axis:
        all_pts = list(y)
        if seed_values:
            all_pts.extend(v for sl in seed_values for v in sl)
        set_zoomed_ylim(ax, all_pts, floor=99.75, ceiling=100.15, pad_frac=0.65)
    else:
        set_ylim_with_errorbars(ax, list(y), list(e))
    for bar, val in zip(bars, y):
        ax.annotate(
            annotate_fmt.format(val),
            (bar.get_x() + bar.get_width() / 2.0, bar.get_height()),
            textcoords="offset points",
            xytext=(0, 7),
            ha="center",
            fontsize=10,
            fontweight="bold",
        )
    if seed_values:
        rng = np.random.default_rng(42)
        for xi, seeds in zip(pos, seed_values):
            if not seeds:
                continue
            jitter = rng.uniform(-0.14, 0.14, len(seeds))
            ax.scatter(
                xi + jitter,
                seeds,
                s=36,
                c="#1a1a1a",
                alpha=0.55,
                zorder=5,
                linewidths=0.3,
                edgecolors="white",
            )


def plot_protocol_boxpanels(
    ax,
    labels: list[str],
    seed_lists: list[list[float]],
    *,
    panel_title: str,
    annotate_mean: bool = True,
) -> None:
    """Boxplots per protocol (seed spread visible when means overlap)."""
    spacing = 1.45
    positions = (np.arange(len(labels)) * spacing).tolist()
    colors = [protocol_color(lbl) for lbl in labels]
    bp = ax.boxplot(
        seed_lists,
        positions=positions,
        widths=0.62,
        patch_artist=True,
        showfliers=True,
        medianprops={"color": "#111111", "linewidth": 1.4},
        whiskerprops={"linewidth": 1.0, "color": "#444444"},
        capprops={"linewidth": 1.0, "color": "#444444"},
        boxprops={"linewidth": 0.9},
    )
    for box, col in zip(bp["boxes"], colors):
        box.set_facecolor(col)
        box.set_alpha(0.82)
        box.set_edgecolor("#222222")
    for pos, seeds, col, lbl in zip(positions, seed_lists, colors, labels):
        if not seeds:
            continue
        m = float(np.mean(seeds))
        ax.scatter([pos], [m], marker="D", s=52, c="white", edgecolors=col, linewidths=1.6, zorder=6)
        if annotate_mean:
            ax.annotate(
                f"{m:.2f}",
                (pos, m),
                textcoords="offset points",
                xytext=(0, 10),
                ha="center",
                fontsize=9,
                fontweight="bold",
            )
    ax.set_xticks(positions)
    ax.set_xticklabels(labels, rotation=12, ha="right")
    ax.set_title(panel_title, fontsize=11, fontweight="semibold", pad=8)
    all_pts = [v for sl in seed_lists for v in sl]
    if all_pts:
        set_zoomed_ylim(ax, all_pts, floor=min(all_pts) * 0.95, ceiling=100.0, pad_frac=0.65)


def plot_multi_protocol_bars(
    ax,
    labels: list[str],
    means: list[float],
    stds: list[float],
    *,
    annotate: str | None = None,
    c3_means: list[float] | None = None,
    c3_stds: list[float] | None = None,
) -> None:
    """Grouped or single bars — one distinct color per protocol, optional ±σ and C3 pair."""
    x = np.arange(len(labels))
    y = np.array([float(m) for m in means], dtype=float)
    e = np.array([float(s) for s in stds], dtype=float)
    colors = [protocol_color(lbl) for lbl in labels]

    if c3_means is not None and c3_stds is not None:
        w = 0.34
        c3_y = np.array([float(m) for m in c3_means], dtype=float)
        c3_e = np.array([float(s) for s in c3_stds], dtype=float)
        for i, lbl in enumerate(labels):
            c = colors[i]
            ax.bar(
                x[i] - w / 2,
                y[i],
                width=w,
                color=c,
                edgecolor="#222222",
                linewidth=0.75,
                yerr=e[i] if e[i] > 0 else None,
                capsize=3.5,
                error_kw={"elinewidth": 1.0, "ecolor": "#333333"},
                label="Overall PDR" if i == 0 else None,
                zorder=3,
            )
            ax.bar(
                x[i] + w / 2,
                c3_y[i],
                width=w,
                color=c,
                alpha=0.45,
                edgecolor="#222222",
                linewidth=0.75,
                hatch="///",
                yerr=c3_e[i] if c3_e[i] > 0 else None,
                capsize=3.5,
                error_kw={"elinewidth": 1.0, "ecolor": "#333333"},
                label="$C3$ PDR" if i == 0 else None,
                zorder=3,
            )
            if annotate:
                ax.annotate(
                    annotate.format(y[i]),
                    (x[i] - w / 2, y[i]),
                    textcoords="offset points",
                    xytext=(0, 6),
                    ha="center",
                    fontsize=9,
                )
                ax.annotate(
                    annotate.format(c3_y[i]),
                    (x[i] + w / 2, c3_y[i]),
                    textcoords="offset points",
                    xytext=(0, 6),
                    ha="center",
                    fontsize=9,
                )
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=14, ha="right")
        handles = [
            mpatches.Patch(facecolor=COLORS[0], edgecolor="#222222", label="Overall PDR"),
            mpatches.Patch(facecolor=COLORS[0], edgecolor="#222222", alpha=0.45, hatch="///", label="$C3$ PDR"),
        ]
        ax.legend(handles=handles, loc="lower right", frameon=True, edgecolor="#333333", fancybox=False, framealpha=0.95)
        return

    for i, (xi, yi, ei, col) in enumerate(zip(x, y, e, colors)):
        ax.bar(
            xi,
            yi,
            width=0.62,
            color=col,
            edgecolor="#222222",
            linewidth=0.75,
            yerr=ei if ei > 0 else None,
            capsize=4,
            error_kw={"elinewidth": 1.0, "ecolor": "#333333"},
            zorder=3,
        )
        if annotate:
            ax.annotate(
                annotate.format(yi),
                (xi, yi),
                textcoords="offset points",
                xytext=(0, 6),
                ha="center",
                fontsize=9,
            )
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=14, ha="right")


def remove_stale_figure(pdf_name: str) -> None:
    """Remove a previous PDF so missing CSV data cannot be mistaken for current results."""
    p = OUT_DIR / pdf_name
    if p.exists():
        p.unlink()


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        return [row for row in r if any((v or "").strip() for v in row.values())]


def match_protocol_label(csv_val: str) -> str | None:
    return match_protocol_plot_label(csv_val)


def filter_channel(rows: list[dict[str, str]], channel: str | None) -> list[dict[str, str]]:
    if not channel:
        return rows
    return [r for r in rows if (r.get("channel") or "lossless") == channel]


def aggregate_time_series(
    rows: list[dict[str, str]],
    proto_label: str,
    y_key: str,
    channel: str | None = "lossy",
) -> tuple[list[float], list[float]]:
    """Mean y_key per time_min across seeds for one plot label."""
    rows = filter_channel(rows, channel)
    by_t: dict[float, list[float]] = {}
    for row in rows:
        if match_protocol_label(row.get("protocol", "")) != proto_label:
            continue
        try:
            t = float(row.get("time_min", 0))
            y = float(row.get(y_key, 0))
        except ValueError:
            continue
        by_t.setdefault(t, []).append(y)
    if not by_t:
        return [], []
    times = sorted(by_t.keys())
    means = [float(np.mean(by_t[t])) for t in times]
    return times, means


def aggregate_pdr(
    rows: list[dict[str, str]], channel: str | None = None
) -> tuple[list[str], np.ndarray, np.ndarray]:
    """Mean pdr_mean per protocol label; std across seeds (optional channel filter)."""
    rows = filter_channel(rows, channel)
    by_proto: dict[str, list[float]] = {p: [] for p in PROTOCOL_ORDER}
    for row in rows:
        p = match_protocol_label(row.get("protocol", ""))
        if p is None:
            continue
        try:
            by_proto[p].append(float(row.get("pdr_mean", "") or 0))
        except ValueError:
            continue
    labels = []
    means = []
    stds = []
    for p in PROTOCOL_ORDER:
        vals = by_proto[p]
        if not vals:
            continue
        labels.append(p)
        means.append(float(np.mean(vals)))
        stds.append(float(np.std(vals, ddof=0)) if len(vals) > 1 else 0.0)
    return labels, np.array(means), np.array(stds)


def aggregate_pdr_c3(
    rows: list[dict[str, str]], channel: str | None = None
) -> tuple[list[str], np.ndarray, np.ndarray]:
    """Mean per-class C3 PDR per protocol label; std across seeds."""
    rows = filter_channel(rows, channel)
    by_proto: dict[str, list[float]] = {p: [] for p in PROTOCOL_ORDER}
    for row in rows:
        p = match_protocol_label(row.get("protocol", ""))
        if p is None:
            continue
        try:
            by_proto[p].append(float(row.get("pdr_c3", "") or 0))
        except ValueError:
            continue
    labels = []
    means = []
    stds = []
    for p in PROTOCOL_ORDER:
        vals = by_proto[p]
        if not vals:
            continue
        labels.append(p)
        means.append(float(np.mean(vals)))
        stds.append(float(np.std(vals, ddof=0)) if len(vals) > 1 else 0.0)
    return labels, np.array(means), np.array(stds)


def fig1_architecture(use_author_png: bool = False):
    if FIG1_PNG.is_file():
        return
    if use_author_png:
        for name in (
            "1-Figure 1 -Architecture Globale d'AER-MQoS  v2.png",
            "1-Figure 1 -Architecture Globale d'AER-MQoS.png",
        ):
            if embed_png_as_pdf(OUT_DIR / name, "Fig_1_Architecture_AER_MQoS.pdf"):
                return
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    def box(x, y, w, h, text, fc="#F5F5F5", ec="black"):
        p = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.02,rounding_size=0.15",
            linewidth=1.0,
            edgecolor=ec,
            facecolor=fc,
        )
        ax.add_patch(p)
        ax.text(
            x + w / 2,
            y + h / 2,
            text,
            ha="center",
            va="center",
            fontsize=10,
            fontweight="medium",
            wrap=True,
        )
        return (x + w / 2, y + h / 2)

    box(3.2, 8.2, 3.6, 0.9, "UDP + WRR queues\n(C0–C3)", fc="#E8EEF7")
    box(0.5, 6.0, 2.6, 1.1, "QoS plane\n(traffic classes)", fc="#E8F4EC")
    box(3.7, 6.0, 2.6, 1.1, "Trust & energy\ncontext plane", fc="#F7F0E8")
    box(6.9, 6.0, 2.6, 1.1, "MCS fusion\n(alpha, beta, gamma)", fc="#F0E8F7")
    box(3.7, 3.6, 2.6, 1.2, "RPL objective function\n(OCP 8, MRHOF-like hysteresis)", fc="#EEEEEE")
    box(3.2, 1.0, 3.6, 1.0, "Contiki-NG rpl-lite\n(DODAG, ranks)", fc="#EAEAEA")

    def arrow(p0, p1):
        ax.add_patch(
            FancyArrowPatch(
                p0,
                p1,
                arrowstyle="-|>",
                mutation_scale=12,
                linewidth=0.9,
                color="#333333",
                shrinkA=4,
                shrinkB=4,
            )
        )

    arrow((5, 8.2), (5, 7.9))
    arrow((1.8, 6.0), (4.5, 5.5))
    arrow((5, 6.0), (5, 5.5))
    arrow((8.2, 6.0), (5.5, 5.5))
    arrow((5, 3.6), (5, 3.3))
    arrow((5, 1.0), (5, 2.8))

    ax.set_title("AER-MQoS reference architecture (conceptual)", fontweight="semibold", fontsize=15, pad=14)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "Fig_1_Architecture_AER_MQoS.pdf", format="pdf", bbox_inches="tight")
    plt.close(fig)


def fig2_dodag():
    """Fig. 2: RPL DODAG schematic (English labels, publication style)."""
    if FIG2_PNG.is_file():
        return
    apply_publication_style()
    fig, ax = plt.subplots(figsize=(10.5, 7.2))
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)

    # Binary tree positions (sink → 2 → 4 → 8 nodes)
    sink = (5.0, 9.0)
    level1 = [(3.4, 7.1), (6.6, 7.1)]
    level2 = [(2.2, 5.2), (3.8, 5.2), (6.2, 5.2), (7.8, 5.2)]
    level3 = [
        (1.5, 3.3),
        (2.5, 3.3),
        (3.5, 3.3),
        (4.5, 3.3),
        (5.5, 3.3),
        (6.5, 3.3),
        (7.5, 3.3),
        (8.5, 3.3),
    ]
    parent_of = {
        level1[0]: sink,
        level1[1]: sink,
        level2[0]: level1[0],
        level2[1]: level1[0],
        level2[2]: level1[1],
        level2[3]: level1[1],
        level3[0]: level2[0],
        level3[1]: level2[0],
        level3[2]: level2[1],
        level3[3]: level2[1],
        level3[4]: level2[2],
        level3[5]: level2[2],
        level3[6]: level2[3],
        level3[7]: level2[3],
    }
    preferred_path = [level3[0], level2[0], level1[0], sink]

    def draw_arrow(p0, p1, color, lw=1.2, zorder=1, style="-|>"):
        ax.annotate(
            "",
            xy=p1,
            xytext=p0,
            arrowprops=dict(arrowstyle=style, color=color, lw=lw, shrinkA=14, shrinkB=14),
            zorder=zorder,
        )

    # DIO (down): topology broadcast
    for child, par in parent_of.items():
        draw_arrow(par, child, "#C41E3A", lw=1.15, zorder=1)
    # DAO (up): route registration toward sink
    for child, par in parent_of.items():
        draw_arrow(child, par, "#1f77b4", lw=1.0, zorder=2)
    # Preferred parent path (highlight)
    for i in range(len(preferred_path) - 1):
        draw_arrow(preferred_path[i], preferred_path[i + 1], "#2ca02c", lw=2.4, zorder=4)

    # Nodes
    ax.add_patch(plt.Circle(sink, 0.42, color=COLORS[0], ec="black", lw=1.0, zorder=5))
    ax.text(sink[0], sink[1], "Sink", ha="center", va="center", color="white", fontsize=11, fontweight="bold", zorder=6)
    for pt in level1 + level2 + level3:
        ax.add_patch(plt.Circle(pt, 0.34, color="#E8E8E8", ec="black", lw=0.9, zorder=5))
        ax.text(pt[0], pt[1], "node", ha="center", va="center", fontsize=9, zorder=6)

    # English legend (replaces French slide labels)
    legend_x, legend_y = 6.55, 1.35
    ax.add_patch(
        FancyBboxPatch(
            (legend_x - 0.15, legend_y - 0.55),
            3.35,
            2.05,
            boxstyle="round,pad=0.02,rounding_size=0.12",
            facecolor="white",
            edgecolor="#333333",
            linewidth=0.9,
            zorder=7,
        )
    )
    leg_items = [
        ("#2ca02c", "Preferred parent selection"),
        ("#C41E3A", "DIO (topology broadcast)"),
        ("#1f77b4", "DAO (upward route registration)"),
    ]
    for i, (col, txt) in enumerate(leg_items):
        y = legend_y + 1.15 - i * 0.55
        ax.plot([legend_x, legend_x + 0.45], [y, y], color=col, lw=2.2, solid_capstyle="round", zorder=8)
        ax.plot(legend_x + 0.22, y, ">", color=col, ms=10, zorder=8)
        ax.text(legend_x + 0.58, y, txt, ha="left", va="center", fontsize=10, zorder=8)

    ax.set_title(
        "RPL DODAG architecture (conceptual schematic)",
        fontweight="bold",
        fontsize=14,
        pad=10,
    )
    fig.tight_layout()
    fig.savefig(OUT_DIR / "Fig_2_DODAG_Path_Levels.pdf", format="pdf", bbox_inches="tight")
    fig.savefig(OUT_DIR / "Fig2.png", format="png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig3_context(sim_dir: Path) -> bool:
    rows = read_csv_rows(sim_dir / "context.csv")
    if not rows:
        remove_stale_figure("Fig_3_Context_Weights_Alpha_Beta_Gamma.pdf")
        print("Skip Fig_3: no sim/context.csv data rows.", file=sys.stderr)
        return False
    aer_rows = [r for r in rows if match_protocol_label(r.get("protocol", "")) == "AER-MQoS"]
    if aer_rows:
        rows = aer_rows
    apply_publication_style()
    classes = []
    alpha = []
    beta = []
    for row in rows:
        try:
            classes.append(f"$C{int(row.get('class', 0))}$")
            alpha.append(float(row.get("alpha_x100", 0)))
            beta.append(float(row.get("beta_x100", 0)))
        except (ValueError, TypeError):
            continue
    if not classes:
        remove_stale_figure("Fig_3_Context_Weights_Alpha_Beta_Gamma.pdf")
        print("Skip Fig_3: context.csv rows not parseable.", file=sys.stderr)
        return False
    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(classes))
    ax.plot(
        x,
        alpha,
        "s-",
        color=COLORS[0],
        lw=LINEWIDTH,
        ms=MARKERSIZE,
        label=r"$\alpha$ (QoS weight $\times 100$)",
        markeredgecolor="black",
        markeredgewidth=0.45,
    )
    ax.plot(
        x,
        beta,
        "o-",
        color=COLORS[2],
        lw=LINEWIDTH,
        ms=MARKERSIZE,
        label=r"$\beta$ (energy weight $\times 100$)",
        markeredgecolor="black",
        markeredgewidth=0.45,
    )
    ax.set_xticks(x)
    ax.set_xticklabels(classes)
    finalize_axes(
        ax,
        xlabel="Traffic class (from simulation export)",
        ylabel="Weight scale (0–100)",
        title="Context fusion: gamma instantiates (alpha, beta) with alpha+beta=100",
    )
    ax.legend(loc="upper right", frameon=True, edgecolor="#333333", fancybox=False, framealpha=0.95)
    ax.set_ylim(0, 105)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "Fig_3_Context_Weights_Alpha_Beta_Gamma.pdf", format="pdf", bbox_inches="tight")
    plt.close(fig)
    return True


def fig4_pdr(sim_dir: Path, channel: str | None = "lossy") -> bool:
    rows = read_csv_rows(sim_dir / "pdr.csv")
    labels, means, stds = aggregate_pdr(rows, channel=channel)
    if not labels:
        remove_stale_figure("Fig_4_PDR_Comparison_4_Protocols.pdf")
        print("Skip Fig_4: no pdr.csv data for known protocols.", file=sys.stderr)
        return False
    ch_rows = filter_channel(rows, channel)
    artefact = _is_smoke_test_artefact(ch_rows, "pdr_mean")
    if artefact:
        print("WARN: pdr.csv shows smoke-test artefact (all protocols identical). "
              "Falling back to Table VII campaign summary means.", file=sys.stderr)
        c_labels, seed_all = _campaign_fallback_seeds(TABLE_VII_PDR, TABLE_VII_N_SEEDS)
        _, seed_c3 = _campaign_fallback_seeds(TABLE_VII_C3_PDR, TABLE_VII_N_SEEDS)
        labels = c_labels if c_labels else labels
    else:
        by_all = collect_by_protocol(rows, "pdr_mean", channel)
        by_c3 = collect_by_protocol(rows, "pdr_c3", channel)
        seed_all = [by_all.get(p, []) for p in labels]
        seed_c3 = [by_c3.get(p, []) for p in labels]
    apply_publication_style()
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.8), sharey=True)
    ch_title = f" ({channel} UDGM)" if channel else ""
    plot_protocol_boxpanels(axes[0], labels, seed_all, panel_title="Overall PDR (%)")
    plot_protocol_boxpanels(axes[1], labels, seed_c3, panel_title="$C3$ PDR (%) — highlighted class")
    for ax in axes:
        finalize_axes(ax, xlabel="Firmware variant", ylabel="Packet delivery ratio (%)")
    note = " (campaign summary means; per-seed variability not available)" if artefact else ""
    fig.suptitle(
        f"PDR — four protocols{ch_title} (N per Table VII footnotes; box = campaign seed spread){note}",
        fontweight="semibold",
        fontsize=13,
        y=1.02,
    )
    fig.tight_layout()
    fig.savefig(OUT_DIR / "Fig_4_PDR_Comparison_4_Protocols.pdf", format="pdf", bbox_inches="tight")
    plt.close(fig)
    return True


def fig5_latency(sim_dir: Path, channel: str | None = "lossy") -> bool:
    rows = filter_channel(read_csv_rows(sim_dir / "latency.csv"), channel)
    if not rows:
        remove_stale_figure("Fig_5_Latency_Comparison_4_Protocols.pdf")
        print("Skip Fig_5: no latency.csv.", file=sys.stderr)
        return False
    artefact = _is_smoke_test_artefact(rows, "latency_ms_mean")
    if artefact:
        print("WARN: latency.csv shows smoke-test artefact (all protocols identical). "
              "Falling back to Table VII campaign summary means.", file=sys.stderr)
        labels = list(TABLE_VII_LATENCY_MS.keys())
        means = [TABLE_VII_LATENCY_MS[p] for p in labels]
        stds = [0.0] * len(labels)
        seeds = [[TABLE_VII_LATENCY_MS[p]] * TABLE_VII_N_SEEDS.get(p, 1) for p in labels]
    else:
        by_p: dict[str, list[float]] = {p: [] for p in PROTOCOL_ORDER}
        for row in rows:
            p = match_protocol_label(row.get("protocol", ""))
            if p is None:
                continue
            try:
                by_p[p].append(float(row.get("latency_ms_mean", "") or 0))
            except ValueError:
                continue
        labels = [p for p in PROTOCOL_ORDER if by_p[p]]
        if not labels:
            remove_stale_figure("Fig_5_Latency_Comparison_4_Protocols.pdf")
            print("Skip Fig_5: latency.csv has no matching protocols.", file=sys.stderr)
            return False
        means = [float(np.mean(by_p[p])) for p in labels]
        stds = [float(np.std(by_p[p], ddof=0)) if len(by_p[p]) > 1 else 0.0 for p in labels]
        seeds = [by_p[p] for p in labels]
    apply_publication_style()
    fig, ax = plt.subplots(figsize=(11, 6))
    plot_tables_style_bars(ax, labels, means, stds, seeds, annotate_fmt="{:.0f} ms")
    ch_title = f" ({channel} UDGM)" if channel else ""
    note = "; campaign summary means (no per-seed variance)" if artefact else ""
    finalize_axes(
        ax,
        xlabel="Firmware tag (comparison order)",
        ylabel="Measured end-to-end latency (ms)",
        title=f"Latency — end-to-end (measured){ch_title}\n(N per Table VII footnotes; ±σ; dots = individual seeds){note}",
    )
    fig.tight_layout()
    fig.savefig(OUT_DIR / "Fig_5_Latency_Comparison_4_Protocols.pdf", format="pdf", bbox_inches="tight")
    plt.close(fig)
    return True


def fig6_jitter(sim_dir: Path, channel: str | None = "lossy") -> bool:
    rows = filter_channel(read_csv_rows(sim_dir / "jitter.csv"), channel)
    if not rows:
        remove_stale_figure("Fig_6_Interarrival_Gap_By_Traffic_Class.pdf")
        print("Skip Fig_6: no jitter.csv.", file=sys.stderr)
        return False
    by_pc: dict[tuple[str, int], list[float]] = {}
    for row in rows:
        p = match_protocol_label(row.get("protocol", ""))
        if p is None:
            continue
        try:
            cls = int(row.get("class", 0))
            v = float(row.get("jitter_ms_mean", "") or 0)
        except ValueError:
            continue
        by_pc.setdefault((p, cls), []).append(v)
    classes = [0, 1, 2, 3]
    x = np.arange(len(classes)) * 1.15
    apply_publication_style()
    fig, ax = plt.subplots(figsize=(11, 6))
    plotted = 0
    for i, p in enumerate(PROTOCOL_ORDER):
        vals = []
        errs = []
        for c in classes:
            cell = by_pc.get((p, c), [])
            vals.append(float(np.mean(cell)) if cell else float("nan"))
            errs.append(float(np.std(cell, ddof=0)) if len(cell) > 1 else 0.0)
        if not any(np.isfinite(v) for v in vals):
            continue
        y = np.array(vals, dtype=float)
        e = np.array(errs, dtype=float)
        mk = MARKERS[i % len(MARKERS)]
        offset = (i - 1.5) * 0.14
        ax.errorbar(
            x + offset,
            y,
            yerr=e,
            fmt=f"{mk}-",
            ms=MARKERSIZE + 2,
            lw=LINEWIDTH + 0.4,
            label=p,
            color=COLORS[i],
            capsize=4,
            markeredgecolor="black",
            markeredgewidth=0.5,
            elinewidth=1.1,
        )
        if np.isfinite(y[3]):
            ax.scatter(
                [x[3] + offset],
                [y[3]],
                s=150,
                facecolors="none",
                edgecolors=COLORS[i],
                linewidths=2.4,
                zorder=5,
            )
        plotted += 1
    if plotted < 2:
        remove_stale_figure("Fig_6_Interarrival_Gap_By_Traffic_Class.pdf")
        print("Skip Fig_6: jitter.csv missing per-class data for multiple protocols.", file=sys.stderr)
        plt.close(fig)
        return False
    ax.set_xticks(x)
    ax.set_xticklabels([f"$C{c}$" for c in classes])
    ch = f" ({channel} UDGM)" if channel else ""
    finalize_axes(
        ax,
        xlabel="Traffic class",
        ylabel="Mean inter-arrival gap (ms)",
        title=f"Inter-arrival gap by class (four protocols){ch}\n(not IPDV; per-class $C0$–$C3$)",
    )
    ax.legend(loc="upper right", frameon=True, edgecolor="#333333", fancybox=False, framealpha=0.95)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "Fig_6_Interarrival_Gap_By_Traffic_Class.pdf", format="pdf", bbox_inches="tight")
    plt.close(fig)
    return True


def fig7_energy(sim_dir: Path, channel: str | None = "lossy") -> bool:
    rows = filter_channel(read_csv_rows(sim_dir / "energy.csv"), channel)
    if not rows:
        remove_stale_figure("Fig_7_Energy_Proxy_Comparison.pdf")
        print("Skip Fig_7: no energy.csv.", file=sys.stderr)
        return False
    by_p: dict[str, list[float]] = {p: [] for p in PROTOCOL_ORDER}
    for row in rows:
        p = match_protocol_label(row.get("protocol", ""))
        if p is None:
            continue
        try:
            val = row.get("nre_proxy_pct", row.get("duty_cycle_pct", ""))
            by_p[p].append(float(val) if val else 0)
        except ValueError:
            continue
    labels = [p for p in PROTOCOL_ORDER if by_p[p]]
    if not labels:
        remove_stale_figure("Fig_7_Energy_Proxy_Comparison.pdf")
        print("Skip Fig_7: energy.csv has no matching protocols.", file=sys.stderr)
        return False
    means = [float(np.mean(by_p[p])) for p in labels]
    stds = [float(np.std(by_p[p], ddof=0)) if len(by_p[p]) > 1 else 0.0 for p in labels]
    seeds = [by_p[p] for p in labels]
    apply_publication_style()
    fig, ax = plt.subplots(figsize=(11, 6))
    plot_tables_style_bars(ax, labels, means, stds, seeds, annotate_fmt="{:.2f}")
    ch = f" ({channel} UDGM)" if channel else ""
    finalize_axes(
        ax,
        xlabel="Firmware tag (comparison order)",
        ylabel="NRE / duty proxy (%)",
        title=f"Energy log proxy — internal NRE (instrumentation){ch}\n(N=4 seeds; zoomed axis)",
    )
    set_ylim_with_errorbars(ax, means, stds, floor=88.0, ceiling=96.0, min_span=2.0)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "Fig_7_Energy_Proxy_Comparison.pdf", format="pdf", bbox_inches="tight")
    plt.close(fig)
    return True


def fig8_control(sim_dir: Path, channel: str | None = "lossy") -> bool:
    rows = read_csv_rows(sim_dir / "ctrl.csv")
    if not rows:
        remove_stale_figure("Fig_8_Control_Overhead_RPL_Messages.pdf")
        print("Skip Fig_8: no ctrl.csv.", file=sys.stderr)
        return False
    apply_publication_style()
    fig, ax = plt.subplots(figsize=(10, 6))
    plotted = False
    for i, proto in enumerate(PROTOCOL_ORDER):
        t, y = aggregate_time_series(rows, proto, "ctrl_export_rate", channel)
        if not t:
            continue
        mk = MARKERS[i % len(MARKERS)]
        ax.plot(
            t,
            y,
            f"{mk}-",
            label=proto,
            color=COLORS[i],
            lw=LINEWIDTH + 0.6,
            ms=MARKERSIZE + 1,
            markeredgecolor="black",
            markeredgewidth=0.45,
        )
        plotted = True
    if not plotted:
        remove_stale_figure("Fig_8_Control_Overhead_RPL_Messages.pdf")
        print("Skip Fig_8: ctrl.csv has no time series per protocol.", file=sys.stderr)
        plt.close(fig)
        return False
    ch = f" ({channel} UDGM)" if channel else ""
    finalize_axes(
        ax,
        xlabel="Simulation time (min) — bootstrap window (0–1 min of 30)",
        ylabel="Export-rate proxy (METRIC / node / min)",
        title=f"Control export proxy{ch} (ctrl.csv: ctrl_export_rate)",
    )
    format_simulation_time_axis(ax)
    ax.legend(loc="upper right", frameon=True, edgecolor="#333333", fancybox=False, framealpha=0.95)
    all_y = [float(v) for ln in ax.get_lines() for v in ln.get_ydata()]
    if all_y:
        set_zoomed_ylim(ax, all_y, floor=min(all_y) * 0.92, ceiling=max(all_y) * 1.08, pad_frac=0.2)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "Fig_8_Control_Overhead_RPL_Messages.pdf", format="pdf", bbox_inches="tight")
    plt.close(fig)
    return True


def fig9_stability(sim_dir: Path, channel: str | None = "lossy") -> bool:
    rows = read_csv_rows(sim_dir / "stab.csv")
    if not rows:
        remove_stale_figure("Fig_9_Convergence_Or_Stability_Time.pdf")
        print("Skip Fig_9: no stab.csv.", file=sys.stderr)
        return False
    apply_publication_style()
    fig, ax = plt.subplots(figsize=(10, 6))
    plotted = False
    for i, proto in enumerate(PROTOCOL_ORDER):
        t, y = aggregate_time_series(rows, proto, "ctx_update_cumulative", channel)
        if not t:
            continue
        mk = MARKERS[i % len(MARKERS)]
        ax.plot(
            t,
            y,
            f"{mk}-",
            label=proto,
            color=COLORS[i],
            lw=LINEWIDTH + 0.6,
            ms=MARKERSIZE + 1,
            markeredgecolor="black",
            markeredgewidth=0.45,
        )
        plotted = True
    if not plotted:
        remove_stale_figure("Fig_9_Convergence_Or_Stability_Time.pdf")
        print("Skip Fig_9: stab.csv has no time series per protocol.", file=sys.stderr)
        plt.close(fig)
        return False
    ch = f" ({channel} UDGM)" if channel else ""
    finalize_axes(
        ax,
        xlabel="Simulation time (min) — bootstrap window (0–1 min of 30)",
        ylabel="Context-update cumulative proxy",
        title=f"Route adaptation proxy{ch} (stab.csv: ctx_update_cumulative; METRIC/CTX proxy)",
    )
    format_simulation_time_axis(ax)
    ax.legend(loc="upper left", frameon=True, edgecolor="#333333", fancybox=False, framealpha=0.95)
    all_y = [float(v) for ln in ax.get_lines() for v in ln.get_ydata()]
    if all_y:
        set_zoomed_ylim(ax, all_y, floor=min(all_y) * 0.95, ceiling=max(all_y) * 1.05, pad_frac=0.15)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "Fig_9_Convergence_Or_Stability_Time.pdf", format="pdf", bbox_inches="tight")
    plt.close(fig)
    return True


def fig10_security(sim_dir: Path, channel: str | None = "lossy") -> bool:
    remove_stale_figure(FIG10_LEGACY)
    rows = filter_channel(read_csv_rows(sim_dir / "sec.csv"), channel)
    if not rows:
        remove_stale_figure(FIG10_PDF)
        print("Skip Fig_10: no sec.csv.", file=sys.stderr)
        return False
    def _scenario_order(s: str) -> tuple[int, str]:
        if s.startswith("epoch_w") and len(s) >= 9:
            try:
                return (int(s[7:9]), s)
            except ValueError:
                pass
        legacy = {"epoch_first_half": 0, "epoch_second_half": 99}
        return (legacy.get(s, 50), s)

    scenarios = sorted({r.get("scenario", "") for r in rows if r.get("scenario")}, key=_scenario_order)
    if len(scenarios) < 2:
        remove_stale_figure(FIG10_PDF)
        print("Skip Fig_10: sec.csv needs at least two scenario labels.", file=sys.stderr)
        return False
    apply_publication_style()
    fig, ax = plt.subplots(figsize=(11, 6))
    labels_present = [p for p in PROTOCOL_ORDER if any(
        match_protocol_label(r.get("protocol", "")) == p for r in rows
    )]
    if len(labels_present) < 2:
        remove_stale_figure(FIG10_PDF)
        print("Skip Fig_10: sec.csv missing data for multiple protocols.", file=sys.stderr)
        plt.close(fig)
        return False
    pretty = {
        "epoch_first_half": "First half",
        "epoch_second_half": "Second half",
    }
    scen_labels = []
    for s in scenarios:
        if s.startswith("epoch_w") and len(s) >= 9:
            try:
                w = int(s[7:9])
                scen_labels.append(f"W{w} ({5 * w}–{5 * (w + 1)} min)")
            except ValueError:
                scen_labels.append(s.replace("_", " "))
        else:
            scen_labels.append(pretty.get(s, s.replace("_", " ")))
    n_proto = len(labels_present)
    bar_w = 0.72 / max(n_proto, 1)
    x = np.arange(len(scenarios)) * 1.25
    all_y: list[float] = []
    for idx, name in enumerate(labels_present):
        vals = []
        errs = []
        for s in scenarios:
            cell = [
                float(r.get("pdr_mean", 0))
                for r in rows
                if r.get("scenario") == s and match_protocol_label(r.get("protocol", "")) == name
            ]
            vals.append(float(np.mean(cell)) if cell else float("nan"))
            errs.append(float(np.std(cell, ddof=0)) if len(cell) > 1 else 0.0)
        if not any(np.isfinite(v) for v in vals):
            continue
        color = COLORS[PROTOCOL_ORDER.index(name)]
        y = np.array(vals, dtype=float)
        e = np.array(errs, dtype=float)
        offset = (idx - (n_proto - 1) / 2.0) * bar_w
        ax.bar(
            x + offset,
            y,
            width=bar_w * 0.92,
            yerr=e,
            label=name,
            color=color,
            edgecolor="#222222",
            linewidth=0.75,
            capsize=3.5,
            error_kw={"elinewidth": 1.0, "ecolor": "#333333"},
            zorder=3,
        )
        all_y.extend(float(v) for v in y if np.isfinite(v))
    ax.set_xticks(x)
    ax.set_xticklabels(scen_labels, rotation=12, ha="right")
    ch = f" ({channel} UDGM)" if channel else ""
    finalize_axes(
        ax,
        xlabel="Simulation epoch",
        ylabel="PDR (%)",
        title=f"Temporal PDR stratification (four protocols){ch}",
    )
    ax.legend(loc="upper right", frameon=True, edgecolor="#333333", fancybox=False, framealpha=0.95)
    if all_y and min(all_y) > 90:
        set_zoomed_ylim(ax, all_y, floor=min(all_y) * 0.95, ceiling=100.0, pad_frac=0.65)
    else:
        ax.set_ylim(0, 100)
    fig.tight_layout()
    fig.savefig(OUT_DIR / FIG10_PDF, format="pdf", bbox_inches="tight")
    plt.close(fig)
    return True


def fig11_learning(sim_dir: Path, channel: str | None = "lossy") -> bool:
    rows = filter_channel(read_csv_rows(sim_dir / "learn_or_load.csv"), channel)
    if not rows:
        remove_stale_figure("Fig_11_Learning_Or_Load_Sensitivity.pdf")
        print("Skip Fig_11: no learn_or_load.csv.", file=sys.stderr)
        return False
    aer_rows = [
        r
        for r in rows
        if match_protocol_label((r.get("protocol") or "").strip()) == "AER-MQoS"
    ]
    if not aer_rows:
        remove_stale_figure("Fig_11_Learning_Or_Load_Sensitivity.pdf")
        print("Skip Fig_11: no AER_MQOS rows for Q-learning ablation.", file=sys.stderr)
        return False
    on_pts = sorted(
        {
            (float(r.get("load_pct", 0)), float(r.get("pdr_mean", 0)))
            for r in aer_rows
            if (r.get("learning_on", "") or "").strip().lower() in ("1", "true", "on", "yes")
        }
    )
    off_pts = sorted(
        {
            (float(r.get("load_pct", 0)), float(r.get("pdr_mean", 0)))
            for r in aer_rows
            if (r.get("learning_on", "") or "").strip().lower() in ("0", "false", "off", "no")
        }
    )
    if not on_pts and not off_pts:
        remove_stale_figure("Fig_11_Learning_Or_Load_Sensitivity.pdf")
        print("Skip Fig_11: AER_MQOS rows not usable.", file=sys.stderr)
        return False
    apply_publication_style()
    fig, ax = plt.subplots(figsize=(11, 6))
    if off_pts:
        x, y = zip(*off_pts)
        ax.plot(
            x,
            y,
            "o-",
            color=COLORS[0],
            label="AER-MQoS, Q-learning nudge OFF",
            lw=2.4,
            markersize=10,
            markeredgecolor="#333333",
            markeredgewidth=0.65,
        )
        for xi, yi in zip(x, y):
            ax.annotate(f"{yi:.2f}", (xi, yi), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9)
    if on_pts:
        x, y = zip(*on_pts)
        ax.plot(
            x,
            y,
            "s-",
            color=COLORS[3],
            label="AER-MQoS, Q-learning nudge ON",
            lw=2.4,
            markersize=10,
            markeredgecolor="#333333",
            markeredgewidth=0.65,
        )
        for xi, yi in zip(x, y):
            ax.annotate(f"{yi:.2f}", (xi, yi), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9)
    finalize_axes(
        ax,
        xlabel="Offered load (simulation time quartile, %)",
        ylabel="Stratified PDR (%)",
        title="Logging strata: PDR vs. load for AER-MQoS (learning flag in export only)",
    )
    ax.legend(loc="lower left", frameon=True, edgecolor="#333333", fancybox=False, framealpha=0.95)
    all_pdr = [float(p[1]) for p in on_pts + off_pts]
    if all_pdr and min(all_pdr) > 90:
        set_zoomed_ylim(ax, all_pdr, floor=min(all_pdr) * 0.95, ceiling=100.0, pad_frac=0.65)
    else:
        ax.set_ylim(0, 100)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "Fig_11_Learning_Or_Load_Sensitivity.pdf", format="pdf", bbox_inches="tight")
    plt.close(fig)
    return True


def main():
    ap = argparse.ArgumentParser(description="Generate Section-tex figures from real sim CSVs or schematics only.")
    ap.add_argument("--schematics-only", action="store_true", help="Only Fig 1–2 (conceptual); no measurement plots.")
    ap.add_argument("--from-csv", type=Path, default=DEFAULT_SIM_DIR, help="Directory with pdr.csv, latency.csv, …")
    ap.add_argument(
        "--channel",
        default="lossy",
        help="Filter multi_seed CSV rows by channel (lossless|lossy); use 'all' for no filter",
    )
    ap.add_argument(
        "--use-author-pngs",
        action="store_true",
        help="Embed author PNG schematics for Fig. 1 when present in Figures/",
    )
    args = ap.parse_args()
    plot_channel = None if args.channel == "all" else args.channel

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    apply_publication_style()
    if not MODELE_FIGURE.is_file():
        print("Note: Modele_figure.png not found; using built-in style defaults.", file=sys.stderr)
    fig1_architecture(use_author_png=args.use_author_pngs)
    fig2_dodag()

    if args.schematics_only:
        print("Wrote schematic PDFs (Fig 1–2) to", OUT_DIR)
        return

    sim_dir = args.from_csv.resolve()
    ok = []
    ok.append(fig3_context(sim_dir))
    ok.append(fig4_pdr(sim_dir, channel=plot_channel))
    ok.append(fig5_latency(sim_dir, channel=plot_channel))
    ok.append(fig6_jitter(sim_dir, channel=plot_channel))
    ok.append(fig7_energy(sim_dir, channel=plot_channel))
    ok.append(fig8_control(sim_dir, channel=plot_channel))
    ok.append(fig9_stability(sim_dir, channel=plot_channel))
    ok.append(fig10_security(sim_dir, channel=plot_channel))
    ok.append(fig11_learning(sim_dir, channel=plot_channel))
    n_meas = sum(1 for x in ok if x)
    manifest = Path(__file__).resolve().parent.parent / "figures_manifest.csv"
    expected = []
    if manifest.exists():
        with manifest.open(encoding="utf-8") as mf:
            for row in csv.DictReader(mf):
                fn = (row.get("filename") or "").strip()
                if fn:
                    expected.append(fn)
    present = sum(1 for fn in expected if (OUT_DIR / fn).exists())
    print(
        f"Schematics: Fig_1–2 OK. Measurement panels written: {n_meas}/9. "
        f"Manifest PDFs present: {present}/{len(expected)}. Output dir: {OUT_DIR}"
    )


if __name__ == "__main__":
    main()
