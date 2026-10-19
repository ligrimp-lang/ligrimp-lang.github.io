# diver.today

One page for Rustam's five dive apps — Turn Pressure, Time to Surface, Weights Check, Surface
Interval and Dive log — with a full-width video of each app in action, its App Store link and one
line on what it is for. Built 2026-10-14 on his brief: *"a single page with full width videos of my
apps in action along with links to apple store … hosting for now shall be free, design shall be
crisp and super modern and without unnecessary elements"*, to bring in new users from forums
and search. **This file is the present tense; read it before changing anything.**

## What is where

| | |
|---|---|
| The page | `index.html` (one file, inline script), `style.css` (`?v=` on its link is the cache-buster: bump it when the CSS changes) |
| Media | `img/` icons at 512, favicon, `og.png` (1200×630), posters; `video/` ten MP4s, `<app>-wide.mp4` (1920×1080, desktops) and `<app>-tall.mp4` (864×1080, 4:5, phones) |
| Generator | `tools/build-media.py` — makes all of `img/` and `video/` from the app repositories beside this one. Needs ffmpeg and Pillow. `build/` is its scratch, git-ignored |
| Hosting | GitHub Pages, repo `ligrimp-lang/ligrimp-lang.github.io` (the account's **user site**, renamed from `divertoday-site` on 2026-10-19 by Rustam's hand; see "Everything under diver.today" below), branch `main`, folder `/`. Push to `main` and it deploys in about a minute. **Everything in this repository is on the web unless `_config.yml` excludes it** — the notes (`CLAUDE.md`, `README.md`, `docs/`), `tools/` and `build/` are excluded there; add any new non-site folder to that list before committing it |
| Domain | `diver.today` at Namecheap. Advanced DNS holds four `A` records on `@` → 185.199.108.153 / .109 / .110 / .111 and `CNAME www` → `ligrimp-lang.github.io` (set by Rustam, 2026-10-14). The `CNAME` file in this repo tells GitHub the domain |
| Search | `robots.txt`, `sitemap.xml`, canonical `https://diver.today/`, JSON-LD `WebSite` + `ItemList` of five `SoftwareApplication`s, Open Graph and Twitter cards |
| Preview | `tools/preview.sh [page-folder]` — screenshots from the files with headless Chrome, desktop and phone width, into `build/preview/`. see "Previewing and publishing" below |
| Question pages | Five articles for Google, one per app, each a folder with its own `index.html`: `weight-for-scuba-diving/`, `minimum-gas-rock-bottom/`, `gradient-factors-explained/`, `blue-gopro-dive-footage/`, `shearwater-dives-on-iphone/`. Linked from the home page under each app and listed in `sitemap.xml`; their CSS is the `/* question pages */` block at the end of `style.css`. See "The question pages" below |
| Promotion | **This project is the home for app promotion** (Rustam, 2026-10-19). Start at `docs/promotion-knowledge.md`: where every number and listing lives, each app's store position, what was learned, what is open, and the weekly loop. Beside it: `docs/promotion-posts-2026-10-15.md` (where to post and the texts, in Rustam's voice, for him to post himself) and `docs/search-findability-proposal-2026-10-19.md` (the proposal that was implemented that day). None of it is on the web |

## Previewing and publishing

Preview a page with `tools/preview.sh [page-folder]`: desktop and phone-width screenshots from the
files, in `build/preview/`. Publish by committing and pushing to `main`; `gh run list -R
ligrimp-lang/ligrimp-lang.github.io --limit 1` shows the deployment, then look at the live page.
This repository is public, CLAUDE.md and `docs/` included, so private working notes stay in the
git-ignored `CLAUDE.local.md`.

## The apps on the page

Rustam chose this order on 2026-10-14 and it is the order on the page, in the header menu, in the
JSON-LD list, in the `APPS` table of the generator and in the share image: Time to Surface, Surface
Interval, Dive log, Turn Pressure, Weights Check. Change all of them together.

The App Store ids, store names and the per-app sites (each app's own repo publishes its landing,
privacy and support pages, which this page links to as "Details, support & privacy"; since 2026-10-19 they
are served under diver.today, the github.io addresses redirect there):

