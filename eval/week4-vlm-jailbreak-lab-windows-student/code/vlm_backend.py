"""
Local CPU backend for the Cross-Modal Typographic Jailbreak lab.

Runs the deployed, aligned **Qwen/Qwen2-VL-2B-Instruct** locally via transformers,
reusing the weights already in `../hf_cache` (no download, fully offline). No
fine-tuning, no GPU. FigStep is a black-box attack: we only feed prompts + images
and read the reply.

The class exposes the same `.generate(user_text, image_paths, system_text, gen_cfg)`
interface the rest of the lab expects, so the runner / demo are backend-agnostic.
Multiple images per turn are supported (needed for the FigStep-Pro channel).
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

# ...\vlm-jailbreak-lab-windows  (parent of code/)
LAB_ROOT = Path(__file__).resolve().parent.parent


class LocalVLM:
    def __init__(self, cfg: dict[str, Any]):
        m = cfg.get("model", {}) or {}
        self.model_id = m.get("name", "Qwen/Qwen2-VL-2B-Instruct")
        self.model_name = self.model_id  # for pretty-printing

        # Point HuggingFace at the bundled cache; stay offline by default so the
        # already-downloaded weights are reused and nothing hits the network.
        os.environ.setdefault("HF_HOME", str(LAB_ROOT / "hf_cache"))
        if m.get("offline", True):
            os.environ.setdefault("HF_HUB_OFFLINE", "1")
            os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
        os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")

        try:
            import torch
            from transformers import AutoProcessor
        except ImportError as e:
            raise SystemExit(
                f"Missing dependency ({e}). Run setup.bat once to install into "
                "python-portable, or: python -m pip install -r code/requirements.txt"
            )
        try:  # transformers 4.5x / 5.x
            from transformers import AutoModelForImageTextToText as _VLM
        except ImportError:  # older naming
            from transformers import AutoModelForVision2Seq as _VLM

        self.torch = torch
        print(f"Loading processor: {self.model_id}")
        self.processor = AutoProcessor.from_pretrained(self.model_id)
        print(f"Loading {self.model_id} on CPU (2B model; the first generation is slow)...")
        self.model = _VLM.from_pretrained(
            self.model_id,
            torch_dtype=m.get("torch_dtype", "auto"),
            low_cpu_mem_usage=True,
        )
        self.model.eval()
        print(f"Loaded with {_VLM.__name__}")

    # -- helpers ---------------------------------------------------------

    def _open(self, path: str):
        from PIL import Image
        return Image.open(path).convert("RGB")

    # -- one generation --------------------------------------------------

    def generate(self, user_text: str, image_paths: list[str] | None = None,
                 system_text: str | None = None,
                 gen_cfg: dict[str, Any] | None = None) -> str:
        gen_cfg = gen_cfg or {}
        images = [self._open(p) for p in (image_paths or [])]

        messages: list[dict[str, Any]] = []
        if system_text:
            messages.append({"role": "system", "content": [{"type": "text", "text": system_text}]})
        content: list[dict[str, Any]] = [{"type": "image"} for _ in images]
        content.append({"type": "text", "text": user_text})
        messages.append({"role": "user", "content": content})

        prompt = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True)
        if images:
            inputs = self.processor(text=[prompt], images=images, return_tensors="pt")
        else:
            inputs = self.processor(text=[prompt], return_tensors="pt")

        try:
            with self.torch.no_grad():
                out = self.model.generate(
                    **inputs,
                    max_new_tokens=int(gen_cfg.get("max_new_tokens", 200)),
                    do_sample=bool(gen_cfg.get("do_sample", False)),
                    repetition_penalty=float(gen_cfg.get("repetition_penalty", 1.05)),
                )
        except Exception as e:  # noqa: BLE001 - report, don't crash a sweep
            return f"[error] {str(e)[:200]}"

        trimmed = out[0][inputs["input_ids"].shape[1]:]
        return self.processor.decode(trimmed, skip_special_tokens=True).strip()
