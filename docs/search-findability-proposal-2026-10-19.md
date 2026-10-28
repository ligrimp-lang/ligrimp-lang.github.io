# Search findability per app — proposal, 2026-10-19

Built on today's Monday report (ranks on Apple's public search index, the store's own search
suggestions, and the Discovery numbers). Not on the web: `docs/` is excluded in `_config.yml`.

## Where we stand

Each dive app gets roughly 45–75 App Store search impressions a week (Surface Interval on the Mac
160). Google Search Console for diver.today is four days old and shows zeros. So the question is
not "more of the same" but which phrases a diver with the problem actually types, and whether the
app is in the list when they do.

Two different places, two different kinds of search:

- **App Store search is nouns.** "dive weight", "trimix mod", "dive videos". The name and subtitle
  are weighted most, the keyword field least, and for crowded nouns ("dive planner", "dive log",
  "buoyancy calculator") the order among matching apps is ratings and downloads, not words.
- **Google is questions.** "how much weight do I need for diving", "why is my GoPro footage
  blue". Nothing we have answers a question yet; diver.today lists the apps.

## Per app

### Turn Pressure — the cheapest win is sitting there
Ranks: *turn pressure* #1 everywhere; *dive planner* #23–40 on all five English stores (page two
or three, in effect invisible); *scuba gas planner* #38 US, #5 DE; *no deco* #53–70.
Not indexed at all: *minimum gas* (one app in the whole German index, not ours), *sac rate scuba*
(three, not ours). Those are the words a diver who has done a gas-planning course types for
exactly what the app computes, and "minimum", "rock", "bottom" and "rate" are nowhere in the
listing. Meanwhile the keyword field spends 11 characters on `log,logbook` — the app ranks
nowhere for *dive log* and never will against logbook apps, and Dive log is about to own that.

**Proposal (one change, next week's report attributes it):** keywords out `log,logbook,buddy`,
in `minimum,rock,bottom,rate`. Expected: #1 for *minimum gas*, a rank for *rock bottom* and *sac
rate scuba*. Add *rock bottom*, *minimum gas* (US/GB too) and *safety stop* to the probe list so
the report measures them.

### Weights Check — localised fields, not the English one
Ranks: *dive weight* #6 US, #16 GB, #1 AU, #1 DE/RU/NL; *scuba weighting* #24 US; *buoyancy
calculator* still absent in the US and UK four weeks after the subtitle was changed to buy it
(#9 DE only). "weight" and "calculator" are swamped by fitness apps; the English fields are as
good as words can make them. The gear words in the keyword field (*wetsuit* #129, *drysuit*
#143, *dive gear* #117) buy nothing.

The empty markets are the opening: the German, Russian and Dutch columns say "#2 of 2", "– of 1",
"– of 9" — a handful of apps, and one localised keyword puts us first. *калькулятор грузов*
has nine results in the US index and we are not one; *tauchen blei rechner* has one, not us.

**Proposal:** (1) check the Russian keyword file carries `груз,грузы,грузов,калькулятор` and the
German one `rechner,tarieren` (*tarieren* is the German verb for trimming buoyancy), French/Spanish/
Italian `lest`/`lastre`/`zavorra`; (2) English keywords: out `wetsuit,drysuit,gear,ditchable`,
in `ballast,trim,calc` (*buoyancy calc* is a suggested query, *dive ballast* has two results).
Two changes, two weeks.

### Time to Surface — forums first, store second
Ranks: *time to surface* #1; *buhlmann* #12–24; *gradient factor* #7–40; *trimix mod* #9–27;
*deco planner* #161 US / #124 GB / #19 DE even though it is the name's second half — "deco" in
the US means home decor, the phrase is noise there. *decompression* is never typed (the
suggestions after it are file tools). The store already suggests "time to surface – deco
planner" after "deco p" in the UK and Germany, which is the sign the name is being learnt.

A tech diver finds a planner on ScubaBoard's technical forum, in a GUE or TDI group, or from an
instructor, then types its name. The words are right; the lever is being named in those places.

**Proposal:** no listing change this week. Post the Time to Surface text from
`promotion-posts-2026-10-15.md` first. Add *tech dive*, *deco stops*, *trimix planner* to the
probe list (suggested queries we do not measure yet).

### Surface Interval — one phrase, his call
Ranks: #1 for *surface interval*, *dive videos*, *dive video*; *snorkel video* #7 US, #10 DE.
Weak where the market is biggest: *underwater video* #13 US and absent in GB/AU, *underwater
video editor* absent, *underwater color correction* #74 US — and that exact phrase is one the US
store suggests after "underwater", so people type it. All four of those words sit in the keyword
field, the lowest-weighted one; the subtitle is the only field that moves it.

**Proposal, Rustam's decision because he chose the current subtitle on 2026-09-28:** a subtitle
that carries *underwater* and *color*, e.g. "Underwater color fix & reels" (28). Trade: *correction*
and *assembly* leave; *dive video* stays in the name. If kept as is, no change; the snorkel and
GoPro side is already won on *dive videos*.

### Dive log — nothing to rank yet, prepare the ruler
Still in review (the lookup returns nothing). *dive log* is the most crowded term of the five
(PADI, Logporter, Thalivue, Sealog…); the subtitle "Shearwater dive import" targets the niche
correctly. **Proposal:** write its terms file now — *dive log, dive logbook, scuba dive log,
shearwater, shearwater log, shearwater import, dive computer log, sac rate* — so the first
Monday after release measures from day one, and drop `log,logbook` from Turn Pressure (above).

## Across all five

1. **Five question pages for Google.** One page each, in Rustam's voice, titled with the
   question and answering it honestly before the app is mentioned; linked from diver.today and the
   per-app site, in the sitemap. This is the one thing that reaches "people who need them" who do
   not yet know an app exists:
   - How much weight do I need for scuba diving? (Weights Check — the method, the weight check at
     the stop, what changes it; no verdict promised)
   - What is minimum gas, and how do I work it out? (Turn Pressure)
   - What are gradient factors, in plain words? (Time to Surface)
   - Why is my GoPro dive footage blue, and how do I fix it? (Surface Interval)
   - How do I get my dives off a Shearwater onto an iPhone? (Dive log, after release)
   Search Console shows within a few weeks which pages draw queries. Pages that read as generated
   are ignored by both Google and divers; these need his words or his review line by line.
2. **Ratings are the multiplier on the head terms.** *dive planner*, *dive log*, *buoyancy
   calculator* order by ratings and downloads. If an app does not yet ask for a rating after a
   completed use (a saved plan, a finished reel, a weight check written down), that one prompt
   outweighs every keyword above. Check each app; add where missing.
3. **Localised keyword fields** where the Discovery numbers already show people: Japan, the
   Netherlands and Belgium, China, Russia, Mexico. The "of N" columns say those indexes are thin.
4. **One change per app per week**, as the listing documents already say, so the Monday report
   can attribute it.

## Order, if done one at a time

1. Turn Pressure keywords (this week).
2. Dive log terms file (this week, five minutes).
3. Weights Check Russian/German/Dutch fields (next week).
4. Surface Interval subtitle — decision.
5. Rating prompt check in all five.
6. The five question pages, as his time allows; Weights Check's first, it has the most searched question.
