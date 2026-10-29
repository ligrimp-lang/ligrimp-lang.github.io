#!/bin/sh
# Refuses to let a token, a secret, a password or an account login reach GitHub (Rustam, 2026-10-29: mandatory).
# Run before every commit and push:
#     tools/check-secrets.sh            the staged changes and the commits not yet on origin
#     tools/check-secrets.sh --all      every version of every file in the whole history, and every commit message
# Exit 1 and a masked excerpt when something matches; nothing is printed in full.
P='EAA[A-Za-z0-9]{30,}|ya29\.[A-Za-z0-9_-]{20,}|1//0[A-Za-z0-9_-]{20,}|GOCSPX-[A-Za-z0-9_-]+|AIza[0-9A-Za-z_-]{30,}|[0-9]{6,}-[a-z0-9]{20,}\.apps\.googleusercontent\.com|code=4/0[A-Za-z0-9_-]+|gh[pousr]_[A-Za-z0-9]{30,}|github_pa[t]_|sk-[A-Za-z0-9]{20,}|xox[bpas]-|-----BEGIN [A-Z ]*PRIVATE KEY|"(app_secret|client_secret|access_token|refresh_token|page_access_token|user_access_token)"[[:space:]]*:[[:space:]]*"[^".<]{12,}"|password[[:space:]]*[=:][[:space:]]*[^[:space:]]{6,}|[a-z0-9._-]+@diver\.today'
cd "$(git rev-parse --show-toplevel)" || exit 2
if [ "$1" = "--all" ]; then
  hits=$( { git rev-list --all | while read c; do git grep -I -h -E "$P" "$c" 2>/dev/null; done; git log --all --format=%B | grep -E "$P"; } | sort -u)
else
  up=$(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || echo origin/main)
  hits=$( { git diff --cached -U0 --no-color | grep '^+'; git log -p --no-color "$up..HEAD" 2>/dev/null | grep '^+'; git log --format=%B "$up..HEAD" 2>/dev/null; } | grep -E "$P")
fi
if [ -n "$hits" ]; then
  echo "check-secrets: REFUSED, found what looks like a token, secret, password or login:" >&2
  echo "$hits" | sed 's/\(.\{20\}\).*/\1…/' >&2
  exit 1
fi
echo "check-secrets: clean"
