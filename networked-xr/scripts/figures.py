#!/usr/bin/env python3
"""Draw the data figures of the review from the atlas label and corpus files.

Usage: python3 scripts/figures.py [ATLAS_DIR]   (default: ../../cc1/networked_xr)
Writes figures/fig_*.pdf. Colours follow the six functional categories defined in preamble.tex.
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent.parent
ATLAS = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parents[1] / "cc1" / "networked_xr"
sys.path.insert(0, str(ATLAS.parent / "scripts"))
from chunked import read_parquet_parts  # noqa: E402

OUT = HERE / "figures"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
FUNC = {  # function -> (label, colour, problems in display order)
    "encode": ("Encode", "#2A78D6", ["compression_coding"]),
    "anticipate": ("Anticipate", "#EB6834", ["rate_adaptation_streaming", "viewport_motion_prediction", "caching_prefetching"]),
    "compute": ("Compute", "#1BAF7A", ["offloading_remote_rendering", "latency"]),
    "provision": ("Provision", "#6250D6", ["resource_allocation", "wireless_link_design", "architecture_vision"]),
    "connect": ("Connect", "#E87BA4", ["multiuser_synchronisation", "tactile_haptic_transport", "holographic_communication"]),
    "assure": ("Assure", "#008300", ["qoe_measurement_modelling", "security_privacy_trust"]),
}
PROB_NAME = {
    "compression_coding": "Compression and coding", "rate_adaptation_streaming": "Rate adaptation and streaming",
    "viewport_motion_prediction": "Viewport and motion prediction", "caching_prefetching": "Caching and prefetching",
    "offloading_remote_rendering": "Offloading and remote rendering", "latency": "Latency and MTP",
    "resource_allocation": "Resource allocation", "wireless_link_design": "Wireless link design",
    "architecture_vision": "Architecture and vision", "multiuser_synchronisation": "Multi-user synchronisation",
    "tactile_haptic_transport": "Tactile and haptic transport", "holographic_communication": "Holographic communication",
    "qoe_measurement_modelling": "QoE measurement and modelling", "security_privacy_trust": "Security, privacy and trust",
}
CONT_NAME = {
    "video_360": "360-degree video", "volumetric_pointcloud": "Volumetric content", "holographic": "Holographic content",
    "haptic_tactile": "Haptic signals", "rendered_frames": "Rendered frames", "ar_objects_overlays": "AR objects, overlays",
    "avatars_social_state": "Avatars, social state", "digital_twin_data": "Digital-twin data",
    "general_xr_traffic": "XR traffic in general",
}
CONT_FUNC = {"video_360": "anticipate", "volumetric_pointcloud": "encode", "holographic": "encode",
             "haptic_tactile": "encode", "rendered_frames": "compute", "ar_objects_overlays": "compute",
             "avatars_social_state": "connect", "digital_twin_data": "connect", "general_xr_traffic": "provision"}
EVAL = [("real_testbed_users", "Real testbed, users"), ("real_testbed", "Real testbed"),
        ("trace_emulation", "Trace emulation"), ("simulation", "Simulation"), ("analytical", "Analytical"),
        ("none", "None")]
# Sequential ramp, dark (most realistic) to light; one hue.
EVAL_COL = ["#0d366b", "#1f5aa6", "#4f86c6", "#8fb3dd", "#c3d6ee", "#ecebe7"]
PROB_OF = {p: f for f, (_, _, ps) in FUNC.items() for p in ps}

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6, "pdf.fonttype": 42})


def load():
    lab = read_parquet_parts(ATLAS / "data/taxonomy/paper_labels.parquet")
    inc = read_parquet_parts(ATLAS / "data/processed/included.parquet", columns=["id", "year"])
    return lab.merge(inc, on="id")


def period(y):
    return "early" if 2017 <= y <= 2019 else "late" if 2022 <= y <= 2024 else None


def fig_growth(df):
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 2.4), gridspec_kw={"width_ratios": [1, 1.25], "wspace": 0.32})
    yc = df.year.value_counts().sort_index()
    yrs = list(range(2016, 2027))
    vals = [int(yc.get(y, 0)) for y in yrs]
    partial = {2016, 2025, 2026}
    a.bar(yrs, vals, width=0.72, color=["#c3d6ee" if y in partial else "#2A78D6" for y in yrs], edgecolor="white", linewidth=1)
    for y, v in zip(yrs, vals):
        a.text(y, v + 12, f"{v}", ha="center", va="bottom", fontsize=6.5, color=INK2)
    a.set_xticks(yrs, [f"'{str(y)[2:]}" for y in yrs])
    a.set_ylabel("Included papers")
    a.set_ylim(0, max(vals) * 1.15)
    a.yaxis.grid(True, color=GRID, linewidth=0.5); a.set_axisbelow(True)
    a.set_title("(a) Papers per year (light: partial year)", fontsize=8, loc="left", color=INK)

    sub = df[(df.year >= 2017) & (df.year <= 2025)]
    tab = pd.crosstab(sub.year, sub.evaluation, normalize="index") * 100
    bottom = np.zeros(len(tab))
    for (k, name), c in zip(EVAL, EVAL_COL):
        v = tab.get(k, pd.Series(0, index=tab.index)).values
        b.bar(tab.index, v, bottom=bottom, color=c, width=0.78, edgecolor="white", linewidth=0.8, label=name)
        bottom += v
    b.set_ylim(0, 100); b.set_ylabel("Share of papers (%)")
    b.set_xticks(tab.index, [f"'{str(y)[2:]}" for y in tab.index])
    b.set_title("(b) Most realistic evaluation reported", fontsize=8, loc="left", color=INK)
    b.legend(loc="center left", bbox_to_anchor=(1.0, 0.5), frameon=False, fontsize=7, handlelength=1, reverse=True)
    fig.savefig(OUT / "fig_growth.pdf", bbox_inches="tight")
    plt.close(fig)


def shares(df, col, cats):
    out = {}
    for per in ("early", "late"):
        s = df[df.year.map(period) == per][col].value_counts(normalize=True) * 100
        out[per] = {c: float(s.get(c, 0)) for c in cats}
    return out


def dumbbell(ax, items, sh, names, colour_of, title):
    items = sorted(items, key=lambda c: sh["late"][c] - sh["early"][c])
    for i, c in enumerate(items):
        e, l = sh["early"][c], sh["late"][c]
        col = colour_of(c)
        ax.plot([e, l], [i, i], color=col, linewidth=1.6, solid_capstyle="round", zorder=1)
        ax.scatter([e], [i], s=22, facecolor="white", edgecolor=col, linewidth=1.3, zorder=2)
        ax.scatter([l], [i], s=26, color=col, edgecolor="white", linewidth=0.8, zorder=3)
        d = l - e
        ax.text(max(e, l) + 0.8, i, f"{d:+.1f}", va="center", fontsize=6.5, color=INK2)
    ax.set_yticks(range(len(items)), [names[c] for c in items], fontsize=7)
    ax.xaxis.grid(True, color=GRID, linewidth=0.5); ax.set_axisbelow(True)
    ax.set_xlabel("Share of papers (%)  ○ 2017–19   ● 2022–24")
    ax.set_title(title, fontsize=8, loc="left", color=INK)
    ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)


def fig_shifts(df):
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 3.1), gridspec_kw={"wspace": 0.95})
    probs = list(PROB_NAME)
    dumbbell(a, probs, shares(df, "problem", probs), PROB_NAME, lambda c: FUNC[PROB_OF[c]][1], "(a) Networking problem")
    conts = list(CONT_NAME)
    dumbbell(b, conts, shares(df, "content", conts), CONT_NAME, lambda c: FUNC[CONT_FUNC[c]][1], "(b) Content type")
    a.set_xlim(0, 26); b.set_xlim(0, 40)
    handles = [plt.Line2D([], [], color=c, linewidth=2, label=l) for l, c, _ in FUNC.values()]
    fig.legend(handles=handles, loc="lower center", ncol=6, frameon=False, fontsize=7, bbox_to_anchor=(0.5, -0.13))
    fig.savefig(OUT / "fig_shifts.pdf", bbox_inches="tight")
    plt.close(fig)


def fig_realism(df):
    rows = [(f, p) for f, (_, _, ps) in FUNC.items() for p in ps]
    fig, ax = plt.subplots(figsize=(7.0, 3.3))
    y = np.arange(len(rows))[::-1]
    for yi, (f, p) in zip(y, rows):
        s = df[df.problem == p].evaluation.value_counts(normalize=True) * 100
        left = 0
        for (k, _), c in zip(EVAL, EVAL_COL):
            w = float(s.get(k, 0))
            ax.barh(yi, w, left=left, color=c, height=0.72, edgecolor="white", linewidth=0.8)
            if w >= 9:
                ax.text(left + w / 2, yi, f"{w:.0f}", ha="center", va="center", fontsize=6.3,
                        color="white" if c in EVAL_COL[:3] else INK)
            left += w
        n = int((df.problem == p).sum())
        ax.text(101.5, yi, f"n={n}", va="center", fontsize=6.5, color=INK2)
        ax.add_patch(plt.Rectangle((-1.6, yi - 0.36), 0.9, 0.72, color=FUNC[f][1], clip_on=False))
    ax.set_yticks(y, [PROB_NAME[p] for _, p in rows], fontsize=7)
    ax.tick_params(axis="y", length=0, pad=9)
    ax.set_xlim(0, 100); ax.set_xlabel("Share of papers (%)")
    ax.spines["left"].set_visible(False)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c, label=n) for (_, n), c in zip(EVAL, EVAL_COL)]
    ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.45, 1.0), ncol=6, frameon=False, fontsize=7,
              handlelength=1)
    # Function brackets on the right.
    start = 0
    for f, (lab, col, ps) in FUNC.items():
        ys = y[start:start + len(ps)]
        ax.text(111, ys.mean(), lab, va="center", ha="left", fontsize=7, color=INK, fontweight="bold")
        ax.plot([109.5, 109.5], [ys.min() - 0.3, ys.max() + 0.3], color=col, linewidth=2.2, clip_on=False)
        start += len(ps)
    fig.savefig(OUT / "fig_realism.pdf", bbox_inches="tight")
    plt.close(fig)


def fig_heatmap(df):
    probs = [p for _, (_, _, ps) in FUNC.items() for p in ps]
    conts = [c for c in CONT_NAME if c != "general_xr_traffic"]
    sub = df[df.problem.isin(probs) & df.content.isin(conts)]
    obs = pd.crosstab(sub.problem, sub.content).reindex(index=probs, columns=conts, fill_value=0)
    exp = np.outer(obs.sum(axis=1), obs.sum(axis=0)) / obs.values.sum()
    g = np.log2((obs.values + 1) / (exp + 1))
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    im = ax.imshow(g, cmap="RdBu", vmin=-3, vmax=3, aspect="auto")
    for i in range(len(probs)):
        for j in range(len(conts)):
            ax.text(j, i, f"{obs.values[i, j]}", ha="center", va="center", fontsize=6.3,
                    color="white" if abs(g[i, j]) > 1.9 else INK)
    ax.set_xticks(range(len(conts)), [CONT_NAME[c] for c in conts], rotation=35, ha="right", fontsize=7)
    ax.set_yticks(range(len(probs)), [PROB_NAME[p] for p in probs], fontsize=7)
    for i, p in enumerate(probs):
        ax.add_patch(plt.Rectangle((-0.5 - 0.2, i - 0.5), 0.14, 1, color=FUNC[PROB_OF[p]][1], clip_on=False))
    ax.tick_params(length=0); ax.tick_params(axis="y", pad=12)
    for s in ax.spines.values(): s.set_visible(False)
    cb = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
    cb.set_label(r"$\log_2$ (observed+1)/(expected+1)", fontsize=7); cb.ax.tick_params(labelsize=6.5)
    cb.outline.set_visible(False)
    fig.savefig(OUT / "fig_heatmap.pdf", bbox_inches="tight")
    plt.close(fig)
    return obs, exp


if __name__ == "__main__":
    df = load()
    fig_growth(df); fig_shifts(df); fig_realism(df); obs, exp = fig_heatmap(df)
    # Function-level macros used in the text (data/function_numbers.tex).
    lines = ["% generated by scripts/figures.py - do not edit"]
    for f, (lab, _, ps) in FUNC.items():
        n = int(df.problem.isin(ps).sum())
        e = df[df.year.map(period) == "early"].problem.isin(ps).mean() * 100
        l = df[df.year.map(period) == "late"].problem.isin(ps).mean() * 100
        lines += [f"\\newcommand{{\\fn{lab}N}}{{{n:,}}}".replace(",", "{,}"),
                  f"\\newcommand{{\\fn{lab}Sh}}{{{100 * n / len(df):.1f}\\%}}",
                  f"\\newcommand{{\\fn{lab}Early}}{{{e:.1f}\\%}}",
                  f"\\newcommand{{\\fn{lab}Late}}{{{l:.1f}\\%}}"]
    (HERE / "data" / "function_numbers.tex").write_text("\n".join(lines) + "\n")
