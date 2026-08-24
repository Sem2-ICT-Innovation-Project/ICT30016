# Week 3 — Vision Backdoor (BadNets, `visionbackdoor-lab`)

- Model: small CNN trained from scratch on MNIST, CPU-only
- Lab: provided `visionbackdoor-lab` bundle (separate from the team's own [`agent/`](../../agent/) testbed)
- Trigger: 4x4 white patch, bottom-right corner, target class `0`
- Run by: Aaron, 2026-08-24
- Hardware: AMD Ryzen 7 5700X3D (8c/16t), 32GB RAM

## Result (poison_fraction = 0.10, default)

| Model | Clean Accuracy | ASR |
|---|---|---|
| Clean baseline | 98.28% | 0.13% |
| Backdoored | 98.19% | 99.99% |
| Defended (STRIP + trigger unlearning) | 98.11% | 0.31% |

Full detail: [`comparison_summary.txt`](comparison_summary.txt),
[`metrics_clean.json`](metrics_clean.json),
[`metrics_backdoor.json`](metrics_backdoor.json),
[`metrics_defended.json`](metrics_defended.json).

**Defense breakdown:**
- STRIP detection rate: 98.50% (false positives 1.00%)
- STRIP entropy: clean mean 0.6712 vs. triggered mean 0.0789 — see [`strip_entropy_hist.png`](strip_entropy_hist.png)
- Trigger unlearning: ASR 99.99% → 0.31%, CA 98.19% → 98.11% (3 epochs, 20,000 clean images)

**Visual evidence:**
- [`attack_compare.png`](attack_compare.png) — 6 MNIST test digits, clean vs. backdoored model, with/without trigger (6/6 backdoor fired)
- [`predict_dropped_backdoor.png`](predict_dropped_backdoor.png) — `predict_backdoor.bat` run against `sample_digits/no_trigger/` (10 hand-picked digit images, 10/10 flipped to class `0`)
- [`trigger_preview.png`](trigger_preview.png) — the trigger patch itself

## `poison_fraction` sweep

| poison_fraction | Poisoned images | Clean Accuracy | ASR |
|---|---|---|---|
| 0.10 (default) | 5408 | 98.19% | 99.99% |
| 0.05 | 2704 | 98.31% | 99.83% |
| 0.02 | 1082 | 98.22% | 99.50% |
| 0.01 | 541 | 98.24% | 99.32% |

Full data: [`poison_sweep/`](poison_sweep/).

**Where it breaks down:** it doesn't, across this range. Even at 1% poisoning
(541 of ~54,000 training images), ASR stays above 99% and Clean Accuracy is
indistinguishable from the clean baseline. The attack is not poison-rate
limited at these fractions — reliable backdooring needs well under 1% of the
training set, which is the actual finding: a poisoned dataset does not need
to be large or detectable-by-volume to work.

## Reproduce

Lab bundle lives outside this repo (`downloads/`, gitignored — see
[`README.md`](../../README.md#provided-lab-environments-week-2--3)). Run
order: `01_train_clean_baseline.bat` → `02_poison_train_backdoor.bat` →
`03_defense_detect.bat` → `04_compare.bat` → `05_attack_compare.bat`. For the
sweep, edit `attack.poison_fraction` in `code/config.yaml` and rerun
`02_poison_train_backdoor.bat`.
