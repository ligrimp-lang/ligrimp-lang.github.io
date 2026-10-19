#!/bin/bash
# Screenshots of pages straight from the files, no web server needed.
# Chrome renders file:// pages fully (styles, images, posters); the phone cut is a 390-px frame,
# because headless Chrome will not make a window that narrow. Videos do not play in a screenshot,
# their posters (which are the videos' first frames) do show.
#
#   tools/preview.sh                          # home page
#   tools/preview.sh weight-for-scuba-diving  # a question page (its folder)
#
# Writes build/preview/<name>-wide.png (1440 wide) and <name>-phone.png (390 wide).
set -euo pipefail
cd "$(dirname "$0")/.."
SITE="$PWD"
PAGE="${1:-}"
if [ -n "$PAGE" ]; then FILE="$SITE/${PAGE%/}/index.html"; NAME="${PAGE%/}"; else FILE="$SITE/index.html"; NAME="home"; fi
[ -f "$FILE" ] || { echo "no page at $FILE" >&2; exit 1; }

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT="$SITE/build/preview"; mkdir -p "$OUT"
PROFILE="$SITE/build/chrome-profile"
QUIET=(--headless=new --disable-gpu --no-first-run --no-default-browser-check --user-data-dir="$PROFILE"
       --disable-background-networking --disable-component-update --disable-sync --no-pings
       --allow-file-access-from-files --hide-scrollbars)

"$CHROME" "${QUIET[@]}" --window-size=1440,2400 --screenshot="$OUT/$NAME-wide.png" "file://$FILE" 2>/dev/null

FRAME="$OUT/$NAME-phone-frame.html"
printf '<!doctype html><meta charset="utf-8"><style>html,body{margin:0;background:#333}iframe{border:0;display:block}</style><iframe src="file://%s" width="390" height="2400"></iframe>\n' "$FILE" > "$FRAME"
"$CHROME" "${QUIET[@]}" --window-size=600,2400 --screenshot="$OUT/$NAME-phone.png" "file://$FRAME" 2>/dev/null
rm -f "$FRAME"

echo "$OUT/$NAME-wide.png"
echo "$OUT/$NAME-phone.png"
