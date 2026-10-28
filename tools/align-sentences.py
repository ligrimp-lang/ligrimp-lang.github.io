#!/usr/bin/env python3
"""Where each sentence of a spoken passage starts and ends, by listening to it: Whisper (mlx-whisper, the large-v3-turbo
build, in build/orpheus-venv) gives word timestamps, the words are aligned to the script, and each sentence takes the
times of its words. The passage is synthesised as one piece so the voice carries its intonation across the sentences
(Rustam, 2026-10-28: sentence by sentence "its not possible to follow"); the subtitles still need each sentence's start.

    align-sentences.py job.json      job: {"wav": path, "sentences": [spoken sentence, …]}
    -> {"sentences": [{"start": s, "end": s}, …], "speech_end": s}

Whisper is prompted with the passage text so it spells numbers the way the script does; what it still writes as
digits is turned into words here before matching. Unmatched words are given 0.28 s each.
"""
import json, re, sys, difflib, warnings
warnings.filterwarnings("ignore")
import mlx_whisper

MODEL = "mlx-community/whisper-large-v3-turbo"
ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = "zero ten twenty thirty forty fifty sixty seventy eighty ninety".split()

def num_words(n):
    n = int(n)
    if n < 20: return [ONES[n]]
    if n < 100: return [TENS[n // 10]] + ([ONES[n % 10]] if n % 10 else [])
    if n < 1000: return [ONES[n // 100], "hundred"] + (num_words(n % 100) if n % 100 else [])
    if n < 10000: return [ONES[n // 1000], "thousand"] + (num_words(n % 1000) if n % 1000 else [])
    return [str(n)]

def norm(word):
    """Lower-case letters and digits only, digits said as words ("2.4" -> two point four, "1,440" -> one thousand four hundred forty)."""
    w = word.lower().replace(",", "")
    w = re.sub(r"[^a-z0-9.]", "", w).strip(".")
    if not w: return []
    if re.fullmatch(r"\d+(\.\d+)?", w):
        whole, _, frac = w.partition(".")
        out = num_words(whole)
        if frac: out += ["point"] + [ONES[int(c)] for c in frac]
        return out
    return [w]

job = json.load(open(sys.argv[1])); wav, sents = job["wav"], job["sentences"]
res = mlx_whisper.transcribe(wav, path_or_hf_repo=MODEL, word_timestamps=True, language="en", initial_prompt=" ".join(sents),
                             condition_on_previous_text=False, temperature=0.0)
heard = []   # (norm word, start, end)
for seg in res["segments"]:
    for w in seg.get("words", []):
        for n in norm(w["word"]): heard.append((n, float(w["start"]), float(w["end"])))
script, owner = [], []   # norm words of the script, and which sentence each belongs to
for i, s in enumerate(sents):
    for raw in s.split():
        for n in norm(raw): script.append(n); owner.append(i)
sm = difflib.SequenceMatcher(None, script, [h[0] for h in heard], autojunk=False)
match = {}   # script word index -> heard word index
for a, b, size in sm.get_matching_blocks():
    for k in range(size): match[a + k] = b + k
duration = max((h[2] for h in heard), default=0.0)
out = []
for i in range(len(sents)):
    idx = [k for k, o in enumerate(owner) if o == i]
    hit = [k for k in idx if k in match]
    if hit:
        first, last = hit[0], hit[-1]
        start = heard[match[first]][1] - 0.28 * (first - idx[0])
        end = heard[match[last]][2] + 0.28 * (idx[-1] - last)
    else:
        start = end = None
    out.append([start, end])
# sentences with no matched word at all take the gap between their neighbours
for i, (st, en) in enumerate(out):
    if st is None:
        prev_end = next((out[j][1] for j in range(i - 1, -1, -1) if out[j][1] is not None), 0.0)
        next_start = next((out[j][0] for j in range(i + 1, len(out)) if out[j][0] is not None), duration)
        out[i] = [prev_end, next_start]
# monotonic, inside the audio
t = 0.0
for i in range(len(out)):
    out[i][0] = max(out[i][0], t); out[i][1] = max(out[i][1], out[i][0] + 0.3); t = out[i][1]
speech_end = max(duration, out[-1][1]) if out else duration
print(json.dumps({"sentences": [{"start": round(a, 3), "end": round(b, 3)} for a, b in out], "speech_end": round(speech_end, 3),
                  "heard": " ".join(h[0] for h in heard), "matched": len(match), "script_words": len(script)}))
