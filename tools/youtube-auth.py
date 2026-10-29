#!/usr/bin/env python3
"""The one-time sign-in that gives the publishing scripts their YouTube token, and a check that it works. Standard library only.

    youtube-auth.py url               print Google's consent address: open it in the browser signed in as the channel's account and grant
    youtube-auth.py exchange <url>    the address the browser lands on after the grant (http://127.0.0.1:8765/?code=...), exchanged for
                                      a refresh token, saved beside the client file
    youtube-auth.py check             refresh an access token and print the channel's name, as proof

The client file is the OAuth "Desktop app" client's JSON from the Google Cloud console, at ~/.config/diver-today/youtube-client.json
(outside every repository; the token lands next to it as youtube-token.json, mode 600). The redirect goes to a loopback address with
nothing listening: the browser shows an error page, and the address it shows carries the code. No local server is run.
"""
import json, os, sys, urllib.parse, urllib.request

HOME = os.path.join(os.path.expanduser("~"), ".config", "diver-today")
CLIENT, TOKEN = os.path.join(HOME, "youtube-client.json"), os.path.join(HOME, "youtube-token.json")
REDIRECT = "http://127.0.0.1:8765/"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.force-ssl",
          "https://www.googleapis.com/auth/yt-analytics.readonly"]

def client():
    c = json.load(open(CLIENT))
    return c.get("installed") or c.get("web")

def post(url, data):
    req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(), headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req) as r: return json.load(r)

def access_token():
    c, t = client(), json.load(open(TOKEN))
    return post(c["token_uri"], {"client_id": c["client_id"], "client_secret": c["client_secret"], "refresh_token": t["refresh_token"],
                                 "grant_type": "refresh_token"})["access_token"]

def get(url, params):
    req = urllib.request.Request(url + "?" + urllib.parse.urlencode(params), headers={"Authorization": "Bearer " + access_token()})
    with urllib.request.urlopen(req) as r: return json.load(r)

if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else ""
    if what == "url":
        c = client()
        print(c["auth_uri"] + "?" + urllib.parse.urlencode({"client_id": c["client_id"], "redirect_uri": REDIRECT, "response_type": "code",
              "scope": " ".join(SCOPES), "access_type": "offline", "prompt": "consent", "include_granted_scopes": "true"}))
    elif what == "exchange":
        q = urllib.parse.parse_qs(urllib.parse.urlparse(sys.argv[2]).query)
        if "code" not in q: sys.exit("no code in that address: " + ", ".join(q))
        c = client()
        t = post(c["token_uri"], {"code": q["code"][0], "client_id": c["client_id"], "client_secret": c["client_secret"],
                                  "redirect_uri": REDIRECT, "grant_type": "authorization_code"})
        if "refresh_token" not in t: sys.exit("no refresh token came back (grant again with the consent prompt); keys: " + ", ".join(t))
        fd = os.open(TOKEN, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as f: json.dump({"refresh_token": t["refresh_token"], "scope": t.get("scope", "")}, f)
        print("token saved:", TOKEN)
    elif what == "check":
        ch = get("https://www.googleapis.com/youtube/v3/channels", {"part": "snippet,statistics", "mine": "true"})
        for item in ch.get("items", []):
            print("channel:", item["snippet"]["title"], "| videos:", item["statistics"].get("videoCount"), "| subscribers:", item["statistics"].get("subscriberCount"))
        if not ch.get("items"): print("signed in, but no channel on this account yet (create it in YouTube Studio)")
    else:
        sys.exit(__doc__)
