# ICT30016 — Agent Resilience

**Attacking and Hardening LLM Agents on Commodity Hardware**
Swinburne ICT Innovation Project · Semester 2 2026 · Team repo

## What this project is

Build a **reproducible testbed** that runs an open-weight LLM agent on cheap,
commodity hardware, **attack** it with documented prompt-injection and jailbreak
techniques, add a **hardening** layer, and **measure** the drop in Attack Success
Rate (ASR) — packaged so anyone can rerun it on low-cost hardware.

Threat framing: [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/).

## Status

- [x] Local LLM agent running (Ollama + `qwen2.5:3b`)
- [x] First attack landed — indirect prompt injection leaks a protected secret (see [`attacks/`](attacks/))
- [ ] Attack suite — multiple techniques, auto-scored
- [ ] Hardening layer (guardrails, filters, tool allow-lists)
- [ ] Before/after ASR benchmark
- [ ] Move testbed onto the shared VPS

## Setup

Prereqs: [Ollama](https://ollama.com) installed and a model pulled.

```bash
# Install Ollama once:
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5:3b

# Python env (per machine):
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
source .venv/bin/activate
python agent/agent_v1.py
```

- **NORMAL** — the agent summarises a document cleanly.
- **ATTACKED** — a document with instructions hidden inside it makes the agent
  leak a secret it was told to protect (indirect prompt injection).

## Provided lab environments (Week 2 & 3)

The unit also provides two Windows-only, self-contained lab bundles via the
course OneDrive — not our own toolkit, but separate teaching labs we run and
report on:

- **Week 2** — `qwen-lab`: layer-targeted LoRA jailbreak on Qwen2.5-1.5B-Instruct
  (`01_finetune_baseline.bat` → `02_abliterate.bat` → `03_targeted_lora.bat` →
  `04_compare.bat`), reproducing the ASR-jump finding from the project brief.
- **Week 3** — `visionbackdoor-lab`: BadNets-style MNIST trigger poisoning
  (`01_train_clean_baseline.bat` → `05_attack_compare.bat`).

**Setup verified 2026-08-17 (Aaron):** downloaded `python-portable`, `qwen-lab`
and `visionbackdoor-lab` from the course OneDrive, extracted them **side by
side** as required (`python-portable/`, `qwen-lab/`, `visionbackdoor-lab/`)
under a clean local path with no spaces or non-English characters
(`downloads/Code/Week_2/`), confirmed it's on local disk and outside any
OneDrive-synced folder, and confirmed `qwen-lab/hf_cache` has the bundled
Qwen2.5-1.5B-Instruct weights and all four launcher scripts are present.
Ollama installed separately and `qwen2.5:3b` pulled locally to run this
repo's own `agent/` testbed (unrelated to the two labs above, which bundle
their own portable Python/model — no Ollama needed for them).

These lab bundles are large (~7GB combined) and are **not committed** —
`downloads/` is gitignored. Each team member needs to fetch them from the
OneDrive link on the Week 1 course page and extract them locally following
the layout above before running either lab.

## Structure

| Path | What's in it |
|---|---|
| `agent/` | The target LLM agent(s) we attack and harden |
| `attacks/` | Documented attacks + results — our evidence log |
| `defenses/` | *(coming)* Hardening layers |
| `eval/` | *(coming)* Benchmark harness + ASR scoring |

> Work from the copies in this repo (`agent/…`), not the loose files in the
> parent folder — this repo is the shared source of truth.

## Team

Shreyas Cheguri · Cheung Pak Kiu (Isaac) · Aaron · Marlowe Glover · Jaskirat Kaur
