#!/usr/bin/env python3
"""Upload one episode of the question engine to YouTube: the video, its thumbnail, its captions and, if asked, a playlist entry.
Standard library only, like every tool in this repository.

    publish-youtube.py <slug> [--cut wide|short] [--file path] [--thumb path] [--privacy private|unlisted|public]
                       [--schedule 2026-11-03T09:00:00Z] [--playlist id] [--video-id id] [--dry-run]

The episodes are those of tools/pilot-episode.py, which renders build/pilot/<slug>-wide.mp4 (1920×1080, for YouTube and the page),
<slug>-short.mp4 (1080×1920, a Short), <slug>-thumb.png and <slug>.srt (the captions). Title, description and tags come from METADATA
below, one entry per episode, written from the episode's words: the question, the worked example, the app it ends on with its App Store
link and diver.today, and Apple's credit lines at the end, as on the outro. A new episode is a new entry. For --cut short the title gets
"#Shorts" added. Nothing is claimed about an app beyond its App Store listing, and the reserve is called minimum gas.

What it does, in order (the quota cost in brackets; the project has 10,000 units a day):
  1. videos.insert [1,600]: a resumable upload in 8 MiB chunks, taken up again from where it stopped after a network error; parts
     snippet and status, privacyStatus private unless --privacy says otherwise, selfDeclaredMadeForKids false, categoryId 27
     (Education), defaultLanguage en, and publishAt from --schedule (which YouTube allows only with private)
  2. thumbnails.set [50] with the thumb PNG, for the wide cut only (a Short takes its own frame)
  3. captions.insert [400] with the .srt, language en, name "English"
  4. playlistItems.insert [50] when --playlist names a playlist
Then it prints the video id, the watch address and the YouTube Studio address.

Private until the audit. A video uploaded through the API by a project that has not passed YouTube's API compliance audit is locked
to private whatever privacyStatus or publishAt asks; the upload succeeds and YouTube says so by e-mail. Until the audit passes, Rustam
sets each video public, or schedules it, in YouTube Studio. The script sends what it was asked all the same, so nothing here changes on
the day the audit passes.

--dry-run prints the metadata and every call that would be made; it touches no network and reads no credentials.
--video-id skips the upload and does steps 2 to 4 for a video that is already up (after a failed thumbnail or captions call:
uploading again would make a second video).

Credentials: ~/.config/diver-today/youtube-client.json and youtube-token.json, made by tools/youtube-auth.py, which this script imports
for the access token. The scopes granted there are youtube.upload, youtube.force-ssl (captions and playlists need it) and yt-analytics.readonly.
"""
import os, sys, json, time, uuid, argparse, datetime, importlib.util, urllib.request, urllib.parse, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PILOT = os.path.join(ROOT, "build", "pilot")
SITE = "https://diver.today"
UPLOAD = "https://www.googleapis.com/upload/youtube/v3"
API = "https://www.googleapis.com/youtube/v3"
CHUNK = 8 * 1024 * 1024      # a multiple of 256 KiB, as the resumable protocol asks
RETRIES = 6                  # after a network error or a 5xx: 2, 4, 8, 16, 32, 64 s, then give up
THUMB_LIMIT = 2 * 1024 * 1024  # YouTube's limit on a thumbnail file
CUTS = {"wide": "wide", "short": "short"}
PRIVACY = ("private", "unlisted", "public")

# The apps an episode can end on: name, App Store id (CLAUDE.md, "The apps on the page").
APPS = {"turn-pressure": ("Turn Pressure", "6801749776"), "dive-log": ("Dive log", "6822452235")}
# App Store campaign links (pt = the provider token from App Store Connect, ct = the channel, one token per channel as the proposal
# decided). The provider token is not in this repository: set DIVER_TODAY_PT in the environment and every store link carries it;
# unset, the links are plain.
PROVIDER_TOKEN = os.environ.get("DIVER_TODAY_PT", "")
CREDIT = ("Apple and the Apple logo are trademarks of Apple Inc., registered in the U.S. and other countries. "
          "App Store is a service mark of Apple Inc., registered in the U.S. and other countries.")
WORKED = "A worked example with made-up numbers, not your dive."

def store_link(app, channel="youtube"):
    name, app_id = APPS[app]
    link = f"https://apps.apple.com/app/id{app_id}"
    return link + ("?" + urllib.parse.urlencode({"pt": PROVIDER_TOKEN, "ct": channel, "mt": "8"}) if PROVIDER_TOKEN else "")

