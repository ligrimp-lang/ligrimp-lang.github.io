#!/usr/bin/env python3
"""Publish one episode's short cut to Instagram as a Reel, through Meta's Instagram Graph API on the Facebook-login route (host
graph.facebook.com): the account's Instagram professional profile is linked to a Facebook Page, and the Page's access token publishes
to the Instagram account behind it. tools/instagram-auth.py makes the credentials (Meta's dashboard offered no Instagram-login
set-up, 2026-10-29). Standard library only, like every tool in this repository.

    publish-instagram.py <slug> --video-url https://diver.today/video/<file>.mp4 [--caption-file path] [--dry-run]

Instagram takes no upload: it fetches the video from a public https address. So the short cut (build/pilot/<slug>-short.mp4, 1080×1920,
rendered by tools/pilot-episode.py) is put on diver.today first, which is not this script's job, and its address is passed here. The
caption comes from CAPTIONS below, one entry per episode: the question, a line on the answer, the worked example marked as one, the app
and diver.today, hashtags. --caption-file replaces it (also for an episode not yet in the table). The reserve is called minimum gas.

What it does, in order, with the Page access token:
  1. looks at the credentials' "obtained" date: 50 days old or more, or missing, and it warns that the token must be renewed with
     tools/instagram-auth.py (a new short-lived token from the Graph API Explorer, then `exchange` again). There is no refresh call
     on this route, so nothing is refreshed and the run goes on with the token it has; the user token behind it lasts about 60 days,
     after which every call fails with Meta's message.
  2. GET /{ig_user_id}/content_publishing_limit: how many API posts went out in the rolling 24 hours, against the limit Meta reports
  3. POST /{ig_user_id}/media with media_type=REELS, video_url, caption, share_to_feed=true: a media container
  4. GET /{container}?fields=status_code,status every 10 s until FINISHED (ERROR and EXPIRED stop the run with Meta's message)
  5. POST /{ig_user_id}/media_publish with creation_id=the container
  6. GET /{media}?fields=permalink, and prints the address

--dry-run prints the caption and every call that would be made, the token masked; it touches no network (it reads the credentials
file, if present, for the Instagram account's id and name only).

Credentials: ~/.config/diver-today/instagram.json as tools/instagram-auth.py writes it: {"route": "facebook", "app_id", "app_secret",
"user_access_token", "page_id", "page_name", "page_access_token", "ig_user_id", "ig_username", "obtained": "YYYY-MM-DD"}. This script
never writes it. Nothing here replies, follows, likes or messages: publishing is the only thing the account does by machine (Rustam's
rule; docs/publishing-runbook.md).
"""
import os, sys, json, time, stat, argparse, datetime, urllib.request, urllib.parse, urllib.error

CREDS = os.path.join(os.path.expanduser("~"), ".config", "diver-today", "instagram.json")
GRAPH = "https://graph.facebook.com/v21.0"   # the same host and version as tools/instagram-auth.py
POLL, POLL_LIMIT = 10, 60        # every 10 s, for up to 10 minutes
RENEW_AFTER, LIFETIME = 50, 60   # days: warn from 50; the long-lived user token behind the Page token lasts about 60
CAPTION_LIMIT, HASHTAG_LIMIT = 2200, 30
SITE = "diver.today"
NEVER = ("rock bottom", "rock-bottom", "rockbottom")   # the reserve is minimum gas and nothing else (Rustam, 2026-10-28)

