#!/usr/bin/env python3
"""The question engine's episodes (docs/promotion-engine-proposal-2026-10-28.md), told through a cat: C × A × T,
consumption times ambient pressure times time, is the gas a dive needs (Rustam, 2026-10-28). Three episodes, each
under a minute so it works as a Reel: `gas-for-the-dive` (the cat), `sac-rate` (the C, from a dive you have done),
`minimum-gas` (the same cat for two divers in a hurry). Reuses the site generator's phone, caption and font helpers
(tools/build-media.py). Each spoken sentence is synthesised on its own, so its start time is known and it is drawn
as text while it is said (Rustam: the voice duplicated by text; a young US male voice; a cat, simple and unusual).

    python3 tools/pilot-episode.py gas-for-the-dive script   # the words, for the correctness review
    python3 tools/pilot-episode.py gas-for-the-dive time     # synthesise the voice and print each cut's length
    python3 tools/pilot-episode.py gas-for-the-dive wide     # 1920x1080, YouTube and the page
    python3 tools/pilot-episode.py gas-for-the-dive short    # 1080x1920, Reel / Short
    python3 tools/pilot-episode.py all all                   # every episode, both cuts
Outputs in build/pilot/: <episode>-<cut>.mp4, <episode>-thumb.png. The same words in both cuts.
"""
import os, re, sys, json, hashlib, subprocess, importlib.util
from PIL import Image, ImageDraw

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
VOICE = os.environ.get("PILOT_VOICE", "kokoro:am_puck")
RATE, SPEED = 168, 1.06          # the macOS rate; Kokoro's speed
KOKORO_PY = os.path.join(bm.ROOT, "build", "kokoro-venv", "bin", "python")
ORPHEUS_PY = os.path.join(bm.ROOT, "build", "orpheus-venv", "bin", "python")   # "orpheus:<leo|dan|zac>", see tools/orpheus-say.py
SPOKEN = [(r"\bSAC\b", "sack"), (r"\bRMV\b", "R.M.V."), (r"\bpsi\b", "P.S.I."), (r"\bEAN\b", "E.A.N.")]   # said, not shown
GAP, PAD, LEAD, FADE = 0.25, 0.6, 0.3, 0.5   # between sentences; after a segment's last sentence; before its first; layer fades
FMT = {"wide": dict(W=1920, H=1080, phone_h=1210, phone_top=70, drift=80),
       "short": dict(W=1080, H=1920, phone_h=880, phone_top=540, drift=90)}

