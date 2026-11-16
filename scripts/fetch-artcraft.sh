#!/bin/bash
# Downloads the official ArtCraft .deb packages (launcher + WordCraft,
# PdfCraft, PhotoCraft) from the storytold GitHub releases and checks each
# one against the release's SHA256SUMS.txt.
#   usage: fetch-artcraft.sh <dest-dir>
# Exit status: 0 = all downloaded and verified, 1 = something failed.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
. "$HERE/versions.env"
DEST=$1; mkdir -p "$DEST"
ARCH=x86_64
fail=0

latest_version() { # repo -> version (no leading v), via the releases/latest redirect
  local url
  url=$(curl -fsSIL -o /dev/null -w '%{url_effective}' "https://github.com/storytold/$1/releases/latest") || return 1
  case "$url" in */releases/tag/v*) echo "${url##*/tag/v}";; *) return 1;; esac
}

for entry in $ARTCRAFT_APPS; do
  repo=${entry%%:*}; name=${entry##*:}
  var="ARTCRAFT_VERSION_${repo//-/_}"; ver=${!var:-latest}
  if [ "$ver" = latest ]; then
    ver=$(latest_version "$repo") || { echo "ERROR: cannot resolve latest release of $repo" >&2; fail=1; continue; }
  fi
  base="https://github.com/storytold/$repo/releases/download/v$ver"
  deb="$name-$ver-linux-$ARCH.deb"
  echo "ArtCraft: $repo $ver -> $deb"
  if ! curl -fsSL --retry 3 -o "$DEST/$deb.part" "$base/$deb"; then
    echo "ERROR: download failed: $base/$deb" >&2; rm -f "$DEST/$deb.part"; fail=1; continue
  fi
  if curl -fsSL --retry 3 -o "$DEST/$repo-SHA256SUMS.txt" "$base/SHA256SUMS.txt"; then
    want=$(awk -v f="$deb" '{n=$2; sub(/^\*/,"",n)} n==f {print $1}' "$DEST/$repo-SHA256SUMS.txt")
    got=$(sha256sum "$DEST/$deb.part" | cut -d' ' -f1)
    if [ -z "$want" ]; then
      echo "WARNING: $deb is not listed in SHA256SUMS.txt; keeping it unverified" >&2
    elif [ "$want" != "$got" ]; then
      echo "ERROR: checksum mismatch for $deb (want $want, got $got)" >&2
      rm -f "$DEST/$deb.part"; fail=1; continue
    else
      echo "  sha256 OK $got"
    fi
  else
    echo "WARNING: no SHA256SUMS.txt for $repo $ver; keeping $deb unverified" >&2
  fi
  mv "$DEST/$deb.part" "$DEST/$deb"
done
exit $fail
