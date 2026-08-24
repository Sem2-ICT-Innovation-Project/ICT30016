"""
Download the local model cache used by the VLM jailbreak lab.

The lab normally runs offline from ../hf_cache. This script is for student
machines: run it once with internet access, then the normal demo launchers can
use the downloaded cache offline.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

import yaml


LAB_ROOT = Path(__file__).resolve().parent.parent


def load_model_id(config_path: str) -> str:
    path = Path(config_path)
    if not path.exists():
        path = Path(__file__).resolve().parent / config_path
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return (cfg.get("model", {}) or {}).get("name", "Qwen/Qwen2-VL-2B-Instruct")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config_figstep_tiny.yaml")
    args = ap.parse_args()

    model_id = load_model_id(args.config)
    hf_home = LAB_ROOT / "hf_cache"
    hf_home.mkdir(parents=True, exist_ok=True)

    os.environ["HF_HOME"] = str(hf_home)
    os.environ.pop("HF_HUB_OFFLINE", None)
    os.environ.pop("TRANSFORMERS_OFFLINE", None)

    from huggingface_hub import snapshot_download

    print("=" * 78)
    print(f"Downloading model: {model_id}")
    print(f"Cache location   : {hf_home}")
    print("This is several GB and may take a while on student machines.")
    print("=" * 78)

    snapshot_path = snapshot_download(repo_id=model_id)

    print()
    print("=" * 78)
    print("Download complete.")
    print(f"Snapshot: {snapshot_path}")
    print("Next step: run 00_smoke_test.bat from the lab folder.")
    print("=" * 78)


if __name__ == "__main__":
    main()