# One entry per episode. {store} and {site} are filled in at run time. The words are the episode's (tools/pilot-episode.py, EPISODES);
# the app paragraph repeats what its listing and the diver.today page say, no more. YouTube's limits: title 100 characters, description
# 5,000 bytes, tags 500 characters in all; check() enforces them before anything is sent.
METADATA = {
 "gas-for-the-dive": dict(app="turn-pressure",
  title="How much gas does your dive need? Remember a cat: C × A × T",
  description=(
   "You are planning a dive, say forty minutes at around twenty metres. Will the gas on your back cover it? Divers work that out with a "
   "cat: C × A × T.\n\n"
   "C is your consumption, your SAC rate: what you breathe in a minute at the surface. A is the pressure at your average depth: one bar at "
   "the surface, plus one for every ten metres. T is the time of the dive.\n\n"
   f"{WORKED} 15 litres a minute × 3 bar at 20 m × 40 minutes = 1,800 litres. Your gauge reads bar, so divide by the size of your cylinder: "
   "from a 12-litre cylinder that is 150 bar for the dive. Your minimum gas comes on top.\n\n"
   "Turn Pressure works out both for the dive you are planning: the gas for the dive, and the minimum gas to keep. A recreational scuba gas "
   "planner and no-deco calculator, with your own SAC rate. Free, offline, no account.\n"
   "Turn Pressure on the App Store: {store}\n\n"
   "More answers for divers, and the five apps: {site}\n\n"
   "#scuba #diving #gasplanning\n\n"
   "© Rustam Ismailov\n" + CREDIT),
  tags=["scuba diving", "gas planning", "how much gas for a dive", "SAC rate", "dive planning", "cylinder pressure", "minimum gas",
        "scuba gas planner", "Turn Pressure", "dive theory", "diver.today"]),
 "sac-rate": dict(app="dive-log",
  title="What is your SAC rate? Work it out from a dive you have done",
  description=(
   "Every gas plan starts with your SAC rate: what you breathe in a minute, at the surface. It is the C in C × A × T, the cat that gives "
   "the gas a dive needs, and you get it from a dive you have done.\n\n"
   "Three things from that dive: the gas you used, how long it took, and the average depth your computer recorded.\n\n"
   f"{WORKED} 120 bar used from a 12-litre cylinder is 1,440 litres; over 40 minutes, 36 litres a minute at depth. At an average depth of "
   "14 m the pressure was 2.4 bar, so you breathed 2.4 times the gas: 36 ÷ 2.4, and your SAC rate is 15 litres a minute. Do it for a few "
   "dives and use the average.\n\n"
   "Dive log works it out from each dive's profile and pressures, and draws it over time. A Shearwater dive log app for iPhone: import your "
   "dives once, over Bluetooth, into a dive logbook, with your SAC per dive and over time. Free, private, no account.\n"
   "Dive log on the App Store: {store}\n\n"
   "More answers for divers, and the five apps: {site}\n\n"
   "#scuba #diving #sacrate\n\n"
   "© Rustam Ismailov\n" + CREDIT),
  tags=["scuba diving", "SAC rate", "surface air consumption", "gas planning", "dive log", "dive logbook", "Shearwater", "dive computer",
        "Dive log app", "dive theory", "diver.today"]),
 "minimum-gas": dict(app="turn-pressure",
  title="What is minimum gas? The same cat, for two divers on the way up",
  description=(
   "At the deepest point your buddy signals: out of gas. You share, and you both go up. How much must be left for that? That is minimum "
   "gas.\n\n"
   "Work it out with the cat: consumption × pressure × time, for two divers on the way up.\n\n"
   "A worked example, not a minimum gas for your dive; courses differ on the rate for a stressed diver. Two stressed divers at 20 litres a "
   "minute each is 40 litres a minute. A minute at 30 m, which is 4 bar, to sort it out: 160 litres. Then the ascent at 9 m a minute, "
   "3.3 minutes at 2.5 bar on average: about 330 litres. Nearly 500 litres together; from an 11-litre cylinder, 45 bar. When your gauge "
   "gets there, the dive is over, whatever the plan said.\n\n"
   "The written answer, with the method step by step: {site}/minimum-gas/\n\n"
   "Turn Pressure works out minimum gas for the dive you are planning, and the turn pressure: when to turn the dive. A recreational scuba "
   "gas planner and no-deco calculator, with your own SAC rate. Free, offline, no account.\n"
   "Turn Pressure on the App Store: {store}\n\n"
   "More answers for divers, and the five apps: {site}\n\n"
   "#scuba #diving #minimumgas\n\n"
   "© Rustam Ismailov\n" + CREDIT),
  tags=["scuba diving", "minimum gas", "gas planning", "gas sharing", "out of gas", "ascent", "turn pressure", "SAC rate",
        "scuba gas planner", "Turn Pressure", "dive theory", "diver.today"]),
}
NEVER = ("rock bottom", "rock-bottom", "rockbottom")   # the reserve is minimum gas and nothing else (Rustam, 2026-10-28)

