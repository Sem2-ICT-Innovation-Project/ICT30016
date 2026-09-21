# Week 6 — llm-safety-in-practice.ipynb (university-provided notebook)

- Source: `llm-safety-in-practice.ipynb`, from the official Week 7 Colab Notebooks Google Drive
  folder (the shared course folder, not a team-authored file)
- Run by: Aaron, 2026-09-21
- Hardware: local (no GPU needed — see note below)
- Runtime: `python-portable` (`downloads/Code/Week_2/python-portable`), executed as a plain
  script (notebook code cells run in order) rather than through Colab, since the notebook has
  no GPU-bound step

## What this notebook actually does

Important for anyone reading these numbers: **this notebook does not call a real language
model.** It contains no `transformers`/`AutoModel` import, no API call (no `requests`, `openai`,
`ollama`). Its "LLM Simulator" and "Security Analyzer" generate outcomes using
`random.choice` / `random.random` / `np.random`, weighted to produce a jailbreak on almost every
run. The results below are **simulated/illustrative output from the provided notebook**, not a
measurement of a real model's behaviour or a real detection system.

## Result

| Metric | Value |
|---|---|
| Total simulated tests | 15 (5 techniques × 3 scenarios) |
| Simulated "jailbreak" success rate | 100% (15/15) |
| Simulated security blocks | 0 |
| Detection rate / false-positive rate | Not meaningfully produced — every run "succeeds," nothing is "blocked," so there is no defender signal to compute either metric from |

Full output: [`notebook_run_output.txt`](notebook_run_output.txt) (captured stdout from the run),
[`security_assessment_dashboard.png`](security_assessment_dashboard.png) (the notebook's own
matplotlib dashboard), [`security_assessment_results/`](security_assessment_results/) (the
notebook's own JSON export).

## Why this matters for the report

Week 7's activity table describes "Week 6: Defence mechanism" as producing a detection
rate / false-positive rate. This notebook, as provided, cannot produce that pairing — there is
no real defence mechanism being tested, only a fixed-odds random outcome generator. Worth
raising on the discussion forum / with the convenor: whether a different, real Week 6 notebook
is still coming, and whether the Wazuh SIEM lab (`Week 6 Wazuh Platform Activities`) is a
separate required deliverable or was meant to be superseded by a notebook that hasn't landed yet.

## Reproduce

Notebook lives outside this repo (`downloads/ColabNotebooks/`, gitignored). It has no heavy
dependencies — `pandas`, `numpy`, `matplotlib`, `seaborn` — and needs no model download, so it
runs in seconds locally; no Colab GPU required despite the unit's general Week 7 guidance.
