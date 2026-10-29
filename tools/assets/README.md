# tools/assets

Artwork the pilot generator (`tools/pilot-episode.py`) draws into the episodes. This folder is under `tools/`, which
`_config.yml` keeps off the published site.

- `app-store-badge.svg`, `app-store-badge.png` — Apple's "Download on the App Store" badge, black, English, exactly as
  Apple's App Store Marketing Tools serve it (the badge named `Download_on_the_App_Store_Badge_US-UK_RGB_blk_4SVG_092917`),
  saved 2026-10-29; the PNG is the SVG rendered at 400 px high with a transparent background. Used under Apple's App
  Store Marketing Artwork License (developer.apple.com/app-store/marketing/guidelines/): never altered, tilted or
  animated, one per video, smaller than the main message, a clear space of a quarter of its height, and the credit
  line at the end of the video. Apple asks marketing not to refer to "iOS" and offers no iOS logo to third parties.
- `cat/cat-<pose>.png` — Rustam's own cat drawings (2026-10-29, to be made with ChatGPT in the charcoal-sketch style he
  chose): dark strokes on a transparent background, or on plain white, which the generator keys out. Poses: standing,
  swimming, ascending, sharing (two cats), gauge, head. Until a pose's file exists the generator draws its own sketch.
