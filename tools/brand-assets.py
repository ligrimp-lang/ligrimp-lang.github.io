#!/usr/bin/env python3
"""The family's pictures for its three profiles (YouTube, Instagram, the Facebook Page behind Instagram), made from the repository's
own pieces so the channels look like the site and the episodes: the dark ground, the five app icons in the page's order, the hero
line, the teal, and Rustam's charcoal cat drawn in silver (Rustam, 2026-10-29: "personalize as much as you can the screens including
colors, images, logos etc"). Needs Pillow; the type is SF Pro from the system, so the real render is on the Mac (anywhere else DejaVu
stands in, with a warning, for a look at the layout). Writes build/brand/:

    youtube-banner.png            2560×1440; everything that matters inside the centred 1546×423 that every device shows
    avatar-{a,b}-youtube.png      800×800     two candidates for the mark: the cat on the dark ground, cropped to a circle by the
    avatar-{a,b}-instagram.png    1080×1080   platforms, legible at 110 px, no text; a is the head, b the standing cat in a teal ring
    avatar-{a,b}-facebook.png     720×720
    facebook-cover.png            1640×624; everything that matters inside the centred 820×312; the banner's language
    youtube-watermark.png         150×150, transparent: the mark alone, for the corner of every video
    sheet.png                     every asset at display size, the avatars as circles at 300 and 110 px, for Rustam's look

    python3 tools/brand-assets.py            # everything
    python3 tools/brand-assets.py sheet      # banner | avatars | cover | watermark | sheet

Imports tools/build-media.py (font(), ACCENT, the dark palette, app_icon()) and tools/pilot-episode.py (cat(size, pose), the drawings
in tools/assets/cat/ in the silver tint with the teal glow). The profiles' texts are docs/brand-profiles.md; tools/apply-youtube-branding.py
sends the banner, the watermark and the texts to YouTube; the avatars and the Facebook cover are set by hand (no API for them).
"""
import os, sys, importlib.util
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "build", "brand")

def load(name, fn):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn)); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
bm, pe = load("bm", "build-media.py"), load("pe", "pilot-episode.py")
ACCENT, INK, DIM = bm.ACCENT, bm.INK, bm.DIM
DARK = (16, 22, 28)           # #10161C, the site's ground
REEF = (13, 42, 60)           # the deep reef blue the ground runs into
HERO = "Apps for divers, today and every day."   # the page's hero line
SITE = "diver.today"
APPS = ["time-to-surface", "surface-interval", "dive-log", "turn-pressure", "weights-check"]   # the page's order, never changed alone
SAFE_BANNER = (1546, 423)     # YouTube: the centred area every device shows (phones show only this)
SAFE_COVER = (820, 312)       # Facebook: the centred area shown on desktop and phone alike
pe.CAT_TINTS["mark"] = ((104, 122, 132), (244, 247, 247), (ACCENT, 0.45))   # for the watermark alone: a lighter body, so it reads over footage

_warned = [False]
def font(size, weight="Regular"):
    try: return bm.font(size, weight)
    except OSError:
        if not _warned[0]: print("SF Pro not found: DejaVu stands in; render on the Mac for the real thing", file=sys.stderr); _warned[0] = True
        return ImageFont.truetype("DejaVuSans-Bold.ttf" if weight in ("Bold", "Semibold", "Heavy") else "DejaVuSans.ttf", size)

# ---------- the pieces ----------

def ground(w, h, glow=0.9):
    """The dark ground: #10161C at the top running into the reef blue, a faint teal glow low in the middle, as behind the episodes' cards."""
    im = Image.new("RGB", (1, h))
    for y in range(h):
        t = (y / max(1, h - 1)) ** 1.3
        im.putpixel((0, y), tuple(int(DARK[k] + (REEF[k] - DARK[k]) * t) for k in range(3)))
    im = im.resize((w, h), Image.BILINEAR).convert("RGBA")
    if glow:
        g = Image.new("L", (w, h), 0); d = ImageDraw.Draw(g)
        rx, ry = int(w * 0.36), int(h * 0.42); cx, cy = w // 2, int(h * 0.62)
        d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=int(255 * 0.16 * glow))
        g = g.filter(ImageFilter.GaussianBlur(min(w, h) * 0.18))
        layer = Image.new("RGBA", (w, h), ACCENT + (0,)); layer.putalpha(g); im.alpha_composite(layer)
    return im

def icons_row(size, gap):
    row = Image.new("RGBA", (len(APPS) * size + (len(APPS) - 1) * gap, size), (0, 0, 0, 0))
    for i, slug in enumerate(APPS):
        row.alpha_composite(bm.app_icon(os.path.join(ROOT, "img", f"{slug}.png"), size), (i * (size + gap), 0))
    return row

