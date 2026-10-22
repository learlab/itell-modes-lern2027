"""make_sankey.py — alluvial diagrams of true mode -> guessed mode, humans vs LLM judge.
Outputs figures/mode_flow.pdf and figures/mode_flow.png"""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch

COL = {"faithful": "#2a78d6", "simplified": "#eb6834", "condensed": "#1baf7a"}
LAB = {"faithful": "Faithful", "simplified": "Simplified", "condensed": "Condensed"}
ORDER = ["faithful", "simplified", "condensed"]
plt.rcParams.update({"font.family": "serif", "font.size": 9})

def counts_human():
    h = pd.read_csv("../mode_tournament/unshuffled_results_corrected.csv")
    h = h[h["Overall (1-6)"].notna()]
    g = h["Mode Guess"].str.strip().str.lower()
    d = h.assign(guess=g)[g.isin(ORDER)]
    return pd.crosstab(d["True Mode"], d["guess"]).reindex(index=ORDER, columns=ORDER, fill_value=0)

def counts_judge():
    x = pd.ExcelFile("output/llm-study-ratings-2026-10-05.xlsx")
    j = pd.concat([x.parse(s) for s in ["Pass 1", "Pass 2", "Pass 3"]], ignore_index=True)
    j["guess"] = j.mode_guess.str.strip().str.lower()
    return pd.crosstab(j["mapped_true_mode"], j["guess"]).reindex(index=ORDER, columns=ORDER, fill_value=0)

def alluvial(ax, ct, title):
    tot = ct.values.sum(); gap = 0.03; bw = 0.08
    def blocks(sizes):  # returns {mode: (y0, y1)} stacked top to bottom
        out, y = {}, 1.0
        for m, s in zip(ORDER, sizes):
            hgt = s / tot * (1 - gap * 2); out[m] = (y - hgt, y); y -= hgt + gap
        return out
    L = blocks(ct.sum(axis=1).values); R = blocks(ct.sum(axis=0).values)
    # bars + labels
    for m in ORDER:
        for side, B, x in (("L", L, 0.0), ("R", R, 1.0 - bw)):
            y0, y1 = B[m]
            ax.add_patch(plt.Rectangle((x, y0), bw, y1 - y0, color=COL[m], lw=0))
            n = ct.loc[m].sum() if side == "L" else ct[m].sum()
            ax.text(x - 0.02 if side == "L" else x + bw + 0.02, (y0 + y1) / 2,
                    f"{LAB[m]}\n{n}", ha="right" if side == "L" else "left", va="center", fontsize=8.5)
    # flows
    lcur = {m: L[m][1] for m in ORDER}; rcur = {m: R[m][1] for m in ORDER}
    for src in ORDER:
        for dst in ORDER:
            v = ct.loc[src, dst]
            if v == 0: continue
            hgt = v / tot * (1 - gap * 2)
            ly1, ly0 = lcur[src], lcur[src] - hgt; ry1, ry0 = rcur[dst], rcur[dst] - hgt
            lcur[src] -= hgt; rcur[dst] -= hgt
            x0, x1 = bw, 1.0 - bw; cx = (x0 + x1) / 2
            verts = [(x0, ly1), (cx, ly1), (cx, ry1), (x1, ry1), (x1, ry0), (cx, ry0), (cx, ly0), (x0, ly0), (x0, ly1)]
            codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.CLOSEPOLY]
            ax.add_patch(PathPatch(Path(verts, codes), facecolor=COL[src], alpha=0.75 if src == dst else 0.32, lw=0))
            box = dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.9)
            if src == dst:
                ax.text(cx, (ly0 + ly1 + ry0 + ry1) / 4, str(v), ha="center", va="center",
                        fontsize=9.5, fontweight="bold", color="#222", bbox=box)
            elif v / tot >= 0.04:
                ax.text(x0 + 0.05, (ly0 + ly1) / 2, str(v), ha="left", va="center",
                        fontsize=8.5, color="#222", bbox=box)
            elif v > 0:   # thin flow: label at destination end, where it does not stack with siblings
                ax.text(x1 - 0.05, (ry0 + ry1) / 2, str(v), ha="right", va="center",
                        fontsize=8.5, color="#222", bbox=box)
    acc = np.trace(ct.values) / tot
    ax.set_title(f"{title}\naccuracy {acc:.0%} (n = {tot})", fontsize=9.5, pad=6)
    ax.text(bw / 2, 1.03, "True mode", ha="center", fontsize=8, color="#555")
    ax.text(1 - bw / 2, 1.03, "Guessed", ha="center", fontsize=8, color="#555")
    ax.set_xlim(-0.32, 1.32); ax.set_ylim(-0.02, 1.08); ax.axis("off")

fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.4))
alluvial(axes[0], counts_human(), "Human raters")
alluvial(axes[1], counts_judge(), "LLM judge (3 passes)")
fig.tight_layout(w_pad=1.5)
fig.savefig("figures/mode_flow.pdf", bbox_inches="tight")
fig.savefig("figures/mode_flow.png", dpi=220, bbox_inches="tight")
print("ok")
