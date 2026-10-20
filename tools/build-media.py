#!/usr/bin/env python3
"""Builds every piece of media on diver.today from the app repositories beside this one.

    python3 tools/build-media.py bg        # the shared blurred-reef background clip (once)
    python3 tools/build-media.py icons     # img/<slug>.png (512), favicon, og.png
    python3 tools/build-media.py videos [slug ...]   # video/<slug>-wide.mp4 (16:9), -tall.mp4 (4:5), img/<slug>-{wide,tall}-poster.jpg
    python3 tools/build-media.py all

Sources are the screenshots each app's ship tooling already captures for the App Store, with
their approved captions, and the icon in each app's asset catalogue. Nothing here is edited by
hand: change the table below, rerun, commit the outputs.
"""
import glob, os, sys, subprocess, math, shutil, glob
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECTS = os.path.dirname(ROOT)
BUILD = os.path.join(ROOT, "build")
VIDEO = os.path.join(ROOT, "video")
IMG = os.path.join(ROOT, "img")
FPS = 30
# "wide" is the page on a desktop, "tall" (4:5) is the page on a phone; the same scenes, laid out for each.
FORMATS = {
    "wide": dict(W=1920, H=1080, phone_h=1210, phone_top=70, drift=80, out_h=1080),
    "tall": dict(W=1080, H=1350, phone_h=1180, phone_top=500, drift=110, out_h=1080),
}

SF = "/System/Library/Fonts/SFNS.ttf"
def font(size, weight="Regular"):
    f = ImageFont.truetype(SF, size)
    f.set_variation_by_name(weight)
    return f

ACCENT = (79, 209, 197)      # one teal for the whole family
INK = (240, 243, 245)
DIM = (168, 178, 186)
# A video is dark (the family's look) or light (`theme="light"`: the dive-professional cut, so its section
# of the page can be bright). The palette in force while a video is built:
PALETTES = {"dark": dict(ink=(240, 243, 245), dim=(168, 178, 186), bg="bg.mp4"),
            "light": dict(ink=(14, 22, 28), dim=(74, 88, 96), bg="bg-light.mp4")}
P = dict(PALETTES["dark"])

# What stays put while a page scrolls, in points down a 956-point screen: Dive log's status bar, button
# strip and tab bar; or only a status bar. See stitch().
DIVE_LOG_CHROME = dict(top=118, fade=40, bottom=120, tab=872)
# Time to Surface's page scrolls straight under the status bar, so only the bar's glyphs (time, signal,
# battery, the island) are kept and laid over the scrolled page, the way the phone draws them.
STATUS_BAR_CHROME = dict(top=56, fade=0, bottom=0, tab=None, glyphs=True)

