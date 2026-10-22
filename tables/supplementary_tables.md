# Supplementary tables

Tables cut from the LERN 2027 submission for space.
LaTeX sources for each table are in this folder (`latex_*.tex`, `automated_indices_table.tex`).

## Table S1. Generation mode specifications

| | Faithful | Simplified | Condensed |
|---|---|---|---|
| Length target | 100% | 100% | ≈60% (55–65%) |
| Reading level | Source | Flesch–Kincaid grade 9–10 | Source |
| Chunk size (words) | 400–500 | 200–400 | 150–300 |
| Chunks per page | 2–4 | 3–6 | 4–8 |
| CRI answer length (sentences) | 2–3 | 1–2 | 1–2 |
| Text modification | None | Lexical / syntactic | Deletion |

Each mode adds its own rules to the shared validation checklist (`prompts/modes/`).

## Table S2. Prompting-strategy tournament (6 raters × 8 documents, 48 votes)

| Document | S1 Chain-of-thought | S2 Few-shot | S3 Validation |
|---|---|---|---|
| Communication 1 | 0 | 1 | **5** |
| Communication 2 | 0 | 2 | **4** |
| Psychology 1 | 0 | 2 | **4** |
| Psychology 2 | **3** | 2 | 1 |
| Public speaking | 1 | **4** | 1 |
| Lexical resources | **5** | 1 | 0 |
| USCIS 1 | 1 | 0 | **5** |
| USCIS 2 | 1 | 0 | **5** |
| **Total** | 11 (22.9%) | 12 (25.0%) | **25 (52.1%)** |

Justification themes (multi-coded): CRI field completeness 45.8% of comments; chunk-length appropriateness 43.8%; adherence to chunking rules 37.5%; CRI quality 35.4%; hallucinated page summaries 16.7% (present under all strategies).

## Table S3. Human ratings by mode, mean (SD), and omnibus likelihood-ratio χ²(2)

| Scale | Faithful (n=49) | Simplified (n=46) | Condensed (n=46) | χ²(2) |
|---|---|---|---|---|
| Cohesion | 4.49 (1.08) | 4.74 (0.95) | **5.02** (0.80) | 8.22* |
| Complexity | **3.90** (1.33) | 3.28 (1.41) | 3.59 (1.31) | 5.32† |
| Readability | 4.31 (1.08) | **4.87** (1.07) | 4.70 (0.94) | 9.33** |
| Overall | 4.37 (1.13) | **4.80** (1.00) | 4.61 (1.11) | 5.31† |

† p < .08, * p < .05, ** p < .01. Mixed model with crossed random intercepts for source document and rater.

## Table S4. Human mode identification (141 guesses)

| True \ Guessed | Faithful | Simplified | Condensed | Recall |
|---|---|---|---|---|
| Faithful | **27** | 7 | 15 | .55 |
| Simplified | 12 | **22** | 12 | .48 |
| Condensed | 20 | 10 | **16** | .35 |

Accuracy 46.1% (chance 33.3%), binomial p = .002, Cohen's κ = .19.

## Table S5. LLM judge replication (gpt-5.6-sol, 6 passes, 36 volumes)

| | Cohesion | Complexity | Readability | Overall |
|---|---|---|---|---|
| *Judge means by mode (6 passes)* | | | | |
| Faithful | 5.04 | 5.01 | 4.07 | 4.44 |
| Simplified | 5.33 | 3.62 | 5.06 | 4.72 |
| Condensed | 5.40 | 4.79 | 4.78 | 4.65 |
| *Reliability: single unit* | | | | |
| Judge, one pass: ICC(1) | .67 | .89 | .84 | .87 |
| Judge, pass vs. pass: mean QWK | .66 | .88 | .84 | .87 |
| Human, one rater: ICC(1) | .29 | .41 | .31 | .20 |
| Human, rater vs. rater: mean QWK | .28 | .19 | .20 | .15 |
| *Reliability: aggregate used in analyses* | | | | |
| Judge, mean of 6 passes: ICC(1,6) | .92 | .98 | .97 | .98 |
| Humans, mean of ≈4 raters: ICC(1,k) | .61 | .73 | .64 | .50 |
| *Judge–human agreement: aggregates (N = 36 volumes)* | | | | |
| r, judge mean vs. human mean | .32 | .43** | .49** | .33* |
| ρ, judge mean vs. human mean | .27 | .45** | .59** | .36* |
| r, disattenuated | .43 | .51 | .62 | .48 |
| QWK, judge mean vs. human mean | .12 | .20 | .42 | .28 |
| *Judge–human agreement: judge as one more rater* | | | | |
| mean r, one judge pass vs. each human rater | .21 | .38 | .32 | .21 |
| mean r, human vs. human (reference) | .33 | .25 | .23 | .18 |
| mean QWK, one judge pass vs. each human rater | .14 | .29 | .26 | .18 |
| mean QWK, human vs. human (reference) | .28 | .19 | .20 | .15 |

ICC(1): reliability of a single pass or rater. ICC(1,k): reliability of the mean of k passes or raters. QWK: quadratic weighted kappa, mean over pairs sharing ≥ 6 volumes. Disattenuated r divides by √(ICC_judge · ICC_human) of the two aggregates. * p < .05, ** p < .01.

Mode identification: judge majority vote correct for 33/36 volumes (92%, κ = .88); 196/216 individual judgments (91%). All errors were Condensed volumes.

## Table S6. Automated indices: tools, versions, and the 20 indices

| Tool | Construct | Indices (variable name in `data/salat_indices_300_texts.csv`) |
|---|---|---|
| TAACO 2.1.3 | Cohesion (4) | adjacent-sentence argument overlap (`adjacent_overlap_2_argument_sent`); adjacent-sentence LSA similarity (`lsa_2_all_sent`); basic connectives (`basic_connectives`); all connectives (`all_connective`) |
| TAALES 2.8.1 | Lexical sophistication (9) | COCA news log frequency, all words (`COCA_news_Frequency_Log_AW`); word frequency (`Freq_N`); COCA bigram association ΔP (`COCA_news_bi_DP`); proportion of bigrams in top 30k (`COCA_news_bi_prop_30k`); Academic Word List coverage (`All_AWL_Normed`); age of acquisition, all words (`Kuperman_AoA_AW`); concreteness, all words (`Brysbaert_Concreteness_Combined_AW`); contextual distinctiveness, content words (`McD_CD_CW`); lexical decision RT z-score (`LD_Mean_RT_Zscore`) |
| TAASSC 1.3.8 | Syntactic complexity (3) | dependents per clause (`dep_per_cl`); coordinating conjunctions per clause (`cc_per_cl`); clausal complements per clause (`ccomp_per_cl`) |
| textstat (direct) | Length and readability (4) | word count; mean sentence length; Flesch–Kincaid grade level; Flesch reading ease (computed in `code/lexical_analysis.py`) |

## Table S7. Automated indices by mode

Full results (means, SDs, χ², Holm-corrected p, pairwise d_z) are in `data/automated_index_results.csv`; the LaTeX table is `automated_indices_table.tex`.

## Figure S1. Length of each Simplified and Condensed volume relative to its Faithful volume

`figures/length_ratio.png`. Condensed volumes average 59% of Faithful length (median 58%, SD 0.22; 27 of 100 within the 55–65% target). Simplified volumes average 91% (SD 0.24) despite the no-omission rule.

## Figure S2. Mode flow (human guesses vs. true mode)

`figures/mode_flow.png`.
