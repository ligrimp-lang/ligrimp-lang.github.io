#!/usr/bin/env python3
"""The question engine's episodes (docs/promotion-engine-proposal-2026-10-28.md), told through a cat: C × A × T,
consumption times ambient pressure times time, is the gas a dive needs (Rustam, 2026-10-28). Three episodes, each
under a minute so it works as a Reel: `gas-for-the-dive` (the cat), `sac-rate` (the C, from a dive you have done),
`minimum-gas` (the same cat for two divers in a hurry). Reuses the site generator's phone, caption and font helpers
(tools/build-media.py). The voice is synthesised in passages of connected sentences (new=True starts one), so the
intonation carries across them; each sentence is then located in the audio (tools/align-sentences.py) so that the cards
change on their first words and a captions file goes out with the video. Nothing spoken is drawn on the screen (Rustam,
2026-10-29: the voiceover's text is unnecessary; the card's own text is the only content, so it is big). A young US male
voice; a cat, simple and unusual, drawn as a charcoal sketch on a sheet of paper (his 2026-10-29 reference).

    python3 tools/pilot-episode.py gas-for-the-dive script   # the words, for the correctness review
    python3 tools/pilot-episode.py gas-for-the-dive time     # synthesise the voice and print each cut's length
    python3 tools/pilot-episode.py gas-for-the-dive wide     # 1920x1080, YouTube and the page
    python3 tools/pilot-episode.py gas-for-the-dive short    # 1080x1920, Reel / Short
    python3 tools/pilot-episode.py all all                   # every episode, both cuts
Outputs in build/pilot/: <episode>-<cut>.mp4, <episode>-thumb.png, <episode>.srt (the captions). The same words in both cuts.
"""
import os, re, sys, json, math, random, hashlib, subprocess, importlib.util, functools
from PIL import Image, ImageDraw, ImageFilter, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("bm", os.path.join(HERE, "build-media.py"))
bm = importlib.util.module_from_spec(spec); spec.loader.exec_module(bm)
PROJECTS, BUILD, FPS, ACCENT, P = bm.PROJECTS, bm.BUILD, bm.FPS, bm.ACCENT, bm.P
font, phone, wrap, app_icon, run, caption_layer = bm.font, bm.phone, bm.wrap, bm.app_icon, bm.run, bm.caption_layer

WORK = os.path.join(BUILD, "pilot"); os.makedirs(WORK, exist_ok=True)
CLIPS = f"{PROJECTS}/surface_interval/reference-footage/clips"
SHOTS = {"dive-log": (f"{PROJECTS}/sharewater_dive_log/design/screenshots/dive-log-site", "DIVE LOG", "img/dive-log.png"),
         "turn-pressure": (f"{PROJECTS}/turn_pressure/design/screenshots/turn-pressure", "TURN PRESSURE", "img/turn-pressure.png")}
# The voice: "kokoro:<voice>" runs the Kokoro neural model in build/kokoro-venv (tools/kokoro-say.py; American
# male voices am_puck, am_michael, am_fenrir, am_adam, am_echo…), "say:<name>" a macOS system voice. Rustam,
# 2026-10-28, on the system voice: "terrible metallic", so Kokoro is the default. PILOT_VOICE overrides.
VOICE = os.environ.get("PILOT_VOICE", "orpheus:leo")   # Rustam's pick, 2026-10-28, from samples of three engines
RATE, SPEED = 168, 1.06          # the macOS rate; Kokoro's speed
KOKORO_PY = os.path.join(bm.ROOT, "build", "kokoro-venv", "bin", "python")
ORPHEUS_PY = os.path.join(bm.ROOT, "build", "orpheus-venv", "bin", "python")   # "orpheus:<leo|dan|zac>[:temperature]", see tools/orpheus-say.py
CHATTERBOX_PY = os.path.join(bm.ROOT, "build", "chatterbox-venv", "bin", "python")   # "chatterbox:default[:exaggeration:cfg]", tools/chatterbox-say.py
SPOKEN = [(r"\bSAC\b", "sack"), (r"\bSCR\b", "S.C.R."), (r"\bDCR\b", "D.C.R."), (r"\bRMV\b", "R.M.V."), (r"\bpsi\b", "P.S.I."), (r"\bEAN\b", "E.A.N.")]   # said, not shown
GAP, PAD, LEAD, FADE = 0.25, 0.8, 0.3, 0.5   # between sentences (unused since passages); after a passage; before the first; layer fades
# pt_per_px: the points one frame pixel is on the viewer's screen (a 1080-wide Reel on a 390-pt iPhone; a 1920-wide video in a
# 1280-pt window), for the type's optical size and the minimum size. safe: the box text keeps to (x0, y0, x1, y1): on the short cut the
# top 14% and the bottom 25% are under the platforms' chrome and the right-hand column under their buttons (docs/episode-type-system.md).
FMT = {"wide": dict(W=1920, H=1080, phone_h=1210, phone_top=70, drift=80, pt_per_px=0.667, safe=(120, 70, 1800, 1010)),
       "short": dict(W=1080, H=1920, phone_h=880, phone_top=540, drift=90, pt_per_px=0.361, safe=(72, 270, 910, 1440))}

