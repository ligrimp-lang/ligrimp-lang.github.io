# diver.today

One page for the five dive apps: Turn Pressure, Time to Surface, Weights Check, Surface
Interval and Dive log. A full-width video of each app in action, one line on what it does,
and its App Store link. Served by GitHub Pages from `main` / root (`ligrimp-lang/ligrimp-lang.github.io`, the account's user site, so the per-app sites are served under diver.today too),
custom domain `diver.today` (the `CNAME` file). No build step: `index.html`, `style.css`
and the files under `img/` and `video/` are the site.

## The media is generated, not drawn by hand

`tools/build-media.py` makes every icon, poster and video from the app repositories beside
this one — the App Store screenshots each app's ship tooling captures, their approved
captions, and the icon from each asset catalogue:

    python3 tools/build-media.py bg        # the shared blurred-reef background (once)
    python3 tools/build-media.py icons     # img/<app>.png, favicon, og.png
    python3 tools/build-media.py videos    # video/<app>-1080.mp4, -720.mp4, img/<app>-poster.jpg

Needs `ffmpeg` and Pillow (both on this Mac). `build/` is scratch and ignored. To refresh an
app's video after new screenshots: rerun `videos <app-slug>`, commit, push.

## Publishing

    git add -A && git commit -m "…" && git push

GitHub Pages redeploys within a minute. DNS at Namecheap: four `A` records on `@` to
185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153, and a `CNAME` on `www`
to `ligrimp-lang.github.io`.

---

© 2026 Rustam Ismailov. All rights reserved. The text and design here are published so
divers can read them, not as an open-source release.
