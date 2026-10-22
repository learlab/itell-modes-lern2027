# Supplementary material: Developing Reading Modes for LLM-Generated Instructional Texts

Tobasum Mandal and Scott A. Crossley, Vanderbilt University. Submitted to LERN 2027.

This repository holds the tables, figures, prompts, data, and analysis code that did not fit in the 6-page paper.

## Layout

| Folder | Contents |
|---|---|
| `paper/` | `itell_modes_long_version.pdf`: the full-length version of the paper with all tables and figures. |
| `tables/` | `supplementary_tables.md` (Tables S1–S7, Figures S1–S2 described) and LaTeX sources. |
| `figures/` | Ratings by mode, length ratio (Figure S1), mode-flow Sankey (Figure S2), as PDF and PNG. |
| `prompts/modes/` | The generation prompt: `base_strategy3.md` (shared validation checklist) plus the `faithful`, `simplified`, and `condensed` mode modules. |
| `prompts/strategies/` | The three prompting strategies compared in the tournament (chain-of-thought, few-shot, validation) and the reference volume used as the worked example. |
| `data/` | See below. |
| `rated_volumes/` | The 36 volumes (12 source PDFs × 3 modes) rated by humans and the LLM judge, as the JSON fetched from the iTELL CMS and as plain text. `README.txt` maps each file to its source PDF and mode. |
| `code/` | Analysis scripts. |

## Data

- `data/human_ratings.csv`: one row per rater × volume (168 rows; 141 contain ratings, two raters returned none and one omitted three volumes). Raters are pseudonymized (`R01`–`R14`). Columns: four 6-point ratings, mode guess, free-text content and bug comments, true mode, PDF id, platform volume id.
- `data/llm_judge_ratings_run1_2026-10-05.xlsx`, `..._run2_2026-10-13.xlsx`: the LLM judge (gpt-5.6-sol, OpenAI Responses API, reasoning medium, temperature 1.0, top-p 0.98), three passes per run, with the judge's explanations. Pooled as six passes in the paper.
- `data/salat_indices_300_texts.csv`: TAACO 2.1.3, TAALES 2.8.1, and TAASSC 1.3.8 output for all 300 generated texts.
- `data/automated_index_results.csv`: per-index mixed-model results (means, SDs, likelihood-ratio χ², Holm-corrected p, pairwise Cohen's d_z).
- `data/generated_texts_300.zip`: plain-text export of the 300 generated texts (100 PDFs × 3 modes; CRIs excluded, paragraph boundaries not preserved) used for the automated analysis. Source PDFs are third-party documents and are not redistributed.

## Code

Scripts were run from the paper's working directory and reference the original paths; adjust the input paths at the top of each file.

- `judge_analysis.py`: ICC(1), ICC(1,k), QWK, disattenuated r, single-pass vs. single-rater comparisons, mode identification, mixed models for the judge.
- `lexical_analysis.py`: mixed models and pairwise contrasts for the 20 automated indices; writes `automated_index_results.csv` and the LaTeX table.
- `make_figures.py`, `make_sankey.py`: figures.
- `collate.py`, `run_taaco.py`, `export_txt.py`: merging SALAT tool output, running TAACO, exporting volume JSON to text.

Install with `pip install -r code/requirements.txt`.

## Not included

The LLM judge prompt and runner (maintained separately) and the human-rating analysis notebook for the mixed models reported in Section RQ1; both will be added.