# One entry per episode. The cat is per episode: cat="<pose>" on a card and thumb_cat on the entry; none at all on sac-rate (Rustam,
# 2026-10-31: nobody asked for a cat in a SAC episode) and none on a new episode unless he says so.
# One entry per episode. Footage clips must show no diver's face (Rustam, 2026-10-21: no pictures of him in a wetsuit; two-divers-facing,
# diver-over-reef and reef-drill-deep are him). Segment kinds: footage (a card over a reef clip), card (over the family's blurred loop; cat="<pose>"
# puts one of Rustam's cat drawings beside it), phone (an app screenshot with the site's caption), outro. Every segment is in both cuts.
WORKED = "A worked example with made-up numbers, not your dive."
# Every episode is a story in Rustam's order (2026-10-28): the problem the diver has, then the definitions, then one worked example, then
# the practical wrap-up (into bar, by the cylinder). Never facts before the context is set.
# The voice is the story and is written first, as one person talking to another: whole sentences, each following from the one before,
# every number arriving inside a sentence that says what it is and why it is needed. A card carries only a title and the figure the voice
# is reaching, drawn big; the spoken sentence is not drawn (2026-10-29), it goes out as the captions file. "Cat" is said as the word; the letters are spoken only when each is
# defined. Nothing is rendered before Rustam has read the words (his 2026-10-28 verdict on the first takes: word salad, no narrative).
EPISODES = {
 "gas-for-the-dive": dict(
  question="How much gas does a dive need?", thumb_cat="standing", thumb_sub="remember a cat: C × A × T", clip="turtle-slope",
  segments=[
   dict(kind="footage", clip="turtle-slope", title="The question", big="How much gas does your dive need?",
        voice="You are planning a dive, say forty minutes at around twenty metres. Will the gas on your back cover it?"),
   dict(kind="card", cat="standing", title="The cat", big="C × A × T",
        voice="Divers work that out with a cat."),
   dict(new=True, kind="card", cat="standing", title="C is consumption", big="Your SAC rate: 15 litres a minute", foot=WORKED,
        voice="C is your consumption, your SAC rate: what you breathe in a minute at the surface. Say fifteen litres a minute."),
   dict(kind="card", cat="swimming", title="A is the average pressure", big="20 m: 1 + 2 = 3 bar",
        voice="A is the pressure at your average depth: one bar at the surface, plus one for every ten metres. Twenty metres: three bar."),
   dict(kind="card", cat="swimming", title="T is time", big="40 minutes",
        voice="T is the time of the dive: forty minutes."),
   dict(new=True, kind="card", cat="standing", title="Multiply", big="15 × 3 × 40 = 1,800 litres",
        voice="Fifteen, times three, times forty: eighteen hundred litres."),
   dict(kind="card", cat="gauge", title="Into bar", big="1,800 L ÷ 12 L = 150 bar",
        voice="Your gauge reads bar, so divide by the size of your cylinder. Twelve litres: a hundred and fifty bar."),
   dict(kind="card", cat="gauge", title="Plus minimum gas", big="150 bar for the dive, then your minimum gas",
        voice="That is the dive. Your minimum gas comes on top."),
   dict(new=True, kind="phone", app="turn-pressure", shot="1-inputs", pill="Free app", head="Turn Pressure works out both for the dive you are planning", sub="The gas for the dive, and the minimum gas to keep",
        voice="Turn Pressure works out both for your dive."),
   dict(kind="outro", voice="Free on the App Store. diver dot today."),
  ]),
 "sac-rate": dict(
  # Redone 2026-10-31 after Rustam's verdict on the first take, the GUE expert's review and his structure (docs/pilot-postmortem-sac-2026-10-31.md),
  # and again on 2026-11-01 after he watched the render: a slower pace with a pause after every number (hold=), one example dive kept in
  # view on every step (scenario=, lit per step by uses=), formula cards whose every number carries a label and whose result appears on the
  # beat (figures=, result=), the term explained with why SAC is not used, and the type system in docs/episode-type-system.md. SCR is the term,
  # GUE's and his decision; the GUE reviews' wording stays ("reserves", the transmitter clause, "soon over time", the 20 L/min table he
  # approved). No cat anywhere in it. Every figure is on the check list in the post-mortem; nothing is rendered before the Mac has
  # checked it and Rustam has read the words.
  question="Your surface consumption rate, or SAC: work it out step by step", thumb_cat=None, thumb_sub="from any dive, without hard maths", clip="dolphins-blue",
  scenario=[("depth", "average depth", "20 m"), ("time", "dive time", "40 min"), ("tank", "aluminium tank", "11.1 L"), ("bar", "gauge, start \u2192 end", "200 \u2192 40 bar")],
  segments=[
   dict(kind="footage", clip="dolphins-blue", title="Gas planning", big="One number to plan your dives with",
        voice="To plan dives and reserves you need one number: a key part of gas planning."),
   dict(new=True, kind="card", title="The number", big="Surface consumption rate",
        rows=[("SCR", "its short form"), ("Unit", "litres a minute, at the surface"), ("Also SAC", "surface air consumption, though the gas is not always air: nitrox, trimix")], hold=1.0,
        voice="Your surface consumption rate, SCR: the litres you breathe in a minute at the surface. Also called SAC, surface air consumption, but the gas is not always air: nitrox, trimix."),
   dict(new=True, kind="card", title="Our example", uses="all", lines=["every step below uses these four values"], hold=1.5,
        voice="An example dive: twenty metres average depth, forty minutes, an eleven point one litre aluminium tank, two hundred bar down to forty."),
   dict(kind="card", title="Step 1 \u00b7 gas used", uses=["bar"], figures=[("200 bar", "start"), "\u2212", ("40 bar", "end")], result=("160 bar", "used"), hold=1.2,
        voice="Step one: two hundred down to forty bar. A hundred and sixty bar used."),
   dict(kind="card", title="Step 2 \u00b7 litres", uses=["bar", "tank"], figures=[("160 bar", "used"), "\u00d7", ("11.1 L", "tank")], result=("1,776 L", "gas used"), hold=1.2,
        voice="Step two: a hundred and sixty bar times eleven point one litres. Seventeen hundred and seventy-six litres."),
   dict(new=True, kind="card", title="Step 3 \u00b7 litres a minute", uses=["time"], figures=[("1,776 L", "gas used"), "\u00f7", ("40 min", "dive time")], result=("44.4 L/min", "at depth"), hold=1.2,
        voice="Step three: over forty minutes. Forty-four point four litres a minute at depth."),
   dict(kind="card", title="Step 4 \u00b7 pressure at depth", uses=["depth"], figures=[("20 m", "average depth"), "\u00f7 10 + 1"], result=("3 ATA", "pressure at 20 m"), hold=1.0,
        voice="Step four: twenty metres is twenty over ten, plus one. Three atmospheres."),
   dict(kind="card", title="Step 5 \u00b7 back to the surface", uses=["depth"], figures=[("44.4 L/min", "at depth"), "\u00f7", ("3 ATA", "pressure")], result=("14.8 \u2192 15 L/min", "your SCR, rounded up"), hold=2.0,
        voice="Step five: divide by that pressure. Fourteen point eight, rounded up to fifteen litres a minute at the surface. That is your rate."),
   dict(new=True, kind="card", title="Several dives, easy and hard", big="Plan with the higher figure", lines=["rounded up"], hold=0.8,
        voice="Over several dives, easy and hard, plan with the higher figure, rounded up."),
   dict(kind="card", title="An easy rule: 20 L/min", big="Bar every 5 minutes",
        table=[("", "single AL80", "double AL80"), ("10 m", "20 bar", "10 bar"), ("20 m", "30 bar", "15 bar"), ("30 m", "40 bar", "20 bar")],
        foot="Rounded up. Breathe more? Use your own figure. Breathe less? This adds a margin.", hold=2.0,
        voice="For an easy rule, plan with twenty litres a minute: in bar, every five minutes. Breathe more? Use your own number. Breathe less? Extra margin."),
   dict(new=True, kind="phone", app="dive-log", shot="1-dive-page/00", pill="Free app", head="Dive log shows your rate for each dive", sub="Your Shearwater dives, as the computer logged them",
        voice="Some computers track it with a transmitter; for Shearwater divers, Dive log shows it for each dive, and soon over time."),
   dict(kind="outro", voice="Free on the App Store. diver dot today."),
  ]),
 "minimum-gas": dict(
  question="What is minimum gas?", thumb_cat="sharing", thumb_sub="the same cat, for two divers on the way up", clip="reef-slope",
  segments=[
   dict(kind="footage", clip="reef-slope", title="The question", big="What is minimum gas?",
        voice="At the deepest point your buddy signals: out of gas. You share, and you both go up. How much must be left for that? That is minimum gas."),
   dict(new=True, kind="card", cat="sharing", title="The cat, for two", big="C × A × T, for the way up",
        voice="Work it out with the cat: consumption times pressure times time, for two on the way up."),
   dict(kind="card", cat="sharing", title="C is consumption, for two", big="20 + 20 = 40 litres a minute", foot="A worked example. Courses differ on the rate for a stressed diver.",
        voice="C: two stressed divers, say twenty litres a minute each. Forty together."),
   dict(new=True, kind="card", cat="sharing", title="A minute to sort it out", big="40 × 4 bar × 1 min = 160 litres", lines=["30 m: 30 ÷ 10 + 1 = 4 bar"],
        voice="A minute at thirty metres to sort it out. Thirty metres is four bar: a hundred and sixty litres."),
   dict(kind="card", cat="ascending", title="The ascent", big="40 × 2.5 bar × 3.3 min ≈ 330 litres", lines=["30 m at 9 m/min = 3.3 min · (4 + 1) ÷ 2 = 2.5 bar"],
        voice="Then the ascent at nine metres a minute: three point three minutes at two and a half bar on average, three hundred and thirty litres."),
   dict(new=True, kind="card", cat="gauge", title="Together", big="≈ 490 L ÷ 11 L = 45 bar", foot="The cat's example, not a minimum gas for your dive.",
        voice="Nearly five hundred litres: from an eleven-litre cylinder, forty-five bar."),
   dict(kind="card", cat="gauge", title="The rule", big="At minimum gas, the dive is over",
        voice="When your gauge gets there, the dive is over, whatever the plan said."),
   dict(kind="phone", app="turn-pressure", shot="5-plan-two-level", pill="Free app", head="Turn Pressure works out minimum gas for the dive you are planning", sub="And the turn pressure: when to turn the dive",
        voice="Turn Pressure works it out for your dive."),
   dict(kind="outro", voice="Free on the App Store. diver dot today."),
  ]),
}

# ---------- voice ----------
def sentences(text):
    return [s.strip() for s in re.split(r'(?<=[.?!;])\s+', text.strip()) if s.strip()]

def spoken(text):
    for pat, rep in SPOKEN: text = re.sub(pat, rep, text)
    return text

TEMPO = float(os.environ.get("PILOT_TEMPO", "1"))   # Orpheus and Chatterbox have no speed of their own: their passages can be sped up with ffmpeg's
                                                       # atempo after synthesis (1.04 is not heard). Not needed since passages: Leo tells an episode in about 50 s.

def base_path(text):
    return os.path.join(WORK, "s-" + hashlib.sha1((VOICE + str(RATE) + str(SPEED) + text).encode()).hexdigest()[:12] + ".wav")

def wav_path(text):
    """The sentence as used: the synthesised file, or a tempo-changed copy of it for the engines without a speed."""
    if TEMPO == 1 or VOICE.split(":")[0] in ("kokoro", "say"): return base_path(text)
    return os.path.join(WORK, "t-" + hashlib.sha1((VOICE + str(TEMPO) + text).encode()).hexdigest()[:12] + ".wav")

