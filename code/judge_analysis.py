"""
judge_analysis.py
-----------------
LLM-as-judge replication of the human mode rating study (paper.tex §5.6).

Inputs : output/llm-study-ratings-2026-10-05.xlsx and -2026-10-13.xlsx
         (two independent runs x 3 passes x 36 volumes = 6 passes, from A. Kalidindi)
         ../mode_tournament/unshuffled_results_corrected.csv (human ratings, corrected labels)
Reports: judge per-mode means; judge self-consistency across passes (ICC, exact agreement);
         judge mode identification; judge vs. human agreement on volume means;
         whether the judge reproduces the human mode effects (mixed model).
"""
import warnings, itertools
import numpy as np, pandas as pd
from scipy import stats
import statsmodels.formula.api as smf
warnings.filterwarnings("ignore")

SCALES = ["cohesion", "complexity", "readability", "overall"]
MODES = ["faithful", "simplified", "condensed"]

JUDGE_FILES = ["output/llm-study-ratings-2026-10-05.xlsx", "output/llm-study-ratings-2026-10-13.xlsx"]

def load_judge():
    parts, look = [], None
    for f in JUDGE_FILES:
        x = pd.ExcelFile(f)
        for s in ["Pass 1", "Pass 2", "Pass 3"]:
            parts.append(x.parse(s).assign(pass_=len(parts) + 1, run=f[-15:-5]))
        lk = x.parse("Volume Lookup")[["app_id", "source_pdf_id"]]
        assert look is None or look.equals(lk), "Volume Lookup differs between runs"
        look = lk
    j = pd.concat(parts)
    j = j.rename(columns={"pdf_id": "app_id", "mapped_true_mode": "mode"}).merge(look, on="app_id")
    j["doc"] = j.source_pdf_id.astype(int).astype(str).str.zfill(3)
    j["guess"] = j.mode_guess.str.strip().str.lower()
    return j

def load_human():
    h = pd.read_csv("../mode_tournament/unshuffled_results_corrected.csv")
    h = h[h["Overall (1-6)"].notna()].copy()
    for c, n in {"Overall (1-6)": "overall", "Cohesion (1-6)": "cohesion", "Complexity (1-6)": "complexity", "Readability (1-6)": "readability"}.items():
        h[n] = h[c].str.extract(r"^(\d)").astype(float)
    h["app_id"] = h.Link.str.extract(r"/volumes/[^/]+/(\d+)")[0].astype(int)
    h["mode"] = h["True Mode"]; h["doc"] = h["PDF Number Out of 100"].astype(str).str.zfill(3)
    h["guess"] = h["Mode Guess"].str.strip().str.lower()
    return h

def icc1k(units):
    k, ns = len(units), [len(u) for u in units]; N = sum(ns); gm = np.mean([v for u in units for v in u])
    msb = sum(n * (np.mean(u) - gm) ** 2 for u, n in zip(units, ns)) / (k - 1)
    msw = sum(sum((v - np.mean(u)) ** 2 for v in u) for u in units) / (N - k)
    n0 = (N - sum(n * n for n in ns) / N) / (k - 1)
    return (msb - msw) / (msb + (n0 - 1) * msw), (msb - msw) / msb

def qwk(a, b, lo=1, hi=6):
    """Quadratic weighted kappa on integer ratings in [lo, hi]."""
    from sklearn.metrics import cohen_kappa_score
    return cohen_kappa_score(np.asarray(a, int), np.asarray(b, int), weights="quadratic", labels=list(range(lo, hi + 1)))

def sb(r, k):
    """Spearman-Brown: reliability of a k-unit mean from single-unit reliability r."""
    return k * r / (1 + (k - 1) * r)

