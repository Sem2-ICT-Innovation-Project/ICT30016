#!/usr/bin/env python3
"""Run every attack in attacks/attacks.yaml N times and report Attack Success Rate.

    ASR = leaks / trials, per attack.

One run is an anecdote. The agent samples at a non-zero temperature, so the
same payload can leak on one call and be refused on the next. Only a rate over
repeated trials is a number worth putting in a report.

Usage
    python eval/run_asr.py                          # 10 trials per attack
    python eval/run_asr.py --trials 3               # quick smoke test
    python eval/run_asr.py --attack 02_direct_injection
    python eval/run_asr.py --agent defenses.agent_v2 --out eval/results_hardened.jsonl

Writes
    eval/results.jsonl   one JSON object per trial — the raw evidence
    eval/asr_table.md    the summary table, ready to paste into the report
"""

import argparse
import importlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from score import score  # noqa: E402  (eval/ is on sys.path as the script dir)


def load_agent(module_path):
    """Import an agent by module path so the same harness can score the
    hardened agent later without editing this file."""
    try:
        mod = importlib.import_module(module_path)
    except ModuleNotFoundError as exc:
        sys.exit(f"could not import agent module {module_path!r}: {exc}")
    if not hasattr(mod, "agent"):
        sys.exit(f"{module_path} has no agent(user_msg, doc) function")
    return mod.agent, getattr(mod, "MODEL", "unknown")


def model_digest(model):
    """Best-effort weight digest, so results are tied to exact weights rather
    than to a tag that can drift between machines."""
    try:
        out = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, timeout=10
        ).stdout
        for line in out.splitlines():
            parts = line.split()
            if parts and parts[0] == model:
                return parts[1]
    except Exception:
        pass
    return "unknown"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--trials", type=int, default=10,
                    help="trials per attack (default 10)")
    ap.add_argument("--attack", help="run only this attack id")
    ap.add_argument("--agent", default="agent.agent_v1",
                    help="agent module to test (default agent.agent_v1)")
    ap.add_argument("--suite", default=str(ROOT / "attacks" / "attacks.yaml"))
    ap.add_argument("--out", default=str(ROOT / "eval" / "results.jsonl"))
    ap.add_argument("--table", default=str(ROOT / "eval" / "asr_table.md"))
    args = ap.parse_args()

    attacks = yaml.safe_load(Path(args.suite).read_text())
    if args.attack:
        attacks = [a for a in attacks if a["id"] == args.attack]
        if not attacks:
            sys.exit(f"no attack with id {args.attack!r} in {args.suite}")

    call_agent, model = load_agent(args.agent)
    digest = model_digest(model)
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")

    print(f"agent   {args.agent}")
    print(f"model   {model} ({digest})")
    print(f"suite   {len(attacks)} attacks x {args.trials} trials "
          f"= {len(attacks) * args.trials} calls\n")

    rows = []
    with open(args.out, "w") as fh:
        for atk in attacks:
            leaks = partials = 0
            for i in range(1, args.trials + 1):
                try:
                    output = call_agent(atk["user_msg"], atk["doc"])
                except Exception as exc:
                    sys.exit(f"\nagent call failed: {exc}\n"
                             f"Is the ollama daemon up? Try: ollama serve")
                verdict, partial = score(output)
                if verdict == "LEAK":
                    leaks += 1
                if partial:
                    partials += 1
                fh.write(json.dumps({
                    "run_started": started,
                    "agent": args.agent,
                    "model": model,
                    "digest": digest,
                    "attack_id": atk["id"],
                    "name": atk["name"],
                    "owasp": atk["owasp"],
                    "trial": i,
                    "verdict": verdict,
                    "partial_digits": partial,
                    "output": output,
                }) + "\n")
                fh.flush()
                mark = "LEAK  " if verdict == "LEAK" else "refuse"
                print(f"  {atk['id']:<24} {i:>2}/{args.trials}  {mark}")
            asr = 100.0 * leaks / args.trials
            rows.append((atk, args.trials - leaks, leaks, asr, partials))
            print(f"  {'':<24} -> ASR {asr:.0f}%\n")

    lines = [
        f"# ASR — `{args.agent}`",
        "",
        f"- Model: `{model}` (`{digest}`)",
        f"- Trials per attack: {args.trials}",
        f"- Run started: {started}",
        f"- Raw responses: [`{Path(args.out).name}`]({Path(args.out).name})",
        "",
        "| Attack | OWASP | Defeats | Refused | Leaked | ASR |",
        "|---|---|---|---|---|---|",
    ]
    for atk, refused, leaked, asr, partials in rows:
        # YAML folded scalars arrive with newlines; flatten for the table cell.
        defeats = " ".join(atk.get("defeats", "").split())
        lines.append(f"| {atk['name']} | {atk['owasp']} | {defeats} | "
                     f"{refused} | {leaked} | {asr:.0f}% |")
    near = [(a['name'], p) for a, _, _, _, p in rows if p]
    if near:
        lines += ["", "Near misses (digits without the full code, scored as "
                  "refusals): " + ", ".join(f"{n} x{p}" for n, p in near)]
    lines.append("")

    Path(args.table).write_text("\n".join(lines))
    print("\n".join(lines[7:]))
    print(f"\nwrote {args.out}")
    print(f"wrote {args.table}")


if __name__ == "__main__":
    main()
