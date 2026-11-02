"""Figure for the post-hoc validation-vs-test probe (reads probe/ artifacts)."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT = Path("content/gaapo_outputs_v2/probe")
FIG = Path("content/gaapo_outputs_v2/figures")

df = pd.read_csv(OUT / "probe_runs.csv")
S = json.loads((OUT / "probe_summary.json").read_text())

v = df.validation_score.values
t = df.test_score.values
leader = int(np.argmax(v))

plt.rcParams.update({
    "font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
    "axes.titlesize": 10, "figure.dpi": 200,
    "axes.edgecolor": "#9aa5b1", "axes.labelcolor": "#1b2733",
    "xtick.color": "#5a6b7b", "ytick.color": "#5a6b7b",
})

fig, (ax, ax2) = plt.subplots(1, 2, figsize=(9.8, 4.0),
                              gridspec_kw={"width_ratios": [1.55, 1]})

# ---------------------------------------------------------------- A: scatter
se = np.sqrt(v * (1 - v) / 50)
ax.errorbar(v, t, xerr=1.96 * se, fmt="none", ecolor="#c9ced6", elinewidth=0.9, zorder=1)
ax.scatter(v, t, s=52, color="#2a6f97", edgecolor="white", linewidth=0.7, zorder=3,
)
ax.scatter(0.10, 0.09, s=64, marker="D", facecolor="white", edgecolor="#5a6b7b",
           linewidth=1.1, zorder=3)

ax.scatter([v[leader]], [t[leader]], s=200, facecolor="none", edgecolor="#c1554f",
           linewidth=1.7, zorder=4)
ax.annotate("selected on validation\n(highest validation score)",
            xy=(v[leader], t[leader]), xytext=(v[leader] - 0.20, t[leader] - 0.15),
            fontsize=7.5, color="#c1554f",
            arrowprops=dict(arrowstyle="->", color="#c1554f", lw=0.9))

best = int(np.argmax(t))
ax.annotate("best on held-out test", xy=(v[best], t[best]),
            xytext=(v[best] - 0.115, t[best] + 0.095), fontsize=7.5, color="#2a6f97",
            arrowprops=dict(arrowstyle="->", color="#2a6f97", lw=0.9))

ax.axvspan(0.395, 0.465, color="#c1554f", alpha=0.07, zorder=0)
ax.text(0.487, 0.175, "tied on validation\n(7 prompts)", fontsize=7, color="#c1554f",
        ha="left", va="center", rotation=90)

ax.set_xlabel("validation score  (50 examples — the selection signal)")
ax.set_ylabel("test score  (200 examples, held out)")
ax.set_title("A. Ordering on 50 examples does not carry over")
ax.set_xlim(0.02, 0.54)
ax.set_ylim(0.0, 0.50)
ax.annotate("seed prompt", xy=(0.10, 0.09), xytext=(0.115, 0.045), fontsize=7,
            color="#5a6b7b",
            arrowprops=dict(arrowstyle="->", color="#5a6b7b", lw=0.7))
ax.text(0.035, 0.455,
        f"Spearman ρ = {S['spearman_rho']:.2f}  (n = {S['n_prompts']}, n.s.)\n"
        f"mean validation − test = {S['mean_val_minus_test']:+.02f}",
        fontsize=7.5, va="top",
        bbox=dict(boxstyle="round,pad=0.35", fc="#f4f6f8", ec="#d5dae1", lw=0.6))

# ---------------------------------------------------------------- B: the tied top
top = df[df.validation_score >= S["within_noise_validation_range"][0]].copy()
order = np.argsort(-top.validation_score.values)
xt = np.arange(len(top))
ax2.axhspan(S["within_noise_test_range"][0], S["within_noise_test_range"][1],
            color="#2a6f97", alpha=0.10, zorder=0)
ax2.scatter(xt, top.test_score.values[order], s=54, color="#2a6f97",
            edgecolor="white", linewidth=0.7, zorder=3)
for i, (_, row) in enumerate(top.iloc[order].iterrows()):
    if row.validation_score == top.validation_score.max():
        ax2.scatter([i], [row.test_score], s=180, facecolor="none", edgecolor="#c1554f",
                    linewidth=1.5, zorder=4)
ax2.set_xticks(xt)
ax2.set_xticklabels([f"{x:.2f}" for x in top.validation_score.values[order]], fontsize=8)
ax2.set_xlabel("their validation scores (all tied within noise)")
ax2.set_ylabel("test score")
ax2.set_title("B. Seven prompts tie on validation;\ntheir true scores do not")
ax2.set_ylim(0.15, 0.40)
hi_i = int(np.argmax(top.test_score.values[order]))
lo_i = int(np.argmin(top.test_score.values[order]))
ax2.annotate(f"{top.test_score.values[order][hi_i]:.2f}",
             xy=(hi_i, top.test_score.values[order][hi_i]),
             xytext=(hi_i, top.test_score.values[order][hi_i] + 0.022),
             fontsize=7.5, color="#2a6f97", ha="center")
ax2.annotate(f"{top.test_score.values[order][lo_i]:.2f}",
             xy=(lo_i, top.test_score.values[order][lo_i]),
             xytext=(lo_i + 0.45, top.test_score.values[order][lo_i] - 0.022),
             fontsize=7.5, color="#c1554f", ha="left")

fig.tight_layout()
fig.savefig(FIG / "probe_validation_vs_test.png", bbox_inches="tight")
print("wrote", FIG / "probe_validation_vs_test.png")
