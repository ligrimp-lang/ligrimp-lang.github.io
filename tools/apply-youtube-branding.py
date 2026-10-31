#!/usr/bin/env python3
"""Puts the family's branding on the YouTube channel: the banner, the description, the keywords and the watermark. Standard library only.

    apply-youtube-branding.py [--banner path] [--watermark path] [--dry-run]

What it does, in order (the quota cost in brackets):
  1. channels.list [1], mine=true, parts id and brandingSettings: the channel's id and what its branding holds now
  2. channelBanners.insert [50] with the banner (build/brand/youtube-banner.png by default, from tools/brand-assets.py; YouTube wants
     2048×1152 or more, 16:9, under 6 MB): the answer carries the address YouTube gave the picture
  3. channels.update [50], part=brandingSettings: channel.description, channel.keywords and channel.defaultLanguage en from
     docs/brand-profiles.md (the fenced blocks under "YouTube description" and "YouTube keywords"), image.bannerExternalUrl from
     step 2; no country. The update replaces the whole brandingSettings, so the rest of what step 1 read goes back unchanged.
  4. watermarks.set [50] with the watermark (build/brand/youtube-watermark.png, 150×150, transparent), timed from the end of each
     video: offsetFromEnd, 15,000 ms, in the bottom-right corner. YouTube answers 204 with no body when it worked.

The profile picture has no API: the Mac sets it in YouTube Studio (Customisation, Branding), from build/brand/avatar-<a|b>-youtube.png,
and the channel's links, handle and trailer are set there too. --dry-run prints the texts, the files and every call and touches no network.

Credentials: ~/.config/diver-today/youtube-client.json and youtube-token.json from tools/youtube-auth.py, which this script imports for
the access token; the scopes granted there (youtube.upload, youtube.force-ssl) cover all four calls.
"""
import os, re, sys, json, uuid, argparse, importlib.util, urllib.request, urllib.parse, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
BRAND = os.path.join(ROOT, "build", "brand")
PROFILES = os.path.join(ROOT, "docs", "brand-profiles.md")
UPLOAD = "https://www.googleapis.com/upload/youtube/v3"
API = "https://www.googleapis.com/youtube/v3"
WATERMARK = {"timing": {"type": "offsetFromEnd", "offsetMs": 15000, "durationMs": 15000}, "position": {"type": "corner", "cornerPosition": "bottomRight"}}
BANNER_LIMIT, WATERMARK_LIMIT = 6 * 1024 * 1024, 1024 * 1024
NEVER = ("rock bottom", "rock-bottom", "rockbottom")   # the reserve is minimum gas and nothing else (Rustam, 2026-10-28)

spec = importlib.util.spec_from_file_location("youtube_auth", os.path.join(HERE, "youtube-auth.py"))
auth = importlib.util.module_from_spec(spec); spec.loader.exec_module(auth)

# ---------- the texts ----------

def profile_texts():
    """The fenced blocks of docs/brand-profiles.md, keyed by the heading above each: the document is the one place the texts live."""
    s = open(PROFILES, encoding="utf-8").read(); texts = {}
    for m in re.finditer(r"^#+[ \t]+([^\n]+?)[ \t]*\n(?:(?!^#).)*?^```\w*\n(.*?)^```", s, re.S | re.M):
        texts.setdefault(m.group(1).strip(), m.group(2).rstrip("\n"))
    return texts

def keywords_string(block):
    """YouTube's keywords field is one string, a space-separated list with multi-word keywords in double quotes; the document lists one
    keyword per line."""
    words = [w.strip() for w in block.splitlines() if w.strip() and not w.strip().startswith("#")]
    return " ".join(f'"{w}"' if " " in w else w for w in words), words

def check(description, keywords, words):
    problems = []
    if len(description) > 1000: problems.append(f"the description is {len(description)} characters; YouTube takes 1,000")
    if "<" in description or ">" in description: problems.append("the description has < or >, which YouTube rejects")
    if len(keywords) > 500: problems.append(f"the keywords come to {len(keywords)} characters; YouTube takes 500")
    text = (description + " " + keywords).lower()
    for term in NEVER:
        if term in text: problems.append(f"'{term}' is in the text; the reserve is called minimum gas")
    if "!" in description: problems.append("an exclamation mark; the house style has none")
    if not words: problems.append("no keywords found in docs/brand-profiles.md")
    return problems

# ---------- the calls ----------

class Token:
    def __init__(self): self.value = None
    def get(self):
        if self.value is None: self.value = auth.access_token()
        return self.value
    def refresh(self): self.value = None; return self.get()

def call(method, url, data=None, headers=None, token=None, timeout=120):
    h = dict(headers or {})
    if token: h["Authorization"] = "Bearer " + token
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r: return r.status, r.headers, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.headers, e.read()

def reason(body):
    try: return json.loads(body)["error"]["message"]
    except Exception: return body.decode(errors="replace")[:400]

