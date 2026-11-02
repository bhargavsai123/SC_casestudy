"""Slide-sized chart of the adaptive weights (large type, direct labels)."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ADAPT = Path("content/gaapo_outputs_v2/adaptive")
FIG = Path("content/gaapo_outputs_v2/figures")

ORDER = ["random_mutation", "apo", "opro", "fewshot", "crossover"]
NICE = {"random_mutation": "mutation", "apo": "APO", "opro": "OPRO",
        "fewshot": "few-shot", "crossover": "crossover"}
COLOR = {"random_mutation": "#2a6f97", "apo": "#c1554f", "opro": "#e0a458",
         "fewshot": "#4f8a5b", "crossover": "#8a6aa8"}

frames = []
for f in sorted(ADAPT.glob("log_adaptive_r*.csv")):
    d = pd.read_csv(f)
    rows = []
    for _, r in d.iterrows():
        w = json.loads(r["weights_json"])
        rows.append({"generation": int(r["generation"]), **{k: w.get(k) for k in ORDER}})
    tidy = pd.DataFrame(rows).groupby("generation").first().reset_index()
    tidy["repeat"] = f.stem
    frames.append(tidy)

allw = pd.concat(frames)
mean = allw.groupby("generation")[ORDER].mean()

plt.rcParams.update({"font.size": 13, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.edgecolor": "#9aa5b1",
                     "xtick.color": "#5a6b7b", "ytick.color": "#5a6b7b",
                     "axes.labelcolor": "#1b2733", "figure.dpi": 200})

fig, ax = plt.subplots(figsize=(6.0, 4.2))
SHIFT = {"random_mutation": 0.0, "apo": 0.012, "opro": -0.012,
         "fewshot": 0.013, "crossover": -0.011}
for k in ORDER:
    ax.plot(mean.index, mean[k], color=COLOR[k], lw=2.0, marker="o", ms=3.5)
    ax.annotate(NICE[k], xy=(mean.index[-1] + 0.10, mean[k].iloc[-1] + SHIFT[k]),
                fontsize=12, color=COLOR[k], va="center", fontweight="bold")

ax.set_xlabel("generation")
ax.set_ylabel("share of the budget")
ax.set_xlim(-0.25, 7.6)
ax.set_ylim(0.05, 0.44)
ax.set_xticks(range(len(mean)))
ax.annotate("40 % → 24 %", xy=(4.6, mean["random_mutation"].iloc[4]),
            xytext=(2.9, 0.335), fontsize=12, color="#2a6f97",
            arrowprops=dict(arrowstyle="->", color="#2a6f97", lw=1.1))
ax.annotate("10 % → 16 %", xy=(4.2, mean["fewshot"].iloc[4]),
            xytext=(2.6, 0.105), fontsize=12, color="#4f8a5b",
            arrowprops=dict(arrowstyle="->", color="#4f8a5b", lw=1.1))
fig.tight_layout()
fig.savefig(FIG / "slide_adaptive_weights.png", bbox_inches="tight")
print("wrote", FIG / "slide_adaptive_weights.png")
print(mean.round(3).to_string())


# ---------------------------------------------------------------- ablation, slide-sized
abl = pd.read_csv("content/gaapo_outputs_v2/ablation/ablation_summary.csv")
order = ["full_hybrid", "without_opro", "without_apo", "without_random_mutation"]
nice = ["full\nhybrid", "without\nOPRO", "without\nAPO", "without\nmutation"]
abl = abl.set_index("config").loc[order]

fig, ax = plt.subplots(figsize=(5.6, 4.2))
x = np.arange(len(order))
w = 0.36
ax.bar(x - w / 2, abl.best_val_mean, w, yerr=abl.best_val_std, capsize=3,
       color="#2a6f97", label="validation")
ax.bar(x + w / 2, abl.test_mean, w, yerr=abl.test_std, capsize=3,
       color="#e0a458", label="held-out test")
ax.set_xticks(x)
ax.set_xticklabels(nice, fontsize=11)
ax.set_ylabel("score")
ax.set_ylim(0, 0.36)
ax.legend(fontsize=11, frameon=False, loc="upper right")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.axhline(0.232, color="#9aa5b1", lw=0.8, ls=":")
fig.tight_layout()
fig.savefig(FIG / "slide_ablation.png", bbox_inches="tight")
print("wrote", FIG / "slide_ablation.png")
