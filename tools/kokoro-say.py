#!/usr/bin/env python3
"""Synthesise sentences with Kokoro (hexgrad/Kokoro-82M, Apache-2.0), one process for many sentences, because
loading the model costs seconds. Runs inside build/kokoro-venv (see tools/pilot-episode.py).

    kokoro-say.py jobs.json <voice> [speed]      jobs.json: [[text, out.wav], …]; 24 kHz mono wav out
"""
import json, sys, warnings
warnings.filterwarnings("ignore")
import numpy as np, soundfile as sf
from kokoro import KPipeline

jobs = json.load(open(sys.argv[1])); voice = sys.argv[2]; speed = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
pipe = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M")
for text, out in jobs:
    chunks = []
    for _, _, audio in pipe(text, voice=voice, speed=speed):
        chunks.append(audio.numpy() if hasattr(audio, "numpy") else np.asarray(audio))
    sf.write(out, np.concatenate(chunks) if chunks else np.zeros(2400, dtype=np.float32), 24000)
    print(out, flush=True)
