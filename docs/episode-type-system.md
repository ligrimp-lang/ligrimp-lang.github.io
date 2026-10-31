# Type on the episodes' screens (2026-11-01)

Rustam's feedback on the SCR episode's first render: use the best font for bold and for small text, separate bold from small
visibly, position the text so it reads on a small screen, keep every number understandable from the screen alone, and follow
"the latest proven practices about text on screen for Mac and iPhones". This is the system `tools/pilot-episode.py` now draws
with, what it rests on, and what the Mac checks, since the cloud session that wrote it rendered only with a stand-in font.

## The frame and where text may go

The short cut is 1080×1920 and is watched inside Instagram's and YouTube's players, which lay their own chrome over the picture.
Meta's own guidance for Reels asks for roughly the top 14% and the bottom 35% to be kept free of text and logos for ads, and 6%
on each side ([Meta, Instagram Reels image specs](https://www.facebook.com/business/ads-guide/update/image/instagram-reels);
[Meta, text overlays and the safe zone for Stories and Reels](https://www.facebook.com/business/help/980593475366490/)). YouTube
publishes no pixel margins for Shorts; the community guides cluster around 180–290 px at the top, 390–670 px at the bottom and
120–190 px on the right for the title, the description and the button column
([Hopper HQ](https://www.hopperhq.com/blog/youtube-shorts-dimensions/); [Exemplary](https://exemplary.ai/youtube-shorts-size)).
Organic Reels show less chrome than ads; one guide puts the right-hand button column at about 120 px and the bottom overlay at
320–400 px ([Lilach Bullock](https://www.lilachbullock.com/instagram-reels-safe-zone/)).

So the renderer keeps all text inside **`FMT["short"]["safe"] = (72, 270, 910, 1440)`**: the top 14% and the bottom 25% clear, as
Rustam asked, 72 px on the left and 170 px on the right for the button column. The wide cut keeps to `(120, 70, 1800, 1010)`: a
margin, since a 16:9 player covers nothing but its own controls. **Check on the Mac:** play the rendered short in the Instagram
and YouTube apps on an iPhone and look at where the chrome actually falls; the bottom band is the one that moves between app
versions.

## The type

The type is SF Pro from the system, through `build-media.py`'s `font()`. SF Pro is one variable font whose design moves from the
Text cut (open counters, looser spacing, for small sizes) to the Display cut (tighter, for big sizes); Apple's typographers put
the change between 17 and 28 points, and the system does it by optical size
([Apple, WWDC20: The details of UI typography](https://developer.apple.com/videos/play/wwdc2020/10175/)). A frame pixel is not a
point, so `typeface()` sets the font's optical-size axis to the points the viewer sees: `pt_per_px` is 0.361 on the short cut
(a 1080-px frame on a 390-pt iPhone) and 0.667 on the wide (a 1920-px frame in a 1280-pt window). Where the font has no such axis
(DejaVu standing in off the Mac) it is used as it is. **Check on the Mac:** that `SFNS.ttf` exposes an optical-size axis to
Pillow (`ImageFont.truetype(...).get_variation_axes()`); if it does not, the system falls back to the plain weight and the Mac
may prefer loading SF Pro Text and SF Pro Display as two files.

Apple's floor for legible text is 11 points at a normal viewing distance
([Apple, UI design dos and don'ts](https://developer.apple.com/design/tips/)); on the short cut that is 30.5 frame pixels, so the
smallest text drawn is 32 px (the strip's labels) and footnotes and figure labels are 34 px, about 12 pt. The levels, in frame
pixels for the short cut (`TYPE["short"]`; the wide cut is about 12% larger):

| Level | Size | Weight and cut | Colour |
|---|---|---|---|
| Card title (spaced small caps) | 34 | Semibold, Text | teal (`ACCENT`) |
| Headline (`big`) | 92 | Bold, Display | ink (240, 243, 245) |
| Secondary lines | 46 | Medium, Display | muted grey-blue (178, 198, 208) |
| Figures (operands) | 96 | Bold, Display | ink |
| Figure labels | 34 | Medium, Text | muted |
| Result | 104 | Bold, Display | teal |
| Example-dive values | 46 | Semibold, Display | teal lit, grey (112, 126, 136) unlit |
| Example-dive labels | 32 | Regular, Text | muted lit, grey unlit |
| Footnote | 34 | Regular, Text | dim (168, 178, 186) |

Each level is a clear step in size and weight from the next, and secondary text has its own colour, so bold and small never
compete. A long headline, figures row or result shrinks in steps (to about 70%) rather than running out of the column or
taking a third line.

## Contrast

The top of the family's water background is bright cyan and washes out white type (Rustam's observation). WCAG asks for 4.5:1
for normal text and 3:1 for large text, as thresholds rather than targets, and notes that text over video and gradients needs a
human check because the ratio changes along the text ([W3C, Understanding SC 1.4.3](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html)).
So every block of text sits on a **scrim panel**: a rounded rectangle of (8, 14, 20) at 73% over the water (`PANEL`), which puts
ink at well above 10:1 and the muted secondary at about 7:1 whatever the water does behind it. The panel spans the safe width,
with 44 px of padding around the text, and the example-dive strip has a panel of its own. **Check on the Mac:** a frame from the
brightest second of the dolphin clip under the hook card, and one from the blurred loop under a step card.

## Reading order, and what each card may carry

- **Nothing spoken is drawn** (Rustam, 2026-10-29); the cards carry a title, a figure and labels, and the captions file carries the
  words.
- **A step card is read from the screen alone**: each operand carries a small label under it (`160 bar` over `used`, `11.1 L`
  over `tank`), the operator sits between in the muted colour, and the result appears below in teal, labelled, only when the voice
  reaches it (`result`, on the segment's `reveal`: the start of the segment's second sentence, else `beat=` seconds).
- **The example dive stays in view** on every step as a strip at the top (`scenario` on the episode, `uses` on the segment), its
  used values lit in teal and the rest dimmed, so the viewer always has the numbers the step takes in front of them; the step
  card sits straight under it.
- **A definition is a list, not a paragraph.** Several facts about one thing (what the term is short for, its unit, its other
  name) go in a `rows=` list: a short key in teal on the left, its explanation beside it in the secondary colour, left-aligned and
  wrapped at about forty characters, one fact per row with air between rows; the title and headline of such a card sit on the
  same left axis. Centred text is kept for what it suits: a headline, a figure, a single short line. Rustam's 2026-11-01 verdict
  on the first take of the term card ("this block of text is not readable") is the reason: three centred, wrapped lines read as a
  block, the same words as a keyed list read at a glance.
- **Every row tells the viewer something the screen does not already.** A row that only names what is in front of them
  ("SCR — its short form" under the headline "Surface consumption rate") is padding and goes, or becomes a fact ("SCR — for
  short; the term GUE uses"). Rustam rejected that row on the second take of the same card, the same day. Before a card is handed
  over, each line is read as the viewer will read it, with the question "what does this give me that the rest of the card does
  not", and a line with no answer is cut.
- **A pause after every number** (`hold=` seconds of silence after a segment's words), so a figure can be taken in before the
  next sentence starts.
- **The example is announced at the start** ("An example dive: …", its own card), not disclaimed in small type at the end.

## What was tested, and where

Stills of every card of the SCR episode at 1080×1920 and 1920×1080, rendered in the cloud with DejaVu standing in for SF Pro over
a stand-in water gradient, checked by a script against the safe area (nothing left it) and looked at; and the timeline with the
voice faked, to see the holds and the reveal times land. DejaVu is wider than SF Pro, so SF will leave more room, not less. The
real render, with SF Pro, the real water and the real voice, is the Mac's, and the three checks above are its.
