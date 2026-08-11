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
