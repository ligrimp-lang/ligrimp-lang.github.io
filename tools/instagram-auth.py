#!/usr/bin/env python3
"""The one-time step that turns a Facebook login into the Instagram publishing credentials, and a check. Standard library only.

The account's Instagram professional profile is linked to a Facebook Page, and the Meta app uses "API setup with Facebook login"
(Meta's dashboard offered Rustam's developer account no Instagram-login setup, 2026-10-29). A short-lived user token comes from the
Graph API Explorer (developers.facebook.com/tools/explorer: the app, the permissions, Generate Access Token); this script makes it
last and finds the Instagram account behind the Page.

    instagram-auth.py exchange <short-lived user token>     needs app_id and app_secret already in the file (written by hand, mode 600)
    instagram-auth.py adopt <long-lived user token>          the same, for a token already made long-lived by Meta's Access Token Debugger
                                                            ("Extend Access Token"), so no app secret is needed
    instagram-auth.py check                                 prints the Instagram username and id the credentials reach

The file is ~/.config/diver-today/instagram.json (outside every repository), after exchange:
    {"route": "facebook", "app_id", "app_secret", "user_access_token" (long-lived, about 60 days), "page_id", "page_name",
     "page_access_token" (does not expire while the user token is valid), "ig_user_id", "ig_username", "obtained": "YYYY-MM-DD"}
Publishing goes to https://graph.facebook.com/<version>/<ig_user_id>/media with the page access token.
"""
import datetime, json, os, sys, urllib.parse, urllib.request

PATH = os.path.join(os.path.expanduser("~"), ".config", "diver-today", "instagram.json")
GRAPH = "https://graph.facebook.com/v21.0"

def get(path, params):
    with urllib.request.urlopen(GRAPH + path + "?" + urllib.parse.urlencode(params)) as r: return json.load(r)

def save(d):
    fd = os.open(PATH, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f: json.dump(d, f, indent=1)

if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else ""
    d = json.load(open(PATH)) if os.path.exists(PATH) else {}
    if what in ("exchange", "adopt"):
        if what == "exchange":
            if not d.get("app_id") or not d.get("app_secret"): sys.exit("put app_id and app_secret into " + PATH + " first")
            long_ = get("/oauth/access_token", {"grant_type": "fb_exchange_token", "client_id": d["app_id"], "client_secret": d["app_secret"], "fb_exchange_token": sys.argv[2]})
            user_token = long_["access_token"]
        else:
            user_token = sys.argv[2]
        pages = get("/me/accounts", {"fields": "id,name,access_token,instagram_business_account", "access_token": user_token}).get("data", [])
        linked = [p for p in pages if p.get("instagram_business_account")]
        if not linked: sys.exit("no Page with an Instagram professional account linked; pages seen: " + ", ".join(p["name"] for p in pages))
        page = linked[0]
        ig = get("/" + page["instagram_business_account"]["id"], {"fields": "id,username", "access_token": page["access_token"]})
        d.update({"route": "facebook", "user_access_token": user_token, "page_id": page["id"], "page_name": page["name"], "page_access_token": page["access_token"],
                  "ig_user_id": ig["id"], "ig_username": ig["username"], "obtained": datetime.date.today().isoformat()})
        save(d); print("saved:", PATH, "| page:", page["name"], "| instagram:", ig["username"])
    elif what == "check":
        ig = get("/" + d["ig_user_id"], {"fields": "id,username,media_count,followers_count", "access_token": d["page_access_token"]})
        print("instagram:", ig["username"], "| id:", ig["id"], "| media:", ig.get("media_count"), "| followers:", ig.get("followers_count"))
    else:
        sys.exit(__doc__)
