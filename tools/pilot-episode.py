#!/usr/bin/env python3
"""Pilot episode of the question engine (docs/promotion-engine-proposal-2026-10-28.md):
"How do you work out your SAC rate?" told through a cat's dive. Reuses the site generator's phone,
caption and font helpers (tools/build-media.py). Each spoken sentence is synthesised on its own, so its
start time is known and it is drawn as text while it is said (Rustam, 2026-10-28: the voice duplicated
by text; a young US male voice; a cat, simple and unusual).

    python3 tools/pilot-episode.py script          # the words, for the correctness review
    python3 tools/pilot-episode.py wide            # 1920x1080, YouTube
    python3 tools/pilot-episode.py short           # 1080x1920, Short / Reel
Outputs in build/pilot/: sac-rate-<cut>.mp4, sac-rate-thumb.png.
"""
import os, re, sys, hashlib, subprocess, importlib.util
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
VOICE, RATE = "Eddy (English (US))", 168
GAP, PAD, FADE = 0.35, 1.0, 0.5          # between sentences; after a segment's last sentence; layer fades
FMT = {"wide": dict(W=1920, H=1080, phone_h=1210, phone_top=70, drift=80),
       "short": dict(W=1080, H=1920, phone_h=880, phone_top=540, drift=90)}

SEGMENTS = [
 dict(kind="footage", clip="bannerfish-reef", title="The question", big="How do you work out your SAC rate?", lines=["and what is a normal one"],
      voice="Your SAC rate is the one number the rest of your gas planning stands on. Here is how to work it out from a dive you have already done, what a normal one looks like, and a cat to help.",
      short=True, short_voice="How do you work out your SAC rate? A cat and four numbers."),
 dict(kind="footage", clip="dolphins-blue", title="What it is", big="The gas you breathe in a minute, measured at the surface", lines=[],
      voice="SAC stands for surface air consumption. It is the volume of gas you breathe in one minute, corrected to the surface, where the pressure is one atmosphere. Depth multiplies what you use, so taking the depth back out leaves a number that is yours, not the dive's. You can use it to estimate your gas at any depth and from any cylinder."),
 dict(kind="card", cat=True, title="The cat's dive", lines=["A 12-litre cylinder", "200 bar in, 80 bar out", "40 minutes", "Average depth 15 metres, from the computer"],
      foot="A worked example with made-up numbers, not your dive.",
      voice="Meet the cat. The cat has done a dive, and the dive gives us four things. Made-up numbers, not yours. A twelve-litre cylinder. Two hundred bar at the start, eighty at the end. Forty minutes. And an average depth of fifteen metres. The average, not the maximum.", short=True),
 dict(kind="card", cat=True, title="Step one: the gas used", big="120 bar × 12 litres ≈ 1,440 litres", lines=["Bar used times the cylinder's litres is the gas breathed, counted at surface pressure"],
      voice="Step one. The cat used one hundred twenty bar. Times twelve litres, that is about one thousand four hundred forty litres of gas, counted at surface pressure.", short=True),
 dict(kind="card", cat=True, title="Step two: per minute", big="1,440 ÷ 40 = 36 litres a minute", lines=["The gas the cat used each minute, counted as surface gas: down there every breath is denser, so the number comes out bigger"],
      voice="Step two. Divide by the forty minutes: thirty-six litres a minute. That is the gas the cat used each minute, counted as surface gas. Down there every breath is denser, so the number comes out bigger.", short=True),
 dict(kind="card", cat=True, title="Step three: back to the surface", big="36 ÷ 2.5 = 14.4 L/min",
      lines=["15 m ÷ 10 + 1 = 2.5 atmospheres absolute at the average depth", "Divide by it, and the number is the cat's, not the dive's"],
      foot="In cubic feet and psi: each psi is worth the cylinder's rated volume ÷ its rated pressure, and the pressure at depth is feet ÷ 33 + 1.",
      voice="Step three. At fifteen metres the pressure is fifteen over ten, plus one: two and a half atmospheres absolute. Divide by that, and the cat's SAC rate is fourteen point four litres a minute. In cubic feet and psi the idea is the same, with two changes. Each psi is worth the cylinder's rated volume divided by its rated pressure. And the pressure at depth is feet divided by thirty-three, plus one.", short=True),
 dict(kind="card", cat=True, title="The whole formula", big="SAC = bar used × litres ÷ minutes ÷ (average depth in metres ÷ 10 + 1)", lines=[],
      voice="So the whole thing in one line: bar used, times litres, divided by minutes, then divided by the pressure at the average depth: the depth in metres over ten, plus one."),
 dict(kind="card", cat=True, title="What is a normal SAC rate?", lines=["Relaxed and experienced: often 12 to 18 L/min", "New, cold or working hard: more often 20 to 30 L/min", "A current, a task or a fright can double it on the day"],
      foot="A range people see, not a target. Yours changes with how you dive.",
      voice="So what is a normal SAC rate? Relaxed, experienced divers often sit between twelve and eighteen litres a minute. New divers, cold divers and anyone working hard are more often between twenty and thirty. A current, a task or a fright can double it on the day. It is a range people see, not a target, and yours changes with how you dive. That is why one dive is not your SAC rate. A season of dives is.", short=True),
 dict(kind="card", cat=True, title="Two things that go wrong", lines=["Using the maximum depth instead of the average makes the rate come out too low", "Trusting one dive: use several, and plan with a higher rate than your average"],
      foot="Some courses call litres per minute RMV and keep SAC for bar per minute. Here, SAC means litres per minute.",
      voice="Two things go wrong. Using the maximum depth instead of the average divides by too much, and the rate comes out too low. And trusting one dive: use several, and when you plan, plan with a higher rate than your average, because the dive that needs the gas is not the relaxed one. One more thing. Some courses call litres per minute RMV and keep the word SAC for bar per minute from a particular cylinder. Here, SAC means litres per minute, which does not depend on the cylinder."),
 dict(kind="phone", app="dive-log", shot="4-statistics", pill="Free app", head="Your SAC rate per dive, and over time", sub="Imported from your dive computer, drawn over time",
      voice="Or let the logbook do it. Dive log works the SAC rate out for each dive you import from your dive computer and draws it over time, so you can see how it changes from dive to dive.", short=True),
 dict(kind="phone", app="turn-pressure", shot="6-sac-from-dive", pill="Free app", head="Take your SAC rate from a dive into the next plan", sub="Minimum gas and the turn pressure at your depth",
      voice="Turn Pressure takes a SAC rate from a dive you have done and uses it to plan minimum gas and the turn pressure."),
 dict(kind="outro", voice="Both are free on the App Store, and they share one iCloud with the rest of the diver dot today apps. The link is below.",
      short=True, short_voice="Free on the App Store. diver dot today."),
]

