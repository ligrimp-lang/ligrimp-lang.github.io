# One engine to bring divers to the five apps — proposal, 2026-10-28

Rustam's brief (2026-10-28): the apps are not found by the people who need them. He wants **one** most
reliable way of promoting the whole family, built around the use cases and the compelling advantages
(free, an unmatched UI, strong sharing, fast evolution, a broad footprint), **run almost entirely by AI**,
fed by his training knowledge and his dive footage. The end: app users, some of whom subscribe, and a
project he can show as a proven success. He gave one idea to challenge: an Instagram account that posts
app use cases and quick how-tos, grows by following divers' followers, and is run by AI.

This document gives the answer in one paragraph, then shows the alternatives and what kills each, then
the design of the one that survives, what it will and will not do, and the few decisions he has to make.

## The answer

**Answer one diver's question a week, as a video and as a page, and let search deliver it.** A weekly,
AI-run production line turns one question divers actually type ("how do I work out my SAC rate", "how
much weight do I need", "why is my GoPro footage blue") into **one video of under a minute** (his rule, 2026-10-28: Reel-friendly, *"no one will watch
instagram longer"*) in two shapes, 16:9 for **YouTube** and the page and 9:16 for Shorts and Reels, built from
his footage, the app on screen and a voice-over; and its written twin on **diver.today** with a worked example. Each ends with the app that does the thing for free, linked with an App Store campaign link so every
install is attributed. **Instagram carries the same content with the same weight** (his decision,
2026-10-28): the vertical cut as a Reel and the answer's key cards as a carousel, posted through
Meta's own API, each channel with its own campaign token so the two can be compared after eight weeks.
The following of instructors and their students is his, at a human pace, from a list the AI builds. The AI picks the next question from the demand
it can see (Search Console, YouTube's own suggestions, his research), writes in his voice, passes the
instructor-level review that the question pages already have, renders, uploads, measures on Monday and adjusts. He supplies footage and ideas, opens each video with
20 seconds of himself asking the question, and for the first months sets the publish time in YouTube
Studio once a week (five minutes; review note 1 says why), which is also his veto.

Why YouTube is in it at all, when the content is the same: a channel with no subscribers is not an
orphan there, because how-to distribution on YouTube is search and suggestion, not the subscriber list.
A video titled with the question is found by the people typing it for years, carries a clickable link,
and is measured per video. Instagram forgets a post in two days and allows one link in the bio, but it
has the lever he values: active divers reached through instructors and their students. So both run,
the same unit to each, and the campaign tokens say which one brings installs.

## What the numbers already say

- Each app gets about **45–75 App Store search impressions a week** (`promotion-knowledge.md`). The
  store orders matching apps by ratings and downloads; the head nouns (*dive planner*, *dive log*,
  *buoyancy calculator*) are won by popularity, which a new free app cannot buy with wording.
- **Store search is nouns; Google is questions** (lesson 3 there). The five question pages exist for
  that since 2026-10-19; Search Console starts showing their queries around the week of 2026-10-26.
- The forum posts that would move the head terms are written and **not posted**; that part cannot be
  automated without becoming spam, and this proposal does not pretend otherwise.

So the gap is between a diver with a problem and the knowledge that a free app solves it. Nothing in the
store closes that gap; something outside the store has to.

## The candidates, and what kills each

| Candidate | What it would do | What kills it as the one engine |
|---|---|---|
| **Instagram account, AI-run, follow-for-follow** (his idea) | Carousels and Reels of use cases and how-tos; follow the followers of big diver accounts for follow-backs | Meta's terms forbid automated following; new accounts are action-blocked after a few dozen follows and suspended on repetition, so the growth half of the plan endangers the asset. A follow-back audience is courtesy, not intent. No clickable links in posts. A post is dead in 48 hours; nothing compounds. AI captions on Instagram are met with low tolerance. **Kept as a by-product output** (Reels through the official API), not as the engine. |
| **TikTok** | Shorts with cold-start reach | Audience skews young and non-diving; the posting API needs an app audit before anything is public; the geopolitical state is unstable. No. |
| **Reddit / ScubaBoard / Facebook groups** | The highest-intent divers there are | Automation is spam, gets banned and burns the name. Stays what it is: his own posts, already written. |
| **Apple Search Ads** | Buys the head terms the free app cannot win organically | Costs money and needs a conversion story first; a later accelerator, not the engine. |
| **More question pages on diver.today** (continue 2026-10-19) | Rank for questions in Google | Right intent, fully automatable, compounding — but a two-week-old domain ranks slowly, Google's AI answers take the easy clicks, and text alone does not use what he can feed: footage and training. **Becomes half of the engine**, as the written twin of each video. |
| **YouTube channel** | Rank for the same questions where divers watch how-tos, plus Google's video results, plus Shorts for cold-start reach | Slow first month; a voice is needed; thumbnails matter; competition from established dive channels on gear and travel — but thin on planning, gas and weighting how-tos, which is exactly his ground. **Becomes the spine.** |
| **Pinterest** | Evergreen visual how-tos with clickable links, API posting allowed | Small diving audience. Optional later output; not pursued now. |
| **Dive-centre outreach for signed team plans** | Emails to dive centres, AI-drafted | A sales channel, needs him to send and follow up; a different project. Noted, not pursued here. |

The survivor is not a platform but a **content unit with two search surfaces**: a question, answered
honestly in video and in text, with the app at the end. One script, three outputs, one measurement.

## Where the questions come from

He does not have to supply them; the engine reads demand, and his training notes are the seasoning.

1. **What divers type after a prefix**: Google's and YouTube's suggestions for "how to", "what is",
   "why is my" with the dive nouns (sac rate, minimum gas, dive weight, gradient factor, gopro
   underwater, shearwater). The same probe the store work already uses, pointed at search engines.
2. **Search Console** for diver.today: queries with impressions and a poor position are questions
   people ask that the site nearly answers. From the week of 2026-10-26 on.
3. **Forum thread titles** on ScubaBoard and r/scuba in the training, gas-planning and weighting
   sections: the questions divers ask each other, in their words. Read, not posted to.
4. **His research files** in the app repositories (`search-terms.txt`, the findability plans) and the
   store suggestion probes: the nouns a question must contain to be found.
5. **His training knowledge**: the misconceptions he saw in courses, and his footage, decide how a
   question is answered and which dive illustrates it; a note from him jumps the queue.

The first twelve below were picked that way by hand; the Monday step does it each week and shows its
choice and the three runners-up in the message he gets.

## Will it be yet another AI-generated channel?

Fair concern, and nothing promised here can settle it; only a finished episode can. So the first
deliverable is a pilot, made before any account exists, for him to judge. The first take, a four-minute
explainer of the SAC rate, he called "stupid": **the cat is C × A × T**, consumption times the average pressure
times time, the gas a dive needs, and nothing may run longer than a minute. So the pilot is **three episodes of
under 60 seconds**: the cat itself (how much gas a dive needs, in litres and bar), the SAC rate from a logged dive
(the C), and minimum gas (the same cat for two stressed divers). The second take he called confusing, and set the
shape of every episode: **a story**, the problem the diver has, then the definitions, then one worked example, then
the practical wrap-up into bar by the cylinder; *"you cannot throw the information without setting up a context"*. The third take he called word salad that cannot build
narrative: the voice had been written to match the screens. So the words are now written first, as speech, and he reads
them before anything is rendered; the rules are in `CLAUDE.md`.
What is designed to keep it from looking generated:

- **Real dives, his footage.** The b-roll is his own clips (the reef clips the site videos already use
  until he adds more), never stock; the worked examples are the cat's, with made-up numbers labelled as such, and the app
  screens show real dives: his Blue Hole dive in Dive log, the Canyon plan in Time to Surface. A viewer who dives recognises real water.
- **The app on screen doing the real thing**, rendered the way the site videos are: the same phone, the
  same captions, the same family look, so the channel and the site are one object.
- **A voice he chose, and every word on screen.** His instruction on 2026-10-28: a very pleasant young
  US male voice (not his own), and the narration duplicated as text. So every spoken sentence is
  synthesised on its own, its length measured, and drawn as a line of text while it is said. The macOS system voices failed his ear ("terrible metallic"), so the narration comes from Kokoro, a
  free neural speech model running on the Mac, in one of its young American male voices; he picks which
  from six samples. A paid speech service stays the upgrade if even that is not pleasant enough. His
  on-camera intros remain the strongest trust lever and stay on offer.
- **The cat.** His idea the same day: C × A × T is the gas a dive needs, so the mascot is a cat. The cat is
  the diver of every worked example, drawn in the family's line and teal, breathing bubbles on the
  cards, so the example is visibly not the viewer's dive and the channel has a face of its own.
- **One answer a week, reviewed.** Scripts come from his training notes, in his voice, with no filler,
  no "dive safe", no exclamation marks, and pass the instructor-level correctness review before render.
  Generated channels fail on volume and vagueness; this makes one specific thing a week.
- **Honest limits.** It is an assembly: footage, screens, captions, narration, music. There is no
  talking head beyond his intro and no underwater demonstration shot for the episode. If the pilot
  reads as generated to him, the voice and the intro are the two levers, and the plan says so.

## The engine in detail

### The unit: one question, one answer

Each week produces one question in three shapes from one script:

1. **The video, under a minute, in two shapes** (16:9 for YouTube and the page, 9:16 for Shorts and Reels;
   the same words in both). Open on his footage with the question. The answer with the
   physics, in captions and voice, about 125 words in all. A worked example, labelled as one, never a verdict for the viewer's
   own dive (the rule from the question pages). Then the app doing it on screen: the generator in
   `tools/build-media.py` already renders phone journeys from the apps' screenshots, so the app part
   costs nothing new. Close on the app, free, and the campaign link.
2. **The carousel.** The vertical cut goes to YouTube as a Short and to Instagram as a Reel; beside it, a **carousel** of the answer's key cards (the question, the formula, the worked example, the app
   screen, the link card) is Instagram's own educational shape and is cut from the same captions.
3. **The page on diver.today.** The script as a reviewed article with the worked example, linked from
   the home page like the five existing ones, in the sitemap, **with a small inline calculator** (SAC,
   minimum gas, weight check). The calculator is the one thing Google's inline AI answer cannot replace
   and the thing a forum thread links to, and links are what a two-week-old domain lacks; it needs one
   change to the question pages' "no scripts" rule. The page is the video's link target and Google's
   written entry, not a traffic source to count on by itself.

The claims about an app are only those its listing makes; the physics passes the clean-context
instructor-level review before anything renders; his names and spelling; no exclamation marks.

### The channels and what each is for

- **YouTube** is the spine: search intent, Google's video results, Shorts for a channel with no
  subscribers, clickable description links, chapters, and years of life per video.
- **diver.today** is the written twin: Google's page results, the place for a calculator, and the
  canonical home each video links to.
- **Instagram** receives the same unit as Reels and a carousel through Meta's content-publishing API,
  with equal weight and its own campaign token. The AI builds the weekly list of instructors, centres
  and training-heavy accounts; the following and replying are his, at a human pace. No following, no
  liking, no DMs by machine (the reasons are in his section below).

### What the AI does, end to end

1. **Picks the question** on Monday from four sources: his search research in the app repositories,
   Search Console's queries with impressions but a poor position, YouTube's search suggestions after
   "how to" and the dive nouns, and his notes from training. Rule: visible demand, and an answer one of
   the five apps embodies.
2. **Writes the script** in his voice (the promotion posts are the reference) and sends it through the
   instructor-level review; a failed review is rewritten, not published.
3. **Renders**: his footage as b-roll (he drops clips in a folder), the app journey from the existing
   generator, captions, a voice (see decisions), royalty-free music from the `dive-music-library`
   skill, a thumbnail; ffmpeg does the assembly, as it does today's videos.
4. **Publishes**: the video and Short are uploaded to YouTube as private with title, description,
   chapters and thumbnail in place; the page is committed and pushed; the Reel goes out through Meta's
   API. Until YouTube's one-time API compliance audit is granted (review note 1), a video uploaded by a
   program stays private whatever the program asks, so he gets one message with the links and sets the
   two publish times in YouTube Studio himself, five minutes a week, which is also his veto. Once the
   audit passes, the upload carries its own publish time and the veto becomes **48 hours of silence**.
5. **Measures on Monday** in the existing report: views, watch time and click-through from YouTube's
   analytics; page clicks and queries from Search Console; installs per campaign link from App Store Connect, which the `asc-analytics` skill already reads. One
   campaign token per channel (youtube, site, instagram), not per video: App Analytics shows a campaign
   only after five first-time downloads and counts only first installs within 24 hours of the click
   (review note 6), so per-video tokens would read zero for months; per-video interest comes from
   YouTube's own click counts. Writes what it learned into
   `promotion-knowledge.md`, dated, and lets it steer the next pick.

### What Rustam does

- **Once**: a YouTube channel for Diver.Today in his Google account; a Google Cloud project with the YouTube Data API and OAuth credentials (the secret stays on his machine, never in a repository) and the API compliance audit applied for on
  day one; an Instagram professional account if he wants the Reels (Meta's current API needs no
  Facebook Page, review note 4); a folder of footage clips; his choice of voice for the body of the video.
- **Weekly, ten minutes**: set the two publish times in YouTube Studio (until the audit passes), read
  the links, veto or not, drop in an idea or a clip. And **record 20 seconds of himself asking the
  question** on his phone: a diving audience trusts a named instructor over an anonymous voice, so the
  video opening on a person is the single biggest trust gain available and the default for the first
  eight videos, not an option.
- **Still his alone**: posting the forum texts. The engine gives those posts a video and a page to link
  to, which is what makes a forum post read as help rather than advertising.

### Where it runs

The same weekly mechanism as the Monday report, with more steps. It runs on his Mac, not in the cloud,
because the footage and ffmpeg are there, so the Mac has to be awake at the hour. The upload is a Python
script using Google's client library, ordinary developer activity, run only with his say-so.

## What to expect, honestly

- **The first months are near zero, and the signal is slow.** Search compounds; it does not spike. A
  zero-subscriber channel's how-to video may gather a few hundred views in its first three months, or
  far fewer; established diving how-tos on SAC or weighting sit at tens of thousands over years. The
  reviewer's estimate, which I accept: the first twelve videos together bring **tens of installs**, not
  hundreds. A different order than today's 45–75 store impressions a week needs six to twelve months of
  compounding, if it compounds. Estimates, not promises; the campaign links decide.
- **A cheap early test and a kill rule.** Shorts are 45-second cuts, so in the first four weeks the
  engine also posts two extra Shorts a week from the five already-reviewed question pages: about twelve
  Shorts in a month show which questions get reach before much has been spent. Kill rule, written down
  now: **by the eighth weekly video (about two months), under 300 views per long video and under ten
  attributed installs in total means stop**, and the effort moves to his forum posts and a small Apple
  Search Ads test on the owned terms. Meeting it means continue; the slope decides more than the level.
- **Subscriptions** follow installs at the family's own rate; this engine moves the top of the funnel.
- **The AI voice** will cost some viewers in a safety-minded niche that trusts named instructors. His
  recorded intro at the top of every video is the mitigation, and why it is the default above.
- **Policy**: YouTube's 2025 "inauthentic content" rule is a monetisation rule; its spam guidelines
  still apply to any channel, and Google's "scaled content abuse" policy targets mass pages made to
  manipulate rankings however they are produced. One reviewed, original, footage-backed answer a week
  with a real tool is the opposite of what both target; the review gate is what keeps it so.
- **The written twin is the weakest leg.** Google answers "how much weight for scuba" inline, and the
  domain is two weeks old. That is why the calculator is core and the page is counted as the video's
  link target, not as a traffic source.
- **Platform facts** the design rests on were checked on 2026-10-28; they are the review notes below.

## The first twelve questions

| # | Question a diver types | Ends on |
|---|---|---|
| 1 | How much gas does my dive need? (C × A × T: the cat; pilot) | Turn Pressure |
| 2 | What is my SAC rate, from a dive I have done? (the C; pilot) | Dive log (SAC per dive and over time) |
| 3 | What is minimum gas? (the same cat for two; pilot) | Turn Pressure (page exists) |
| 4 | What is a turn pressure and how do I set one? | Turn Pressure |
| 5 | How much weight do I need for scuba diving? | Weights Check (page exists) |
| 6 | Why am I heavy at the end of the dive, or light at the safety stop? | Weights Check |
| 7 | What are gradient factors? | Time to Surface (page exists) |
| 8 | What is the MOD of nitrox 32, and why does it matter? | Time to Surface |
| 9 | Why is my GoPro dive footage blue, and how do I fix it? | Surface Interval (page exists) |
| 10 | How do I make a dive highlights reel in ten minutes? | Surface Interval |
| 11 | How do I get my dives off a Shearwater onto my iPhone? | Dive log (page exists) |
| 12 | How does a dive centre share a plan the whole team signs? | Time to Surface for dive pros |

Five of these have a reviewed page already, so those videos cost only the video work; the three pilot
episodes are rendered (`tools/pilot-episode.py`), awaiting his verdict.

## Decisions he has to make

1. ~~Go, or Instagram first~~ **Decided 2026-10-28: go, with Instagram and YouTube as equals**; the
   pilot (three episodes around the cat, each under a minute) comes first and his verdict gates the accounts.
2. **The voice**: decided 2026-10-28, a pleasant young US male voice; the Mac's own voices were rejected
   the same evening. Kokoro (free, local) is in; which of its six American male voices is his pick from the
   samples, and a paid speech service is the upgrade if none pleases. His recorded intros stay optional.
3. **Allow a small inline script on the question pages** for the calculators; the design counts on it.
4. **The veto**: his weekly publish click until the audit, then 48 hours of silence; or no veto after.
5. **Publishing from this Mac**: the upload script runs inside the weekly job and he applies for the
   YouTube API audit on day one (default), or he waits for the audit before the first video. His say-so is needed for a new program to run there on a schedule; this is that question.

## Instagram alongside YouTube (his decision, 2026-10-28)

The same weekly unit goes to Instagram as Reels plus a carousel through Meta's API, from his own
professional account, nothing automated beyond publishing. No follow-for-follow by machine, no bots, no
bought followers: the account is the asset and those are the ways to lose it. Reach comes from Reels and
from his own following of the right people; the link is in the bio with its campaign token.

### His point about instructors and their students (2026-10-28)

Rustam's reason for Instagram is tactical: *follow instructors and their students, and you have active
divers at once.* The targeting is right, and sharper than anything in the table above. A student in the
weeks around a course is the one person asking exactly these questions (how much weight, what is my SAC,
what is minimum gas), and the instructor is the node every one of them follows. That insight goes into the
plan whichever channel leads. What does not survive is the machine doing the following:

- **Following people is allowed; a program following people is not.** Meta's terms forbid it, the action
  blocks come at thresholds nobody publishes, and the penalty falls on the account that holds the content.
  A tool that follows a few hundred accounts a day from one new account is what Instagram's detection is
  built to catch; this is the one part of the idea that would be gambling the asset on unknown limits.
- **The compliant form of the same tactic.** The AI builds the list: instructors by region and agency, the
  dive centres, the training-heavy accounts whose comment sections are students. It drafts what to say.
  Rustam does the following and the commenting himself at a human pace, ten minutes a day, from his own
  phone. That is not self-managed, which is why it is not the engine; it is a strong accompaniment to it.
- **What is automated for him on that audience.** Reels are shown by interest, not by follower graph:
  a Reel about SAC rates reaches people who watch dive-training Reels whether or not anyone followed
  anyone, and posting Reels through Meta's API is allowed. On YouTube the same holds with more force,
  since the viewer is already searching for the answer. So the engine reaches instructors' students
  without a follow; his own following makes the account look alive and brings the first replies.
- **The instructor as a multiplier, not a follow target.** One instructor who hands the apps to every
  course is worth more than a thousand follow-backs. The dive-pro cut of Time to Surface (signed team
  plans in the centre's brand) is already built for that person; a weights worksheet or a student
  gas-planning sheet from the apps, offered to instructors to pass on, is the one-to-many move. The AI
  drafts the outreach; he sends it. This is the separate project noted in the table, and the first
  candidate after the engine runs.

## Review notes (2026-10-28)

A clean-context reviewer checked the platform facts this design rests on and attacked the recommendation;
its three objections (slow signal and optimistic numbers; the publishing lock; the written twin against
Google's inline answers) are folded in above. The facts:

1. **YouTube API uploads are private until an audit.** Videos uploaded through the YouTube Data API by a
   project created after 2020-07-28 that has not passed the API compliance audit are locked to private;
   the upload succeeds and the owner is told by email. A `publishAt` time does not lift the lock. How long
   the audit takes is not published; "weeks" is hearsay. https://developers.google.com/youtube/v3/docs/videos/insert
2. **Quota**: 10,000 units a day by default; an upload costs 1,600 units, so about six a day, far more
   than needed. https://developers.google.com/youtube/v3/determine_quota_cost
3. **Scheduled publishing** through the API is `privacyStatus=private` plus `publishAt`, usable once the
   audit has passed. https://developers.google.com/youtube/v3/docs/videos
4. **Instagram publishing**: Meta's "Instagram API with Instagram Login" publishes to a professional
   account **without a Facebook Page**; an app in development mode serves accounts that hold a role on
   the app (App Review is for other people's accounts; that it is not needed for the owner's own account
   is Meta's stated model, not a sentence found on one page); the limit is 50–100 API posts per rolling
   24 hours, a carousel counting as one. https://developers.facebook.com/docs/instagram-platform/content-publishing
5. **Follow automation**: prohibited by Instagram's terms; action-block thresholds are not published and
   the sources on them are of low quality, which is itself the point: the account would be gambling on
   unknown limits. https://help.instagram.com/581066165581870
6. **App Store campaign links** (`pt`, `ct`, `mt`) attribute in App Analytics with three caveats: only
   first-time downloads within 24 hours of the click count, the last click wins, and a campaign appears
   only after at least five first-time downloads. Hence one token per channel, not per video.
   https://developer.apple.com/help/app-store-connect-analytics/acquisition/campaign-links/
7. **YouTube "inauthentic content"** (2025-07-15) is a Partner Program monetisation rule; the Community
   Guidelines on spam apply to every channel regardless. Google's scaled-content-abuse policy is the 2024
   Search spam rule on mass pages made for rankings, however produced (from memory, not re-fetched).
   https://www.plagiarismtoday.com/2025/07/08/youtube-targets-inauthentic-content/
8. **TikTok's Content Posting API** keeps an unaudited client's posts private, which is why TikTok is not
   in the design. https://developers.tiktok.com/doc/content-posting-api-reference-direct-post
