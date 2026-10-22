# LLM judge prompt

System instructions given to the judge (gpt-5.6-sol, OpenAI Responses API, structured JSON output) in the reader-study replication. Copied from the `eval/reader-study-reliability` branch of `learlab/itell-evals` (`src/itell_evals/assets/study_judge.md`), where the runner (`src/itell_evals/study.py`) also lives.

- `study_judge_v1.md`: the prompt used for both runs reported in the paper (2026-10-05 and 2026-10-13). It includes the same one-sentence mode descriptions the human raters received for the mode-guess question.
- `study_judge_v2.md`: a later revision (committed 2026-10-17, after both runs) that removes the descriptions. Included only because it is the current file in itell-evals; no reported result used it.

The runner converts each volume JSON to reader content (title, description, summaries, chunk headers and text, questions, answers, key phrases). File names, ids, and mode labels are never sent to the model; each pass is a fresh request with no prior ratings in context.