def synthesise(texts):
    """Every sentence not yet on disk, as 48 kHz stereo wav, in one go (the model loads once); then the tempo copies."""
    texts = list(dict.fromkeys(texts))
    todo = [t for t in texts if not os.path.exists(base_path(t))]
    engine, _, name = VOICE.partition(":")
    if todo:
        raws = []
        if engine == "kokoro":
            jobs = [[spoken(t), base_path(t)[:-4] + ".raw.wav"] for t in todo]
            jp = os.path.join(WORK, "jobs.json"); json.dump(jobs, open(jp, "w"))
            subprocess.run([KOKORO_PY, os.path.join(HERE, "kokoro-say.py"), jp, name, str(SPEED)], check=True, stdout=subprocess.DEVNULL)
            raws = [r for _, r in jobs]
        elif engine == "orpheus":
            jobs = [[spoken(t), base_path(t)[:-4] + ".raw.wav"] for t in todo]
            jp = os.path.join(WORK, "jobs.json"); json.dump(jobs, open(jp, "w"))
            subprocess.run([ORPHEUS_PY, os.path.join(HERE, "orpheus-say.py"), jp] + name.split(":"), check=True, stdout=subprocess.DEVNULL)
            raws = [r for _, r in jobs]
        elif engine == "chatterbox":
            jobs = [[spoken(t), base_path(t)[:-4] + ".raw.wav"] for t in todo]
            jp = os.path.join(WORK, "jobs.json"); json.dump(jobs, open(jp, "w"))
            subprocess.run([CHATTERBOX_PY, os.path.join(HERE, "chatterbox-say.py"), jp] + name.split(":"), check=True, stdout=subprocess.DEVNULL)
            raws = [r for _, r in jobs]
        else:
            for t in todo:
                r = base_path(t)[:-4] + ".aiff"; raws.append(r)
                subprocess.run(["say", "-v", name, "-r", str(RATE), "-o", r, spoken(t)], check=True)
        for t, r in zip(todo, raws):
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", r, "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", base_path(t)], check=True)
            os.remove(r)
    for t in texts:
        if wav_path(t) != base_path(t) and not os.path.exists(wav_path(t)):
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", base_path(t), "-af", f"atempo={TEMPO}", "-c:a", "pcm_s16le", wav_path(t)], check=True)

def say(text):
    """One sentence's wav and its length in seconds (synthesise() has run for it)."""
    wav = wav_path(text)
    if not os.path.exists(wav): synthesise([text])
    d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", wav]).strip())
    return wav, d

def silence(d):
    p = os.path.join(WORK, f"sil-{d:.3f}.wav")
    if not os.path.exists(p):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", f"{d:.3f}", "-c:a", "pcm_s16le", p], check=True)
    return p

def passages(segs):
    """Consecutive segments whose voice is synthesised as one piece, so the intonation runs across the sentences (Rustam,
    2026-10-28: sentence by sentence "its not possible to follow"). A segment with new=True starts a passage; the first always does."""
    groups = []
    for i, x in enumerate(segs):
        if i == 0 or x.get("new"): groups.append([])
        groups[-1].append(i)
    return groups

def align(wav, spoken_sents):
    """Each sentence's start and end inside the passage audio, by tools/align-sentences.py (Whisper word timestamps); cached beside the wav."""
    cache = wav[:-4] + "-" + hashlib.sha1("\n".join(spoken_sents).encode()).hexdigest()[:8] + ".align.json"
    if not os.path.exists(cache):
        job = os.path.join(WORK, "align-job.json"); json.dump({"wav": wav, "sentences": spoken_sents}, open(job, "w"))
        out = subprocess.check_output([ORPHEUS_PY, os.path.join(HERE, "align-sentences.py"), job], stderr=subprocess.DEVNULL)
        open(cache, "wb").write(out)
    return json.load(open(cache))

def cut(wav, a, b):
    p = os.path.join(WORK, "c-" + hashlib.sha1(f"{wav}{a:.3f}{b:.3f}".encode()).hexdigest()[:12] + ".wav")
    if not os.path.exists(p):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", wav, "-c:a", "pcm_s16le", p], check=True)
    return p

CARD_LEAD = 0.25   # a segment's card appears this long before its first word (within the previous sentence's silence)

def timeline(ep):
    """The episode's segments with their sentences timed: seg['dur'], seg['subs'] = [(start, end, text)] relative to the segment,
    seg['audio'] the wav pieces to concatenate. Each passage is one synthesised piece, cut at the segments' first words."""
    segs = [dict(x) for x in ep["segments"]]
    for x in segs: x.setdefault("scenario", ep.get("scenario"))   # the example dive every step keeps in view
    groups = passages(segs)
    texts = [" ".join(segs[i]["voice"] for i in g) for g in groups]
    synthesise(texts)
    for g, text in zip(groups, texts):
        wav, total = say(text)
        sents = [(i, sent) for i in g for sent in sentences(segs[i]["voice"])]
        al = align(wav, [spoken(sent) for _, sent in sents])
        times = [(a["start"], a["end"]) for a in al["sentences"]]
        end_of_speech = min(total, al["speech_end"] + 0.15)
        first = {}   # segment -> index of its first sentence
        for j, (i, _) in enumerate(sents): first.setdefault(i, j)
        bounds = [0.0]
        for n, i in enumerate(g[1:], 1):
            j = first[i]; prev_end = times[j - 1][1]
            bounds.append(max(prev_end, times[j][0] - CARD_LEAD, bounds[-1] + 0.3))
        bounds.append(max(end_of_speech, bounds[-1] + 0.3))
        for n, i in enumerate(g):
            b0, b1 = bounds[n], bounds[n + 1]; x = segs[i]
            lead = LEAD if n == 0 else 0.0; pad = PAD if n == len(g) - 1 else 0.0
            subs = []
            for j, (i2, sent) in enumerate(sents):
                if i2 != i: continue
                st, en = times[j]; nxt = times[j + 1][0] if j + 1 < len(times) else b1
                subs.append((lead + st - b0, lead + min(en + 0.3, nxt, b1) - b0, sent))
            x["subs"] = subs
            hold = float(x.get("hold", 0))   # a pause after the words, so a number can be taken in (Rustam, 2026-11-01: "let the user think more")
            x["audio"] = ([silence(LEAD)] if lead else []) + [cut(wav, b0, b1)] + ([silence(hold)] if hold else []) + ([silence(PAD)] if pad else [])
            x["dur"] = lead + (b1 - b0) + hold + pad
            # a card's result appears on a beat: at its own `beat`, else when its second sentence starts (a step says the operands, then the
            # result), else early in a one-sentence card
            reveal = x["beat"] if x.get("beat") is not None else (subs[1][0] - CARD_LEAD if len(subs) > 1 else min(0.9, (b1 - b0) * 0.45))
            x["reveal"] = max(0.3, min(reveal, x["dur"] - 0.8))
    return segs

# ---------- drawing ----------
INK, DIM, DARK = (240, 243, 245), (168, 178, 186), (16, 22, 28)
PAPER, CHARCOAL = (238, 236, 231), (22, 22, 24)
CAT_DIR = os.path.join(HERE, "assets", "cat")   # Rustam's own cat drawings, cat-<pose>.png, black strokes on transparent (or white)
CAT_MOUTH = {"standing": (0.13, 0.50), "swimming": (0.12, 0.53), "ascending": (0.22, 0.25), "sharing": (0.14, 0.47), "gauge": (0.26, 0.45),
             "head": (0.22, 0.80), "sketch": (0.20, 0.47)}   # where the bubbles start, as a fraction of the drawing's square, per pose
CAT_SIZE = {"wide": 680, "short": 620}

def bez(p0, p1, p2, p3, n):
    pts = []
    for k in range(n + 1):
        t = k / n; u = 1 - t
        pts.append((u*u*u*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t*t*t*p3[0], u*u*u*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t*t*t*p3[1]))
    return pts

def wobble(pts, amp, rnd):
    return [(x + rnd.uniform(-amp, amp), y + rnd.uniform(-amp, amp)) for x, y in pts]

def stroke(d, pts, width, fill, alpha, rnd, grain=3):
    """A charcoal stroke: a few thin passes side by side, each a little off, so the edge is dry and grainy."""
    for _ in range(grain):
        off = rnd.uniform(-width * 0.4, width * 0.4); ang = rnd.uniform(0, math.pi)
        dx, dy = off * math.cos(ang), off * math.sin(ang)
        d.line([(x + dx, y + dy) for x, y in pts], fill=fill + (int(alpha * rnd.uniform(0.6, 1.0)),),
               width=max(1, int(width * rnd.uniform(0.45, 0.85))), joint="curve")

def tapered(d, pts, w0, w1, fill, alpha):
    n = len(pts) - 1
    for k in range(n):
        w = w0 + (w1 - w0) * k / n
        d.line([pts[k], pts[k + 1]], fill=fill + (alpha,), width=max(1, int(w)))
        x, y = pts[k]; d.ellipse((x - w/2, y - w/2, x + w/2, y + w/2), fill=fill + (alpha,))

