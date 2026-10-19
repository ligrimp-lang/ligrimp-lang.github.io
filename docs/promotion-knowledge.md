# Promoting the dive apps — what is known, what was tried, what is open

**This project is the home for app promotion from 2026-10-19 on** (Rustam: *"i will use this project
onwards to investigate how to promote apps"*). Read this first, then the two dated documents beside
it; the per-app repositories hold the raw material named below. Not on the web (`docs/` is excluded).

## Where the facts live

| What | Where |
|---|---|
| Weekly numbers (every Monday 07:00): impressions, downloads by source and territory, unanswered reviews, store rank per search term, what people type, Google Search Console for diver.today | `~/.claude/skills/asc-analytics/` → `reports/<date>.html` (opened in Safari by the run), per-app pages in each repo's `.claude/analytics/weekly/` (Weights Check: `nimbalyst-local/promotion/weekly/`). The job: `resources/weekly-all.sh`; the app list: `resources/apps.tsv` |
| Search terms probed per app | `turn_pressure/docs/store-search-terms-turn-pressure.txt`, `…-time-to-surface.txt`, `weights_check/nimbalyst-local/promotion/search-terms.txt`, `surface_interval/docs/store-search-terms.txt`, `sharewater_dive_log/docs/store-search-terms.txt` (`? prefix` lines drive the suggestion probe) |
| Store listings (name, subtitle, keywords, texts, per locale, with the dated reasoning for every change) | `docs/app-store-listing*.md` in each app repo; `turn_pressure/docs/app-store-listing-time-to-surface*.md` for Time to Surface. Pushed with each repo's `.claude/skills/ship/scripts/asc-store.rb` |
| Search research that chose the words | `weights_check/nimbalyst-local/promotion/findability-plan-2026-09-21.md`, `turn_pressure/nimbalyst-local/plans/app-store-findability-2026-09-16.md` and `-09-21.md` |
| The site and its question pages | this repo; `CLAUDE.md` here |
| Forum and group posts, in Rustam's voice | `docs/promotion-posts-2026-10-15.md` (venues, five reply templates, five posts) |
| The findability proposal and its data | `docs/search-findability-proposal-2026-10-19.md` |
| Google Search Console | property `https://diver.today/`, Rustam's Google account; the weekly job reads it through a service account |

## The apps and their store position (2026-10-19)

Each dive app gets about 45–75 App Store search impressions a week; Surface Interval on the Mac about 160.
Store search ranks matching apps by ratings and downloads once the words match, so crowded nouns are
won by popularity, not wording.

| App | Owns (#1) | Visible | Weak or absent | Done 2026-10-19 |
|---|---|---|---|---|
| Turn Pressure | *turn pressure* | *scuba gas planner* #38 US / #5 DE; *dive planner* #23–40 (invisible in effect) | *minimum gas*, *sac rate scuba* not indexed (the words were not in the listing) | keywords: out `log,logbook,buddy`, in `minimum,rock,bottom,rate` (all English locales); probe terms *rock bottom*, *safety stop* |
| Time to Surface | *time to surface* | *buhlmann* #12–24, *gradient factor* #7–40, *trimix mod* #9–27 | *deco planner* #161 US (US "deco" = home decor); *decompression* never typed | no listing change; probe terms *tech dive*, *deco stops*, *trimix planner*; forum posts are the lever |
| Weights Check | *weights check*, *dive weight* AU/DE/RU/NL | *dive weight* #6 US / #16 GB | *buoyancy calculator* absent US/GB four weeks after the subtitle bought it (fitness apps); gear words rank #117–143 | English keywords: out `wetsuit,drysuit,gear,ditchable`, in `ballast,trim,calc`; RU/DE/NL/FR/ES/IT fields re-cut toward груз/rechner/tarieren/lood/lest/lastre/calcolo |
| Surface Interval | *surface interval*, *dive videos*, *dive video* | *snorkel video* #7 US | *underwater color correction* #74 US although the US store suggests that phrase; *underwater video editor* absent | subtitle → `Underwater color fix & reels` (replaces his 2026-09-28 choice); keywords: out `underwater,color,reel`, in `correction,assembly,blue`; goes out with 1.7.2 |
| Dive log | — (in review since 2026-10-14) | — | *dive log* is the most crowded term of the five | terms file written, app added to the Monday job, rating request after the second import |

## What was learned (keep these; they cost time to find out)

1. **Keywords change nothing until a version ships.** Name, subtitle and keywords belong to a version
   record. When every version is on sale ("No editable version" from `asc-store.rb … audit`), the new
   words wait in the listing document until the next version is opened, then `metadata` pushes them.
   Turn Pressure and Weights Check sit in that state since 2026-10-19.
2. **One listing change per app per week**, so the Monday report can attribute a rank move to it. The
   documents keep every superseded field under a dated "kept for the record" heading; follow that.
3. **The store search is nouns; Google is questions.** The suggestion probe shows what divers type after
   a prefix; a word the store never suggests (*ndl*, *decompression*, *minimum gas*) is typed by almost
   nobody, however well it describes the app. Google gets "how much weight do I need", so the question
   pages on diver.today exist for that; Search Console tells within weeks which draw.
4. **Ratings are the multiplier on head terms.** For *dive planner*, *dive log*, *buoyancy calculator*
   the order among matching apps is ratings and downloads. Every app now asks for a rating after a
   completed use (Weights Check first, 2026-09; Turn Pressure and Time to Surface; Surface Interval and
   Dive log from 2026-10-19), never the first time, once per version. The brief:
   `weights_check/docs/rating-prompt-brief-for-other-apps.md`.
5. **Thin markets are cheap to own.** The German, Russian, Dutch indexes hold a handful of apps per dive
   phrase ("#2 of 2", "– of 1"); one localised keyword puts an app first. The Discovery numbers show
   where people already are (JP, NL/BE, CN, RU, MX), so localised fields matter more than another English
   synonym.
6. **A word that is the name's second half can still rank badly** when it means something else in that
   market (*deco* in the US). Check the suggestion list of the storefront, not the dictionary.
7. **Brands.** *Shearwater* is in Dive log's subtitle, never in a keyword field (a trademark there is a
   rejection); the trademark line at the foot of the description is the answer if review raises it.
8. **Everything in a GitHub Pages repository is on the web** unless `_config.yml` excludes it; the
   per-app sites publish by copying the whole folder, so anything committed there goes out with the next
   publish (the Time to Surface pages went out early on 2026-10-19 that way). Hold back by not committing.
9. **The domain.** Since 2026-10-19 the diver.today repository is the account's user site, so every
   per-app site is served at `diver.today/<repo>-site/` and github.io redirects. Canonical tags on the
   per-app sites name diver.today; the App Store support and privacy URLs still name github.io, which
   is fine through the redirect.
10. **Google Search Console** lags two to three days and was empty on day four; the first real numbers
    are expected in the report of 2026-10-26. The verification meta tag in `index.html` must stay.

## Challenges still open

- **Head terms** (*dive planner*, *dive log*, *buoyancy calculator*) need ratings and downloads, which
  need the forum posts to be made (they are written, not posted) and time.
- **Weights Check's English phrase** *buoyancy calculator* may never surface in the US against fitness
  apps; the localised fields and the question page are the route.
- **Dive log** launches into the most crowded term; its Shearwater niche (subtitle) and the Shearwater
  page on diver.today are the plan. Its first Monday report comes the week after approval.
- **Time to Surface** is a tech-diver product; the store finds it only by name. ScubaBoard's technical
  forum, GUE and TDI groups, instructors.
- **Measuring Google** per page: Search Console's page report, from the week of 2026-10-26.
- **Not done yet:** posting the forum texts (Rustam does it himself); request indexing of the five
  question pages in Search Console (or wait for the sitemap); `APP_SITE_URL` in each app's
  `app-config.sh` still prints the github.io address (harmless, redirects).

## How to continue (the loop)

Monday: read the report, note any rank that moved against last week's change. Pick one change per app,
record it in the listing document with the date and the reason, push it with `asc-store.rb` if a version
is editable, add any new phrase to the terms file so it is measured. Look at Search Console's pages and
queries for diver.today; a question that brings people and has no page gets one, written in Rustam's
voice and reviewed for diving correctness before publishing (the review rules are in `CLAUDE.md`,
"The question pages"). Write what was learned into this file, dated.