# One entry per episode. Footage clips must show no diver's face (Rustam, 2026-10-21: no pictures of him in a wetsuit; two-divers-facing,
# diver-over-reef and reef-drill-deep are him). Segment kinds: footage (a card over a reef clip), card (over the family's blurred loop; cat=True
# puts the cat beside it), phone (an app screenshot with the site's caption), outro. Every segment is in both cuts.
WORKED = "A worked example with made-up numbers, not your dive."
# Every episode is a story in Rustam's order (2026-10-28): the problem the diver has, then the definitions, then one worked example, then
# the practical wrap-up (into bar, by the cylinder). Never facts before the context is set.
# The voice is the story and is written first, as one person talking to another: whole sentences, each following from the one before,
# every number arriving inside a sentence that says what it is and why it is needed. A card carries only a title and the figure the voice
# is reaching; the spoken sentence itself is shown by the subtitle. "Cat" is said as the word; the letters are spoken only when each is
# defined. Nothing is rendered before Rustam has read the words (his 2026-10-28 verdict on the first takes: word salad, no narrative).
EPISODES = {
 "gas-for-the-dive": dict(
  question="How much gas does a dive need?", thumb_sub="remember a cat: C × A × T", clip="turtle-slope",
  segments=[
   dict(kind="footage", clip="turtle-slope", title="The question", big="How much gas does your dive need?",
        voice="You are planning a dive, say forty minutes at around twenty metres. Will the gas on your back cover it?"),
   dict(kind="card", cat=True, title="The cat", big="C × A × T",
        voice="Divers work that out with a cat."),
   dict(kind="card", cat=True, title="C is consumption", big="Your SAC rate: 15 litres a minute", foot=WORKED,
        voice="C is your consumption, your SAC rate: what you breathe in a minute at the surface. Say fifteen litres a minute."),
   dict(kind="card", cat=True, title="A is the average pressure", big="20 m: 1 + 2 = 3 bar",
        voice="A is the pressure at your average depth: one bar at the surface, plus one for every ten metres. Twenty metres: three bar."),
   dict(kind="card", cat=True, title="T is time", big="40 minutes",
        voice="T is the time of the dive: forty minutes."),
   dict(kind="card", cat=True, title="Multiply", big="15 × 3 × 40 = 1,800 litres",
        voice="Fifteen, times three, times forty: eighteen hundred litres."),
   dict(kind="card", cat=True, title="Into bar", big="1,800 L ÷ 12 L = 150 bar",
        voice="Your gauge reads bar, so divide by the size of your cylinder. Twelve litres: a hundred and fifty bar."),
   dict(kind="card", cat=True, title="Plus minimum gas", big="150 bar for the dive, then your minimum gas",
        voice="That is the dive. Your minimum gas comes on top."),
   dict(kind="phone", app="turn-pressure", shot="1-inputs", pill="Free app", head="Turn Pressure works out both for the dive you are planning", sub="The gas for the dive, and the minimum gas to keep",
        voice="Turn Pressure works out both for your dive."),
   dict(kind="outro", voice="Free on the App Store. diver dot today."),
  ]),
 "sac-rate": dict(
  question="What is your SAC rate?", thumb_sub="the C in C × A × T, from a dive you have done", clip="dolphins-blue",
  segments=[
   dict(kind="footage", clip="dolphins-blue", title="The question", big="What is your SAC rate?",
        voice="Every gas plan starts with your SAC rate: what you breathe in a minute, at the surface. You get it from a dive you have done."),
   dict(kind="card", cat=True, title="Three things from that dive", big="120 bar used, from a 12-litre cylinder", foot=WORKED,
        voice="Three things from that dive. The gas you used: say a hundred and twenty bar, from a twelve-litre cylinder."),
   dict(kind="card", cat=True, title="Three things from that dive", big="40 minutes · average depth 14 m",
        voice="How long: forty minutes. And the average depth your computer recorded: fourteen metres."),
   dict(kind="card", cat=True, title="Litres a minute, at depth", big="120 × 12 = 1,440 L ÷ 40 min = 36 L/min",
        voice="A hundred and twenty bar times twelve litres: fourteen hundred and forty litres. Over forty minutes, thirty-six litres a minute."),
   dict(kind="card", cat=True, title="Back to the surface", big="14 ÷ 10 + 1 = 2.4 bar · 36 ÷ 2.4 = 15",
        voice="At fourteen metres the pressure was two point four bar, so you breathed two point four times the gas. Divide by two point four, and your SAC rate is fifteen litres a minute."),
   dict(kind="card", cat=True, title="Make it yours", big="A few dives, averaged",
        voice="Do it for a few dives and use the average."),
   dict(kind="phone", app="dive-log", shot="4-statistics", pill="Free app", head="Dive log works it out from each dive's profile and pressures", sub="And draws it over time",
        voice="Dive log works it out from each dive's profile and pressures."),
   dict(kind="outro", voice="Free on the App Store. diver dot today."),
  ]),
 "minimum-gas": dict(
  question="What is minimum gas?", thumb_sub="the same cat, for two divers on the way up", clip="reef-slope",
  segments=[
   dict(kind="footage", clip="reef-slope", title="The question", big="What is minimum gas?",
        voice="At the deepest point your buddy signals: out of gas. You share, and you both go up. How much must be left for that? That is minimum gas."),
   dict(kind="card", cat=True, title="The cat, for two", big="C × A × T, for the way up",
        voice="Work it out with the cat: consumption times pressure times time, for two on the way up."),
   dict(kind="card", cat=True, title="C is consumption, for two", big="20 + 20 = 40 litres a minute", foot="A worked example. Courses differ on the rate for a stressed diver.",
        voice="C: two stressed divers, say twenty litres a minute each. Forty together."),
   dict(kind="card", cat=True, title="A minute to sort it out", big="40 × 4 bar × 1 min = 160 litres", lines=["30 m: 30 ÷ 10 + 1 = 4 bar"],
        voice="A minute at thirty metres to sort it out. Thirty metres is four bar: a hundred and sixty litres."),
   dict(kind="card", cat=True, title="The ascent", big="40 × 2.5 bar × 3.3 min ≈ 330 litres", lines=["30 m at 9 m/min = 3.3 min · (4 + 1) ÷ 2 = 2.5 bar"],
        voice="Then the ascent at nine metres a minute: three point three minutes at two and a half bar on average, three hundred and thirty litres."),
   dict(kind="card", cat=True, title="Together", big="≈ 490 L ÷ 11 L = 45 bar", foot="The cat's example, not a minimum gas for your dive.",
        voice="Nearly five hundred litres: from an eleven-litre cylinder, forty-five bar."),
   dict(kind="card", cat=True, title="The rule", big="At minimum gas, the dive is over",
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

def wav_path(text):
    return os.path.join(WORK, "s-" + hashlib.sha1((VOICE + str(RATE) + str(SPEED) + text).encode()).hexdigest()[:12] + ".wav")

def synthesise(texts):
    """Every sentence not yet on disk, as 48 kHz stereo wav, in one go (Kokoro loads once)."""
    todo = [t for t in dict.fromkeys(texts) if not os.path.exists(wav_path(t))]
    if not todo: return
    engine, _, name = VOICE.partition(":")
    raws = []
    if engine == "kokoro":
        jobs = [[spoken(t), wav_path(t)[:-4] + ".raw.wav"] for t in todo]
        jp = os.path.join(WORK, "jobs.json"); json.dump(jobs, open(jp, "w"))
        subprocess.run([KOKORO_PY, os.path.join(HERE, "kokoro-say.py"), jp, name, str(SPEED)], check=True, stdout=subprocess.DEVNULL)
        raws = [r for _, r in jobs]
    elif engine == "orpheus":
        jobs = [[spoken(t), wav_path(t)[:-4] + ".raw.wav"] for t in todo]
        jp = os.path.join(WORK, "jobs.json"); json.dump(jobs, open(jp, "w"))
        subprocess.run([ORPHEUS_PY, os.path.join(HERE, "orpheus-say.py"), jp, name], check=True, stdout=subprocess.DEVNULL)
        raws = [r for _, r in jobs]
    else:
        for t in todo:
            r = wav_path(t)[:-4] + ".aiff"; raws.append(r)
            subprocess.run(["say", "-v", name, "-r", str(RATE), "-o", r, spoken(t)], check=True)
    for t, r in zip(todo, raws):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", r, "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", wav_path(t)], check=True)
        os.remove(r)

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

def timeline(ep):
    """The episode's segments with their sentences timed: seg['dur'], seg['subs'] = [(start, end, text)] relative to the segment."""
    segs = [dict(x) for x in ep["segments"]]
    synthesise([sent for x in segs for sent in sentences(x["voice"])])
    for x in segs:
        t, subs, audio = LEAD, [], [silence(LEAD)]
        for sent in sentences(x["voice"]):
            wav, d = say(sent)
            subs.append((t, t + d + min(GAP, 0.25), sent)); audio += [wav, silence(GAP)]; t += d + GAP
        audio.append(silence(PAD)); t += PAD
        x["dur"], x["subs"], x["audio"] = t, subs, audio
    return segs

# ---------- drawing ----------
INK, DIM, DARK = (240, 243, 245), (168, 178, 186), (16, 22, 28)

def cat(size):
    """A diving cat in line art: round head, ears, a mask over the eyes, a cylinder on its back, a hose to its mouth."""
    s = size; im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    lw = max(4, s // 70)
    cx, cy, r = s * 0.46, s * 0.46, s * 0.26
    # cylinder behind the body, leaning
    d.rounded_rectangle((s*0.64, s*0.50, s*0.80, s*0.96), radius=s*0.07, fill=ACCENT)
    d.rounded_rectangle((s*0.69, s*0.44, s*0.75, s*0.52), radius=s*0.02, fill=INK)        # valve
    # body
    d.ellipse((s*0.22, s*0.60, s*0.72, s*0.98), fill=DARK, outline=INK, width=lw)
    # tail
    d.arc((s*0.60, s*0.72, s*0.98, s*1.06), 200, 330, fill=INK, width=lw)
    # ears
    for sx in (-1, 1):
        ex = cx + sx * r * 0.62
        d.polygon([(ex - r*0.30, cy - r*0.55), (ex + r*0.30, cy - r*0.55), (ex + sx*r*0.12, cy - r*1.28)], fill=DARK, outline=INK)
        d.line([(ex - r*0.30, cy - r*0.55), (ex + sx*r*0.12, cy - r*1.28), (ex + r*0.30, cy - r*0.55)], fill=INK, width=lw, joint="curve")
    # head
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=DARK, outline=INK, width=lw)
    # mask: one rounded window over both eyes, teal rim
    d.rounded_rectangle((cx - r*0.80, cy - r*0.52, cx + r*0.80, cy + r*0.10), radius=r*0.28, fill=(40, 70, 80), outline=ACCENT, width=lw)
    d.line([(cx + r*0.80, cy - r*0.22), (cx + r*1.02, cy - r*0.26)], fill=ACCENT, width=lw)   # strap
    d.line([(cx - r*0.80, cy - r*0.22), (cx - r*1.02, cy - r*0.26)], fill=ACCENT, width=lw)
    for sx in (-1, 1):   # eyes with slit pupils
        ex = cx + sx * r * 0.38; ey = cy - r * 0.21
        d.ellipse((ex - r*0.17, ey - r*0.15, ex + r*0.17, ey + r*0.15), fill=INK)
        d.ellipse((ex - r*0.05, ey - r*0.13, ex + r*0.05, ey + r*0.13), fill=DARK)
    # nose and mouth, whiskers
    d.polygon([(cx - r*0.08, cy + r*0.30), (cx + r*0.08, cy + r*0.30), (cx, cy + r*0.40)], fill=ACCENT)
    for sx in (-1, 1):
        for k, dy in enumerate((-0.04, 0.08, 0.20)):
            d.line([(cx + sx*r*0.30, cy + r*(0.36 + dy*0.5)), (cx + sx*r*1.05, cy + r*(0.30 + dy))], fill=INK, width=max(2, lw-2))
    # regulator in the mouth, hose to the cylinder
    d.rounded_rectangle((cx - r*0.22, cy + r*0.48, cx + r*0.22, cy + r*0.72), radius=r*0.08, fill=INK)
    d.arc((cx + r*0.1, cy + r*0.45, s*0.78, s*0.72), 270, 360, fill=INK, width=lw)
    d.line([(s*0.72, s*0.52), (s*0.72, s*0.60)], fill=INK, width=lw)
    return im

def bubble(diam):
    im = Image.new("RGBA", (diam + 6, diam + 6), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((3, 3, diam + 3, diam + 3), outline=(240, 243, 245, 210), width=max(2, diam // 10), fill=(255, 255, 255, 40))
    d.ellipse((3 + diam*0.22, 3 + diam*0.18, 3 + diam*0.42, 3 + diam*0.34), fill=(255, 255, 255, 170))
    return im

def card_layer(fmt, s, with_cat):
    """A card: a small spaced title in teal, an optional big line, lines, a footnote; the cat beside (wide) or above (short)."""
    W, H = fmt["W"], fmt["H"]; tall = W < H
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    if tall:
        x0, max_w = 70, W - 140
        f_title, f_big, f_line, f_foot = font(28, "Semibold"), font(64, "Bold"), font(44, "Medium"), font(30, "Regular")
        lh_big, lh_line, lh_foot = 76, 58, 40
    else:
        x0, max_w = 160, (1120 if with_cat else 1500)
        f_title, f_big, f_line, f_foot = font(28, "Semibold"), font(70, "Bold"), font(44, "Medium"), font(30, "Regular")
        lh_big, lh_line, lh_foot = 84, 58, 40
    blocks = [(s["title"].upper(), f_title, ACCENT, 50, True)]
    if s.get("big"):
        blocks += [(ln, f_big, INK, lh_big, False) for ln in wrap(d, s["big"], f_big, max_w)]; blocks.append(("", None, None, 22, False))
    for ln in s.get("lines", []):
        blocks += [(w, f_line, INK, lh_line, False) for w in wrap(d, ln, f_line, max_w)]; blocks.append(("", None, None, 16, False))
    if s.get("foot"):
        blocks.append(("", None, None, 20, False)); blocks += [(w, f_foot, DIM, lh_foot, False) for w in wrap(d, s["foot"], f_foot, max_w)]
    total = sum(b[3] for b in blocks)
    if tall:
        y = 640 if with_cat else (H - 420 - total) // 2
    else:
        y = (H - 130 - total) // 2
    for text, f, fill, lh, spaced in blocks:
        if text:
            x = (W - d.textlength(text, font=f)) // 2 if tall else x0
            if spaced:
                bm.draw_spaced(d, (x - 6, y), text, f, fill, 2.2)
            else:
                d.text((x, y), text, font=f, fill=fill)
        y += lh
    if with_cat:
        c = cat(500 if not tall else 400)
        pos = ((W - c.width) // 2, 160) if tall else (W - c.width - 150, (H - 130 - c.height) // 2)
        layer.alpha_composite(c, pos)
    return layer

def dim_layer(fmt, alpha=120):
    return Image.new("RGBA", (fmt["W"], fmt["H"]), (0, 0, 0, alpha))

def sub_layer(fmt, text, under_phone_left):
    """One spoken sentence, as text in a dark rounded box at the foot of the frame."""
    W, H = fmt["W"], fmt["H"]; tall = W < H
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    f = font(40 if tall else 38, "Medium"); lh = 50 if tall else 48
    max_w = 900 if tall else (800 if under_phone_left else 1400)
    lines = wrap(d, text, f, max_w)
    tw = max(d.textlength(l, font=f) for l in lines); bh = len(lines) * lh + 30
    if tall:
        x0 = (W - tw) // 2 - 26; y0 = H - 300 - bh
    elif under_phone_left:
        x0 = 150 - 26; y0 = H - 70 - bh
    else:
        x0 = (W - tw) // 2 - 26; y0 = H - 70 - bh
    d.rounded_rectangle((x0, y0, x0 + tw + 52, y0 + bh), radius=18, fill=(8, 12, 16, 170))
    y = y0 + 14
    for l in lines:
        x = x0 + 26 if (under_phone_left and not tall) else x0 + 26 + (tw - d.textlength(l, font=f)) // 2
        d.text((x, y), l, font=f, fill=INK); y += lh
    return layer

NAMES = {"dive-log": "Dive log", "turn-pressure": "Turn Pressure"}

def outro_layer(fmt, apps):
    """The episode's app(s), free, diver.today: the apps are those its phone segments showed, in order."""
    W, H = fmt["W"], fmt["H"]
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    icons = [app_icon(os.path.join(bm.ROOT, SHOTS[a][2]), 170) for a in apps]
    cy = H // 2 - 150 if W > H else H // 2 - 330
    x = (W - (170 * len(icons) + 48 * (len(icons) - 1))) // 2
    for ic in icons: layer.alpha_composite(ic, (x, cy)); x += 170 + 48
    f_name, f_line, f_url = font(60, "Semibold"), font(34, "Regular"), font(32, "Medium")
    for text, f, fill, dy in [("  ·  ".join(NAMES[a] for a in apps), f_name, INK, 220), ("Free on the App Store  ·  one iCloud, five apps", f_line, DIM, 310), ("diver.today", f_url, ACCENT, 380)]:
        d.text(((W - d.textlength(text, font=f)) // 2, cy + dy), text, font=f, fill=fill)
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
            p = os.path.join(WORK, f"{name}-{i}.png"); card_layer(fmt, s, s.get("cat", False)).save(p); layers.append((p, t, s["dur"], 0, "0", True))
            if s.get("cat"): cat_spans.append((t, t + s["dur"]))
        elif k == "phone":
            folder, label, _ = SHOTS[s["app"]]
            ph, pad = phone(os.path.join(folder, s["shot"] + ".png"), fmt["phone_h"])
            p = os.path.join(WORK, f"{name}-{i}-phone.png"); ph.save(p)
            px = (W - ph.width) // 2 if W < H else W - 330 - ph.width + pad
            layers.append((p, t, s["dur"], px, f"{fmt['phone_top'] - pad}-{fmt['drift']}*clip((t-{t:.2f})/{s['dur']:.2f},0,1)", True))
            p = os.path.join(WORK, f"{name}-{i}.png"); caption_layer(fmt, label, s["pill"], s["head"], s["sub"], left=True).save(p); layers.append((p, t, s["dur"], 0, "0", True))
        elif k == "outro":
            p = os.path.join(WORK, f"{name}-{i}.png"); outro_layer(fmt, s.get("apps") or list(dict.fromkeys(x["app"] for x in segs if x["kind"] == "phone"))).save(p); layers.append((p, t, s["dur"], 0, "0", True))
        for j, (st, en, text) in enumerate(s["subs"]):
            p = os.path.join(WORK, f"{name}-{i}-sub{j}.png"); sub_layer(fmt, text, k == "phone").save(p)
            layers.append((p, t + st, en - st, 0, "0", True))
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
        tall = W < H
        mouth = ((W // 2 - 30, 160 + 400 * 0.66) if tall else (W - 150 - 500 + 500 * 0.46 - 20, (H - 130 - 500) // 2 + 500 * 0.62))
        enable = "+".join(f"between(t,{a:.2f},{b:.2f})" for a, b in cat_spans)
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
               "-c:v", "libx264", "-preset", "fast", "-crf", "16", "-pix_fmt", "yuv420p", out])
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
    run(["ffmpeg", "-y", "-v", "error", "-i", video, "-i", audio, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000", "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "-shortest", out])
    total = sum(x["dur"] for x in segs)
    print(f"{slug} {cut}: {total:.1f}s, {len(segs)} segments ->", out)
    if cut == "wide": thumbnail(slug, fmt)

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
    im.alpha_composite(cat(360), (880, 190))
    im.convert("RGB").save(os.path.join(WORK, f"{slug}-thumb.png"))

def dump_script(slug):
    ep = EPISODES[slug]
    print(f"# {slug}: {ep['question']}\n\nOn screen (cards) and spoken (voice), in order; the same in both cuts.\n")
    for i, x in enumerate(ep["segments"], 1):
        on = [x.get("title", ""), x.get("big", "")] + x.get("lines", []) + [x.get("foot", "")]
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