if __name__ == "__main__":
    j, h = load_judge(), load_human()
    K = j.pass_.nunique()
    print("judge model:", j.judge_model.unique(), "| passes:", j.pass_.nunique(), "| rows:", len(j))

    print("\n=== Judge per-mode means (SD) over all judgments")
    print(j.groupby("mode")[SCALES].agg(["mean", "std"]).round(2).loc[MODES].to_string())
    print("\n=== Judge scale use (value counts)")
    for s in SCALES: print(s, j[s].value_counts().sort_index().to_dict())

    print("\n=== Judge self-consistency across all passes (unit = volume)")
    for s in SCALES:
        units = [g[s].tolist() for _, g in j.groupby("app_id")]
        i1, ik = icc1k(units)
        exact = np.mean([len(set(u)) == 1 for u in units])
        print(f"{s:12s} ICC(1)={i1:.3f} ICC(1,k)={ik:.3f}  identical across passes: {exact:.0%}")
    gu = [g.guess.tolist() for _, g in j.groupby("app_id")]
    print(f"mode guess   identical across passes: {np.mean([len(set(u))==1 for u in gu]):.0%}")

    print(f"\n=== Apples-to-apples reliability: single unit, and mean of k units (judge k={K}; humans k~4 and Spearman-Brown to k={K})")
    hk = h.groupby("app_id").size().mean()
    for s in SCALES:
        ju = [g[s].tolist() for _, g in j.groupby("app_id")]; hu = [g[s].dropna().tolist() for _, g in h.groupby("app_id")]
        j1, jk = icc1k(ju); h1, hkk = icc1k(hu)
        print(f"{s:12s} judge ICC(1)={j1:.2f} ICC(1,{K})={jk:.2f} | human ICC(1)={h1:.2f} ICC(1,{hk:.1f})={hkk:.2f} SB->k={K}: {sb(h1,K):.2f}")

    print(f"\n=== QWK (ordinal agreement on the 1-6 scale)")
    wide = j.pivot(index="app_id", columns="pass_", values=SCALES)
    for s in SCALES:
        pw = [qwk(wide[s][a], wide[s][b]) for a, b in itertools.combinations(range(1, K + 1), 2)]
        print(f"{s:12s} judge pass-vs-pass mean QWK={np.mean(pw):.2f} (range {min(pw):.2f}-{max(pw):.2f})")
    hw = h.pivot_table(index="app_id", columns="Participant", values=SCALES)
    for s in SCALES:
        pw = []
        for a, b in itertools.combinations(hw[s].columns, 2):
            x = hw[s][[a, b]].dropna()
            if len(x) >= 6: pw.append(qwk(x[a], x[b]))
        print(f"{s:12s} human rater-vs-rater mean QWK={np.mean(pw):.2f} (n pairs={len(pw)})")
    jagg = j.groupby("app_id")[SCALES].mean().round().astype(int)
    for s in SCALES:
        pw = []
        for rater, g in h.groupby("Participant"):
            x = g.set_index("app_id")[s].to_frame("h").join(jagg[s].rename("j")).dropna()
            if len(x) >= 6: pw.append(qwk(x.h, x.j))
        single = []
        for p_ in range(1, K + 1):
            jp1 = j[j.pass_ == p_].set_index("app_id")[s]
            for rater, g in h.groupby("Participant"):
                x = g.set_index("app_id")[s].to_frame("h").join(jp1.rename("j")).dropna()
                if len(x) >= 6: single.append(qwk(x.h, x.j))
        hm = h.groupby("app_id")[s].mean().round().astype(int)
        print(f"{s:12s} QWK judge-mean vs each human rater={np.mean(pw):.2f} | single judge pass vs each human rater={np.mean(single):.2f} | judge-mean vs human-mean (N=36)={qwk(jagg[s], hm.reindex(jagg.index)):.2f}")

    print("\n=== Judge mode identification")
    for p, g in j.groupby("pass_"):
        hit = (g.guess == g["mode"]); print(f"pass {p}: {hit.sum()}/{len(g)} = {hit.mean():.3f}")
    maj = j.groupby("app_id").agg(mode=("mode", "first"), guess=("guess", lambda s: s.mode().iloc[0]),
                                  n_modes=("guess", lambda s: len(s.mode())))
    print(f"ties in majority vote: {(maj.n_modes > 1).sum()} volumes")
    allhit = (j.guess == j["mode"]); print(f"per-judgment: {allhit.sum()}/{len(j)} = {allhit.mean():.3f}")
    for r, g in j.groupby("run"): print(f"run {r}: {(g.guess==g['mode']).sum()}/{len(g)} per-judgment")
    hit = (maj.guess == maj["mode"]); print(f"majority vote: {hit.sum()}/36 = {hit.mean():.3f}  binomial p={stats.binomtest(int(hit.sum()),36,1/3).pvalue:.2e}")
    print(pd.crosstab(maj["mode"], maj.guess).reindex(index=MODES, columns=MODES, fill_value=0))
    po = hit.mean(); pe = sum((maj["mode"] == m).mean() * (maj.guess == m).mean() for m in MODES); print(f"kappa={(po-pe)/(1-pe):.3f}")

    print("\n=== Judge vs human: volume-level means (36 volumes)")
    jm = j.groupby("app_id")[SCALES].mean(); hm = h.groupby("app_id")[SCALES].mean()
    both = jm.join(hm, lsuffix="_j", rsuffix="_h")
    for s in SCALES:
        r, p = stats.pearsonr(both[f"{s}_j"], both[f"{s}_h"]); rho, _ = stats.spearmanr(both[f"{s}_j"], both[f"{s}_h"])
        ju = [g[s].tolist() for _, g in j.groupby("app_id")]; hu = [g[s].dropna().tolist() for _, g in h.groupby("app_id")]
        rel = icc1k(ju)[1] * icc1k(hu)[1]
        print(f"{s:12s} r={r:+.3f} (p={p:.3f})  rho={rho:+.3f}  disattenuated r={r/np.sqrt(rel):+.3f}   judge mean={both[f'{s}_j'].mean():.2f}  human mean={both[f'{s}_h'].mean():.2f}")
    print("\n=== Judge as one more rater: mean r with each human rater (shared volumes >= 6)")
    jp = j.groupby("app_id")[SCALES].mean()
    for s in SCALES:
        rs = []
        for rater, g in h.groupby("Participant"):
            x = g.set_index("app_id")[s].to_frame("h").join(jp[s].rename("j")).dropna()
            if len(x) >= 6: rs.append(stats.pearsonr(x.h, x.j)[0])
        single = []
        for p_ in range(1, K + 1):
            jp1 = j[j.pass_ == p_].set_index("app_id")[s]
            for rater, g in h.groupby("Participant"):
                x = g.set_index("app_id")[s].to_frame("h").join(jp1.rename("j")).dropna()
                if len(x) >= 6: single.append(stats.pearsonr(x.h, x.j)[0])
        print(f"{s:12s} mean r(judge mean of {K}, human rater)={np.nanmean(rs):+.3f}  mean r(single judge pass, human rater)={np.nanmean(single):+.3f}  (n raters={len(rs)})")
    print("\n=== Judge vs human mode guesses on same volumes")
    hg = h[h.guess.isin(MODES)].groupby("app_id").guess.agg(lambda s: s.mode().iloc[0])
    agree = (maj.guess == hg.reindex(maj.index)).mean(); print(f"majority human guess == majority judge guess: {agree:.0%}")

    print("\n=== Does the judge reproduce the mode effects?  rating ~ mode + (1|doc), pass-level rows")
    for s in SCALES:
        m1 = smf.mixedlm(f"{s} ~ C(mode, Treatment('faithful'))", j, groups="doc").fit(reml=False)
        m0 = smf.mixedlm(f"{s} ~ 1", j, groups="doc").fit(reml=False)
        lr = 2 * (m1.llf - m0.llf)
        eff = {k.split("[T.")[-1].rstrip("]"): f"{v:+.2f} (p={m1.pvalues[k]:.3f})" for k, v in m1.params.items() if "mode" in k}
        print(f"{s:12s} chi2(2)={lr:.2f} p={stats.chi2.sf(lr,2):.3f}  {eff}")