APPS = [
    # The journey (2026-10-20, Rustam: the whole plan end to end, "a connected story"): the swim to the
    # drop-off, two deep segments, the deco, the profile, the runtime, the gas, then the plan sent. The
    # shots are the site's own set, taken on the 1.8 build in review by `-scrollY` and the screenshot
    # sections (turn_pressure, branch site-shots). 18/45 on the back, not 21/35: at 51 m the app refuses
    # 21/35 (1.28 bar of oxygen, past the 1.2 working limit), and 18/45 is its own gas for that depth.
    dict(slug="time-to-surface", name="Time to Surface", tagline="Decompression planner for technical divers",
         icon=f"{PROJECTS}/turn_pressure/Apps/TimeToSurface/Resources/Assets.xcassets/AppIcon.appiconset/icon-1024.png",
         shots=f"{PROJECTS}/turn_pressure/design/screenshots/time-to-surface-site", chrome=STATUS_BAR_CHROME,
         journey=[
            dict(shot="a1-swim", pill="The Canyon, Dahab", head="Let's plan the Canyon",
                 sub="First a 15-minute swim at 10 m across the plateau to the drop-off, on back gas.", hold=4.6),
            dict(shot="a2-second", pill="Down the Canyon", head="45 m for 10 minutes, then 51 m for 4",
                 sub="Down the Canyon, then a look at its floor. 18/45 on the back, EAN50 for the way up.", hold=4.4),
            dict(page="a3-page", at=2472, pill="The answer", head="58 minutes, 19 of them in deco",
                 sub="First stop at 24 m, CNS 27 %: Bühlmann ZH-L16C with your gradient factors, 20/85 here."),
            dict(page="a3-page", at=3022, pill="The profile", head="The dive, drawn",
                 sub="The swim, the drop, the floor, the switch to EAN50 at 21 m, every stop."),
            dict(page="a3-page", at=3246, to=3720, pill="Minute by minute", head="The runtime, stop by stop",
                 sub="Where each stop begins and ends, and what to do there.", hold=5.2),
            dict(page="a3-page", at=4178, pill="The gas", head="190 bar of 18/45, 140 bar of EAN50",
                 sub="Minimum gas at 45 and 51 m, the pressure to switch on, and what five minutes more cost."),
            dict(shot="a9-send", pill="The team", head="Name the team, send it for signatures",
                 sub="Tom Becker leads; Aisha, Luca and Emma dive with him."),
            dict(shot="a10-picture", pill="One page", head="The whole plan, signed by all four",
                 sub="A picture or a PDF, for the team and for the dive centre.", hold=4.8),
         ]),
    # The second proposition of the same app (Rustam, 2026-10-20): a dive professional's brand, the
    # signed plan, the page for the dive centre, and four sample brands. Same icon; not an app of its own,
    # so no icon or og entry (`second=True`).
    dict(slug="time-to-surface-pro", name="Time to Surface", tagline="Signed team dive plans, in your brand",
         outro="For dive leads, instructors and dive centres", second=True, theme="light",
         icon=f"{PROJECTS}/turn_pressure/Apps/TimeToSurface/Resources/Assets.xcassets/AppIcon.appiconset/icon-1024.png",
         shots=f"{PROJECTS}/turn_pressure/design/screenshots/time-to-surface-site", chrome=STATUS_BAR_CHROME,
         journey=[
            dict(gallery=["b1-red-plan", "b1-yellow-plan", "b1-black-plan"], pill="Your app",
                 head="Time to Surface in your dive centre's look", sub="Your logo, your picture, your colour. Three dive centres, one app.", hold=5.0),
            dict(shot="b2-red-settings", pill="Your brand", head="Set it once, in Settings",
                 sub="Logo, pictures, colour, name and two lines. On the app and on every page it sends."),
            dict(shot="b3-yellow-send", pill="The team", head="Plan the dive, name the team",
                 sub="Tom Becker leads; Aisha, Luca and Emma dive with him. Send it for signatures."),
            dict(shot="b4-black-signing", pill="Signatures", head="Each diver signs on the phone",
                 sub="The plan in front of them, their signature under one line: we have reviewed this plan as a team and agree to dive it."),
            dict(shot="b5-red-team", pill="The round", head="Who has signed, who has not",
                 sub="Pick the round up later. A signature belongs to its person."),
            dict(shot="b6-yellow-document", pill="The page", head="One page the dive centre checks and keeps",
                 sub="Your logo on top, the schedule, the gases, the gas plan, four signatures. A picture or an A4 PDF.", hold=4.8),
            dict(gallery=["b6-red-document", "b6-yellow-document", "b6-black-document"],
                 pill="Your forms", head="The same plan, three brands", sub="Every page you send carries your name.", hold=4.6),
         ]),
    # A journey since 2026-10-21 (Rustam: "show both iOS and Mac applications, use nice pictures"): the iPhone
    # shots are the site set `design/screenshots/surface-interval-site/` in the app's repo and the Mac
    # windows are `design/screenshots/site/` in surface_interval_desktop, both on four Pexels clips
    # (`reference-footage/pexels/SOURCES.md`), none of his own footage.
    dict(slug="surface-interval", name="Surface Interval", tagline="Dive video colour and reels, on iPhone and Mac",
         icon=f"{PROJECTS}/surface_interval/App/Resources/Assets.xcassets/AppIcon.appiconset/icon-1024.png",
         shots=f"{PROJECTS}/surface_interval/design/screenshots/surface-interval-site", chrome=STATUS_BAR_CHROME,
         journey=[
            dict(shot="1-home", pill="Your dives", head="Every dive in its own folder",
                 sub="Add the videos of a dive; the folder is named for the day, rename it to the site.", hold=4.4),
            dict(shot="2-folder", pill="One button", head="One button makes the reel",
                 sub="Of the whole dive, or of the videos you pick."),
            dict(shot="3-making", pill="Best moments", head="The best moments are chosen for you",
                 sub="Every video is read, the moments worth keeping found, the colour measured: shallow, mid, deep or night.", hold=4.6),
            dict(shot="4-reel-ready", pill="The reel", head="A reel that carries the best of the dive",
                 sub="The moments trimmed and put in order, colour restored, music under them. Nothing to edit.", hold=4.8),
            dict(shot=f"{PROJECTS}/surface_interval_desktop/design/screenshots/site/1-home", pill="On the Mac",
                 head="The same app on your Mac", sub="The same folders, the same reels, the same colour engine, on the big screen.", hold=4.6),
            dict(shot=f"{PROJECTS}/surface_interval_desktop/design/screenshots/site/3-reel", pill="Reels",
                 head="Reels made on the Mac", sub="From the dive's folder, 4K if you want it, ready to save or post.", hold=4.6),
            dict(shot=f"{PROJECTS}/surface_interval_desktop/design/screenshots/site/4-play", pill="Colour",
                 head="Colour by Surface Interval", sub="The reef as you saw it, not as the water left it.", hold=4.6),
         ]),
    # The journey (2026-10-20): his six key features in his 2026-10-17 order, then tags and buddies, search,
    # and "make it yours" — four fictional divers' brands (name, picture, colour) on the app and on the card.
    # The shots are the site's own set (`scripts/site-screenshots.sh` and the site-shots branch's seeds in
    # the app's repo): his Blue Hole dive 273 on 18/45 and a year of sample trips.
    dict(slug="dive-log", name="Dive log", tagline="Shearwater dive import for iPhone",
         icon=f"{PROJECTS}/sharewater_dive_log/App/Resources/Assets.xcassets/AppIcon.appiconset/AppIcon.png",
         shots=f"{PROJECTS}/sharewater_dive_log/design/screenshots/dive-log-site", chrome=DIVE_LOG_CHROME,
         journey=[
            dict(shot="3-computers", pill="Import", head="Import once, from any computer",
                 sub="Bluetooth or Shearwater Cloud. A dive your backup computer logged too merges on its own.", hold=4.2),
            dict(shot="2-log", pill="The log", head="Year, month, week, dive",
                 sub="Super fast navigation: the month's dives, its hours, its top sites."),
            dict(page="1-dive-page", at=0, to=1300, pill="The dive", head="The whole dive on one page",
                 sub="Profile, stops, every gas with its pressure and rate, as your computer logged it.", hold=6.4),
            dict(shot="8-tags", pill="Tags and buddies", head="Tag it, name your buddies",
                 sub="#deep #trimix #wall, with Lena and Anna. A rig from Weights Check, if you use it."),
            dict(shot="7-search", pill="Search", head="Find it again",
                 sub="By site, place, buddy, tag, note or dive number."),
            dict(shot="4-statistics", pill="Statistics", head="Your SAC, dive by dive and over time",
                 sub="Surface consumption rate on bottom and deco gas, depth bands, deco and trimix dives."),
            dict(shot="5-map", pill="Sites", head="Every site you dived, on one map",
                 sub="9,000 known dive sites to pick from, nearest first."),
            dict(shot="6-card", pill="Share", head="A card of your dive, for social media",
                 sub="Picture or video, story-sized, every word kept in a feed post."),
            dict(shot=["me-1-log", "me-2-log", "me-3-log", "me-4-log"], pill="Yours", head="Make it yours",
                 sub="Your name, your picture, your colour, on the app. Aiko's orange, Lucas's blue, Nadia's green, Marco's purple.", hold=7.6),
            dict(gallery=["me-1-card-picture", "me-2-card-picture", "me-3-card-picture", "me-4-card-picture"],
                 pill="Yours", head="And on every card you share", sub="Your picture and your name, in your colour. No app name, no store link.", hold=4.8),
         ]),
    dict(slug="turn-pressure", name="Turn Pressure", tagline="Recreational dive planner for iPhone",
         icon=f"{PROJECTS}/turn_pressure/App/Resources/Assets.xcassets/AppIcon.appiconset/icon-1024.png",
         shots=f"{PROJECTS}/turn_pressure/design/screenshots/turn-pressure",
         scenes=[
            ("1-inputs", "The dive", "Depth, gas and cylinder", "Depth and your minutes at it on sliders — no keyboard on a rocking boat."),
            ("2-plan-ndl", "Turn pressure", "Turn pressure, before you kit up", "The number a flat 50 bar cannot give you."),
            ("5-plan-two-level", "Minimum gas", "Minimum gas for each level", "What to leave 30 m with, what to leave 18 m with, and from 9 m up."),
            ("6-sac-from-dive", "Your SAC", "Your breathing rate, out of a dive you did", "Depths, minutes and two gauge readings — it works the rest out."),
            ("7-profile", "The profile", "The dive you chose, drawn", "Each level with its minutes and the gauge you leave it on."),
            ("8-repetitive", "Repeat dives", "It asks what you already dived", "Because a long shallow dive is what carries nitrogen into the next one."),
         ]),
    dict(slug="weights-check", name="Weights Check", tagline="Your rig, your lead, your water",
         icon=f"{PROJECTS}/weights_check/App/Assets.xcassets/AppIcon.appiconset/icon-1024.png",
         shots=f"{PROJECTS}/weights_check/design/screenshots/weights-check",
         scenes=[
            ("1-balance", "Balance", "Your rig at depth, drawn", "The load to carry if the wing fails, and what is left to hold the stop."),
            ("2-library", "Library", "Every rig you dive, kept", "The one you have checked leads; the ones you are still planning sit under it."),
            ("3-check", "The check", "Record the check you actually did", "What you wore, the water it happened in, and the lead that came out of it."),
            ("4-starting-weight", "First dive", "A rig you have never checked", "A range of lead to bring, narrowed by the first check you record."),
            ("5-gear", "Gear", "Enter your gear once", "Cylinders, suits, regulators, wings and stages, reused by every rig you build."),
            ("6-suit", "Suit", "Style, size, layers", "The suit's own estimate to start from, until your own check replaces it."),
         ]),
]

