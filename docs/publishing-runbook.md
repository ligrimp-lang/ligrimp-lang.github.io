# Publishing runbook: the question engine

How an episode of the question engine (`docs/promotion-engine-proposal-2026-10-28.md`; the rules in `CLAUDE.md`, "The
question engine and its pilot") goes out each week, which command does what, the two platforms' limits, and what is never
automated. Everything runs on Rustam's Mac, by hand, with his say-so; the credentials live there and nowhere else. This
file is in the public repository, so it names paths and commands and no accounts.

## What goes out

One episode a week, the same words in two shapes, rendered by `tools/pilot-episode.py <slug> all` into `build/pilot/`:

| File | What | Where it goes |
|---|---|---|
| `<slug>-wide.mp4` | 1920×1080 | YouTube, as the video; later the episode's page on diver.today |
| `<slug>-short.mp4` | 1080×1920 | YouTube, as a Short; Instagram, as a Reel |
| `<slug>-thumb.png` | 1280×720 | YouTube's thumbnail for the wide cut |
| `<slug>.srt` | the spoken sentences with their times | YouTube's captions (nothing spoken is drawn on the screen) |
| `<slug>.vtt` | the same cues as WebVTT | the episode page's captions (`episodes/<slug>/`; browsers take WebVTT, not SubRip) |

The pilot's three slugs are `gas-for-the-dive`, `sac-rate` and `minimum-gas`. A new episode is a new entry in three tables:
`EPISODES` in `tools/pilot-episode.py`, `METADATA` in `tools/publish-youtube.py` and `CAPTIONS` in `tools/publish-instagram.py`.

## Before anything is published

1. Rustam has read the words (`tools/pilot-episode.py <slug> script`) and the clean-context instructor review has passed; only
   then is the episode rendered. Nothing goes out without his verdict on the episode.
2. Both cuts, the thumbnail and the two captions files are in `build/pilot/`.
3. The episode's page exists at `episodes/<slug>/index.html` (built like the question pages; the three pilot pages are in), and
   the wide cut, the thumbnail and the `.vtt` are committed beside it as `episodes/<slug>/<slug>-wide.mp4`, `<slug>-thumb.png`
   and `<slug>.vtt`, from the Mac. The short cut sits at a public https address on diver.today too (a copy as
   `episodes/<slug>/<slug>-short.mp4` is the natural place); that address is what `publish-instagram.py` needs, since Instagram
   fetches the file rather than taking an upload. Once the YouTube upload is done, its video id goes into the page's
   `data-youtube` attribute.
4. The app the episode ends on is on sale: the `sac-rate` episode names Dive log's App Store link, which works only once Apple
   has approved the app (`CLAUDE.md`, "The apps on the page").
5. Each command is run with `--dry-run` first. It prints the title, description and tags, or the caption, and every call that
   would be made, and touches no network and no credentials. Read the words once more there.

## The weekly run

    python3 tools/publish-youtube.py <slug> --dry-run
    python3 tools/publish-youtube.py <slug>                              # the wide cut, private
    python3 tools/publish-youtube.py <slug> --cut short                  # the Short, private, "#Shorts" added to the title
    python3 tools/publish-instagram.py <slug> --video-url https://diver.today/episodes/<slug>/<slug>-short.mp4 --dry-run
    python3 tools/publish-instagram.py <slug> --video-url https://diver.today/episodes/<slug>/<slug>-short.mp4

Then, in YouTube Studio, Rustam sets the two videos public or gives them a publish time (why, below). The addresses the
scripts print go into the week's note. Running the publish inside the Monday job is decision 5 of the proposal and is still
open; until he decides, the run is by hand.

## YouTube: `tools/publish-youtube.py`

    publish-youtube.py <slug> [--cut wide|short] [--file path] [--thumb path] [--privacy private|unlisted|public]
                       [--schedule 2026-11-03T09:00:00Z] [--playlist id] [--video-id id] [--dry-run]

What it does, in order, with the quota cost in brackets (the project has 10,000 units a day, so one episode's two uploads
use under half of it):

1. `videos.insert` [1,600], a resumable upload: it opens an upload session, sends the file in 8 MiB pieces, and after a
   network error or a server error asks the session how far it got and carries on from there. Parts `snippet` (title,
   description, tags, category 27 Education, default language en) and `status` (`privacyStatus` private unless `--privacy`
   says otherwise, `selfDeclaredMadeForKids` false, `publishAt` from `--schedule`, which YouTube accepts only with private).
2. `thumbnails.set` [50] with `<slug>-thumb.png`, for the wide cut only; a Short takes its own frame. YouTube takes a file of
   up to 2 MB; the script says so and names the ffmpeg line to make a JPEG if the PNG is bigger. Custom thumbnails need the
   channel to be phone-verified; if the call is refused, verify once in YouTube Studio.
3. `captions.insert` [400] with `<slug>.srt`, language en, named "English", published (not a draft).
4. `playlistItems.insert` [50] when `--playlist` names a playlist (the id is in the playlist's address in YouTube Studio).

It prints the video id, the watch address and the YouTube Studio address. If a step after the upload fails, it says which,
and the same command with `--video-id <id>` redoes those steps without uploading the video again.

**Private until the audit.** A video uploaded through the API by a project that has not passed YouTube's API compliance
audit is locked to private whatever `privacyStatus` or `publishAt` asks; the upload succeeds and YouTube says so by e-mail
(review note 1 in the proposal). So until the audit passes, the weekly publish ends in YouTube Studio: open each video, set
it public, or give it the publish time. That click is also Rustam's veto. The script sends what it was asked all the same,
so when the audit passes nothing here changes: `--schedule 2026-11-03T09:00:00Z` then publishes at that time by itself.

**Credentials.** `~/.config/diver-today/youtube-client.json` (the OAuth client) and `youtube-token.json` (the refresh
token), both made by `tools/youtube-auth.py`; `python3 tools/youtube-auth.py check` proves they work by printing the
channel's name. The script imports that file for the access token. Scopes: `youtube.upload`, `youtube.force-ssl` (captions
and playlists need it) and `yt-analytics.readonly` (the Monday measure).

**Campaign links.** The App Store links in the descriptions are plain unless `DIVER_TODAY_PT` is set in the environment to
the provider token from App Store Connect; then each carries `pt`, `ct=youtube` and `mt=8`, one token per channel as the
proposal decided (review note 6: a campaign shows in App Analytics only after five first-time downloads).

## Instagram: `tools/publish-instagram.py`

    publish-instagram.py <slug> --video-url https://diver.today/episodes/<slug>/<slug>-short.mp4 [--caption-file path] [--dry-run]

What it does, in order, against `graph.facebook.com`, Meta's Instagram Graph API on the Facebook-login route: the Instagram
professional account is linked to a Facebook Page, and the Page's access token publishes to the Instagram account behind it
(Meta's dashboard offered no Instagram-login set-up on 2026-10-29, so this is the route; the account's own use, no App Review).

1. Looks at the credentials' age and warns when the token is due for renewal (below).
2. Reads `content_publishing_limit`: how many API posts went out in the rolling 24 hours against the limit Meta reports, and
   stops if it is used up.
3. Checks the video address answers, then creates a media container: `POST /{ig_user_id}/media` with `media_type=REELS`, the
   `video_url`, the caption and `share_to_feed=true`.
4. Polls the container's `status_code` every 10 s, for up to 10 minutes, until `FINISHED`; `ERROR` or `EXPIRED` stops the run
   with Meta's message (most often the file could not be fetched or is not a shape Instagram takes).
5. `POST /{ig_user_id}/media_publish` with the container, then reads the new media's `permalink` and prints it.

**The caption** comes from `CAPTIONS` in the script, keyed by slug: the question, a line on the answer, the worked example
marked as one, the app, diver.today and the hashtags. Links in a caption are not clickable, so it says "link in bio"; the bio
link is diver.today with the Instagram campaign token. Instagram takes up to 2,200 characters and 30 hashtags; the script
checks both before sending. `--caption-file` replaces the table's text, for a one-off or for an episode not yet in the table.

**The daily limit.** Meta limits posts published through the API per rolling 24 hours; the brief for these scripts puts it
at 25, the proposal's 2026-10-28 review read 50–100 on Meta's page, and the number the account actually has is what the
script prints from `content_publishing_limit` before each post. One Reel a week is far inside any of them.

**The token.** The credentials file, `~/.config/diver-today/instagram.json`, is written by `tools/instagram-auth.py`:
`route` (facebook), `app_id`, `app_secret`, the long-lived `user_access_token`, the Page's `page_id`, `page_name` and
`page_access_token`, the Instagram account's `ig_user_id` and `ig_username`, and `obtained`, the day of the exchange. The
publishing calls use the Page token. It does not expire on its own, but it is only as good as the user token behind it, which
lasts about 60 days, and **there is no refresh call on this route**. So the script warns when `obtained` is 50 days old or
more (or missing) that the token must be renewed, and goes on with the token it has; it never writes the file. Renewing is by
hand, once in under two months: a new short-lived token from the Graph API Explorer, then

    python3 tools/instagram-auth.py exchange <short-lived token>
    python3 tools/instagram-auth.py check

which rewrites the file with today's `obtained`. After 60 days without that, every call fails with Meta's message and the
same two commands put it right.

## What is never automated

Rustam's rule, and Meta's and YouTube's terms: **nothing here replies to comments, follows anyone, likes, messages or
subscribes.** The scripts publish, and that is all the accounts do by machine. Following instructors and their students,
answering comments and any outreach are his, by hand, at a human pace (the proposal, "His point about instructors and their
students"). No follow-for-follow, no bots, no bought followers: the accounts are the asset and those are the ways to lose
them.

## After publishing

The Monday measure reads YouTube's analytics (the `yt-analytics.readonly` scope is already granted), Search Console for the
page, and App Analytics for the campaign links, and writes what it learned into `docs/promotion-knowledge.md`, dated
(the proposal, "What the AI does, end to end", step 5). The kill rule stands there too: by the eighth weekly video, under
300 views per long video and under ten attributed installs in all means stop.

## What was not tested where these were written

The two scripts were written in a cloud session with no credentials and no route to either platform, so every network call
is untested until the first run on the Mac: the resumable upload, the thumbnail, captions and playlist calls, and the
publishing-limit, container, publish and permalink calls. The dry runs were tested, and the network paths were exercised
against a local stand-in for each API. The platform documentation was not reachable from that session either, so the
endpoint details follow the brief, `tools/instagram-auth.py` and the documentation as known; the first live run checks them.