# ---------- the pieces ----------

spec = importlib.util.spec_from_file_location("youtube_auth", os.path.join(HERE, "youtube-auth.py"))
auth = importlib.util.module_from_spec(spec); spec.loader.exec_module(auth)

class Token:
    """One access token for the run, refreshed from the saved refresh token when YouTube answers 401."""
    def __init__(self): self.value = None
    def get(self):
        if self.value is None: self.value = auth.access_token()
        return self.value
    def refresh(self): self.value = None; return self.get()

class NoRedirect(urllib.request.HTTPRedirectHandler):
    """urllib would follow a 308; the resumable protocol uses 308 to mean "carry on", so redirects are left alone."""
    def redirect_request(self, req, fp, code, msg, headers, newurl): return None
OPENER = urllib.request.build_opener(NoRedirect)

def call(method, url, data=None, headers=None, token=None, timeout=120):
    """One HTTP call: (status, headers, body). An HTTP error is a status, not an exception; a network error raises."""
    h = dict(headers or {})
    if token: h["Authorization"] = "Bearer " + token
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with OPENER.open(req, timeout=timeout) as r: return r.status, r.headers, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.headers, e.read()

def reason(body):
    try: return json.loads(body)["error"]["message"]
    except Exception: return body.decode(errors="replace")[:400]

def json_call(method, url, obj, tok, what):
    st, h, body = call(method, url, json.dumps(obj).encode(), {"Content-Type": "application/json; charset=UTF-8"}, tok.get())
    if st == 401:
        st, h, body = call(method, url, json.dumps(obj).encode(), {"Content-Type": "application/json; charset=UTF-8"}, tok.refresh())
    if st >= 300: raise RuntimeError(f"{what} failed ({st}): {reason(body)}")
    return json.loads(body) if body else {}

def media_call(url, data, content_type, tok, what):
    st, h, body = call("POST", url, data, {"Content-Type": content_type}, tok.get(), timeout=300)
    if st == 401:
        st, h, body = call("POST", url, data, {"Content-Type": content_type}, tok.refresh(), timeout=300)
    if st >= 300: raise RuntimeError(f"{what} failed ({st}): {reason(body)}")
    return json.loads(body) if body else {}

def multipart_related(meta, media, media_type):
    b = uuid.uuid4().hex
    body = (f"--{b}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n{json.dumps(meta)}\r\n"
            f"--{b}\r\nContent-Type: {media_type}\r\n\r\n").encode() + media + f"\r\n--{b}--\r\n".encode()
    return body, f"multipart/related; boundary={b}"

def resume_point(session, size, tok):
    """Ask the upload session how far it got: (bytes the server has, finished video or None). 404 means the session is gone."""
    try:
        st, h, body = call("PUT", session, b"", {"Content-Range": f"bytes */{size}"}, tok.get(), timeout=60)
    except (urllib.error.URLError, OSError):
        return None, None
    if st in (200, 201): return size, json.loads(body)
    if st == 308:
        r = h.get("Range"); return (int(r.split("-")[1]) + 1 if r else 0), None
    if st == 404: sys.exit("the upload session expired on YouTube's side; run the command again")
    return None, None