# ---------- voice ----------
def sentences(text):
    return [s.strip() for s in re.split(r'(?<=[.?!;])\s+', text.strip()) if s.strip()]

def say(text):
    """One sentence as 48 kHz stereo wav, cached by its text. Returns (path, seconds)."""
    key = hashlib.sha1((VOICE + str(RATE) + text).encode()).hexdigest()[:12]
    wav = os.path.join(WORK, f"s-{key}.wav")
    if not os.path.exists(wav):
        aiff = wav[:-4] + ".aiff"
        subprocess.run(["say", "-v", VOICE, "-r", str(RATE), "-o", aiff, text], check=True)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", aiff, "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", wav], check=True)
        os.remove(aiff)
    d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", wav]).strip())
    return wav, d

def silence(d):
    p = os.path.join(WORK, f"sil-{d:.3f}.wav")
    if not os.path.exists(p):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", f"{d:.3f}", "-c:a", "pcm_s16le", p], check=True)
    return p

def timeline(cut):
    """Segments of this cut with their sentences timed: seg['dur'], seg['subs'] = [(start, end, text)] relative to the segment."""
    segs = [dict(s) for s in SEGMENTS if cut == "wide" or s.get("short")]
    for s in segs:
        text = s.get("short_voice") if cut == "short" and s.get("short_voice") else s["voice"]
        t, subs, audio = 0.6, [], [silence(0.6)]
        for sent in sentences(text):
            wav, d = say(sent)
            subs.append((t, t + d + min(GAP, 0.25), sent)); audio += [wav, silence(GAP)]; t += d + GAP
        audio.append(silence(PAD)); t += PAD
        s["dur"], s["subs"], s["audio"] = t, subs, audio
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