# TITLE_D 0 = no title card: the video opens on scene 1, the same frame as its poster, because the page
# already shows the icon, name and sentence right under the video. A few seconds of title card made
# viewers wait 8-10 s before the app appeared. Set it to 1.5 or more to bring a title card back.
TITLE_D, SCENE_D, OUTRO_D, FADE = 0.0, 4.6, 3.6, 0.6
BG_CLIPS = [f"{PROJECTS}/surface_interval/reference-footage/clips/reef-slope.mp4",
            f"{PROJECTS}/surface_interval/reference-footage/clips/turtle-slope.mp4"]

def run(cmd):
    print("$", " ".join(cmd if len(" ".join(cmd)) < 600 else cmd[:6] + ["…"]))
    subprocess.run(cmd, check=True)

# ---------- drawing ----------
def rounded_mask(size, radius):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, size[0]-1, size[1]-1), radius=radius, fill=255)
    return m

def app_icon(path, size):
    im = Image.open(path).convert("RGBA").resize((size, size), Image.LANCZOS)
    im.putalpha(rounded_mask((size, size), int(size*0.224)))
    return im

_frames = {}
def phone_chrome(w, height, radius_k=0.062, bezel=7, pad=90, lift=30):
    """The bezel and the soft shadow for a screen w x height, drawn once per size."""
    key = (w, height, radius_k, bezel)
    if key in _frames: return _frames[key]
    r = int(height * radius_k)
    frame = Image.new("RGBA", (w + 2*bezel, height + 2*bezel), (0, 0, 0, 0))
    ImageDraw.Draw(frame).rounded_rectangle((0, 0, frame.width-1, frame.height-1), radius=r+bezel, fill=(14, 16, 20, 255), outline=(70, 76, 84, 255), width=1)
    canvas = Image.new("RGBA", (frame.width + 2*pad, frame.height + 2*pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((pad, pad+lift, pad+frame.width, pad+frame.height+lift), radius=r+bezel, fill=(0, 0, 0, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(40))
    canvas.alpha_composite(sh)
    canvas.alpha_composite(frame, (pad, pad))
    _frames[key] = (canvas, rounded_mask((w, height), r), pad, bezel)
    return _frames[key]

def phone(path, height):
    """A screenshot in a phone: rounded corners, a thin bezel, a soft shadow. Returns the picture and its padding."""
    shot = (path if isinstance(path, Image.Image) else Image.open(path)).convert("RGBA")
    w = round(shot.width * height / shot.height)
    shot = shot.resize((w, height), Image.LANCZOS)
    canvas, mask, pad, bezel = phone_chrome(w, height)
    shot.putalpha(mask)
    canvas = canvas.copy()
    canvas.alpha_composite(shot, (pad + bezel, pad + bezel))
    return canvas, pad

def window(path, height):
    """A Mac window (a screenshot wider than tall): small corners, no bezel, the same shadow."""
    shot = (path if isinstance(path, Image.Image) else Image.open(path)).convert("RGBA")
    w = round(shot.width * height / shot.height)
    shot = shot.resize((w, height), Image.LANCZOS)
    canvas, mask, pad, bezel = phone_chrome(w, height, radius_k=0.018, bezel=0)
    shot.putalpha(mask)
    canvas = canvas.copy()
    canvas.alpha_composite(shot, (pad + bezel, pad + bezel))
    return canvas, pad

def paper(path, height):
    """A picture the app shares (the sent plan, the card), drawn as a sheet: square-ish corners, a hairline, the same shadow."""
    shot = (path if isinstance(path, Image.Image) else Image.open(path)).convert("RGBA")
    w = round(shot.width * height / shot.height)
    shot = shot.resize((w, height), Image.LANCZOS)
    canvas, mask, pad, bezel = phone_chrome(w, height, radius_k=0.012, bezel=1)
    shot.putalpha(mask)
    canvas = canvas.copy()
    canvas.alpha_composite(shot, (pad + bezel, pad + bezel))
    return canvas, pad

# ---------- a scene that scrolls a whole page ----------
# A scene whose stem is a folder of screenshots (00.png, 01.png, … each the same screen scrolled
# further down, overlapping the one before) scrolls the phone through the whole page, top to bottom.
# The app's own screenshot script takes the pieces (Dive log: `scripts/site-screenshots.sh`).
SCROLL_D = 6.4            # seconds; it holds the top, scrolls, holds the bottom
# What stays put while a page scrolls, in points down a 956-point screen. Dive log: the status bar
# and the strip with the buttons once the page has scrolled (fading in under it), and the tab bar
# with its shadow, over an opaque band from 872. An app whose page has only a status bar keeps that.
CHROME_TOP_PT, CHROME_FADE_PT, CHROME_BOTTOM_PT, TAB_BAR_PT = 118, 40, 120, 872   # Dive log's, kept for the notes

_pages = {}
def stitch(folder, chrome=DIVE_LOG_CHROME):
    """The pieces of one scrolling page as one tall picture, and the chrome that stays put."""
    key = (folder, tuple(sorted(chrome.items(), key=str)))
    if key in _pages: return _pages[key]
    paths = sorted(glob.glob(os.path.join(folder, "*.png")))
    shots = [np.asarray(Image.open(p).convert("RGB")) for p in paths]
    H = shots[0].shape[0]
    scale = shots[0].shape[1] / 440
    y0, y1 = int(chrome["top"] * scale), H - int(chrome["bottom"] * scale)
    pieces = [shots[0][:y1]]
    for a, b in zip(shots, shots[1:]):
        # the shift whose overlapping rows agree best; compared on every 3rd row and 8th column
        A, B = a[y0:y1:3, ::8].astype(np.int16), b[y0:y1:3, ::8].astype(np.int16)
        n = A.shape[0]
        diffs = [np.abs(A[d:] - B[:n - d]).mean() for d in range(0, n - 40)]
        d = int(np.argmin(diffs)) * 3
        if d >= 6: pieces.append(b[y1 - d:y1])
    pieces.append(shots[-1][y1:])
    page = Image.fromarray(np.concatenate(pieces))
    top = Image.fromarray(shots[1 if len(shots) > 1 else 0][:y0]).convert("RGBA")
    if chrome.get("glyphs"):
        # the glyphs come from the piece whose bar has the least under it, a page's own blank rows
        cleanest = min(shots[1:], key=lambda sh: int((np.asarray(Image.fromarray(sh[:y0]).convert("L")) < 150).sum()))
        top = Image.fromarray(cleanest[:y0]).convert("RGBA")
        dark = top.convert("L").point(lambda v: 255 if v < 150 else 0).filter(ImageFilter.MaxFilter(3))
        top.putalpha(dark)
    fade = int(chrome["fade"] * scale)
    if fade:
        alpha = Image.new("L", top.size, 255)
        for y in range(fade):
            ImageDraw.Draw(alpha).line((0, y0 - fade + y, top.width, y0 - fade + y), fill=int(255 * (1 - y / fade)))
        top.putalpha(alpha)
    bar = None
    if chrome["tab"] is not None:
        ty0 = int(chrome["tab"] * scale)
        bar = (Image.fromarray(shots[0][ty0:]).convert("RGBA"), (0, ty0))
    _pages[key] = (page, top, bar, H, scale)
    return _pages[key]

def page_screen(folder, y, chrome=DIVE_LOG_CHROME):
    """The screen a phone shows with the stitched page scrolled y pixels down."""
    page, top, bar, H, scale = stitch(folder, chrome)
    travel = page.height - H
    y = max(0, min(round(y), travel))
    screen = page.crop((0, y, page.width, y + H)).convert("RGBA")
    if chrome["fade"]:
        k = min(y / (150 * scale), 1)               # the strip comes in as the banner leaves
        if k > 0:
            strip = top.copy(); strip.putalpha(strip.getchannel("A").point(lambda a: int(a * k)))
            screen.alpha_composite(strip)
    else:
        screen.alpha_composite(top)
    if bar and y < travel: screen.alpha_composite(bar[0], bar[1])   # the last piece has its own
    return screen, travel, scale

def scroll_frames(folder, height, work, index, duration):
    """The phone at each frame of a scrolling scene, as PNGs; returns the ffmpeg pattern and pad."""
    _, travel, _ = page_screen(folder, 0)
    frames = round(duration * FPS)
    hold_top, hold_end = 0.9, 1.3
    pad = None
    for f in range(frames):
        t = f / FPS
        u = min(max((t - hold_top) / (duration - hold_top - hold_end), 0), 1)
        u = u * u * (3 - 2 * u)                         # ease in and out
        screen, _, _ = page_screen(folder, u * travel)
        ph, pad = phone(screen, height)
        ph.save(os.path.join(work, f"scroll-{index}-{f:04d}.png"))
    return os.path.join(work, f"scroll-{index}-%04d.png"), pad, ph.width

def wrap(draw, text, f, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=f) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def draw_spaced(draw, xy, text, f, fill, spacing):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=f, fill=fill)
        x += draw.textlength(ch, font=f) + spacing
    return x

def caption_layer(fmt, index, pill, headline, sub, left, banner=False):
    W, H = fmt["W"], fmt["H"]
    tall = W < H or banner
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    if tall:
        x0, max_w = 70, W - 140
        f_pill, f_head, f_sub = font(22, "Semibold"), font(58, "Bold"), font(31, "Regular")
    else:
        x0, max_w = (150, 820) if left else (1010, 760)
        f_pill, f_head, f_sub = font(22, "Semibold"), font(62, "Bold"), font(32, "Regular")
    head_lh, sub_lh = (70, 42) if tall else (74, 44)
    head_lines = wrap(d, headline, f_head, max_w)
    sub_lines = wrap(d, sub, f_sub, max_w) if sub else []
    block_h = 44 + 24 + len(head_lines)*head_lh + (18 + len(sub_lines)*sub_lh if sub_lines else 0)
    y = (96 if W < H else 70) if tall else (H - block_h) // 2
    def place(text, f):   # centred on a tall frame, left-aligned on a wide one
        return (W - d.textlength(text, font=f)) // 2 if tall else x0
    label = f"{index} · {pill.upper()}"
    tw = sum(d.textlength(c, font=f_pill) + 2.2 for c in label)
    px = (W - tw - 34) // 2 if tall else x0
    d.rounded_rectangle((px, y, px + tw + 34, y + 44), radius=22, fill=ACCENT)
    draw_spaced(d, (px + 18, y + 9), label, f_pill, (8, 24, 28), 2.2)
    y += 44 + 24
    for ln in head_lines:
        d.text((place(ln, f_head), y), ln, font=f_head, fill=P['ink']); y += head_lh
    if sub_lines:
        y += 18
        for ln in sub_lines:
            d.text((place(ln, f_sub), y), ln, font=f_sub, fill=P['dim']); y += sub_lh
    return layer

def title_layer(fmt, app):
    W, H = fmt["W"], fmt["H"]
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    if W < H:
        icon = app_icon(app["icon"], 250)
        layer.alpha_composite(icon, ((W - 250)//2, H//2 - 300))
        f_name, f_tag = font(84, "Semibold"), font(36, "Regular")
        for text, f, fill, dy in [(app["name"], f_name, P['ink'], 0), (app["tagline"], f_tag, ACCENT, 110)]:
            d.text(((W - d.textlength(text, font=f))//2, H//2 + dy), text, font=f, fill=fill)
        return layer
    icon = app_icon(app["icon"], 230)
    f_name, f_tag = font(96, "Semibold"), font(40, "Regular")
    name_w = d.textlength(app["name"], font=f_name)
    tag_w = d.textlength(app["tagline"], font=f_tag)
    total_w = 230 + 56 + max(name_w, tag_w)
    x = (W - total_w) // 2
    layer.alpha_composite(icon, (int(x), (H - 230)//2))
    tx = x + 230 + 56
    d.text((tx, H//2 - 92), app["name"], font=f_name, fill=P['ink'])
    d.text((tx + 4, H//2 + 30), app["tagline"], font=f_tag, fill=ACCENT)
    return layer

def outro_layer(fmt, app):
    W, H = fmt["W"], fmt["H"]
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    icon = app_icon(app["icon"], 150)
    layer.alpha_composite(icon, ((W-150)//2, H//2 - 230))
    f_name, f_line, f_url = font(66, "Semibold"), font(34, "Regular"), font(30, "Medium")
    for text, f, fill, dy in [(app["name"], f_name, P['ink'], -40), (app.get("outro", "Free on the App Store"), f_line, P['dim'], 50), ("diver.today", f_url, ACCENT, 120)]:
        tw = d.textlength(text, font=f)
        d.text(((W - tw)//2, H//2 + dy), text, font=f, fill=fill)
    return layer

# ---------- a journey: one phone, the story on its screen ----------
# A journey replaces an app's scenes with steps the phone goes through without leaving its place: the
# screen crossfades to the next shot, scrolls to the next place on the same stitched page, or cycles
# through a few shots under one caption; a picture the app shares (the sent plan, the card) is drawn
# as a sheet of paper where the phone was, and a gallery lays a few shots side by side under a banner.
# Each step: dict(shot="stem" | shot=["stem", …] | page="folder", at=<points> [, to=<points>] |
#                 gallery=["stem", …], pill=…, head=…, sub=…, hold=<seconds>)
JOURNEY_HOLD, XFADE, SCROLL_PPS = 3.8, 0.6, 650   # a step's hold, the crossfade, scroll speed in points per second

def ease(u): return u * u * (3 - 2 * u)

class Stage:
    """Draws what a journey step shows, as one full frame on a transparent background."""
    def __init__(self, fmt, app):
        self.fmt, self.app = fmt, app
        W, H = fmt["W"], fmt["H"]
        self.tall = W < H
        self.chrome = app.get("chrome", STATUS_BAR_CHROME)
        probe, pad = phone(Image.new("RGB", (1320, 2868)), fmt["phone_h"])
        self.ph_w, self.pad = probe.width, pad
        # centred on a tall frame; on the right of a wide one, the caption on the left
        self.px = (W - self.ph_w) // 2 if self.tall else W - 330 - self.ph_w + pad
        self.py = fmt["phone_top"] - pad
    def blank(self): return Image.new("RGBA", (self.fmt["W"], self.fmt["H"]), (0, 0, 0, 0))
    def path(self, stem): return stem + ".png" if stem.startswith("/") else os.path.join(self.app["shots"], stem + ".png")
    def aspect(self, stem):
        im = Image.open(self.path(stem)); return im.width / im.height
    def is_window(self, stem): return self.aspect(stem) > 1.0      # a Mac window
    def is_paper(self, stem):
        a = self.aspect(stem); return not (0.40 < a < 0.52) and a <= 1.0   # a 6.9" screen is 0.46; a shared picture otherwise
    def item(self, stem, height):
        return (window if self.is_window(stem) else paper if self.is_paper(stem) else phone)(self.path(stem), height)
    def still(self, stem):
        f = self.blank()
        if self.is_window(stem):                        # a window sits under a banner caption, centred, as wide as fits
            W, H = self.fmt["W"], self.fmt["H"]; top = 330 if self.tall else 270
            h = min(self.fmt["phone_h"], H - top - 40, int((W - 120) / self.aspect(stem)))
            it, pad = self.item(stem, h); f.alpha_composite(it, ((W - it.width) // 2, top - pad)); return f
        h = self.fmt["phone_h"]
        if self.is_paper(stem):                          # a sent page is shown whole, signatures included
            h = min(h, self.fmt["H"] - self.py - self.pad - 24)
        it, pad = self.item(stem, h)
        f.alpha_composite(it, (self.px + (self.ph_w - it.width) // 2, self.py)); return f
    def page(self, stem, at_pt):
        folder = os.path.join(self.app["shots"], stem)
        _, travel, scale = page_screen(folder, 0, self.chrome)
        screen, _, _ = page_screen(folder, at_pt * scale, self.chrome)
        ph, _ = phone(screen, self.fmt["phone_h"]); f = self.blank(); f.alpha_composite(ph, (self.px, self.py)); return f
    def page_end_pt(self, stem):
        _, travel, scale = page_screen(os.path.join(self.app["shots"], stem), 0, self.chrome); return travel / scale
    def gallery(self, stems):
        W, H = self.fmt["W"], self.fmt["H"]
        f = self.blank(); n = len(stems); gap = 36 if self.tall else 48
        top = 330 if self.tall else 270
        aspects = [Image.open(self.path(s)).size for s in stems]
        aspects = [w / h for w, h in aspects]
        h = int((W - 120 - gap * (n - 1)) / sum(aspects))
        h = min(h, H - top + int(0.3 * H), self.fmt["phone_h"])   # phones may run off the bottom, as the phone does
        if all(self.is_paper(s) for s in stems): h = min(h, H - top - 24)   # sent pages are shown whole
        widths = [round(a * h) for a in aspects]
        x = (W - sum(widths) - gap * (n - 1)) // 2
        for s, w in zip(stems, widths):
            it, pad = self.item(s, h)
            f.alpha_composite(it, (x - pad, top - pad)); x += w + gap
        return f

def journey_layers(app, fmt, work):
    """The picture layer of a journey as a run of PNG frames (a held frame is a hard link), and its caption layers."""
    stage = Stage(fmt, app)
    steps = app["journey"]
    frames = []                      # (image, how many frames)
    captions = []                    # (index, pill, head, sub, start, duration, banner)
    prev = None
    for i, step in enumerate(steps):
        banner = "gallery" in step or ("shot" in step and not isinstance(step["shot"], list) and stage.is_window(step["shot"]))
        if "gallery" in step: imgs = [stage.gallery(step["gallery"])]
        elif "page" in step: imgs = [stage.page(step["page"], step["at"])]
        else: imgs = [stage.still(s) for s in (step["shot"] if isinstance(step["shot"], list) else [step["shot"]])]
        hold = step.get("hold", JOURNEY_HOLD)
        start = sum(n for _, n in frames) / FPS
        if prev is not None:                                   # the way in
            last = steps[i - 1]
            if "page" in step and last.get("page") == step["page"]:
                a, b = last.get("to", last["at"]), step["at"]
                n = round(min(max(abs(b - a) / SCROLL_PPS, 0.8), 2.4) * FPS)
                for k in range(1, n + 1): frames.append((stage.page(step["page"], a + (b - a) * ease(k / n)), 1))
            else:
                n = round(XFADE * FPS)
                for k in range(1, n + 1): frames.append((Image.blend(prev, imgs[0], k / n), 1))
        if "to" in step:                                       # the page scrolls under the caption
            n = round(hold * FPS); hold_in, hold_out = 0.9, 1.1
            for k in range(n):
                u = ease(min(max((k / FPS - hold_in) / (hold - hold_in - hold_out), 0), 1))
                frames.append((stage.page(step["page"], step["at"] + (step["to"] - step["at"]) * u), 1))
            prev = frames[-1][0]
        elif len(imgs) > 1:                                    # a few shots under one caption
            each = (hold - XFADE * (len(imgs) - 1)) / len(imgs)
            for j, im in enumerate(imgs):
                if j: 
                    n = round(XFADE * FPS)
                    for k in range(1, n + 1): frames.append((Image.blend(imgs[j - 1], im, k / n), 1))
                frames.append((im, round(each * FPS)))
            prev = imgs[-1]
        else:
            frames.append((imgs[0], round(hold * FPS))); prev = imgs[0]
        end = sum(n for _, n in frames) / FPS
        captions.append((i + 1, step["pill"], step["head"], step.get("sub", ""), start, end - start, banner))
    # write the frames; a held frame is one file and hard links (the last run's frames go first)
    for old in glob.glob(os.path.join(work, "journey-*.png")): os.remove(old)
    k = 0
    for im, n in frames:
        p = os.path.join(work, f"journey-{k:04d}.png"); im.save(p, compress_level=1)
        for j in range(1, n): os.link(p, os.path.join(work, f"journey-{k + j:04d}.png"))
        k += n
    return os.path.join(work, "journey-%04d.png"), k / FPS, captions

# ---------- stages ----------
def build_bg():
    os.makedirs(BUILD, exist_ok=True)
    out = os.path.join(BUILD, "bg.mp4")
    inputs = []
    for c in BG_CLIPS: inputs += ["-i", c]
    fc = "[0:v][1:v]concat=n=2:v=1:a=0,scale=1920:1080,setpts=1.5*PTS,gblur=sigma=28,eq=brightness=-0.22:saturation=1.0:contrast=1.06,fps=30,format=yuv420p[v]"
    run(["ffmpeg", "-y", "-v", "error"] + inputs + ["-filter_complex", fc, "-map", "[v]", "-t", "40", "-c:v", "libx264", "-preset", "medium", "-crf", "16", out])
    print("bg ->", out)
    # the light one: the same reef, washed towards white, for a video on a bright section of the page
    out = os.path.join(BUILD, "bg-light.mp4")
    fc = ("[0:v][1:v]concat=n=2:v=1:a=0,scale=1920:1080,setpts=1.5*PTS,gblur=sigma=34,eq=brightness=0.14:saturation=0.9:contrast=0.85,"
          "format=rgba,colorchannelmixer=aa=0.30[reef];color=c=0xf1faf8:s=1920x1080:r=30,format=rgba[paper];"
          "[paper][reef]overlay=shortest=1,fps=30,format=yuv420p[v]")
    run(["ffmpeg", "-y", "-v", "error"] + inputs + ["-filter_complex", fc, "-map", "[v]", "-t", "40", "-c:v", "libx264", "-preset", "medium", "-crf", "16", out])
    print("bg ->", out)

def build_icons():
    os.makedirs(IMG, exist_ok=True)
    for app in APPS:
        if app.get("second"): continue
        app_icon(app["icon"], 512).save(os.path.join(IMG, f"{app['slug']}.png"), optimize=True)
    # favicon: a teal disc with a white diver's bubble ring — no app's icon favoured over another
    fav = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    d = ImageDraw.Draw(fav)
    d.rounded_rectangle((0, 0, 255, 255), radius=58, fill=(11, 15, 20))
    d.ellipse((58, 58, 198, 198), outline=ACCENT, width=22)
    d.ellipse((108, 108, 148, 148), fill=ACCENT)
    fav.save(os.path.join(IMG, "favicon.png"))
    fav.resize((180, 180), Image.LANCZOS).save(os.path.join(IMG, "apple-touch-icon.png"))
    # og image 1200x630
    og = Image.new("RGB", (1200, 630), (11, 15, 20))
    d = ImageDraw.Draw(og)
    f_big, f_small = font(64, "Semibold"), font(28, "Regular")
    d.text((80, 90), "diver.today", font=font(30, "Medium"), fill=ACCENT)
    d.text((80, 140), "Five iPhone apps for divers", font=f_big, fill=P['ink'])
    d.text((80, 230), "Gas planning · decompression · weighting · Shearwater log · dive videos", font=f_small, fill=P['dim'])
    x = 80
    for app in APPS:
        if app.get("second"): continue
        og.paste(app_icon(app["icon"], 150), (x, 380), app_icon(app["icon"], 150)); x += 150 + 50
    og.save(os.path.join(IMG, "og.png"), optimize=True)
    print("icons, favicon, og ->", IMG)

def build_video(app, name, fmt):
    W, H = fmt["W"], fmt["H"]
    slug = app["slug"]
    P.clear(); P.update(PALETTES[app.get("theme", "dark")])
    work = os.path.join(BUILD, slug, name); os.makedirs(work, exist_ok=True)
    layers = []   # (path, start, duration, x, y_expr)
    t = 0.0
    if TITLE_D > 0:
        p = os.path.join(work, "title.png"); title_layer(fmt, app).save(p); layers.append((p, t, TITLE_D, 0, "0")); t += TITLE_D
    if "journey" in app:
        pattern, total_j, captions = journey_layers(app, fmt, work)
        layers.append((pattern, t, total_j, 0, "0"))
        for index, pill, head, sub, st, du, banner in captions:
            p = os.path.join(work, f"caption-{index}.png"); caption_layer(fmt, index, pill, head, sub, left=True, banner=banner).save(p)
            layers.append((p, t + st, du, 0, "0"))
        t += total_j
    for i, (shot, pill, head, sub) in enumerate(app.get("scenes", []), 1):
        phone_left = (i % 2 == 0)
        folder = os.path.join(app["shots"], shot)
        if os.path.isdir(folder):
            d = SCROLL_D
            p1, pad, ph_w = scroll_frames(folder, fmt["phone_h"], work, i, d)
        else:
            d = SCENE_D
            ph, pad = phone(os.path.join(app["shots"], shot + ".png"), fmt["phone_h"])
            p1 = os.path.join(work, f"phone-{i}.png"); ph.save(p1); ph_w = ph.width
        if W < H:
            px = (W - ph_w) // 2
        else:
            px = (330 - pad) if phone_left else (W - 330 - ph_w + pad)
        layers.append((p1, t, d, px, f"{fmt['phone_top'] - pad}-{fmt['drift']}*clip((t-{t:.2f})/{d},0,1)"))
        p2 = os.path.join(work, f"caption-{i}.png"); caption_layer(fmt, i, pill, head, sub, left=not phone_left).save(p2)
        layers.append((p2, t, d, 0, "0"))
        t += d
    p = os.path.join(work, "outro.png"); outro_layer(fmt, app).save(p); layers.append((p, t, OUTRO_D, 0, "0")); t += OUTRO_D
    total = t
    cmd = ["ffmpeg", "-y", "-v", "error", "-stats", "-stream_loop", "-1", "-i", os.path.join(BUILD, P["bg"])]
    bg_fit = f"[0:v]scale=-2:{H},crop={W}:{H}[bg]" if W < H else f"[0:v]scale={W}:{H}[bg]"
    fc = [bg_fit]
    for k, (path, st, du, x, yexpr) in enumerate(layers, 1):
        still = [] if "%" in path else ["-loop", "1"]   # a scrolling phone is a run of frames
        cmd += still + ["-framerate", str(FPS), "-t", f"{du:.2f}", "-i", path]
        fade_out = max(du - FADE, 0)
        fade_in = f"fade=t=in:st=0:d={FADE}:alpha=1," if st > 0 else ""   # the opening frame is never faded: it is the poster
        fc.append(f"[{k}:v]format=rgba,{fade_in}fade=t=out:st={fade_out:.2f}:d={FADE}:alpha=1,"
                  f"tpad=start_duration={st:.2f}:start_mode=add:color=black@0.0[l{k}]")
    prev = "[bg]"
    for k, (path, st, du, x, yexpr) in enumerate(layers, 1):
        fc.append(f"{prev}[l{k}]overlay=x={x}:y='{yexpr}':eof_action=pass:format=auto:eval=frame[o{k}]")
        prev = f"[o{k}]"
    fc.append(f"{prev}format=yuv420p[v]")
    os.makedirs(VIDEO, exist_ok=True)
    master = os.path.join(work, "master.mp4")
    run(cmd + ["-filter_complex", ";".join(fc), "-map", "[v]", "-t", f"{total:.2f}", "-r", str(FPS),
               "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-pix_fmt", "yuv420p", master])
    out = os.path.join(VIDEO, f"{slug}-{name}.mp4")
    run(["ffmpeg", "-y", "-v", "error", "-i", master, "-vf", f"scale=-2:{fmt['out_h']}", "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "25",
         "-profile:v", "high", "-level", "4.1", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-tune", "stillimage", out])
    poster_w = 1600 if W > H else 960
    run(["ffmpeg", "-y", "-v", "error", "-ss", "0", "-i", master, "-frames:v", "1", "-vf", f"scale={poster_w}:-2", "-q:v", "4", os.path.join(IMG, f"{slug}-{name}-poster.jpg")])
    print(f"{slug} {name}: {total:.1f}s ->", out)

if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    only = set(sys.argv[2:])
    if what in ("bg", "all"): build_bg()
    if what in ("icons", "all"): build_icons()
    if what in ("videos", "all"):
        for app in APPS:
            if not only or app["slug"] in only:
                for name, fmt in FORMATS.items(): build_video(app, name, fmt)