def api(method, url, tok, what, data=None, content_type="application/json; charset=UTF-8", ok=(200,)):
    st, h, body = call(method, url, data, {"Content-Type": content_type} if data is not None else {}, tok.get())
    if st == 401: st, h, body = call(method, url, data, {"Content-Type": content_type} if data is not None else {}, tok.refresh())
    if st not in ok: sys.exit(f"{what} failed ({st}): {reason(body)}")
    return json.loads(body) if body else {}

def multipart_related(meta, media, media_type):
    b = uuid.uuid4().hex
    body = (f"--{b}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n{json.dumps(meta)}\r\n"
            f"--{b}\r\nContent-Type: {media_type}\r\n\r\n").encode() + media + f"\r\n--{b}--\r\n".encode()
    return body, f"multipart/related; boundary={b}"

def image_type(path): return "image/png" if path.lower().endswith(".png") else "image/jpeg"

# ---------- the run ----------

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--banner", default=os.path.join(BRAND, "youtube-banner.png"), help="the banner PNG (default build/brand/youtube-banner.png)")
    ap.add_argument("--watermark", default=os.path.join(BRAND, "youtube-watermark.png"), help="the watermark PNG (default build/brand/youtube-watermark.png)")
    ap.add_argument("--dry-run", action="store_true", help="print the texts and every call; no network, no credentials")
    a = ap.parse_args()

    texts = profile_texts()
    description, (keywords, words) = texts.get("YouTube description", ""), keywords_string(texts.get("YouTube keywords", ""))
    if not description: sys.exit(f"no 'YouTube description' block in {PROFILES}")
    problems = check(description, keywords, words)
    if problems: sys.exit("not sent:\n  " + "\n  ".join(problems))
    def size(p): return f"{os.path.getsize(p):,} bytes" if os.path.exists(p) else "NOT FOUND"

    if a.dry_run:
        print("dry run. Nothing is sent.\n")
        print(f"description ({len(description)} characters):\n{description}\n")
        print(f"keywords ({len(words)}, {len(keywords)} characters):\n{keywords}\n")
        print(f"1. GET  {API}/channels?part=id,brandingSettings&mine=true")
        print(f"2. POST {UPLOAD}/channelBanners/insert?uploadType=media  <- {a.banner} ({size(a.banner)})")
        print(f"3. PUT  {API}/channels?part=brandingSettings  channel.description, channel.keywords, channel.defaultLanguage=en, image.bannerExternalUrl=<from 2>")
        print(f"4. POST {UPLOAD}/watermarks/set?channelId=<id>&uploadType=multipart  <- {a.watermark} ({size(a.watermark)})  {json.dumps(WATERMARK)}")
        print("\nThe profile picture has no API: set build/brand/avatar-<a|b>-youtube.png in YouTube Studio.")
        return

    for path, limit, what in ((a.banner, BANNER_LIMIT, "banner"), (a.watermark, WATERMARK_LIMIT, "watermark")):
        if not os.path.exists(path): sys.exit(f"no {what} at {path}; make it with tools/brand-assets.py")
        if os.path.getsize(path) > limit: sys.exit(f"{path} is over YouTube's limit of {limit // 1024 // 1024} MB")
    tok = Token()
    ch = api("GET", f"{API}/channels?" + urllib.parse.urlencode({"part": "id,brandingSettings", "mine": "true"}), tok, "channels.list")
    items = ch.get("items") or []
    if not items: sys.exit("signed in, but no channel on this account (create it in YouTube Studio first)")
    cid, branding = items[0]["id"], items[0].get("brandingSettings", {})
    print(f"channel {cid}")

    banner = api("POST", f"{UPLOAD}/channelBanners/insert?uploadType=media", tok, "channelBanners.insert", open(a.banner, "rb").read(), image_type(a.banner))
    url = banner.get("url")
    if not url: sys.exit("channelBanners.insert answered without a url: " + json.dumps(banner)[:300])
    print(f"banner uploaded: {url}")

    channel = dict(branding.get("channel", {}))
    channel.update({"description": description, "keywords": keywords, "defaultLanguage": "en"})
    body = {"id": cid, "brandingSettings": dict(branding, channel=channel, image={"bannerExternalUrl": url})}
    api("PUT", f"{API}/channels?part=brandingSettings", tok, "channels.update", json.dumps(body).encode())
    print("description, keywords, language and banner set")

    data, kind = multipart_related(WATERMARK, open(a.watermark, "rb").read(), image_type(a.watermark))
    api("POST", f"{UPLOAD}/watermarks/set?" + urllib.parse.urlencode({"channelId": cid, "uploadType": "multipart"}), tok, "watermarks.set", data, kind, ok=(200, 204))
    print("watermark set: the last 15 s of every video, bottom right")
    print("\nleft for YouTube Studio: the profile picture (build/brand/avatar-<a|b>-youtube.png), the links, the handle, the trailer.")

if __name__ == "__main__":
    main()