def outro_layer(fmt):
    W, H = fmt["W"], fmt["H"]
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    icons = [app_icon(os.path.join(bm.ROOT, SHOTS[a][2]), 170) for a in ("dive-log", "turn-pressure")]
    cy = H // 2 - 150 if W > H else H // 2 - 330
    layer.alpha_composite(icons[0], (W // 2 - 170 - 24, cy)); layer.alpha_composite(icons[1], (W // 2 + 24, cy))
    f_name, f_line, f_url = font(60, "Semibold"), font(34, "Regular"), font(32, "Medium")
    for text, f, fill, dy in [("Dive log  ·  Turn Pressure", f_name, INK, 220), ("Free on the App Store  ·  one iCloud, five apps", f_line, DIM, 310), ("diver.today", f_url, ACCENT, 380)]:
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
            p = os.path.join(WORK, f"{name}-{i}.png"); outro_layer(fmt).save(p); layers.append((p, t, s["dur"], 0, "0", True))
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

def build(cut):
    fmt = FMT[cut]; segs = timeline(cut)
    P.clear(); P.update(bm.PALETTES["dark"])
    # chunks: each footage segment alone on its clip; the rest together on the blurred loop
    chunks, group = [], []
    for s in segs:
        if s["kind"] == "footage":
            if group: chunks.append(("bg", group)); group = []
            chunks.append((s["clip"], [s]))
        else:
            group.append(s)
    if group: chunks.append(("bg", group))
    parts = [render_chunk(fmt, g, f"{cut}-{i}", src, with_bubbles=True) for i, (src, g) in enumerate(chunks)]
    lst = os.path.join(WORK, f"{cut}-video.txt"); open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    video = os.path.join(WORK, f"{cut}-video.mp4"); run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", video])
    alst = os.path.join(WORK, f"{cut}-audio.txt"); open(alst, "w").write("".join(f"file '{p}'\n" for s in segs for p in s["audio"]))
    audio = os.path.join(WORK, f"{cut}-voice.wav"); run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", alst, "-c:a", "pcm_s16le", audio])
    out = os.path.join(WORK, f"sac-rate-{cut}.mp4")
    run(["ffmpeg", "-y", "-v", "error", "-i", video, "-i", audio, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "-shortest", out])
    total = sum(s["dur"] for s in segs)
    print(f"{cut}: {total:.1f}s, {len(segs)} segments ->", out)
    if cut == "wide": thumbnail(fmt)

def thumbnail(fmt):
    frame = os.path.join(WORK, "thumb-frame.png")
    run(["ffmpeg", "-y", "-v", "error", "-ss", "3", "-i", os.path.join(CLIPS, "bannerfish-reef.mp4"), "-frames:v", "1", "-vf", "scale=1280:720", frame])
    im = Image.open(frame).convert("RGBA"); im.alpha_composite(Image.new("RGBA", im.size, (0, 0, 0, 105)))
    d = ImageDraw.Draw(im); f = font(84, "Bold"); f2 = font(30, "Medium")
    lines = wrap(d, "How do you work out your SAC rate?", f, 780)
    y = (720 - len(lines) * 96) // 2 - 20
    for ln in lines: d.text((70, y), ln, font=f, fill=INK); y += 96
    d.text((72, y + 10), "the formula, a worked example, and what is normal", font=f2, fill=ACCENT)
    im.alpha_composite(cat(360), (880, 190))
    im.convert("RGB").save(os.path.join(WORK, "sac-rate-thumb.png"))

def dump_script():
    print("# Pilot episode: How do you work out your SAC rate?\n\nOn screen (cards) and spoken (voice), in order. S = also in the Short.\n")
    for i, s in enumerate(SEGMENTS, 1):
        on = [s.get("title", ""), s.get("big", "")] + s.get("lines", []) + [s.get("foot", "")]
        if s["kind"] == "phone": on = [s["head"], s["sub"]]
        print(f"## {i}. {s['kind']}{' S' if s.get('short') else ''}\n\nOn screen: " + " | ".join(x for x in on if x) + f"\n\nVoice: {s['voice']}\n")
        if s.get("short_voice"): print(f"Voice in the Short: {s['short_voice']}\n")

if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "script"
    if what == "script": dump_script()
    elif what in FMT: build(what)
    else: sys.exit("script | wide | short")
