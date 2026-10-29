# Supplementary material: Developing Reading Modes for LLM-Generated Instructional Texts

Tobasum Mandal, Scott A. Crossley, Langdon Holmes, Wesley Morris, and Adithya Kalidindi, Vanderbilt University. Submitted to LERN 2027.

The paper tests three AI generation modes for the iTELL intelligent textbook platform (Faithful, Simplified, Condensed) with three research questions: RQ1, do human raters perceive the modes as different and can they tell them apart; RQ2, can an LLM judge reproduce the human judgments; RQ3, do the modes differ on linguistic features as predicted. This repository holds everything referenced from the paper as supplementary material, plus the prompts, data, and code needed to reproduce the analyses.

## Where to find what the paper points to

| Paper reference | Location |
|---|---|
| Mode specifications and the prompting-strategy comparison (Text Generation) | `tables/supplementary_tables.md` Tables S1–S2; prompts in `prompts/` |
| Human ratings by mode and the mode-identification confusion matrix (RQ1) | Tables S3–S4 |
| Full LLM-judge reliability and agreement table (RQ2) | Table S5 |
| The 16 SALAT indices with definitions and variable names (RQ3 Materials) | Table S6 |
| Automated indices by mode, all 20 (RQ3 Results) | Table S7 and `data/automated_index_results.csv` |
| Figure S1, volume length relative to Faithful | `figures/length_ratio.png` |
| Figure S2, human mode guesses vs. true mode | `figures/mode_flow.png` |

## Layout

| Folder | Contents |
|---|---|
| `tables/` | `supplementary_tables.md` (Tables S1–S7, Figures S1–S2) and LaTeX sources. |
| `figures/` | Ratings by mode (paper Figure 1), length ratio (S1), mode-flow Sankey (S2), as PDF and PNG. |
| `prompts/modes/` | The generation prompt as sent to Gemini 2.5 Flash: `base_strategy3.md` (the validation checklist shared by all modes) plus the `faithful`, `simplified`, and `condensed` mode modules. |
| `prompts/judge/` | The LLM judge system prompt and a note on exactly what the judge received. |
| `prompts/strategies/` | The three prompting strategies compared before the modes were built (chain-of-thought, few-shot, validation) and the reference volume used as the worked example. |
| `data/` | See below. |
| `rated_volumes/` | The 36 volumes (12 source PDFs × 3 modes) rated by humans and the LLM judge, as the JSON fetched from the iTELL CMS and as plain text. `README.txt` maps each file to its source PDF and mode. |
| `code/` | Analysis scripts. |

Prompts and code are released in full. The judge prompt is the research instrument used for this study, not a production component.

## Data

- `data/human_ratings.csv`: one row per rater × volume (168 rows; 141 contain ratings, two enrolled raters returned none and one omitted three volumes). Raters are pseudonymized (`R01`–`R14`). Columns: four 6-point ratings, mode guess, free-text content and bug comments, true mode, PDF id, platform volume id.
- `data/llm_judge_ratings_run1_2026-10-05.xlsx`, `..._run2_2026-10-13.xlsx`: the LLM judge (gpt-5.6-sol via the OpenAI Responses API, reasoning effort medium), three passes per run, with the judge's explanations. The two runs used the same prompt and settings and are pooled as six passes in the paper. Temperature and top-p were not set in the request and so took the API defaults.
- `data/salat_indices_300_texts.csv`: TAACO 2.1.3, TAALES 2.8.1, and TAASSC 1.3.8 output for all 300 generated texts.
- `data/automated_index_results.csv`: per-index mixed-model results (means, SDs, likelihood-ratio χ², Holm-corrected p, pairwise Cohen's d_z).
- `data/generated_texts_300.zip`: plain-text export of the 300 generated texts (100 PDFs × 3 modes; quick questions excluded, paragraph boundaries not preserved) used for the automated analysis. Source PDFs are third-party documents and are not redistributed.

## Code

Scripts were run from the paper's working directory and reference the original paths; adjust the input paths at the top of each file.

- `judge_analysis.py`: ICC(1), ICC(1,6), QWK, disattenuated r, single-pass vs. single-rater comparisons, mode identification, mixed models for the judge (RQ2).
- `lexical_analysis.py`: mixed models and pairwise contrasts for the 20 automated indices (RQ3); writes `automated_index_results.csv` and the LaTeX table.
- `make_figures.py`, `make_sankey.py`: figures.
- `collate.py`, `run_taaco.py`, `export_txt.py`: merging SALAT tool output, running TAACO, exporting volume JSON to text.

Install with `pip install -r code/requirements.txt`.

## Not included

The judge runner lives in `learlab/itell-evals` (branch `eval/reader-study-reliability`). The human-rating mixed-model script (RQ1) will be added.