def sketch_cat(size, seed=11):
    """A black cat in loose charcoal strokes, drawn here until Rustam's own drawings arrive (the look he pointed at on 2026-10-29: a
    silhouette built from flowing dark strokes, a sweeping tail, two sharp ears; nothing of anyone's drawing copied). The diving kit is
    one teal line: a mask over the eye, a hose to a cylinder on its back. RGBA, charcoal on transparent, `size` square."""
    rnd = random.Random(seed); ink = CHARCOAL
    S = size * 3
    def P(x, y): return (x * S, y * S)
    body = [P(0.13, 0.47), P(0.15, 0.38), P(0.19, 0.33), P(0.175, 0.19), P(0.27, 0.30), P(0.32, 0.29), P(0.36, 0.29), P(0.40, 0.16), P(0.44, 0.33),
            P(0.50, 0.345), P(0.62, 0.315), P(0.74, 0.34), P(0.84, 0.44), P(0.87, 0.56), P(0.86, 0.66), P(0.885, 0.90), P(0.815, 0.91), P(0.79, 0.80),
            P(0.775, 0.70), P(0.66, 0.715), P(0.52, 0.72), P(0.455, 0.73), P(0.46, 0.90), P(0.385, 0.91), P(0.37, 0.78), P(0.345, 0.70),
            P(0.27, 0.66), P(0.20, 0.60), P(0.145, 0.53)]
    mask = Image.new("L", (S, S), 0); ImageDraw.Draw(mask).polygon(body, fill=255)
    far_legs = Image.new("L", (S, S), 0); fd = ImageDraw.Draw(far_legs)
    fd.polygon([P(0.43, 0.72), P(0.50, 0.72), P(0.53, 0.905), P(0.45, 0.91)], fill=255)
    fd.polygon([P(0.71, 0.70), P(0.78, 0.70), P(0.78, 0.905), P(0.70, 0.91)], fill=255)
    out = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    far = Image.new("RGBA", (S, S), ink + (0,)); far.putalpha(far_legs.filter(ImageFilter.GaussianBlur(S*0.006)).point(lambda v: v * 120 // 255))
    out.alpha_composite(far)
    grad = Image.linear_gradient("L").resize((S, S)).point(lambda v: 185 - v * 95 // 255)   # darker along the back, lighter under the belly
    massa = ImageChops.multiply(mask.filter(ImageFilter.GaussianBlur(S*0.006)), grad)
    mass = Image.new("RGBA", (S, S), ink + (0,)); mass.putalpha(massa); out.alpha_composite(mass)
    strokes = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(strokes)
    bc = (S*0.56, S*0.62)
    for _ in range(330):
        for _try in range(30):
            x, y = rnd.uniform(S*0.10, S*0.92), rnd.uniform(S*0.14, S*0.94)
            if mask.getpixel((int(x), int(y))) > 0: break
        else:
            continue
        if x < S*0.40 and y < S*0.62: ang = rnd.uniform(-0.35, 0.15)
        elif y > S*0.74: ang = math.pi/2 + rnd.uniform(-0.15, 0.15)
        else:
            ang = math.atan2(y - bc[1], x - bc[0]) + math.pi/2 + rnd.uniform(-0.12, 0.12)
            if rnd.random() < 0.05: ang += rnd.uniform(-0.8, 0.8)
        L = rnd.uniform(S*0.16, S*0.42) if y <= S*0.74 else rnd.uniform(S*0.06, S*0.16)
        pts = []; bend = rnd.uniform(-0.6, 0.6)
        for k in range(6):
            t = -0.5 + k / 5
            pts.append((x + L*t*math.cos(ang) - L*0.6*bend*t*t*math.sin(ang), y + L*t*math.sin(ang) + L*0.6*bend*t*t*math.cos(ang)))
        stroke(d, wobble(pts, S*0.002, rnd), rnd.uniform(S*0.008, S*0.03), ink, rnd.uniform(90, 230), rnd, grain=4)
    clip = mask.filter(ImageFilter.MaxFilter(int(S*0.012) | 1)).filter(ImageFilter.GaussianBlur(S*0.012)).point(lambda v: min(255, int(v * 1.5)))
    strokes.putalpha(ImageChops.multiply(strokes.split()[3], clip))
    strokes = strokes.filter(ImageFilter.GaussianBlur(S*0.0015))
    out.alpha_composite(strokes); d = ImageDraw.Draw(out)
    for k in range(7):   # long loose contour strokes: the back, the chest, the belly
        p0 = (S*rnd.uniform(0.36, 0.44), S*rnd.uniform(0.30, 0.36)); p3 = (S*rnd.uniform(0.78, 0.86), S*rnd.uniform(0.42, 0.50))
        stroke(d, bez(p0, (S*0.55, S*rnd.uniform(0.30, 0.34)), (S*0.72, S*rnd.uniform(0.33, 0.38)), p3, 24), rnd.uniform(S*0.010, S*0.022), ink, rnd.uniform(100, 180), rnd, grain=4)
    for k in range(4):
        p0 = (S*rnd.uniform(0.14, 0.18), S*rnd.uniform(0.54, 0.58)); p3 = (S*rnd.uniform(0.32, 0.38), S*rnd.uniform(0.72, 0.76))
        stroke(d, bez(p0, (S*0.18, S*0.64), (S*0.26, S*0.71), p3, 16), rnd.uniform(S*0.008, S*0.016), ink, rnd.uniform(80, 140), rnd)
    for k in range(4):
        p0 = (S*rnd.uniform(0.46, 0.50), S*rnd.uniform(0.74, 0.78)); p3 = (S*rnd.uniform(0.72, 0.78), S*rnd.uniform(0.72, 0.76))
        stroke(d, bez(p0, (S*0.56, S*0.80), (S*0.68, S*0.79), p3, 16), rnd.uniform(S*0.006, S*0.014), ink, rnd.uniform(60, 120), rnd)
    for base, tip, inner in ((P(0.19, 0.33), P(0.175, 0.19), P(0.27, 0.30)), (P(0.36, 0.29), P(0.40, 0.16), P(0.44, 0.32))):   # ears
        stroke(d, wobble([base, tip, inner], S*0.003, rnd), S*0.012, ink, 230, rnd, grain=3)
    for px in (0.425, 0.84, 0.485, 0.745):   # paws, and a soft shadow on the ground
        d.ellipse((S*(px - 0.035), S*0.895, S*(px + 0.035), S*0.93), fill=ink + (200,))
    for k in range(6):
        stroke(d, [(S*rnd.uniform(0.30, 0.42), S*rnd.uniform(0.93, 0.95)), (S*rnd.uniform(0.80, 0.94), S*rnd.uniform(0.93, 0.955))], S*0.012, ink, rnd.uniform(20, 55), rnd, grain=2)
    tail = bez(P(0.84, 0.50), P(1.02, 0.46), P(0.97, 0.08), P(0.74, 0.05), 60)   # a sweep up and over, scribbled along its length
    tapered(d, tail, S*0.075, S*0.01, ink, 190)
    for k in range(18):
        off = rnd.uniform(-1, 1); i0 = rnd.randint(0, 22); i1 = rnd.randint(i0 + 12, 60)
        pts = [(x + off*S*0.028*(1 - i/60), y + off*S*0.028*(1 - i/60)) for i, (x, y) in enumerate(tail)]
        stroke(d, wobble(pts[i0:i1], S*0.004, rnd), rnd.uniform(S*0.005, S*0.02), ink, rnd.uniform(110, 230), rnd, grain=2)
    for k in range(4):
        i = rnd.randint(2, 16); x, y = tail[i]; a = math.atan2(tail[i+1][1] - y, tail[i+1][0] - x) + rnd.uniform(-0.5, 0.5); L = S*rnd.uniform(0.03, 0.06)
        stroke(d, [(x - L*math.cos(a), y - L*math.sin(a)), (x + L*math.cos(a), y + L*math.sin(a))], S*rnd.uniform(0.005, 0.012), ink, rnd.uniform(80, 160), rnd, grain=2)
    ex, ey = S*0.215, S*0.44   # eye, whiskers
    d.ellipse((ex - S*0.028, ey - S*0.015, ex + S*0.028, ey + S*0.015), fill=PAPER + (240,))
    d.ellipse((ex - S*0.007, ey - S*0.013, ex + S*0.007, ey + S*0.013), fill=ink + (255,))
    for dy in (-0.012, 0.0, 0.012):
        stroke(d, [(S*0.17, S*(0.50 + dy*0.3)), (S*(0.05 + rnd.uniform(-0.01, 0.01)), S*(0.49 + dy*2.5))], S*0.0035, ink, 110, rnd, grain=1)
    t = ACCENT   # the kit: mask rim and strap, regulator in the mouth, cylinder on the back, hose over the head
    rim = [(ex + S*0.052*math.cos(a), ey + S*0.038*math.sin(a)) for a in [i*2*math.pi/40 for i in range(41)]]
    stroke(d, wobble(rim, S*0.0025, rnd), S*0.009, t, 235, rnd, grain=2)
    stroke(d, wobble([(ex + S*0.05, ey - S*0.012), (S*0.31, S*0.34), (S*0.36, S*0.31)], S*0.0025, rnd), S*0.007, t, 210, rnd, grain=2)
    cyl = Image.new("RGBA", (S, S), (0, 0, 0, 0)); cd = ImageDraw.Draw(cyl)
    cm = Image.new("L", (S, S), 0); ImageDraw.Draw(cm).rounded_rectangle((S*0.52, S*0.30, S*0.66, S*0.60), radius=S*0.055, fill=255)
    body_grey = Image.new("RGBA", (S, S), (120, 122, 126, 0)); body_grey.putalpha(cm.filter(ImageFilter.GaussianBlur(S*0.004)).point(lambda v: v * 235 // 255))
    cyl.alpha_composite(body_grey); cd = ImageDraw.Draw(cyl)
    for k in range(28):
        x = S*rnd.uniform(0.525, 0.655); y0 = S*rnd.uniform(0.30, 0.45); y1 = y0 + S*rnd.uniform(0.08, 0.2)
        stroke(cd, wobble([(x, y0), (x + S*rnd.uniform(-0.006, 0.006), (y0 + y1)/2), (x, y1)], S*0.002, rnd), rnd.uniform(S*0.004, S*0.012), (60, 60, 64), rnd.uniform(30, 90), rnd, grain=2)
    cyl.putalpha(ImageChops.multiply(cyl.split()[3], cm.filter(ImageFilter.GaussianBlur(S*0.003))))
    out.alpha_composite(cyl); d = ImageDraw.Draw(out)
    outline = [P(0.535, 0.305), P(0.645, 0.305), P(0.66, 0.34), P(0.66, 0.57), P(0.645, 0.60), P(0.535, 0.60), P(0.52, 0.57), P(0.52, 0.34), P(0.535, 0.305)]
    stroke(d, wobble(outline, S*0.003, rnd), S*0.009, ink, 190, rnd, grain=3)
    stroke(d, [(S*0.59, S*0.30), (S*0.59, S*0.255)], S*0.016, t, 240, rnd, grain=2)
    hose = bez(P(0.59, 0.255), P(0.54, 0.12), P(0.28, 0.17), P(0.20, 0.47), 30)
    stroke(d, wobble(hose, S*0.0025, rnd), S*0.0075, t, 220, rnd, grain=2)
    d.ellipse((S*0.175, S*0.455, S*0.225, S*0.495), fill=t + (240,))
    noise = Image.effect_noise((S, S), 60).point(lambda v: 120 + v * 135 // 255)   # charcoal grain
    out.putalpha(ImageChops.multiply(out.split()[3], noise))
    return out.resize((size, size), Image.LANCZOS)

def cat_art(pose, size):
    """Rustam's drawing for the pose if it exists (tools/assets/cat/cat-<pose>.png: dark strokes on transparent, or on plain white,
    which is keyed out here), fitted into a square of `size` with a margin; else the sketch above."""
    path = os.path.join(CAT_DIR, f"cat-{pose}.png")
    if not os.path.exists(path): return sketch_cat(size)   # the fallback; its mouth is CAT_MOUTH["sketch"]
    im = Image.open(path).convert("RGBA")
    if im.getextrema()[3][0] == 255:   # no transparency: dark strokes on white become charcoal on transparent
        lum = im.convert("L"); im = Image.new("RGBA", im.size, CHARCOAL + (0,)); im.putalpha(lum.point(lambda v: 255 - v))
    im = im.crop(im.getbbox())
    inner = int(size * 0.84); im.thumbnail((inner, inner), Image.LANCZOS)   # CAT_MOUTH was measured in this fit
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0)); out.alpha_composite(im, ((size - im.width) // 2, (size - im.height) // 2))
    return out

# The drawing's own tones (black fur, grey highlight strokes) are mapped onto a ramp from a deep water-blue, a step lighter than the
# card, to a pale aqua, so the cat is drawn in light on the dark card rather than pasted onto it (Rustam, 2026-10-29: no white
# background, "embedded … so it looks native"); a soft teal glow underneath sets it off from the blurred reef.
CAT_TINTS = {"silver": ((30, 38, 46), (236, 244, 244), (ACCENT, 0.30)),     # the pick: dark body, silver strokes, a whisper of teal glow
             "aqua": ((26, 48, 60), (216, 242, 238), (ACCENT, 0.42)),       # softer: deep water body, pale aqua strokes
             "ink": ((30, 36, 42), (240, 243, 245), (None, 0.0)),             # plain: no glow
             "teal": ((16, 58, 64), (120, 232, 220), (ACCENT, 0.55))}          # bolder: everything teal
CAT_TINT = os.environ.get("PILOT_CAT_TINT", "silver")

@functools.lru_cache(maxsize=None)
def cat(size, pose="standing", tint=None):
    """The cat for a card: RGBA, `size` square, transparent around it."""
    deep, light, (glow, glow_a) = CAT_TINTS[tint or CAT_TINT]
    art = cat_art(pose, size)
    lum = art.convert("L"); alpha = art.split()[3]
    bands = []
    for k, (d, l) in enumerate(zip(deep, light)):   # per channel: deep at black, light at the brightest strokes (gamma so mid greys stay dark)
        bands.append(lum.point(lambda v, d=d, l=l: int(d + (l - d) * (v / 255) ** 0.75)))
    body = Image.merge("RGBA", bands + [alpha])
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    if glow is not None:
        halo = alpha.filter(ImageFilter.GaussianBlur(size * 0.035)).point(lambda v: int(v * glow_a))
        g = Image.new("RGBA", (size, size), glow + (0,)); g.putalpha(halo); out.alpha_composite(g)
    out.alpha_composite(body)
    return out

def cat_mouth(size, pose="standing"):
    """Where the bubbles start, in the cat square's own pixels."""
    fx, fy = CAT_MOUTH.get(pose, CAT_MOUTH["standing"])
    return (fx * size, fy * size)

def cat_place(fmt):
    """Top-left of the cat square on a card: beside the text on a wide frame, above it on a tall one."""
    W, H = fmt["W"], fmt["H"]; size = CAT_SIZE["short" if W < H else "wide"]
    return ((W - size) // 2, 120) if W < H else (W - size - 120, (H - size) // 2 - 10)

def bubble(diam):
    """A ring that shows on the paper and on the dark background alike."""
    im = Image.new("RGBA", (diam + 6, diam + 6), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((3, 3, diam + 3, diam + 3), outline=(150, 162, 170, 225), width=max(2, diam // 10), fill=(255, 255, 255, 40))
    d.ellipse((3 + diam*0.22, 3 + diam*0.18, 3 + diam*0.42, 3 + diam*0.34), fill=(255, 255, 255, 200))
    return im

MUTED = (178, 198, 208)      # secondary text: a cool grey-blue, a clear step down from the ink and apart from the teal
PANEL = (8, 14, 20, 186)     # the scrim behind text: the water's bright top washes out white type (Rustam, 2026-11-01)
UNLIT = (112, 126, 136)      # a scenario value the step does not use
# Sizes in frame pixels per cut (docs/episode-type-system.md): on the short cut 34 px is about 12 pt on an iPhone, above Apple's 11-pt
# floor; big lines and figures are Display sizes, labels and footnotes Text sizes; a clear step between each level.
TYPE = {"short": dict(title=34, big=92, line=46, foot=34, fig=96, lab=34, res=104, sv=46, sl=32),
        "wide":  dict(title=38, big=104, line=52, foot=38, fig=108, lab=38, res=116, sv=50, sl=34)}
WEIGHTS = {"Regular": 400, "Medium": 500, "Semibold": 600, "Bold": 700, "Heavy": 800}

def typeface(fmt, size, weight="Regular"):
    """SF Pro at `size` with its optical size set to the points the viewer sees: SF Pro is one variable font whose design moves from the
    Text cut to the Display cut between 17 and 28 pt (Apple, WWDC20), so small labels get the Text cut and big lines the Display cut
    when the axis is there. A font without the axis (DejaVu standing in off the Mac) is used as it is."""
    f = font(size, weight)
    try:
        axes = f.get_variation_axes()
        names = [(a.get("name") or b"").decode("latin-1") if isinstance(a.get("name"), bytes) else str(a.get("name") or "") for a in axes]
        if any("ptical" in n or n.lower() == "opsz" for n in names):
            vals = []
            for a, n in zip(axes, names):
                if "ptical" in n or n.lower() == "opsz": v = size * fmt["pt_per_px"]
                elif "eight" in n or n.lower() == "wght": v = WEIGHTS.get(weight, 400)
                else: v = a["default"]
                vals.append(max(a["minimum"], min(a["maximum"], v)))
            f.set_variation_by_axes(vals)
    except Exception:
        pass
    return f

def panel(layer, box, radius=36):
    """The scrim: a rounded dark panel behind a block of text."""
    ImageDraw.Draw(layer).rounded_rectangle(box, radius=radius, fill=PANEL)

def scenario_strip(fmt, scenario, uses):
    """The example dive, kept in view on every step: a compact strip of its values, the ones this step uses lit in teal, the rest dimmed
    (Rustam, 2026-11-01: the viewer always has the scenario in front of them). A 2×2 grid on the short cut, one row on the wide."""
    W, H = fmt["W"], fmt["H"]; tall = W < H; T = TYPE["short" if tall else "wide"]
    sx0, sy0, sx1, sy1 = fmt["safe"]; width = sx1 - sx0
    f_cap, f_v, f_l = typeface(fmt, T["title"] - 6, "Semibold"), typeface(fmt, T["sv"], "Semibold"), typeface(fmt, T["sl"], "Regular")
    cols = 2 if tall else len(scenario); rows = -(-len(scenario) // cols)
    cell_h = int(T["sv"] * 1.2 + T["sl"] * 1.35); pad = 28; cap_h = int(T["title"] * 1.1)
    h = pad + cap_h + rows * cell_h + pad
    im = Image.new("RGBA", (width, h), (0, 0, 0, 0)); panel(im, (0, 0, width - 1, h - 1), radius=30); d = ImageDraw.Draw(im)
    bm.draw_spaced(d, (pad, pad - 2), "EXAMPLE DIVE", f_cap, ACCENT, 2.4)
    cw = (width - 2 * pad) // cols
    for i, (key, label, value) in enumerate(scenario):
        lit = uses == "all" or key in uses
        cx = pad + (i % cols) * cw + cw // 2; cy = pad + cap_h + (i // cols) * cell_h
        d.text((cx - d.textlength(value, font=f_v) / 2, cy), value, font=f_v, fill=ACCENT if lit else UNLIT)
        d.text((cx - d.textlength(label, font=f_l) / 2, cy + int(T["sv"] * 1.15)), label, font=f_l, fill=MUTED if lit else UNLIT)
    return im, h

def card_layer(fmt, s, pose, stage=None):
    """A card: a small spaced title in teal, a big line, secondary lines, a figures row (each number with a small label under it) and a
    result, a table, a footnote; on a dark panel inside the safe area so it reads over the bright top of the water; the example-dive
    strip above it when the segment names what it `uses`. Big, because it is the only content on the screen (Rustam, 2026-10-29).
    `stage` "base" draws everything but the result (its space kept), "result" the result alone: it appears on the segment's beat.
    The cat beside it (wide) or above it (short) when the segment names a pose."""
    W, H = fmt["W"], fmt["H"]; tall = W < H; T = TYPE["short" if tall else "wide"]
    sx0, sy0, sx1, sy1 = fmt["safe"]
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    tf = lambda k, w: typeface(fmt, T[k], w)
    f_title, f_big, f_line, f_foot = tf("title", "Semibold"), tf("big", "Bold"), tf("line", "Medium"), tf("foot", "Regular")
    f_fig, f_lab, f_res = tf("fig", "Bold"), tf("lab", "Medium"), tf("res", "Bold")
    pad = 44 if tall else 48
    px0, px1 = sx0, (sx1 if not (pose and not tall) else sx0 + 1000)   # the panel's span; the text column sits inside its padding
    x0, max_w = px0 + pad, (px1 - px0) - 2 * pad
    top = sy0
    strip = None
    if s.get("scenario") and "uses" in s and stage != "result":
        strip, sh = scenario_strip(fmt, s["scenario"], s["uses"]); top = sy0 + sh + 16
    elif s.get("scenario") and "uses" in s:
        _, sh = scenario_strip(fmt, s["scenario"], s["uses"]); top = sy0 + sh + 16
    lh = lambda f: int(f.size * 1.22)
    blocks = [("spaced", s["title"].upper(), f_title, ACCENT, lh(f_title) + 10)]
    if s.get("big"):
        for shrink in (1.0, 0.88, 0.78):   # a long line takes a smaller size rather than a third line
            fb = typeface(fmt, int(T["big"] * shrink), "Bold"); lines = wrap(d, s["big"], fb, max_w)
            if len(lines) <= 2: break
        blocks += [("text", ln, fb, INK, lh(fb)) for ln in lines]; blocks.append(("gap", None, None, None, 18))
    for ln in s.get("lines", []):
        blocks += [("text", w, f_line, MUTED, lh(f_line)) for w in wrap(d, ln, f_line, max_w)]
    if s.get("lines"): blocks.append(("gap", None, None, None, 14))
    if s.get("rows"):   # a definition list: a short key in teal, its explanation beside it, left-aligned and wrapped, one row per fact
        f_key, f_val = typeface(fmt, T["lab"] + 6, "Semibold"), typeface(fmt, T["line"] - 4, "Medium")
        keyw = max(d.textlength(k, font=f_key) for k, _ in s["rows"]) + 30
        for k, v in s["rows"]:
            vl = wrap(d, v, f_val, max_w - keyw)
            blocks.append(("row", (k, vl, keyw, f_key), f_val, MUTED, max(lh(f_key), int(f_val.size * 1.3) * len(vl)) + 16))
        blocks.append(("gap", None, None, None, 6))
    if s.get("figures"):   # operands with a label under each, operators between: every number understood from the screen alone
        for shrink in (1.0, 0.9, 0.8, 0.7):
            ff, fl = typeface(fmt, int(T["fig"] * shrink), "Bold"), typeface(fmt, int(T["lab"] * max(shrink, 0.85)), "Medium")
            items, wsum = [], 0
            for it in s["figures"]:
                if isinstance(it, tuple):
                    wv, wl = d.textlength(it[0], font=ff), d.textlength(it[1], font=fl); items.append(("operand", it, max(wv, wl)))
                else:
                    items.append(("op", it, d.textlength(it, font=ff)))
            wsum = sum(w for _, _, w in items) + 30 * (len(items) - 1)
            if wsum <= max_w: break
        blocks.append(("gap", None, None, None, 10))
        blocks.append(("figures", (items, ff, fl, wsum), None, None, lh(ff) + int(fl.size * 1.35)))
    if s.get("result"):
        for shrink in (1.0, 0.88, 0.78, 0.68):   # a long result takes a smaller size rather than running out of the column
            f_res = typeface(fmt, int(T["res"] * shrink), "Bold")
            if d.textlength("= " + s["result"][0], font=f_res) <= max_w: break
        blocks.append(("gap", None, None, None, 26))
        blocks.append(("result", s["result"], f_res, ACCENT, lh(f_res) + int(f_lab.size * 1.35)))
    if s.get("table"):   # rows of cells in columns, the first row a dim header (Rustam, 2026-10-31: the 20 L/min table, approved)
        rows = s["table"]; gap = 48
        cw = [max(d.textlength(r[i], font=f_foot if k == 0 else f_line) for k, r in enumerate(rows)) for i in range(len(rows[0]))]
        tw = sum(cw) + gap * (len(cw) - 1); tx = x0 + (max_w - tw) // 2 if tall else x0
        xs = [tx + sum(cw[:i]) + gap * i for i in range(len(cw))]
        blocks.append(("gap", None, None, None, 12))
        for k, r in enumerate(rows):
            blocks.append(("table", (r, xs, cw), f_foot if k == 0 else f_line, MUTED if k == 0 else INK, lh(f_foot) + 6 if k == 0 else lh(f_line) + 4))
    if s.get("foot"):
        blocks.append(("gap", None, None, None, 20)); blocks += [("text", w, f_foot, DIM, lh(f_foot)) for w in wrap(d, s["foot"], f_foot, max_w)]
    total = sum(b[4] for b in blocks)
    room = (sy1 - pad) - (top + pad)   # the text block is centred in the safe area, the panel's padding kept inside it; under a strip it
    anchored = s.get("scenario") and "uses" in s   # sits straight below the strip instead, so the step and its example read as one
    if tall:
        y = 120 + CAT_SIZE["short"] + 40 if pose else (top + pad if anchored else top + pad + max(0, (room - total) // 2))
    else:
        y = top + pad if anchored else top + pad + max(0, (room - total) // 2)
    if stage != "result":
        panel(layer, (px0, y - pad, px1 - 1, min(sy1, y + total + pad) - 1))
        if strip is not None: layer.alpha_composite(strip, (sx0, sy0))
    cx = x0 + max_w / 2
    left = (not tall) or bool(s.get("rows"))   # one left axis for a card that explains (title, headline and rows alike); numbers stay centred on the short cut
    for kind, payload, f, fill, h in blocks:
        draw_it = (stage is None) or (stage == "base" and kind != "result") or (stage == "result" and kind == "result")
        if draw_it and kind == "spaced":
            x = x0 if left else cx - (d.textlength(payload, font=f) + 2.6 * len(payload)) / 2
            bm.draw_spaced(d, (x, y), payload, f, fill, 2.6)
        elif draw_it and kind == "text":
            x = x0 if left else cx - d.textlength(payload, font=f) / 2
            d.text((x, y), payload, font=f, fill=fill)
        elif draw_it and kind == "figures":
            items, ff, fl, wsum = payload; x = cx - wsum / 2 if tall else x0
            for which, it, w in items:
                if which == "operand":
                    v, lab = it
                    d.text((x + (w - d.textlength(v, font=ff)) / 2, y), v, font=ff, fill=INK)
                    d.text((x + (w - d.textlength(lab, font=fl)) / 2, y + lh(ff)), lab, font=fl, fill=MUTED)
                else:
                    d.text((x, y), it, font=ff, fill=MUTED)
                x += w + 30
        elif draw_it and kind == "result":
            v, lab = payload; text = "= " + v
            x = cx - d.textlength(text, font=f) / 2 if tall else x0
            d.text((x, y), text, font=f, fill=fill)
            lx = cx - d.textlength(lab, font=f_lab) / 2 if tall else x0 + d.textlength("= ", font=f)
            d.text((lx, y + lh(f)), lab, font=f_lab, fill=MUTED)
        elif draw_it and kind == "row":
            k, vl, keyw, f_key = payload
            d.text((x0, y + 4), k, font=f_key, fill=ACCENT)
            for n, ln in enumerate(vl): d.text((x0 + keyw, y + n * int(f.size * 1.3)), ln, font=f, fill=fill)
        elif draw_it and kind == "table":
            cells, xs, cw = payload
            for i, c in enumerate(cells):
                d.text((xs[i] + (0 if i == 0 else cw[i] - d.textlength(c, font=f)), y), c, font=f, fill=fill)
        y += h
    if pose and stage != "result":
        layer.alpha_composite(cat(CAT_SIZE["short" if tall else "wide"], pose), cat_place(fmt))
    return layer

def dim_layer(fmt, alpha=120):
    return Image.new("RGBA", (fmt["W"], fmt["H"]), (0, 0, 0, alpha))

NAMES = {"dive-log": "Dive log", "turn-pressure": "Turn Pressure"}

BADGE = os.path.join(HERE, "assets", "app-store-badge.png")   # Apple's black badge, as provided (tools/assets/README.md); never altered or tilted
CREDIT = ("Apple and the Apple logo are trademarks of Apple Inc., registered in the U.S. and other countries. "
          "App Store is a service mark of Apple Inc., registered in the U.S. and other countries.")

def outro_layer(fmt, apps):
    """The episode's app(s), the App Store badge, and diver.today as the last and biggest line (Rustam, 2026-10-29: finish with the link to the
    website and the store mark). The badge keeps a clear space of a quarter of its height and stays smaller than the address, as Apple asks;
    the credit line at the foot is the one Apple asks for at the end of a video."""
    W, H = fmt["W"], fmt["H"]; tall = W < H
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    icons = [app_icon(os.path.join(bm.ROOT, SHOTS[a][2]), 170) for a in apps]
    y = 520 if tall else 150
    x = (W - (170 * len(icons) + 48 * (len(icons) - 1))) // 2
    for ic in icons: layer.alpha_composite(ic, (x, y)); x += 170 + 48
    y += 170 + 36
    f_name = font(56, "Semibold"); name = "  ·  ".join(NAMES[a] for a in apps)
    d.text(((W - d.textlength(name, font=f_name)) // 2, y), name, font=f_name, fill=INK); y += 70 + 56
    badge = Image.open(BADGE).convert("RGBA"); bh = 130 if tall else 110; badge = badge.resize((badge.width * bh // badge.height, bh), Image.LANCZOS)
    layer.alpha_composite(badge, ((W - badge.width) // 2, y)); y += bh + 70
    f_url = font(112 if tall else 128, "Bold"); url = "diver.today"
    d.text(((W - d.textlength(url, font=f_url)) // 2, y), url, font=f_url, fill=ACCENT)
    f_credit = font(22, "Regular"); yc = (H - 430) if tall else (H - 72)
    for ln in wrap(d, CREDIT, f_credit, W - 160):
        d.text(((W - d.textlength(ln, font=f_credit)) // 2, yc), ln, font=f_credit, fill=DIM); yc += 28
    return layer

# ---------- assembly ----------
def render_chunk(fmt, segs, name, source, with_bubbles):
    """One run of segments over one background (a footage clip, or the family's blurred loop) → an mp4 with no audio."""
    W, H = fmt["W"], fmt["H"]
    total = sum(s["dur"] for s in segs)
    layers = []   # (path, start, duration, x, y_expr, fades)
    if source != "bg":
        p = os.path.join(WORK, f"{name}-dim.png"); dim_layer(fmt).save(p); layers.append((p, 0, total, 0, "0", False))
    t = 0.0; cat_spans = []
    for i, s in enumerate(segs):
        k = s["kind"]
        if k in ("footage", "card"):
            pose = s.get("cat"); pose = "standing" if pose is True else pose
            if s.get("result"):   # the operands first, the result on the beat
                p = os.path.join(WORK, f"{name}-{i}.png"); card_layer(fmt, s, pose, "base").save(p); layers.append((p, t, s["dur"], 0, "0", True))
                r = s.get("reveal", 0.9)
                p = os.path.join(WORK, f"{name}-{i}-result.png"); card_layer(fmt, s, pose, "result").save(p); layers.append((p, t + r, s["dur"] - r, 0, "0", True))
            else:
                p = os.path.join(WORK, f"{name}-{i}.png"); card_layer(fmt, s, pose).save(p); layers.append((p, t, s["dur"], 0, "0", True))
            if pose: cat_spans.append((t, t + s["dur"], pose))
        elif k == "phone":
            folder, label, _ = SHOTS[s["app"]]
            ph, pad = phone(os.path.join(folder, s["shot"] + ".png"), fmt["phone_h"])
            p = os.path.join(WORK, f"{name}-{i}-phone.png"); ph.save(p)
            px = (W - ph.width) // 2 if W < H else W - 330 - ph.width + pad
            layers.append((p, t, s["dur"], px, f"{fmt['phone_top'] - pad}-{fmt['drift']}*clip((t-{t:.2f})/{s['dur']:.2f},0,1)", True))
            p = os.path.join(WORK, f"{name}-{i}.png"); caption_layer(fmt, label, s["pill"], s["head"], s["sub"], left=True).save(p); layers.append((p, t, s["dur"], 0, "0", True))
        elif k == "outro":
            p = os.path.join(WORK, f"{name}-{i}.png"); outro_layer(fmt, s.get("apps") or list(dict.fromkeys(x["app"] for x in segs if x["kind"] == "phone"))).save(p); layers.append((p, t, s["dur"], 0, "0", True))
        t += s["dur"]
    src = os.path.join(BUILD, "bg.mp4") if source == "bg" else os.path.join(CLIPS, source + ".mp4")
    cmd = ["ffmpeg", "-y", "-v", "error", "-stats", "-stream_loop", "-1", "-i", src]
    fc = [f"[0:v]scale=-2:{H},crop={W}:{H}[bg]" if W < H else f"[0:v]scale={W}:{H}[bg]"]
    for k, (path, st, du, x, yexpr, fades) in enumerate(layers, 1):
        cmd += ["-loop", "1", "-framerate", str(FPS), "-t", f"{du:.2f}", "-i", path]
        f_in = f"fade=t=in:st=0:d={FADE}:alpha=1," if (fades and st > 0) else ""
        f_out = f"fade=t=out:st={max(du - FADE, 0):.2f}:d={FADE}:alpha=1," if fades else ""
        fc.append(f"[{k}:v]format=rgba,{f_in}{f_out}tpad=start_duration={st:.2f}:start_mode=add:color=black@0.0[l{k}]")
    n = len(layers)
    if with_bubbles and cat_spans:
        px, py = cat_place(fmt)
        for pose in dict.fromkeys(ps for _, _, ps in cat_spans):   # one set of bubbles per pose, rising from that drawing's mouth
            mx, my = cat_mouth(CAT_SIZE["short" if W < H else "wide"], pose); mouth = (px + mx - 12, py + my - 10)
            enable = "+".join(f"between(t,{a:.2f},{b:.2f})" for a, b, ps in cat_spans if ps == pose)
            for j, (diam, speed, period, off, amp) in enumerate([(26, 150, 5.3, 0.0, 14), (38, 125, 6.1, 2.1, 20), (18, 175, 4.4, 3.6, 10)]):
                n += 1; p = os.path.join(WORK, f"bubble-{j}.png"); bubble(diam).save(p)
                cmd += ["-loop", "1", "-framerate", str(FPS), "-t", f"{total:.2f}", "-i", p]
                fc.append(f"[{n}:v]format=rgba[l{n}]")
                layers.append((p, 0, total, f"{mouth[0]:.0f}+{amp}*sin(1.7*t+{off})", f"{mouth[1]:.0f}-{speed}*mod(t+{off},{period})", enable))
    prev = "[bg]"
    for k, (path, st, du, x, yexpr, extra) in enumerate(layers, 1):
        en = f":enable='{extra}'" if isinstance(extra, str) else ""
        fc.append(f"{prev}[l{k}]overlay=x='{x}':y='{yexpr}':eof_action=pass:format=auto:eval=frame{en}[o{k}]")
        prev = f"[o{k}]"
    fc.append(f"{prev}format=yuv420p[v]")
    out = os.path.join(WORK, f"{name}.mp4")
    run(cmd + ["-filter_complex", ";".join(fc), "-map", "[v]", "-t", f"{total:.2f}", "-r", str(FPS),
               "-c:v", "libx264", "-preset", "fast", "-crf", "10", "-pix_fmt", "yuv420p", out])   # near-lossless: the final step encodes again
    return out

def build(slug, cut):
    ep, fmt = EPISODES[slug], FMT[cut]; segs = timeline(ep)
    P.clear(); P.update(bm.PALETTES["dark"])
    # chunks: each footage segment alone on its clip; the rest together on the blurred loop
    chunks, group = [], []
    for x in segs:
        if x["kind"] == "footage":
            if group: chunks.append(("bg", group)); group = []
            chunks.append((x["clip"], [x]))
        else:
            group.append(x)
    if group: chunks.append(("bg", group))
    parts = [render_chunk(fmt, g, f"{slug}-{cut}-{i}", src, with_bubbles=True) for i, (src, g) in enumerate(chunks)]
    lst = os.path.join(WORK, f"{slug}-{cut}-video.txt"); open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    video = os.path.join(WORK, f"{slug}-{cut}-video.mp4"); run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", video])
    alst = os.path.join(WORK, f"{slug}-{cut}-audio.txt"); open(alst, "w").write("".join(f"file '{p}'\n" for x in segs for p in x["audio"]))
    audio = os.path.join(WORK, f"{slug}-{cut}-voice.wav"); run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", alst, "-c:a", "pcm_s16le", audio])
    out = os.path.join(WORK, f"{slug}-{cut}.mp4")
    # YouTube re-encodes whatever it gets, and a 1080p upload of a mostly still, dark, blurred picture at CRF 21 came out at
    # 2.3 Mbit/s and looked smeared there (2026-10-31). So: one high-quality encode (CRF 14, slow, aq-mode 3 against banding in the
    # dark water) for Instagram and the page, and a YouTube master upscaled to 1440 on the short side, which YouTube serves with
    # its better VP9 encodes even to 1080p viewers.
    enc = ["-c:v", "libx264", "-preset", "slow", "-crf", "14", "-x264-params", "aq-mode=3", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest"]
    run(["ffmpeg", "-y", "-v", "error", "-i", video, "-i", audio, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000"] + enc + [out])
    yt = "2560:1440" if cut == "wide" else "1440:2560"
    run(["ffmpeg", "-y", "-v", "error", "-i", out, "-vf", f"scale={yt}:flags=lanczos", "-c:a", "copy"] + enc[:10] + ["-movflags", "+faststart", out.replace(".mp4", "-youtube.mp4")])
    total = sum(x["dur"] for x in segs)
    print(f"{slug} {cut}: {total:.1f}s, {len(segs)} segments ->", out)
    if cut == "wide": thumbnail(slug, fmt); captions(slug, segs)

def captions(slug, segs):
    """The spoken sentences with their times, as build/pilot/<slug>.srt, for YouTube's and Instagram's captions (nothing spoken is drawn on screen)."""
    def stamp(t): return f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(round((t % 1) * 1000)):03d}"
    lines, n, t = [], 0, 0.0
    for x in segs:
        for st, en, text in x["subs"]:
            n += 1; lines.append(f"{n}\n{stamp(t + st)} --> {stamp(t + en)}\n{text}\n")
        t += x["dur"]
    open(os.path.join(WORK, f"{slug}.srt"), "w").write("\n".join(lines))

def thumbnail(slug, fmt):
    ep = EPISODES[slug]
    frame = os.path.join(WORK, f"{slug}-thumb-frame.png")
    run(["ffmpeg", "-y", "-v", "error", "-ss", "0.5", "-i", os.path.join(CLIPS, ep["clip"] + ".mp4"), "-frames:v", "1", "-vf", "scale=1280:720", frame])
    im = Image.open(frame).convert("RGBA"); im.alpha_composite(Image.new("RGBA", im.size, (0, 0, 0, 105)))
    d = ImageDraw.Draw(im); f = font(84, "Bold"); f2 = font(30, "Medium")
    lines = wrap(d, ep["question"], f, 780)
    y = (720 - len(lines) * 96) // 2 - 20
    for ln in lines: d.text((70, y), ln, font=f, fill=INK); y += 96
    d.text((72, y + 10), ep["thumb_sub"], font=f2, fill=ACCENT)
    if ep.get("thumb_cat"): im.alpha_composite(cat(440, ep["thumb_cat"]), (820, 150))   # no cat on an episode that has none (sac-rate, 2026-10-31)
    im.convert("RGB").save(os.path.join(WORK, f"{slug}-thumb.png"))

def dump_script(slug):
    ep = EPISODES[slug]
    print(f"# {slug}: {ep['question']}\n\nOn screen (cards) and spoken (voice), in order; the same in both cuts.\n")
    for i, x in enumerate(ep["segments"], 1):
        on = [x.get("title", ""), x.get("big", "")] + x.get("lines", [])
        if x.get("rows"): on += [f"{k}: {v}" for k, v in x["rows"]]
        if x.get("figures"): on.append(" ".join(f"{it[0]} ({it[1]})" if isinstance(it, tuple) else it for it in x["figures"]))
        if x.get("result"): on.append(f"= {x['result'][0]} ({x['result'][1]}), on the beat")
        if x.get("table"): on += [" | ".join(r) for r in x["table"]]
        on.append(x.get("foot", ""))
        if "uses" in x and ep.get("scenario"): on.insert(0, "example dive strip, lit: " + ", ".join(v for k, l, v in ep["scenario"] if x["uses"] == "all" or k in x["uses"]))
        if x.get("hold"): on.append(f"then a pause of {x['hold']} s")
        if x["kind"] == "phone": on = [x["head"], x["sub"]]
        print(f"## {i}. {x['kind']}\n\nOn screen: " + " | ".join(o for o in on if o) + f"\n\nVoice: {x['voice']}\n")

def timing(slug):
    segs = timeline(EPISODES[slug]); total = sum(x["dur"] for x in segs)
    for x in segs: print(f"  {x['dur']:5.1f}s  {x['kind']:8s} {x.get('title', x.get('head', ''))}")
    print(f"{slug}: {total:.1f}s, {sum(len(sentences(x['voice'])) for x in segs)} sentences, {sum(len(x['voice'].split()) for x in segs)} words")

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"; what = sys.argv[2] if len(sys.argv) > 2 else "script"
    slugs = list(EPISODES) if which == "all" else [which]
    if which != "all" and which not in EPISODES: sys.exit("episode: " + " | ".join(EPISODES) + " | all")
    for slug in slugs:
        if what == "script": dump_script(slug)
        elif what == "time": timing(slug)
        elif what in FMT: build(slug, what)
        elif what == "thumb": thumbnail(slug, FMT["wide"])
        elif what == "all": build(slug, "wide"); build(slug, "short")
        else: sys.exit("script | time | wide | short | thumb | all")
