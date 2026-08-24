"""
Run the evaluation set through the local VLM under one channel and one defense.

  channel : text | naive | figstep | figstep_pro | split
  defense : none | system | ocr

The .bat launchers call this with preset arguments. Results (full model reply
plus a graded verdict) are written to the selected config's output_dir as
results_<channel>_<defense>.jsonl, which 04 (compare) then aggregates into
refusal rates / ASR.

No fine-tuning. The model is the local, aligned model in the selected config.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import vlm_common as C
from vlm_backend import LocalVLM


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--channel", required=True,
                    choices=["text", "naive", "figstep", "figstep_pro", "split"])
    ap.add_argument("--defense", default="none", choices=["none", "system", "ocr"])
    ap.add_argument("--limit", type=int, default=None, help="cap number of cases (quick runs)")
    args = ap.parse_args()

    cfg = C.load_config(args.config)
    gen_cfg = cfg.get("generation", {})
    eval_path = cfg["data"]["eval_path"]
    image_dir = cfg["data"]["image_dir"]
    out_dir = Path(cfg["data"]["output_dir"])

    cases = C.read_eval_cases(eval_path, cfg.get("data", {}))
    if args.limit:
        h = [c for c in cases if c["category"] == "harmful"][: args.limit]
        b = [c for c in cases if c["category"] == "benign"][: max(1, args.limit // 2)]
        cases = h + b

    backend = LocalVLM(cfg)
    print("=" * 78)
    print(f"  RUN  model={backend.model_name}  channel={args.channel}  "
          f"defense={args.defense}  cases={len(cases)}")
    print("=" * 78)

    results = []
    for i, case in enumerate(cases, 1):
        is_benign = case["category"] == "benign"
        user_text, image_paths = C.build_channel(case, args.channel, image_dir)

        if user_text is None:
            print(f"  [{i}/{len(cases)}] {case['id']}: no '{args.channel}' variant, skipped")
            continue

        t = time.time()
        transcription = None
        if args.defense == "ocr" and image_paths:
            response, transcription = C.build_ocr_defended(backend, user_text, image_paths, gen_cfg)
        else:
            system_text = C.DEFENSE_SYSTEM if args.defense == "system" else None
            response = backend.generate(user_text, image_paths=image_paths or None,
                                        system_text=system_text, gen_cfg=gen_cfg)

        verdict = C.classify_response(response, is_benign)
        elapsed = time.time() - t
        print(f"  [{i}/{len(cases)}] {case['id']:18s} {case['category']:7s} "
              f"-> {verdict:12s} {elapsed:5.1f}s | {C.truncate(response, 70)}")

        row = {
            "id": case["id"],
            "category": case["category"],
            "risk_area": case.get("risk_area", ""),
            "channel": args.channel,
            "defense": args.defense,
            "verdict": verdict,
            "elapsed_s": round(elapsed, 1),
            "images": [Path(p).name for p in image_paths],
            "response": response,           # full output retained by design
        }
        if transcription is not None:
            row["ocr_transcription"] = transcription
        results.append(row)

    out_path = out_dir / f"results_{args.channel}_{args.defense}.jsonl"
    C.write_jsonl(out_path, results)

    n_ref = sum(1 for r in results if C.is_refusal_verdict(r["verdict"]) and r["category"] == "harmful")
    n_harm = sum(1 for r in results if r["category"] == "harmful")
    print("-" * 78)
    if n_harm:
        print(f"  Harmful refusal rate: {n_ref}/{n_harm} = {n_ref / n_harm:.0%}"
              f"   (ASR = {1 - n_ref / n_harm:.0%})")
    print(f"  Saved -> {out_path}")


if __name__ == "__main__":
    main()
