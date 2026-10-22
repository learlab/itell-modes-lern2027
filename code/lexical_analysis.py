"""
lexical_analysis.py
-------------------
Automated discourse analysis for paper.tex §6 (Automated Discourse Analysis).

Inputs : output/results_all_salat.csv   (TAACO + TAALES + TAASSC merged, 300 rows)
         txt/prompt_modes_txt_updated.zip (300 texts; used for sentence length + Flesch-Kincaid)
Outputs: output/lexical_results.csv     one row per index: means, SDs, LRT, pairwise, effect sizes
         output/lexical_table.tex       LaTeX rows for Table 5

Model  : index ~ mode + (1 | source document), ML fit; LRT vs intercept-only,
         Holm-corrected across indices.  Pairwise contrasts from the model,
         Holm-corrected within index.  Effect size = Cohen's d on document-level
         paired differences (100 pairs).
Features follow Crossley's April 2026 R selection (itell_salat_modes_analysis.Rmd)
plus computed length/readability indices.
"""
import re, zipfile, warnings
import numpy as np, pandas as pd, textstat
from scipy import stats
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests
warnings.filterwarnings("ignore")

MODES = ["faithful", "simplified", "condensed"]
FEATURES = [  # (column, family, label)
    ("nwords",                            "Length",     "Word count"),
    ("mean_sent_len",                     "Length",     "Mean sentence length (words)"),
    ("fk_grade",                          "Readability","Flesch--Kincaid grade level"),
    ("flesch_ease",                       "Readability","Flesch reading ease"),
    ("dep_per_cl",                        "Syntax",     "Dependents per clause"),
    ("cc_per_cl",                         "Syntax",     "Coordinating conj.\\ per clause"),
    ("ccomp_per_cl",                      "Syntax",     "Clausal complements per clause"),
    ("adjacent_overlap_2_argument_sent",  "Cohesion",   "Adjacent-sentence argument overlap (2)"),
    ("lsa_2_all_sent",                    "Cohesion",   "Adjacent-sentence LSA similarity (2)"),
    ("basic_connectives",                 "Cohesion",   "Basic connectives"),
    ("all_connective",                    "Cohesion",   "All connectives"),
    ("COCA_news_Frequency_Log_AW",        "Lexical",    "COCA news log frequency (AW)"),
    ("Freq_N",                            "Lexical",    "Word frequency (Freq\\_N)"),
    ("COCA_news_bi_DP",                   "Lexical",    "COCA bigram association (DP)"),
    ("COCA_news_bi_prop_30k",             "Lexical",    "Bigram proportion in top 30k"),
    ("All_AWL_Normed",                    "Lexical",    "Academic Word List coverage"),
    ("Kuperman_AoA_AW",                   "Lexical",    "Age of acquisition (AW)"),
    ("Brysbaert_Concreteness_Combined_AW","Lexical",    "Concreteness (AW)"),
    ("McD_CD_CW",                         "Lexical",    "Contextual distinctiveness (CW)"),
    ("LD_Mean_RT_Zscore",                 "Lexical",    "Lexical decision RT ($z$)"),
]

def load():
    df = pd.read_csv("output/results_all_salat.csv")
    df["doc"] = df.filename.str.extract(r"^(\d{3})_")[0]
    df["mode"] = df.filename.str.extract(r"_(\w+)\.txt$")[0]
    z = zipfile.ZipFile("txt/prompt_modes_txt_updated.zip")
    txt = {}
    for n in z.namelist():
        m = re.search(r"(\d{3}_(?:faithful|simplified|condensed))\.txt$", n)
        if m: txt[m.group(1) + ".txt"] = z.read(n).decode("utf-8", "ignore")
    df["text"] = df.filename.map(txt)
    df["mean_sent_len"] = df.text.map(lambda s: len(s.split()) / max(1, textstat.sentence_count(s)))
    df["fk_grade"] = df.text.map(textstat.flesch_kincaid_grade)
    df["flesch_ease"] = df.text.map(textstat.flesch_reading_ease)
    return df

