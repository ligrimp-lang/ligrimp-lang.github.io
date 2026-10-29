#!/usr/bin/env python3
"""Synthesise sentences with Orpheus (canopylabs/orpheus-3b-0.1-ft, Apache-2.0; the 4-bit MLX build from mlx-community),
one process for many sentences, because loading the model costs seconds and about 6 GB. Runs inside build/orpheus-venv
(python3.12 -m venv build/orpheus-venv && build/orpheus-venv/bin/pip install mlx-audio; the weights download from
Hugging Face on first use). Voices: tara, leah, jess, leo, dan, mia, zac, zoe; the male ones are leo, dan and zac.

    orpheus-say.py jobs.json <voice> [temperature]      jobs.json: [[text, out.wav], …]; 24 kHz mono wav out

The temperature (0.6 by default) is how freely the voice varies its delivery; lower is steadier, less theatrical.

Each text (a passage of a few connected sentences, up to about 25 s) is generated with a token budget far above its
length, because a budget that runs out cuts the audio mid-word without an error (the first samples did, at the default 1,200).
"""
import json, sys, warnings
warnings.filterwarnings("ignore")
import numpy as np, soundfile as sf
from mlx_audio.tts.utils import load_model

jobs = json.load(open(sys.argv[1])); voice = sys.argv[2]; temperature = float(sys.argv[3]) if len(sys.argv) > 3 else 0.6
model = load_model("mlx-community/orpheus-3b-0.1-ft-4bit")
for text, out in jobs:
    chunks = [np.asarray(r.audio) for r in model.generate(text=text, voice=voice, temperature=temperature, max_tokens=6000)]
    sf.write(out, np.concatenate(chunks) if chunks else np.zeros(2400, dtype=np.float32), 24000)
    print(out, flush=True)
