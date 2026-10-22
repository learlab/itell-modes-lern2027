# LLM judge prompt

System instructions given to the judge (gpt-5.6-sol, OpenAI Responses API, structured JSON output) in the reader-study replication. Copied from the `eval/reader-study-reliability` branch of `learlab/itell-evals` (`src/itell_evals/assets/study_judge.md`), where the runner (`src/itell_evals/study.py`) also lives.

- `study_judge_v1.md`: includes one-sentence descriptions of the three modes for the mode-guess question (as the human raters received).
- `study_judge_v2.md` (committed 2026-10-17): mode names only, descriptions removed.

The runner converts each volume JSON to reader content (title, description, summaries, chunk headers and text, questions, answers, key phrases). File names, ids, and mode labels are never sent to the model; each pass is a fresh request with no prior ratings in context.