| App | Store name | id | Per-app site |
|---|---|---|---|
| Time to Surface | Time to Surface – Deco Planner | 6803187271 | diver.today/timetosurface-site/ |
| Surface Interval | Surface Interval – Dive Videos (iPhone and Mac, one record) | 6813333816 | diver.today/surfaceinterval-site/ |
| Dive log | Dive log – Computer Logbook | 6822452235 | diver.today/divelog-site/ |
| Turn Pressure | Turn Pressure – Dive Planner | 6801749776 | diver.today/turnpressure-site/ |
| Weights Check | Weights Check – Dive Weighting | 6806640499 | diver.today/weightscheck-site/ |

Verify a listing by opening `https://itunes.apple.com/lookup?id=<id>` rather than from memory.
**Dive log went into App Review on 2026-10-14**; the page shows its button as "Coming soon on the
App Store" (class `soon` on the link, plus the `.note` under it). The link already points at the
store, so when Apple approves it, remove the class and the note — nothing else.

## Words on the page are the apps' approved words

The sentence after the opening phrase is the App Store promotional text
(`docs/app-store-listing*.md` in each app's repo), lightly joined — **except Dive log's**, which
names his six key features in the video's order (Rustam, 2026-10-18, "update the website"); its
listing still has the older promotional text. **The line under each name and
the first words of each paragraph are search wording, no longer the store subtitle** (2026-10-15,
Rustam: searchers type the problem, not the app names). Each leads with what a diver types, taken
from the search research (`weights_check/nimbalyst-local/promotion/search-terms.txt` and
`findability-plan-2026-09-21.md`; `turn_pressure/nimbalyst-local/plans/app-store-findability-2026-09-16.md`
and `-09-21.md`; the Keywords and Subtitle blocks of each listing), with the claims unchanged:

| App | Line under the name | Phrases carried in the paragraph |
|---|---|---|
| Time to Surface | Trimix deco and technical dive planner | decompression planner |
| Surface Interval | Underwater video colour correction & reels | fix blue GoPro dive footage, one reel |
| Dive log | Shearwater dive log app for iPhone | dive logbook, Shearwater Bluetooth import |
| Turn Pressure | Dive planner and minimum gas calculator | scuba gas planner, no-deco calculator, turn pressure |
| Weights Check | Scuba weight and buoyancy calculator | dive weighting |

The page title, description, Open Graph and Twitter text and each JSON-LD item description carry
the same phrases. Left out on purpose: "NDL" (the research shows the store's suggestions never offer
it) and "how much weight for diving" (not in the research, and it would promise Weights Check's
answer as a verdict, which it is not). The footer names GoPro's trademark because the Surface
Interval line names GoPro. To change a phrase, change it here, in the title/description and in the
JSON-LD together. The captions
inside the videos are the screenshot captions each app ships to the store
(`caption-screenshots.swift` in each repo's ship scripts). **Do not write new marketing claims
here** — change the listing in the app's repo first, then mirror it. The app is "Weights Check"
with the s, "Dive log" with a small l; these are his names.

Rules carried over from every app: copyright reads **Rustam Ismailov** and nothing else; no
invented company; British spelling in his own text, American only where it quotes the US store.

## How the videos are made (so they stay one family)

Each video opens straight on scene 1 (no title card, see below), then one scene per store screenshot (the phone with
rounded corners and a shadow, drifting upward; a numbered teal pill, headline and subline), and
an outro ("Free on the App Store · diver.today"), over a blurred, darkened, slowed loop of two reef
clips from `surface_interval/reference-footage/clips/`. The look was taken from the Time to
Surface promo Rustam had made on 2026-10-10 (`turn_pressure/build/promo/`). Scenes and captions
are the `APPS` table at the top of the generator; the screenshots are read from each app's
`design/screenshots/<app>/` (1320×2868, the 6.9" set). Fonts are SF Pro from the system.

**Dive log is the exception** (2026-10-17, Rustam's six key features in his order: the dive on one
page, super fast navigation, import once from any computer with the merge, SAC per dive and over
time, dive sites, the social card). Its video reads its own set, `design/screenshots/dive-log-site/`,
taken by `scripts/site-screenshots.sh` in the app's repo, not the App Store set. In it: his real
Blue Hole dive (273) labelled **18/45**, his gas for it (the computer logged 21/35; profile and stops
are the computer's), and a year of **generated sample trips** (`-siteHistory YES` in
`App/Preview/SampleDives.swift`) so Statistics draws a rate settling from about 25 to 15 L/min —
his real export's rate is too noisy for that. The trips are at four famous sites, one per area —
the Blue Hole (where all the Dahab dives, his five real ones too, are put), Richelieu Rock, Maaya
Thila, Batu Bolong — because the map names only one pin of a crowd, and a sample site in Gozo once
showed up as "Blue Hole" near Italy (Rustam, 2026-10-17). The merge scene is the app's two-computer seed.

**A scene can scroll a whole page.** When a scene's stem is a folder of pieces (`00.png`, `01.png`, …
the same screen 500 points further down each time), the generator stitches them, keeps the status
bar strip and the tab bar band fixed, and scrolls the phone through the page over `SCROLL_D`
(6.4 s) instead of `SCENE_D`. Dive log's first scene does this; `CHROME_TOP_PT` and `TAB_BAR_PT`
fit its chrome, so check them before using it for another app.

    python3 tools/build-media.py bg          # once, or when the background should change
    python3 tools/build-media.py icons       # icons, favicon, og.png
    python3 tools/build-media.py videos      # all ten videos and posters (~6 min)
    python3 tools/build-media.py videos dive-log   # one app

Then commit and push. Check a video by pulling frames with ffmpeg and looking at them; the
caption must never run under the phone (the wide layout keeps 820 px for a left caption).

## Reworking a video (new screens, new words, another use case)

Everything a video says and shows is one entry in the `APPS` table at the top of
`tools/build-media.py`. Nothing is edited in a video editor; change the table, re-render, look,
commit. Per app:

- `name`, `tagline` — the outro uses the name. The tagline is only drawn if a title card is switched
  back on (`TITLE_D`, below); with the card off, the first scene's headline is the line the video opens on.
- `scenes` — the story, in order, one tuple per scene:
  `("<screenshot stem>", "<pill>", "<headline>", "<subline>")`. The stem is a file in that app's
  `design/screenshots/<app>/` without `.png`; the pill is two or three words that get numbered
  ("1 · THE DIVE"); the subline may be `""` for a one-liner scene (Dive log's are).

**To change the words**: edit the headline or subline in the tuple. If Rustam gives new wording,
that is his approval — use it as given, his names and his spelling, no exclamation marks, no
claim the screenshot behind it does not show. If the wording is also on the App Store, change it
in the app's `caption-screenshots.swift` too, so the store and the site keep saying the same.

**To change which screens**: pick other stems from the same folder (each app has five to eight
shots; the videos use at most six). A screen that has no screenshot yet is captured in the
app's own repository first, with its ship tooling (`screenshots.sh`, 6.9" at 1320×2868, into
`design/screenshots/<app>/`), and only then named here — the generator never captures anything
and never reads the simulator.

**To focus on another use case**: reorder the scenes so the first scene is the
answer that use case wants (the planners open on the dive, Weights Check on the balance,
Surface Interval on the finished reel), drop the scenes that do not serve it, and rewrite the
first headline. Keep six scenes or fewer: the length is 4.6 s per scene + 3.6 s (a title card, if
switched on, adds its own seconds), and past 35 seconds a muted loop on a web page is not watched.

**To change the look for all five at once**: `ACCENT` (the teal), `TITLE_D / SCENE_D / OUTRO_D /
FADE` (timings; `TITLE_D` is 0, no title card — see below), `FORMATS` (frame sizes, phone height, where the phone sits, how far it drifts),
`BG_CLIPS` (the background footage — after changing it run `bg` before `videos`). The phone
bezel, corner radius and shadow are in `phone()`; the caption type sizes in `caption_layer()`.

Then:

    python3 tools/build-media.py videos surface-interval    # both cuts and both posters of one app
    python3 tools/build-media.py videos                     # all five, about six minutes

**Look before committing.** Pull frames and view them, both cuts — a caption that wraps to
three lines, a headline that runs under the phone, or a subline that fell off the bottom are
the usual faults:

    ffmpeg -y -ss 6.5 -i video/surface-interval-wide.mp4 -frames:v 1 /tmp/wide.png
    ffmpeg -y -ss 6.5 -i video/surface-interval-tall.mp4 -frames:v 1 /tmp/tall.png

(scene *n* starts at 4.6·(n−1) seconds — for Dive log, whose first scene scrolls, 6.4 + 4.6·(n−2); add two seconds to land past the fade; scene 1 has no
fade-in, its first frame is the poster). Then run `tools/preview.sh` for the page at desktop and
phone width; to watch a video play, `open -a Safari index.html` opens the file itself for Rustam.
Commit the changed `video/` and `img/` files with the script, and push.

**If a real screen recording should replace a generated video**: encode it to the same names
and shapes — `video/<slug>-wide.mp4` at 1920×1080 and `video/<slug>-tall.mp4` at 864×1080
(4:5), H.264, no audio track, `-movflags +faststart`, roughly 7 MB and 3 MB — plus the two
posters in `img/`. The page needs no change; the generator will overwrite them the next time it
runs for that app, so note the replacement in this file.

## The question pages (2026-10-19)

Store search is nouns; Google is questions. On 2026-10-19 Rustam asked for the findability proposal
(`docs/search-findability-proposal-2026-10-19.md`) to be implemented in full, and the one part that
reaches a diver who does not yet know an app exists is an article that answers the question they
type, honestly, and only then names the app. Five pages, one per app, written in his voice (the
promotion posts are the reference for it), each checked by a clean-context instructor-level review
for diving and physics correctness before publishing:

| Page | Question | App |
|---|---|---|
| `weight-for-scuba-diving/` | How much weight do I need for scuba diving? | Weights Check |
| `minimum-gas-rock-bottom/` | What is minimum gas (rock bottom) and how do I work it out? | Turn Pressure |
| `gradient-factors-explained/` | What are gradient factors? | Time to Surface |
| `blue-gopro-dive-footage/` | Why is my GoPro dive footage blue, and how do I fix it? | Surface Interval |
| `shearwater-dives-on-iphone/` | How do I get my dives off a Shearwater onto my iPhone? | Dive log |

Rules for them: no number is given as a verdict for the reader's own dive (weights, gas, gradient
factors appear only in worked examples labelled as such); every claim about an app is one its
App Store listing makes, and the Dive log page says which features arrive in the first update after
the build that is in review (the Shearwater Cloud import and the two-computer merge); no scripts,
no CDN fonts, no analytics; the `?v=` on the stylesheet link is bumped on all six pages together.
The Dive log page carries a dated note about the Perdix 3 not yet connecting over Bluetooth
("In October 2026"); update it when Shearwater's interface ships. Search Console shows within a few
weeks which pages draw queries; that is the signal for writing more or rewriting one.

## What was decided and why

- **GitHub Pages, not Cloudflare or Netlify** — free, already used by all five app sites. One repo is both source and site; there is no
  separate publishing repo because this project *is* the site.
- **Generated videos, not screen recordings** — one consistent family for five apps in one
  session, regenerable in minutes when an app's screenshots change. The real screen recordings
  can replace them later by dropping files with the same names into `video/`.
- **Two cuts per video** — a 16:9 frame is unreadable at phone width, so phones get a 4:5 cut
  with the caption above the phone. The page picks the cut in its script by viewport width.
- **Videos load only near the viewer**, muted, looping, and stop when scrolled away; with
  "reduce motion" set they wait for a tap. A video starts downloading when its section is within
  about a screen and a half, so it is ready on arrival (not when "save data" is on). No analytics,
  no fonts from a CDN, no framework.
- **No title card, and the poster is the opening frame** (2026-10-14, Rustam: 8–10 seconds from
  scrolling to a video until the app appeared, too long). The poster used to be cut from the title
  card and the video opened on four more seconds of it. Now every video opens on scene 1 and the
  poster is its first frame, so the app is on screen at once and the video fades in over an
  identical picture. The page already shows the icon, name and sentence under the video. A title
  card can come back with `TITLE_D` of 1.5 or more, but then the poster is the card again.
- **The top bar is sticky on desktop only** (2026-10-14, Rustam: on iPhone the bar with the site name
  stuck a hand's width below the top edge, the page showing above it; "either at the very top or not
  at all"). iOS Safari keeps its own address bar over the top of the screen and parks a sticky bar
  under it. On phones (`max-width: 760px`, and a phone held sideways) the bar is `position: static`
  and scrolls away; the menu links are hidden there anyway, so the bar is only the site name.
- **Everything under diver.today** (2026-10-19, Rustam: *"make all the pages you are linking from diver.today be
  under the diver.today domain and not a github"*). GitHub serves every project site of an account under the
  custom domain of the account's *user site*, the repository named `<account>.github.io`. So the site
  repository was renamed from `divertoday-site` to `ligrimp-lang.github.io`; nothing else changed, and
  from then on `ligrimp-lang.github.io/<repo>/` answers `301` to `diver.today/<repo>/` for all six Pages
  sites of the account (the five per-app sites and `fourandsix-site`, which comes along whether or not it
  is a dive app). The App Store links in the listings still name github.io and keep working through the
  redirect; the per-app sites' canonical tags were changed to diver.today the same day. The repo names keep
  their `-site` suffix: Pages addresses of a renamed repository do not redirect, so renaming them would
  break the store links.
- **Why the repo was `divertoday-site` and not `diver-today`** — the first repository's Pages
  deployment got stuck for good. The whole story, and the way out, is the next section.

## GitHub Pages: the deployment that stayed "in progress" (root cause, 2026-10-14)

**Symptom.** Every `pages build and deployment` run fails after about 25 seconds in the
"Deploy to GitHub Pages" step with

    Deployment request failed for <sha> due to in progress deployment.
    Please cancel 50d67bf810ec4ae36cabf06879441f138c65e877 first or wait for it to complete.

and the domain shows GitHub's "There isn't a GitHub Pages site here" page.

**Root cause.** The very first deployment of the site carried the `CNAME` file for diver.today
while diver.today's DNS still pointed at Namecheap's parking page. GitHub's deploy step
(`actions/deploy-pages`) health-checks the site *at its custom domain* and waits up to ten
minutes for that check to pass. It never could, the action gave up ("Timeout reached,
aborting!") and sent a cancel — but the Pages backend kept that deployment registered as in
progress, and from then on refused every new deployment for that site. The lock belongs to the
repository's Pages site; nothing in the repository's files is wrong.

**What does not clear it — do not spend time on these again.**
- `POST repos/<r>/pages/deployments/<sha>/cancel` returns 204, the status endpoint even reads
  `deployment_cancelled`, and the lock stays.
- `gh run rerun <id> --failed` — the re-run sits in "queued" indefinitely; `force-cancel` on
  it answers 409.
- Marking the `github-pages` environment deployments inactive and deleting them — succeeds,
  lock stays.
- `DELETE` then `POST repos/<r>/pages` to re-create the Pages site — a new certificate is
  issued, lock stays.
- Waiting half an hour.

**What works.** A fresh repository. Pages state is per repository site, so the same commits
pushed to `ligrimp-lang/divertoday-site` (now `ligrimp-lang.github.io`), with Pages enabled there, deployed in under a minute —
by then the DNS already resolved to GitHub, so the health check passed on the first try. Before
enabling Pages on the new repository, `DELETE repos/<old>/pages` on the stuck one so the domain
is free (a custom domain can be bound to only one Pages site), then archive the old one. That is
what `ligrimp-lang/diver-today` is: archived, superseded, nothing points at it.

**Prevention — the one rule.** Put the `CNAME` file in only after the DNS already resolves to
GitHub: `dig +short A diver.today` must list 185.199.108.153 through 185.199.111.153 first.
A site that has to go up before its DNS exists is published without `CNAME` (it is reachable at
`ligrimp-lang.github.io/<repo>/`) and gets the file in a second commit once the records are in.
If the symptom above ever appears anyway, skip the cancels and go straight to the new repository.

## Not done yet / next

- "Enforce HTTPS": done 2026-10-14 (`https_enforced` is true on `repos/ligrimp-lang/ligrimp-lang.github.io/pages`).
- Dive log's button when it is on sale (above).
- Google Search Console: **done 2026-10-15.** URL-prefix property `https://diver.today/` in
  Rustam's Google account, verified by the HTML tag (`google-site-verification` meta in the head
  of `index.html`; **keep it there**, removing it un-verifies the property), `sitemap.xml`
  submitted (status Success, one page discovered) and indexing requested for the home page. The
  home page was "Discovered, currently not indexed" until then. The Performance report there is
  where the search queries show up, a few days after it starts to fill.