# One entry per episode, from the episode's words (tools/pilot-episode.py, EPISODES). Links in a caption are not clickable, so the
# site is named and the link is the one in the bio. No claim about an app beyond its App Store listing.
CAPTIONS = {
 "gas-for-the-dive": (
  "How much gas does your dive need?\n\n"
  "Remember a cat: C × A × T. C is your consumption, the SAC rate: what you breathe in a minute at the surface. A is the pressure at "
  "your average depth: one bar at the surface, plus one for every ten metres. T is the time of the dive. Multiply, then divide by the "
  "size of your cylinder to get bar.\n\n"
  "A worked example with made-up numbers, not your dive: 15 litres a minute × 3 bar at 20 m × 40 minutes = 1,800 litres; from a "
  "12-litre cylinder, 150 bar for the dive. Your minimum gas comes on top.\n\n"
  f"Turn Pressure works out both for the dive you are planning. Free on the App Store. More at {SITE}, link in bio.\n\n"
  "#scuba #scubadiving #diving #divetraining #gasplanning #sacrate #minimumgas #diveplanning #divetheory #openwaterdiver "
  "#turnpressure #divertoday"),
 "sac-rate": (
  "What is your SAC rate?\n\n"
  "It is what you breathe in a minute at the surface, the C in C × A × T, and you get it from a dive you have done: the gas you used, "
  "how long it took, and the average depth your computer recorded. Litres used over the minutes gives litres a minute at depth; divide "
  "by the pressure at that depth and it is back at the surface.\n\n"
  "A worked example with made-up numbers, not your dive: 120 bar from a 12-litre cylinder is 1,440 litres; over 40 minutes, 36 litres "
  "a minute; at an average depth of 14 m, which is 2.4 bar, that is 15 litres a minute at the surface. Do it for a few dives and use "
  "the average.\n\n"
  f"Dive log works it out from each dive's profile and pressures, and draws it over time. Free on the App Store. More at {SITE}, link in bio.\n\n"
  "#scuba #scubadiving #diving #divetraining #sacrate #gasplanning #divelog #divelogbook #divecomputer #divetheory #openwaterdiver "
  "#divertoday"),
 "minimum-gas": (
  "What is minimum gas?\n\n"
  "At the deepest point your buddy signals: out of gas. You share, and you both go up. Minimum gas is what must be left for that: the "
  "same cat, consumption × pressure × time, for two divers on the way up.\n\n"
  "A worked example, not a minimum gas for your dive; courses differ on the rate for a stressed diver. Two stressed divers at 20 litres "
  "a minute each, a minute at 30 m to sort it out: 160 litres. Then the ascent at 9 m a minute: about 330 litres. Nearly 500 litres "
  "together; from an 11-litre cylinder, 45 bar. When your gauge gets there, the dive is over, whatever the plan said.\n\n"
  f"Turn Pressure works out minimum gas, and the turn pressure, for the dive you are planning. Free on the App Store. The written "
  f"answer is at {SITE}/minimum-gas, link in bio.\n\n"
  "#scuba #scubadiving #diving #divetraining #minimumgas #gasplanning #gasmanagement #sacrate #diveplanning #divetheory #turnpressure "
  "#divertoday"),
}

# ---------- the pieces ----------

class GraphError(Exception): pass

def graph(method, path, params, token):
    """One call to the Graph API, the token in the parameters; Meta's error message becomes the exception text (never the token)."""
    data = urllib.parse.urlencode(dict(params, access_token=token)).encode()
    url = f"{GRAPH}/{path}"
    req = urllib.request.Request(url if method == "POST" else url + "?" + data.decode(), data=data if method == "POST" else None, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r: return json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        try:
            err = json.loads(body)["error"]
            msg = f"{err.get('message')} (code {err.get('code')}, subcode {err.get('error_subcode')}, trace {err.get('fb_trace_id')})"
        except Exception:
            msg = body[:400]
        raise GraphError(f"{method} /{path} failed ({e.code}): {msg}")
    except (urllib.error.URLError, OSError) as e:
        raise GraphError(f"{method} /{path}: {e}")

def load_creds():
    if not os.path.exists(CREDS): sys.exit(f"no credentials at {CREDS}; make them with tools/instagram-auth.py exchange <token>")
    if stat.S_IMODE(os.stat(CREDS).st_mode) & 0o077: print(f"warning: {CREDS} is readable by others; chmod 600 it")
    c = json.load(open(CREDS))
    if c.get("route") != "facebook": print(f"warning: the credentials say route {c.get('route')!r}; this script publishes by the facebook route")
    missing = [k for k in ("ig_user_id", "page_access_token") if not c.get(k)]
    if missing: sys.exit(f"{CREDS} lacks {', '.join(missing)}; run tools/instagram-auth.py exchange <token> again")
    return c

def token_age(c):
    """Days since the credentials were obtained, or None when the file does not say."""
    try: return (datetime.date.today() - datetime.date.fromisoformat(c["obtained"])).days
    except (KeyError, ValueError, TypeError): return None

def token_warning(c):
    """No refresh call exists on this route: the token is renewed by hand with tools/instagram-auth.py. Say so when it is time."""
    age = token_age(c)
    renew = "renew it with tools/instagram-auth.py: a new token from the Graph API Explorer, then `exchange` again"
    if age is None: print(f"warning: no 'obtained' date in {CREDS}, so the token's age is unknown; {renew} if this run fails")
    elif age >= LIFETIME: print(f"warning: the token was obtained {age} days ago and has most likely expired ({LIFETIME} days); {renew}")
    elif age >= RENEW_AFTER: print(f"warning: the token was obtained {age} days ago; it lasts about {LIFETIME}; {renew}")
    else: print(f"token: obtained {age} days ago" + (f" ({c['ig_username']})" if c.get("ig_username") else ""))

def reachable(url):
    """Instagram fetches the file itself; a dead address fails later with an opaque message, so look first."""
    for method, headers in (("HEAD", {}), ("GET", {"Range": "bytes=0-0"})):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers, method=method), timeout=30) as r:
                kind = r.headers.get("Content-Type", "")
                if not kind.startswith("video/"): print(f"warning: {url} is served as {kind or 'no content type'}, not video/mp4")
                return True
        except urllib.error.HTTPError as e:
            if e.code in (403, 405) and method == "HEAD": continue
            sys.exit(f"{url} answers {e.code}; the Reel must sit at a public https address before Instagram can fetch it")
        except (urllib.error.URLError, OSError) as e:
            sys.exit(f"{url} is not reachable: {e}")
    return True