def centred(d, text, f, cx, y, fill):
    d.text((cx - d.textlength(text, font=f) / 2, y), text, font=f, fill=fill)

def hero_block(im, cx, top, icon, gap, hero_size, url_size, spacing):
    """The five icons, the hero line and diver.today, stacked and centred on cx from `top`. Returns the bottom."""
    row = icons_row(icon, gap); im.alpha_composite(row, (int(cx - row.width / 2), top))
    d = ImageDraw.Draw(im); y = top + icon + spacing[0]
    f_hero = font(hero_size, "Semibold"); centred(d, HERO, f_hero, cx, y, INK); y += int(hero_size * 1.18) + spacing[1]
    f_url = font(url_size, "Bold"); centred(d, SITE, f_url, cx, y, ACCENT); y += int(url_size * 1.18)
    return y

def circle_mask(size, inset=0):
    m = Image.new("L", (size, size), 0); ImageDraw.Draw(m).ellipse((inset, inset, size - 1 - inset, size - 1 - inset), fill=255); return m

# ---------- the assets ----------

def banner():
    """2560×1440. The hero block sits in the centred 1546×423 so every crop (TV: all of it; desktop: a 2560×423 band; phone: 1546×423)
    carries the icons, the line and the address; the cat swims outside the safe area, so desktops and TVs see it and phones lose it."""
    W, H = 2560, 1440; im = ground(W, H)
    sx, sy = (W - SAFE_BANNER[0]) // 2, (H - SAFE_BANNER[1]) // 2
    bottom = hero_block(im, W / 2, sy + 24, icon=112, gap=26, hero_size=60, url_size=54, spacing=(30, 18))
    assert bottom <= sy + SAFE_BANNER[1] - 16, f"the hero block runs out of the safe area ({bottom} > {sy + SAFE_BANNER[1]})"
    c = pe.cat(430, "swimming"); im.alpha_composite(c, (sx - c.width - 40, (H - c.height) // 2 + 10))
    return im

def avatar(candidate, size=1080):
    """The mark: a is the head, close, filling the circle; b the standing cat, smaller, in a thin teal ring. Rendered square (the
    platforms crop the circle themselves); the ground fills the square so a square crop works too."""
    im = ground(size, size, glow=1.2)
    if candidate == "a":
        c = pe.cat(int(size * 1.02), "head"); im.alpha_composite(c, (int(size * 0.02), int(size * 0.06)))
    else:
        d = ImageDraw.Draw(im); w = max(3, size // 90); inset = int(size * 0.075)
        d.ellipse((inset, inset, size - 1 - inset, size - 1 - inset), outline=ACCENT + (255,), width=w)
        c = pe.cat(int(size * 0.76), "standing"); im.alpha_composite(c, ((size - c.width) // 2, int(size * 0.14)))
    return im

def cover():
    """1640×624 for the Facebook Page; the hero block inside the centred 820×312, the cat to the left of it."""
    W, H = 1640, 624; im = ground(W, H)
    sx, sy = (W - SAFE_COVER[0]) // 2, (H - SAFE_COVER[1]) // 2
    bottom = hero_block(im, W / 2, sy + 18, icon=68, gap=16, hero_size=36, url_size=34, spacing=(20, 12))
    assert bottom <= sy + SAFE_COVER[1] - 10, f"the hero block runs out of the safe area ({bottom} > {sy + SAFE_COVER[1]})"
    c = pe.cat(300, "swimming"); im.alpha_composite(c, (sx - c.width - 30, (H - c.height) // 2))
    return im

def watermark():
    """150×150, transparent: the head alone in the lighter tint, with the teal glow for an edge over any footage."""
    return pe.cat(150, "head", "mark")

def as_circle(im, size):
    out = im.resize((size, size), Image.LANCZOS).convert("RGBA"); out.putalpha(circle_mask(size)); return out

def sheet(assets):
    """Everything at display size, with the safe areas drawn, for the look before anything is uploaded."""
    W, H = 2400, 1900; im = Image.new("RGBA", (W, H), (34, 40, 46, 255)); d = ImageDraw.Draw(im)
    f_label, f_small = font(26, "Semibold"), font(20, "Regular")
    def label(x, y, text): d.text((x, y), text, font=f_label, fill=INK)
    def note(x, y, text): d.text((x, y), text, font=f_small, fill=DIM)
    label(60, 40, "YouTube banner 2560×1440, at half size"); note(60, 76, "outer line: what desktops show (a 2560×423 band) · teal: what phones show (1546×423, the safe area) · TVs show all of it")
    b = assets["banner"].resize((1280, 720), Image.LANCZOS); im.alpha_composite(b, (60, 110))
    sx, sy = (1280 - 773) // 2, (720 - 212) // 2
    d.rectangle((60, 110 + sy, 60 + 1279, 110 + sy + 211), outline=(255, 255, 255, 110), width=2)
    d.rectangle((60 + sx, 110 + sy, 60 + sx + 772, 110 + sy + 211), outline=ACCENT + (255,), width=3)
    for i, cand in enumerate(("a", "b")):
        y = 110 + i * 400; x = 1420
        label(x, y - 70, f"Mark, candidate {cand}" + (": the head, close" if cand == "a" else ": the standing cat in a teal ring"))
        note(x, y - 36, "one picture: youtube 800 · instagram 1080 · facebook 720; each platform crops the circle")
        im.alpha_composite(as_circle(assets[f"avatar-{cand}"], 300), (x, y))
        im.alpha_composite(as_circle(assets[f"avatar-{cand}"], 110), (x + 340, y + 190)); note(x + 340, y + 160, "at 110 px")
        im.alpha_composite(assets[f"avatar-{cand}"].resize((110, 110), Image.LANCZOS), (x + 480, y + 190)); note(x + 480, y + 160, "square")
    label(60, 890, "Facebook cover 1640×624, at half size"); note(60, 926, "teal: the centred 820×312 shown on desktop and phone alike")
    c = assets["cover"].resize((820, 312), Image.LANCZOS); im.alpha_composite(c, (60, 960))
    cx, cy = (820 - 410) // 2, (312 - 156) // 2
    d.rectangle((60 + cx, 960 + cy, 60 + cx + 409, 960 + cy + 155), outline=ACCENT + (255,), width=3)
    label(960, 890, "YouTube watermark 150×150, transparent"); note(960, 926, "the corner of every video, over dark water and over sunlit blue")
    wm = assets["watermark"]
    for j, bg in enumerate(((12, 24, 34), (90, 160, 190), (230, 236, 238))):
        tile = Image.new("RGBA", (230, 230), bg + (255,)); tile.alpha_composite(wm, (40, 40)); im.alpha_composite(tile, (960 + j * 250, 960))
    label(60, 1330, "The banner as a phone shows it (1546×423, at half size)")
    ph = assets["banner"].crop(((2560 - 1546) // 2, (1440 - 423) // 2, (2560 + 1546) // 2, (1440 + 423) // 2)).resize((773, 212), Image.LANCZOS)
    im.alpha_composite(ph, (60, 1380))
    label(960, 1330, "The banner as a desktop shows it (2560×423, at a third)")
    dk = assets["banner"].crop((0, (1440 - 423) // 2, 2560, (1440 + 423) // 2)).resize((853, 141), Image.LANCZOS)
    im.alpha_composite(dk, (960, 1380))
    note(60, 1640, "Made by tools/brand-assets.py from img/, tools/assets/cat/ and the site's colours; the texts are in docs/brand-profiles.md.")
    return im

# ---------- the run ----------

SIZES = {"youtube": 800, "instagram": 1080, "facebook": 720}

def save(im, name):
    path = os.path.join(OUT, name); im.save(path); print(f"  {name}  {im.width}×{im.height}  {os.path.getsize(path) / 1024:.0f} KB"); return path

def main(what):
    os.makedirs(OUT, exist_ok=True); assets = {}
    print("build/brand/")
    if what in ("all", "banner", "sheet"): assets["banner"] = banner()
    if what in ("all", "banner"): save(assets["banner"], "youtube-banner.png")
    if what in ("all", "avatars", "sheet"):
        for cand in ("a", "b"):
            assets[f"avatar-{cand}"] = avatar(cand)
            if what != "sheet":
                for platform, size in SIZES.items(): save(assets[f"avatar-{cand}"].resize((size, size), Image.LANCZOS), f"avatar-{cand}-{platform}.png")
    if what in ("all", "cover", "sheet"): assets["cover"] = cover()
    if what in ("all", "cover"): save(assets["cover"], "facebook-cover.png")
    if what in ("all", "watermark", "sheet"): assets["watermark"] = watermark()
    if what in ("all", "watermark"): save(assets["watermark"], "youtube-watermark.png")
    if what in ("all", "sheet"): save(sheet(assets), "sheet.png")

if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what not in ("all", "banner", "avatars", "cover", "watermark", "sheet"): sys.exit("all | banner | avatars | cover | watermark | sheet")
    main(what)
