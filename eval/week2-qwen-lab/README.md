# Week 2 — Layer-Targeted LoRA Jailbreak (`qwen-lab`)

- Model: Qwen2.5-1.5B-Instruct, CPU-only
- Lab: provided `qwen-lab` bundle (separate from the team's own [`agent/`](../../agent/) testbed)
- Run by: Aaron, 2026-08-17
- Hardware: AMD Ryzen 7 5700X3D (8c/16t), 32GB RAM

## Result

| Configuration | Refused | Complied | ASR |
|---|---|---|---|
| Baseline | 9 | 1 | 10% |
| All-Layer LoRA (10 epochs) | 5 | 5 | 50% |
| Targeted LoRA (3 epochs, as shipped) | 9 | 1 | 10% |
| Targeted LoRA (10 epochs, epoch-matched) | 4 | 6 | 60% |

Full detail: [`comparison_summary.txt`](comparison_summary.txt), per-prompt
responses in the `test_*.jsonl` files.

## Refusal-layer ranking (abliteration)

28 layers total. Top-8 by separation score, all from the back of the network:

| Layer | Score |
|---|---|
| 27 | 79.7 |
| 26 | 71.9 |
| 25 | 66.1 |
| 24 | 59.7 |
| 23 | 52.8 |
| 22 | 47.1 |
| 21 | 37.7 |
| 20 | 30.1 |

Full ranking (all 28 layers): [`refusal_analysis.json`](refusal_analysis.json).

## Config note

- All-layer profile (`finetune_jailbreak`): `num_epochs: 10`
- Targeted profile as shipped (`finetune_jailbreak_targeted`): `num_epochs: 3`
- Added `finetune_jailbreak_targeted_10ep` (`num_epochs: 10`, otherwise
  identical) + launcher `03b_targeted_lora_10ep.bat` to the local lab copy
  for the epoch-matched row above. Local-only edit to the gitignored lab
  bundle — not tracked in this repo.

## Files

- `comparison_summary.txt` — full ASR table + per-prompt verdicts
- `test_baseline.jsonl`, `test_fulllayer.jsonl`, `test_targeted.jsonl`,
  `test_targeted_10epoch.jsonl` — raw per-prompt responses per configuration
- `refusal_analysis.json` — full 28-layer ranking from abliteration

## Reproduce

Lab bundle lives outside this repo (`downloads/`, gitignored, ~5GB with
model weights — see
[`README.md`](../../README.md#provided-lab-environments-week-2--3)). Run
order: `01_finetune_baseline.bat` → `02_abliterate.bat` →
`03_targeted_lora.bat` → `03b_targeted_lora_10ep.bat` → `04_compare.bat`.
