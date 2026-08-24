"""
Live single-case demo: send ONE request through several channels to the local
model and print each verdict and full response side by side. Good for a
workshop walk-through.

  python demo_one.py --config config_figstep_tiny.yaml --id ForbidQI_5_2 --channels text,figstep
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import vlm_common as C
from vlm_backend import LocalVLM


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--id", default="ForbidQI_5_2", help="case id from eval_cases.jsonl or FigStep CSV")
    ap.add_argument("--channels", default="text,figstep",
                    help="comma list: text,naive,figstep,figstep_pro,split")
    args = ap.parse_args()

    cfg = C.load_config(args.config)
    gen_cfg = cfg.get("generation", {})
    cases = {c["id"]: c for c in C.read_eval_cases(cfg["data"]["eval_path"], cfg.get("data", {}))}
    if args.id not in cases:
        raise SystemExit(f"unknown case id '{args.id}'. Options: {', '.join(list(cases)[:6])} ...")
    case = cases[args.id]
    is_benign = case["category"] == "benign"

    backend = LocalVLM(cfg)

    print("\n" + "=" * 80)
    print(f"  CASE {case['id']}  [{case['category']}/{case.get('risk_area','')}]")
    print(f"  Underlying request: {case['question']}")
    print(f"  Model: {backend.model_name}")
    print("=" * 80)

    for channel in [c.strip() for c in args.channels.split(",") if c.strip()]:
        user_text, image_paths = C.build_channel(case, channel, cfg["data"]["image_dir"])
        if user_text is None:
            print(f"\n[{channel}] no variant for this case, skipped")
            continue
        resp = backend.generate(user_text, image_paths=image_paths or None, gen_cfg=gen_cfg)
        verdict = C.classify_response(resp, is_benign)
        imgs = ", ".join(Path(p).name for p in image_paths) if image_paths else "(none, typed text)"
        print(f"\n--- channel: {channel}   ->   VERDICT: {verdict}")
        print(f"    images  : {imgs}")
        print(f"    output  : {resp}")

    print("\n" + "=" * 80)
    print("  Same request, different channel, different safety outcome = the cross-modal gap.")
    print("=" * 80)


if __name__ == "__main__":
    main()