def publishing_limit(ig_user_id, token):
    try:
        r = graph("GET", f"{ig_user_id}/content_publishing_limit", {"fields": "quota_usage,config"}, token)
        d = (r.get("data") or [{}])[0]; used, total = d.get("quota_usage"), (d.get("config") or {}).get("quota_total")
        print(f"publishing limit: {used} of {total} API posts used in the rolling 24 hours")
        if used is not None and total is not None and used >= total: sys.exit("the 24-hour publishing limit is used up; try later")
    except GraphError as e:
        print(f"publishing limit not read ({e}); carrying on")

def check(caption):
    problems = []
    if len(caption) > CAPTION_LIMIT: problems.append(f"caption is {len(caption)} characters; the limit is {CAPTION_LIMIT}")
    tags = [w for w in caption.split() if w.startswith("#")]
    if len(tags) > HASHTAG_LIMIT: problems.append(f"{len(tags)} hashtags; the limit is {HASHTAG_LIMIT}")
    for term in NEVER:
        if term in caption.lower(): problems.append(f"'{term}' is in the caption; the reserve is called minimum gas")
    if "!" in caption: problems.append("an exclamation mark; the house style has none")
    return problems

# ---------- the run ----------

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog="Episodes: " + ", ".join(CAPTIONS))
    ap.add_argument("slug", help="the episode, an entry of CAPTIONS (or any name with --caption-file)")
    ap.add_argument("--video-url", required=True, metavar="https://...", help="the public https address of the short cut")
    ap.add_argument("--caption-file", metavar="PATH", help="a caption from a file instead of the table")
    ap.add_argument("--dry-run", action="store_true", help="print what would be sent; no network")
    a = ap.parse_args()

    if a.caption_file: caption = open(a.caption_file, encoding="utf-8").read().strip()
    elif a.slug in CAPTIONS: caption = CAPTIONS[a.slug]
    else: sys.exit(f"no caption for {a.slug!r}; add an entry to CAPTIONS or pass --caption-file (episodes: {', '.join(CAPTIONS)})")
    problems = check(caption)
    if problems: sys.exit("not sent:\n  " + "\n  ".join(problems))
    if not a.video_url.startswith("https://"): sys.exit("--video-url must be a public https address")

    if a.dry_run:
        c = json.load(open(CREDS)) if os.path.exists(CREDS) else {}
        uid = c.get("ig_user_id", "<ig_user_id>")
        print(f"dry run: {a.slug}" + (f", to {c['ig_username']}" if c.get("ig_username") else "") + ". Nothing is sent.\n\n"
              f"caption ({len(caption)} characters):\n{caption}\n")
        print("1. ", end=""); token_warning(c) if c else print("token: no credentials file here; the run would stop")
        print(f"2. GET  {GRAPH}/{uid}/content_publishing_limit?fields=quota_usage,config&access_token=***")
        print(f"3. POST {GRAPH}/{uid}/media  media_type=REELS  video_url={a.video_url}  share_to_feed=true  caption=(above)  access_token=***")
        print(f"4. GET  {GRAPH}/<container>?fields=status_code,status  every {POLL} s until FINISHED (up to {POLL * POLL_LIMIT // 60} min)")
        print(f"5. POST {GRAPH}/{uid}/media_publish  creation_id=<container>")
        print(f"6. GET  {GRAPH}/<media>?fields=permalink")
        return

    c = load_creds()
    token_warning(c)
    uid, token = c["ig_user_id"], c["page_access_token"]
    reachable(a.video_url)
    publishing_limit(uid, token)
    try:
        r = graph("POST", f"{uid}/media", {"media_type": "REELS", "video_url": a.video_url, "caption": caption, "share_to_feed": "true"}, token)
        container = r["id"]; print(f"container {container}; waiting for Instagram to fetch and process the video", flush=True)
        for n in range(POLL_LIMIT):
            time.sleep(POLL)
            s = graph("GET", f"{container}", {"fields": "status_code,status"}, token)
            code = s.get("status_code"); print(f"  {(n + 1) * POLL:4d} s  {code}", flush=True)
            if code == "FINISHED": break
            if code in ("ERROR", "EXPIRED"): sys.exit(f"container {container} ended in {code}: {s.get('status', 'no message')}")
        else:
            sys.exit(f"container {container} still {code} after {POLL * POLL_LIMIT // 60} minutes; publish it later with media_publish or make a new one")
        m = graph("POST", f"{uid}/media_publish", {"creation_id": container}, token)
        media = m["id"]
        p = graph("GET", f"{media}", {"fields": "permalink"}, token)
    except GraphError as e:
        sys.exit(str(e))
    print(f"\nreel published: media {media}\n  {p.get('permalink', '(no permalink in the answer)')}")

if __name__ == "__main__":
    main()
