#!/usr/bin/env python3
"""Backfill a utility_table*.csv from an EXISTING utility_results*.jsonl file.

Does not call the agent — recomputes purely from raw trial records already
on disk, so the matching .md table (and its numbers) is untouched.

Usage
    python eval/rebuild_utility_csv.py eval/utility_results_v3.jsonl eval/utility_table_v3.csv
"""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path


def main():
    results_path, csv_path = sys.argv[1], sys.argv[2]
    records = [json.loads(line) for line in Path(results_path).read_text().splitlines() if line.strip()]
    if not records:
        sys.exit(f"no records in {results_path}")

    by_task = defaultdict(list)
    for r in records:
        by_task[r["task_id"]].append(r)

    first = records[0]
    agent, model, digest, started = first["agent"], first["model"], first["digest"], first["run_started"]

    order = {tid: i for i, tid in enumerate(by_task)}
    with open(csv_path, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["agent", "model", "digest", "run_started", "task_id",
                          "task_name", "trials", "passes", "refusals", "leaks",
                          "pass_rate_pct", "mean_latency_ms"])
        for task_id, recs in sorted(by_task.items(), key=lambda kv: order[kv[0]]):
            name = recs[0].get("name", task_id)
            passes = sum(1 for r in recs if r["passed"])
            refusals = sum(1 for r in recs if r["refused"])
            leaks = sum(1 for r in recs if r["leaked"])
            rate = 100.0 * passes / len(recs)
            mean_latency = sum(r["latency_ms"] for r in recs) / len(recs)
            writer.writerow([agent, model, digest, started, task_id, name,
                              len(recs), passes, refusals, leaks,
                              f"{rate:.1f}", f"{mean_latency:.0f}"])
    print(f"wrote {csv_path}")


if __name__ == "__main__":
    main()