def upload(path, snippet, status, tok):
    """videos.insert as a resumable upload: start a session, PUT the file in chunks, pick up where it stopped after an error."""
    size = os.path.getsize(path)
    start = f"{UPLOAD}/videos?" + urllib.parse.urlencode({"uploadType": "resumable", "part": "snippet,status"})
    meta = json.dumps({"snippet": snippet, "status": status}).encode()
    head = {"Content-Type": "application/json; charset=UTF-8", "X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(size)}
    st, h, body = call("POST", start, meta, head, tok.get())
    if st == 401: st, h, body = call("POST", start, meta, head, tok.refresh())
    if st != 200: sys.exit(f"could not start the upload ({st}): {reason(body)}")
    session = h["Location"]
    sent, tries = 0, 0
    with open(path, "rb") as f:
        while True:
            f.seek(sent); chunk = f.read(CHUNK); end = sent + len(chunk) - 1
            try:
                st, h, body = call("PUT", session, chunk, {"Content-Type": "video/mp4", "Content-Range": f"bytes {sent}-{end}/{size}"},
                                   tok.get(), timeout=600)
            except (urllib.error.URLError, OSError) as e:
                st, h, body = None, {}, repr(e).encode()
            if st in (200, 201): return json.loads(body)
            if st == 308:
                r = h.get("Range"); sent = int(r.split("-")[1]) + 1 if r else 0; tries = 0
                print(f"  {sent * 100 // size:3d}%  {sent:,} of {size:,} bytes", flush=True); continue
            if st == 404: sys.exit("the upload session expired on YouTube's side; run the command again")
            if st is not None and st < 500 and st not in (401, 408, 429):
                sys.exit(f"upload failed ({st}): {reason(body)}")
            tries += 1   # a network error, a 5xx, 401, 408 or 429: wait, ask where the server got to, carry on from there
            if tries > RETRIES: sys.exit(f"upload failed after {RETRIES} retries: {reason(body)}")
            print(f"  upload interrupted ({st if st is not None else reason(body)}); retry {tries} in {2 ** tries} s", flush=True)
            time.sleep(2 ** tries)
            if st == 401: tok.refresh()
            at, done = resume_point(session, size, tok)
            if done: return done
            if at is not None: sent = at

def set_thumbnail(video_id, thumb, tok):
    kind = "image/png" if thumb.lower().endswith(".png") else "image/jpeg"
    url = f"{UPLOAD}/thumbnails/set?" + urllib.parse.urlencode({"videoId": video_id, "uploadType": "media"})
    return media_call(url, open(thumb, "rb").read(), kind, tok, "thumbnails.set")

def insert_captions(video_id, srt, tok):
    meta = {"snippet": {"videoId": video_id, "language": "en", "name": "English", "isDraft": False}}
    body, kind = multipart_related(meta, open(srt, "rb").read(), "application/octet-stream")
    url = f"{UPLOAD}/captions?" + urllib.parse.urlencode({"uploadType": "multipart", "part": "snippet"})
    return media_call(url, body, kind, tok, "captions.insert")

def add_to_playlist(video_id, playlist, tok):
    body = {"snippet": {"playlistId": playlist, "resourceId": {"kind": "youtube#video", "videoId": video_id}}}
    return json_call("POST", f"{API}/playlistItems?part=snippet", body, tok, "playlistItems.insert")

# ---------- the run ----------

def check(title, description, tags):
    """YouTube's limits and the house rules, before anything is sent."""
    problems = []
    if len(title) > 100: problems.append(f"title is {len(title)} characters; the limit is 100")
    if "<" in title or ">" in title: problems.append("title has < or >, which YouTube rejects")
    if len(description.encode()) > 5000: problems.append(f"description is {len(description.encode())} bytes; the limit is 5,000")
    if "<" in description or ">" in description: problems.append("description has < or >, which YouTube rejects")
    if sum(len(t) for t in tags) + 2 * sum(" " in t for t in tags) > 500: problems.append("tags come to more than 500 characters")
    text = (title + " " + description + " " + " ".join(tags)).lower()
    for term in NEVER:
        if term in text: problems.append(f"'{term}' is in the text; the reserve is called minimum gas")
    if "!" in title or "!" in description: problems.append("an exclamation mark; the house style has none")
    return problems

def schedule_time(s):
    try: when = datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
    except ValueError: sys.exit(f"--schedule wants a UTC time like 2026-11-03T09:00:00Z, not {s!r}")
    if when <= datetime.datetime.now(datetime.timezone.utc): sys.exit(f"--schedule {s} is in the past")
    return s

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog="Episodes: " + ", ".join(METADATA))
    ap.add_argument("slug", help="the episode, an entry of METADATA (and of EPISODES in tools/pilot-episode.py)")
    ap.add_argument("--cut", choices=list(CUTS), default="wide", help="wide (1920×1080, default) or short (1080×1920, a Short: #Shorts in the title)")
    ap.add_argument("--file", help="the video file; default build/pilot/<slug>-<cut>.mp4")
    ap.add_argument("--thumb", help="the thumbnail; default build/pilot/<slug>-thumb.png, wide cut only")
    ap.add_argument("--privacy", choices=PRIVACY, default="private", help="privacyStatus; private by default (and forced private until the API audit)")
    ap.add_argument("--schedule", metavar="2026-11-03T09:00:00Z", help="publishAt, a UTC time; needs --privacy private")
    ap.add_argument("--playlist", metavar="ID", help="add the video to this playlist")
    ap.add_argument("--video-id", metavar="ID", help="skip the upload: thumbnail, captions and playlist for this existing video")
    ap.add_argument("--dry-run", action="store_true", help="print what would be sent; no network, no credentials")
    a = ap.parse_args()

    if a.slug not in METADATA: sys.exit(f"no metadata for {a.slug!r}; add an entry to METADATA (episodes: {', '.join(METADATA)})")
    m = METADATA[a.slug]
    title = m["title"] + (" #Shorts" if a.cut == "short" else "")
    description = m["description"].format(store=store_link(m["app"]), site=SITE)
    tags = list(m["tags"])
    problems = check(title, description, tags)
    if problems: sys.exit("not sent:\n  " + "\n  ".join(problems))
    if a.schedule and a.privacy != "private": sys.exit("--schedule works only with --privacy private (YouTube's rule for publishAt)")
    video = a.file or os.path.join(PILOT, f"{a.slug}-{a.cut}.mp4")
    thumb = (a.thumb or os.path.join(PILOT, f"{a.slug}-thumb.png")) if a.cut == "wide" else None
    srt = os.path.join(PILOT, f"{a.slug}.srt")
    snippet = {"title": title, "description": description, "tags": tags, "categoryId": "27", "defaultLanguage": "en"}
    status = {"privacyStatus": a.privacy, "selfDeclaredMadeForKids": False}
    if a.schedule: status["publishAt"] = schedule_time(a.schedule)

    def exists(p): return p and os.path.exists(p)
    def size(p): return f"{os.path.getsize(p):,} bytes" if exists(p) else "NOT FOUND"

    if a.dry_run:
        print(f"dry run: {a.slug}, {a.cut} cut. Nothing is sent.\n")
        print("snippet:", json.dumps(snippet, indent=2, ensure_ascii=False))
        print("status:", json.dumps(status, indent=2))
        if a.video_id: print(f"\n1. (no upload: --video-id {a.video_id})")
        else: print(f"\n1. POST {UPLOAD}/videos?uploadType=resumable&part=snippet,status, then PUT {video} ({size(video)}) in {CHUNK // 1024 // 1024} MiB chunks")
        if thumb: print(f"2. POST {UPLOAD}/thumbnails/set?videoId=<id>&uploadType=media  <- {thumb} ({size(thumb)})")
        else: print("2. (no thumbnail for the short cut)")
        print(f"3. POST {UPLOAD}/captions?uploadType=multipart&part=snippet  <- {srt} ({size(srt)}), language en, name English")
        print(f"4. POST {API}/playlistItems?part=snippet  playlist {a.playlist}" if a.playlist else "4. (no playlist)")
        print("\nAfter the upload, until the API audit passes, the video is private whatever was asked: set it public in YouTube Studio.")
        return

    if not a.video_id and not exists(video): sys.exit(f"no video at {video}; render it with tools/pilot-episode.py {a.slug} {a.cut}")
    if not exists(srt): print(f"warning: no captions at {srt} (the wide render writes it); captions skipped")
    tok = Token(); failed = []
    if a.video_id:
        video_id = a.video_id; print(f"using the existing video {video_id}")
    else:
        print(f"uploading {video} ({size(video)}) as {a.privacy}" + (f", publishAt {a.schedule}" if a.schedule else ""))
        res = upload(video, snippet, status, tok)
        video_id = res["id"]
        print(f"video id: {video_id}\n  https://www.youtube.com/watch?v={video_id}")
    if thumb:
        if not exists(thumb): print(f"warning: no thumbnail at {thumb}; skipped")
        elif os.path.getsize(thumb) > THUMB_LIMIT:
            print(f"warning: {thumb} is over YouTube's 2 MB limit; make a JPEG (ffmpeg -i {thumb} -q:v 3 {thumb[:-4]}.jpg) and pass it with --thumb"); failed.append("thumbnail")
        else:
            try: set_thumbnail(video_id, thumb, tok); print("thumbnail set")
            except RuntimeError as e: print(e, "\n  (custom thumbnails need a phone-verified channel; set it in YouTube Studio if this keeps failing)"); failed.append("thumbnail")
    if exists(srt):
        try: insert_captions(video_id, srt, tok); print("captions added (English)")
        except RuntimeError as e: print(e); failed.append("captions")
    if a.playlist:
        try: add_to_playlist(video_id, a.playlist, tok); print(f"added to playlist {a.playlist}")
        except RuntimeError as e: print(e); failed.append("playlist")
    print(f"\n{video_id}\n  watch:  https://www.youtube.com/watch?v={video_id}" + (f"\n  short:  https://www.youtube.com/shorts/{video_id}" if a.cut == "short" else "")
          + f"\n  studio: https://studio.youtube.com/video/{video_id}/edit")
    if failed: sys.exit(f"not done: {', '.join(failed)}. Run again with --video-id {video_id} to retry without uploading again.")

if __name__ == "__main__":
    main()
