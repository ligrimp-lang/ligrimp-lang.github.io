# tools/assets

Artwork the pilot generator (`tools/pilot-episode.py`) draws into the episodes. This folder is under `tools/`, which
`_config.yml` keeps off the published site.

- `app-store-badge.svg`, `app-store-badge.png` — Apple's "Download on the App Store" badge, black, English, exactly as
  Apple's App Store Marketing Tools serve it (the badge named `Download_on_the_App_Store_Badge_US-UK_RGB_blk_4SVG_092917`),
  saved 2026-10-29; the PNG is the SVG rendered at 400 px high with a transparent background. Used under Apple's App
  Store Marketing Artwork License (developer.apple.com/app-store/marketing/guidelines/): never altered, tilted or
  animated, one per video, smaller than the main message, a clear space of a quarter of its height, and the credit
  line at the end of the video. Apple asks marketing not to refer to "iOS" and offers no iOS logo to third parties.
- `cat/cat-<pose>.png` — Rustam's own cat drawings, made with ChatGPT on 2026-10-29 in the charcoal-sketch style he chose
  (black strokes on transparent; his masters are 2048 px, these are the same pictures at 1400 px): `standing`, `swimming`,
  `ascending`, `sharing` (two cats), `gauge`, `head`. A card's `cat="<pose>"` picks one, `CAT_MOUTH` in the generator says
  where its bubbles start, and an episode's `thumb_cat` picks the thumbnail's. If a pose's file were missing the generator
  would draw its own sketch instead.
