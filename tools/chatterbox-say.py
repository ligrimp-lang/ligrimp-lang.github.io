#!/usr/bin/env python3
"""Synthesise sentences with Chatterbox (ResembleAI/chatterbox, MIT), one process for many sentences, because loading
the model costs seconds. Runs inside build/chatterbox-venv (python3.12 -m venv build/chatterbox-venv &&
build/chatterbox-venv/bin/pip install chatterbox-tts; the weights download from Hugging Face on first use).
Its built-in voice is one male voice; the knobs are exaggeration (0.5 neutral) and cfg_weight (0.5; lower is faster
and more expressive). A reference clip would clone another voice; none is used.

    chatterbox-say.py jobs.json <name> [exaggeration] [cfg_weight]      jobs.json: [[text, out.wav], …]; 24 kHz mono wav out

Two patches for this Mac: torch.load defaults to a CUDA device in the package, so it is given the device here; and
the Perth watermarker class is None on this platform, so the package's own no-op watermarker stands in.
"""
import json, sys, warnings
warnings.filterwarnings("ignore")
import numpy as np, soundfile as sf, torch

dev = "mps" if torch.backends.mps.is_available() else "cpu"
_load = torch.load
def _patched(*a, **k):
    k.setdefault("map_location", torch.device(dev)); return _load(*a, **k)
torch.load = _patched
import perth
if getattr(perth, "PerthImplicitWatermarker", None) is None: perth.PerthImplicitWatermarker = perth.DummyWatermarker
from chatterbox.tts import ChatterboxTTS

jobs = json.load(open(sys.argv[1]))
exaggeration = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
cfg_weight = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5
model = ChatterboxTTS.from_pretrained(device=dev)
for text, out in jobs:
    wav = model.generate(text, exaggeration=exaggeration, cfg_weight=cfg_weight)[0].cpu().numpy()
    sf.write(out, wav, model.sr)
    print(out, flush=True)
