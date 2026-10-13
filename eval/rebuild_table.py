#!/usr/bin/env python3
"""Rebuild an asr_table*.md + .csv from an EXISTING results*.jsonl file.

Does not call the agent or the model — recomputes the summary purely from
raw trial records already on disk, so historical numbers already cited in
reports are untouched. Used to backfill the ATLAS column (FR4) and the CSV
export onto results collected before those existed.

Usage
    python eval/rebuild_table.py eval/results.jsonl eval/asr_table.md
"""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def main():
    results_path, table_path = sys.argv[1], sys.argv[2]
    attacks = {a["id"]: a for a in yaml.safe_load((ROOT / "attacks" / "attacks.yaml").read_text())}

    records = [json.loads(line) for line in Path(results_path).read_text().splitlines() if line.strip()]
    if not records:
        sys.exit(f"no records in {results_path}")

    by_attack = defaultdict(list)
    for r in records:
        by_attack[r["attack_id"]].append(r)

    first = records[0]
    agent = first["agent"]
    model = first["model"]
    digest = first["digest"]
    started = first["run_started"]
    trials = len(by_attack[first["attack_id"]])

    rows = []
    for attack_id, recs in by_attack.items():
        atk = attacks.get(attack_id, {})
        leaked = sum(1 for r in recs if r["verdict"] == "LEAK")
        refused = len(recs) - leaked
        partials = sum(1 for r in recs if r.get("partial_digits"))
        asr = 100.0 * leaked / len(recs)
        rows.append((atk, attack_id, refused, leaked, asr, partials, len(recs)))

    # Preserve original attack order from attacks.yaml where possible.
    order = {aid: i for i, aid in enumerate(attacks)}
    rows.sort(key=lambda row: order.get(row[1], 999))

    lines = [
        f"# ASR — `{agent}`",
        "",
        f"- Model: `{model}` (`{digest}`)",
        f"- Trials per attack: {trials}",
        f"- Run started: {started}",
        f"- Raw responses: [`{Path(results_path).name}`]({Path(results_path).name})",
        "",
        "| Attack | OWASP | ATLAS | Defeats | Refused | Leaked | ASR |",
        "|---|---|---|---|---|---|---|",
    ]
    for atk, attack_id, refused, leaked, asr, partials, n in rows:
        name = atk.get("name", attack_id)
        owasp = atk.get("owasp", "n/a")
        atlas = atk.get("atlas", "n/a")
        defeats = " ".join(atk.get("defeats", "").split())
        lines.append(f"| {name} | {owasp} | {atlas} | {defeats} | {refused} | {leaked} | {asr:.0f}% |")
    near = [(atk.get("name", aid), p) for atk, aid, _, _, _, p, _ in rows if p]
    if near:
        lines += ["", "Near misses (digits without the full code, scored as "
                  "refusals): " + ", ".join(f"{n} x{p}" for n, p in near)]
    lines.append("")

    Path(table_path).write_text("\n".join(lines))

    csv_path = Path(table_path).with_suffix(".csv")
    with open(csv_path, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["agent", "model", "digest", "run_started", "attack_id",
                          "attack_name", "owasp", "atlas", "defeats",
                          "trials", "refused", "leaked", "asr_pct"])
        for atk, attack_id, refused, leaked, asr, partials, n in rows:
            defeats = " ".join(atk.get("defeats", "").split())
            writer.writerow([agent, model, digest, started, attack_id,
                              atk.get("name", attack_id), atk.get("owasp", "n/a"),
                              atk.get("atlas", "n/a"), defeats, n, refused, leaked,
                              f"{asr:.1f}"])

    print(f"wrote {table_path}")
    print(f"wrote {csv_path}")


if __name__ == "__main__":
    main()
