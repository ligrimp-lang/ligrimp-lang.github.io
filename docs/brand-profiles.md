# The three profiles: pictures and texts (2026-10-29)

The YouTube channel, the Instagram creator profile and the Facebook Page behind it were created blank on 2026-10-29. This file holds
the exact texts for their fields and says which picture goes where; the pictures are made by `tools/brand-assets.py` into
`build/brand/` (git-ignored; the Mac renders them, because the type is SF Pro) and `tools/apply-youtube-branding.py` sends the
YouTube ones that have an API. Rustam's brief: *"personalize as much as you can the screens including colors, images, logos etc"*.
Rules: British spelling, no exclamation marks, nothing about an app beyond its App Store listing, the reserve is minimum gas, Dive log is
in App Review so it is "coming soon", and nothing here is a login, a token or a secret (`tools/check-secrets.sh` must say clean).

`tools/apply-youtube-branding.py` reads the fenced blocks below by their headings, so the headings "YouTube description" and
"YouTube keywords" are part of the mechanism: change the text, not the heading.

## The pictures

| Where | File from `build/brand/` | Set by |
|---|---|---|
| YouTube banner | `youtube-banner.png` (2560×1440; the centred 1546×423 carries everything that matters) | `apply-youtube-branding.py` |
| YouTube profile picture | `avatar-a-youtube.png` or `avatar-b-youtube.png` (800×800), Rustam's pick from `sheet.png` | by hand, YouTube Studio: Customisation, Branding |
| YouTube video watermark | `youtube-watermark.png` (150×150, transparent), the last 15 s of every video, bottom right | `apply-youtube-branding.py` |
| Instagram profile picture | `avatar-a-instagram.png` or `-b-` (1080×1080) | by hand, in the app |
| Facebook Page profile picture | `avatar-a-facebook.png` or `-b-` (720×720) | by hand |
| Facebook Page cover | `facebook-cover.png` (1640×624; the centred 820×312 carries everything that matters) | by hand |

The two candidates for the mark: **a** is the cat's head, close, filling the circle; **b** the standing cat, smaller, in a thin teal
ring. Both are Rustam's own charcoal drawing in the silver tint on the dark ground, no text, made to read at 110 px. The same mark goes
on all three profiles.

## YouTube

### YouTube description

```text
Apps for divers, today and every day.

One diver's question a week, answered in under a minute with a worked example, by the person who makes the five apps. The cat on the cards is C × A × T: consumption, pressure, time, the gas a dive needs.

Time to Surface: Trimix deco and technical dive planner
Surface Interval: Underwater video colour correction & reels
Dive log: Shearwater dive log app for iPhone (coming soon, in App Review)
Turn Pressure: Dive planner and minimum gas calculator
Weights Check: Scuba weight and buoyancy calculator

Free on the App Store. Every answer, and the apps, at https://diver.today
```

### YouTube keywords

One per line; the script joins them into YouTube's one string, quoting the multi-word ones. They are the site's search wording
(`CLAUDE.md`, "Words on the page").

```text
scuba diving
dive planner
decompression planner
trimix
technical diving
scuba gas planner
no-deco calculator
turn pressure
minimum gas
SAC rate
gas planning
dive weighting
scuba weight calculator
buoyancy calculator
dive log
dive logbook
Shearwater
GoPro dive footage
underwater video colour correction
diver.today
```

Default language: en. No country. The channel's links (set in YouTube Studio, no API): `https://diver.today/` first, then the five
App Store links in the page's order (`CLAUDE.md`, "The apps on the page").

## Instagram

### Instagram name

The display name, under the username:

```text
diver.today
```

### Instagram bio

150 characters at most; line breaks count:

```text
One diver's question a week, in under a minute, with a worked example.
Free apps for divers, by the person who makes them.
diver.today
```

Link field: `https://diver.today/`. Category, if one is asked for: Education.

## Facebook Page

### Facebook Page intro

101 characters at most:

```text
One diver's question a week, answered in under a minute. Free apps for divers. diver.today
```

Website: `https://diver.today/`. Category: Education. The cover is `facebook-cover.png`, the profile picture the same mark as the
other two.

## What is never automated

The profiles are set once and the scripts publish; nothing replies, follows, likes or messages by machine
(`docs/publishing-runbook.md`, "What is never automated").