def analyse(df):
    rows = []
    for col, fam, label in FEATURES:
        d = df[["doc", "mode", col]].dropna().copy()
        m1 = smf.mixedlm(f"{col} ~ C(mode, Treatment('faithful'))", d, groups="doc").fit(reml=False)
        m0 = smf.mixedlm(f"{col} ~ 1", d, groups="doc").fit(reml=False)
        lr = 2 * (m1.llf - m0.llf); p = stats.chi2.sf(lr, 2)
        wide = d.pivot(index="doc", columns="mode", values=col)
        row = dict(index=col, family=fam, label=label, chi2=lr, p=p)
        for m in MODES:
            row[f"{m}_mean"] = wide[m].mean(); row[f"{m}_sd"] = wide[m].std()
        pairs = {}
        for a, b in [("faithful", "simplified"), ("faithful", "condensed"), ("simplified", "condensed")]:
            diff = wide[b] - wide[a]
            dz = diff.mean() / diff.std()
            t, pp = stats.ttest_rel(wide[b], wide[a])
            pairs[f"{a[:1]}{b[:1]}"] = (dz, pp)
        pp_adj = multipletests([v[1] for v in pairs.values()], method="holm")[1]
        for (k, (dz, _)), pa in zip(pairs.items(), pp_adj):
            row[f"d_{k}"] = dz; row[f"p_{k}"] = pa
        rows.append(row)
    res = pd.DataFrame(rows)
    res["p_holm"] = multipletests(res.p, method="holm")[1]
    return res

def stars(p): return "$^{***}$" if p < .001 else "$^{**}$" if p < .01 else "$^{*}$" if p < .05 else ""
def fmt(x): return f"{x:.2f}" if abs(x) >= 0.01 or x == 0 else f"{x:.3f}"

def latex(res):
    out = []
    for fam, g in res.groupby("family", sort=False):
        out.append(f"    \\multicolumn{{6}}{{l}}{{\\emph{{{fam}}}}} \\\\")
        for _, r in g.iterrows():
            best = max(MODES, key=lambda m: r[f"{m}_mean"])
            cells = []
            for m in MODES:
                c = f"{fmt(r[f'{m}_mean'])} ({fmt(r[f'{m}_sd'])})"
                cells.append(c)
            sig = f"{r.chi2:.1f}{stars(r.p_holm)}"
            # pairwise letters: which contrasts significant
            sigs = [k for k in ("fs", "fc", "sc") if r[f"p_{k}"] < .05]
            lab = {"fs": "F$\\neq$S", "fc": "F$\\neq$C", "sc": "S$\\neq$C"}
            out.append(f"    {r.label} & {cells[0]} & {cells[1]} & {cells[2]} & {sig} & {', '.join(lab[k] for k in sigs) or '--'} \\\\")
    return "\n".join(out)

if __name__ == "__main__":
    df = load()
    res = analyse(df)
    res.to_csv("output/lexical_results.csv", index=False)
    open("output/lexical_table.tex", "w").write(latex(res))
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
    show = res[["label", "faithful_mean", "simplified_mean", "condensed_mean", "chi2", "p_holm", "d_fs", "p_fs", "d_fc", "p_fc", "d_sc", "p_sc"]].round(3)
    print(show.to_string())
    # compliance: FK grade for simplified
    print("\nSimplified FK grade: mean %.2f, SD %.2f, in 9-10: %d/100, <9: %d, >10: %d" % (
        df[df["mode"] == "simplified"].fk_grade.mean(), df[df["mode"] == "simplified"].fk_grade.std(),
        df[(df["mode"] == "simplified") & df.fk_grade.between(9, 10.99)].shape[0],
        (df[df["mode"] == "simplified"].fk_grade < 9).sum(), (df[df["mode"] == "simplified"].fk_grade >= 11).sum()))
    print("Faithful FK grade: mean %.2f, SD %.2f" % (df[df["mode"] == "faithful"].fk_grade.mean(), df[df["mode"] == "faithful"].fk_grade.std()))
