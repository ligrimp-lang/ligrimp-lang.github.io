# Running the weekly publish from the cloud — proposal, 2026-10-29

Rustam's wish (2026-10-29): hand as much of the question engine as possible to a cloud session, and keep on his Mac only
what cannot leave it. This proposes the split for the weekly publish. It is a proposal: no routine, schedule or secret
has been created, and nothing runs until he says so after the pilot.

## The split

**On the Mac, once a week, by hand:** render the episode (`tools/pilot-episode.py <slug> all`; the voice model, ffmpeg,
his clips and the apps' screenshots are there and nowhere else), look at it, and commit its files into the repository
beside the episode's page: `episodes/<slug>/<slug>-wide.mp4`, `<slug>-short.mp4`, `<slug>-thumb.png`, `<slug>.srt` and
`<slug>.vtt`, with the page `episodes/<slug>/index.html` (made in the cloud, from the episode's words). The push puts
the short cut at a public address, which Instagram needs.

**In the cloud, on a schedule:** a scheduled task that starts a fresh session in the cloud environment once a week, which
runs the two publishing scripts as they are (`docs/publishing-runbook.md`): `tools/publish-youtube.py <slug>` and `--cut
short`, then `tools/publish-instagram.py <slug> --video-url https://diver.today/episodes/<slug>/<slug>-short.mp4`; writes
the YouTube id into the page's `data-youtube` attribute and pushes that; and reports the three addresses, the quota and
publishing-limit figures the scripts print, and anything that failed, in one message. Which episode is this week's comes
from a small queue file in the repository (the slug and the week), so the Mac side commits the files and the cloud side
publishes without anyone typing a slug.

The scripts read their credentials from `~/.config/diver-today/`, which does not exist in a cloud session. So the task's
first step writes the credential files there from the environment's secrets, mode 600, and the scripts run unchanged.

## What it needs from Rustam

1. **His go after the pilot.** Nothing is scheduled before his verdict on the three episodes.
2. **The credential files as secrets of the cloud environment**: `youtube-client.json`, `youtube-token.json` and
   `instagram.json` (three files; the YouTube side is a client and a token), each stored as one environment secret
   holding the file's JSON. They are added in the cloud environment's settings (the environment menu in the session's
   title bar, then Edit; under Network secrets where that section is offered, otherwise as environment variables), never
   pasted into a chat and never committed. A new session picks them up. Proposed names: `DIVER_TODAY_YOUTUBE_CLIENT`,
   `DIVER_TODAY_YOUTUBE_TOKEN`, `DIVER_TODAY_INSTAGRAM`. The App Store provider token for campaign links is a fourth,
   optional one (`DIVER_TODAY_PT`, which `publish-youtube.py` already reads).
3. **Network access** for the environment to `www.googleapis.com` and `graph.facebook.com` (and `diver.today`, which the
   Instagram script checks before it posts). The session that wrote the scripts could reach neither platform nor their
   documentation, so the first run from the cloud is also the first test of the environment's network policy.
4. **The weekly veto stays his** in either form: until the YouTube audit passes, the videos are private and he sets them
   public in YouTube Studio; after it, the task can carry `--schedule` and the veto is 48 hours of silence, as the
   proposal of 2026-10-28 says.

## The two platform limits, which the cloud does not change

- **YouTube is private until the API audit.** A video uploaded through the API by a project that has not passed the
  compliance audit stays private whatever the upload asks, so the weekly run ends with him in YouTube Studio until the
  audit passes. The script already sends `publishAt` when asked, so nothing changes in the task on the day it passes.
- **The Instagram token is renewed by hand, about every 60 days.** The Facebook-login route has no refresh call: the
  long-lived user token behind the Page token lasts about 60 days, and renewing it is the Graph API Explorer step and
  `tools/instagram-auth.py exchange` again, on the Mac. After that the `instagram.json` secret in the cloud environment
  has to be updated too, or the cloud run fails at the first call with Meta's message. `publish-instagram.py` warns
  from day 50; the task's report carries that warning so the renewal is never a surprise.

## What stays as it is

No automated engagement, in the cloud as on the Mac: the task publishes and reports, and nothing replies, follows, likes
or messages. The Monday measure (YouTube's analytics through the granted `yt-analytics.readonly` scope, Search Console,
App Analytics for the campaign links) can join the same cloud task later; it is not part of this proposal.

## Why not simply keep it on the Mac

It can stay there; the runbook describes that. The reasons to move it: the Mac has to be awake and his at the hour, the
credentials then live in two places only if he chooses the cloud, and a cloud run leaves a written report every week
whether or not he was at the keyboard. The reason not to: three secrets in a second place, and a renewal step every two
months that has to reach both. His call, after the pilot.
