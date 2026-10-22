"""
make_figures.py — figures for paper.tex
  figures/ratings_by_mode.pdf   mean ± 95% CI per mode, four rating scales
  figures/length_ratio.pdf      per-document length ratio vs Faithful, with target bands
Run from sigdial/:  python make_figures.py
"""
import re, zipfile, statistics as st
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

COL = {"faithful": "#2a78d6", "simplified": "#eb6834", "condensed": "#1baf7a"}
LAB = {"faithful": "Faithful", "simplified": "Simplified", "condensed": "Condensed"}
ORDER = ["faithful", "simplified", "condensed"]
plt.rcParams.update({"font.family": "serif", "font.size": 8, "axes.edgecolor": "#888",
                     "axes.linewidth": 0.6, "xtick.color": "#444", "ytick.color": "#444",
                     "axes.labelcolor": "#222", "text.color": "#222"})

# ---------- Figure 1: ratings ----------
df = pd.read_csv("../mode_tournament/unshuffled_results_corrected.csv")
df = df[df["True Mode"].notna()].copy()
scales = {"Cohesion (1-6)": "Cohesion", "Complexity (1-6)": "Complexity",
          "Readability (1-6)": "Readability", "Overall (1-6)": "Overall"}
for c in scales: df[c] = df[c].str.extract(r"^(\d)").astype(float)
df["mode"] = df["True Mode"]

fig, axes = plt.subplots(1, 4, figsize=(6.3, 1.9), sharey=True)
for ax, (col, name) in zip(axes, scales.items()):
    for i, m in enumerate(ORDER):
        v = df.loc[df["mode"] == m, col].dropna()
        mean, ci = v.mean(), 1.96 * v.std(ddof=1) / np.sqrt(len(v))
        ax.errorbar(i, mean, yerr=ci, fmt="o", ms=5, color=COL[m], ecolor=COL[m],
                    elinewidth=1.2, capsize=3, capthick=1.2)
        ax.text(i, mean + ci + 0.08, f"{mean:.2f}", ha="center", va="bottom", fontsize=7)
    ax.set_title(name, fontsize=8.5, pad=4)
    ax.set_xticks(range(3)); ax.set_xticklabels(["Faith.", "Simp.", "Cond."])
    ax.set_xlim(-0.6, 2.6); ax.set_ylim(3.0, 5.6)
    ax.grid(axis="y", color="#e5e5e5", lw=0.5); ax.set_axisbelow(True)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
axes[0].set_ylabel("Mean rating (1–6)")
fig.tight_layout(w_pad=0.6)
fig.savefig("figures/ratings_by_mode.pdf", bbox_inches="tight")

# ---------- Figure 2: length ratios ----------
z = zipfile.ZipFile("txt/prompt_modes_txt_updated.zip")
wc = {m: {} for m in ORDER}
for n in z.namelist():
    mt = re.search(r"(\d{3})_(faithful|simplified|condensed)\.txt$", n)
    if mt: wc[mt.group(2)][mt.group(1)] = len(z.read(n).decode("utf-8", "ignore").split())
ids = sorted(wc["faithful"])
ratio = {m: np.array([wc[m][i] / wc["faithful"][i] for i in ids]) for m in ("condensed", "simplified")}

fig, ax = plt.subplots(figsize=(3.1, 2.0))
rng = np.random.default_rng(0)
rows = {"condensed": 0, "simplified": 1}
ax.axvspan(0.55, 0.65, color=COL["condensed"], alpha=0.12, lw=0)
ax.axvline(1.0, color=COL["simplified"], lw=1, ls=(0, (3, 2)))
for m, y in rows.items():
    r = ratio[m]
    ax.scatter(r, y + rng.uniform(-0.18, 0.18, len(r)), s=9, color=COL[m], alpha=0.65, lw=0)
    med = np.median(r)
    ax.plot([med, med], [y - 0.3, y + 0.3], color="#222", lw=1.4)
    ax.text(1.62, y, f"{LAB[m]}\nmedian {med:.2f}", va="center", ha="left", fontsize=7)
ax.text(0.60, 1.62, "target\n55–65%", ha="center", va="center", fontsize=6.5, color="#1a7a55")
ax.text(1.03, 1.62, "target 100%", ha="left", va="center", fontsize=6.5, color="#b04a1e")
ax.set_yticks([]); ax.set_ylim(-0.8, 1.8); ax.set_xlim(0.15, 1.6)
ax.set_xlabel("Length relative to Faithful volume")
ax.set_xticks([0.25, 0.5, 0.75, 1.0, 1.25, 1.5])
for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
ax.grid(axis="x", color="#e5e5e5", lw=0.5); ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig("figures/length_ratio.pdf", bbox_inches="tight")
print("ok")
