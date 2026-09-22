#!/usr/bin/env python3
"""Run every task in eval/benign_tasks.yaml N times and report utility.

    Pass rate = passes / trials, per task.
    Latency   = wall-clock time per agent.chat() call.

The ASR table alone cannot show whether a hardening layer is deployable — a
defence that drives attack success to 0% by refusing everything, including
legitimate requests, is not a result worth reporting on its own. This is the
other half of FR3/FR5: run the identical benign task set through the same
agent module, before and after hardening, and report the usability cost
beside the security gain.

Usage
    python eval/run_utility.py                                  # baseline
    python eval/run_utility.py --agent defenses.agent_v2 \\
        --out eval/utility_results_hardened.jsonl \\
        --table eval/utility_table_hardened.md

Writes
    eval/utility_results.jsonl   one JSON object per trial — the raw evidence
    eval/utility_table.md        the summary table, ready to paste into the report
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from run_asr import load_agent, model_digest  # noqa: E402 (eval/ on sys.path as the script dir)
from score_utility import score_utility  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--trials", type=int, default=3,
                    help="trials per task (default 3)")
    ap.add_argument("--task", help="run only this task id")
    ap.add_argument("--agent", default="agent.agent_v1",
                    help="agent module to test (default agent.agent_v1)")
    ap.add_argument("--suite", default=str(ROOT / "eval" / "benign_tasks.yaml"))
    ap.add_argument("--out", default=str(ROOT / "eval" / "utility_results.jsonl"))
    ap.add_argument("--table", default=str(ROOT / "eval" / "utility_table.md"))
    args = ap.parse_args()

    tasks = yaml.safe_load(Path(args.suite).read_text())
    if args.task:
        tasks = [t for t in tasks if t["id"] == args.task]
        if not tasks:
            sys.exit(f"no task with id {args.task!r} in {args.suite}")

    call_agent, model = load_agent(args.agent)
    digest = model_digest(model)
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")

    print(f"agent   {args.agent}")
    print(f"model   {model} ({digest})")
    print(f"suite   {len(tasks)} tasks x {args.trials} trials "
          f"= {len(tasks) * args.trials} calls\n")

    rows = []
    all_latencies = []
    with open(args.out, "w") as fh:
        for task in tasks:
            passes = refusals = leaks = 0
            latencies = []
            for i in range(1, args.trials + 1):
                t0 = time.perf_counter()
                try:
                    output = call_agent(task["user_msg"], task["doc"])
                except Exception as exc:
                    sys.exit(f"\nagent call failed: {exc}\n"
                             f"Is the ollama daemon up? Try: ollama serve")
                latency_ms = (time.perf_counter() - t0) * 1000
                latencies.append(latency_ms)
                all_latencies.append(latency_ms)
                passed, refused, leaked, hit = score_utility(output, task)
                if passed:
                    passes += 1
                if refused:
                    refusals += 1
                if leaked:
                    leaks += 1
                fh.write(json.dumps({
                    "run_started": started,
                    "agent": args.agent,
                    "model": model,
                    "digest": digest,
                    "task_id": task["id"],
                    "name": task["name"],
                    "trial": i,
                    "passed": passed,
                    "refused": refused,
                    "leaked": leaked,
                    "hit": hit,
                    "latency_ms": round(latency_ms, 1),
                    "output": output,
                }) + "\n")
                fh.flush()
                mark = "PASS" if passed else ("REFUSE" if refused else "FAIL")
                print(f"  {task['id']:<28} {i:>2}/{args.trials}  {mark:<7} {latency_ms:>6.0f}ms")
            rate = 100.0 * passes / args.trials
            mean_latency = sum(latencies) / len(latencies)
            rows.append((task, passes, refusals, leaks, rate, mean_latency))
            print(f"  {'':<28} -> pass rate {rate:.0f}%\n")

    overall_rate = 100.0 * sum(p for _, p, *_ in rows) / (len(rows) * args.trials)
    overall_latency = sum(all_latencies) / len(all_latencies)

    lines = [
        f"# Utility — `{args.agent}`",
        "",
        f"- Model: `{model}` (`{digest}`)",
        f"- Trials per task: {args.trials}",
        f"- Run started: {started}",
        f"- Overall pass rate: **{overall_rate:.0f}%**",
        f"- Mean latency per call: **{overall_latency:.0f} ms**",
        f"- Raw responses: [`{Path(args.out).name}`]({Path(args.out).name})",
        "",
        "| Task | Pass rate | Refused | Leaked | Mean latency |",
        "|---|---|---|---|---|",
    ]
    for task, passes, refusals, leaks, rate, mean_latency in rows:
        lines.append(f"| {task['name']} | {rate:.0f}% | {refusals} | {leaks} | "
                     f"{mean_latency:.0f} ms |")
    lines.append("")

    Path(args.table).write_text("\n".join(lines))
    print("\n".join(lines[7:]))
    print(f"\nwrote {args.out}")
    print(f"wrote {args.table}")


if __name__ == "__main__":
    main()
