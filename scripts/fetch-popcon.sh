#!/bin/sh
# Snapshot of the Debian Popularity Contest ranking (most used packages
# first) for the Mango Store's "apps of the week" when popcon.debian.org
# cannot be reached from the computer.   usage: fetch-popcon.sh <overlay>
set -u
DEST=$1/usr/share/mangos/popcon-top.txt
mkdir -p "$(dirname "$DEST")"
tmp=$(mktemp)
if curl -fsSL --retry 3 --max-time 120 https://popcon.debian.org/by_vote -o "$tmp" &&
   awk '!/^#/ && $1 ~ /^[0-9]+$/ && $1 <= 9000 {print $1, $2}' "$tmp" > "$DEST.new" &&
   [ "$(wc -l < "$DEST.new")" -gt 1000 ]; then
  { echo "# Debian Popularity Contest by_vote, $(date -u +%Y-%m-%d)"; cat "$DEST.new"; } > "$DEST"
  rm -f "$DEST.new" "$tmp"; echo "popcon snapshot: $(wc -l < "$DEST") lines"
else
  rm -f "$DEST.new" "$tmp"; echo "WARNING: popcon snapshot not available" >&2
fi
exit 0
